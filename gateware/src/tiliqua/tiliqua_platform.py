# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: BSD-3-Clause

""" Tiliqua and SoldierCrab platform definitions. """

from amaranth                    import *
from amaranth.build              import *
from amaranth.lib                import wiring
from amaranth.vendor             import LatticeECP5Platform

from amaranth_boards.resources   import *

from luna.gateware.platform.core import LUNAPlatform

from tiliqua                     import tiliqua_pll
from tiliqua.types               import *

class _SoldierCrabPlatform(LatticeECP5Platform):
    package      = "BG256"
    default_clk  = "clk48"
    default_rst  = "rst"

    # ULPI and PSRAM can both be populated with 3V3 or 1V8 parts -
    # the IOTYPE of bank 6 and 7 must match. U4 and R16 determine
    # which voltage these banks are supplied with.

    def bank_6_7_iotype(self):
        assert self.ulpi_psram_voltage in ["1V8", "3V3"]
        return "LVCMOS18" if self.ulpi_psram_voltage == "1V8" else "LVCMOS33"

    def bank_6_7_iotype_d(self):
        # 1V8 doesn't support LVCMOS differential outputs.
        # TODO(future): switch this to SSTL?
        if "18" not in self.bank_6_7_iotype():
            return self.bank_6_7_iotype() + "D"
        return self.bank_6_7_iotype()

    # Connections inside soldiercrab SoM.

    resources = [
        # 48MHz master
        Resource("clk48", 0, Pins("A8", dir="i"), Clock(48e6), Attrs(IO_TYPE="LVCMOS33")),

        # PROGRAMN, triggers warm self-reconfiguration
        Resource("self_program", 0, PinsN("T13", dir="o"),
                 Attrs(IO_TYPE="LVCMOS33", PULLMODE="UP")),

        # Indicator LEDs
        Resource("led_a", 0, PinsN("T14", dir="o"),  Attrs(IO_TYPE="LVCMOS33")),
        Resource("led_b", 0, PinsN("T15", dir="o"),  Attrs(IO_TYPE="LVCMOS33")),

        # USB2 PHY
        ULPIResource("ulpi", 0,
            data="N1 M2 M1 L2 L1 K2 K1 K3",
            clk="T3", clk_dir="o", dir="P2", nxt="P1",
            stp="R2", rst="T2", rst_invert=True,
            attrs=Attrs(IO_TYPE=bank_6_7_iotype)
        ),

        # oSPIRAM / HyperRAM
        Resource("ram", 0,
            Subsignal("clk",   DiffPairs("C3", "D3", dir="o"),
                      Attrs(IO_TYPE=bank_6_7_iotype_d)),
            Subsignal("dq",    Pins("F2 B1 C2 E1 E3 E2 F3 G4", dir="io")),
            Subsignal("rwds",  Pins( "D1", dir="io")),
            Subsignal("cs",    PinsN("B2", dir="o")),
            Subsignal("reset", PinsN("C1", dir="o")),
            Attrs(IO_TYPE=bank_6_7_iotype)
        ),

        # Configuration SPI flash
        Resource("spi_flash", 0,
            # Note: SCK needs to go through a USRMCLK instance.
            Subsignal("sdi",  Pins("T8",  dir="o")),
            Subsignal("sdo",  Pins("T7",  dir="i")),
            Subsignal("cs",   PinsN("N8", dir="o")),
            Attrs(IO_TYPE="LVCMOS33")
        ),

        # Connection to our SPI flash but using quad mode (QSPI)
        Resource("qspi_flash", 0,
            # SCK is on pin 9; but doesn't have a traditional I/O buffer.
            # Instead, we'll need to drive a clock into a USRMCLK instance.
            # See interfaces/flash.py for more information.
            Subsignal("dq",  Pins("T8 T7 M7 N7",  dir="io")),
            Subsignal("cs",  PinsN("N8", dir="o")),
            Attrs(IO_TYPE="LVCMOS33")
        ),

        # Pseudo-supply pins - connected to supply voltage or GND for routing reasons.
        Resource("pseudo_vccio", 0,
                 Pins("E6 E7 D10 E10 E11 F12 J12 K12 L12 N13 P13 M11 P11 P12 R6", dir="o"),
                 Attrs(IO_TYPE="LVCMOS33")),

        Resource("pseudo_gnd", 0,
                 Pins("E5 E8 E9 E12 F13 M13 M12 N12 N11", dir="o"),
                 Attrs(IO_TYPE="LVCMOS33")),

        Resource("pseudo_vccram", 0,
                 Pins("L4 M4 R5 N5 P4 M6 F5 G5 H5 H4 J4 J5 J3 J1 J2", dir="o"),
                 Attrs(IO_TYPE=bank_6_7_iotype)),

        Resource("pseudo_gndram", 0,
                 Pins("L5 L3 M3 N6 P5 P6 F4 G2 G3 H3 H2", dir="o"),
                 Attrs(IO_TYPE=bank_6_7_iotype)),

    ]

