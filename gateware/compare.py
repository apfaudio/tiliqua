#!/bin/python3

from amaranth import *
from amaranth.back import rtlil, verilog

from amaranth_future import fixed
from tiliqua import dsp

if __name__ == "__main__":
    dut = dsp.SVF()
    print(verilog.convert(dut, name='Dut', ports=[dut.i.payload.as_value(), dut.o.payload.as_value()]))
