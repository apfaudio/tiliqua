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
#include "i2s.h"
#include "psram.h"
#include "tinywav.h"

#include <cmath>

#define NUM_CHANNELS 1
#define SAMPLE_RATE 48000
#define BLOCK_SIZE 480

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
    uint64_t sim_time =  300000000000;

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
    PSRAMDriver psram_driver(top);
#endif

    I2SDriver i2s_driver(top);

    TinyWav wav_read0;
    tinywav_open_read(&wav_read0,
        "carrier.wav",
        TW_INLINE
    );
    TinyWav wav_read1;
    tinywav_open_read(&wav_read1,
        "modulator.wav",
        TW_INLINE
    );

    for (int i = 0; i != 70000; ++i) {
        // Sawtooth carrier
        //i2s_driver.inject_sample(0, (int16_t)70.0*((int16_t)(i % 400) - 200));
        // .wav modulator
        if (i % BLOCK_SIZE == 0) {
            float samples[NUM_CHANNELS * BLOCK_SIZE];
            tinywav_read_f(&wav_read0, samples, BLOCK_SIZE);
            for (int j = 0; j != BLOCK_SIZE; ++j) {
                i2s_driver.inject_sample(0, (int16_t)(samples[j]*16000.0));
            }
            tinywav_read_f(&wav_read1, samples, BLOCK_SIZE);
            for (int j = 0; j != BLOCK_SIZE; ++j) {
                i2s_driver.inject_sample(1, (int16_t)(samples[j]*16000.0));
            }
        }
        //i2s_driver.inject_sample(1, (int16_t)10000.0*sin((float)i / 10.0));
        i2s_driver.inject_sample(2, (int16_t)10000.0*sin((float)i / 30.0));
        i2s_driver.inject_sample(3, (int16_t)10000.0*sin((float)i /  5.0));
    }

    while (contextp->time() < sim_time && !contextp->gotFinish()) {

        uint64_t timestamp_ns = contextp->time() / 1000;

        // Sync clock domain (PSRAM read/write simulation)
        if (timestamp_ns % (ns_in_sync_cycle/2) == 0) {
            top->clk_sync = !top->clk_sync;
#ifdef PSRAM_SIM
            psram_driver.post_edge();
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

        contextp->timeInc(1000);
        top->eval();
#if defined VM_TRACE_FST && VM_TRACE_FST == 1
        tfp->dump(contextp->time());
#endif
    }

#ifdef PSRAM_SIM
    psram_driver.post_sim();
#endif

#if defined VM_TRACE_FST && VM_TRACE_FST == 1
    tfp->close();
#endif


    /*
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
    */

    TinyWav wav_write;
    tinywav_open_write(&wav_write,
        NUM_CHANNELS,
        SAMPLE_RATE,
        TW_FLOAT32,
        TW_INLINE,
        "out.wav"
    );
    auto s_out = i2s_driver.get_captured_samples(0);
    for (int i = 0; i < s_out.size()-BLOCK_SIZE; i+=BLOCK_SIZE) {
        float samples[BLOCK_SIZE];
        for (int j = 0; j != BLOCK_SIZE; ++j) {
            samples[j] = ((float)s_out[i+j])/32768.0;
        }
        tinywav_write_f(&wav_write, samples, BLOCK_SIZE);
    }
    tinywav_close_write(&wav_write);

    return 0;
}
