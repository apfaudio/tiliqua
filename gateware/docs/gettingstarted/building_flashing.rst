Building and flashing examples
==============================

Building
--------

Each top-level bitstream has a command-line interface. You can see the options by running (for example):

.. code-block:: bash

   # from `gateware` directory
   pdm dsp

The available options change depending on the top-level project. For example, many projects have video output, and from the CLI you can select the video modeline.

.. warning::

    For prototype Tiliqua hardware, be careful to add an :py:`--hw r4` (or similar) flag specifying your hardware version to all commands below.

A few examples of building top-level bitstreams:

.. code-block:: bash

   # from `gateware` directory

   # for the selftest bitstream (prints diagnostics out DVI and serial)
   pdm selftest build
   # for a vectorscope / oscilloscope
   pdm xbeam build
   # for a polyphonic MIDI synth
   pdm polysyn build
   # for the LUNA-based 4in + 4out USB soundcard example
   # note: LUNA USB port presents itself on the second USB port (not dbg)!
   pdm usb_audio build
   # for a 4-channel waveshaping oscillator
   pdm dsp build --dsp-core nco
   # for a diffusion delay effect
   pdm dsp build --dsp-core diffuser
   # simplified vectorscope (no SoC / menu system)
   pdm vectorscope_no_soc build

Generally, bitstreams are also built in CI - check ``.github/workflows`` if you need more gruesome details on how systems are built.

For SoC projects that have firmware, for quicker iteration, ``--fw-only`` is useful to only re-build the firmware for that bitstream and repackage the archive, without re-synthesizing the bitstream (which often takes quite a while).

Flashing
--------


When you build projects from the command line, it will create a *Bitstream Archive*, which is a ``.tar.gz`` file that contains everything the bootloader needs to start a custom bitstream. Details on the inner workings of these archives can be found in the :doc:`../bootloader` section.

You can flash custom bitstreams to one of 8 slots, using the built-in ``pdm flash`` command. To flash a bitstream archive you have just built, you can use ``pdm flash archive`` as follows:

.. warning::

    For prototype hardware, you may need to reflash the RP2040 and bootloader bitstream  per :doc:`../bootloader`, before the following instructions will work.

.. code-block:: bash

   # Flash user bitstreams to the desired slot (0-7)
   pdm flash archive build/selftest-r4/selftest-*.tar.gz --slot 1
   pdm flash archive build/xbeam-r4/xbeam-*.tar.gz --slot 2

``pdm flash`` also supplies a ``status`` command to read back the Tiliqua's SPI flash to see what is currently on there:

.. code-block:: bash

   pdm flash status

.. note::

    If you want to avoid audio pops while flashing, it is best to flash from the bootloader bitstream, as the audio CODEC is always muted in that bitstream.

If you are running an SoC, you can monitor serial output like so:

.. code-block:: bash

   sudo picocom -b 115200 /dev/ttyACM0

For non-SoC projects that don't require extra firmware, note that you can also directly flash bitstreams to the SRAM of the FPGA like so:

.. code-block:: bash

   sudo openFPGALoader -c dirtyJtag build/dsp-mirror-r4/top.bit

This flashes much quicker, as we don't have to wait for flash pages to update. This can be useful for quickly iterating on DSP gateware. In the future, this will be possible with SoC bitstreams as well, but requires an extra bridge to directly stream debug firmware to the PSRAM from the host, which isn't implemented yet.

Video Modes
-----------

From the Tiliqua bootloader (or whenever a display is hotplugged whilst in the bootloader), Tiliqua reads the attached display EDID to determine which display timings to use. Tiliqua will adapt to the first timing descriptor it finds, and if none of them can be met (usually if the pixel clock is too fast), it falls back to 1280x720p60. You can inspect the logs as to how the bootloader decided which display mode to use by looking at the serial telemetry on the debug port.

Depending on the project, Tiliqua user bitstreams may:

- Not use the video output at all (for example ``pdm dsp`` and ``pdm usb_audio`` are audio-only)
- Use a static video mode (for example ``pdm vectorscope_no_soc``)
- Support dynamic video modes (all SoC bitstreams)

Dynamic video modes are useful as the same bitstream can be used/shared, regardless of which screen is plugged in. When dynamic video modes are supported, the user bitstream will inherit the video mode that was autodetected by the bootloader (this is communicated by a ``bootinfo`` struct saved to PSRAM before the user bitstream is booted).


.. note::

   If for some reason you want to disable EDID reading and use a static/specific mode, you can always re-build and re-flash all bitstreams using a flag like ``--modeline 1280x720p60`` to force a static modeline, disabling dynamic mode detection. Note that the bootloader built with a static modeline can *only* start bitstreams that are also built with a static modeline, however a bootloader built for dynamic modelines can start *both* types of bitstreams. The bootloader will display an error if these conditions are not met.
