# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""Classes for representing DVI timings and video clock/PLL settings."""

from dataclasses import dataclass

@dataclass
class DVIModeline:
    """
    Video timing modelines. Values match the semantics used by xrandr, e.g.:

    $ xrandr --verbose
    ...
    640x480 (0x80) 25.175MHz -HSync -VSync
           h: width   640 start  656 end  752 total  800 skew    0 clock  31.47KHz
           v: height  480 start  490 end  492 total  525           clock  59.94Hz

    The mapping of each field is commented below.
    """

    h_active:      int  # width
    h_sync_start:  int  # start
    h_sync_end:    int  # end
    h_total:       int  # total
    h_sync_invert: bool # True for -HSync, False for +HSync
    v_active:      int  # height
    v_sync_start:  int  # start
    v_sync_end:    int  # end
    v_total:       int  # total
    v_sync_invert: bool # True for -VSync, False for +VSync

    # Note: when not using an external PLL for video, the correct
    # settings for a high-res ECP5 PLL must exist in DVIPLL.get()
    # for the desired frequency. This number is used to lookup
    # the PLL settings. On R4+, an external PLL is usually used
    # as it supports dynamic switching. R2/R3 don't have this.
    pixel_clk_mhz: float

    @property
    def active_pixels(self):
        return self.h_active * self.v_active

    @property
    def refresh_rate(self):
        return (self.pixel_clk_mhz*1e6)/(self.h_total * self.v_total)

    @staticmethod
    def all_timings():
        return {
            # CVT 640x480p59.94
            # Every DVI-compatible monitor should support this, according to the standard.
            # These numbers correspond directly to `xrandr --verbose`, if you're reading an EDID.
            "640x480p59.94": DVIModeline(
                h_active      = 640,
                h_sync_start  = 656,
                h_sync_end    = 752,
                h_total       = 800,
                h_sync_invert = True,
                v_active      = 480,
                v_sync_start  = 490,
                v_sync_end    = 492,
                v_total       = 525,
                v_sync_invert = True,
                pixel_clk_mhz = 25.175,
            ),

            # DMT 800x600p60
            "800x600p60": DVIModeline(
                h_active      = 800,
                h_sync_start  = 840,
                h_sync_end    = 968,
                h_total       = 1056,
                h_sync_invert = False,
                v_active      = 600,
                v_sync_start  = 601,
                v_sync_end    = 605,
                v_total       = 628,
                v_sync_invert = False,
                pixel_clk_mhz = 40,
            ),

            # DMT 1280x720p60
            "1280x720p60": DVIModeline(
                h_active      = 1280,
                h_sync_start  = 1390,
                h_sync_end    = 1430,
                h_total       = 1650,
                h_sync_invert = False,
                v_active      = 720,
                v_sync_start  = 725,
                v_sync_end    = 730,
                v_total       = 750,
                v_sync_invert = False,
                pixel_clk_mhz = 74.25,
            ),

            "1920x1080p30": DVIModeline(
                h_active      = 1920,
                h_sync_start  = 2008,
                h_sync_end    = 2052,
                h_total       = 2200,
                h_sync_invert = False,
                v_active      = 1080,
                v_sync_start  = 1084,
                v_sync_end    = 1089,
                v_total       = 1125,
                v_sync_invert = False,
                pixel_clk_mhz = 74.25,
            ),

            # BEGIN ODDBALL TIMINGS

            # Tiliqua screen (early proto)
            "720x720p60proto1": DVIModeline(
                h_active      = 720,
                h_sync_start  = 760,
                h_sync_end    = 780,
                h_total       = 820,
                h_sync_invert = False,
                v_active      = 720,
                v_sync_start  = 744,
                v_sync_end    = 748,
                v_total       = 760,
                v_sync_invert = False,
                pixel_clk_mhz = 37.40,
            ),

            # Tiliqua screen (production version)
            "720x720p60r2": DVIModeline(
                h_active      = 720,
                h_sync_start  = 760,
                h_sync_end    = 768,
                h_total       = 812,
                h_sync_invert = True,
                v_active      = 720,
                v_sync_start  = 770,
                v_sync_end    = 786,
                v_total       = 802,
                v_sync_invert = True,
                pixel_clk_mhz = 39.07,
            ),
        }

@dataclass
class DVIPLL:
    """
    Fixed hi-res PLL settings for a single ECP5 PLL instance, generating 'dvi' and 'dvi5x'
    domains. On HW R4+, these are not used and a programmable external PLL is used instead.
    """
    pixel_clk_mhz: float
    clki_div:      int
    clkop_div:     int
    clkop_cphase:  int
    clkos_div:     int
    clkos_cphase:  int
    clkos2_div:    int
    clkos2_cphase: int
    clkos2_cphase: int
    clkfb_div:     int

    @staticmethod
    def get(pixel_clk_mhz: float):
        all_plls = [
            # DVIPLL() instances are generated by looking at the results of incantations like:
            # $ ecppll -i 48 --clkout0 371.25 --highres --reset -f pll60.v
            # where clkout0 is 5x the pixel clock. clkos2_div set by inspection to clkos_div*5.
            DVIPLL(
                pixel_clk_mhz = 25.175,
                clki_div      = 9,
                clkop_div     = 59,
                clkop_cphase  = 9,
                clkos_div     = 5,
                clkos_cphase  = 0,
                clkos2_div    = 25,
                clkos2_cphase = 0,
                clkfb_div     = 2
            ),
            DVIPLL(
                pixel_clk_mhz = 40,
                clki_div      = 2,
                clkop_div     = 25,
                clkop_cphase  = 9,
                clkos_div     = 3,
                clkos_cphase  = 0,
                clkos2_div    = 15,
                clkos2_cphase = 0,
                clkfb_div     = 1
            ),
            DVIPLL(
                pixel_clk_mhz = 74.25,
                clki_div      = 15,
                clkop_div     = 58,
                clkop_cphase  = 9,
                clkos_div     = 2,
                clkos_cphase  = 0,
                clkos2_div    = 10,
                clkos2_cphase = 0,
                clkfb_div     = 4
            ),
            DVIPLL(
                pixel_clk_mhz = 37.40,
                clki_div      = 12,
                clkop_div     = 17,
                clkop_cphase  = 9,
                clkos_div     = 4,
                clkos_cphase  = 0,
                clkos2_div    = 20,
                clkos2_cphase = 0,
                clkfb_div     = 11
            ),
        ]

        for pll in all_plls:
            if pixel_clk_mhz == pll.pixel_clk_mhz:
                return pll

        raise ValueError(f"DVI PLL for {pixel_clk_mhz} MHz not present!")
