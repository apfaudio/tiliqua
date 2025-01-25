# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: BSD-3-Clause

""" Tiliqua and SoldierCrab PLL configurations. """

from amaranth.build             import *
from amaranth                    import *
from tiliqua                     import video
from amaranth.lib.cdc            import FFSynchronizer

def create_dvi_pll(pll_settings: video.DVIPLL, clk48, reset, locked):
    """
    Create a PLL to generate DVI clocks (depends on resolution selected).
    1x pixel clock and 5x (half DVI TDMS clock, output is DDR).
    """
    return Instance("EHXPLLL",
            # Clock in.
            i_CLKI=ClockSignal("expll_clk1"),
            # Generated clock outputs.
            o_CLKOP=ClockSignal("dvi5x"),
            o_CLKOS=ClockSignal("dvi"),
            # Status.
            o_LOCK=locked,
            # PLL parameters...
            p_PLLRST_ENA      = "ENABLED",
            p_INTFB_WAKE      = "DISABLED",
            p_STDBY_ENABLE    = "DISABLED",
            p_DPHASE_SOURCE   = "DISABLED",
            p_OUTDIVIDER_MUXA = "DIVA",
            p_OUTDIVIDER_MUXB = "DIVB",
            p_OUTDIVIDER_MUXC = "DIVC",
            p_OUTDIVIDER_MUXD = "DIVD",
            p_CLKI_DIV        = 1,
            p_CLKOP_ENABLE    = "ENABLED",
            p_CLKOP_DIV       = 2,
            p_CLKOP_CPHASE    = 0,
            p_CLKOP_FPHASE    = 0,
            p_CLKOS_ENABLE    = "ENABLED",
            p_CLKOS_DIV       = 10,
            p_CLKOS_CPHASE    = 0,
            p_CLKOS_FPHASE    = 0,
            p_FEEDBK_PATH     = "CLKOP",
            p_CLKFB_DIV       = 5,
            # Internal feedback.
            i_CLKFB=ClockSignal("dvi5x"),
            # Control signals.
            i_RST=reset,
            i_PHASESEL0=0,
            i_PHASESEL1=0,
            i_PHASEDIR=1,
            i_PHASESTEP=1,
            i_PHASELOADREG=1,
            i_STDBY=0,
            i_PLLWAKESYNC=0,
            # Output Enables.
            i_ENCLKOP=0,
            i_ENCLKOS=0,
            i_ENCLKOS2=0,
            i_ENCLKOS3=0,
            # Synthesis attributes.
            a_ICP_CURRENT="12",
            a_LPF_RESISTOR="8",
            a_MFG_ENABLE_FILTEROPAMP="1",
            a_MFG_GMCREF_SEL="2",
    )

