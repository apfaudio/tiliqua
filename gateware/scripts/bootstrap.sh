#!/bin/bash

pdm flash archive build/bootloader-*/*.tar.gz --noconfirm
pdm flash archive build/polysyn-*/*.tar.gz --slot 0 --noconfirm
pdm flash archive build/macro-osc-*/*.tar.gz --slot 1 --noconfirm
pdm flash archive build/xbeam-*/*.tar.gz --slot 2 --noconfirm
pdm flash archive build/sid-*/*.tar.gz --slot 3 --noconfirm
pdm flash archive build/selftest-*/*.tar.gz --slot 4 --noconfirm
