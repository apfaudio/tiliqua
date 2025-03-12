Bootloader
##########

Interface
---------

The bootloader allows you to arbitrarily select from one of 8 bitstreams after the Tiliqua powers on, without needing to connect a computer. In short:

- When Tiliqua boots, you can select a bitstream with the encoder (either using the display output, or by reading the currently lit LED if no display is connected).
- When you select a bitstream (press encoder), the FPGA reconfigures itself and enters the selected bitstream.
- From any bitstream, you can always go back to the bootloader by holding the encoder for 3sec (this is built into the logic of every bitstream).

Setup and implementation
------------------------

The bitstream selector consists of 2 key components that work together:

- The RP2040 firmware (`apfbug - fork of dirtyJTAG <https://github.com/apfaudio/apfbug>`_)
- The `bootloader <https://github.com/apfaudio/tiliqua/tree/main/gateware/src/top/bootloader>`_ top-level bitstream.

First-time setup
^^^^^^^^^^^^^^^^

1. Flash the RP2040. Use the latest pre-built binaries `found here <https://github.com/apfaudio/apfbug/releases>`_. To flash them, hold RP2040 BOOTSEL before applying power, then copy the :code:`build/*.uf2` to the usb storage device and power cycle Tiliqua again.

2. Build and flash the bootloader bitstream using the built-in flash tool (alternatively just download the latest bootloader archive from the CI artifacts):

.. code-block:: bash

    # Flash bootloader to start of flash, build assuming XIP (execute directly from SPI flash, not PSRAM)
    # Be careful to replace `--hw r4` with your hardware revision!
    pdm bootloader build --hw r4 --fw-location=spiflash --resolution 1280x720p60
    pdm flash archive build/bootloader-*.tar.gz

3. Build and flash any other bitstreams you want to slots 0..7 (you can also download these archives from CI artifacts):

.. code-block:: bash

   # assuming the archive has already been built / downloaded
   pdm flash archive build/xbeam-*.tar.gz --slot 2

2. Check what is currently flashed in each slot (by reading out the flash manifests):

.. code-block:: bash

   pdm flash status

3. Before using the new bitstreams, disconnect the USB port and power cycle Tiliqua. (note: for the latest RP2040 firmware, this is not necessary and you can use them straight away).

.. warning::

    Before ``apfbug`` beta2 firmware, the bootloader would NOT reboot correctly (just show a blank screen) if you have
    the :py:`dbg` USB port connected WITHOUT a tty open. You HAD to have the
    ``/dev/ttyACM0`` open OR have the ``dbg`` USB port disconnected for it to work correctly.
    `Tracking issue (linked) <https://github.com/apfaudio/apfbug/issues/2>`_ (resolved in beta2 FW).


4. Now when Tiliqua boots you will enter the bootloader. Use the encoder to select an image. Hold the encoder for >3sec in any image to go back to the bootloader.

Bitstream Archives and Flash Memory Layout
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Each bitstream archive contains:

- Bitstream file (top.bit)
- Firmware binary (if applicable)
- Any extra resources to be loaded into PSRAM (if applicable)
- Manifest file describing the contents

The flash tool manages the following memory layout on the SoldierCrab's 128Mbit SPI flash:

.. code-block:: text

    ┌────────────────────────────┐  0x000000
    │                            │
    │    Bootloader Bitstream    │
    │                            │
    ├────────────────────────────┤
    │          (padding)         │
    ├────────────────────────────┤  0x0B0000
    │                            │
    │    Bootloader FW (XiP)     │
    │                            │
    ├────────────────────────────┤
    │          (padding)         │
    ╞════════════════════════════╡  0x100000
    │                            │
    │      Slot 0 Bitstream      │
    │                            │
    ├────────────────────────────┤
    │          (padding)         │
    ├────────────────────────────┤  0x1B0000
    │                            │
    │        Slot 0 FW           │
    │  NOT XiP, copied to PSRAM  │
    │                            │
    ├────────────────────────────┤  (any additional slot 0 resources appended here)
    │          (padding)         │
    ├────────────────────────────┤  0x1FFC00
    │      Slot 0 Manifest       │
    ╞════════════════════════════╡  0x200000 (End of Slot 0, start of Slot 1)
    │                            │
    │      Slot 1 Bitstream      │
    │                            │
    ├────────────────────────────┤
    │          (padding)         │
    ├────────────────────────────┤  0x2B0000
    │                            │
    │        Slot 1 FW           │
    │  NOT XiP, copied to PSRAM  │
    │                            │
    ├────────────────────────────┤ (any additional slot 1 resources appended here)
    │          (padding)         │
    ├────────────────────────────┤  0x2FFC00
    │       Slot 1 Manifest      │
    ╞════════════════════════════╡  0x300000 (End of Slot 1, start of Slot 2)
    │                            │

    ... continued up to Slot 7

- Bootloader bitstream: 0x000000
- User bitstream slots: 0x100000, 0x200000, etc (1MB spacing)
- Manifest: End of each slot (slot 0: 0x100000 + 0x100000 - 1024 (manifest size))
- Firmware: Loaded into PSRAM by bootloader, usually fixed offset from the bitstream start (i.e firmware for slot 0 is loaded from 0x100000 + 0xB0000 = 0x1B0000)

The manifest includes metadata like the bitstream name and version, as well as information about where firmware should be loaded in PSRAM.

If an image requires firmware loaded to PSRAM, the SPI flash source address (in the manifest) is set to the true firmware base address by the flash tool when it is flashed.
That is, the value of ``spiflash_src`` is not preserved by the flash tool and instead depends on the slot number.
This allows a bitstream that requires firmware to be loaded to PSRAM to be flashed to any slot, and the bootloader will load the firmware from the correct address.

Implementation details: ECP5
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ECP5 :code:`bootloader` bitstream copies firmware from SPI flash to PSRAM before jumping to user bitstreams by asking the RP2040 to execute a stub bitstream replay (load a special bitstream to SRAM that jumps to the new bitstream). The request is issued over UART from the ECP5 to the RP2040, so it is visible if you have the ``/dev/ttyACMX`` open. User bitstreams are responsible for asserting PROGRAMN when the encoder is held to reconfigure back to the bootloader.

Implementation details: RP2040
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:code:`apfbug` firmware includes the same features as :code:`pico-dirtyjtag` (USB-JTAG and USB-UART bridge), with some additions:

- UART traffic is inspected to look for keywords.
- If a keyword is encountered e.g. :code:`BITSTREAM1`, a pre-recorded JTAG stream stored on the RP2040's SPI flash is decompressed and replayed. The JTAG streams are instances of the `bootstub <https://github.com/apfaudio/tiliqua/blob/main/gateware/src/top/bootstub/top.py>`_ top-level bitstream. These are tiny bitstreams that are programmed directly into SRAM with the target :code:`bootaddr` and PROGRAMN assertion.
- This facilitates ECP5 multiboot (jumping to arbitrary bitstreams) without needing to write to the ECP5's SPI flash and exhausting write cycles.


Recording new JTAG streams for RP2040
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TODO documentation on recording new JTAG bitstreams for storage on RP2040 flash - not necessary to change this for ordinary Tiliqua usecases. Note: SoldierCrab R3 and R2 use different ECP5 variants, so they need different RP2040 images. This is addressed by the ``TILIQUA_HW_VERSION_MAJOR`` cmake flag in the ``apfbug`` project.
