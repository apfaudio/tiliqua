# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
#

"""Low-level drivers and domain crossing logic for `eurorack-pmod` hardware."""

import os

from amaranth                   import *
from amaranth.build             import *
from amaranth.lib               import wiring, data, stream, io
from amaranth.lib.wiring        import In, Out
from amaranth.lib.fifo          import AsyncFIFO
from amaranth.lib.cdc           import FFSynchronizer
from amaranth.lib.memory        import Memory
from amaranth.utils             import exact_log2
from amaranth_soc               import gpio

from tiliqua                    import i2c
from tiliqua.tiliqua_platform   import TiliquaRevision, EurorackPmodRevision
from vendor                     import i2c as vendor_i2c

from amaranth_future            import fixed

# Native 'Audio sample SQ': shape of audio samples from CODEC.
# Signed fixed point, where -1 to +1 represents -8.192V to +8.192V.
ASQ = fixed.SQ(1, int(os.environ.get('TILIQUA_ASQ_WIDTH', '16')) - 1)

class I2SSignature(wiring.Signature):
    """
    Standard I2S inter-chip audio bus.
    We use TDM for multiple audio channels.

    All signals except MCLK are expected to be going through IO registers,
    which implies a 1 cycle delay compared to the pin itself.
    """
    def __init__(self):
        super().__init__({
            "sdin1":   Out(1),
            "sdout1":   In(1),
            "lrck":    Out(1),
            "bick":    Out(1),
            "mclk":    Out(1),
        })

class EurorackPmodPinSignature(wiring.Signature):
    """
    Interface between tiliqua-mobo and audio interface board.
    """
    def __init__(self):
        super().__init__({
            "i2s":     Out(I2SSignature()),
            "i2c":     Out(vendor_i2c.I2CPinSignature()),
            "pdn_clk": Out(1),
            "pdn_d":   Out(1),
        })


class EurorackPmodIOBuffers(wiring.Component):

    """
    Adapter to add all IO buffers necessary for eurorack-pmod interfacing.
    """

    def __init__(self, i2s_pads, aux_pads):
        self.i2s_pads = i2s_pads
        self.aux_pads = aux_pads
        super().__init__({
            "pins": In(EurorackPmodPinSignature())
        })

    def elaborate(self, platform):
        m = Module()
        # Registered IO buffers are necessary for reliable timing at 192kHz (~50MHz MCLK)
        # so let's just always use them.
        m.submodules.ff_sdout1 = ff_sdout1 = io.FFBuffer(
                "i", self.i2s_pads.sdout1, i_domain="audio")
        m.submodules.ff_sdin1 = ff_sdin1 = io.FFBuffer(
                "o", self.i2s_pads.sdin1, o_domain="audio")
        m.submodules.ff_lrck = ff_lrck = io.FFBuffer(
                "o", self.i2s_pads.lrck, o_domain="audio")
        m.submodules.ff_bick = ff_bick = io.FFBuffer(
                "o", self.i2s_pads.bick, o_domain="audio")
        # MCLK does not need to be an FFBuffer as the MCLK phase does not matter for
        # most CODECs. from the AK4619VN datasheet, page 32 'the phase of MCLK is
        # not critical'. This is important as at 48kHz, we drive MCLK combinatorially from
        # the audio clock domain, which would not work through an FFBuffer.
        m.submodules.ff_mclk = ff_mclk = io.Buffer("o", self.i2s_pads.mclk)
        m.d.comb += [
            # I2S bus
            ff_sdin1.o.eq(self.pins.i2s.sdin1),
            self.pins.i2s.sdout1.eq(ff_sdout1.i),
            ff_lrck.o.eq(self.pins.i2s.lrck),
            ff_bick.o.eq(self.pins.i2s.bick),
            ff_mclk.o.eq(self.pins.i2s.mclk),
        ],
        m.d.comb += [
            # Power clocking (Note: only R3+ has a flip-flop on PDN with pdn_clk).
            self.aux_pads.pdn_clk.o.eq(self.pins.pdn_clk) if hasattr(self.aux_pads, "pdn_clk") else [],
            self.aux_pads.pdn_d.o.eq(self.pins.pdn_d),
            # I2C bus
            self.aux_pads.i2c_sda.o.eq(self.pins.i2c.sda.o),
            self.aux_pads.i2c_sda.oe.eq(self.pins.i2c.sda.oe),
            self.pins.i2c.sda.i.eq(self.aux_pads.i2c_sda.i),
            self.aux_pads.i2c_scl.o.eq(self.pins.i2c.scl.o),
            self.aux_pads.i2c_scl.oe.eq(self.pins.i2c.scl.oe),
            self.pins.i2c.scl.i.eq(self.aux_pads.i2c_scl.i),
        ]
        return m

