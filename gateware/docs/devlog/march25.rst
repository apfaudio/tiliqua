[Devlog 1] EMC Adventures
===========================


*Thanks for dropping by! Tiliqua is an open-source project (see* :doc:`../foss_funding` *). Feel free to join the discussion (see* :doc:`../community`).

What a crazy last couple of months! I've been super busy bringing up the Tiliqua R4 (latest) hardware revision and getting it ready for production. The trickiest aspect was getting it through EMC testing, so this will be our focus today.

PHOTO: tiliqua back

New Features
------------

Before we dive deep into EMC, a quickfire list of unrelated wins from the last couple months:

- **R4 Hardware Diagrams**: I put together some detailed hardware diagrams of how the different bits of Tiliqua connect together, you can find them under :doc:`/hardware_design`.
- **Self-calibration**: Tiliqua can now semi-automatically calibrate its own CODEC for better control voltage tracking, you'll find the gruesome details under :doc:`/calibration`.
- **Bitstream Archives**: The format used for sharing and flashing user bitstreams is implemented and relatively stable now, this means you can share a single file which contains everything a project needs (bitstream, firmware, images, description of the contents). Gruesome details under :doc:`/bootloader`.
- **Parallel builds**: It's now possible to build all the Tiliqua projects simultaneously, which reduces the build time from about 15min for all projects (about 30 bitstreams) to about 5min on my machine. Try this out with ``gateware/scripts/build_bitstreams_soc.sh``!
- **Menu system refactor**: The Tiliqua menu system has been `completely rewritten <https://github.com/apfaudio/tiliqua/pull/85>`_ , which should make it much easier to modify it for your own purposes. I plan to write a short tutorial on how this works soon.

In this update
--------------

- **R4 Hardware & EMC**: A lot of work went into getting Tiliqua ready for EMC testing, and I learned much from the process.
- **Dynamic Clocking**: The latest revision adds an external PLL, useful for EMC (spread spectrum) and dynamic resolution switching. We'll cover this below.
- **100% Amaranth**: Until recently there were some core Tiliqua components (especially audio CODEC initialization, calibration, the video subsystem) that were still re-using Verilog cores. These are now all removed and `ported to Amaranth <https://github.com/apfaudio/tiliqua/pull/89>`_, which should make the codebase easier to understand!

CE and FCC
----------

Any kind of electronic product sold in the EU must have evidence that it meets the requirements for a CE mark, in the US the (almost) equivalent mark is FCC. For a eurorack module like Tiliqua, there 2 most interesting sets of standards:

- EMC: There are hundreds of standards related to EMC (Electromagnetic Compliance: radio emissions and static discharge), however only a few are relevant to a low-voltage musical instrument like Tiliqua.
- RoHS: Restrictions on Hazardous Substances - this means that we are not using any nasty chemicals or leaded solder for example. Usually no testing is required to meet this, you just collect documentation for every single component and assembly step of your product and make sure that each part meets RoHS.

If you go to a test lab they will tell you exactly which standards are relevant to your product. For something like a Eurorack Module, it's the emissions requirements (radiated radio emissions) and ESD immunity (sparks from fingers) that are the most challenging.

The Setup
---------

Example system
**************

At a test lab, you are expected to bring a self-contained test system with your product in use. This means in the end it is not just your Eurorack module that must meet EMC, but the entire system, including the mains cable!

For Tiliqua's testing I put together a small system like this, including not just the Tiliqua but also a screen module, display cable, headphone interface and so on:

PHOTO: example system

The other modules, mains adapter, case, and DC-DC converters inside the case will all affect the test result. So, if you're going to a test lab for the first time, best to bring spares to swap out for each part.

Pre-test chamber
****************

Time at a test lab can be expensive. To save time and money, I built a small EMC test chamber using a slighty modified version of the `design you'll find here <https://essentialscrap.com/tem_cell/>`_. Here's a picture of mine:

PHOTO: test chamber with example system inside it

The chamber is called a "TEM cell", and you can visualize it like an oversized transmission line - a huge coax cable, which you can put your device into to take broadband measurements. A chamber like this is even allowed as an official measurement method (if you get a much more expensive and calibrated one!).

Spectrum Analyzer
*****************

For a cheap spectrum analyzer, I decided to use a TinySA Pro.

With a TEM cell, there are tables you can use to convert measurements from a cell like this into (rough) far-field measurements, to get an idea of whether you would pass the 'real' test or not.

In my case, I used the TinySA preset found here to check my own measurements against the rough EMC standard thresholds. This results in a nice red 'fail line' that is helpful to identify the problematic areas:

PHOTO: tinySA pro with fail line

Note: I discovered the preset above requires firmware version vXXX to work properly, you might want to downgrade to that firmware version in order to use the preset

Dodgy sniffer probe
*******************

PHOTO: dodgy sniffer probe

Unfortunately this probe did not end up being very useful, it often seemed to point at an area of the board that had nothing to do with the source of the noise!

Pre-testing: Findings
---------------------

Fail!
*****

PHOTO: failing the limits on R3

Learning 1: SMPS input filtering
********************************

PHOTO: routing on input: R2 vs R4

Learning 2: FPGA drive strengths, series resistors
**************************************************

PHOTO: amaranth drive settings

PHOTO: routing on series resistors going to FFC

Learning 3: Split ground planes
*******************************

PHOTO: clamshell with arrow

PHOTO: shorting bottom ground plane to stubs

Learning 4: Spread Spectrum
***************************

PHOTO: capture with and without spread spectrum

DETAILS: si5351 driver

Lab-testing: Findings
---------------------

Learning 5: Long cables
***********************

PHOTO: long cables (faraday photo)

Bring backups!

Learning 6: ESD is no joke
***************************

EMC: Conclusion
---------------

Bonus: Dynamic Clocking!
------------------------

PHOTO: edid decoding?

Bonus: New Amaranth Cores!
--------------------------


Bonus: Crowd Supply and Tariffs
-------------------------------