class TiliquaDomainGenerator2PLLs(Elaboratable):

    """
    Top-level clocks and resets for Tiliqua platform with 2 PLLs available:

    sync, usb: 60 MHz (Main clock)
    fast:      120 MHz (PSRAM DDR clock)
    audio:     12.5 MHz or 50 MHz (audio CODEC master clock, divide by 256 for CODEC sample rate)
    dvi/dvi5x: video clocks, depend on resolution passed with `--resolution` flag.

    """

    def __init__(self, *, pixclk_pll=None, audio_192=False, clock_frequencies=None, clock_signal_name=None):
        super().__init__()
        self.pixclk_pll = pixclk_pll
        self.audio_192  = audio_192

        self.clocks_hz = {
            "sync":  60_000_000,
            "fast": 120_000_000,
            "audio": 50_000_000 if audio_192 else 12_500_000,
        }
        if isinstance(pixclk_pll, video.DVIPLL):
            self.clocks_hz |= {
                "dvi": int(pixclk_pll.pixel_clk_mhz*1_000_000),
                "dvi5x": 5*int(pixclk_pll.pixel_clk_mhz*1_000_000),
            }

        print("PLL outputs:", self.clocks_hz)

    def elaborate(self, platform):
        m = Module()

        # Create our domains.
        m.domains.sync   = ClockDomain()
        m.domains.usb    = ClockDomain()
        m.domains.fast   = ClockDomain()
        m.domains.audio  = ClockDomain()
        m.domains.raw48  = ClockDomain()

        clk48 = platform.request(platform.default_clk, dir='i').i
        reset  = Signal(init=0)

        # ecppll -i 48 --clkout0 60 --clkout1 120 --clkout2 50 --reset -f pll60.v
        # 60MHz for USB (currently also sync domain. fast is for DQS)

        m.d.comb += [
            ClockSignal("raw48").eq(clk48),
        ]

        feedback60 = Signal()
        locked60   = Signal()
        m.submodules.pll = Instance("EHXPLLL",

                # Clock in.
                i_CLKI=clk48,

                # Generated clock outputs.
                o_CLKOP=feedback60,
                o_CLKOS=ClockSignal("fast"),
                o_CLKOS2=ClockSignal("audio"),

                # Status.
                o_LOCK=locked60,

                # PLL parameters...
                p_PLLRST_ENA="ENABLED",
                p_INTFB_WAKE="DISABLED",
                p_STDBY_ENABLE="DISABLED",
                p_DPHASE_SOURCE="DISABLED",
                p_OUTDIVIDER_MUXA="DIVA",
                p_OUTDIVIDER_MUXB="DIVB",
                p_OUTDIVIDER_MUXC="DIVC",
                p_OUTDIVIDER_MUXD="DIVD",
                p_CLKI_DIV=4,
                p_CLKOP_ENABLE="ENABLED",
                p_CLKOP_DIV=10,
                p_CLKOP_CPHASE=4,
                p_CLKOP_FPHASE=0,
                p_CLKOS_ENABLE="ENABLED",
                p_CLKOS_DIV=5,
                p_CLKOS_CPHASE=4,
                p_CLKOS_FPHASE=0,
                p_CLKOS2_ENABLE="ENABLED",
                p_CLKOS2_DIV=12 if self.audio_192 else 48, # 50.0MHz (~195kHz) or 12.0MHz (~47kHz)
                p_CLKOS2_CPHASE=4,
                p_CLKOS2_FPHASE=0,
                p_FEEDBK_PATH="CLKOP",
                p_CLKFB_DIV=5,

                # Internal feedback.
                i_CLKFB=feedback60,

                # Control signals.
                i_RST=reset,
                i_PHASESEL0=0,
                i_PHASESEL1=0,
                i_PHASEDIR=1,
                i_PHASESTEP=1,
                i_PHASELOADREG=1,
                i_STDBY=0,
                i_PLLWAKESYNC=0,

                # Output Enables.
                i_ENCLKOP=0,
                i_ENCLKOS=0,
                i_ENCLKOS2=0,
                i_ENCLKOS3=0,

                # Synthesis attributes.
                a_ICP_CURRENT="12",
                a_LPF_RESISTOR="8"
        )

        # Video PLL and derived signals
        if self.pixclk_pll is not None:

            m.domains.dvi   = ClockDomain()
            m.domains.dvi5x = ClockDomain()

            locked_dvi   = Signal()
            m.submodules.pll_dvi = create_dvi_pll(self.pixclk_pll, clk48, reset, feedback_dvi, locked_dvi)

            m.d.comb += [
                ResetSignal("dvi")  .eq(~locked_dvi),
                ResetSignal("dvi5x").eq(~locked_dvi),
            ]

        # Derived clocks and resets
        m.d.comb += [
            ClockSignal("sync")  .eq(feedback60),
            ClockSignal("usb")   .eq(feedback60),

            ResetSignal("sync")  .eq(~locked60),
            ResetSignal("fast")  .eq(~locked60),
            ResetSignal("usb")   .eq(~locked60),
            ResetSignal("audio") .eq(~locked60),
        ]

        return m