class SoldierCrabR2Platform(_SoldierCrabPlatform):
    device             = "LFE5U-45F"
    speed              = "7"
    ulpi_psram_voltage = "3V3"
    psram_id           = "7KL1282GAHY02"
    psram_registers    = []

    connectors  = [
        Connector("m2", 0,
            # 'E' side of slot (23 physical pins + 8 virtual pins)
            # Pins  1 .. 20 (inclusive)
            "-     -   -   -   -  C4  -  D5   - T10  A3   -  A2   -  B3   -  B4 R11  A4  E4 "
            # Pins 21 .. 30
            "T11  D4 M10   -   -   -  -   -   -   - "
            # Other side of slot (45 physical pins)
            # Pins 31 .. 50
            "-    D6   -  C5  B5   - A5  C6   -  C7  B6  D7  A6  D8   -  C9  B7 C10   -  D9 "
            # Pins 51 .. 70
            "A7  B11  B8 C11  A9 D13 B9 C13 A10 B13 B10 A13 B15 A14 A15 B14 C15 C14 B16 D14 "
            # Pins 71 .. 75
            "C16   - D16   -  -" ),
    ]

class SoldierCrabR3Platform(_SoldierCrabPlatform):
    device             = "LFE5U-25F"
    speed              = "6"
    ulpi_psram_voltage = "1V8"
    psram_id           = "APS256XXN-OBR"
    psram_registers    = [
        ("REG_MR0","REG_MR4",    0x00, 0x0c),
        ("REG_MR4","REG_MR8",    0x04, 0xc0),
        ("REG_MR8","TRAIN_INIT", 0x08, 0x0f),
    ]

    connectors  = [
        Connector("m2", 0,
            # 'E' side of slot (23 physical pins + 7 virtual pins)
            # Pins  1 .. 20 (inclusive)
            "-     -   -   -   -  C4  -  D5   - T10 A3 D11  A2 D13  B3   -  B4 R11  A4  E4 "
            # Pins 21 .. 30
            "T11  D4 M10   -   -   -  -   -   -   - "
            # Other side of slot (45 physical pins)
            # Pins 31 .. 50
            "-    D6   -  C5 B5   - A5  C6   -  C7  B6  D7  A6  D8   -  C9  B7 C10   -  D9 "
            # Pins 51 .. 70
            "A7  B11  B8 C11 A9 C12 B9 C13 A10 B13 B10 A13 B15 A14 A15 B14 C15 C14 B16 D14 "
            # Pins 71 .. 75
            "C16   - D16   -  -" ),
    ]

