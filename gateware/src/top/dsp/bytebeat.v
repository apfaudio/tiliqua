// Copyright 2023 Google LLC.
// SPDX-License-Identifier: Apache-2.0

module bytebeat(
  input wire clk,
  input wire reset,
  input wire [3:0] bytebeat__a_r,
  input wire bytebeat__a_r_vld,
  input wire [3:0] bytebeat__b_r,
  input wire bytebeat__b_r_vld,
  input wire [3:0] bytebeat__c_r,
  input wire bytebeat__c_r_vld,
  input wire [3:0] bytebeat__d_r,
  input wire bytebeat__d_r_vld,
  input wire bytebeat__output_s_rdy,
  output wire [7:0] bytebeat__output_s,
  output wire bytebeat__output_s_vld,
  output wire bytebeat__a_r_rdy,
  output wire bytebeat__b_r_rdy,
  output wire bytebeat__c_r_rdy,
  output wire bytebeat__d_r_rdy
);
  // lint_off MULTIPLY
  function automatic [15:0] umul16b_16b_x_4b (input reg [15:0] lhs, input reg [3:0] rhs);
    begin
      umul16b_16b_x_4b = lhs * rhs;
    end
  endfunction
  // lint_on MULTIPLY
  reg [3:0] ____state_0;
  reg [3:0] ____state_1;
  reg [3:0] ____state_2;
  reg [3:0] ____state_3;
  reg [15:0] ____state_4;
  reg [3:0] __bytebeat__a_r_reg;
  reg __bytebeat__a_r_valid_reg;
  reg [3:0] __bytebeat__b_r_reg;
  reg __bytebeat__b_r_valid_reg;
  reg [3:0] __bytebeat__c_r_reg;
  reg __bytebeat__c_r_valid_reg;
  reg [3:0] __bytebeat__d_r_reg;
  reg __bytebeat__d_r_valid_reg;
  reg [7:0] __bytebeat__output_s_reg;
  reg __bytebeat__output_s_valid_reg;
  wire p0_all_active_inputs_valid;
  wire p0_all_active_states_valid;
  wire bytebeat__output_s_valid_inv;
  wire __bytebeat__output_s_vld_buf;
  wire bytebeat__output_s_valid_load_en;
  wire [3:0] bytebeat__a_r_select;
  wire [3:0] bytebeat__b_r_select;
  wire [3:0] bytebeat__c_r_select;
  wire [3:0] bytebeat__d_r_select;
  wire bytebeat__output_s_load_en;
  wire p0_all_active_states_ready;
  wire [3:0] a;
  wire [3:0] b;
  wire [3:0] c;
  wire [3:0] d;
  wire p0_stage_done;
  wire [15:0] umul_170;
  wire [15:0] shrl_171;
  wire [15:0] umul_172;
  wire [15:0] shrl_173;
  wire pipeline_enable;
  wire bytebeat__a_r_valid_inv;
  wire bytebeat__b_r_valid_inv;
  wire bytebeat__c_r_valid_inv;
  wire bytebeat__d_r_valid_inv;
  wire bytebeat__a_r_valid_load_en;
  wire bytebeat__b_r_valid_load_en;
  wire bytebeat__c_r_valid_load_en;
  wire bytebeat__d_r_valid_load_en;
  wire [15:0] add_187;
  wire bytebeat__a_r_load_en;
  wire bytebeat__b_r_load_en;
  wire bytebeat__c_r_load_en;
  wire bytebeat__d_r_load_en;
  wire [7:0] s__1;
  assign p0_all_active_inputs_valid = 1'h1 & 1'h1 & 1'h1 & 1'h1;
  assign p0_all_active_states_valid = 1'h1;
  assign bytebeat__output_s_valid_inv = ~__bytebeat__output_s_valid_reg;
  assign __bytebeat__output_s_vld_buf = p0_all_active_inputs_valid & p0_all_active_states_valid & 1'h1;
  assign bytebeat__output_s_valid_load_en = bytebeat__output_s_rdy | bytebeat__output_s_valid_inv;
  assign bytebeat__a_r_select = __bytebeat__a_r_valid_reg ? __bytebeat__a_r_reg : 4'h0;
  assign bytebeat__b_r_select = __bytebeat__b_r_valid_reg ? __bytebeat__b_r_reg : 4'h0;
  assign bytebeat__c_r_select = __bytebeat__c_r_valid_reg ? __bytebeat__c_r_reg : 4'h0;
  assign bytebeat__d_r_select = __bytebeat__d_r_valid_reg ? __bytebeat__d_r_reg : 4'h0;
  assign bytebeat__output_s_load_en = __bytebeat__output_s_vld_buf & bytebeat__output_s_valid_load_en;
  assign p0_all_active_states_ready = 1'h1;
  assign a = __bytebeat__a_r_valid_reg ? bytebeat__a_r_select : ____state_0;
  assign b = __bytebeat__b_r_valid_reg ? bytebeat__b_r_select : ____state_1;
  assign c = __bytebeat__c_r_valid_reg ? bytebeat__c_r_select : ____state_2;
  assign d = __bytebeat__d_r_valid_reg ? bytebeat__d_r_select : ____state_3;
  assign p0_stage_done = p0_all_active_states_valid & p0_all_active_inputs_valid & bytebeat__output_s_load_en & p0_all_active_states_ready;
  assign umul_170 = umul16b_16b_x_4b(____state_4, a);
  assign shrl_171 = ____state_4 >> b;
  assign umul_172 = umul16b_16b_x_4b(____state_4, c);
  assign shrl_173 = ____state_4 >> d;
  assign pipeline_enable = p0_stage_done & p0_stage_done;
  assign bytebeat__a_r_valid_inv = ~__bytebeat__a_r_valid_reg;
  assign bytebeat__b_r_valid_inv = ~__bytebeat__b_r_valid_reg;
  assign bytebeat__c_r_valid_inv = ~__bytebeat__c_r_valid_reg;
  assign bytebeat__d_r_valid_inv = ~__bytebeat__d_r_valid_reg;
  assign bytebeat__a_r_valid_load_en = pipeline_enable | bytebeat__a_r_valid_inv;
  assign bytebeat__b_r_valid_load_en = pipeline_enable | bytebeat__b_r_valid_inv;
  assign bytebeat__c_r_valid_load_en = pipeline_enable | bytebeat__c_r_valid_inv;
  assign bytebeat__d_r_valid_load_en = pipeline_enable | bytebeat__d_r_valid_inv;
  assign add_187 = ____state_4 + 16'h0001;
  assign bytebeat__a_r_load_en = bytebeat__a_r_vld & bytebeat__a_r_valid_load_en;
  assign bytebeat__b_r_load_en = bytebeat__b_r_vld & bytebeat__b_r_valid_load_en;
  assign bytebeat__c_r_load_en = bytebeat__c_r_vld & bytebeat__c_r_valid_load_en;
  assign bytebeat__d_r_load_en = bytebeat__d_r_vld & bytebeat__d_r_valid_load_en;
  assign s__1 = umul_170[7:0] & shrl_171[7:0] | umul_172[7:0] & shrl_173[7:0];
  always @ (posedge clk) begin
    if (reset) begin
      ____state_0 <= 4'h5;
      ____state_1 <= 4'h7;
      ____state_2 <= 4'h3;
      ____state_3 <= 4'ha;
      ____state_4 <= 16'h0000;
      __bytebeat__a_r_reg <= 4'h0;
      __bytebeat__a_r_valid_reg <= 1'h0;
      __bytebeat__b_r_reg <= 4'h0;
      __bytebeat__b_r_valid_reg <= 1'h0;
      __bytebeat__c_r_reg <= 4'h0;
      __bytebeat__c_r_valid_reg <= 1'h0;
      __bytebeat__d_r_reg <= 4'h0;
      __bytebeat__d_r_valid_reg <= 1'h0;
      __bytebeat__output_s_reg <= 8'h00;
      __bytebeat__output_s_valid_reg <= 1'h0;
    end else begin
      ____state_0 <= pipeline_enable ? a : ____state_0;
      ____state_1 <= pipeline_enable ? b : ____state_1;
      ____state_2 <= pipeline_enable ? c : ____state_2;
      ____state_3 <= pipeline_enable ? d : ____state_3;
      ____state_4 <= pipeline_enable ? add_187 : ____state_4;
      __bytebeat__a_r_reg <= bytebeat__a_r_load_en ? bytebeat__a_r : __bytebeat__a_r_reg;
      __bytebeat__a_r_valid_reg <= bytebeat__a_r_valid_load_en ? bytebeat__a_r_vld : __bytebeat__a_r_valid_reg;
      __bytebeat__b_r_reg <= bytebeat__b_r_load_en ? bytebeat__b_r : __bytebeat__b_r_reg;
      __bytebeat__b_r_valid_reg <= bytebeat__b_r_valid_load_en ? bytebeat__b_r_vld : __bytebeat__b_r_valid_reg;
      __bytebeat__c_r_reg <= bytebeat__c_r_load_en ? bytebeat__c_r : __bytebeat__c_r_reg;
      __bytebeat__c_r_valid_reg <= bytebeat__c_r_valid_load_en ? bytebeat__c_r_vld : __bytebeat__c_r_valid_reg;
      __bytebeat__d_r_reg <= bytebeat__d_r_load_en ? bytebeat__d_r : __bytebeat__d_r_reg;
      __bytebeat__d_r_valid_reg <= bytebeat__d_r_valid_load_en ? bytebeat__d_r_vld : __bytebeat__d_r_valid_reg;
      __bytebeat__output_s_reg <= bytebeat__output_s_load_en ? s__1 : __bytebeat__output_s_reg;
      __bytebeat__output_s_valid_reg <= bytebeat__output_s_valid_load_en ? __bytebeat__output_s_vld_buf : __bytebeat__output_s_valid_reg;
    end
  end
  assign bytebeat__output_s = __bytebeat__output_s_reg;
  assign bytebeat__output_s_vld = __bytebeat__output_s_valid_reg;
  assign bytebeat__a_r_rdy = bytebeat__a_r_load_en;
  assign bytebeat__b_r_rdy = bytebeat__b_r_load_en;
  assign bytebeat__c_r_rdy = bytebeat__c_r_load_en;
  assign bytebeat__d_r_rdy = bytebeat__d_r_load_en;
endmodule
