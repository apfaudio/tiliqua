Building and Flashing
=====================

*Note: this section assumes you have already followed all steps in* :doc:`install`

Overview
--------

In the ``tiliqua`` repository, all top-level bitstreams that can be flashed to the hardware are located in `gateware/src/top <https://github.com/apfaudio/tiliqua/tree/main/gateware/src/top>`_. Each folder is a project, which may contain gateware, test harnesses, firmware (if it has a CPU) and additional command-line arguments.

In `gateware/pyproject.toml <https://github.com/apfaudio/tiliqua/tree/main/gateware/pyproject.toml>`_, there are some ``pdm`` command-line aliases set up to make these examples easier to type. For example, in this file we have a section like this:

.. code-block:: toml

    [tool.pdm.scripts]
    dsp = "src/top/dsp/top.py"

This means that when we run the command ``pdm dsp``, this will expand to a Python interpreter running the file ``src/top/dsp/top.py`` in the current virtual environment (using the dependencies we installed in :doc:`install`). There is nothing special going on here, it's just a shortcut for needing to type out the whole path every time. The following 2 commands are equivalent:

.. code-block:: bash

   # from `gateware` directory
   pdm dsp
   # or equivalently, not using the alias
   pdm run src/top/dsp/top.py

Building
--------

Each ``top.py`` has its own command-line interface. You can see the options by running:

.. code-block:: bash

   # from `gateware` directory
   pdm dsp -h

The available options change depending on which project you are building. For example, if a bitstream supports video, it will have an extra CLI option for ``--modeline``. If it supports different clock speeds, you will see an ``--fs-192khz`` option. If it has a CPU, you can pick where the firmware should be stored, and so on.

The `dsp/top.py` project contains lots of example cores demonstrating different parts of the DSP library. I encourage taking a peek through it. The project is structured that an extra CLI argument ``--dsp-core`` can be used to select which particular core to build. For example:

.. code-block:: bash

   # Build example that just sends audio inputs to outputs unmodified.
   pdm dsp build --dsp-core=mirror

After a while, you should see something like:

.. code-block:: bash

    Building bitstream for Tiliqua R5 / SoldierCrab R3 (LFE5U-25F/APS256XXN-OBR)
    ┌─────────────[tiliqua-mobo]────────────────────────────[soldiercrab]─────────┐
    │                                      ┊┌─[48MHz OSC]                         │
    │                                      ┊└─>[ECP5 PLL]┐                        │
    │                                      ┊             ├>[sync]     60.0000 MHz │
    │                                      ┊             ├>[usb]      60.0000 MHz │
    │                                      ┊             └>[fast]    120.0000 MHz │
    │ [25MHz OSC]──>[si5351 PLL]─┬>[clk0]─────────────────>[audio]    12.2880 MHz │
    │                            └>[clk1]─────────────────>[disable]              │
    └─────────────────────────────────────────────────────────────────────────────┘
    Video clocks disabled (no video out).
    <...>
    Contents:
      top.bit       122 KiB
      manifest.json    0 KiB
    <...>
    Saved to '/Users/seb/dev/tiliqua/gateware/build/dsp-mirror-r5/dsp-mirror-9cd67c90-r5.tar.gz'

As we have built a simple audio-only bitstream without a CPU, there are only 2 artifacts produced:

    - ``top.bit``: the synthesized bitstream to configure the FPGA
    - ``manifest.json``: Metadata about the bitstream, used to display the bootloader help screen, IO assignments, for example.

Both of these end up in ``build/dsp-mirror-r5/``, however, they are finally zipped together into ``dsp-mirror-9cd67c90-r5.tar.gz`` - which is a *Bitstream Archive*. This archive (bitstream + dependencies + metadata) is what can be flashed into a Tiliqua slot and seen by the bootloader. Details on the inner workings of these archives can be found in the :doc:`../bootloader` section.

Verbosity and Logs
------------------

After building a bitstream, the most interesting logs are found in ``build/<my_bitstream>/top.tim``. There you will find a resource utilization report (how much of the FPGA was used) as well as a timing report, both emitted by ``nextpnr-ecp5``.

Optionally, you can build with the ``--verbose`` flag, which will print the ``yosys`` and ``nextpnr`` log output while synthesis is happening. This can be useful for larger bitstreams.

Flashing to a Bitstream Slot
----------------------------

A ``.tar.gz`` *Bitstream Archive* contains everything the bootloader needs to start a custom bitstream. You can build these yourself, or download pre-built archives from the `release page <https://github.com/apfaudio/tiliqua/releases>`_.

You can flash custom bitstreams to one of 8 slots, using the built-in ``pdm flash`` command. To flash a bitstream archive you have just built, you can use ``pdm flash archive`` as follows:

.. code-block:: bash

   # Flash user bitstreams to the desired slot (0-7)
   pdm flash archive build/dsp-mirror-r5/dsp-mirror*.tar.gz --slot 6
   # Same, without Y/N confirmation:
   pdm flash archive build/dsp-mirror-r5/dsp-mirror*.tar.gz --slot 6 --noconfirm

After flashing the above bitstream, you should see its name in the bootloader screen. You can then select it, and if you feed any audio/CV in on input channel 0, you will see it come out on output channel 0. As usual, you can hold the encoder for 3sec to return to the bootloader screen at any time.

.. note::

    If you want to avoid audio pops while flashing, it is best to flash from the bootloader bitstream, as the audio CODEC is always muted in that bitstream.

Webflasher
----------

Another option for flashing bitstreams is `tiliqua-webflash <https://apfaudio.github.io/tiliqua-webflash>`_, which lets you flash a bitstream archive from Chrome on any OS.

You can upload bitstream archives from your computer, or flash one from the server from the latest release package. Generally, using the web flasher is a bit slower than using ``pdm flash``.

Flashing to SRAM
----------------

For simple bitstreams that don't have a CPU, it can be convenient to skip the whole 'permanently flash to a slot' procedure and instead write straight into the FPGA's configuration SRAM. This is much faster as it does not touch the SPI flash or persist permanently.

For our ``dsp-mirror`` example, here's an example of doing so:

.. code-block:: bash

    $ openFPGALoader -c dirtyJtag build/dsp-mirror-r5/top.bit

.. warning::

    Be careful when writing straight to SRAM that your audio and video clocks are exactly the same as what the bootloader was using, otherwise your bitstream won't start correctly. For audio-only bitstreams, this is the case if you don't use the ``--fs-192khz`` flag. For video bitstreams, your ``--modeline`` must match what the bootloader determined.

    If this sounds confusing, I would suggest always flashing to a Bootloader Slot, as it will guarantee things work as expected.

Flash Status
------------

``pdm flash`` also supplies a ``status`` command to read back the Tiliqua's SPI flash to see what is currently on there:

.. code-block:: bash

   pdm flash status

This will dump every manifest currently flashed to Tiliqua, so you can see what is flashed in which slot. This command simply does a readback, it does not write to the SPI flash.