class FFCProvider(wiring.Component):
    """
    Provider for audio interface board connected through FFC on tiliqua-mobo.
    """
    def __init__(self):
        super().__init__({
            "pins": In(EurorackPmodPinSignature())
        })

    def elaborate(self, platform):
        m = Module()
        m.submodules.iobuf = iobuf = EurorackPmodIOBuffers(
            i2s_pads = platform.request("audio_ffc_i2s", dir={
                "sdin1": "-", "sdout1": "-", "lrck": "-", "bick": "-", "mclk": "-",
            }),
            aux_pads = platform.request("audio_ffc_aux")
        )
        wiring.connect(m, wiring.flipped(self.pins), iobuf.pins)
        return m

class PMODProvider(wiring.Component):
    """
    Provider for audio interface board connected through a PMOD port.
    """
    def __init__(self, pmod_index):
        self.pmod_index = pmod_index
        super().__init__({
            "pins": In(EurorackPmodPinSignature())
        })

    def elaborate(self, platform):
        m = Module()
        pmod_resources = [
            Resource("audio_pmod_i2s", self.pmod_index,
                Subsignal("sdin1",   Pins("1", dir="o",  conn=("pmod", self.pmod_index))),
                Subsignal("sdout1",  Pins("2", dir="i",  conn=("pmod", self.pmod_index))),
                Subsignal("lrck",    Pins("3", dir="o",  conn=("pmod", self.pmod_index))),
                Subsignal("bick",    Pins("4", dir="o",  conn=("pmod", self.pmod_index))),
                Subsignal("mclk",    Pins("10", dir="o", conn=("pmod", self.pmod_index))),
                Attrs(IO_TYPE="LVCMOS33", DRIVE="8")
            ),
            Resource("audio_pmod_aux", self.pmod_index,
                Subsignal("pdn_d",   Pins("9", dir="o",  conn=("pmod", self.pmod_index))),
                Subsignal("i2c_sda", Pins("8", dir="io", conn=("pmod", self.pmod_index))),
                Subsignal("i2c_scl", Pins("7", dir="io", conn=("pmod", self.pmod_index))),
                Attrs(IO_TYPE="LVCMOS33", DRIVE="8")
            ),
        ]
        platform.add_resources(pmod_resources)

        m.submodules.iobuf = iobuf = EurorackPmodIOBuffers(
            i2s_pads = platform.request("audio_pmod_i2s", self.pmod_index, dir={
                "sdin1": "-", "sdout1": "-", "lrck": "-", "bick": "-", "mclk": "-",
            }),
            aux_pads = platform.request("audio_pmod_aux", self.pmod_index)
        )
        wiring.connect(m, wiring.flipped(self.pins), iobuf.pins)
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
    S_WIDTH    = ASQ.width
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
            #
            # 1-bit offset comes from FFBuffer on sdout1 pin (1 cycle delay)
            with m.If((bit_counter > 0) & (bit_counter <= self.S_WIDTH)):
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
    Convert uncalibrated I2S samples from the audio CODEC into
    calibrated sample streams (4 samples per payload, each channel
    has its own slot).

    The goal is to remove the CODEC DC offset and scale raw counts to
    calibrated fixed-point types. The calibration memory contains 2
    values per channel, where ``out = in * A + B``. A and B may be arbitrarily
    set to any fixed-point constant that fits within ``self.ctype`` declared
    below.

    Most cores assume 4 counts/mV scaling, that is, a value of 1.0 (float) is
    32768 (underlying data) which represents 8.192V (physically).
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

    # Low latency ADC sample peeking (sync domain, can be used by softcore at same time as streams)
    o_cal_peek: Out(data.ArrayLayout(ASQ, 4))

    # Write port for calibration memory (sync domain)
    # Set values and assert `valid` until `ready` is strobed by this core, which
    # indicates the calibration memory write has been committed.
    cal_mem_write: In(stream.Signature(data.StructLayout({
        "a": signed(2 + ASQ.width),
        "b": signed(2 + ASQ.width),
        "channel": unsigned(exact_log2(I2STDM.N_CHANNELS*2))
        })))

    def __init__(self, stream_domain="sync", fifo_depth=4):
        self.stream_domain = stream_domain
        self.fifo_depth = fifo_depth
        super().__init__()

    def elaborate(self, platform):

        m = Module()

        #
        # CALIBRATION MEMORY
        #

        self.ctype = fixed.SQ(3, ASQ.f_bits)
        default_cal = TiliquaRevision.from_platform(platform).pmod_rev().default_calibration()
        cal_mem = Memory(shape=data.ArrayLayout(self.ctype, 2),
                         depth=I2STDM.N_CHANNELS*2,
                         init=[
                            [fixed.Const(mul, shape=self.ctype), fixed.Const(add, shape=self.ctype)]
                            for mul, add in default_cal
                         ])
        m.submodules.cal_mem = cal_mem # WARN: accessed in 'audio' domain
        cal_read = cal_mem.read_port(domain="comb")
        cal_write = cal_mem.write_port(domain="audio")

        #
        # FIFOs for crossing between sync / audio domains. Both 4 channels wide.
        #

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

        # Low latency ADC sample peeking in sync domain
        m.submodules += FFSynchronizer(adc_samples, self.o_cal_peek, o_domain="sync", init=[0, 0, 0, 0])

        # into / out of the scale/cal process
        in_sample = Signal(ASQ)
        out_sample = Signal(ASQ)

        #
        # CALIBRATION ALGORITHM (simple Ax + B, clamp output to min/max storage of ASQ)
        #

        # calibration logic (single MAC then saturating clamp)
        m.d.comb += out_sample.eq(
            ((in_sample * cal_read.data[0]) + cal_read.data[1]).saturate(ASQ))

        # Calibrating samples happens in the 'audio' domain.
        with m.FSM(domain="audio") as cal_fsm:
            with m.State("IDLE"):
                with m.If(self.strobe):
                    m.d.audio += [
                        cal_read.addr.eq(self.channel),
                        in_sample.as_value().eq(self.i_uncal)
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
                m.d.audio += self.o_uncal.eq(out_sample.as_value())
                m.next = "IDLE"

        #
        # CALIBRATION MEMORY UPDATES (sync domain, execute in audio domain)
        #

        # Bring writes into audio domain
        cal_write_payload_audio = Signal.like(self.cal_mem_write.payload)
        cal_write_en_audio = Signal()
        m.submodules += FFSynchronizer(self.cal_mem_write.payload, cal_write_payload_audio, o_domain="audio",
                                       init={"a": 0, "b": 0, "channel": 0})
        m.submodules += FFSynchronizer(self.cal_mem_write.valid, cal_write_en_audio, o_domain="audio")

        # Execute write to calibration memory (in audio domain)
        with m.If(cal_write_en_audio):
            m.d.audio += [
                cal_write.data.eq(Cat(cal_write_payload_audio.a, cal_write_payload_audio.b)),
                cal_write.en.eq(1),
            ]
            # TODO: CLEANUP DAC cal channel off-by-one should be unnecessary!
            with m.If(cal_write_payload_audio.channel < 4):
                m.d.audio += cal_write.addr.eq(cal_write_payload_audio.channel)
            with m.Else():
                m.d.audio += cal_write.addr.eq(
                        Mux(cal_write_payload_audio.channel == 4, 7, cal_write_payload_audio.channel-1))

        # `valid` (hence en_audio) should be held high until we strobe `ready` in sync domain
        # detect a rising edge on en_audio and send a single `ready` strobe (1 cycle) after
        # the write has been committed to the calibration memory.
        done_sync = Signal()
        l_done_sync = Signal()
        m.submodules += FFSynchronizer(cal_write_en_audio, done_sync, o_domain="sync")
        m.d.sync += l_done_sync.eq(done_sync)
        with m.If(done_sync & ~l_done_sync):
            # detected rising edge (write), strobe once.
            m.d.comb += self.cal_mem_write.ready.eq(1)

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

    An SoC can optionally inject its own I2C traffic into this state machine
    (useful for calibration and selftests) using the `i2c_override` port.
    """

    PCA9557_ADDR        = 0x18
    PCA9635_ADDR        = 0x5
    AK4619VN_ADDR       = 0x10
    CY8CMBR3108_ADDR    = 0x37
    EEPROM_24AA025_ADDR = 0x52

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
        0x40, # GRPPWM
        0x00, # GRPFREQ
        0xFF, # LEDOUT0
        0xFF, # LEDOUT1
        0xFF, # LEDOUT2
        0xFF, # LEDOUT3
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
            "codec_mute":     In(1, init=1),
            # I2C override from SoC, not used unless written to.
            "i2c_override":  In(i2c.I2CStreamerControl()),
        })

    def elaborate(self, platform):
        m = Module()

        m.submodules.i2c_stream = self.i2c_stream
        i2c = self.i2c_stream.control
        wiring.connect(m, wiring.flipped(self.pins), self.i2c_stream.pins)
        l_i2c_address = Signal.like(i2c.address)
        m.d.comb += i2c.address.eq(l_i2c_address)

        def state_id(ix):
            return (f"i2c_state{ix}", f"i2c_state{ix+1}", ix+1)

        def i2c_addr(m, ix, addr):
            # set i2c address of transactions being enqueued
            cur, nxt, ix = state_id(ix)
            with m.State(cur):
                m.d.sync += l_i2c_address.eq(addr),
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
        # mapping from sensor index (IC pin) to logical index (top to bottom
        # on the physical jacks in order).
        touch_order = Signal(data.ArrayLayout(unsigned(4), self.N_SENSORS))
        pmod_rev = TiliquaRevision.from_platform(platform).pmod_rev()
        sensor_order = pmod_rev.touch_order()
        for n in range(self.N_SENSORS):
            m.d.comb += touch_order[n].eq(sensor_order[n])

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
        # On PMOD R3.5+, there is also a soft mute on the audio
        # output path, which is controlled by `pdn_d` further down.
        #
        mute_count  = Signal(8)

        # R3.3 frontend soft mute sequencing
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
                    with m.If(startup_delay == 2**22): # ~70ms
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
            _,   _,   ix  = i2c_write(m, ix, 0xBA + (touch_order[touch_nsensor]<<1))
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
                        for n in range(self.N_SENSORS):
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
                with m.If(self.i2c_override.i.valid):
                    # Pending transaction from SoC?
                    m.next = "I2C-OVERRIDE"
                with m.Else():
                    # Go back to LED brightness update
                    m.next = s_loop_begin

            #
            # I2C OVERRIDE
            # Issue transaction from SoC, then go back to ordinary state machine.
            #

            with m.State("I2C-OVERRIDE"):
                wiring.connect(m, wiring.flipped(self.i2c_override), i2c)
                m.next = "I2C-OVERRIDE-WAIT"

            with m.State("I2C-OVERRIDE-WAIT"):
                wiring.connect(m, wiring.flipped(self.i2c_override), i2c)
                # Single transaction has been executed.
                with m.If(i2c.status.tx_empty & i2c.status.rx_empty & ~i2c.status.busy):
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

    # Calibrated sample streaming
    i_cal:  In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o_cal: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    # Touch sensing and jacksense outputs.
    touch: Out(8).array(8)
    jack: Out(8)
    touch_err: Out(8) # Roughly proportional to touch IC NACKs (0 is good)
    codec_mute: In(1) # Hold at 1 to soft mute CODEC
    hard_reset: In(1) # Strobe a 1 to hard reset the CODEC (pops!)

    # 1s for automatic audio -> LED control. 0s for manual.
    led_mode: In(8, init=0xff)
    # If an LED is in manual, this is signed i8 from -green to +red.
    led: In(8).array(8)

    def __init__(self, audio_clock):
        is_192 = audio_clock.is_192khz()
        self.i2stdm = I2STDM(audio_192=is_192)
        self.i2c_master = I2CMaster(audio_192=is_192)
        self.calibrator = I2SCalibrator()
        super().__init__()


    def elaborate(self, platform) -> Module:

        m = Module()

        #
        # AUDIO/CODEC CONTROL
        #

        m.submodules.i2stdm = i2stdm = self.i2stdm
        m.submodules.calibrator = calibrator = self.calibrator
        # I2STDM <-> I2S pins
        wiring.connect(m, i2stdm.i2s, wiring.flipped(self.pins.i2s))
        # I2STDM <-> calibrator
        m.d.comb += [
            calibrator.channel.eq(i2stdm.channel),
            calibrator.strobe.eq(i2stdm.strobe),
            calibrator.i_uncal.eq(i2stdm.o),
            i2stdm.i.eq(calibrator.o_uncal),
        ]
        # User core <-> calibrator
        wiring.connect(m, calibrator.o_cal, wiring.flipped(self.o_cal))
        wiring.connect(m, wiring.flipped(self.i_cal), calibrator.i_cal)

        #
        # I2C MASTER CONTROL (with global reset for CODEC re-init)
        #

        reset_i2c_master = Signal()
        m.submodules.i2c_master = i2c_master = ResetInserter(
                {"sync": reset_i2c_master})(self.i2c_master)

        # Hook up I2C master pins
        wiring.connect(m, i2c_master.pins, wiring.flipped(self.pins.i2c))
        m.d.comb += [
            # Hook up I2C master registers
            self.jack.eq(i2c_master.jack),
            self.touch_err.eq(i2c_master.touch_err),
            # Hook up coded mute control
            i2c_master.codec_mute.eq(self.codec_mute),
        ]

        #
        # LED/TOUCH HANDLING
        #

        for n in range(8):

            # Touch sense readings per jack
            m.d.comb += self.touch[n].eq(i2c_master.touch[n]),

            # LED auto/manual settings per jack
            with m.If(self.led_mode[n]):
                if n <= 3:
                    with m.If(self.jack[n]):
                        m.d.sync += i2c_master.led[n].eq(self.calibrator.o_cal_peek[n].as_value()>>8),
                    with m.Else():
                        m.d.sync += i2c_master.led[n].eq(0),
                else:
                    with m.If(self.i_cal.valid):
                        m.d.sync += i2c_master.led[n].eq(self.i_cal.payload[n-4].as_value()>>8),
            with m.Else():
                m.d.sync += i2c_master.led[n].eq(self.led[n]),


        pmod_rev = TiliquaRevision.from_platform(platform).pmod_rev()
        if pmod_rev == EurorackPmodRevision.R33:
            #
            # HW R4 / PMOD R3.3: CODEC PDN / FLIP-FLOP CLOCKING (HW R5 is different!)
            #
            # `eurorack-pmod` PCBA has a 'PDN' pin, which drives the CODEC PDN
            # pin. Between the ECP5 and the PDN pin is a flip-flop, such that
            # FPGA bitstream reconfiguration does not imply PDN toggling
            # (which causes a CODEC hard reset). Instead, for pop-free bitstream
            # switching (only on mobo R3+), we can sequence the flip-flop inputs
            # as needed.
            #
            # Note: CODEC RSTN must be asserted (held in reset) across the
            # FPGA reconfiguration. This is performed by `self.codec_mute`.
            #
            # TIMING
            # ------
            #
            # PDN_D   : ____________------------
            # PDN_CLK : ______------______------
            #           |           |
            #           ^ hard reset|
            #                       |
            #                       ^ soft reset
            #
            # hard reset: ensures flip-flop output is driven 0->1
            # soft reset: if flip-flop output was 1, it stays 1
            #

            # soft reset by default
            pdn_cnt = Signal(unsigned(32), init=(1<<20))
            m.d.comb += [
                self.pins.pdn_clk.eq(pdn_cnt[19]),
                self.pins.pdn_d  .eq(pdn_cnt[20]), # 2b11 @ ~35msec
            ]
            with m.If(~(self.pins.pdn_d & self.pins.pdn_clk)):
                m.d.sync += pdn_cnt.eq(pdn_cnt+1)
            with m.Elif(self.hard_reset):
                # hard reset only if requested
                m.d.sync += pdn_cnt.eq(0)
                m.d.comb += reset_i2c_master.eq(1)
        elif pmod_rev == EurorackPmodRevision.R35:
            # HW R5 / PMOD R3.5 mute / clocking.
            #
            # Latest output stage has a hardware soft mute that is always
            # enabled by default, so we can simply just pass through
            # codec_mute to this and don't have to worry about special
            # flip-flop clocking.
            #
            # Here we just toggle the flip flop CLK so that pdn_d is always
            # ~ equal to codec_mute, delayed a bit.
            #
            pdn_cnt = Signal(unsigned(32), init=(1<<20))
            m.d.sync += pdn_cnt.eq(pdn_cnt+1)
            m.d.comb += [
                self.pins.pdn_clk.eq(pdn_cnt[5]), # constant toggling
            ]
            with m.If(self.codec_mute):
                m.d.comb += self.pins.pdn_d.eq(0)
            with m.Else():
                m.d.comb += self.pins.pdn_d.eq(1)
        else:
            raise ValueError(f"Unsupported pmod_rev: {pmod_rev}")


        return m
