# DVI PHY implementation (TMDS Encoder and DDR driver)
#
# This is an Amaranth rewrite of the DVI core in:
# "Project F Library - TMDS Encoder for DVI"
#   - Original attribution:
#       Copyright Will Green
#       Open source hardware released under the MIT License
#       Learn more at https://projectf.io

from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out

class TMDSEncoderDVI(wiring.Component):
    """
    TMDS (Transition Minimized Differential Signaling) Encoder for DVI
    This component encodes 8-bit color data and 2-bit control data into
    10-bit TMDS symbols according to the DVI specification.
    """

    data_in: In(8)    # Color data
    ctrl_in: In(2)    # Control data
    de: In(1)         # Data enable
    tmds: Out(10)     # Encoded TMDS data

    def elaborate(self, platform):
        m = Module()

        # Register for output
        tmds_r = Signal(10, init=0b1101010100) # equivalent to ctrl 2'b00
        m.d.comb += self.tmds.eq(tmds_r)

        # Register for ongoing DC bias
        bias = Signal(signed(5), init=0)

        # Select basic encoding based on number of ones in the input data
        data_1s = Signal(4)
        use_xnor = Signal()

        # Calculate number of ones in data_in (manually unrolled for clarity)
        m.d.comb += data_1s.eq(
            self.data_in[0] + self.data_in[1] + self.data_in[2] + self.data_in[3] +
            self.data_in[4] + self.data_in[5] + self.data_in[6] + self.data_in[7]
        )

        # Determine encoding type
        m.d.comb += use_xnor.eq((data_1s > 4) | ((data_1s == 4) & (self.data_in[0] == 0)))

        # Encode color data with xor/xnor
        enc_qm = Signal(9)

        # First bit is unmodified
        m.d.comb += enc_qm[0].eq(self.data_in[0])

        # Generate the remaining bits using xor/xnor
        for i in range(7):
            m.d.comb += enc_qm[i+1].eq(Mux(
                use_xnor,
                enc_qm[i] ^ ~self.data_in[i+1],  # XNOR
                enc_qm[i] ^ self.data_in[i+1]    # XOR
            ))

        # Set indicator bit
        m.d.comb += enc_qm[8].eq(~use_xnor)

        # Calculate disparity for DC balancing
        ones = Signal(signed(5))
        zeros = Signal(signed(5))
        balance = Signal(signed(5))

        # Count ones in encoded data
        m.d.comb += ones.eq(
            enc_qm[0] + enc_qm[1] + enc_qm[2] + enc_qm[3] +
            enc_qm[4] + enc_qm[5] + enc_qm[6] + enc_qm[7]
        )

        # Calculate zeros and balance
        m.d.comb += [
            zeros.eq(8 - ones),
            balance.eq(ones - zeros)
        ]

        # Main TMDS encoding process
        with m.If(~self.de):
            # Control data during blanking interval
            with m.Switch(self.ctrl_in):
                with m.Case(0b00):
                    m.d.dvi += tmds_r.eq(0b1101010100)
                with m.Case(0b01):
                    m.d.dvi += tmds_r.eq(0b0010101011)
                with m.Case(0b10):
                    m.d.dvi += tmds_r.eq(0b0101010100)
                with m.Default():
                    m.d.dvi += tmds_r.eq(0b1010101011)
            # Reset bias
            m.d.dvi += bias.eq(0)

        with m.Else():
            # Pixel color data logic
            with m.If((bias == 0) | (balance == 0)):
                # No prior bias or disparity
                with m.If(enc_qm[8] == 0):
                    m.d.dvi += [
                        tmds_r.eq(Cat(~enc_qm[0:8], Const(0b10, 2))),
                        bias.eq(bias - balance)
                    ]
                with m.Else():
                    m.d.dvi += [
                        tmds_r.eq(Cat(enc_qm[0:8], Const(0b01, 2))),
                        bias.eq(bias + balance)
                    ]
            with m.Elif(((bias > 0) & (balance > 0)) | ((bias < 0) & (balance < 0))):
                m.d.dvi += [
                    tmds_r.eq(Cat(~enc_qm[0:8], enc_qm[8], Const(1, 1))),
                    bias.eq(bias + Cat(Const(0, 3), enc_qm[8], Const(0, 1)).as_signed() - balance)
                ]
            with m.Else():
                m.d.dvi += [
                    tmds_r.eq(Cat(enc_qm[0:8], enc_qm[8], Const(0, 1))),
                    bias.eq(bias - Cat(Const(0, 3), ~enc_qm[8], Const(0, 1)).as_signed() + balance)
                ]

        return m