class TiliquaDomainGenerator2PLLsEx(Elaboratable):

    """
    Top-level clocks and resets for Tiliqua platform with 2 FPGA PLLs plus external PLL:

    sync, usb: 60 MHz (Main clock)
    fast:      120 MHz (PSRAM DDR clock)
    audio:     external PLL: 12.288 MHz or 49.152 MHz (audio CODEC master clock, divide by 256 for CODEC sample rate)
    dvi/dvi5x: video clocks, depend on resolution passed with `--resolution` flag.

    """

    def __init__(self, *, pixclk_pll=None, audio_192=False, clock_frequencies=None, clock_signal_name=None):
        super().__init__()
        self.pixclk_pll = pixclk_pll
        self.audio_192  = audio_192

        self.clocks_hz = {
            "sync":  60_000_000,
            "fast": 120_000_000,
            "audio": 49_152_000 if audio_192 else 12_288_000,
        }
        if isinstance(pixclk_pll, video.DVIPLL):
            self.clocks_hz |= {
                "dvi": int(pixclk_pll.pixel_clk_mhz*1_000_000),
                "dvi5x": 5*int(pixclk_pll.pixel_clk_mhz*1_000_000),
            }

        print("PLL outputs:", self.clocks_hz)

    def elaborate(self, platform):
        m = Module()

        # Create our domains.
        m.domains.sync       = ClockDomain()
        m.domains.usb        = ClockDomain()
        m.domains.fast       = ClockDomain()
        m.domains.audio      = ClockDomain()
        m.domains.raw48      = ClockDomain()
        m.domains.expll_clk0 = ClockDomain()
        m.domains.expll_clk1 = ClockDomain()

        clk48 = platform.request(platform.default_clk, dir='i').i
        reset  = Signal(init=0)

        # ecppll -i 48 --clkout0 60 --clkout1 120 --clkout2 50 --reset -f pll60.v
        # 60MHz for USB (currently also sync domain. fast is for DQS)

        m.d.comb += [
            ClockSignal("raw48")     .eq(clk48),
            # external PLL clock domain with no synchronous reset.
            ClockSignal("expll_clk0").eq(platform.request("expll_clk0").i),
            ResetSignal("expll_clk0").eq(0),
            ClockSignal("expll_clk1").eq(platform.request("expll_clk1").i),
            ResetSignal("expll_clk1").eq(0),
        ]

        # External PLL: synchronous reset generation
        # TODO: 'unlock' is not implemented, this only works ONCE.
        #
        # Lift synchronous reset on "audio" clock domain once we have seen "raw_audio" toggling for a while
        # (from the perspective of "sync" domain) - i.e. the external PLL is initialized and alive.

        # Bring expll_clk0 into "sync" domain
        expll_clk0_sync = Signal()
        expll_clk0_l_sync = Signal()
        m.submodules += DomainRenamer("sync")(FFSynchronizer(ClockSignal("expll_clk0"), expll_clk0_sync, reset=0))

        # In "sync" domain, count transitions
        expll_clk0_cycles = Signal(8)
        expll_clk0_reset_sync = Signal(init=1)
        m.d.sync += expll_clk0_l_sync.eq(expll_clk0_sync)
        with m.If(expll_clk0_cycles != 0xff):
            m.d.comb += expll_clk0_reset_sync.eq(1)
            with m.If(expll_clk0_sync != expll_clk0_l_sync):
                m.d.sync += expll_clk0_cycles.eq(expll_clk0_cycles+1)
        with m.Else():
            m.d.comb += expll_clk0_reset_sync.eq(0)

        # Bring "reset_sync" back into "expll_clk0" domain.
        expll_clk0_reset = Signal()
        m.submodules += DomainRenamer("expll_clk0")(FFSynchronizer(expll_clk0_reset_sync, expll_clk0_reset, reset=1))

        # "audio" domain is expll_clk0 with a synchronous reset.
        m.d.comb += [
            ClockSignal("audio").eq(ClockSignal("expll_clk0")),
            ResetSignal("audio").eq(expll_clk0_reset),
        ]

        feedback60 = Signal()
        locked60   = Signal()
        m.submodules.pll = Instance("EHXPLLL",

                # Clock in.
                i_CLKI=clk48,

                # Generated clock outputs.
                o_CLKOP=feedback60,
                o_CLKOS=ClockSignal("fast"),

                # Status.
                o_LOCK=locked60,

                # PLL parameters...
                p_PLLRST_ENA="ENABLED",
                p_INTFB_WAKE="DISABLED",
                p_STDBY_ENABLE="DISABLED",
                p_DPHASE_SOURCE="DISABLED",
                p_OUTDIVIDER_MUXA="DIVA",
                p_OUTDIVIDER_MUXB="DIVB",
                p_OUTDIVIDER_MUXC="DIVC",
                p_OUTDIVIDER_MUXD="DIVD",
                p_CLKI_DIV=4,
                p_CLKOP_ENABLE="ENABLED",
                p_CLKOP_DIV=10,
                p_CLKOP_CPHASE=4,
                p_CLKOP_FPHASE=0,
                p_CLKOS_ENABLE="ENABLED",
                p_CLKOS_DIV=5,
                p_CLKOS_CPHASE=4,
                p_CLKOS_FPHASE=0,
                p_FEEDBK_PATH="CLKOP",
                p_CLKFB_DIV=5,

                # Internal feedback.
                i_CLKFB=feedback60,

                # Control signals.
                i_RST=reset,
                i_PHASESEL0=0,
                i_PHASESEL1=0,
                i_PHASEDIR=1,
                i_PHASESTEP=1,
                i_PHASELOADREG=1,
                i_STDBY=0,
                i_PLLWAKESYNC=0,

                # Output Enables.
                i_ENCLKOP=0,
                i_ENCLKOS=0,
                i_ENCLKOS2=0,
                i_ENCLKOS3=0,

                # Synthesis attributes.
                a_ICP_CURRENT="12",
                a_LPF_RESISTOR="8",
        )

        # Video PLL and derived signals
        if self.pixclk_pll is not None:

            m.domains.dvi   = ClockDomain()
            m.domains.dvi5x = ClockDomain()

            locked_dvi   = Signal()
            m.submodules.pll_dvi = create_dvi_pll(self.pixclk_pll, clk48, reset, locked_dvi)

            m.d.comb += [
                ResetSignal("dvi")  .eq(~locked_dvi),
                ResetSignal("dvi5x").eq(~locked_dvi),
            ]

        # Derived clocks and resets
        m.d.comb += [
            ClockSignal("sync")  .eq(feedback60),
            ClockSignal("usb")   .eq(feedback60),

            ResetSignal("sync")  .eq(~locked60),
            ResetSignal("fast")  .eq(~locked60),
            ResetSignal("usb")   .eq(~locked60),
        ]

        ex = [
            Resource(f"ex", 0,
                Subsignal("debug1",  Pins("1",  conn=("pmod", 0), dir='o')),
                Subsignal("debug2",  Pins("2",  conn=("pmod", 0), dir='o')),
                Subsignal("debug3",  Pins("3",  conn=("pmod", 0), dir='o')),
                Subsignal("debug4",  Pins("4",  conn=("pmod", 0), dir='o')),
                Subsignal("debug10", Pins("10", conn=("pmod", 0), dir='o')),
                Subsignal("debug9",  Pins("9",  conn=("pmod", 0), dir='o')),
                Subsignal("debug8",  Pins("8",  conn=("pmod", 0), dir='o')),
                Subsignal("debug7",  Pins("7",  conn=("pmod", 0), dir='o')),
                Attrs(IO_TYPE="LVCMOS33"),
            )
        ]
        platform.add_resources(ex)
        ex0 = platform.request("ex")

        m.d.comb += [
            platform.request("led_a").o.eq(locked60),
            platform.request("led_b").o.eq(locked_dvi),
            ex0.debug1.o.eq(ClockSignal("expll_clk0")),
            ex0.debug2.o.eq(ClockSignal("expll_clk1")),
            ex0.debug3.o.eq(ClockSignal("dvi")),
            ex0.debug4.o.eq(locked_dvi),
        ]


        return m

