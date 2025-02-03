# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
#

"""Low-level drivers and domain crossing logic for `eurorack-pmod` hardware."""

import os

from amaranth                   import *
from amaranth.build             import *
from amaranth.lib               import wiring, data, stream
from amaranth.lib.wiring        import In, Out
from amaranth.lib.fifo          import AsyncFIFO
from amaranth.lib.cdc           import FFSynchronizer
from amaranth.lib.memory        import Memory
from amaranth.utils             import exact_log2
from amaranth_soc               import gpio

from tiliqua                    import i2c
from vendor                     import i2c as vendor_i2c

from amaranth_future            import fixed

WIDTH = 16

# Native 'Audio sample SQ', shape of audio samples from CODEC.
ASQ = fixed.SQ(0, WIDTH-1)

class I2SSignature(wiring.Signature):
    def __init__(self):
        super().__init__({
            "sdin1":   Out(1),
            "sdout1":   In(1),
            "lrck":    Out(1),
            "bick":    Out(1),
            "mclk":    Out(1),
        })

class EurorackPmodPinSignature(wiring.Signature):
    def __init__(self):
        super().__init__({
            "i2s":     Out(I2SSignature()),
            "i2c":     Out(vendor_i2c.I2CPinSignature()),
            "pdn_clk": Out(1),
            "pdn_d":   Out(1),
        })

class FFCProvider(wiring.Component):

    """
    Pin provider for audio interface connected through FFC
    connector and onboard PDN flip-flop on Tiliqua R3+
    """

    def __init__(self):
        super().__init__({
            "pins": In(EurorackPmodPinSignature())
        })

    def elaborate(self, platform):
        m = Module()
        ffc = platform.request("audio_ffc")
        m.d.comb += [
            # I2S bus
            ffc.sdin1.o.eq(self.pins.i2s.sdin1),
            self.pins.i2s.sdout1.eq(ffc.sdout1.i),
            ffc.lrck.o.eq(self.pins.i2s.lrck),
            ffc.bick.o.eq(self.pins.i2s.bick),
            ffc.mclk.o.eq(self.pins.i2s.mclk),
            # Power clocking
            ffc.pdn_clk.o.eq(self.pins.pdn_clk),
            ffc.pdn_d.o.eq(self.pins.pdn_d),
            # I2C bus
            ffc.i2c_sda.o.eq(self.pins.i2c.sda.o),
            ffc.i2c_sda.oe.eq(self.pins.i2c.sda.oe),
            self.pins.i2c.sda.i.eq(ffc.i2c_sda.i),
            ffc.i2c_scl.o.eq(self.pins.i2c.scl.o),
            ffc.i2c_scl.oe.eq(self.pins.i2c.scl.oe),
            self.pins.i2c.scl.i.eq(ffc.i2c_scl.i),
        ]
        return m