class _TiliquaR2Mobo:
    resources   = [
        # Quadrature rotary encoder and switch. These are already debounced by an RC filter.
        Resource("encoder", 0,
                 Subsignal("i", PinsN("42", dir="i", conn=("m2", 0))),
                 Subsignal("q", PinsN("40", dir="i", conn=("m2", 0))),
                 Subsignal("s", PinsN("43", dir="i", conn=("m2", 0))),
                 Attrs(IO_TYPE="LVCMOS33")),

        # USB: 5V supply OUT enable (only touch this if you're sure you are a USB host!)
        Resource("usb_vbus_en", 0, PinsN("32", dir="o", conn=("m2", 0)),
                 Attrs(IO_TYPE="LVCMOS33")),

        # USB: Interrupt line from TUSB322I
        Resource("usb_int", 0, PinsN("47", dir="i", conn=("m2", 0)),
                 Attrs(IO_TYPE="LVCMOS33")),

        # Output enable for LEDs driven by PCA9635 on motherboard PCBA
        Resource("mobo_leds_oe", 0, PinsN("11", dir="o", conn=("m2", 0))),

        # DVI: Hotplug Detect
        Resource("dvi_hpd", 0, Pins("37", dir="i", conn=("m2", 0)),
                 Attrs(IO_TYPE="LVCMOS33")),

        # TRS MIDI RX
        Resource("midi", 0, Subsignal("rx", Pins("8", dir="i", conn=("m2", 0)),
                                      Attrs(IO_TYPE="LVCMOS33"))),

        # Motherboard PCBA I2C bus. Includes:
        # - address 0x05: PCA9635 LED driver
        # - address 0x47: TUSB322I USB-C controller
        # - address 0x50: DVI EDID EEPROM (through 3V3 <-> 5V translator)
        Resource("i2c", 0,
            Subsignal("sda", Pins("51", dir="io", conn=("m2", 0))),
            Subsignal("scl", Pins("53", dir="io", conn=("m2", 0))),
        ),

        # RP2040 UART bridge
        UARTResource(0,
            rx="19", tx="17", conn=("m2", 0),
            attrs=Attrs(IO_TYPE="LVCMOS33", PULLMODE="UP")
        ),

        Resource("audio_ffc_i2s", 0,
            Subsignal("sdin1",   Pins("44", dir="o",  conn=("m2", 0))),
            Subsignal("sdout1",  Pins("46", dir="i",  conn=("m2", 0))),
            Subsignal("lrck",    Pins("48", dir="o",  conn=("m2", 0))),
            Subsignal("bick",    Pins("50", dir="o",  conn=("m2", 0))),
            Subsignal("mclk",    Pins("52", dir="o",  conn=("m2", 0))),
            Attrs(IO_TYPE="LVCMOS33")
        ),

        Resource("audio_ffc_aux", 0,
            Subsignal("pdn_d",   Pins("54", dir="o",  conn=("m2", 0))),
            Subsignal("i2c_sda", Pins("56", dir="io", conn=("m2", 0))),
            Subsignal("i2c_scl", Pins("58", dir="io", conn=("m2", 0))),
            Attrs(IO_TYPE="LVCMOS33")
        ),

        # DVI
        # Note: technically DVI outputs are supposed to be open-drain, but
        # compatibility with cheap AliExpress screens seems better with push/pull outputs.
        Resource("dvi", 0,
            Subsignal("d0", Pins("13", dir="o", conn=("m2", 0))),
            Subsignal("d1", Pins("34", dir="o", conn=("m2", 0))),
            Subsignal("d2", Pins("20", dir="o", conn=("m2", 0))),
            Subsignal("ck", Pins("38", dir="o", conn=("m2", 0))),
            Attrs(IO_TYPE="LVCMOS33D", DRIVE="8", SLEWRATE="FAST")
         ),
    ]

    # Expansion connectors ex0 and ex1
    connectors  = [
        Connector("pmod", 0, "55 62 66 68 - - 57 60 64 70 - -", conn=("m2", 0)),
        Connector("pmod", 1, "59 63 67 71 - - 61 65 69 73 - -", conn=("m2", 0)),
    ]

