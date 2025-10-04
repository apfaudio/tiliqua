Simulating designs
==================

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