class TiliquaDomainGenerator4PLLs(Elaboratable):
    """
    Top-level clocks and resets for Tiliqua platform with 4 PLLs available:

    sync, usb: 60 MHz (Main clock)
    fast:      120 MHz (PSRAM DDR clock)
    audio:     12.288 MHz or 49.152 MHz (*hires* audio CODEC master clock, divide by 256 for CODEC sample rate)
    dvi/dvi5x: video clocks, depend on resolution passed with `--resolution` flag.
    """

    def __init__(self, *, pixclk_pll=None, audio_192=False, clock_frequencies=None, clock_signal_name=None):
        super().__init__()
        self.pixclk_pll = pixclk_pll
        self.audio_192  = audio_192

        self.clocks_hz = {
            "sync":  60_000_000,
            "fast": 120_000_000,
            "audio": 49_152_000 if audio_192 else 12_288_000,
        }
        if isinstance(pixclk_pll, video.DVIPLL):
            self.clocks_hz |= {
                "dvi": int(pixclk_pll.pixel_clk_mhz*1_000_000),
                "dvi5x": 5*int(pixclk_pll.pixel_clk_mhz*1_000_000),
            }

        print("PLL outputs:", self.clocks_hz)

    def elaborate(self, platform):
        m = Module()

        # Create our domains.
        m.domains.sync   = ClockDomain()
        m.domains.usb    = ClockDomain()
        m.domains.fast   = ClockDomain()
        m.domains.audio  = ClockDomain()
        m.domains.raw48  = ClockDomain()

        clk48 = platform.request(platform.default_clk, dir='i').i
        reset  = Signal(init=0)

        m.d.comb += [
            ClockSignal("raw48").eq(clk48),
        ]

        feedback60 = Signal()
        locked60   = Signal()
        m.submodules.pll = Instance("EHXPLLL",

                # Clock in.
                i_CLKI=clk48,

                # Generated clock outputs.
                o_CLKOP=feedback60,
                o_CLKOS=ClockSignal("fast"),

                # Status.
                o_LOCK=locked60,

                # PLL parameters...
                p_PLLRST_ENA="ENABLED",
                p_INTFB_WAKE="DISABLED",
                p_STDBY_ENABLE="DISABLED",
                p_DPHASE_SOURCE="DISABLED",
                p_OUTDIVIDER_MUXA="DIVA",
                p_OUTDIVIDER_MUXB="DIVB",
                p_OUTDIVIDER_MUXC="DIVC",
                p_OUTDIVIDER_MUXD="DIVD",
                p_CLKI_DIV=4,
                p_CLKOP_ENABLE="ENABLED",
                p_CLKOP_DIV=10,
                p_CLKOP_CPHASE=4,
                p_CLKOP_FPHASE=0,
                p_CLKOS_ENABLE="ENABLED",
                p_CLKOS_DIV=5,
                p_CLKOS_CPHASE=4,
                p_CLKOS_FPHASE=0,
                p_FEEDBK_PATH="CLKOP",
                p_CLKFB_DIV=5,

                # Internal feedback.
                i_CLKFB=feedback60,

                # Control signals.
                i_RST=reset,
                i_PHASESEL0=0,
                i_PHASESEL1=0,
                i_PHASEDIR=1,
                i_PHASESTEP=1,
                i_PHASELOADREG=1,
                i_STDBY=0,
                i_PLLWAKESYNC=0,

                # Output Enables.
                i_ENCLKOP=0,
                i_ENCLKOS=0,
                i_ENCLKOS2=0,
                i_ENCLKOS3=0,

                # Synthesis attributes.
                a_ICP_CURRENT="12",
                a_LPF_RESISTOR="8"
        )

        # Video PLL and derived signals
        if self.pixclk_pll is not None:

            m.domains.dvi   = ClockDomain()
            m.domains.dvi5x = ClockDomain()

            feedback_dvi = Signal()
            locked_dvi   = Signal()
            m.submodules.pll_dvi = create_dvi_pll(self.pixclk_pll, clk48, reset, feedback_dvi, locked_dvi)

            m.d.comb += [
                ResetSignal("dvi")  .eq(~locked_dvi),
                ResetSignal("dvi5x").eq(~locked_dvi),
            ]

        # With 4 PLLs available we can afford another high-res PLL for
        # the audio domains.
        feedback_audio  = Signal()
        locked_audio    = Signal()
        if self.audio_192:
            # 49.152MHz for 256*Fs Audio domain (192KHz Fs)
            # ecppll -i 48 --clkout0 49.152 --highres --reset -f pll2.v
            m.submodules.audio_pll = Instance("EHXPLLL",
                    # Status.
                    o_LOCK=locked_audio,
                    # PLL parameters...
                    p_PLLRST_ENA="ENABLED",
                    p_INTFB_WAKE="DISABLED",
                    p_STDBY_ENABLE="DISABLED",
                    p_DPHASE_SOURCE="DISABLED",
                    p_OUTDIVIDER_MUXA="DIVA",
                    p_OUTDIVIDER_MUXB="DIVB",
                    p_OUTDIVIDER_MUXC="DIVC",
                    p_OUTDIVIDER_MUXD="DIVD",
                    p_CLKI_DIV = 13,
                    p_CLKOP_ENABLE = "ENABLED",
                    p_CLKOP_DIV = 71,
                    p_CLKOP_CPHASE = 9,
                    p_CLKOP_FPHASE = 0,
                    p_CLKOS_ENABLE = "ENABLED",
                    p_CLKOS_DIV = 16,
                    p_CLKOS_CPHASE = 0,
                    p_CLKOS_FPHASE = 0,
                    p_FEEDBK_PATH = "CLKOP",
                    p_CLKFB_DIV = 3,
                    # Clock in.
                    i_CLKI=clk48,
                    # Internal feedback.
                    i_CLKFB=feedback_audio,
                    # Control signals.
                    i_RST=reset,
                    i_PHASESEL0=0,
                    i_PHASESEL1=0,
                    i_PHASEDIR=1,
                    i_PHASESTEP=1,
                    i_PHASELOADREG=1,
                    i_STDBY=0,
                    i_PLLWAKESYNC=0,
                    # Output Enables.
                    i_ENCLKOP=0,
                    i_ENCLKOS2=0,
                    # Generated clock outputs.
                    o_CLKOP=feedback_audio,
                    o_CLKOS=ClockSignal("audio"),
                    # Synthesis attributes.
                    a_FREQUENCY_PIN_CLKI="48",
                    a_FREQUENCY_PIN_CLKOS="12.288",
                    a_ICP_CURRENT="12",
                    a_LPF_RESISTOR="8",
                    a_MFG_ENABLE_FILTEROPAMP="1",
                    a_MFG_GMCREF_SEL="2"
            )
        else:
            # 12.288MHz for 256*Fs Audio domain (48KHz Fs)
            # ecppll -i 48 --clkout0 12.288 --highres --reset -f pll2.v
            m.submodules.audio_pll = Instance("EHXPLLL",
                    # Status.
                    o_LOCK=locked_audio,
                    # PLL parameters...
                    p_PLLRST_ENA="ENABLED",
                    p_INTFB_WAKE="DISABLED",
                    p_STDBY_ENABLE="DISABLED",
                    p_DPHASE_SOURCE="DISABLED",
                    p_OUTDIVIDER_MUXA="DIVA",
                    p_OUTDIVIDER_MUXB="DIVB",
                    p_OUTDIVIDER_MUXC="DIVC",
                    p_OUTDIVIDER_MUXD="DIVD",
                    p_CLKI_DIV = 5,
                    p_CLKOP_ENABLE = "ENABLED",
                    p_CLKOP_DIV = 32,
                    p_CLKOP_CPHASE = 9,
                    p_CLKOP_FPHASE = 0,
                    p_CLKOS_ENABLE = "ENABLED",
                    p_CLKOS_DIV = 50,
                    p_CLKOS_CPHASE = 0,
                    p_CLKOS_FPHASE = 0,
                    p_FEEDBK_PATH = "CLKOP",
                    p_CLKFB_DIV = 2,
                    # Clock in.
                    i_CLKI=clk48,
                    # Internal feedback.
                    i_CLKFB=feedback_audio,
                    # Control signals.
                    i_RST=reset,
                    i_PHASESEL0=0,
                    i_PHASESEL1=0,
                    i_PHASEDIR=1,
                    i_PHASESTEP=1,
                    i_PHASELOADREG=1,
                    i_STDBY=0,
                    i_PLLWAKESYNC=0,
                    # Output Enables.
                    i_ENCLKOP=0,
                    i_ENCLKOS2=0,
                    # Generated clock outputs.
                    o_CLKOP=feedback_audio,
                    o_CLKOS=ClockSignal("audio"),
                    # Synthesis attributes.
                    a_FREQUENCY_PIN_CLKI="48",
                    a_FREQUENCY_PIN_CLKOS="12.288",
                    a_ICP_CURRENT="12",
                    a_LPF_RESISTOR="8",
                    a_MFG_ENABLE_FILTEROPAMP="1",
                    a_MFG_GMCREF_SEL="2"
            )

        # Derived clocks and resets
        m.d.comb += [
            ClockSignal("sync")  .eq(feedback60),
            ClockSignal("usb")   .eq(feedback60),

            ResetSignal("sync")  .eq(~locked60),
            ResetSignal("fast")  .eq(~locked60),
            ResetSignal("usb")   .eq(~locked60),
            ResetSignal("audio") .eq(~locked_audio),
        ]

        return m
