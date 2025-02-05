#pragma once

template <typename DutT> class PSRAMDriver {
private:
    DutT* dut;
    uint8_t *psram_data = nullptr;
    uint32_t psram_size_bytes = 1024*1024*32;
    uint64_t idle_lo = 0;
    uint64_t idle_hi = 0;

public:
    explicit PSRAMDriver(DutT* dut) : dut(dut) {
        psram_data = (uint8_t*)malloc(psram_size_bytes);
        memset(psram_data, 0, psram_size_bytes);
    }

    void post_edge() {
        if (dut->clk_sync) {
            if (dut->read_ready) {
                dut->read_data_view =
                    (psram_data[dut->address_ptr+3] << 24)  |
                    (psram_data[dut->address_ptr+2] << 16)  |
                    (psram_data[dut->address_ptr+1] << 8)   |
                    (psram_data[dut->address_ptr+0] << 0);
                /*
                if (dut->read_data_view != 0) {
                    printf("read %x@%x\n", dut->read_data_view, dut->address_ptr);
                }
                */
                dut->eval();
            }

            if (dut->write_ready) {
                psram_data[dut->address_ptr+0] = (uint8_t)(dut->write_data >> 0);
                psram_data[dut->address_ptr+1] = (uint8_t)(dut->write_data >> 8);
                psram_data[dut->address_ptr+2] = (uint8_t)(dut->write_data >> 16);
                psram_data[dut->address_ptr+3] = (uint8_t)(dut->write_data >> 24);
                //printf("write %x@%x\n", dut->write_data, dut->address_ptr);
                dut->eval();
            }

        }

        // Track PSRAM usage to see how close we are to saturation
        if (dut->idle == 1) {
            idle_hi += 1;
        } else {
            idle_lo += 1;
        }
    }

    void post_sim() {
        printf("RAM bandwidth: idle: %i, !idle: %i, percent_used: %f\n", idle_hi, idle_lo,
                100.0f * (float)idle_lo / (float)(idle_hi + idle_lo));
    }
};
