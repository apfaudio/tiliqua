#!/bin/bash

# Build all non-SoC bitstreams in parallel, terminate early
# if any of them fail. Extra arguments to this script are
# forwarded to every command (e.g. --hw or --skip-build flags)

parallel --halt now,fail=1 --jobs 0 --ungroup "{} $@" ::: \
  "pdm dsp build --dsp-core=mirror" \
  "pdm dsp build --dsp-core=nco" \
  "pdm dsp build --dsp-core=svf" \
  "pdm dsp build --dsp-core=vca" \
  "pdm dsp build --dsp-core=pitch" \
  "pdm dsp build --dsp-core=matrix" \
  "pdm dsp build --dsp-core=touchmix" \
  "pdm dsp build --dsp-core=waveshaper" \
  "pdm dsp build --dsp-core=midicv" \
  "pdm dsp build --dsp-core=psram_pingpong" \
  "pdm dsp build --dsp-core=sram_pingpong" \
  "pdm dsp build --dsp-core=psram_diffuser" \
  "pdm dsp build --dsp-core=sram_diffuser" \
  "pdm dsp build --dsp-core=multi_diffuser" \
  "pdm dsp build --dsp-core=resampler" \
  "pdm dsp build --dsp-core=noise" \
  "pdm dsp build --dsp-core=stft_mirror" \
  "pdm dsp build --dsp-core=vocoder" \
  "pdm vectorscope_no_soc build --fs-192khz" \
  "pdm vectorscope_no_soc build --fs-192khz --spectrogram --name=spectrogram" \
  "pdm bootstub build" \
  "pdm usb_audio build" \
  "pdm usb_host build --midi-device=yamaha-cp73"
