Getting started
###############

Building example projects
-------------------------


Each top-level bitstream has a command-line interface. You can see the options by running (for example):

.. code-block:: bash

   # from `gateware` directory
   pdm dsp

The available options change depending on the top-level project. For example, many projects have video output, and from the CLI you can select the video resolution.

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

Flashing example projects
-------------------------

.. warning::

    For prototype hardware, you may need to reflash the RP2040 and bootloader bitstream  per :doc:`bootloader`, before the following instructions will work.

When you build projects from the command line, it will create a .tar.gz archive containing the bitstream, firmware (if applicable), and a manifest describing the contents. You can flash bitstreams to one of 8 slots, using the built-in flash tool.
Such archives may be flashed as follows:

.. code-block:: bash

   # Flash user bitstreams to the desired slot (0-7)
   pdm flash archive build/selftest-r4/selftest-*.tar.gz --slot 1
   pdm flash archive build/xbeam-r4/xbeam-*.tar.gz --slot 2
   pdm flash status # check what is on the Tiliqua

.. note::

    If you want to avoid audio pops while flashing, it is best to flash from the bootloader bitstream, as the audio CODEC is always muted in that bitstream.

If you are running an SoC, you can monitor serial output like so:

.. code-block:: bash

   sudo picocom -b 115200 /dev/ttyACM0

For non-SoC projects that don't require extra firmware, you can also directly flash bitstreams to the SRAM of the FPGA like so:

.. code-block:: bash

   sudo openFPGALoader -c dirtyJtag build/dsp-mirror-r4/top.bit

This flashes much quicker, as we don't have to wait for flash pages to update. This can be useful for quickly iterating on DSP gateware. In the future, this will be possible with SoC bitstreams as well, but requires an extra bridge to directly stream debug firmware to the PSRAM from the host, which isn't implemented yet.

Simulating DSP cores
--------------------

The easiest way to debug the internals of a DSP project is to simulate it. This project provides some shortcuts to enable simulating designs end-to-end with Verilator (at some point these will be migrated to Amaranths CXXRTL simulation backend, once it lands).

For example, to simulate the waveshaping oscillator example:

.. code-block:: bash

   # from `gateware` directory
   pdm dsp sim --dsp-core nco

In short this command:

- Elaborates your Amaranth HDL and convert it to Verilog
- Verilates your verilog into a C++ implementation, compiling it against ``sim_dsp_core.cpp`` provided in ``gateware/top/dsp`` that excites the audio inputs (you can modify this).
- Runs the verilated binary itself and spits out a trace you can view with ``gtkwave`` to see exactly what every net in the whole design is doing.

Simulating SoC cores
--------------------

A subset of SoC-based top-level projects also support end-to-end simulation (i.e including firmware co-simulation). For example, for the selftest SoC:

.. code-block:: bash

   # from `gateware` directory
   pdm selftest sim

   # ...

   run verilated binary 'build/obj_dir/Vtiliqua_soc'...
   sync domain is: 60000 KHz (16 ns/cycle)
   pixel clock is: 74250 KHz (13 ns/cycle)
   [INFO] Hello from Tiliqua selftest!
   [INFO] PSRAM memtest (this will be slow if video is also active)...
   [INFO] write speed 1687 KByte/seout frame00.bmp
   c
   [INFO] read speed 1885 KByte/sec
   [INFO] PASS: PSRAM memtest

UART traffic from the firmware is printed to the terminal, and each video frame is emitted as a bitmap. This kind of simulation is useful for debugging the integration of top-level SoC components.

Simulating vectorscope core
---------------------------

There is a top-level ``vectorscope_no_soc`` provided which is also useful for debugging integration issues between the video and memory controller cores. This can be simulated end-to-end as follows (``--trace-fst`` is also useful for saving waveform traces):

.. code-block:: bash

   # from `gateware` directory
   pdm vectorscope_no_soc sim --trace-fst

Using the ILA
-------------

Some cores support using a built-in ILA (integrated logic analyzer), to collect waveform traces on the hardware into on-FPGA block RAM, which is sampled at the system clock and dumped out the serial port.

For example:

.. code-block:: bash

   # from `gateware` directory
   pdm vectorscope_no_soc build --ila --ila-port /dev/ttyACM0

This will build the bitstream containing the ILA, flash the bitstream, then open the provided serial port waiting for an ILA dump from the Tiliqua to arrive. Once received, the dump will be saved to a waveform trace file.

.. note::
   You may have to play with permissions for flashing to work correctly - make sure ``openFPGALoader`` can run locally under your user without ``sudo``.
