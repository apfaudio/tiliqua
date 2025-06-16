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
  reg [10:0] ____state_6;
  reg [12:0] ____state_5;
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
  wire rate_done;
  wire bytebeat__output_s_valid_inv;
  wire __bytebeat__output_s_vld_buf;
  wire bytebeat__output_s_valid_load_en;
  wire bytebeat__output_s_load_en;
  wire [3:0] bytebeat__a_r_select;
  wire [3:0] bytebeat__b_r_select;
  wire [3:0] bytebeat__c_r_select;
  wire [3:0] bytebeat__d_r_select;
  wire [3:0] a;
  wire [3:0] b;
  wire [3:0] c;
  wire [3:0] d;
  wire ne_354;
  wire p0_stage_done;
  wire div_done;
  wire ne_360;
  wire [15:0] umul_324;
  wire [15:0] shrl_325;
  wire [15:0] umul_326;
  wire [15:0] shrl_327;
  wire pipeline_enable;
  wire bytebeat__a_r_valid_inv;
  wire bytebeat__b_r_valid_inv;
  wire bytebeat__c_r_valid_inv;
  wire bytebeat__d_r_valid_inv;
  wire [1:0] concat_402;
  wire [12:0] add_357;
  wire [1:0] concat_409;
  wire [10:0] add_359;
  wire bytebeat__a_r_valid_load_en;
  wire bytebeat__b_r_valid_load_en;
  wire bytebeat__c_r_valid_load_en;
  wire bytebeat__d_r_valid_load_en;
  wire and_416;
  wire and_418;
  wire and_420;
  wire and_422;
  wire [15:0] add_355;
  wire and_424;
  wire [12:0] one_hot_sel_403;
  wire and_427;
  wire [10:0] one_hot_sel_410;
  wire and_430;
  wire bytebeat__a_r_load_en;
  wire bytebeat__b_r_load_en;
  wire bytebeat__c_r_load_en;
  wire bytebeat__d_r_load_en;
  wire [7:0] s__1;
  assign p0_all_active_inputs_valid = 1'h1 & 1'h1 & 1'h1 & 1'h1;
  assign p0_all_active_states_valid = 1'h1;
  assign rate_done = ____state_6 == 11'h4e2;
  assign bytebeat__output_s_valid_inv = ~__bytebeat__output_s_valid_reg;
  assign __bytebeat__output_s_vld_buf = p0_all_active_inputs_valid & p0_all_active_states_valid & 1'h1 & rate_done;
  assign bytebeat__output_s_valid_load_en = bytebeat__output_s_rdy | bytebeat__output_s_valid_inv;
  assign bytebeat__output_s_load_en = __bytebeat__output_s_vld_buf & bytebeat__output_s_valid_load_en;
  assign bytebeat__a_r_select = __bytebeat__a_r_valid_reg ? __bytebeat__a_r_reg : 4'h0;
  assign bytebeat__b_r_select = __bytebeat__b_r_valid_reg ? __bytebeat__b_r_reg : 4'h0;
  assign bytebeat__c_r_select = __bytebeat__c_r_valid_reg ? __bytebeat__c_r_reg : 4'h0;
  assign bytebeat__d_r_select = __bytebeat__d_r_valid_reg ? __bytebeat__d_r_reg : 4'h0;
  assign a = __bytebeat__a_r_valid_reg ? bytebeat__a_r_select : ____state_0;
  assign b = __bytebeat__b_r_valid_reg ? bytebeat__b_r_select : ____state_1;
  assign c = __bytebeat__c_r_valid_reg ? bytebeat__c_r_select : ____state_2;
  assign d = __bytebeat__d_r_valid_reg ? bytebeat__d_r_select : ____state_3;
  assign ne_354 = ____state_5 != 13'h1d4c;
  assign p0_stage_done = p0_all_active_states_valid & p0_all_active_inputs_valid & (~rate_done | bytebeat__output_s_load_en);
  assign div_done = ____state_5 == 13'h1d4c;
  assign ne_360 = ____state_6 != 11'h4e2;
  assign umul_324 = umul16b_16b_x_4b(____state_4, a);
  assign shrl_325 = ____state_4 >> b;
  assign umul_326 = umul16b_16b_x_4b(____state_4, c);
  assign shrl_327 = ____state_4 >> d;
  assign pipeline_enable = p0_stage_done & p0_stage_done;
  assign bytebeat__a_r_valid_inv = ~__bytebeat__a_r_valid_reg;
  assign bytebeat__b_r_valid_inv = ~__bytebeat__b_r_valid_reg;
  assign bytebeat__c_r_valid_inv = ~__bytebeat__c_r_valid_reg;
  assign bytebeat__d_r_valid_inv = ~__bytebeat__d_r_valid_reg;
  assign concat_402 = {ne_354 & p0_stage_done, div_done & p0_stage_done};
  assign add_357 = ____state_5 + 13'h0001;
  assign concat_409 = {ne_360 & p0_stage_done, rate_done & p0_stage_done};
  assign add_359 = ____state_6 + 11'h001;
  assign bytebeat__a_r_valid_load_en = pipeline_enable | bytebeat__a_r_valid_inv;
  assign bytebeat__b_r_valid_load_en = pipeline_enable | bytebeat__b_r_valid_inv;
  assign bytebeat__c_r_valid_load_en = pipeline_enable | bytebeat__c_r_valid_inv;
  assign bytebeat__d_r_valid_load_en = pipeline_enable | bytebeat__d_r_valid_inv;
  assign and_416 = __bytebeat__a_r_valid_reg & pipeline_enable;
  assign and_418 = __bytebeat__b_r_valid_reg & pipeline_enable;
  assign and_420 = __bytebeat__c_r_valid_reg & pipeline_enable;
  assign and_422 = __bytebeat__d_r_valid_reg & pipeline_enable;
  assign add_355 = ____state_4 + 16'h0001;
  assign and_424 = div_done & pipeline_enable;
  assign one_hot_sel_403 = 13'h0000 & {13{concat_402[0]}} | add_357 & {13{concat_402[1]}};
  assign and_427 = (ne_354 | div_done) & pipeline_enable;
  assign one_hot_sel_410 = 11'h000 & {11{concat_409[0]}} | add_359 & {11{concat_409[1]}};
  assign and_430 = (rate_done | ne_360) & pipeline_enable;
  assign bytebeat__a_r_load_en = bytebeat__a_r_vld & bytebeat__a_r_valid_load_en;
  assign bytebeat__b_r_load_en = bytebeat__b_r_vld & bytebeat__b_r_valid_load_en;
  assign bytebeat__c_r_load_en = bytebeat__c_r_vld & bytebeat__c_r_valid_load_en;
  assign bytebeat__d_r_load_en = bytebeat__d_r_vld & bytebeat__d_r_valid_load_en;
  assign s__1 = umul_324[7:0] & shrl_325[7:0] | umul_326[7:0] & shrl_327[7:0];
  always @ (posedge clk) begin
    if (reset) begin
      ____state_0 <= 4'h5;
      ____state_1 <= 4'h7;
      ____state_2 <= 4'h3;
      ____state_3 <= 4'ha;
      ____state_4 <= 16'h0000;
      ____state_6 <= 11'h000;
      ____state_5 <= 13'h0000;
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
      ____state_0 <= and_416 ? bytebeat__a_r_select : ____state_0;
      ____state_1 <= and_418 ? bytebeat__b_r_select : ____state_1;
      ____state_2 <= and_420 ? bytebeat__c_r_select : ____state_2;
      ____state_3 <= and_422 ? bytebeat__d_r_select : ____state_3;
      ____state_4 <= and_424 ? add_355 : ____state_4;
      ____state_6 <= and_430 ? one_hot_sel_410 : ____state_6;
      ____state_5 <= and_427 ? one_hot_sel_403 : ____state_5;
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
