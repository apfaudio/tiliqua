// A (quite dirty) simulation harness that simulates the vectorscope core
// and uses it to generate some bitmap images and full FST traces for examination.

#include <verilated_fst_c.h>

#include "Vtiliqua_soc.h"
#include "verilated.h"

#include "i2s.h"
#include "psram.h"

#include <cmath>

#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

int gcd(int a, int b)
{
    int temp;
    while (b != 0)
    {
        temp = a % b;

        a = b;
        b = temp;
    }
    return a;
}

int main(int argc, char** argv) {
    VerilatedContext* contextp = new VerilatedContext;
    contextp->commandArgs(argc, argv);
    Vtiliqua_soc* top = new Vtiliqua_soc{contextp};

#if VM_TRACE_FST == 1
    Verilated::traceEverOn(true);
    VerilatedFstC* tfp = new VerilatedFstC;
    top->trace(tfp, 99);  // Trace 99 levels of hierarchy (or see below)
    tfp->open("simx.fst");
#endif

    uint64_t sim_time =  75e9; // 75msec is ~ 4 frames

    uint64_t ns_in_s = 1e9;
    uint64_t ns_in_sync_cycle   = ns_in_s /  SYNC_CLK_HZ;
    uint64_t  ns_in_dvi_cycle   = ns_in_s /   DVI_CLK_HZ;
    uint64_t  ns_in_audio_cycle = ns_in_s / AUDIO_CLK_HZ;

    printf("sync domain is: %i KHz (%i ns/cycle)\n",  SYNC_CLK_HZ/1000,  ns_in_sync_cycle);
    printf("pixel clock is: %i KHz (%i ns/cycle)\n",   DVI_CLK_HZ/1000,   ns_in_dvi_cycle);
    printf("audio clock is: %i KHz (%i ns/cycle)\n", AUDIO_CLK_HZ/1000, ns_in_audio_cycle);

    uint64_t clk_gcd = gcd(SYNC_CLK_HZ, DVI_CLK_HZ);
    uint64_t ns_in_gcd = ns_in_s / clk_gcd;
    printf("GCD is: %i KHz (%i ns/cycle)\n", clk_gcd/1000, ns_in_gcd);

    contextp->timeInc(1);
    top->rst_sync = 1;
    top->rst_dvi = 1;
    top->rst_audio = 1;
    top->eval();

#if VM_TRACE_FST == 1
    tfp->dump(contextp->time());
#endif

    contextp->timeInc(1);
    top->rst_sync = 0;
    top->rst_dvi = 0;
    top->rst_audio = 0;
    top->eval();

#if VM_TRACE_FST == 1
    tfp->dump(contextp->time());
#endif

    PSRAMDriver psram_driver(top);
    I2SDriver i2s_driver(top);

    for (int i = 0; i != 50000; ++i) {
        i2s_driver.inject_sample(0, (int16_t)10000.0*cos((float)i /  300.0));
        i2s_driver.inject_sample(1, (int16_t)10000.0*sin((float)i /  150.0));
    }

    uint32_t im_stride = 3;
    uint8_t *image_data = (uint8_t*)malloc(DVI_H_ACTIVE*DVI_V_ACTIVE*im_stride);
    memset(image_data, 0, DVI_H_ACTIVE*DVI_V_ACTIVE*im_stride);

    uint32_t frames = 0;

    while (contextp->time() < sim_time && !contextp->gotFinish()) {

        uint64_t timestamp_ns = contextp->time() / 1000;

        // DVI clock domain (PHY output simulation to bitmap image)
        if (timestamp_ns % (ns_in_dvi_cycle/2) == 0) {
            top->clk_dvi = !top->clk_dvi;
            if (top->clk_dvi) {
                uint32_t x = top->dvi_x;
                uint32_t y = top->dvi_y;
                if (x < DVI_H_ACTIVE && y < DVI_V_ACTIVE) {
                    image_data[y*DVI_H_ACTIVE*3 + x*3 + 0] = top->dvi_r;
                    image_data[y*DVI_H_ACTIVE*3 + x*3 + 1] = top->dvi_g;
                    image_data[y*DVI_H_ACTIVE*3 + x*3 + 2] = top->dvi_b;
                }
                if (x == DVI_H_ACTIVE-1 && y == DVI_V_ACTIVE-1) {
                    char name[64];
                    sprintf(name, "frame%02d.bmp", frames);
                    printf("out %s\n", name);
                    stbi_write_bmp(name, DVI_H_ACTIVE, DVI_V_ACTIVE, 3, image_data);
                    ++frames;
                }
            }
        }

        // Sync clock domain (PSRAM read/write simulation)
        if (timestamp_ns % (ns_in_sync_cycle/2) == 0) {
            top->clk_sync = !top->clk_sync;
            psram_driver.post_edge();
        }

        // Audio clock domain (Audio stimulation)
        if (timestamp_ns % (ns_in_audio_cycle/2) == 0) {
            top->clk_audio = !top->clk_audio;
            i2s_driver.post_edge();
        }

        contextp->timeInc(1000);
        top->eval();
#if VM_TRACE_FST == 1
        tfp->dump(contextp->time());
#endif
    }

    psram_driver.post_sim();

#if VM_TRACE_FST == 1
    tfp->close();
#endif
    return 0;
}
