# Tiliqua

<sup>WARN: 🚧 under construction! 🚧 - this module is in active development</sup>

**Tiliqua is a powerful, open hardware FPGA-based audio multitool for Eurorack.**

For updates, join the [matrix chatroom](https://matrix.to/#/#apfaudio:matrix.org), subscribe to the [Crowd Supply page](https://www.crowdsupply.com/apfaudio/tiliqua) or my own [mailing list](https://apf.audio/)

<img src="doc/img/tiliqua-front-left.jpg" width="500">

# Documentation

Available at [apfaudio.github.io/tiliqua](https://apfaudio.github.io/tiliqua/) (🚧 under construction)

Documentation is built from source in `gateware/docs`.

# Community

`apfaudio` has a Matrix channel, [#apfaudio:matrix.org](https://matrix.to/#/#apfaudio:matrix.org). Feel free to join to ask questions or discuss ongoing development.

Participants in this project are expected to adhere to the [Berlin Code of Conduct](https://berlincodeofconduct.org/).

## Builds on the following (awesome) open projects

- The [Amaranth HDL](https://github.com/amaranth-lang/amaranth) and [Amaranth SoC](https://github.com/amaranth-lang/amaranth-soc) projects.
- Audio interface and gateware from my existing [eurorack-pmod](https://github.com/apfaudio/eurorack-pmod) project.
- USB interface and gateware based on [LUNA and Cynthion](https://github.com/greatscottgadgets/luna/) projects.
- USB Audio gateware and descriptors based on [adat-usb2-audio-interface](https://github.com/hansfbaier/adat-usb2-audio-interface).
- Some gateware is also inherited from the [Glasgow](https://github.com/GlasgowEmbedded/glasgow) project.

# License

The hardware and gateware in this project is largely covered under the CERN Open-Hardware License V2 CERN-OHL-S, mirrored in the LICENSE text in this repository. Some gateware and software is covered under the BSD 3-clause license - check the header of the individual source files for specifics.

**Copyright (C) 2024 Sebastian Holzapfel**

The above LICENSE and copyright notice do NOT apply to imported artifacts in this repository (i.e datasheets, third-party footprints), or dependencies released under a different (but compatible) open-source license.

# Derivative works

As an addendum to the above license: if you create or manufacture your own derivative hardware, the name `apf.audio`, the names of any `apf.audio` products and the names of the authors, are *not to be used in derivative hardware or marketing materials*, except where obligated for attribution and for retaining the above copyright notice.

For example, your 3U adaptation of "apf.audio Tiliqua" could be called "Gizzard Modular - Lizardbobulator".
