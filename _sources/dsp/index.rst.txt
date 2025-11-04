DSP Library
###########

Philosophy
----------

TODO short overview of the DSP library philosophy.

TODO link to Amaranth documentation on streams.

.. image:: /_static/mydsp.png
  :width: 800

Basic DSP Components
--------------------

After a statement like ``from tiliqua import dsp``, these can be accessed through ``dsp.Split`` or similar:

.. toctree::
   :maxdepth: 2

   delay_lines
   filters
   oscillators
   effects
   vca
   mix
   resample
   oneshot
   stream_util
   misc

Specialized Modules
-------------------

These require qualified access - after a statement like ``from tiliqua import dsp``, these can be accessed through ``dsp.fft.STFTProcessor`` or similar:

.. toctree::
   :maxdepth: 2

   delay_effect
   fft
   spectral
   mac
   block
   complex
   cordic
