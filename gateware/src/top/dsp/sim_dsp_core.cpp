// Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
//
// SPDX-License-Identifier: CERN-OHL-S-2.0
//

// Simple verilator wrapper for simulating self-contained Tiliqua DSP core.

#if defined VM_TRACE_FST && VM_TRACE_FST == 1
#include <verilated_fst_c.h>
#endif

#include "Vtiliqua_soc.h"
#include "verilated.h"

#include "plot.h"
#define VERILATOR_DUT_TYPE Vtiliqua_soc
#include "i2s.h"

#include <cmath>

int main(int argc, char** argv) {

    VerilatedContext* contextp = new VerilatedContext;
    contextp->commandArgs(argc, argv);
    Vtiliqua_soc* top = new Vtiliqua_soc{contextp};

#if defined VM_TRACE_FST && VM_TRACE_FST == 1
    Verilated::traceEverOn(true);
    VerilatedFstC* tfp = new VerilatedFstC;
    top->trace(tfp, 99);  // Trace 99 levels of hierarchy (or see below)
    tfp->open("simx.fst");
#endif
    uint64_t sim_time =  10000000000;

    contextp->timeInc(1);
    top->rst_sync = 1;
    top->rst_audio = 1;
    top->rst_fast = 1;
    top->eval();

#if defined VM_TRACE_FST && VM_TRACE_FST == 1
    tfp->dump(contextp->time());
#endif

    contextp->timeInc(1);
    top->rst_sync = 0;
    top->rst_audio = 0;
    top->rst_fast = 0;
    top->eval();

#if defined VM_TRACE_FST && VM_TRACE_FST == 1
    tfp->dump(contextp->time());
#endif

    uint64_t ns_in_s = 1e9;
    uint64_t ns_in_sync_cycle   = ns_in_s /  SYNC_CLK_HZ;
    uint64_t  ns_in_audio_cycle = ns_in_s / AUDIO_CLK_HZ;
    uint64_t  ns_in_fast_cycle  = ns_in_s / FAST_CLK_HZ;

    printf("sync domain is: %i KHz (%i ns/cycle)\n",  SYNC_CLK_HZ/1000,  ns_in_sync_cycle);
    printf("audio clock is: %i KHz (%i ns/cycle)\n", AUDIO_CLK_HZ/1000, ns_in_audio_cycle);
    printf("fast clock is: %i KHz (%i ns/cycle)\n", FAST_CLK_HZ/1000, ns_in_fast_cycle);

#ifdef PSRAM_SIM
    uint32_t psram_size_bytes = 1024*1024*16;
    uint8_t *psram_data = (uint8_t*)malloc(psram_size_bytes);
    memset(psram_data, 0, psram_size_bytes);

    uint64_t idle_lo = 0;
    uint64_t idle_hi = 0;
#endif

    I2SDriver i2s_driver(top);

    for (int i = 0; i != 10000; ++i) {
        i2s_driver.inject_sample(0, (int16_t)10000.0*sin((float)i / 50.0));
        i2s_driver.inject_sample(1, (int16_t)10000.0*sin((float)i / 10.0));
        i2s_driver.inject_sample(2, (int16_t)10000.0*sin((float)i / 30.0));
        i2s_driver.inject_sample(3, (int16_t)10000.0*sin((float)i /  5.0));
    }

    while (contextp->time() < sim_time && !contextp->gotFinish()) {

        uint64_t timestamp_ns = contextp->time() / 1000;

        // Sync clock domain (PSRAM read/write simulation)
        if (timestamp_ns % (ns_in_sync_cycle/2) == 0) {
            top->clk_sync = !top->clk_sync;
#ifdef PSRAM_SIM
            if (top->clk_sync) {
                if (top->read_ready) {
                    top->read_data_view =
                        (psram_data[top->address_ptr+3] << 24)  |
                        (psram_data[top->address_ptr+2] << 16)  |
                        (psram_data[top->address_ptr+1] << 8)   |
                        (psram_data[top->address_ptr+0] << 0);
                    /*
                    if (top->read_data_view != 0) {
                        printf("read %x@%x\n", top->read_data_view, top->address_ptr);
                    }
                    */
                    top->eval();
                }

                if (top->write_ready) {
                    psram_data[top->address_ptr+0] = (uint8_t)(top->write_data >> 0);
                    psram_data[top->address_ptr+1] = (uint8_t)(top->write_data >> 8);
                    psram_data[top->address_ptr+2] = (uint8_t)(top->write_data >> 16);
                    psram_data[top->address_ptr+3] = (uint8_t)(top->write_data >> 24);
                    //printf("write %x@%x\n", top->write_data, top->address_ptr);
                    top->eval();
                }

            }
#endif
        }


        // Audio clock domain (Audio stimulation)
        if (timestamp_ns % (ns_in_audio_cycle/2) == 0) {
            top->clk_audio = !top->clk_audio;
            i2s_driver.post_edge();
        }

        // Fast clock domain (RAM domain simulation)
        if (timestamp_ns % (ns_in_fast_cycle/2) == 0) {
            top->clk_fast = !top->clk_fast;
        }

#ifdef PSRAM_SIM
        // Track PSRAM usage to see how close we are to saturation
        if (top->idle == 1) {
            idle_hi += 1;
        } else {
            idle_lo += 1;
        }
#endif

        contextp->timeInc(1000);
        top->eval();
#if defined VM_TRACE_FST && VM_TRACE_FST == 1
        tfp->dump(contextp->time());
#endif
    }

#ifdef PSRAM_SIM
    printf("RAM bandwidth: idle: %i, !idle: %i, percent_used: %f\n", idle_hi, idle_lo,
            100.0f * (float)idle_lo / (float)(idle_hi + idle_lo));
#endif

#if defined VM_TRACE_FST && VM_TRACE_FST == 1
    tfp->close();
#endif

    signalsmith::plot::Plot2D plot(1200, 400);
    for (int ax = 0; ax != 4; ++ax) {
        auto &axes = plot.newY(1.0 - 0.25*ax, 1.0 - 0.25*(ax+1));
        axes.linear(-32768, 32768);
        auto &line = plot.line(plot.x, axes).fillToY(ax);
        int x = 0;
        for (auto &y : i2s_driver.get_captured_samples(ax)) {
            line.add(x, y);
            ++x;
        }
    }
    plot.write("sim-i2s-outputs.svg");

    return 0;
}
