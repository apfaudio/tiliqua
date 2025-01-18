Bootloader
##########

.. note::

    'Bootloader' is a bit of a misnomer, as what is currently implemented is more like a 'bitstream selector' (although a true USB bootloader is something in the works).

Interface
---------

The bitstream selector allows you to arbitrarily select from one of 8 bitstreams after the Tiliqua powers on, without needing to connect a computer.

Put simply:

- When Tiliqua boots, you can select a bitstream with the encoder (either using the display output, or by reading the currently lit LED if no display is connected).
- When you select a bitstream (press encoder), the FPGA reconfigures itself and enters the selected bitstream.
- From any bitstream, you can always go back to the bootloader by holding the encoder for 3sec (this is built into the logic of every bitstream).

.. warning::

    The bitstream selector will not reboot correctly if you have
    the :py:`dbg` USB port connected. The assumption is you're flashing
    development bitstreams to SRAM in that scenario anyway.

Setup and implementation
------------------------

The bitstream selector consists of 2 key components that work together:

- The RP2040 firmware (`apfbug - fork of dirtyJTAG <https://github.com/apfaudio/apfbug>`_)
- The `bootloader <https://github.com/apfaudio/tiliqua/tree/main/gateware/src/top/bootloader>`_ top-level bitstream.

First-time setup
^^^^^^^^^^^^^^^^

1. Build and flash the `apfelbug <https://github.com/apfaudio/apfbug>`_ project to the RP2040 (hold RP2040 BOOTSEL during power on, copy the :code:`build/*.uf2` to the usb storage device and reset)

2. Build and flash the bootloader bitstream archive using the built-in flash tool:

.. code-block:: bash

    # Flash bootloader to slot 0 (0x0), force XIP firmware (execute directly from SPI flash)
    pdm bootloader build --fw-location=spiflash
    pdm flash build/bootloader-*.tar.gz

3. DISCONNECT USB DBG port, reboot Tiliqua
    - Currently :code:`apfelbug` only works correctly with the DBG connector DISCONNECTED or with the UART port open on Linux and CONNECTED. Do not have the USB DBG connected without the UART0 open with :code:`picocom` or so.

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

:code:`apfelbug` firmware includes the same features as :code:`pico-dirtyjtag` (USB-JTAG and USB-UART bridge), with some additions:

- UART traffic is inspected to look for keywords.
- If a keyword is encountered e.g. :code:`BITSTREAM1`, a pre-recorded JTAG stream stored on the RP2040's SPI flash is decompressed and replayed. The JTAG streams are instances of the `bootstub <https://github.com/apfaudio/tiliqua/blob/main/gateware/src/top/bootstub/top.py>`_ top-level bitstream. These are tiny bitstreams that are programmed directly into SRAM with the target :code:`bootaddr` and PROGRAMN assertion.
- This facilitates ECP5 multiboot (jumping to arbitrary bitstreams) without needing to write to the ECP5's SPI flash and exhausting write cycles.


Recording new JTAG streams for RP2040
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TODO documentation, not necessary to change this for any ordinary usecase. Update this if needed for SoldierCrab R3.
