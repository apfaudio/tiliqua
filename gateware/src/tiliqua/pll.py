# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: BSD-3-Clause

""" Tiliqua and SoldierCrab PLL configurations. """

import enum
import textwrap
from dataclasses import dataclass
from typing import Optional

from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.cdc import FFSynchronizer

from .video.modeline import DVIPLL, DVIModeline


class AudioClock(str, enum.Enum):
    FINE_48KHZ  = "fine_48khz"
    FINE_192KHZ = "fine_192khz"
    COARSE_48KHZ  = "coarse_48khz"
    COARSE_192KHZ = "coarse_192khz"

    def mclk(self):
        return {
            self.FINE_48KHZ: 12_288_000,
            self.FINE_192KHZ: 49_152_000,
            self.COARSE_48KHZ: 12_500_000, # These don't need an extra PLL.
            self.COARSE_192KHZ: 50_000_000,
        }[self]

    def fs(self):
        return self.mclk() // 256

    def to_192khz(self):
        return {
            self.FINE_48KHZ: self.FINE_192KHZ,
            self.COARSE_48KHZ: self.COARSE_192KHZ,
        }[self]

    def is_192khz(self):
        return self in [
            self.FINE_192KHZ,
            self.COARSE_192KHZ,
        ]

# Maximum allowed pixel clock that may be set by external PLL when `dynamic_modeline`
# is used. Synthesis is performed using this frequency as a constraint, even if
# the true frequency determined at runtime may be lower.
PCLK_FMAX_DYNAMIC = 74250000

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
    dynamic_modeline: bool
    modeline: Optional[DVIModeline]
    frequencies: ClockFrequencies

    def __init__(self, audio_clock: AudioClock, dynamic_modeline: bool,
                       modeline: Optional[DVIModeline]):

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

        if dynamic_modeline and modeline is not None:
            raise ValueError(
                "Both `dynamic_modeline` and fixed `modeline` are set. Only one may be set.")

        if modeline is not None:
            frequencies.dvi = int(modeline.pixel_clk_mhz*1_000_000)
            frequencies.dvi5x = 5*int(modeline.pixel_clk_mhz*1_000_000)

        if dynamic_modeline:
            frequencies.dvi = int(PCLK_FMAX_DYNAMIC)
            frequencies.dvi5x = 5*int(PCLK_FMAX_DYNAMIC)

        self.audio_clock = audio_clock
        self.dynamic_modeline = dynamic_modeline
        self.modeline = modeline
        self.frequencies = frequencies

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

    WARN: It's easy to drive this out of spec. To stay inside the VCO frequency of
    400-800MHz (spec from Trellis), clk1 (pixel clock) should be between 40MHz and
    80MHz. However, it seems experimentaly reliable to lock at lower frequencies,
    at least according to the notes from [1]. Even though 25Mhz for 640x480 is
    way out of spec for this PLL configuration, it seems to work fine.

    [1] https://github.com/YosysHQ/prjtrellis/pull/117
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
    dvi/dvi5x: video clocks, depend on selected resolution.

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
    │                                      ┊            ├─>[dvi]  {dvi:11.4f} MHz │ {dyn1}
    │                                      ┊            └─>[dvi5x]{dvi5x:11.4f} MHz │ {dyn2}
    └─────────────────────────────────────────────────────────────────────────────┘"""
    clock_tree_no_video = """
    │                            └>[clk1]─────────────────>[disable]              │
    └─────────────────────────────────────────────────────────────────────────────┘"""

    def __init__(self, settings: ClockSettings):
        super().__init__()
        self.reset_dvi_pll = Signal(init=0)
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
                dyn1='(dynamic)' if self.settings.dynamic_modeline else '',
                dyn2='(dynamic)' if self.settings.dynamic_modeline else '',
                ))
            if self.settings.dynamic_modeline:
                print("PLL configured for DYNAMIC video mode (maximum pixel clock shown).")
            else:
                print(f"PLL configured for STATIC video mode: {self.settings.modeline}.")
        else:
            print(textwrap.dedent(self.clock_tree_no_video[1:]))
            print("Video clocks disabled (no video out).")

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
        if self.settings.modeline or self.settings.dynamic_modeline:
            m.domains.expll_clk1 = ClockDomain()

        clk48 = platform.request(platform.default_clk, dir='i').i
        reset = Signal(init=0)

        m.d.comb += [
            ClockSignal("raw48")     .eq(clk48),
            # external PLL clock domain with no synchronous reset.
            ClockSignal("expll_clk0").eq(platform.request("clkex", 0).i),
            ResetSignal("expll_clk0").eq(0),
        ]

        if self.settings.modeline or self.settings.dynamic_modeline:
            m.d.comb += [
                ClockSignal("expll_clk1").eq(platform.request("clkex", 1).i),
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

        m.d.comb += platform.request("led_b").o.eq(ResetSignal("audio")),

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
        if self.settings.modeline or self.settings.dynamic_modeline:

            m.domains.dvi   = ClockDomain()
            m.domains.dvi5x = ClockDomain()

            locked_dvi = Signal()
            m.submodules.pll_dvi = create_dynamic_dvi_pll(self.reset_dvi_pll, locked_dvi)

            m.d.comb += [
                ResetSignal("dvi")  .eq(~locked_dvi),
                ResetSignal("dvi5x").eq(~locked_dvi),
            ]

            # LED off when DVI PLL locked
            m.d.comb += platform.request("led_a").o.eq(ResetSignal("dvi"))

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

        if self.settings.frequencies.dvi is not None:
            print(f"PLL configured for STATIC video mode: {self.settings.modeline}.")

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

        if self.settings.modeline is not None:

            m.domains.dvi   = ClockDomain()
            m.domains.dvi5x = ClockDomain()

            feedback_dvi = Signal()
            locked_dvi   = Signal()

            pll_settings = DVIPLL.get(self.settings.modeline.pixel_clk_mhz)
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

        if self.settings.frequencies.dvi is not None:
            print(f"PLL configured for STATIC video mode: {self.settings.modeline}.")

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

        if self.settings.modeline is not None:

            m.domains.dvi   = ClockDomain()
            m.domains.dvi5x = ClockDomain()

            feedback_dvi = Signal()
            locked_dvi   = Signal()
            pll_settings = DVIPLL.get(self.settings.modeline.pixel_clk_mhz)
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
