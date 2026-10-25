#!/bin/bash

# Build all SoC bitstreams in parallel, terminate early
# if any of them fail. Extra arguments to this script are
# forwarded to every command (e.g. --hw or --resolution flags)

parallel --halt now,fail=1 --jobs 0 --ungroup "{} $@" ::: \
  "R35_OUTPUT_ALWAYS_MUTE=1 pdm bootloader build" \
  "pdm polysyn build" \
  "TILIQUA_ASQ_I_BITS=2 TILIQUA_ASQ_WIDTH=17 pdm selftest build" \
  "TILIQUA_ASQ_I_BITS=2 TILIQUA_ASQ_WIDTH=18 pdm xbeam build --fs-192khz" \
  "pdm macro_osc build" \
  "pdm sid build" \
  "pdm sampler build"