class I2STDM(wiring.Component):

    """
    This core talks I2S TDM to an AK4619 configured in the
    interface mode configured by I2CMaster below.

    The interface formats assumed by this core as taken from
    Table 1 in AK4619VN datasheet):
     - For 48kHz, FS == 0b000, which requires:
         - MCLK = 256*Fs,
         - BICK = 128*Fs,
         - Fs must fall within 8kHz <= Fs <= 48Khz.
     - For 192kHz, FS == 0b100, which requires:
         - MCLK = 128*Fs,
         - BICK = 128*Fs,
         - Fs is 192Khz.
    - In both cases, TDM == 0b1 and DCF == 0b010, implies:
         - TDM128 mode I2S compatible.
    """

    N_CHANNELS = 4
    S_WIDTH    = 16
    SLOT_WIDTH = 32

    def __init__(self, audio_192=False):
        self.audio_192 = audio_192
        super().__init__({
            # CODEC pins (I2S)
            "i2s":     Out(I2SSignature()),
            # Gateware interface
            "channel": Out(exact_log2(self.N_CHANNELS)),
            "strobe":  Out(1),
            "i":       In(signed(self.S_WIDTH)),
            "o":       Out(signed(self.S_WIDTH)),
        })

    def elaborate(self, platform):
        m = Module()
        clkdiv       = Signal(8)
        bit_counter  = Signal(5)
        bitsel       = Signal(range(self.S_WIDTH))

        if self.audio_192:
            m.d.comb += self.i2s.mclk.eq(clkdiv[0]),
        else:
            m.d.comb += self.i2s.mclk.eq(ClockSignal("audio")),

        m.d.comb += [
            self.i2s.bick  .eq(clkdiv[0]),
            self.i2s.lrck  .eq(clkdiv[7]),
            bit_counter.eq(clkdiv[1:6]),
            bitsel.eq(self.S_WIDTH-bit_counter-1),
            self.channel.eq(clkdiv[6:8])
        ]
        m.d.audio += clkdiv.eq(clkdiv+1)
        with m.If(bit_counter == (self.SLOT_WIDTH-2)): # TODO s/-2/-1 if S_WIDTH > 24 needed
            with m.If(self.i2s.bick):
                m.d.audio += self.o.eq(0)
            with m.Else():
                m.d.comb += self.strobe.eq(1)
        with m.If(self.i2s.bick):
            # BICK transition HI -> LO: Clock in W bits
            # On HI -> LO both SDIN and SDOUT do not transition.
            # (determined by AK4619 transition polarity register BCKP)
            with m.If(bit_counter < self.S_WIDTH):
                m.d.audio += self.o.eq((self.o << 1) | self.i2s.sdout1)
        with m.Else():
            # BICK transition LO -> HI: Clock out W bits
            # On LO -> HI both SDIN and SDOUT transition.
            with m.If(bit_counter < (self.S_WIDTH-1)):
                m.d.audio += self.i2s.sdin1.eq(self.i.bit_select(bitsel, 1))
            with m.Else():
                m.d.audio += self.i2s.sdin1.eq(0)
        return m

class I2SCalibrator(wiring.Component):

    """
    Convert uncalibrated I2S samples (1 sample per payload)
    into calibrated sample streams (4 samples per payload, each channel
    has its own slot).

    The goal is to remove the CODEC DC offset and scale raw counts to
    consistent fixed-point types.
    """

    # Raw samples (I2S interface, audio domain from I2STDM)
    channel: In(exact_log2(I2STDM.N_CHANNELS))
    strobe:  In(1)
    i_uncal: In(signed(I2STDM.S_WIDTH))
    o_uncal: Out(signed(I2STDM.S_WIDTH))

    # From ADC -> calibrated samples (sync domain)
    o_cal:   Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    # Calibrated samples -> to DAC (sync domain)
    i_cal:    In(stream.Signature(data.ArrayLayout(ASQ, 4)))

    def __init__(self, stream_domain="sync", fifo_depth=4):
        self.stream_domain = stream_domain
        self.fifo_depth = fifo_depth
        super().__init__()

    def elaborate(self, platform):

        m = Module()

        self.ctype = fixed.SQ(2, ASQ.f_width)
        cal_mem = Memory(shape=data.ArrayLayout(self.ctype, 2),
                         depth=I2STDM.N_CHANNELS*2,
                         init=[
                            [fixed.Const(1.0, shape=self.ctype),
                             fixed.Const(0.0, shape=self.ctype)]
                            for _ in range(I2STDM.N_CHANNELS*2)
                         ])
        m.submodules.cal_mem = cal_mem
        cal_read = cal_mem.read_port(domain="comb")

        # FIFOs for crossing clock domains
        m.submodules.adc_fifo = adc_fifo = AsyncFIFO(
            width=I2STDM.S_WIDTH*4,
            depth=self.fifo_depth,
            w_domain="audio",
            r_domain=self.stream_domain
        )

        m.submodules.dac_fifo = dac_fifo = AsyncFIFO(
            width=I2STDM.S_WIDTH*4,
            depth=self.fifo_depth,
            w_domain=self.stream_domain,
            r_domain="audio"
        )

        wiring.connect(m, wiring.flipped(self.i_cal), dac_fifo.w_stream)
        wiring.connect(m, adc_fifo.r_stream, wiring.flipped(self.o_cal))

        adc_samples = Signal(data.ArrayLayout(ASQ, 4))
        dac_samples = Signal(data.ArrayLayout(ASQ, 4))

        # into / out of the scale/cal process
        in_sample = Signal(ASQ)
        out_sample = Signal(ASQ)

        # calibration logic (single MAC)
        m.d.comb += out_sample.eq((in_sample * cal_read.data[0]) +
                                  cal_read.data[1])

        # Combined calibration state machine
        with m.FSM(domain="audio") as cal_fsm:
            with m.State("IDLE"):
                with m.If(self.strobe):
                    m.d.audio += [
                        cal_read.addr.eq(self.channel),
                        in_sample.raw().eq(self.i_uncal)
                    ]
                    with m.If(dac_fifo.r_rdy):
                        with m.If(self.channel == (I2STDM.N_CHANNELS - 1)):
                            m.d.audio += dac_samples.eq(dac_fifo.r_data)
                            m.d.comb += dac_fifo.r_en.eq(1)
                    m.next = "PROCESS_ADC"
            with m.State("PROCESS_ADC"):
                m.d.audio += adc_samples[self.channel].eq(out_sample)
                # Complete set of ADC readings, next FIFO entry
                with m.If(self.channel == (I2STDM.N_CHANNELS - 1)):
                    m.d.comb += [
                        adc_fifo.w_data.eq(adc_samples),
                        adc_fifo.w_en.eq(1),
                    ]
                # Setup signals for DAC processing
                # Fetch DAC readings one channel back
                channel_dac = Signal.like(self.channel)
                m.d.comb += channel_dac.eq(self.channel+1)
                m.d.audio += [
                    cal_read.addr.eq(self.channel + I2STDM.N_CHANNELS),
                    in_sample.eq(dac_samples[channel_dac])
                ]
                m.next = "PROCESS_DAC"
            with m.State("PROCESS_DAC"):
                m.d.audio += self.o_uncal.eq(out_sample.raw())
                m.next = "IDLE"

        return m

