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

1. Flash the `apfbug <https://github.com/apfaudio/apfbug>`_ project to the RP2040. Pre-built binaries `can be found here <https://github.com/apfaudio/apfbug/releases>`_. To flash them, hold RP2040 BOOTSEL during power on, copy the :code:`build/*.uf2` to the usb storage device and power cycle Tiliqua.

2. Build and flash the bootloader bitstream archive using the built-in flash tool:

.. code-block:: bash

    # Flash bootloader to start of flash, build assuming XIP (execute directly from SPI flash, not PSRAM)
    pdm bootloader build --fw-location=spiflash --resolution 1280x720p60
    pdm flash archive build/bootloader-*.tar.gz

3. DISCONNECT USB DBG port, reboot Tiliqua.

.. warning::

    The bootloader will NOT reboot correctly (just show a blank screen) if you have
    the :py:`dbg` USB port connected WITHOUT a tty open. Currently you MUST have the
    ``/dev/ttyACM0`` open OR have the ``dbg`` USB port disconnected for it to work correctly.
    `Tracking issue (linked) <https://github.com/apfaudio/apfbug/issues/2>`_.


4. Now when Tiliqua boots you will enter the bootloader. Use the encoder to select an image. Hold the encoder for >3sec in any image to go back to the bootloader.

Bitstream Archives and Flash Memory Layout
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Each bitstream archive contains:

- Bitstream file (top.bit)
- Firmware binary (if applicable) 
- Any extra resources to be loaded into PSRAM (if applicable)
- Manifest file describing the contents

The flash tool manages the following memory layout on the FPGA's 16MByte SPI flash:

- Bootloader bitstream: 0x000000
- User bitstream slots: 0x100000, 0x200000, etc (1MB spacing)
- Manifest: End of each slot (slot 0: 0x100000 + 0x100000 - 1024 (manifest size))
- Firmware: Loaded into PSRAM by bootloader, usually fixed offset from the bitstream start (i.e firmware for slot 0 is loaded from 0x100000 + 0xC0000 = 0x1C0000)

The manifest includes metadata like the bitstream name and version, as well as information about where firmware should be loaded in PSRAM.

If an image requires firmware loaded to PSRAM, the SPI flash source address (in the manifest) is set to the true firmware base address by the flash tool when it is flashed.
That is, the value of spiflash_src is not preserved by the flash tool and instead depends on the slot number.
This allows a bitstream that requires firmware to be loaded to PSRAM to be flashed to any slot, and the bootloader will load the firmware from the correct address.

Implementation details: ECP5
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ECP5 :code:`bootloader` bitstream copies firmware from SPI flash to PSRAM before jumping to user bitstreams by asking the RP2040 to execute a stub bitstream replay (load a special bitstream to SRAM that jumps to the new bitstream). User bitstreams are responsible for asserting PROGRAMN when the encoder is held to reconfigure back to the bootloader.

Implementation details: RP2040
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:code:`apfbug` firmware includes the same features as :code:`pico-dirtyjtag` (USB-JTAG and USB-UART bridge), with some additions:

- UART traffic is inspected to look for keywords.
- If a keyword is encountered e.g. :code:`BITSTREAM1`, a pre-recorded JTAG stream stored on the RP2040's SPI flash is decompressed and replayed. The JTAG streams are instances of the `bootstub <https://github.com/apfaudio/tiliqua/blob/main/gateware/src/top/bootstub/top.py>`_ top-level bitstream. These are tiny bitstreams that are programmed directly into SRAM with the target :code:`bootaddr` and PROGRAMN assertion.
- This facilitates ECP5 multiboot (jumping to arbitrary bitstreams) without needing to write to the ECP5's SPI flash and exhausting write cycles.


Recording new JTAG streams for RP2040
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TODO documentation on recording new JTAG bitstreams for storage on RP2040 flash - not necessary to change this for ordinary Tiliqua usecases. Note: SoldierCrab R3 and R2 use different ECP5 variants, so they need different RP2040 images.
