Using the ILA
=============

Some cores support using a built-in ILA (integrated logic analyzer), to collect waveform traces on the hardware into on-FPGA block RAM, which is sampled at the system clock and dumped out the serial port.

For example:

.. code-block:: bash

   # from `gateware` directory
   pdm vectorscope_no_soc build --ila --ila-port /dev/ttyACM0

This will build the bitstream containing the ILA, flash the bitstream, then open the provided serial port waiting for an ILA dump from the Tiliqua to arrive. Once received, the dump will be saved to a waveform trace file.

.. note::
   You may have to play with permissions for flashing to work correctly - make sure ``openFPGALoader`` can run locally under your user without ``sudo``.
