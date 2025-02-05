#pragma once

#include <vector>
#include <queue>
#include <cstdint>

template <typename DutT> class I2SDriver {
private:
    // DUT reference
    DutT* dut;

    // Channel state
    struct ChannelState {
        std::queue<int16_t> inject_queue;     // Samples to transmit
        std::vector<int16_t> captured;        // Received samples
        int16_t current_tx_sample = 0;        // Sample being transmitted
        uint32_t current_rx_sample = 0;       // Accumulator for received bits
        bool tx_active = false;               // Transmission in progress
    };

    static constexpr uint8_t N_CHANNELS = 4;
    static constexpr uint8_t SLOT_BITS = 32;
    static constexpr uint8_t SAMPLE_BITS = 16;

    ChannelState channels[N_CHANNELS];
    uint8_t current_channel = 0;
    uint8_t bit_counter = 0;
    bool last_lrck = false;
    bool last_bick = false;

public:
    explicit I2SDriver(DutT* dut) : dut(dut) {}

    void post_edge() {
        const bool current_lrck = dut->i2s_lrck;
        const bool current_bick = dut->i2s_bick;

        // Detect LRCK transition (frame start)
        if (current_lrck != last_lrck && current_lrck) {
            current_channel = 2;
            bit_counter = 0;
            start_channel_transmission(current_channel);
        }

        // Detect BICK falling edge (end of bit period)
        if (last_bick && !current_bick) {
            bit_counter++;
            // Progress through TDM slots
            if (bit_counter >= SLOT_BITS) {
                bit_counter = 0;
                current_channel = (current_channel + 1) % N_CHANNELS;
                start_channel_transmission(current_channel);
            }
        }

        // Capture on BICK rising edge
        if (!last_bick && current_bick) {
            handle_rx_bit();
        }

        // Transmit on BICK falling edge
        if (last_bick && !current_bick) {
            handle_tx_bit();
        }

        last_lrck = current_lrck;
        last_bick = current_bick;
    }

    // API Methods
    void inject_sample(uint8_t channel, int16_t sample) {
        if (channel < N_CHANNELS) {
            channels[channel].inject_queue.push(sample);
        }
    }

    const std::vector<int16_t>& get_captured_samples(uint8_t channel) const {
        static const std::vector<int16_t> empty;
        return (channel < N_CHANNELS) ? channels[channel].captured : empty;
    }

private:
    void start_channel_transmission(uint8_t channel) {
        ChannelState& cs = channels[channel];
        if (!cs.inject_queue.empty()) {
            cs.current_tx_sample = cs.inject_queue.front();
            cs.inject_queue.pop();
            cs.tx_active = true;
        } else {
            cs.tx_active = false;
        }
    }

    void handle_rx_bit() {
        if (bit_counter < SAMPLE_BITS) {
            ChannelState& cs = channels[current_channel];
            cs.current_rx_sample = (cs.current_rx_sample << 1) | (dut->i2s_sdin1 & 1);
            if (bit_counter == SAMPLE_BITS - 1) {
                // Sign-extend and store captured sample
                int16_t sample = static_cast<int32_t>(
                    (cs.current_rx_sample << (32 - SAMPLE_BITS)) >> (32 - SAMPLE_BITS)
                );
                // FIXME: migrate this conversion to bit timings!
                sample = (sample > 16384) ? (sample - 32769) : sample;
                cs.captured.push_back(sample<<1);
                cs.current_rx_sample = 0;
            }
        }
    }

    void handle_tx_bit() {
        ChannelState& cs = channels[current_channel];
        if (bit_counter < SAMPLE_BITS && cs.tx_active) {
            // Transmit MSB first
            dut->i2s_sdout1 = (cs.current_tx_sample >> (SAMPLE_BITS - bit_counter)) & 1;
        } else {
            // Zero padding for rest of slot
            dut->i2s_sdout1 = 0;
        }
    }
};

