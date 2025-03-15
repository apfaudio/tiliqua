# Tiliqua

**Tiliqua is a powerful, open hardware FPGA-based audio multitool for Eurorack.** It looks like this:

![image](https://github.com/user-attachments/assets/4a308920-97dc-4b73-aaac-7f735a71eec0)

# ⮕[Documentation](https://apfaudio.github.io/tiliqua/)⬅

# Updates / Community

For updates, subscribe to the [Crowd Supply page](https://www.crowdsupply.com/apfaudio/tiliqua), join the [matrix chatroom](https://matrix.to/#/#apfaudio:matrix.org), or my own [mailing list](https://apf.audio/).

`apfaudio` has a Matrix channel, [#apfaudio:matrix.org](https://matrix.to/#/#apfaudio:matrix.org). Feel free to join to ask questions or discuss ongoing development.

Participants in this project are expected to adhere to the [Berlin Code of Conduct](https://berlincodeofconduct.org/).

# Acknowledgements

This project would be nothing without the hard work of many (awesome) open-source projects. An exhaustive list would take pages, here I mention only a crucial subset:

- Python-based HDL and SoC framework: The [Amaranth HDL](https://github.com/amaranth-lang/amaranth) and [Amaranth SoC](https://github.com/amaranth-lang/amaranth-soc) projects.
- USB and SoC gateware: The [LUNA and Cynthion](https://github.com/greatscottgadgets/luna/) projects.
- RISCV softcore: The [VexRiscv and SpinalHDL projects](https://github.com/SpinalHDL/VexRiscv)
- USB audio gateware and descriptors: The [adat-usb2-audio-interface](https://github.com/hansfbaier/adat-usb2-audio-interface) project.
- Some gateware (e.g. I2C state machines) are inherited from the [Glasgow](https://github.com/GlasgowEmbedded/glasgow) project.
- Audio interface and gateware: my existing [eurorack-pmod](https://github.com/apfaudio/eurorack-pmod) project.
- SID emulation gateware: [reDIP-SID](https://github.com/daglem/reDIP-SID)
- The "mi-plaits-dsp-rs" project: [mi-plaits-dsp](https://github.com/sourcebox/mi-plaits-dsp-rs)
- The "pico-dirtyJtag" project forms a big chunk of the RP2040 firmware [pico-dirtyJtag](github.com/phdussud/pico-dirtyJtag)

## Funding

We would like to acknowledge partial funding of the [Tiliqua project](https://nlnet.nl/project/Tiliqua/) from the [NGI Commons Fund](https://nlnet.nl/commonsfund), a fund established by [NLnet](https://nlnet.nl/) with financial support from the European Commission’s [Next Generation Internet](https://ngi.eu/) program.

![image](https://github.com/user-attachments/assets/e3eeab37-f5b2-4686-8cb4-5dc49f42ba7d)

# License

The hardware and gateware in this project is largely covered under the CERN Open-Hardware License V2 CERN-OHL-S, mirrored in the LICENSE text in this repository. Some gateware and software is covered under the BSD 3-clause license - check the header of the individual source files for specifics.

**Copyright (C) 2024 Sebastian Holzapfel**

The above LICENSE and copyright notice do NOT apply to imported artifacts in this repository (i.e datasheets, third-party footprints), or dependencies released under a different (but compatible) open-source license.

# Derivative works

As an addendum to the above license: if you create or manufacture your own derivative hardware, the name `apf.audio`, the names of any `apf.audio` products and the names of the authors, are *not to be used in derivative hardware or marketing materials*, except where obligated for attribution and for retaining the above copyright notice.

For example, your 3U adaptation of "apf.audio Tiliqua" could be called "Gizzard Modular - Lizardbobulator".
