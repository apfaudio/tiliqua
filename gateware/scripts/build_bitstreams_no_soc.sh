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
  "pdm dsp build --dsp-core=mdiff" \
  "pdm dsp build --dsp-core=resampler" \
  "pdm dsp build --dsp-core=noise" \
  "pdm dsp build --dsp-core=stft_mirror" \
  "pdm dsp build --dsp-core=vocode" \
  "pdm dsp build --dsp-core=dwo" \
  "TILIQUA_ASQ_WIDTH=17 pdm dsp build --dsp-core=mmm" \
  "pdm beamrace build --core=stripes --modeline 1280x720p60 --name STRIPES12" \
  "pdm beamrace build --core=balls --modeline 1280x720p60 --name BALLS12" \
  "pdm beamrace build --core=checkers --modeline 1280x720p60 --name CHECKERS12" \
  "pdm vectorscope_no_soc build --fs-192khz --modeline 1280x720p60 --name VSCOPE12" \
  "pdm vectorscope_no_soc build --fs-192khz --spectrogram --modeline 1280x720p60 --name=SPECTRO12" \
  "pdm bootstub build" \
  "pdm usb_audio build" \
  "pdm usb_host build" \
  "pdm wavplay build"

# build static modeline bitstreams again at 720x720p60
# this is not done in parallel as it trips a strange bug during amaranth
# elaboration that I have not been able to root cause yet.
parallel --halt now,fail=1 --jobs 0 --ungroup "{} $@" ::: \
  "pdm beamrace build --core=stripes --modeline 720x720p60r2 --name STRIPES7" \
  "pdm beamrace build --core=balls --modeline 720x720p60r2 --name BALLS7" \
  "pdm beamrace build --core=checkers --modeline 720x720p60r2 --name CHECKERS7" \
  "pdm vectorscope_no_soc build --fs-192khz --modeline 720x720p60r2 --name VSCOPE7" \
  "pdm vectorscope_no_soc build --fs-192khz --spectrogram --modeline 720x720p60r2 --name=SPECTRO7"