class I2CMaster(wiring.Component):

    """
    Driver for I2C traffic to/from the `eurorack-pmod`.

    For HW Rev. 3.2+, this is:
       - AK4619 Audio Codec (I2C for configuration only, data is I2S)
       - 24AA025UIDT I2C EEPROM with unique ID
       - PCA9635 I2C PWM LED controller
       - PCA9557 I2C GPIO expander (for jack detection)
       - CY8CMBR3108 I2C touch/proximity sensor (experiment, off by default!)

    This kind of stateful stuff is often best suited for a softcore rather
    than pure RTL, however I wanted to make it possible to use all
    functions of the board without having to resort to using a softcore.
    """

    PCA9557_ADDR     = 0x18
    PCA9635_ADDR     = 0x5
    AK4619VN_ADDR    = 0x10
    CY8CMBR3108_ADDR = 0x37

    N_JACKS   = 8
    N_LEDS    = N_JACKS * 2
    N_SENSORS = 8

    AK4619VN_CFG_48KHZ = [
        0x00, # Register address to start at.
        0x36, # 0x00 Power Management (RSTN asserted!)
        0xAE, # 0x01 Audio I/F Format
        0x1C, # 0x02 Audio I/F Format
        0x00, # 0x03 System Clock Setting
        0x22, # 0x04 MIC AMP Gain
        0x22, # 0x05 MIC AMP Gain
        0x30, # 0x06 ADC1 Lch Digital Volume
        0x30, # 0x07 ADC1 Rch Digital Volume
        0x30, # 0x08 ADC2 Lch Digital Volume
        0x30, # 0x09 ADC2 Rch Digital Volume
        0x22, # 0x0A ADC Digital Filter Setting
        0x55, # 0x0B ADC Analog Input Setting
        0x00, # 0x0C Reserved
        0x06, # 0x0D ADC Mute & HPF Control
        0x18, # 0x0E DAC1 Lch Digital Volume
        0x18, # 0x0F DAC1 Rch Digital Volume
        0x18, # 0x10 DAC2 Lch Digital Volume
        0x18, # 0x11 DAC2 Rch Digital Volume
        0x04, # 0x12 DAC Input Select Setting
        0x05, # 0x13 DAC De-Emphasis Setting
        0x3A, # 0x14 DAC Mute & Filter Setting (soft mute asserted!)
    ]

    AK4619VN_CFG_192KHZ = AK4619VN_CFG_48KHZ.copy()
    AK4619VN_CFG_192KHZ[4] = 0x04 # 0x03 System Clock Setting

    PCA9635_CFG = [
        0x80, # Auto-increment starting from MODE1
        0x81, # MODE1
        0x01, # MODE2
        0x10, # PWM0
        0x10, # PWM1
        0x10, # PWM2
        0x10, # PWM3
        0x10, # PWM4
        0x10, # PWM5
        0x10, # PWM6
        0x10, # PWM7
        0x10, # PWM8
        0x10, # PWM9
        0x10, # PWM10
        0x10, # PWM11
        0x10, # PWM12
        0x10, # PWM13
        0x10, # PWM14
        0x10, # PWM15
        0xFF, # GRPPWM
        0x00, # GRPFREQ
        0xAA, # LEDOUT0
        0xAA, # LEDOUT1
        0xAA, # LEDOUT2
        0xAA, # LEDOUT3
    ]

    def __init__(self, audio_192):
        self.i2c_stream   = i2c.I2CStreamer(period_cyc=256) # 200kHz-ish at 60MHz sync
        self.audio_192    = audio_192
        self.ak4619vn_cfg = self.AK4619VN_CFG_192KHZ if audio_192 else self.AK4619VN_CFG_48KHZ
        super().__init__({
            "pins":           Out(vendor_i2c.I2CPinSignature()),
            # Jack insertion status.
            "jack":           Out(self.N_JACKS),
            # Desired LED state -green/+red
            "led":            In(signed(8)).array(self.N_JACKS),
            # Touch sensor states
            "touch":          Out(unsigned(8)).array(self.N_SENSORS),
            # should be close to 0 if touch sense is OK.
            "touch_err":      Out(unsigned(8)),
            # assert for at least 100msec for complete muting sequence.
            "codec_mute":     In(1),
        })

    def elaborate(self, platform):
        m = Module()

        m.submodules.i2c_stream = i2c = self.i2c_stream
        wiring.connect(m, wiring.flipped(self.pins), self.i2c_stream.pins)

        def state_id(ix):
            return (f"i2c_state{ix}", f"i2c_state{ix+1}", ix+1)

        def i2c_addr(m, ix, addr):
            # set i2c address of transactions being enqueued
            cur, nxt, ix = state_id(ix)
            with m.State(cur):
                m.d.sync += i2c.address.eq(addr),
                m.next = nxt
            return cur, nxt, ix

        def i2c_write(m, ix, data, last=False):
            # enqueue a single byte. delineate transaction boundary with 'last=True'
            cur, nxt, ix = state_id(ix)
            with m.State(cur):
                m.d.comb += [
                    i2c.i.valid.eq(1),
                    i2c.i.payload.rw.eq(0), # Write
                    i2c.i.payload.data.eq(data),
                    i2c.i.payload.last.eq(1 if last else 0),
                ]
                m.next = nxt
            return cur, nxt, ix

        def i2c_w_arr(m, ix, data):
            # enqueue write transactions for an array of data
            cur, nxt, ix = state_id(ix)
            with m.State(cur):
                cnt = Signal(range(len(data)+2))
                mem = Memory(
                    shape=unsigned(8), depth=len(data), init=data)
                m.submodules += mem
                rd_port = mem.read_port()
                m.d.comb += [
                    rd_port.en.eq(1),
                    rd_port.addr.eq(cnt),
                ]
                m.d.sync += cnt.eq(cnt+1)
                with m.If(cnt != len(data) + 1):
                    m.d.comb += [
                        i2c.i.valid.eq(cnt != 0),
                        i2c.i.payload.rw.eq(0), # Write
                        i2c.i.payload.data.eq(rd_port.data),
                        i2c.i.payload.last.eq(cnt == (len(data)-1)),
                    ]
                with m.Else():
                    m.d.sync += cnt.eq(0)
                    m.next = nxt
            return cur, nxt, ix

        def i2c_read(m, ix, last=False):
            # enqueue a single read transaction
            cur, nxt, ix = state_id(ix)
            with m.State(cur):
                m.d.comb += [
                    i2c.i.valid.eq(1),
                    i2c.i.payload.rw.eq(1), # Read
                    i2c.i.payload.last.eq(1 if last else 0),
                ]
                m.next = nxt
            return cur, nxt, ix

        def i2c_wait(m, ix):
            # wait until all enqueued transactions are complete
            cur,  nxt, ix = state_id(ix)
            with m.State(cur):
                with m.If(~i2c.status.busy):
                    m.next = nxt
            return cur, nxt, ix


        # used for implicit state machine ID tracking / generation
        ix = 0

        # compute actual LED register values based on signed 'red/green' desire
        led_reg = Signal(data.ArrayLayout(unsigned(8), self.N_LEDS))
        for n in range(self.N_LEDS):
            if n % 2 == 0:
                with m.If(self.led[n//2] > 0):
                    m.d.comb += led_reg[n].eq(0)
                with m.Else():
                    m.d.comb += led_reg[n].eq(-self.led[n//2])
            else:
                with m.If(self.led[n//2] > 0):
                    m.d.comb += led_reg[n].eq(self.led[n//2])
                with m.Else():
                    m.d.comb += led_reg[n].eq(0)

        # current touch sensor to poll, incremented once per loop
        touch_nsensor = Signal(range(self.N_SENSORS))

        #
        # Compute codec power management register contents,
        # Muting effectively clears/sets the RSTN bit and DA1/DA2
        # soft mute bits. `mute_count` ensures correct sequencing -
        # always soft mute before asserting RSTN. Likewise, always
        # boot with soft mute, and deassert soft mute after RSTN.
        #
        # Clocks - assert RSTN (0) to mute, after MCLK is stable.
        # deassert RSTN (1) to unmute, after MCLK is stable.
        #
        mute_count  = Signal(8)

        # CODEC DAC soft mute sequencing
        codec_reg14 = Signal(8)
        with m.If(self.codec_mute):
            # DA1MUTE / DA2MUTE soft mute ON
            m.d.comb += codec_reg14.eq(self.ak4619vn_cfg[0x15] | 0b00110000)
        with m.Else():
            # DA1MUTE / DA2MUTE soft mute OFF
            m.d.comb += codec_reg14.eq(self.ak4619vn_cfg[0x15] & 0b11001111)

        # CODEC RSTN sequencing
        # Only assert if we know soft mute has been asserted for a while.
        codec_reg00 = Signal(8)
        with m.If(mute_count == 0xff):
            m.d.comb += codec_reg00.eq(self.ak4619vn_cfg[1] & 0b11111110)
        with m.Else():
            m.d.comb += codec_reg00.eq(self.ak4619vn_cfg[1] | 0b00000001)

        startup_delay = Signal(32)

        with m.FSM(init='STARTUP-DELAY') as fsm:

            #
            # AK4619VN init
            #
            init, _,   ix  = i2c_addr (m, ix, self.AK4619VN_ADDR)
            _,    _,   ix  = i2c_w_arr(m, ix, self.ak4619vn_cfg)
            _,    _,   ix  = i2c_wait (m, ix)

            #
            # startup delay
            #

            with m.State('STARTUP-DELAY'):
                if platform is not None:
                    with m.If(startup_delay == 600_000):
                        m.next = init
                    with m.Else():
                        m.d.sync += startup_delay.eq(startup_delay+1)
                else:
                    m.next = init

            #
            # PCA9557 init
            #

            _,   _,   ix  = i2c_addr (m, ix, self.PCA9557_ADDR)
            _,   _,   ix  = i2c_write(m, ix, 0x02)
            _,   _,   ix  = i2c_write(m, ix, 0x00, last=True)
            _,   _,   ix  = i2c_wait (m, ix) # set polarity inversion reg

            #
            # PCA9635 init
            #
            _,   _,   ix  = i2c_addr (m, ix, self.PCA9635_ADDR)
            _,   _,   ix  = i2c_w_arr(m, ix, self.PCA9635_CFG)
            _,   _,   ix  = i2c_wait (m, ix)

            #
            # BEGIN MAIN LOOP
            #

            #
            # PCA9635 update (LED brightnesses)
            #
            cur, _,   ix  = i2c_addr (m, ix, self.PCA9635_ADDR)
            _,   _,   ix  = i2c_write(m, ix, 0x82) # start from first brightness reg
            for n in range(self.N_LEDS):
                _,   _,   ix  = i2c_write(m, ix, led_reg[n], last=(n==self.N_LEDS-1))
            _,   _,   ix  = i2c_wait (m, ix)

            s_loop_begin = cur

            #
            # CY8CMBR3108 read (Touch scan registers)
            #

            _,   _,   ix  = i2c_addr (m, ix, self.CY8CMBR3108_ADDR)
            _,   _,   ix  = i2c_write(m, ix, 0xBA + (touch_nsensor<<1))
            _,   _,   ix  = i2c_read (m, ix, last=True)
            _,   _,   ix  = i2c_wait (m, ix)

            # Latch valid reads to dedicated touch register.
            cur, nxt, ix = state_id(ix)
            with m.State(cur):
                m.d.sync += touch_nsensor.eq(touch_nsensor+1)
                with m.If(~i2c.status.error):
                    with m.If(self.touch_err > 0):
                        m.d.sync += self.touch_err.eq(self.touch_err - 1)
                    with m.Switch(touch_nsensor):
                        for n in range(8):
                            if n > 3:
                                # R3.3 hw swaps last four vs R3.2 to improve PCB routing
                                with m.Case(n):
                                    m.d.sync += self.touch[4+(7-n)].eq(i2c.o.payload)
                            else:
                                with m.Case(n):
                                    m.d.sync += self.touch[n].eq(i2c.o.payload)
                    m.d.comb += i2c.o.ready.eq(1)
                with m.Else():
                    with m.If(self.touch_err != 0xff):
                        m.d.sync += self.touch_err.eq(self.touch_err + 1)
                m.next = nxt


            # AK4619VN power management (Soft mute + RSTN)

            _,   _,   ix  = i2c_addr (m, ix, self.AK4619VN_ADDR)
            _,   _,   ix  = i2c_write(m, ix, 0x00) # RSTN
            _,   _,   ix  = i2c_write(m, ix, codec_reg00, last=True)
            _,   _,   ix  = i2c_wait (m, ix)

            _,   _,   ix  = i2c_write(m, ix, 0x14) # DAC1MUTE / DAC2MUTE
            _,   _,   ix  = i2c_write(m, ix, codec_reg14, last=True)
            _,   _,   ix  = i2c_wait (m, ix)

            #
            # PCA9557 read (Jack input port register)
            #
            _,   _,   ix  = i2c_addr (m, ix, self.PCA9557_ADDR)
            _,   _,   ix  = i2c_write(m, ix, 0x00)
            _,   _,   ix  = i2c_read (m, ix, last=True)
            _,   nxt, ix  = i2c_wait (m, ix)

            # Latch valid reads to dedicated jack register.
            with m.State(nxt):
                with m.If(~i2c.status.error):
                    m.d.sync += self.jack.eq(i2c.o.payload)
                    m.d.comb += i2c.o.ready.eq(1)
                # Also update the soft mute state tracking
                with m.If(self.codec_mute):
                    with m.If(mute_count != 0xff):
                        m.d.sync += mute_count.eq(mute_count+1)
                with m.Else():
                    m.d.sync += mute_count.eq(0)
                # Go back to LED brightness update
                m.next = s_loop_begin

        return m

class EurorackPmod(wiring.Component):
    """
    Driver for `eurorack-pmod` audio interface PCBA (CODEC, LEDs,
    EEPROM, jack detect, touch sensing and so on).

    Requires an "audio" clock domain running at 12.288MHz (256*Fs).

    There are some Amaranth I2S cores around, however they seem to
    use oversampling, which can be glitchy at such high bit clock
    rates (as needed for 4x4 TDM the AK4619 requires).
    """

    # Audio interface pins
    pins:  Out(EurorackPmodPinSignature())

    # Sample streaming
    i_cal:  In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o_cal: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    # Touch sensing and jacksense outputs.
    touch: Out(8).array(8)
    jack: Out(8)
    touch_err: Out(8)
    codec_mute: In(1)

    # 1s for automatic audio -> LED control. 0s for manual.
    led_mode: In(8, init=0xff)
    # If an LED is in manual, this is signed i8 from -green to +red.
    led: In(8).array(8)

    def __init__(self, hardware_r33=True, touch_enabled=True, audio_192=False):
        self.audio_192 = audio_192
        super().__init__()


    def elaborate(self, platform) -> Module:

        m = Module()

        m.submodules.i2c_master = i2c_master = I2CMaster(audio_192=self.audio_192)

        # Hook up I2C master (TODO: use provider)
        wiring.connect(m, i2c_master.pins, wiring.flipped(self.pins.i2c))
        m.d.comb += [
            # Hook up I2C master registers
            self.jack.eq(i2c_master.jack),
            self.touch_err.eq(i2c_master.touch_err),
            # Hook up coded mute control
            i2c_master.codec_mute.eq(self.codec_mute),
        ]

        for n in range(8):

            # Touch sense readings per jack
            m.d.comb += self.touch[n].eq(i2c_master.touch[n]),

            # LED auto/manual settings per jack
            with m.If(self.led_mode[n]):
                if n <= 3:
                    with m.If(self.o_cal.valid & self.jack[n]):
                        m.d.sync += i2c_master.led[n].eq(self.o_cal.payload[n].raw()>>8),
                    with m.If(~self.jack[n]):
                        m.d.sync += i2c_master.led[n].eq(0),
                else:
                    with m.If(self.i_cal.valid):
                        m.d.sync += i2c_master.led[n].eq(self.i_cal.payload[n-4].raw()>>8),
            with m.Else():
                m.d.sync += i2c_master.led[n].eq(self.led[n]),

        # PDN (and clocking for mobo R3+ for pop-free bitstream switching)
        m.d.comb += self.pins.pdn_d.eq(1),
        #
        # Drive external flip-flop, ensuring PDN remains high across
        # FPGA reconfiguration (only works on mobo R3+).
        #
        # Codec RSTN must be asserted (held in reset) across the
        # FPGA reconfiguration. This is performed by `self.codec_mute`.
        #
        pdn_cnt = Signal(unsigned(16))
        with m.If(pdn_cnt != 60000): # 1ms
            m.d.sync += pdn_cnt.eq(pdn_cnt+1)
        with m.If(3000 < pdn_cnt):
            m.d.comb += self.pins.pdn_clk.eq(1)

        m.submodules.i2stdm = i2stdm = I2STDM(audio_192=self.audio_192)
        wiring.connect(m, i2stdm.i2s, wiring.flipped(self.pins.i2s))
        m.submodules.calibrator = calibrator = I2SCalibrator()
        # I2S <-> calibrator
        m.d.comb += [
            calibrator.channel.eq(i2stdm.channel),
            calibrator.strobe.eq(i2stdm.strobe),
            calibrator.i_uncal.eq(i2stdm.o),
            i2stdm.i.eq(calibrator.o_uncal),
        ]
        wiring.connect(m, calibrator.o_cal, wiring.flipped(self.o_cal))
        wiring.connect(m, wiring.flipped(self.i_cal), calibrator.i_cal)

        return m

def pins_from_pmod_connector_with_ribbon(platform, pmod_index):
    """Create a eurorack-pmod resource on a given PMOD connector. Assumes ribbon cable flip."""
    eurorack_pmod = [
        Resource(f"eurorack_pmod{pmod_index}", pmod_index,
            Subsignal("sdin1",   Pins("1",  conn=("pmod", pmod_index), dir='o')),
            Subsignal("sdout1",  Pins("2",  conn=("pmod", pmod_index), dir='i')),
            Subsignal("lrck",    Pins("3",  conn=("pmod", pmod_index), dir='o')),
            Subsignal("bick",    Pins("4",  conn=("pmod", pmod_index), dir='o')),
            Subsignal("mclk",    Pins("10", conn=("pmod", pmod_index), dir='o')),
            Subsignal("pdn",     Pins("9",  conn=("pmod", pmod_index), dir='o')),
            Subsignal("i2c_sda", Pins("8",  conn=("pmod", pmod_index), dir='io')),
            Subsignal("i2c_scl", Pins("7",  conn=("pmod", pmod_index), dir='io')),
            Attrs(IO_TYPE="LVCMOS33"),
        )
    ]
    platform.add_resources(eurorack_pmod)
    return platform.request(f"eurorack_pmod{pmod_index}")