class _TiliquaR3Mobo:
    resources   = [
        # Quadrature rotary encoder and switch. These are already debounced by an RC filter.
        Resource("encoder", 0,
                 Subsignal("i", PinsN("42", dir="i", conn=("m2", 0))),
                 Subsignal("q", PinsN("40", dir="i", conn=("m2", 0))),
                 Subsignal("s", PinsN("43", dir="i", conn=("m2", 0))),
                 Attrs(IO_TYPE="LVCMOS33")),

        # USB: 5V supply OUT enable (only touch this if you're sure you are a USB host!)
        Resource("usb_vbus_en", 0, PinsN("32", dir="o", conn=("m2", 0)),
                 Attrs(IO_TYPE="LVCMOS33")),

        # USB: Interrupt line from TUSB322I
        Resource("usb_int", 0, PinsN("47", dir="i", conn=("m2", 0)),
                 Attrs(IO_TYPE="LVCMOS33")),

        # Output enable for LEDs driven by PCA9635 on motherboard PCBA
        Resource("mobo_leds_oe", 0, PinsN("11", dir="o", conn=("m2", 0))),

        # DVI: Hotplug Detect
        Resource("dvi_hpd", 0, Pins("37", dir="i", conn=("m2", 0)),
                 Attrs(IO_TYPE="LVCMOS33")),

        # TRS MIDI RX
        Resource("midi", 0, Subsignal("rx", Pins("6", dir="i", conn=("m2", 0)),
                                      Attrs(IO_TYPE="LVCMOS33"))),

        # Motherboard PCBA I2C bus. Includes:
        # - address 0x05: PCA9635 LED driver
        # - address 0x47: TUSB322I USB-C controller
        # - address 0x50: DVI EDID EEPROM (through 3V3 <-> 5V translator)
        Resource("i2c", 0,
            Subsignal("sda", Pins("51", dir="io", conn=("m2", 0))),
            Subsignal("scl", Pins("53", dir="io", conn=("m2", 0))),
        ),

        # RP2040 UART bridge
        UARTResource(0,
            rx="19", tx="17", conn=("m2", 0),
            attrs=Attrs(IO_TYPE="LVCMOS33", PULLMODE="UP")
        ),

        Resource("audio_ffc_i2s", 0,
            Subsignal("sdin1",   Pins("44", dir="o",  conn=("m2", 0))),
            Subsignal("sdout1",  Pins("46", dir="i",  conn=("m2", 0))),
            Subsignal("lrck",    Pins("48", dir="o",  conn=("m2", 0))),
            Subsignal("bick",    Pins("50", dir="o",  conn=("m2", 0))),
            Subsignal("mclk",    Pins("67", dir="o",  conn=("m2", 0))),
            Attrs(IO_TYPE="LVCMOS33")
        ),

        Resource("audio_ffc_aux", 0,
            Subsignal("pdn_d",   Pins("65", dir="o",  conn=("m2", 0))),
            Subsignal("pdn_clk", Pins("56", dir="o",  conn=("m2", 0))),
            Subsignal("i2c_sda", Pins("71", dir="io", conn=("m2", 0))),
            Subsignal("i2c_scl", Pins("69", dir="io", conn=("m2", 0))),
            Attrs(IO_TYPE="LVCMOS33")
        ),

        # DVI
        # Note: technically DVI outputs are supposed to be open-drain, but
        # compatibility with cheap AliExpress screens seems better with push/pull outputs.
        Resource("dvi", 0,
            Subsignal("d0", Pins("60", dir="o", conn=("m2", 0))),
            Subsignal("d1", Pins("62", dir="o", conn=("m2", 0))),
            Subsignal("d2", Pins("68", dir="o", conn=("m2", 0))),
            Subsignal("ck", Pins("52", dir="o", conn=("m2", 0))),
            Attrs(IO_TYPE="LVCMOS33D", DRIVE="8", SLEWRATE="FAST")
         ),
    ]

    # Expansion connectors ex0 and ex1
    connectors  = [
        Connector("pmod", 0, "55 38 66 41 - - 57 35 34 70 - -", conn=("m2", 0)),
        Connector("pmod", 1, "59 63 14 20 - - 61 15 13 22 - -", conn=("m2", 0)),
    ]

