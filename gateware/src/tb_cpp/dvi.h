#pragma once

#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

template <typename DutT> class DVIDriver {
private:
    DutT* dut;

    uint32_t im_stride = 3;
    uint8_t *image_data = nullptr;
    uint32_t frames = 0;
    uint32_t x = 0;
    uint32_t y = 0;

public:
    explicit DVIDriver(DutT* dut) : dut(dut) {
        image_data = (uint8_t*)malloc(DVI_H_ACTIVE*DVI_V_ACTIVE*im_stride);
        memset(image_data, 0, DVI_H_ACTIVE*DVI_V_ACTIVE*im_stride);
    }

    void post_edge() {
        if (dut->clk_dvi) {
            // TODO: handle vsync inversion for different timings
            if (dut->dvi_vsync) {
                x = 0;
                y = 0;
            }
            if (dut->dvi_de) {
                ++x;
                if (x >= DVI_H_ACTIVE) {
                    x = 0;
                    ++y;
                }
                if (y >= DVI_V_ACTIVE) {
                    char name[64];
                    sprintf(name, "frame%02d.bmp", frames);
                    printf("DVIDriver: %s\n", name);
                    stbi_write_bmp(name, DVI_H_ACTIVE, DVI_V_ACTIVE, 3, image_data);
                    ++frames;
                }
                image_data[y*DVI_H_ACTIVE*3 + x*3 + 0] = dut->dvi_r;
                image_data[y*DVI_H_ACTIVE*3 + x*3 + 1] = dut->dvi_g;
                image_data[y*DVI_H_ACTIVE*3 + x*3 + 2] = dut->dvi_b;
            }
        }
    }
};
