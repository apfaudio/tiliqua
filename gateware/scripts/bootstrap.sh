#!/bin/bash

pdm flash archive build/bootloader-*/*.tar.gz --noconfirm
pdm flash archive build/xbeam-*/*.tar.gz --slot 0 --erase-option-storage --noconfirm
pdm flash archive build/polysyn-*/*.tar.gz --slot 1 --erase-option-storage --noconfirm
pdm flash archive build/macro-osc-*/*.tar.gz --slot 2 --erase-option-storage --noconfirm
pdm flash archive build/sid-*/*.tar.gz --slot 3 --erase-option-storage --noconfirm
pdm flash archive build/selftest-*/*.tar.gz --slot 4 --noconfirm
pdm flash archive build/dsp-mdiff-*/*.tar.gz --slot 5 --noconfirm
pdm flash archive build/dsp-nco-*/*.tar.gz --slot 6 --noconfirm
pdm flash archive build/dsp-vocode-*/*.tar.gz --slot 7 --noconfirm