class _TiliquaR4R5Mobo:
    resources   = [
        # External PLL (SI5351A) clock inputs. Clock frequencies are dynamic. The constraints
        # are overwritten in `cli.py` based on the project configuration.
        Resource("clkex", 0, Pins("44", dir="i", conn=("m2", 0)), Clock(0), Attrs(IO_TYPE="LVCMOS33")),
        Resource("clkex", 1, Pins("40", dir="i", conn=("m2", 0)),
                 Clock(0), Attrs(IO_TYPE="LVCMOS33")),

        # Quadrature rotary encoder and switch. These are already debounced by an RC filter.
        Resource("encoder", 0,
                 Subsignal("i", PinsN("8", dir="i", conn=("m2", 0))),
                 Subsignal("q", PinsN("12", dir="i", conn=("m2", 0))),
                 Subsignal("s", PinsN("43", dir="i", conn=("m2", 0))),
                 Attrs(IO_TYPE="LVCMOS33")),

        # USB: 5V supply OUT enable (only touch this if you're sure you are a USB host!)
        Resource("usb_vbus_en", 0, PinsN("32", dir="o", conn=("m2", 0)),
                 Attrs(IO_TYPE="LVCMOS33")),

        # USB: Interrupt line from TUSB322I
        Resource("usb_int", 0, PinsN("47", dir="i", conn=("m2", 0)),
                 Attrs(IO_TYPE="LVCMOS33")),

        # DVI: Hotplug Detect
        Resource("dvi_hpd", 0, Pins("37", dir="i", conn=("m2", 0)),
                 Attrs(IO_TYPE="LVCMOS33")),

        # TRS MIDI RX
        Resource("midi", 0, Subsignal("rx", Pins("6", dir="i", conn=("m2", 0)),
                                      Attrs(IO_TYPE="LVCMOS33"))),

        # Motherboard PCBA I2C bus. Includes:
        #
        # - address 0x05: PCA9635 LED driver
        # - address 0x47: TUSB322I USB-C controller
        # - address 0x50: DVI EDID EEPROM (through 3V3 <-> 5V translator)
        # - address 0x60: SI5351A external PLL
        #
        # WARN: mobo i2c bus speed should never exceed 100kHz if you want to reliably
        # be able to read the EDID of external monitors. I have seen cases where going
        # above 100kHz causes the monitor to ACK packets that were not destined for
        # its EEPROM (instead for other i2c peripherals on i2c0) - this is dangerous and
        # could unintentionally write to the monitor EEPROM (!!!)
        #
        # There are some slave addresses on the DDC channel that are reserved according
        # to the standard. As far as I can tell, we have no collisions. Reference:
        #
        #   VESA Display Data Channel Command Interface (DDC/CI)
        #   Standard Version 1.1, October 29, 2004
        #
        # Reserved for VCP: 0x6E
        # Reserved in table 4: 0xF0 - 0xFF
        # Reserved in table 5: 0x12, 0x14, 0x16, 0x80, 0x40, 0xA0
        #
        Resource("i2c", 0,
            Subsignal("sda", Pins("51", dir="io", conn=("m2", 0))),
            Subsignal("scl", Pins("53", dir="io", conn=("m2", 0))),
            Attrs(IO_TYPE="LVCMOS33")
        ),

        # RP2040 UART bridge
        UARTResource(0,
            rx="19", tx="17", conn=("m2", 0),
            attrs=Attrs(IO_TYPE="LVCMOS33", PULLMODE="UP")
        ),

        # Audio FFC: I2S interface to CODEC
        Resource("audio_ffc_i2s", 0,
            Subsignal("sdin1",   Pins("42", dir="o",  conn=("m2", 0))),
            Subsignal("sdout1",  Pins("46", dir="i",  conn=("m2", 0))),
            Subsignal("lrck",    Pins("48", dir="o",  conn=("m2", 0))),
            Subsignal("bick",    Pins("50", dir="o",  conn=("m2", 0))),
            Subsignal("mclk",    Pins("67", dir="o",  conn=("m2", 0))),
            Attrs(IO_TYPE="LVCMOS33", DRIVE="4", SLEWRATE="SLOW")
        ),

        # Audio FFC: Other pins (mute/power, control I2C)
        Resource("audio_ffc_aux", 0,
            Subsignal("pdn_d",   Pins("65", dir="o",  conn=("m2", 0))),
            Subsignal("pdn_clk", Pins("56", dir="o",  conn=("m2", 0))),
            Subsignal("i2c_sda", Pins("71", dir="io", conn=("m2", 0))),
            Subsignal("i2c_scl", Pins("69", dir="io", conn=("m2", 0))),
            Attrs(IO_TYPE="LVCMOS33", DRIVE="4", SLEWRATE="SLOW")
        ),
    ]


