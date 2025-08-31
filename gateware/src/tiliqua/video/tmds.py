# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
#
# This is Amaranth TMDS encoder was inspired by the following verilog encoder:
# "Project F Library - TMDS Encoder for DVI"
#   - Original attribution:
#       Copyright Will Green
#       Open source hardware released under the MIT License
#       Learn more at https://projectf.io
#
# This implementation has an additional pipeline stage, for ~double Fmax.

"""DVI TMDS encoder implementation."""

from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out


class TMDSEncoder(wiring.Component):
    """
    TMDS (Transition Minimized Differential Signaling) Encoder for DVI.
    This component encodes 8-bit color data and 2-bit control data into
    10-bit TMDS symbols according to the DVI specification.

    This component operates in a `dvi` domain running at the pixel clock.
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

        # ========== PIPELINE STAGE ==========

        enc_qm_r = Signal(9)
        data_in_r = Signal(8)
        ctrl_in_r = Signal(2)
        de_r = Signal()
        m.d.dvi += [
            enc_qm_r.eq(enc_qm),
            data_in_r.eq(self.data_in),
            ctrl_in_r.eq(self.ctrl_in),
            de_r.eq(self.de)
        ]

        # Calculate disparity for DC balancing
        ones = Signal(signed(5))
        zeros = Signal(signed(5))
        balance = Signal(signed(5))

        # Count ones in encoded data
        m.d.comb += ones.eq(
            enc_qm_r[0] + enc_qm_r[1] + enc_qm_r[2] + enc_qm_r[3] +
            enc_qm_r[4] + enc_qm_r[5] + enc_qm_r[6] + enc_qm_r[7]
        )

        # Calculate zeros and balance
        m.d.comb += [
            zeros.eq(8 - ones),
            balance.eq(ones - zeros)
        ]

        # Main TMDS encoding process
        with m.If(~de_r):
            # Control data during blanking interval
            with m.Switch(ctrl_in_r):
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
                with m.If(enc_qm_r[8] == 0):
                    m.d.dvi += [
                        tmds_r.eq(Cat(~enc_qm_r[0:8], Const(0b10, 2))),
                        bias.eq(bias - balance)
                    ]
                with m.Else():
                    m.d.dvi += [
                        tmds_r.eq(Cat(enc_qm_r[0:8], Const(0b01, 2))),
                        bias.eq(bias + balance)
                    ]
            with m.Elif(((bias > 0) & (balance > 0)) | ((bias < 0) & (balance < 0))):
                m.d.dvi += [
                    tmds_r.eq(Cat(~enc_qm_r[0:8], enc_qm_r[8], Const(1, 1))),
                    bias.eq(bias + Cat(Const(0, 1), enc_qm_r[8], Const(0, 3)).as_signed() - balance)
                ]
            with m.Else():
                m.d.dvi += [
                    tmds_r.eq(Cat(enc_qm_r[0:8], enc_qm_r[8], Const(0, 1))),
                    bias.eq(bias - Cat(Const(0, 1), ~enc_qm_r[8], Const(0, 3)).as_signed() + balance)
                ]

        return m
