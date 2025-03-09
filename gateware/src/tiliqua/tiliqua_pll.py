# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: BSD-3-Clause

""" Tiliqua and SoldierCrab PLL configurations. """

import textwrap

from amaranth             import *
from amaranth.lib.cdc     import FFSynchronizer
from amaranth.lib         import wiring
from tiliqua.types        import *
from tiliqua.dvi_modeline import DVIModeline, DVIPLL
from dataclasses          import dataclass
from typing               import List, Optional

@dataclass
class ClockFrequencies:
    sync:  int # CPU, SoC, USB, most synchronous logic
    fast:  int # RAM controller (2x sync)
    audio: int # fs*256, audio master clock (codec MCLK)
    dvi:   int # Video pixel clock
    dvi5x: int # Video 5x pixel clock (DDR TMDS clock)

@dataclass
class ClockSettings:
    audio_clock: AudioClock
    default_modeline: Optional[DVIModeline]
    frequencies: ClockFrequencies

def clock_settings(audio_clock: AudioClock, default_modeline: DVIModeline) -> ClockSettings:
    """
    Calculate frequency of all clocks used by Tiliqua gateware given an intended PLL configuration.
    It should match what the PLLs end up generating, as these constants are used in downstream logic.
    """
    frequencies = ClockFrequencies(
        sync=60_000_000,
        fast=120_000_000,
        audio=None,
        dvi=None,
        dvi5x=None
    )
    frequencies.audio = audio_clock.mclk()
    if default_modeline is not None:
        frequencies.dvi = int(default_modeline.pixel_clk_mhz*1_000_000)
        frequencies.dvi5x = 5*int(default_modeline.pixel_clk_mhz*1_000_000)
    settings = ClockSettings(
        audio_clock=audio_clock,
        default_modeline=default_modeline,
        frequencies=frequencies
    )
    return settings