class _TiliquaR4Mobo:
    resources  = _TiliquaR4R5Mobo.resources + [
        # Output enable for LEDs driven by PCA9635 on motherboard PCBA
        Resource("mobo_leds_oe", 0, PinsN("11", dir="o", conn=("m2", 0))),

        # Diffpairs routed directly to video output through termination resistors.
        Resource("dvi", 0,
            Subsignal("d0", Pins("60", dir="o", conn=("m2", 0))),
            Subsignal("d1", Pins("62", dir="o", conn=("m2", 0))),
            Subsignal("d2", Pins("68", dir="o", conn=("m2", 0))),
            Subsignal("ck", Pins("52", dir="o", conn=("m2", 0))),
            Attrs(IO_TYPE="LVCMOS33D", DRIVE="8", SLEWRATE="FAST")
         ),
    ]

    # Expansion connectors ex0 and ex1
    connectors  = [
        Connector("pmod", 0, "55 38 66 41 - - 57 35 34 73 - -", conn=("m2", 0)),
        Connector("pmod", 1, "59 63 14 20 - - 61 15 13 22 - -", conn=("m2", 0)),
    ]

class _TiliquaR5Mobo:
    resources  = _TiliquaR4R5Mobo.resources + [
        # Enable motherboard I2C passthrough to DVI port. Normally, this
        # should probably be disabled (unless we are reading the EDID) as
        # we don't want to accidentally address some random I2C devices in
        # the display!
        Resource("gpdi_ddc_en", 0, Pins("11", dir="o", conn=("m2", 0))),

        # Diffpairs routed to video output, AC-coupled through a DVI redriver IC.
        Resource("dvi", 0,
            Subsignal("d0", Pins("68", dir="o", conn=("m2", 0))),
            Subsignal("d1", Pins("52", dir="o", conn=("m2", 0))),
            Subsignal("d2", Pins("60", dir="o", conn=("m2", 0))),
            Subsignal("ck", Pins("62", dir="o", conn=("m2", 0))),
            Attrs(IO_TYPE="LVCMOS33D", DRIVE="4", SLEWRATE="FAST")
         ),
    ]

    connectors  = [
        Connector("pmod", 0, "38 35 66 41 - - 57 55 34 73 - -", conn=("m2", 0)),
        Connector("pmod", 1, "59 63 14 20 - - 61 15 13 22 - -", conn=("m2", 0)),
    ]

class TiliquaR2SC2Platform(SoldierCrabR2Platform, LUNAPlatform):
    name                   = ("Tiliqua R2 / SoldierCrab R2 "
                              f"({SoldierCrabR2Platform.device}/{SoldierCrabR2Platform.psram_id})")
    version_major          = 2
    clock_domain_generator = tiliqua_pll.TiliquaDomainGenerator4PLLs
    default_audio_clock    = AudioClock.FINE_48KHZ
    default_usb_connection = "ulpi"

    resources = [
        *SoldierCrabR2Platform.resources,
        *_TiliquaR2Mobo.resources
    ]

    connectors = [
        *SoldierCrabR2Platform.connectors,
        *_TiliquaR2Mobo.connectors
    ]

