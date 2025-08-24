#!/bin/bash

# Generate bitstreams used by 'apfbug' for jumping to new bitstreams in SPI flash.

BOOTSTUB_ROOT="../../apfelbug/bootstub"

parallel --halt now,fail=1 --jobs 0 --ungroup "{} $@" ::: \
  "pdm bootstub build --name=bootstub1 --bootaddr=0x100000" \
  "pdm bootstub build --name=bootstub2 --bootaddr=0x200000" \
  "pdm bootstub build --name=bootstub3 --bootaddr=0x300000" \
  "pdm bootstub build --name=bootstub4 --bootaddr=0x400000" \
  "pdm bootstub build --name=bootstub5 --bootaddr=0x500000" \
  "pdm bootstub build --name=bootstub6 --bootaddr=0x600000" \
  "pdm bootstub build --name=bootstub7 --bootaddr=0x700000" \
  "pdm bootstub build --name=bootstub8 --bootaddr=0x800000" \

cp build/bootstub1-*/top.bit $BOOTSTUB_ROOT/bootstub1.bit
cp build/bootstub2-*/top.bit $BOOTSTUB_ROOT/bootstub2.bit
cp build/bootstub3-*/top.bit $BOOTSTUB_ROOT/bootstub3.bit
cp build/bootstub4-*/top.bit $BOOTSTUB_ROOT/bootstub4.bit
cp build/bootstub5-*/top.bit $BOOTSTUB_ROOT/bootstub5.bit
cp build/bootstub6-*/top.bit $BOOTSTUB_ROOT/bootstub6.bit
cp build/bootstub7-*/top.bit $BOOTSTUB_ROOT/bootstub7.bit
cp build/bootstub8-*/top.bit $BOOTSTUB_ROOT/bootstub8.bit