def create_dvi_pll(pll_settings: DVIPLL, clk48, reset, feedback, locked):
    """
    Create a fixed PLL to generate DVI clocks (depends on resolution selected).
    1x pixel clock and 5x (half DVI TDMS clock, output is DDR).
    """
    return Instance("EHXPLLL",
            # Clock in.
            i_CLKI=clk48,
            # Generated clock outputs.
            o_CLKOP=feedback,
            o_CLKOS=ClockSignal("dvi5x"),
            o_CLKOS2=ClockSignal("dvi"),
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
            p_CLKI_DIV        = pll_settings.clki_div,
            p_CLKOP_ENABLE    = "ENABLED",
            p_CLKOP_DIV       = pll_settings.clkop_div,
            p_CLKOP_CPHASE    = pll_settings.clkop_cphase,
            p_CLKOP_FPHASE    = 0,
            p_CLKOS_ENABLE    = "ENABLED",
            p_CLKOS_DIV       = pll_settings.clkos_div,
            p_CLKOS_CPHASE    = pll_settings.clkos_cphase,
            p_CLKOS_FPHASE    = 0,
            p_CLKOS2_ENABLE   = "ENABLED",
            p_CLKOS2_DIV      = pll_settings.clkos2_div,
            p_CLKOS2_CPHASE   = pll_settings.clkos2_cphase,
            p_CLKOS2_FPHASE   = 0,
            p_FEEDBK_PATH     = "CLKOP",
            p_CLKFB_DIV       = pll_settings.clkfb_div,
            # Internal feedback.
            i_CLKFB=feedback,
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

def create_dynamic_dvi_pll(reset, locked):
    """
    Create dynamic PLL to generate DVI clocks (locks to pixel frequency of external PLL).
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

class ClockStabilityMonitor(wiring.Component):
    """
    Synchronous reset generation for external clock.
    TODO: 'unlock' is not implemented, this only works ONCE.

    Begins with `reset_out` asserted.
    Deasserts `reset_out` once we have seen `clk_in` (`target_domain`)
    toggling for a while (from the perspective of `monitor_domain`).
    """
    clk_in: wiring.In(1)          # Clock input in `target_domain` (monitoried in `monitor_domain`)
    reset_out: wiring.Out(1)      # Synchronous reset in `target_domain`

    def __init__(self, *, monitor_domain="sync", target_domain="audio", counter_bits=8):
        super().__init__()
        self.monitor_domain = monitor_domain
        self.target_domain = target_domain
        self.counter_bits = counter_bits

    def elaborate(self, platform):
        m = Module()

        # Bring `clk_in` into `monitor_domain`
        clk_sync = Signal()
        prev_clk = Signal()
        m.submodules += DomainRenamer(self.monitor_domain)(
            FFSynchronizer(self.clk_in, clk_sync, reset=0)
        )

        # In `monitor_domain`, count transitions
        transition_count = Signal(self.counter_bits)
        reset_hold = Signal(reset=1)
        m.d[self.monitor_domain] += prev_clk.eq(clk_sync)
        with m.If(transition_count != (2**self.counter_bits - 1)):
            m.d.comb += reset_hold.eq(1)
            with m.If(clk_sync != prev_clk):
                m.d[self.monitor_domain] += transition_count.eq(transition_count + 1)
        with m.Else():
            m.d.comb += reset_hold.eq(0)

        # Bring `reset_sync` back to `target_domain`.
        m.submodules += DomainRenamer(self.target_domain)(
            FFSynchronizer(reset_hold, self.reset_out, reset=1)
        )

        return m

class TiliquaDomainGeneratorPLLExternal(Elaboratable):

    """
    Top-level clocks and resets for Tiliqua platform using 1 FPGA PLL and 2 external clocks (from si5351):

    sync, usb: 60 MHz (Main clock)
    fast:      120 MHz (PSRAM DDR clock)
    audio:     external PLL: 12.288 MHz or 49.152 MHz (audio CODEC master clock, divide by 256 for CODEC sample rate)
    dvi/dvi5x: video clocks, depend on resolution passed with `--resolution` flag.

    """

    clock_tree_base = """
    ┌─────────────[tiliqua-mobo]────────────────────────────[soldiercrab]─────────┐
    │                                      ┊┌─[48MHz OSC]                         │
    │                                      ┊└─>[ECP5 PLL]┐                        │
    │                                      ┊             ├>[sync]{sync:12.4f} MHz │
    │                                      ┊             ├>[usb] {sync:12.4f} MHz │
    │                                      ┊             └>[fast]{fast:12.4f} MHz │
    │ [25MHz OSC]──>[si5351 PLL]─┬>[clk0]─────────────────>[audio]{audio:11.4f} MHz │"""

    clock_tree_video = """
    │                            └>[clk1]───>[ECP5 PLL]─┐                         │
    │                                      ┊            ├─>[dvi]  {dvi:11.4f} MHz │
    │                                      ┊            └─>[dvi5x]{dvi5x:11.4f} MHz │
    └─────────────────────────────────────────────────────────────────────────────┘"""
    clock_tree_no_video = """
    │                            └>[clk1]─────────────────>[disable]              │
    └─────────────────────────────────────────────────────────────────────────────┘"""

    def __init__(self, settings: ClockSettings):
        super().__init__()
        self.settings = settings

    def prettyprint(self):
        print(textwrap.dedent(self.clock_tree_base).format(
            sync=self.settings.frequencies.sync/1e6,
            fast=self.settings.frequencies.fast/1e6,
            audio=self.settings.frequencies.audio/1e6,
            ))
        if self.settings.frequencies.dvi is not None:
            print(textwrap.dedent(self.clock_tree_video[1:]).format(
                dvi=self.settings.frequencies.dvi/1e6,
                dvi5x=self.settings.frequencies.dvi5x/1e6,
                ))
        else:
            print(textwrap.dedent(self.clock_tree_no_video[1:]))

    def elaborate(self, platform):
        m = Module()

        self.prettyprint()

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

        m.d.comb += [
            ClockSignal("raw48")     .eq(clk48),
            # external PLL clock domain with no synchronous reset.
            ClockSignal("expll_clk0").eq(platform.request("expll_clk0").i),
            ResetSignal("expll_clk0").eq(0),
            ClockSignal("expll_clk1").eq(platform.request("expll_clk1").i),
            ResetSignal("expll_clk1").eq(0),
        ]

        # Generate synchronous reset for audio domain (there is no internal
        # PLL between the external PLL clock and the audio domain).
        m.submodules.clock_monitor = clock_monitor = ClockStabilityMonitor(
            monitor_domain="sync",
            target_domain="expll_clk0"
        )
        m.d.comb += [
            clock_monitor.clk_in.eq(ClockSignal("expll_clk0")),
            ClockSignal("audio").eq(clock_monitor.clk_in),
            ResetSignal("audio").eq(clock_monitor.reset_out),
        ]

        # ecppll -i 48 --clkout0 60 --clkout1 120 --clkout2 50 --reset -f pll60.v
        # 60MHz for USB (currently also sync domain. fast is for DQS)

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
        if self.settings.default_modeline is not None:

            m.domains.dvi   = ClockDomain()
            m.domains.dvi5x = ClockDomain()

            locked_dvi   = Signal()
            m.submodules.pll_dvi = create_dynamic_dvi_pll(reset, locked_dvi)

            m.d.comb += [
                ResetSignal("dvi")  .eq(~locked_dvi),
                ResetSignal("dvi5x").eq(~locked_dvi),
            ]

            m.d.comb += [
                platform.request("led_a").o.eq(locked60),
                platform.request("led_b").o.eq(locked_dvi),
            ]

        # Derived clocks and resets
        m.d.comb += [
            ClockSignal("sync")  .eq(feedback60),
            ClockSignal("usb")   .eq(feedback60),

            ResetSignal("sync")  .eq(~locked60),
            ResetSignal("fast")  .eq(~locked60),
            ResetSignal("usb")   .eq(~locked60),
        ]

        return m

class TiliquaDomainGenerator2PLLs(Elaboratable):

    """
    Top-level clocks and resets for Tiliqua platform with 2 PLLs available:

    sync, usb: 60 MHz (Main clock)
    fast:      120 MHz (PSRAM DDR clock)
    audio:     12.5 MHz or 50 MHz (audio CODEC master clock, divide by 256 for CODEC sample rate)
    dvi/dvi5x: video clocks, depend on resolution passed with `--resolution` flag.

    """

    def __init__(self, settings: ClockSettings):
        super().__init__()
        self.settings = settings

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

        clkos2_dividers = {
            AudioClock.COARSE_48KHZ:  48,
            AudioClock.COARSE_192KHZ: 12,
        }
        # With 2 PLLs only coarse audio clocks are supported.
        assert self.settings.audio_clock in clkos2_dividers.keys()

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
                p_CLKOS2_DIV=clkos2_dividers[self.settings.audio_clock],
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
        if self.settings.default_modeline is not None:

            m.domains.dvi   = ClockDomain()
            m.domains.dvi5x = ClockDomain()

            feedback_dvi = Signal()
            locked_dvi   = Signal()

            pll_settings = DVIPLL.get(self.settings.default_modeline.pixel_clk_mhz)
            m.submodules.pll_dvi = create_dvi_pll(pll_settings, clk48,
                                                  reset, feedback_dvi, locked_dvi)

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

class TiliquaDomainGenerator4PLLs(Elaboratable):
    """
    Top-level clocks and resets for Tiliqua platform with 4 PLLs available:

    sync, usb: 60 MHz (Main clock)
    fast:      120 MHz (PSRAM DDR clock)
    audio:     12.288 MHz or 49.152 MHz (*hires* audio CODEC master clock, divide by 256 for CODEC sample rate)
    dvi/dvi5x: video clocks, depend on resolution passed with `--resolution` flag.
    """

    def __init__(self, settings: ClockSettings):
        super().__init__()
        self.settings = settings

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
        if self.settings.default_modeline is not None:

            m.domains.dvi   = ClockDomain()
            m.domains.dvi5x = ClockDomain()

            feedback_dvi = Signal()
            locked_dvi   = Signal()
            pll_settings = DVIPLL.get(self.settings.default_modeline.pixel_clk_mhz)
            m.submodules.pll_dvi = create_dvi_pll(pll_settings, clk48,
                                                  reset, feedback_dvi, locked_dvi)

            m.d.comb += [
                ResetSignal("dvi")  .eq(~locked_dvi),
                ResetSignal("dvi5x").eq(~locked_dvi),
            ]

        # With 4 PLLs available we can afford another high-res PLL for
        # the audio domains.
        feedback_audio  = Signal()
        locked_audio    = Signal()
        if self.settings.audio_clock == AudioClock.FINE_192KHZ:
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
                    a_ICP_CURRENT="12",
                    a_LPF_RESISTOR="8",
                    a_MFG_ENABLE_FILTEROPAMP="1",
                    a_MFG_GMCREF_SEL="2"
            )
        elif self.settings.audio_clock == AudioClock.FINE_48KHZ:
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
                    a_ICP_CURRENT="12",
                    a_LPF_RESISTOR="8",
                    a_MFG_ENABLE_FILTEROPAMP="1",
                    a_MFG_GMCREF_SEL="2"
            )
        else:
            raise ValueError("Unsupported audio PLL requested.")

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