class TiliquaR2SC3Platform(SoldierCrabR3Platform, LUNAPlatform):
    name                   = ("Tiliqua R2 / SoldierCrab R3 "
                              f"({SoldierCrabR3Platform.device}/{SoldierCrabR3Platform.psram_id})")
    version_major          = 2
    clock_domain_generator = tiliqua_pll.TiliquaDomainGenerator2PLLs
    default_audio_clock    = AudioClock.COARSE_48KHZ
    default_usb_connection = "ulpi"

    resources = [
        *SoldierCrabR3Platform.resources,
        *_TiliquaR2Mobo.resources
    ]

    connectors = [
        *SoldierCrabR3Platform.connectors,
        *_TiliquaR2Mobo.connectors
    ]

class TiliquaR3SC3Platform(SoldierCrabR3Platform, LUNAPlatform):
    name                   = ("Tiliqua R3 / SoldierCrab R3 "
                              f"({SoldierCrabR3Platform.device}/{SoldierCrabR3Platform.psram_id})")
    version_major          = 3
    clock_domain_generator = tiliqua_pll.TiliquaDomainGenerator2PLLs
    default_audio_clock    = AudioClock.COARSE_48KHZ
    default_usb_connection = "ulpi"

    resources = [
        *SoldierCrabR3Platform.resources,
        *_TiliquaR3Mobo.resources
    ]

    connectors = [
        *SoldierCrabR3Platform.connectors,
        *_TiliquaR3Mobo.connectors
    ]

class TiliquaR4SC3Platform(SoldierCrabR3Platform, LUNAPlatform):
    name                   = ("Tiliqua R4 / SoldierCrab R3 "
                              f"({SoldierCrabR3Platform.device}/{SoldierCrabR3Platform.psram_id})")
    version_major          = 4
    clock_domain_generator = tiliqua_pll.TiliquaDomainGeneratorPLLExternal
    default_audio_clock    = AudioClock.FINE_48KHZ
    default_usb_connection = "ulpi"

    resources = [
        *SoldierCrabR3Platform.resources,
        *_TiliquaR4Mobo.resources
    ]

    connectors = [
        *SoldierCrabR3Platform.connectors,
        *_TiliquaR4Mobo.connectors
    ]

class TiliquaR5SC3Platform(SoldierCrabR3Platform, LUNAPlatform):
    name                   = ("Tiliqua R5 / SoldierCrab R3 "
                              f"({SoldierCrabR3Platform.device}/{SoldierCrabR3Platform.psram_id})")
    version_major          = 5
    clock_domain_generator = tiliqua_pll.TiliquaDomainGeneratorPLLExternal
    default_audio_clock    = AudioClock.FINE_48KHZ
    default_usb_connection = "ulpi"

    resources = [
        *SoldierCrabR3Platform.resources,
        *_TiliquaR5Mobo.resources
    ]

    connectors = [
        *SoldierCrabR3Platform.connectors,
        *_TiliquaR5Mobo.connectors
    ]


class EurorackPmodRevision(str, enum.Enum):
    R33    = "r3.3"
    R35    = "r3.5"

    def touch_order(self):
        return {
            self.R33: [0, 1, 2, 3, 7, 6, 5, 4],
            self.R35: [5, 7, 8, 9, 10, 11, 12, 13]
        }[self]

    def default_calibration(self):
        # default calibration constants based on averaging some R3.3 units
        # These should be accurate to +/- 100mV or so on a fresh unit without
        # requiring any initial calibration.
        default_cal_r33 = [
            [-1.158, 0.008], # in (mul, add)
            [-1.158, 0.008],
            [-1.158, 0.008],
            [-1.158, 0.008],
            [ 0.97,  0.03 ], # out (mul, add)
            [ 0.97,  0.03 ],
            [ 0.97,  0.03 ],
            [ 0.97,  0.03 ],
        ]
        default_cal_r35 = [
            [-1.248, -0.03], # in (mul, add)
            [-1.248, -0.03],
            [-1.248, -0.03],
            [-1.248, -0.03],
            [ 0.90,  0.0], # out (mul, add)
            [ 0.90,  0.0],
            [ 0.90,  0.0],
            [ 0.90,  0.0],
        ]
        return {
            self.R33:    default_cal_r33,
            self.R35:    default_cal_r35,
        }[self]

    def default_calibration_rs(self):
        cal = self.default_calibration()
        return "[{}, {}, {}, {}]".format(
            cal[0][0],
            cal[0][1],
            cal[4][0],
            cal[4][1],
        )