class DVIGenerator(wiring.Component):
    """
    DVI Generator module for ECP5

    This component generates DVI signals by encoding data using TMDS encoders
    and serializing it for output.

    Note: Assumes existing clock domains 'dvi' (pixel clock) and 'dvi5x' (5x pixel clock)
    """

    # Video signals
    de: In(1)          # Data enable (high when drawing)

    # Channel data and control inputs
    data_in_ch0: In(8)  # Channel 0 - data
    data_in_ch1: In(8)  # Channel 1 - data
    data_in_ch2: In(8)  # Channel 2 - data
    ctrl_in_ch0: In(2)  # Channel 0 - control
    ctrl_in_ch1: In(2)  # Channel 1 - control
    ctrl_in_ch2: In(2)  # Channel 2 - control

    # Serial TMDS outputs
    tmds_ch0_serial: Out(1)  # Channel 0 - serial TMDS
    tmds_ch1_serial: Out(1)  # Channel 1 - serial TMDS
    tmds_ch2_serial: Out(1)  # Channel 2 - serial TMDS
    tmds_clk_serial: Out(1)  # Clock - serial TMDS

    def elaborate(self, platform):
        m = Module()

        # TMDS encoded signals
        tmds_ch0 = Signal(10)
        tmds_ch1 = Signal(10)
        tmds_ch2 = Signal(10)
        # Instantiate TMDS encoders for each channel
        m.submodules.encode_ch0 = encode_ch0 = TMDSEncoderDVI()
        m.submodules.encode_ch1 = encode_ch1 = TMDSEncoderDVI()
        m.submodules.encode_ch2 = encode_ch2 = TMDSEncoderDVI()

        # Connect TMDS encoder inputs
        m.d.comb += [
            # Channel 0
            encode_ch0.data_in.eq(self.data_in_ch0),
            encode_ch0.ctrl_in.eq(self.ctrl_in_ch0),
            encode_ch0.de.eq(self.de),
            tmds_ch0.eq(encode_ch0.tmds),
            # Channel 1
            encode_ch1.data_in.eq(self.data_in_ch1),
            encode_ch1.ctrl_in.eq(self.ctrl_in_ch1),
            encode_ch1.de.eq(self.de),
            tmds_ch1.eq(encode_ch1.tmds),
            # Channel 2
            encode_ch2.data_in.eq(self.data_in_ch2),
            encode_ch2.ctrl_in.eq(self.ctrl_in_ch2),
            encode_ch2.de.eq(self.de),
            tmds_ch2.eq(encode_ch2.tmds)
        ]

        # Register TMDS signals in the DVI clock domain
        s_tmds_ch0 = Signal(10)
        s_tmds_ch1 = Signal(10)
        s_tmds_ch2 = Signal(10)

        m.d.dvi += [
            s_tmds_ch0.eq(tmds_ch0),
            s_tmds_ch1.eq(tmds_ch1),
            s_tmds_ch2.eq(tmds_ch2)
        ]

        # Serialization logic
        tmds_ch0_shift = Signal(10)
        tmds_ch1_shift = Signal(10)
        tmds_ch2_shift = Signal(10)

        # 5-bit circular shift buffer
        shift5 = Signal(5, reset=1)

        # Serialization in the 5x DVI clock domain
        m.d.dvi5x += [
            shift5.eq(Cat(shift5[4], shift5[0:4]))
        ]

        with m.If(shift5[0]):
            m.d.dvi5x += [
                tmds_ch0_shift.eq(s_tmds_ch0),
                tmds_ch1_shift.eq(s_tmds_ch1),
                tmds_ch2_shift.eq(s_tmds_ch2)
            ]
        with m.Else():
            m.d.dvi5x += [
                tmds_ch0_shift.eq(Cat(tmds_ch0_shift[2:10], Const(0, 2))),
                tmds_ch1_shift.eq(Cat(tmds_ch1_shift[2:10], Const(0, 2))),
                tmds_ch2_shift.eq(Cat(tmds_ch2_shift[2:10], Const(0, 2)))
            ]

        m.submodules += Instance("ODDRX1F",
            i_D0=tmds_ch0_shift[0],
            i_D1=tmds_ch0_shift[1],
            i_SCLK=ClockSignal("dvi5x"),
            i_RST=Const(0, 1),
            o_Q=self.tmds_ch0_serial
        )

        m.submodules += Instance("ODDRX1F",
            i_D0=tmds_ch1_shift[0],
            i_D1=tmds_ch1_shift[1],
            i_SCLK=ClockSignal("dvi5x"),
            i_RST=Const(0, 1),
            o_Q=self.tmds_ch1_serial
        )

        m.submodules += Instance("ODDRX1F",
            i_D0=tmds_ch2_shift[0],
            i_D1=tmds_ch2_shift[1],
            i_SCLK=ClockSignal("dvi5x"),
            i_RST=Const(0, 1),
            o_Q=self.tmds_ch2_serial
        )

        # Clock output
        m.d.comb += self.tmds_clk_serial.eq(ClockSignal("dvi"))

        return m
