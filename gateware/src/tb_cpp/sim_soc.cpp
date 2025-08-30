// A (quite dirty) simulation harness that simulates the tiliqua_soc core
// and uses it to generate some full FST traces for examination.

#include <cmath>

#if VM_TRACE_FST == 1
#include <verilated_fst_c.h>
#endif

#include "Vtiliqua_soc.h"
#include "verilated.h"

#include "i2s.h"
#include "psram.h"
#include "dvi.h"

#include <fstream>

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

    uint64_t sim_time =  5000e9;

    uint64_t ns_in_s = 1e9;
    uint64_t ns_in_sync_cycle   = ns_in_s /  SYNC_CLK_HZ;
    uint64_t  ns_in_dvi_cycle   = ns_in_s /   DVI_CLK_HZ;
    uint64_t  ns_in_audio_cycle = ns_in_s / AUDIO_CLK_HZ;
    printf("sync domain is: %i KHz (%i ns/cycle)\n",  SYNC_CLK_HZ/1000,  ns_in_sync_cycle);
    printf("pixel clock is: %i KHz (%i ns/cycle)\n",   DVI_CLK_HZ/1000,   ns_in_dvi_cycle);
    printf("audio clock is: %i KHz (%i ns/cycle)\n", AUDIO_CLK_HZ/1000, ns_in_audio_cycle);

    contextp->timeInc(1);
    top->rst_sync = 1;
    top->rst_dvi  = 1;
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


    uint32_t spiflash_size_bytes = 1024*1024*32;
    uint32_t spiflash_offset = 0x00100000; // fw base
    char *spiflash_data = (char*)malloc(spiflash_size_bytes);
    memset(spiflash_data, 0, spiflash_size_bytes);

#ifdef SPIFLASH_FW_OFFSET
    std::ifstream fin(FIRMWARE_BIN_PATH, std::ios::in | std::ios::binary);
    fin.read(spiflash_data + SPIFLASH_FW_OFFSET, spiflash_size_bytes);
#endif

    PSRAMDriver psram_driver(top);
    I2SDriver i2s_driver(top);
    DVIDriver dvi_driver(top);

    for (int i = 0; i != 50000; ++i) {
        i2s_driver.inject_sample(0, (int16_t)10000.0*cos((float)i /  300.0));
        i2s_driver.inject_sample(1, (int16_t)10000.0*sin((float)i /  150.0));
    }

#ifdef PSRAM_FW_OFFSET
    std::ifstream fin(FIRMWARE_BIN_PATH, std::ios::in | std::ios::binary);
    fin.read((char*)psram_driver.psram_data + PSRAM_FW_OFFSET, psram_driver.psram_size_bytes);
#endif

#ifdef BOOTINFO_BIN_PATH
    // Load bootinfo at the calculated offset in PSRAM
    std::ifstream bootinfo_fin(BOOTINFO_BIN_PATH, std::ios::in | std::ios::binary);
    if (bootinfo_fin) {
        bootinfo_fin.read((char*)psram_driver.psram_data + BOOTINFO_OFFSET, 1024);
        printf("Loaded bootinfo to PSRAM offset 0x%x\n", BOOTINFO_OFFSET);
    } else {
        printf("Warning: Could not load bootinfo from %s\n", BOOTINFO_BIN_PATH);
    }
#endif


    while (contextp->time() < sim_time && !contextp->gotFinish()) {

        uint64_t timestamp_ns = contextp->time() / 1000;

        top->spiflash_data = ((uint32_t*)spiflash_data)[top->spiflash_addr];

        // DVI clock domain (PHY output simulation to bitmap image)
        if (timestamp_ns % (ns_in_dvi_cycle/2) == 0) {
            top->clk_dvi = !top->clk_dvi;
            dvi_driver.post_edge();
        }

        // Sync clock domain (PSRAM read/write simulation, UART printouts)
        if (timestamp_ns % (ns_in_sync_cycle/2) == 0) {
            top->clk_sync = !top->clk_sync;
            psram_driver.post_edge();
            top->eval();
            if (top->clk_sync) {
                if (top->uart0_w_stb) {
                    putchar(top->uart0_w_data);
                }
            }
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
#if VM_TRACE_FST == 1
    tfp->close();
#endif
    return 0;
}