class TiliquaRevision(str, enum.Enum):
    R2    = "r2"
    R2SC3 = "r2sc3"
    R3    = "r3"
    R4    = "r4"
    R5    = "r5"

    def default():
        return TiliquaRevision.R4

    def all():
        return [
            TiliquaRevision.R2,
            TiliquaRevision.R2SC3,
            TiliquaRevision.R3,
            TiliquaRevision.R4,
            TiliquaRevision.R5,
        ]

    def from_platform(platform: Platform):
        # e.g. simulation platform
        if not hasattr(platform, 'version_major'):
            return TiliquaRevision.default()
        # real platforms
        return {
            2: TiliquaRevision.R2,
            3: TiliquaRevision.R3,
            4: TiliquaRevision.R4,
            5: TiliquaRevision.R5,
        }[platform.version_major]

    def platform_class(self):
        return {
            TiliquaRevision.R2:    TiliquaR2SC2Platform,
            TiliquaRevision.R2SC3: TiliquaR2SC3Platform,
            TiliquaRevision.R3:    TiliquaR3SC3Platform,
            TiliquaRevision.R4:    TiliquaR4SC3Platform,
            TiliquaRevision.R5:    TiliquaR5SC3Platform,
        }[self]

    def pmod_rev(self):
        return {
            TiliquaRevision.R2:    EurorackPmodRevision.R33,
            TiliquaRevision.R2SC3: EurorackPmodRevision.R33,
            TiliquaRevision.R3:    EurorackPmodRevision.R33,
            TiliquaRevision.R4:    EurorackPmodRevision.R33,
            TiliquaRevision.R5:    EurorackPmodRevision.R35,
        }[self]

class RebootProvider(wiring.Component):

    """
    Issue a 'self_program' (return to bootloader) when the 'button'
    signal is high for 'reboot_seconds', and a 'mute' output shortly
    before then (to warn the CODEC to prevent pops).
    """

    button: wiring.In(unsigned(1))
    mute:   wiring.Out(unsigned(1), init=1)

    def __init__(self, clock_sync_hz, reboot_seconds=3, mute_seconds=2.5, unmute_seconds=0.25):
        self.reboot_seconds = reboot_seconds
        self.mute_seconds   = mute_seconds
        self.unmute_seconds = unmute_seconds
        self.clock_sync_hz  = clock_sync_hz
        super().__init__()

    def elaborate(self, platform):
        m = Module()

        timeout_unmute   = int(self.unmute_seconds*self.clock_sync_hz)
        unmute_counter = Signal(range(timeout_unmute+1))
        with m.If(unmute_counter < timeout_unmute):
            m.d.sync += self.mute.eq(1)
            m.d.sync += unmute_counter.eq(unmute_counter + 1)
        with m.Else():
            m.d.sync += self.mute.eq(0)

        timeout_reboot = self.reboot_seconds*self.clock_sync_hz
        timeout_mute   = int(self.mute_seconds*self.clock_sync_hz)
        assert(timeout_reboot > (timeout_mute - 0.25))
        button_counter = Signal(range(timeout_reboot+1))
        with m.If(button_counter >= timeout_mute):
            m.d.sync += self.mute.eq(1)
        with m.If(button_counter >= timeout_reboot):
            m.d.comb += platform.request("self_program").o.eq(1)
        with m.Else():
            # we already started muting. point of no return.
            with m.If(self.button | self.mute):
                m.d.sync += button_counter.eq(button_counter + 1)
            with m.Else():
                m.d.sync += button_counter.eq(0)


        m.d.comb += platform.request("pseudo_vccio").o.eq(-1)
        m.d.comb += platform.request("pseudo_vccram").o.eq(-1)
        m.d.comb += platform.request("pseudo_gnd").o.eq(0)
        m.d.comb += platform.request("pseudo_gndram").o.eq(0)

        return m
