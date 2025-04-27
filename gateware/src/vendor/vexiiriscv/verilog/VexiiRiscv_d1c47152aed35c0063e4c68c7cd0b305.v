// Generator : SpinalHDL dev    git head : 1ff7bd76920e5b4bb30096daedd62c6d2fb67d2f
// Component : VexiiRiscv
// Git hash  : dd2fb21cab62d68408fc402e6a9557f2d61f9a0f

`timescale 1ns/1ps

module VexiiRiscv (
  input  wire [63:0]   PrivilegedPlugin_logic_rdtime,
  input  wire          PrivilegedPlugin_logic_harts_0_int_m_timer /* verilator public */ ,
  input  wire          PrivilegedPlugin_logic_harts_0_int_m_software /* verilator public */ ,
  input  wire          PrivilegedPlugin_logic_harts_0_int_m_external /* verilator public */ ,
  output wire          LsuL1WishbonePlugin_logic_bus_CYC,
  output wire          LsuL1WishbonePlugin_logic_bus_STB,
  input  wire          LsuL1WishbonePlugin_logic_bus_ACK,
  output wire          LsuL1WishbonePlugin_logic_bus_WE,
  output wire [29:0]   LsuL1WishbonePlugin_logic_bus_ADR,
  input  wire [31:0]   LsuL1WishbonePlugin_logic_bus_DAT_MISO,
  output wire [31:0]   LsuL1WishbonePlugin_logic_bus_DAT_MOSI,
  output wire [3:0]    LsuL1WishbonePlugin_logic_bus_SEL,
  input  wire          LsuL1WishbonePlugin_logic_bus_ERR,
  output wire [2:0]    LsuL1WishbonePlugin_logic_bus_CTI,
  output wire [1:0]    LsuL1WishbonePlugin_logic_bus_BTE,
  output reg           FetchL1WishbonePlugin_logic_bus_CYC,
  output reg           FetchL1WishbonePlugin_logic_bus_STB,
  input  wire          FetchL1WishbonePlugin_logic_bus_ACK,
  output wire          FetchL1WishbonePlugin_logic_bus_WE,
  output wire [29:0]   FetchL1WishbonePlugin_logic_bus_ADR,
  input  wire [31:0]   FetchL1WishbonePlugin_logic_bus_DAT_MISO,
  output wire [31:0]   FetchL1WishbonePlugin_logic_bus_DAT_MOSI,
  output wire [3:0]    FetchL1WishbonePlugin_logic_bus_SEL,
  input  wire          FetchL1WishbonePlugin_logic_bus_ERR,
  output wire [2:0]    FetchL1WishbonePlugin_logic_bus_CTI,
  output wire [1:0]    FetchL1WishbonePlugin_logic_bus_BTE,
  output wire          LsuCachelessWishbonePlugin_logic_bridge_down_CYC,
  output wire          LsuCachelessWishbonePlugin_logic_bridge_down_STB,
  input  wire          LsuCachelessWishbonePlugin_logic_bridge_down_ACK,
  output wire          LsuCachelessWishbonePlugin_logic_bridge_down_WE,
  output wire [29:0]   LsuCachelessWishbonePlugin_logic_bridge_down_ADR,
  input  wire [31:0]   LsuCachelessWishbonePlugin_logic_bridge_down_DAT_MISO,
  output wire [31:0]   LsuCachelessWishbonePlugin_logic_bridge_down_DAT_MOSI,
  output wire [3:0]    LsuCachelessWishbonePlugin_logic_bridge_down_SEL,
  input  wire          LsuCachelessWishbonePlugin_logic_bridge_down_ERR,
  output wire [2:0]    LsuCachelessWishbonePlugin_logic_bridge_down_CTI,
  output wire [1:0]    LsuCachelessWishbonePlugin_logic_bridge_down_BTE,
  input  wire          clk,
  input  wire          reset
);
  localparam IntAluPlugin_AluBitwiseCtrlEnum_XOR_1 = 2'd0;
  localparam IntAluPlugin_AluBitwiseCtrlEnum_OR_1 = 2'd1;
  localparam IntAluPlugin_AluBitwiseCtrlEnum_AND_1 = 2'd2;
  localparam IntAluPlugin_AluBitwiseCtrlEnum_ZERO = 2'd3;
  localparam BranchPlugin_BranchCtrlEnum_B = 2'd0;
  localparam BranchPlugin_BranchCtrlEnum_JAL = 2'd1;
  localparam BranchPlugin_BranchCtrlEnum_JALR = 2'd2;
  localparam EnvPluginOp_ECALL = 3'd0;
  localparam EnvPluginOp_EBREAK = 3'd1;
  localparam EnvPluginOp_PRIV_RET = 3'd2;
  localparam EnvPluginOp_FENCE_I = 3'd3;
  localparam EnvPluginOp_SFENCE_VMA = 3'd4;
  localparam EnvPluginOp_WFI = 3'd5;
  localparam LsuL1CmdOpcode_LSU = 3'd0;
  localparam LsuL1CmdOpcode_ACCESS_1 = 3'd1;
  localparam LsuL1CmdOpcode_STORE_BUFFER = 3'd2;
  localparam LsuL1CmdOpcode_FLUSH = 3'd3;
  localparam LsuL1CmdOpcode_PREFETCH = 3'd4;
  localparam LsuPlugin_logic_flusher_IDLE = 2'd0;
  localparam LsuPlugin_logic_flusher_CMD = 2'd1;
  localparam LsuPlugin_logic_flusher_COMPLETION = 2'd2;
  localparam TrapPlugin_logic_harts_0_trap_fsm_RESET = 4'd0;
  localparam TrapPlugin_logic_harts_0_trap_fsm_RUNNING = 4'd1;
  localparam TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1 = 4'd2;
  localparam TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC = 4'd3;
  localparam TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL = 4'd4;
  localparam TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC = 4'd5;
  localparam TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY = 4'd6;
  localparam TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC = 4'd7;
  localparam TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY = 4'd8;
  localparam TrapPlugin_logic_harts_0_trap_fsm_JUMP = 4'd9;
  localparam TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH = 4'd10;
  localparam TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH = 4'd11;
  localparam CsrAccessPlugin_logic_fsm_IDLE = 2'd0;
  localparam CsrAccessPlugin_logic_fsm_READ = 2'd1;
  localparam CsrAccessPlugin_logic_fsm_WRITE = 2'd2;
  localparam CsrAccessPlugin_logic_fsm_COMPLETION = 2'd3;

  wire                early0_DivPlugin_logic_processing_div_io_cmd_valid;
  wire                LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_output_ready;
  reg                 LsuPlugin_logic_flusher_arbiter_io_output_ready;
  wire                LsuPlugin_logic_onAddress0_arbiter_io_output_ready;
  reg                 integer_RegFilePlugin_logic_regfile_fpga_io_writes_0_valid;
  reg        [4:0]    integer_RegFilePlugin_logic_regfile_fpga_io_writes_0_address;
  reg        [31:0]   integer_RegFilePlugin_logic_regfile_fpga_io_writes_0_data;
  reg        [31:0]   LsuL1Plugin_logic_banks_0_mem_spinal_port1;
  reg        [23:0]   LsuL1Plugin_logic_ways_0_mem_spinal_port1;
  reg        [0:0]    LsuL1Plugin_logic_shared_mem_spinal_port1;
  reg        [31:0]   LsuL1Plugin_logic_writeback_victimBuffer_spinal_port1;
  reg        [49:0]   BtbPlugin_logic_mem_spinal_port1;
  reg        [31:0]   FetchL1Plugin_logic_banks_0_mem_spinal_port1;
  reg        [23:0]   FetchL1Plugin_logic_ways_0_mem_spinal_port1;
  reg        [31:0]   CsrRamPlugin_logic_mem_spinal_port1;
  wire                early0_DivPlugin_logic_processing_div_io_cmd_ready;
  wire                early0_DivPlugin_logic_processing_div_io_rsp_valid;
  wire       [31:0]   early0_DivPlugin_logic_processing_div_io_rsp_payload_result;
  wire       [31:0]   early0_DivPlugin_logic_processing_div_io_rsp_payload_remain;
  wire                LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_inputs_0_ready;
  wire                LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_inputs_1_ready;
  wire                LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_output_valid;
  wire                LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_output_payload_last;
  wire                LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_output_payload_fragment_write;
  wire       [31:0]   LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_output_payload_fragment_address;
  wire       [0:0]    LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_chosen;
  wire       [1:0]    LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_chosenOH;
  wire                LsuPlugin_logic_flusher_arbiter_io_inputs_0_ready;
  wire                LsuPlugin_logic_flusher_arbiter_io_output_valid;
  wire       [0:0]    LsuPlugin_logic_flusher_arbiter_io_chosenOH;
  wire                LsuPlugin_logic_onAddress0_arbiter_io_inputs_0_ready;
  wire                LsuPlugin_logic_onAddress0_arbiter_io_inputs_1_ready;
  wire                LsuPlugin_logic_onAddress0_arbiter_io_output_valid;
  wire       [2:0]    LsuPlugin_logic_onAddress0_arbiter_io_output_payload_op;
  wire       [31:0]   LsuPlugin_logic_onAddress0_arbiter_io_output_payload_address;
  wire       [1:0]    LsuPlugin_logic_onAddress0_arbiter_io_output_payload_size;
  wire                LsuPlugin_logic_onAddress0_arbiter_io_output_payload_load;
  wire                LsuPlugin_logic_onAddress0_arbiter_io_output_payload_store;
  wire                LsuPlugin_logic_onAddress0_arbiter_io_output_payload_atomic;
  wire                LsuPlugin_logic_onAddress0_arbiter_io_output_payload_clean;
  wire                LsuPlugin_logic_onAddress0_arbiter_io_output_payload_invalidate;
  wire       [11:0]   LsuPlugin_logic_onAddress0_arbiter_io_output_payload_storeId;
  wire       [0:0]    LsuPlugin_logic_onAddress0_arbiter_io_chosen;
  wire       [1:0]    LsuPlugin_logic_onAddress0_arbiter_io_chosenOH;
  wire                streamArbiter_4_io_inputs_0_ready;
  wire                streamArbiter_4_io_output_valid;
  wire       [31:0]   streamArbiter_4_io_output_payload_pcOnLastSlice;
  wire       [31:0]   streamArbiter_4_io_output_payload_pcTarget;
  wire                streamArbiter_4_io_output_payload_taken;
  wire                streamArbiter_4_io_output_payload_isBranch;
  wire                streamArbiter_4_io_output_payload_isPush;
  wire                streamArbiter_4_io_output_payload_isPop;
  wire                streamArbiter_4_io_output_payload_wasWrong;
  wire                streamArbiter_4_io_output_payload_badPredictedTarget;
  wire       [15:0]   streamArbiter_4_io_output_payload_uopId;
  wire       [0:0]    streamArbiter_4_io_chosenOH;
  wire       [31:0]   integer_RegFilePlugin_logic_regfile_fpga_io_reads_0_data;
  wire       [31:0]   integer_RegFilePlugin_logic_regfile_fpga_io_reads_1_data;
  wire       [31:0]   _zz_early0_IntAluPlugin_logic_alu_result;
  wire       [31:0]   _zz_early0_IntAluPlugin_logic_alu_result_1;
  wire       [31:0]   _zz_early0_IntAluPlugin_logic_alu_result_2;
  wire       [31:0]   _zz_early0_IntAluPlugin_logic_alu_result_3;
  wire       [31:0]   _zz_early0_IntAluPlugin_logic_alu_result_4;
  wire       [0:0]    _zz_early0_IntAluPlugin_logic_alu_result_5;
  wire       [4:0]    _zz_early0_BarrelShifterPlugin_logic_shift_amplitude;
  wire       [31:0]   _zz_early0_BarrelShifterPlugin_logic_shift_reversed;
  wire                _zz_early0_BarrelShifterPlugin_logic_shift_reversed_1;
  wire       [0:0]    _zz_early0_BarrelShifterPlugin_logic_shift_reversed_2;
  wire       [20:0]   _zz_early0_BarrelShifterPlugin_logic_shift_reversed_3;
  wire                _zz_early0_BarrelShifterPlugin_logic_shift_reversed_4;
  wire       [0:0]    _zz_early0_BarrelShifterPlugin_logic_shift_reversed_5;
  wire       [9:0]    _zz_early0_BarrelShifterPlugin_logic_shift_reversed_6;
  wire       [32:0]   _zz_early0_BarrelShifterPlugin_logic_shift_shifted;
  wire       [32:0]   _zz_early0_BarrelShifterPlugin_logic_shift_shifted_1;
  wire       [31:0]   _zz_early0_BarrelShifterPlugin_logic_shift_patched;
  wire                _zz_early0_BarrelShifterPlugin_logic_shift_patched_1;
  wire       [0:0]    _zz_early0_BarrelShifterPlugin_logic_shift_patched_2;
  wire       [20:0]   _zz_early0_BarrelShifterPlugin_logic_shift_patched_3;
  wire                _zz_early0_BarrelShifterPlugin_logic_shift_patched_4;
  wire       [0:0]    _zz_early0_BarrelShifterPlugin_logic_shift_patched_5;
  wire       [9:0]    _zz_early0_BarrelShifterPlugin_logic_shift_patched_6;
  wire       [23:0]   _zz_LsuL1Plugin_logic_ways_0_mem_port;
  wire                _zz_LsuL1Plugin_logic_ways_0_mem_port_1;
  wire       [3:0]    _zz_LsuL1Plugin_logic_writeback_read_wordIndex;
  wire       [0:0]    _zz_LsuL1Plugin_logic_writeback_read_wordIndex_1;
  wire       [3:0]    _zz_LsuL1Plugin_logic_writeback_victimBuffer_port;
  wire       [3:0]    _zz_LsuL1Plugin_logic_writeback_write_wordIndex;
  wire       [0:0]    _zz_LsuL1Plugin_logic_writeback_write_wordIndex_1;
  wire       [0:0]    _zz_LsuL1Plugin_logic_lsu_ctrl_refillWayNeedWriteback;
  wire       [0:0]    _zz_LsuL1Plugin_logic_lsu_ctrl_doWrite;
  reg        [0:0]    _zz_22;
  wire       [0:0]    _zz_23;
  reg        [1:0]    _zz_24;
  wire       [2:0]    _zz_25;
  wire       [0:0]    _zz_when;
  wire       [0:0]    _zz_LsuL1Plugin_logic_shared_write_payload_data_dirty;
  wire       [32:0]   _zz_execute_ctrl2_down_MUL_SRC1_lane0;
  wire       [32:0]   _zz_execute_ctrl2_down_MUL_SRC2_lane0;
  wire       [46:0]   _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_1_lane0;
  wire       [33:0]   _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_1_lane0_1;
  wire       [17:0]   _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_1_lane0_2;
  wire       [15:0]   _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_1_lane0_3;
  wire       [46:0]   _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_2_lane0;
  wire       [33:0]   _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_2_lane0_1;
  wire       [15:0]   _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_2_lane0_2;
  wire       [17:0]   _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_2_lane0_3;
  wire       [29:0]   _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_3_lane0;
  wire       [31:0]   _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_3_lane0_1;
  wire       [15:0]   _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_3_lane0_2;
  wire       [15:0]   _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_3_lane0_3;
  wire       [62:0]   _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0_3;
  wire       [62:0]   _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0_4;
  wire       [62:0]   _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0_5;
  wire       [62:0]   _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0_6;
  wire       [4:0]    _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0_3;
  wire       [4:0]    _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0_4;
  wire       [4:0]    _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0_5;
  wire       [4:0]    _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0_6;
  wire       [31:0]   _zz_execute_ctrl2_down_RsUnsignedPlugin_RS1_UNSIGNED_lane0;
  wire       [0:0]    _zz_execute_ctrl2_down_RsUnsignedPlugin_RS1_UNSIGNED_lane0_1;
  wire       [31:0]   _zz_execute_ctrl2_down_RsUnsignedPlugin_RS2_UNSIGNED_lane0;
  wire       [0:0]    _zz_execute_ctrl2_down_RsUnsignedPlugin_RS2_UNSIGNED_lane0_1;
  wire       [31:0]   _zz_execute_ctrl2_down_DivPlugin_DIV_RESULT_lane0_1;
  wire       [31:0]   _zz_execute_ctrl2_down_DivPlugin_DIV_RESULT_lane0_2;
  wire       [0:0]    _zz_execute_ctrl2_down_DivPlugin_DIV_RESULT_lane0_3;
  wire       [31:0]   _zz_late0_IntAluPlugin_logic_alu_result;
  wire       [31:0]   _zz_late0_IntAluPlugin_logic_alu_result_1;
  wire       [31:0]   _zz_late0_IntAluPlugin_logic_alu_result_2;
  wire       [31:0]   _zz_late0_IntAluPlugin_logic_alu_result_3;
  wire       [31:0]   _zz_late0_IntAluPlugin_logic_alu_result_4;
  wire       [0:0]    _zz_late0_IntAluPlugin_logic_alu_result_5;
  wire       [4:0]    _zz_late0_BarrelShifterPlugin_logic_shift_amplitude;
  wire       [31:0]   _zz_late0_BarrelShifterPlugin_logic_shift_reversed;
  wire                _zz_late0_BarrelShifterPlugin_logic_shift_reversed_1;
  wire       [0:0]    _zz_late0_BarrelShifterPlugin_logic_shift_reversed_2;
  wire       [20:0]   _zz_late0_BarrelShifterPlugin_logic_shift_reversed_3;
  wire                _zz_late0_BarrelShifterPlugin_logic_shift_reversed_4;
  wire       [0:0]    _zz_late0_BarrelShifterPlugin_logic_shift_reversed_5;
  wire       [9:0]    _zz_late0_BarrelShifterPlugin_logic_shift_reversed_6;
  wire       [32:0]   _zz_late0_BarrelShifterPlugin_logic_shift_shifted;
  wire       [32:0]   _zz_late0_BarrelShifterPlugin_logic_shift_shifted_1;
  wire       [31:0]   _zz_late0_BarrelShifterPlugin_logic_shift_patched;
  wire                _zz_late0_BarrelShifterPlugin_logic_shift_patched_1;
  wire       [0:0]    _zz_late0_BarrelShifterPlugin_logic_shift_patched_2;
  wire       [20:0]   _zz_late0_BarrelShifterPlugin_logic_shift_patched_3;
  wire                _zz_late0_BarrelShifterPlugin_logic_shift_patched_4;
  wire       [0:0]    _zz_late0_BarrelShifterPlugin_logic_shift_patched_5;
  wire       [9:0]    _zz_late0_BarrelShifterPlugin_logic_shift_patched_6;
  wire       [49:0]   _zz_BtbPlugin_logic_mem_port;
  wire       [23:0]   _zz_FetchL1Plugin_logic_ways_0_mem_port;
  wire                _zz_FetchL1Plugin_logic_ways_0_mem_port_1;
  wire                _zz_when_1;
  wire       [0:0]    _zz_FetchL1Plugin_logic_ctrl_dataAccessFault;
  wire       [63:0]   _zz_WhiteboxerPlugin_logic_decodes_0_pc;
  wire       [0:0]    _zz_FetchL1Plugin_pmaBuilder_onTransfers_0_addressHit;
  wire       [0:0]    _zz_FetchL1Plugin_logic_ctrl_pmaPort_rsp_io_1;
  wire       [25:0]   _zz_FetchL1WishbonePlugin_logic_bus_ADR;
  wire       [11:0]   _zz__zz_execute_ctrl1_down_early0_SrcPlugin_SRC2_lane0;
  wire       [11:0]   _zz__zz_execute_ctrl1_down_early0_SrcPlugin_SRC2_lane0_1;
  wire       [31:0]   _zz_execute_ctrl2_down_early0_SrcPlugin_ADD_SUB_lane0;
  wire       [31:0]   _zz_execute_ctrl2_down_early0_SrcPlugin_ADD_SUB_lane0_1;
  wire       [31:0]   _zz_execute_ctrl2_down_early0_SrcPlugin_ADD_SUB_lane0_2;
  wire       [0:0]    _zz_execute_ctrl2_down_early0_SrcPlugin_ADD_SUB_lane0_3;
  wire       [11:0]   _zz__zz_execute_ctrl3_down_late0_SrcPlugin_SRC2_lane0;
  wire       [31:0]   _zz_execute_ctrl4_down_late0_SrcPlugin_ADD_SUB_lane0;
  wire       [31:0]   _zz_execute_ctrl4_down_late0_SrcPlugin_ADD_SUB_lane0_1;
  wire       [31:0]   _zz_execute_ctrl4_down_late0_SrcPlugin_ADD_SUB_lane0_2;
  wire       [0:0]    _zz_execute_ctrl4_down_late0_SrcPlugin_ADD_SUB_lane0_3;
  wire       [3:0]    _zz_early0_EnvPlugin_logic_trapPort_payload_code;
  wire       [20:0]   _zz_early0_BranchPlugin_pcCalc_target_b;
  wire       [11:0]   _zz_early0_BranchPlugin_pcCalc_target_b_1;
  wire       [12:0]   _zz_early0_BranchPlugin_pcCalc_target_b_2;
  wire       [1:0]    _zz_early0_BranchPlugin_pcCalc_slices;
  wire       [0:0]    _zz_early0_BranchPlugin_pcCalc_slices_1;
  wire       [31:0]   _zz_execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_TRUE_lane0;
  wire       [31:0]   _zz_execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_FALSE_lane0;
  wire       [3:0]    _zz_execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_FALSE_lane0_1;
  wire       [31:0]   _zz_execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_LAST_SLICE_lane0;
  wire       [1:0]    _zz_execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_LAST_SLICE_lane0_1;
  wire       [11:0]   _zz_LsuPlugin_logic_onAddress0_ls_storeId;
  wire       [0:0]    _zz_LsuPlugin_logic_onAddress0_ls_storeId_1;
  wire       [10:0]   _zz_LsuPlugin_logic_onAddress0_flush_port_payload_address;
  reg        [7:0]    _zz_LsuPlugin_logic_onCtrl_loadData_shited;
  wire       [1:0]    _zz_LsuPlugin_logic_onCtrl_loadData_shited_1;
  reg        [7:0]    _zz_LsuPlugin_logic_onCtrl_loadData_shited_2;
  wire       [0:0]    _zz_LsuPlugin_logic_onCtrl_loadData_shited_3;
  wire       [2:0]    _zz_LsuPlugin_logic_trapPort_payload_code;
  wire       [3:0]    _zz_LsuPlugin_logic_flusher_cmdCounter;
  wire       [0:0]    _zz_LsuPlugin_pmaBuilder_l1_onTransfers_0_addressHit;
  wire       [0:0]    _zz_LsuPlugin_logic_onPma_cached_rsp_io_1;
  wire       [0:0]    _zz_LsuPlugin_pmaBuilder_io_onTransfers_0_addressHit;
  wire       [31:0]   _zz_LsuPlugin_logic_onPma_io_rsp_fault;
  wire       [31:0]   _zz_LsuPlugin_logic_onPma_io_rsp_fault_1;
  wire       [0:0]    _zz_LsuPlugin_logic_onPma_io_rsp_io;
  wire       [0:0]    _zz_decode_ctrls_1_down_RS1_ENABLE_0;
  wire       [0:0]    _zz_decode_ctrls_1_down_RS2_ENABLE_0;
  wire       [0:0]    _zz_decode_ctrls_1_down_RD_ENABLE_0;
  wire       [31:0]   _zz_decode_ctrls_1_down_RD_ENABLE_0_1;
  wire       [31:0]   _zz_decode_ctrls_1_down_RD_ENABLE_0_2;
  wire       [31:0]   _zz_decode_ctrls_1_down_RD_ENABLE_0_3;
  wire       [31:0]   _zz_decode_ctrls_1_down_RD_ENABLE_0_4;
  wire       [31:0]   _zz_decode_ctrls_1_down_RD_ENABLE_0_5;
  wire       [31:0]   _zz_decode_ctrls_1_down_Decode_LEGAL_0;
  wire       [31:0]   _zz_decode_ctrls_1_down_Decode_LEGAL_0_1;
  wire       [31:0]   _zz_decode_ctrls_1_down_Decode_LEGAL_0_2;
  wire                _zz_decode_ctrls_1_down_Decode_LEGAL_0_3;
  wire       [0:0]    _zz_decode_ctrls_1_down_Decode_LEGAL_0_4;
  wire       [13:0]   _zz_decode_ctrls_1_down_Decode_LEGAL_0_5;
  wire       [31:0]   _zz_decode_ctrls_1_down_Decode_LEGAL_0_6;
  wire       [31:0]   _zz_decode_ctrls_1_down_Decode_LEGAL_0_7;
  wire       [31:0]   _zz_decode_ctrls_1_down_Decode_LEGAL_0_8;
  wire                _zz_decode_ctrls_1_down_Decode_LEGAL_0_9;
  wire       [0:0]    _zz_decode_ctrls_1_down_Decode_LEGAL_0_10;
  wire       [7:0]    _zz_decode_ctrls_1_down_Decode_LEGAL_0_11;
  wire       [31:0]   _zz_decode_ctrls_1_down_Decode_LEGAL_0_12;
  wire       [31:0]   _zz_decode_ctrls_1_down_Decode_LEGAL_0_13;
  wire       [31:0]   _zz_decode_ctrls_1_down_Decode_LEGAL_0_14;
  wire                _zz_decode_ctrls_1_down_Decode_LEGAL_0_15;
  wire       [0:0]    _zz_decode_ctrls_1_down_Decode_LEGAL_0_16;
  wire       [1:0]    _zz_decode_ctrls_1_down_Decode_LEGAL_0_17;
  wire       [0:0]    _zz_DecoderPlugin_logic_laneLogic_0_fixer_isJb;
  wire       [31:0]   _zz_DecoderPlugin_logic_forgetPort_payload_pcOnLastSlice;
  wire       [1:0]    _zz_DecoderPlugin_logic_forgetPort_payload_pcOnLastSlice_1;
  wire       [29:0]   _zz_BtbPlugin_logic_memWrite_payload_address;
  wire       [0:0]    _zz_decode_ctrls_1_down_DecoderPlugin_logic_NEED_FPU_0;
  wire       [0:0]    _zz_decode_ctrls_1_down_DecoderPlugin_logic_NEED_FPU_0_1;
  wire       [0:0]    _zz_decode_ctrls_1_down_DecoderPlugin_logic_NEED_RM_0;
  wire       [0:0]    _zz_decode_ctrls_1_down_DecoderPlugin_logic_NEED_RM_0_1;
  wire       [0:0]    _zz_decode_ctrls_1_down_DispatchPlugin_logic_LANES_LAYER_HIT_0_0;
  wire       [0:0]    _zz_decode_ctrls_1_down_DispatchPlugin_logic_LANES_LAYER_HIT_0_0_1;
  wire       [0:0]    _zz_decode_ctrls_1_down_DispatchPlugin_logic_LANES_LAYER_HIT_1_0_1;
  wire       [0:0]    _zz_decode_ctrls_1_down_DispatchPlugin_logic_LANES_LAYER_HIT_1_0_2;
  wire       [0:0]    _zz_decode_ctrls_1_down_DispatchPlugin_MAY_FLUSH_0_1;
  wire       [0:0]    _zz_decode_ctrls_1_down_DispatchPlugin_MAY_FLUSH_0_2;
  wire       [0:0]    _zz_decode_ctrls_1_down_DispatchPlugin_DONT_FLUSH_0;
  wire       [0:0]    _zz_decode_ctrls_1_down_DispatchPlugin_DONT_FLUSH_0_1;
  wire       [0:0]    _zz_decode_ctrls_1_down_DispatchPlugin_DONT_FLUSH_FROM_LANES_0;
  wire       [0:0]    _zz_decode_ctrls_1_down_DispatchPlugin_DONT_FLUSH_FROM_LANES_0_1;
  wire       [0:0]    _zz_decode_ctrls_1_down_DispatchPlugin_FENCE_OLDER_0;
  wire       [0:0]    _zz_decode_ctrls_1_down_DispatchPlugin_FENCE_OLDER_0_1;
  wire       [0:0]    _zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_3_0;
  wire       [0:0]    _zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_3_0_1;
  wire       [0:0]    _zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_4_0_2;
  wire       [0:0]    _zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_4_0_3;
  wire       [0:0]    _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_0_ENABLES_0_0;
  wire       [0:0]    _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_0_ENABLES_0_0_1;
  wire       [0:0]    _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_0_0_1;
  wire       [0:0]    _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_0_0_2;
  wire       [0:0]    _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_1_0;
  wire       [0:0]    _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_1_0_1;
  wire       [0:0]    _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_0_ENABLES_0_0;
  wire       [0:0]    _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_0_ENABLES_0_0_1;
  wire       [0:0]    _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_1_ENABLES_0_0_1;
  wire       [0:0]    _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_1_ENABLES_0_0_2;
  wire       [29:0]   _zz_BtbPlugin_logic_memWrite_payload_address_1;
  wire       [29:0]   _zz_BtbPlugin_logic_memRead_cmd_payload;
  wire                _zz_decode_logic_flushes_1_onLanes_0_doIt;
  wire                _zz_decode_logic_flushes_1_onLanes_0_doIt_1;
  wire                _zz_decode_logic_flushes_1_onLanes_0_doIt_2;
  wire                _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception;
  wire                _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_1;
  wire                _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_2;
  wire                _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_3;
  wire                _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_4;
  wire                _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_5;
  wire       [0:0]    _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_1_1;
  wire       [0:0]    _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_1_2;
  wire       [32:0]   _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_exception;
  wire       [32:0]   _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_exception_1;
  wire       [32:0]   _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_exception_2;
  wire       [32:0]   _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_exception_3;
  wire       [31:0]   _zz_TrapPlugin_logic_harts_0_trap_fsm_jumpTarget;
  wire       [2:0]    _zz_TrapPlugin_logic_harts_0_trap_fsm_jumpTarget_1;
  wire       [31:0]   _zz_PcPlugin_logic_harts_0_self_pc;
  wire       [2:0]    _zz_PcPlugin_logic_harts_0_self_pc_1;
  wire       [0:0]    _zz_PcPlugin_logic_harts_0_aggregator_fault;
  wire       [0:0]    _zz_CsrAccessPlugin_logic_fsm_inject_implemented;
  wire       [4:0]    _zz_CsrAccessPlugin_logic_fsm_inject_implemented_1;
  wire       [31:0]   _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_5;
  wire       [5:0]    _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_6;
  wire       [31:0]   _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_7;
  wire       [31:0]   _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_8;
  wire       [7:0]    _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_9;
  wire       [31:0]   _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_10;
  wire       [3:0]    _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_11;
  wire       [31:0]   _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_12;
  wire       [12:0]   _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_13;
  wire       [31:0]   _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_14;
  wire       [31:0]   _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_15;
  wire       [17:0]   _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_16;
  wire       [31:0]   _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_17;
  wire       [31:0]   _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_18;
  wire       [3:0]    _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_19;
  wire       [31:0]   _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_20;
  wire       [11:0]   _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_21;
  wire       [31:0]   _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_22;
  wire       [7:0]    _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_23;
  wire       [31:0]   _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_24;
  wire       [3:0]    _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_25;
  wire       [31:0]   _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_26;
  wire       [11:0]   _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_27;
  wire       [31:0]   _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_28;
  wire       [7:0]    _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_29;
  wire       [31:0]   _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_30;
  wire       [3:0]    _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_31;
  wire       [31:0]   _zz_CsrAccessPlugin_logic_fsm_writeLogic_alu_mask;
  wire       [4:0]    _zz_CsrAccessPlugin_logic_fsm_writeLogic_alu_mask_1;
  wire                _zz_fetch_logic_flushes_0_doIt;
  wire                _zz_fetch_logic_flushes_0_doIt_1;
  wire                _zz_fetch_logic_flushes_1_doIt;
  wire                _zz_fetch_logic_flushes_1_doIt_1;
  wire                _zz_fetch_logic_flushes_1_doIt_2;
  wire       [2:0]    _zz_CsrRamPlugin_logic_writeLogic_hits_ohFirst_masked;
  wire       [1:0]    _zz_CsrRamPlugin_logic_readLogic_hits_ohFirst_masked;
  reg        [1:0]    _zz_CsrRamPlugin_logic_readLogic_port_cmd_payload;
  wire       [2:0]    _zz_CsrRamPlugin_logic_flush_counter;
  wire       [0:0]    _zz_CsrRamPlugin_logic_flush_counter_1;
  wire       [0:0]    _zz_execute_ctrl1_down_early0_IntAluPlugin_SEL_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_early0_IntAluPlugin_SEL_lane0_1;
  wire       [32:0]   _zz_execute_ctrl1_down_early0_IntAluPlugin_SEL_lane0_2;
  wire       [32:0]   _zz_execute_ctrl1_down_early0_IntAluPlugin_SEL_lane0_3;
  wire       [0:0]    _zz_execute_ctrl1_down_early0_BarrelShifterPlugin_SEL_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_early0_BarrelShifterPlugin_SEL_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_early0_BranchPlugin_SEL_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_early0_BranchPlugin_SEL_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_early0_MulPlugin_SEL_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_early0_MulPlugin_SEL_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_early0_DivPlugin_SEL_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_early0_DivPlugin_SEL_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_early0_EnvPlugin_SEL_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_early0_EnvPlugin_SEL_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_late0_IntAluPlugin_SEL_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_late0_IntAluPlugin_SEL_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_late0_BarrelShifterPlugin_SEL_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_late0_BarrelShifterPlugin_SEL_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_late0_BranchPlugin_SEL_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_late0_BranchPlugin_SEL_lane0_2;
  wire       [0:0]    _zz_execute_ctrl1_down_CsrAccessPlugin_SEL_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_CsrAccessPlugin_SEL_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_AguPlugin_SEL_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_AguPlugin_SEL_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_LsuPlugin_logic_FENCE_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_LsuPlugin_logic_FENCE_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_lane0_integer_WriteBackPlugin_SEL_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_lane0_integer_WriteBackPlugin_SEL_lane0_2;
  wire       [0:0]    _zz_execute_ctrl1_down_COMPLETION_AT_2_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_COMPLETION_AT_2_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_COMPLETION_AT_4_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_COMPLETION_AT_4_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_COMPLETION_AT_3_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_COMPLETION_AT_3_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0_5;
  wire       [0:0]    _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0_6;
  wire       [0:0]    _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0_4;
  wire       [0:0]    _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0_5;
  wire       [0:0]    _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0_3;
  wire       [0:0]    _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0_4;
  wire       [0:0]    _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_ADD_SUB_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_ADD_SUB_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_SLTX_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_SLTX_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_SrcStageables_REVERT_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_SrcStageables_REVERT_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_SrcStageables_ZERO_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_SrcStageables_ZERO_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_lane0_IntFormatPlugin_logic_SIGNED_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_lane0_IntFormatPlugin_logic_SIGNED_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_BYPASSED_AT_2_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_BYPASSED_AT_2_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_BYPASSED_AT_3_lane0_2;
  wire       [0:0]    _zz_execute_ctrl1_down_BYPASSED_AT_3_lane0_3;
  wire       [0:0]    _zz_execute_ctrl1_down_MAY_FLUSH_PRECISE_3_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_MAY_FLUSH_PRECISE_3_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_MAY_FLUSH_PRECISE_4_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_MAY_FLUSH_PRECISE_4_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_SrcStageables_UNSIGNED_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_SrcStageables_UNSIGNED_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_BarrelShifterPlugin_LEFT_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_BarrelShifterPlugin_LEFT_lane0_2;
  wire       [0:0]    _zz_execute_ctrl1_down_BarrelShifterPlugin_SIGNED_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_BarrelShifterPlugin_SIGNED_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_MulPlugin_HIGH_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_MulPlugin_HIGH_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_RsUnsignedPlugin_RS1_SIGNED_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_RsUnsignedPlugin_RS1_SIGNED_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_RsUnsignedPlugin_RS2_SIGNED_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_RsUnsignedPlugin_RS2_SIGNED_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_DivPlugin_REM_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_DivPlugin_REM_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_CsrAccessPlugin_CSR_IMM_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_CsrAccessPlugin_CSR_IMM_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_CsrAccessPlugin_CSR_MASK_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_CsrAccessPlugin_CSR_MASK_lane0_2;
  wire       [0:0]    _zz_execute_ctrl1_down_CsrAccessPlugin_CSR_CLEAR_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_CsrAccessPlugin_CSR_CLEAR_lane0_2;
  wire       [0:0]    _zz_execute_ctrl1_down_AguPlugin_LOAD_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_AguPlugin_LOAD_lane0_2;
  wire       [0:0]    _zz_execute_ctrl1_down_AguPlugin_STORE_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_AguPlugin_STORE_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_AguPlugin_ATOMIC_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_AguPlugin_ATOMIC_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_AguPlugin_FLOAT_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_AguPlugin_FLOAT_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_AguPlugin_CLEAN_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_AguPlugin_CLEAN_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_AguPlugin_INVALIDATE_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_AguPlugin_INVALIDATE_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_LsuPlugin_logic_LSU_PREFETCH_lane0;
  wire       [0:0]    _zz_execute_ctrl1_down_LsuPlugin_logic_LSU_PREFETCH_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_ADD_SUB_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_ADD_SUB_lane0_2;
  wire       [0:0]    _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_SLTX_lane0_1;
  wire       [0:0]    _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_SLTX_lane0_2;
  wire                _zz_when_ExecuteLanePlugin_l306_2;
  wire                _zz_when_ExecuteLanePlugin_l306_2_1;
  wire                _zz_when_ExecuteLanePlugin_l306_2_2;
  wire                _zz_when_ExecuteLanePlugin_l306_2_3;
  wire                _zz_when_ExecuteLanePlugin_l306_2_4;
  wire                _zz_when_ExecuteLanePlugin_l306_2_5;
  wire                _zz_when_ExecuteLanePlugin_l306_2_6;
  wire       [31:0]   _zz_WhiteboxerPlugin_logic_csr_access_payload_address;
  reg        [0:0]    _zz_WhiteboxerPlugin_logic_perf_candidatesCount;
  wire       [0:0]    _zz_WhiteboxerPlugin_logic_perf_candidatesCount_1;
  reg        [0:0]    _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCount;
  wire       [0:0]    _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCount_1;
  wire       [59:0]   _zz__zz_WhiteboxerPlugin_logic_perf_executeFreezedCounter_1;
  wire       [0:0]    _zz__zz_WhiteboxerPlugin_logic_perf_executeFreezedCounter_1_1;
  wire       [59:0]   _zz__zz_WhiteboxerPlugin_logic_perf_dispatchHazardsCounter_1;
  wire       [0:0]    _zz__zz_WhiteboxerPlugin_logic_perf_dispatchHazardsCounter_1_1;
  wire       [59:0]   _zz__zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_0_1;
  wire       [0:0]    _zz__zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_0_1_1;
  wire       [59:0]   _zz__zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_1_1;
  wire       [0:0]    _zz__zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_1_1_1;
  wire       [59:0]   _zz__zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_0_1;
  wire       [0:0]    _zz__zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_0_1_1;
  wire       [59:0]   _zz__zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_1_1;
  wire       [0:0]    _zz__zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_1_1_1;
  wire                fetch_logic_ctrls_0_up_isReady;
  wire                fetch_logic_ctrls_0_up_isValid;
  reg        [31:0]   execute_ctrl5_up_lane0_integer_WriteBackPlugin_logic_DATA_lane0;
  reg                 execute_ctrl5_up_COMMIT_lane0;
  reg        [4:0]    execute_ctrl5_up_RD_PHYS_lane0;
  wire       [11:0]   execute_ctrl3_down_Decode_STORE_ID_lane0;
  wire                execute_ctrl3_down_LsuL1_PREFETCH_lane0;
  wire                execute_ctrl3_down_LsuL1_INVALID_lane0;
  wire                execute_ctrl3_down_LsuL1_CLEAN_lane0;
  wire       [31:0]   execute_ctrl3_down_early0_BranchPlugin_pcCalc_PC_LAST_SLICE_lane0;
  wire       [31:0]   execute_ctrl3_down_early0_BranchPlugin_pcCalc_PC_FALSE_lane0;
  wire       [31:0]   execute_ctrl3_down_early0_BranchPlugin_pcCalc_PC_TRUE_lane0;
  wire       [1:0]    execute_ctrl3_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0;
  wire                execute_ctrl3_down_late0_IntAluPlugin_ALU_SLTX_lane0;
  wire                execute_ctrl3_down_late0_IntAluPlugin_ALU_ADD_SUB_lane0;
  wire                execute_ctrl3_down_LsuPlugin_logic_LSU_PREFETCH_lane0;
  wire                execute_ctrl3_down_AguPlugin_FLOAT_lane0;
  wire                execute_ctrl3_down_AguPlugin_ATOMIC_lane0;
  wire                execute_ctrl3_down_AguPlugin_LOAD_lane0;
  wire                execute_ctrl3_down_MulPlugin_HIGH_lane0;
  wire       [1:0]    execute_ctrl3_down_BranchPlugin_BRANCH_CTRL_lane0;
  wire                execute_ctrl3_down_BarrelShifterPlugin_SIGNED_lane0;
  wire                execute_ctrl3_down_BarrelShifterPlugin_LEFT_lane0;
  wire                execute_ctrl3_down_SrcStageables_UNSIGNED_lane0;
  wire       [1:0]    execute_ctrl3_down_lane0_IntFormatPlugin_logic_WIDTH_ID_lane0;
  wire                execute_ctrl3_down_lane0_IntFormatPlugin_logic_SIGNED_lane0;
  wire                execute_ctrl3_down_SrcStageables_ZERO_lane0;
  wire                execute_ctrl3_down_SrcStageables_REVERT_lane0;
  wire                execute_ctrl3_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0;
  wire                execute_ctrl3_down_COMPLETION_AT_4_lane0;
  wire                execute_ctrl3_down_lane0_integer_WriteBackPlugin_SEL_lane0;
  wire                execute_ctrl3_down_late0_BranchPlugin_SEL_lane0;
  wire                execute_ctrl3_down_late0_BarrelShifterPlugin_SEL_lane0;
  wire                execute_ctrl3_down_late0_IntAluPlugin_SEL_lane0;
  wire                execute_ctrl3_down_early0_MulPlugin_SEL_lane0;
  wire                execute_ctrl3_down_early0_BranchPlugin_SEL_lane0;
  wire       [1:0]    execute_ctrl3_down_AguPlugin_SIZE_lane0;
  wire       [31:0]   execute_ctrl3_down_Prediction_ALIGNED_JUMPED_PC_lane0;
  wire                execute_ctrl3_down_Prediction_ALIGNED_JUMPED_lane0;
  reg                 execute_ctrl4_up_MMU_BYPASS_TRANSLATION_lane0;
  reg                 execute_ctrl4_up_MMU_HAZARD_lane0;
  reg                 execute_ctrl4_up_MMU_REFILL_lane0;
  reg                 execute_ctrl4_up_MMU_ACCESS_FAULT_lane0;
  reg                 execute_ctrl4_up_LsuPlugin_logic_MMU_FAILURE_lane0;
  reg                 execute_ctrl4_up_LsuPlugin_logic_MMU_PAGE_FAULT_lane0;
  reg                 execute_ctrl4_up_LsuPlugin_logic_onPma_FROM_LSU_MSB_FAILED_lane0;
  reg                 execute_ctrl4_up_LsuPlugin_logic_onPma_IO_lane0;
  reg                 execute_ctrl4_up_LsuPlugin_logic_onPma_IO_RSP_lane0_fault;
  reg                 execute_ctrl4_up_LsuPlugin_logic_onPma_IO_RSP_lane0_io;
  reg                 execute_ctrl4_up_LsuPlugin_logic_onPma_CACHED_RSP_lane0_fault;
  reg                 execute_ctrl4_up_LsuPlugin_logic_onPma_CACHED_RSP_lane0_io;
  reg                 execute_ctrl4_up_LsuPlugin_logic_preCtrl_MISS_ALIGNED_lane0;
  reg        [31:0]   execute_ctrl4_up_MMU_TRANSLATED_lane0;
  reg                 execute_ctrl4_up_LsuPlugin_logic_onTrigger_HIT_lane0;
  reg        [31:0]   execute_ctrl4_up_late0_SrcPlugin_SRC2_lane0;
  reg        [31:0]   execute_ctrl4_up_late0_SrcPlugin_SRC1_lane0;
  reg        [4:0]    execute_ctrl4_up_early0_MulPlugin_logic_steps_0_adders_1_lane0;
  reg        [62:0]   execute_ctrl4_up_early0_MulPlugin_logic_steps_0_adders_0_lane0;
  reg        [0:0]    execute_ctrl4_up_LsuL1Plugin_logic_WAYS_HITS_lane0;
  reg                 execute_ctrl4_up_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_loaded;
  reg        [21:0]   execute_ctrl4_up_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_address;
  reg                 execute_ctrl4_up_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_fault;
  reg        [31:0]   execute_ctrl4_up_LsuL1_PHYSICAL_ADDRESS_lane0;
  reg        [1:0]    execute_ctrl4_up_LsuL1Plugin_logic_WRITE_TO_READ_HAZARDS_lane0;
  reg        [31:0]   execute_ctrl4_up_LsuL1Plugin_logic_BANKS_MUXES_lane0_0;
  reg        [0:0]    execute_ctrl4_up_LsuL1Plugin_logic_BANK_BUSY_REMAPPED_lane0;
  reg        [0:0]    execute_ctrl4_up_LsuL1Plugin_logic_SHARED_lane0_dirty;
  reg                 execute_ctrl4_up_LsuPlugin_logic_FROM_PREFETCH_lane0;
  reg                 execute_ctrl4_up_LsuPlugin_logic_FROM_LSU_lane0;
  reg        [11:0]   execute_ctrl4_up_Decode_STORE_ID_lane0;
  reg                 execute_ctrl4_up_LsuL1_FLUSH_lane0;
  reg                 execute_ctrl4_up_LsuL1_PREFETCH_lane0;
  reg                 execute_ctrl4_up_LsuL1_INVALID_lane0;
  reg                 execute_ctrl4_up_LsuL1_CLEAN_lane0;
  reg                 execute_ctrl4_up_LsuL1_STORE_lane0;
  reg                 execute_ctrl4_up_LsuL1_ATOMIC_lane0;
  reg                 execute_ctrl4_up_LsuL1_LOAD_lane0;
  reg        [1:0]    execute_ctrl4_up_LsuL1_SIZE_lane0;
  reg        [3:0]    execute_ctrl4_up_LsuL1_MASK_lane0;
  reg        [31:0]   execute_ctrl4_up_early0_BranchPlugin_pcCalc_PC_LAST_SLICE_lane0;
  reg        [31:0]   execute_ctrl4_up_early0_BranchPlugin_pcCalc_PC_FALSE_lane0;
  reg        [31:0]   execute_ctrl4_up_early0_BranchPlugin_pcCalc_PC_TRUE_lane0;
  reg        [29:0]   execute_ctrl4_up_early0_MulPlugin_logic_mul_VALUES_3_lane0;
  reg        [46:0]   execute_ctrl4_up_early0_MulPlugin_logic_mul_VALUES_2_lane0;
  reg        [46:0]   execute_ctrl4_up_early0_MulPlugin_logic_mul_VALUES_1_lane0;
  reg        [33:0]   execute_ctrl4_up_early0_MulPlugin_logic_mul_VALUES_0_lane0;
  reg        [31:0]   execute_ctrl4_up_LsuL1_MIXED_ADDRESS_lane0;
  reg        [1:0]    execute_ctrl4_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0;
  reg                 execute_ctrl4_up_late0_IntAluPlugin_ALU_SLTX_lane0;
  reg                 execute_ctrl4_up_late0_IntAluPlugin_ALU_ADD_SUB_lane0;
  reg                 execute_ctrl4_up_LsuPlugin_logic_LSU_PREFETCH_lane0;
  reg                 execute_ctrl4_up_AguPlugin_FLOAT_lane0;
  reg                 execute_ctrl4_up_AguPlugin_ATOMIC_lane0;
  reg                 execute_ctrl4_up_AguPlugin_STORE_lane0;
  reg                 execute_ctrl4_up_AguPlugin_LOAD_lane0;
  reg                 execute_ctrl4_up_MulPlugin_HIGH_lane0;
  reg        [1:0]    execute_ctrl4_up_BranchPlugin_BRANCH_CTRL_lane0;
  reg                 execute_ctrl4_up_BarrelShifterPlugin_SIGNED_lane0;
  reg                 execute_ctrl4_up_BarrelShifterPlugin_LEFT_lane0;
  reg                 execute_ctrl4_up_SrcStageables_UNSIGNED_lane0;
  reg        [1:0]    execute_ctrl4_up_lane0_IntFormatPlugin_logic_WIDTH_ID_lane0;
  reg                 execute_ctrl4_up_lane0_IntFormatPlugin_logic_SIGNED_lane0;
  reg                 execute_ctrl4_up_SrcStageables_ZERO_lane0;
  reg                 execute_ctrl4_up_SrcStageables_REVERT_lane0;
  reg                 execute_ctrl4_up_lane0_logic_completions_onCtrl_1_ENABLE_lane0;
  reg                 execute_ctrl4_up_COMPLETION_AT_4_lane0;
  reg                 execute_ctrl4_up_lane0_integer_WriteBackPlugin_SEL_lane0;
  reg                 execute_ctrl4_up_LsuPlugin_logic_FENCE_lane0;
  reg                 execute_ctrl4_up_AguPlugin_SEL_lane0;
  reg                 execute_ctrl4_up_late0_BranchPlugin_SEL_lane0;
  reg                 execute_ctrl4_up_late0_BarrelShifterPlugin_SEL_lane0;
  reg                 execute_ctrl4_up_late0_IntAluPlugin_SEL_lane0;
  reg                 execute_ctrl4_up_early0_MulPlugin_SEL_lane0;
  reg                 execute_ctrl4_up_early0_BranchPlugin_SEL_lane0;
  reg        [1:0]    execute_ctrl4_up_AguPlugin_SIZE_lane0;
  reg        [4:0]    execute_ctrl4_up_RD_PHYS_lane0;
  reg        [15:0]   execute_ctrl4_up_Decode_UOP_ID_lane0;
  reg        [31:0]   execute_ctrl4_up_PC_lane0;
  reg        [31:0]   execute_ctrl4_up_Prediction_ALIGNED_JUMPED_PC_lane0;
  reg                 execute_ctrl4_up_Prediction_ALIGNED_JUMPED_lane0;
  reg        [31:0]   execute_ctrl4_up_Decode_UOP_lane0;
  wire       [1:0]    execute_ctrl2_down_late0_SrcPlugin_logic_SRC2_CTRL_lane0;
  wire       [0:0]    execute_ctrl2_down_late0_SrcPlugin_logic_SRC1_CTRL_lane0;
  wire       [1:0]    execute_ctrl2_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0;
  wire                execute_ctrl2_down_late0_IntAluPlugin_ALU_SLTX_lane0;
  wire                execute_ctrl2_down_late0_IntAluPlugin_ALU_ADD_SUB_lane0;
  wire                execute_ctrl2_down_LsuPlugin_logic_LSU_PREFETCH_lane0;
  wire                execute_ctrl2_down_AguPlugin_FLOAT_lane0;
  wire                execute_ctrl2_down_MulPlugin_HIGH_lane0;
  wire       [1:0]    execute_ctrl2_down_lane0_IntFormatPlugin_logic_WIDTH_ID_lane0;
  wire                execute_ctrl2_down_lane0_IntFormatPlugin_logic_SIGNED_lane0;
  wire                execute_ctrl2_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0;
  wire                execute_ctrl2_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0;
  wire                execute_ctrl2_down_COMPLETION_AT_3_lane0;
  wire                execute_ctrl2_down_COMPLETION_AT_4_lane0;
  wire                execute_ctrl2_down_lane0_integer_WriteBackPlugin_SEL_lane0;
  wire                execute_ctrl2_down_LsuPlugin_logic_FENCE_lane0;
  wire                execute_ctrl2_down_late0_BranchPlugin_SEL_lane0;
  wire                execute_ctrl2_down_late0_BarrelShifterPlugin_SEL_lane0;
  wire                execute_ctrl2_down_late0_IntAluPlugin_SEL_lane0;
  wire                execute_ctrl2_down_early0_MulPlugin_SEL_lane0;
  reg                 execute_ctrl3_up_LsuPlugin_logic_FROM_PREFETCH_lane0;
  reg                 execute_ctrl3_up_LsuPlugin_logic_FROM_LSU_lane0;
  reg        [11:0]   execute_ctrl3_up_Decode_STORE_ID_lane0;
  reg                 execute_ctrl3_up_LsuL1_FLUSH_lane0;
  reg                 execute_ctrl3_up_LsuL1_PREFETCH_lane0;
  reg                 execute_ctrl3_up_LsuL1_INVALID_lane0;
  reg                 execute_ctrl3_up_LsuL1_CLEAN_lane0;
  reg                 execute_ctrl3_up_LsuL1_STORE_lane0;
  reg                 execute_ctrl3_up_LsuL1_ATOMIC_lane0;
  reg                 execute_ctrl3_up_LsuL1_LOAD_lane0;
  reg        [1:0]    execute_ctrl3_up_LsuL1_SIZE_lane0;
  reg        [3:0]    execute_ctrl3_up_LsuL1_MASK_lane0;
  reg                 execute_ctrl3_up_LsuPlugin_logic_FROM_ACCESS_lane0;
  reg        [31:0]   execute_ctrl3_up_early0_BranchPlugin_pcCalc_PC_LAST_SLICE_lane0;
  reg        [31:0]   execute_ctrl3_up_early0_BranchPlugin_pcCalc_PC_FALSE_lane0;
  reg        [31:0]   execute_ctrl3_up_early0_BranchPlugin_pcCalc_PC_TRUE_lane0;
  reg        [31:0]   execute_ctrl3_up_DivPlugin_DIV_RESULT_lane0;
  reg        [29:0]   execute_ctrl3_up_early0_MulPlugin_logic_mul_VALUES_3_lane0;
  reg        [46:0]   execute_ctrl3_up_early0_MulPlugin_logic_mul_VALUES_2_lane0;
  reg        [46:0]   execute_ctrl3_up_early0_MulPlugin_logic_mul_VALUES_1_lane0;
  reg        [33:0]   execute_ctrl3_up_early0_MulPlugin_logic_mul_VALUES_0_lane0;
  reg        [0:0]    execute_ctrl3_up_LsuL1Plugin_logic_lsu_rt0_SHARED_BYPASS_VALUE_lane0_dirty;
  reg                 execute_ctrl3_up_LsuL1Plugin_logic_lsu_rt0_SHARED_BYPASS_VALID_lane0;
  reg        [3:0]    execute_ctrl3_up_LsuL1Plugin_logic_EVENT_WRITE_MASK_lane0;
  reg        [31:0]   execute_ctrl3_up_LsuL1Plugin_logic_EVENT_WRITE_ADDRESS_lane0;
  reg                 execute_ctrl3_up_LsuL1Plugin_logic_EVENT_WRITE_VALID_lane0;
  reg        [0:0]    execute_ctrl3_up_LsuL1Plugin_logic_BANK_BUSY_lane0;
  reg        [31:0]   execute_ctrl3_up_LsuL1_MIXED_ADDRESS_lane0;
  reg        [31:0]   execute_ctrl3_up_early0_SrcPlugin_ADD_SUB_lane0;
  reg                 execute_ctrl3_up_COMMIT_lane0;
  reg        [1:0]    execute_ctrl3_up_late0_SrcPlugin_logic_SRC2_CTRL_lane0;
  reg        [0:0]    execute_ctrl3_up_late0_SrcPlugin_logic_SRC1_CTRL_lane0;
  reg        [1:0]    execute_ctrl3_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0;
  reg                 execute_ctrl3_up_late0_IntAluPlugin_ALU_SLTX_lane0;
  reg                 execute_ctrl3_up_late0_IntAluPlugin_ALU_ADD_SUB_lane0;
  reg                 execute_ctrl3_up_LsuPlugin_logic_LSU_PREFETCH_lane0;
  reg                 execute_ctrl3_up_AguPlugin_FLOAT_lane0;
  reg                 execute_ctrl3_up_AguPlugin_ATOMIC_lane0;
  reg                 execute_ctrl3_up_AguPlugin_STORE_lane0;
  reg                 execute_ctrl3_up_AguPlugin_LOAD_lane0;
  reg                 execute_ctrl3_up_MulPlugin_HIGH_lane0;
  reg        [1:0]    execute_ctrl3_up_BranchPlugin_BRANCH_CTRL_lane0;
  reg                 execute_ctrl3_up_BarrelShifterPlugin_SIGNED_lane0;
  reg                 execute_ctrl3_up_BarrelShifterPlugin_LEFT_lane0;
  reg                 execute_ctrl3_up_SrcStageables_UNSIGNED_lane0;
  reg        [1:0]    execute_ctrl3_up_lane0_IntFormatPlugin_logic_WIDTH_ID_lane0;
  reg                 execute_ctrl3_up_lane0_IntFormatPlugin_logic_SIGNED_lane0;
  reg                 execute_ctrl3_up_SrcStageables_ZERO_lane0;
  reg                 execute_ctrl3_up_SrcStageables_REVERT_lane0;
  reg                 execute_ctrl3_up_lane0_logic_completions_onCtrl_2_ENABLE_lane0;
  reg                 execute_ctrl3_up_lane0_logic_completions_onCtrl_1_ENABLE_lane0;
  reg                 execute_ctrl3_up_COMPLETION_AT_3_lane0;
  reg                 execute_ctrl3_up_COMPLETION_AT_4_lane0;
  reg                 execute_ctrl3_up_lane0_integer_WriteBackPlugin_SEL_lane0;
  reg                 execute_ctrl3_up_LsuPlugin_logic_FENCE_lane0;
  reg                 execute_ctrl3_up_AguPlugin_SEL_lane0;
  reg                 execute_ctrl3_up_CsrAccessPlugin_SEL_lane0;
  reg                 execute_ctrl3_up_late0_BranchPlugin_SEL_lane0;
  reg                 execute_ctrl3_up_late0_BarrelShifterPlugin_SEL_lane0;
  reg                 execute_ctrl3_up_late0_IntAluPlugin_SEL_lane0;
  reg                 execute_ctrl3_up_early0_DivPlugin_SEL_lane0;
  reg                 execute_ctrl3_up_early0_MulPlugin_SEL_lane0;
  reg                 execute_ctrl3_up_early0_BranchPlugin_SEL_lane0;
  reg        [1:0]    execute_ctrl3_up_AguPlugin_SIZE_lane0;
  reg        [4:0]    execute_ctrl3_up_RD_PHYS_lane0;
  reg        [4:0]    execute_ctrl3_up_RS2_PHYS_lane0;
  reg        [4:0]    execute_ctrl3_up_RS1_PHYS_lane0;
  reg        [15:0]   execute_ctrl3_up_Decode_UOP_ID_lane0;
  reg                 execute_ctrl3_up_TRAP_lane0;
  reg        [31:0]   execute_ctrl3_up_PC_lane0;
  reg        [31:0]   execute_ctrl3_up_Prediction_ALIGNED_JUMPED_PC_lane0;
  reg                 execute_ctrl3_up_Prediction_ALIGNED_JUMPED_lane0;
  reg        [31:0]   execute_ctrl3_up_Decode_UOP_lane0;
  wire       [1:0]    execute_ctrl1_down_AguPlugin_SIZE_lane0;
  wire                execute_ctrl1_down_COMPLETED_lane0;
  wire       [4:0]    execute_ctrl1_down_RD_PHYS_lane0;
  wire       [15:0]   execute_ctrl1_down_Decode_UOP_ID_lane0;
  wire       [31:0]   execute_ctrl1_down_Prediction_ALIGNED_JUMPED_PC_lane0;
  wire                execute_ctrl1_down_Prediction_ALIGNED_JUMPED_lane0;
  wire                execute_ctrl1_down_isReady;
  reg        [1:0]    execute_ctrl2_up_late0_SrcPlugin_logic_SRC2_CTRL_lane0;
  reg        [0:0]    execute_ctrl2_up_late0_SrcPlugin_logic_SRC1_CTRL_lane0;
  reg        [1:0]    execute_ctrl2_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0;
  reg                 execute_ctrl2_up_late0_IntAluPlugin_ALU_SLTX_lane0;
  reg                 execute_ctrl2_up_late0_IntAluPlugin_ALU_ADD_SUB_lane0;
  reg        [2:0]    execute_ctrl2_up_early0_EnvPlugin_OP_lane0;
  reg                 execute_ctrl2_up_LsuPlugin_logic_LSU_PREFETCH_lane0;
  reg                 execute_ctrl2_up_AguPlugin_FLOAT_lane0;
  reg                 execute_ctrl2_up_AguPlugin_ATOMIC_lane0;
  reg                 execute_ctrl2_up_AguPlugin_STORE_lane0;
  reg                 execute_ctrl2_up_AguPlugin_LOAD_lane0;
  reg                 execute_ctrl2_up_CsrAccessPlugin_CSR_CLEAR_lane0;
  reg                 execute_ctrl2_up_CsrAccessPlugin_CSR_MASK_lane0;
  reg                 execute_ctrl2_up_CsrAccessPlugin_CSR_IMM_lane0;
  reg                 execute_ctrl2_up_DivPlugin_REM_lane0;
  reg                 execute_ctrl2_up_RsUnsignedPlugin_RS2_SIGNED_lane0;
  reg                 execute_ctrl2_up_RsUnsignedPlugin_RS1_SIGNED_lane0;
  reg                 execute_ctrl2_up_MulPlugin_HIGH_lane0;
  reg        [1:0]    execute_ctrl2_up_BranchPlugin_BRANCH_CTRL_lane0;
  reg                 execute_ctrl2_up_BarrelShifterPlugin_SIGNED_lane0;
  reg                 execute_ctrl2_up_BarrelShifterPlugin_LEFT_lane0;
  reg                 execute_ctrl2_up_SrcStageables_UNSIGNED_lane0;
  reg                 execute_ctrl2_up_BYPASSED_AT_3_lane0;
  reg        [1:0]    execute_ctrl2_up_lane0_IntFormatPlugin_logic_WIDTH_ID_lane0;
  reg                 execute_ctrl2_up_lane0_IntFormatPlugin_logic_SIGNED_lane0;
  reg                 execute_ctrl2_up_SrcStageables_ZERO_lane0;
  reg                 execute_ctrl2_up_SrcStageables_REVERT_lane0;
  reg        [1:0]    execute_ctrl2_up_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0;
  reg                 execute_ctrl2_up_early0_IntAluPlugin_ALU_SLTX_lane0;
  reg                 execute_ctrl2_up_early0_IntAluPlugin_ALU_ADD_SUB_lane0;
  reg                 execute_ctrl2_up_lane0_logic_completions_onCtrl_2_ENABLE_lane0;
  reg                 execute_ctrl2_up_lane0_logic_completions_onCtrl_1_ENABLE_lane0;
  reg                 execute_ctrl2_up_lane0_logic_completions_onCtrl_0_ENABLE_lane0;
  reg                 execute_ctrl2_up_COMPLETION_AT_3_lane0;
  reg                 execute_ctrl2_up_COMPLETION_AT_4_lane0;
  reg                 execute_ctrl2_up_COMPLETION_AT_2_lane0;
  reg                 execute_ctrl2_up_lane0_integer_WriteBackPlugin_SEL_lane0;
  reg                 execute_ctrl2_up_LsuPlugin_logic_FENCE_lane0;
  reg                 execute_ctrl2_up_AguPlugin_SEL_lane0;
  reg                 execute_ctrl2_up_CsrAccessPlugin_SEL_lane0;
  reg                 execute_ctrl2_up_late0_BranchPlugin_SEL_lane0;
  reg                 execute_ctrl2_up_late0_BarrelShifterPlugin_SEL_lane0;
  reg                 execute_ctrl2_up_late0_IntAluPlugin_SEL_lane0;
  reg                 execute_ctrl2_up_early0_EnvPlugin_SEL_lane0;
  reg                 execute_ctrl2_up_early0_DivPlugin_SEL_lane0;
  reg                 execute_ctrl2_up_early0_MulPlugin_SEL_lane0;
  reg                 execute_ctrl2_up_early0_BranchPlugin_SEL_lane0;
  reg                 execute_ctrl2_up_early0_BarrelShifterPlugin_SEL_lane0;
  reg                 execute_ctrl2_up_early0_IntAluPlugin_SEL_lane0;
  reg                 execute_ctrl2_up_MAY_FLUSH_PRECISE_3_lane0;
  reg        [31:0]   execute_ctrl2_up_early0_SrcPlugin_SRC2_lane0;
  reg        [31:0]   execute_ctrl2_up_early0_SrcPlugin_SRC1_lane0;
  reg        [1:0]    execute_ctrl2_up_AguPlugin_SIZE_lane0;
  reg        [4:0]    execute_ctrl2_up_RS2_PHYS_lane0;
  reg        [4:0]    execute_ctrl2_up_RS1_PHYS_lane0;
  reg        [15:0]   execute_ctrl2_up_Decode_UOP_ID_lane0;
  reg        [31:0]   execute_ctrl2_up_PC_lane0;
  reg        [31:0]   execute_ctrl2_up_Prediction_ALIGNED_JUMPED_PC_lane0;
  reg                 execute_ctrl2_up_Prediction_ALIGNED_JUMPED_lane0;
  reg        [31:0]   execute_ctrl2_up_Decode_UOP_lane0;
  wire       [0:0]    execute_ctrl0_down_lane0_LAYER_SEL_lane0;
  wire                execute_ctrl0_down_COMPLETED_lane0;
  wire       [4:0]    execute_ctrl0_down_RD_PHYS_lane0;
  wire                execute_ctrl0_down_TRAP_lane0;
  wire       [31:0]   execute_ctrl0_down_PC_lane0;
  wire       [31:0]   execute_ctrl0_down_Prediction_ALIGNED_JUMPED_PC_lane0;
  wire                execute_ctrl0_down_Prediction_ALIGNED_JUMPED_lane0;
  reg        [1:0]    execute_ctrl1_up_AguPlugin_SIZE_lane0;
  reg        [0:0]    execute_ctrl1_up_lane0_LAYER_SEL_lane0;
  reg                 execute_ctrl1_up_COMPLETED_lane0;
  reg        [4:0]    execute_ctrl1_up_RS2_PHYS_lane0;
  reg        [4:0]    execute_ctrl1_up_RS1_PHYS_lane0;
  reg        [15:0]   execute_ctrl1_up_Decode_UOP_ID_lane0;
  reg                 execute_ctrl1_up_TRAP_lane0;
  reg        [31:0]   execute_ctrl1_up_PC_lane0;
  reg        [31:0]   execute_ctrl1_up_Prediction_ALIGNED_JUMPED_PC_lane0;
  reg                 execute_ctrl1_up_Prediction_ALIGNED_JUMPED_lane0;
  reg        [31:0]   execute_ctrl1_up_Decode_UOP_lane0;
  wire                decode_ctrls_1_down_isReady;
  wire                decode_ctrls_0_down_Prediction_ALIGN_REDO_0;
  wire       [0:0]    decode_ctrls_0_down_Prediction_ALIGNED_SLICES_TAKEN_0;
  wire       [0:0]    decode_ctrls_0_down_Prediction_ALIGNED_SLICES_BRANCH_0;
  wire       [31:0]   decode_ctrls_0_down_Prediction_ALIGNED_JUMPED_PC_0;
  wire                decode_ctrls_0_down_Prediction_ALIGNED_JUMPED_0;
  wire       [31:0]   decode_ctrls_0_down_Decode_INSTRUCTION_RAW_0;
  wire                decode_ctrls_0_down_Decode_DECOMPRESSION_FAULT_0;
  wire       [31:0]   decode_ctrls_0_down_Decode_INSTRUCTION_0;
  wire                decode_ctrls_0_down_isValid;
  wire                decode_ctrls_0_down_isReady;
  reg                 decode_ctrls_1_up_Prediction_ALIGN_REDO_0;
  reg        [0:0]    decode_ctrls_1_up_Prediction_ALIGNED_SLICES_TAKEN_0;
  reg        [0:0]    decode_ctrls_1_up_Prediction_ALIGNED_SLICES_BRANCH_0;
  reg        [31:0]   decode_ctrls_1_up_Prediction_ALIGNED_JUMPED_PC_0;
  reg                 decode_ctrls_1_up_Prediction_ALIGNED_JUMPED_0;
  reg        [9:0]    decode_ctrls_1_up_Decode_DOP_ID_0;
  reg        [31:0]   decode_ctrls_1_up_PC_0;
  reg        [31:0]   decode_ctrls_1_up_Decode_INSTRUCTION_RAW_0;
  reg                 decode_ctrls_1_up_Decode_DECOMPRESSION_FAULT_0;
  reg        [31:0]   decode_ctrls_1_up_Decode_INSTRUCTION_0;
  wire       [9:0]    fetch_logic_ctrls_1_down_Fetch_ID;
  wire                fetch_logic_ctrls_1_down_Fetch_PC_FAULT;
  wire                fetch_logic_ctrls_1_down_isValid;
  wire                fetch_logic_ctrls_1_down_isReady;
  reg                 fetch_logic_ctrls_2_up_MMU_BYPASS_TRANSLATION;
  reg                 fetch_logic_ctrls_2_up_MMU_ACCESS_FAULT;
  reg                 fetch_logic_ctrls_2_up_MMU_PAGE_FAULT;
  reg                 fetch_logic_ctrls_2_up_MMU_ALLOW_EXECUTE;
  reg                 fetch_logic_ctrls_2_up_MMU_HAZARD;
  reg                 fetch_logic_ctrls_2_up_MMU_REFILL;
  reg                 fetch_logic_ctrls_2_up_BtbPlugin_logic_chunksLogic_0_hitCalc_HIT;
  reg        [15:0]   fetch_logic_ctrls_2_up_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_hash;
  reg        [29:0]   fetch_logic_ctrls_2_up_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_pcTarget;
  reg                 fetch_logic_ctrls_2_up_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isBranch;
  reg                 fetch_logic_ctrls_2_up_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isPush;
  reg                 fetch_logic_ctrls_2_up_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isPop;
  reg                 fetch_logic_ctrls_2_up_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_taken;
  reg                 fetch_logic_ctrls_2_up_FetchL1Plugin_logic_WAYS_HIT;
  reg        [31:0]   fetch_logic_ctrls_2_up_MMU_TRANSLATED;
  reg                 fetch_logic_ctrls_2_up_FetchL1Plugin_logic_WAYS_HITS_0;
  reg                 fetch_logic_ctrls_2_up_FetchL1Plugin_logic_HAZARD;
  reg        [31:0]   fetch_logic_ctrls_2_up_FetchL1Plugin_logic_BANKS_MUXES_0;
  reg                 fetch_logic_ctrls_2_up_FetchL1Plugin_logic_WAYS_TAGS_0_loaded;
  reg                 fetch_logic_ctrls_2_up_FetchL1Plugin_logic_WAYS_TAGS_0_error;
  reg        [21:0]   fetch_logic_ctrls_2_up_FetchL1Plugin_logic_WAYS_TAGS_0_address;
  reg        [9:0]    fetch_logic_ctrls_2_up_Fetch_ID;
  reg                 fetch_logic_ctrls_2_up_Fetch_PC_FAULT;
  reg        [31:0]   fetch_logic_ctrls_2_up_Fetch_WORD_PC;
  wire                fetch_logic_ctrls_0_down_Fetch_PC_FAULT;
  wire                fetch_logic_ctrls_0_down_isValid;
  reg        [0:0]    fetch_logic_ctrls_1_up_BtbPlugin_logic_readCmd_HAZARDS;
  reg        [3:0]    fetch_logic_ctrls_1_up_FetchL1Plugin_logic_cmd_TAGS_UPDATE_ADDRESS;
  reg                 fetch_logic_ctrls_1_up_FetchL1Plugin_logic_cmd_TAGS_UPDATE;
  reg                 fetch_logic_ctrls_1_up_FetchL1Plugin_logic_cmd_PLRU_BYPASS_VALID;
  reg        [9:0]    fetch_logic_ctrls_1_up_Fetch_ID;
  reg                 fetch_logic_ctrls_1_up_Fetch_PC_FAULT;
  reg        [31:0]   fetch_logic_ctrls_1_up_Fetch_WORD_PC;
  reg                 fetch_logic_ctrls_2_up_valid;
  wire                decode_ctrls_1_down_valid;
  reg                 fetch_logic_ctrls_1_down_valid;
  wire                decode_ctrls_0_down_valid;
  reg                 fetch_logic_ctrls_0_down_valid;
  wire                execute_ctrl0_up_ready;
  wire                execute_ctrl0_down_ready;
  wire                execute_ctrl1_up_ready;
  wire                execute_ctrl1_down_ready;
  wire                execute_ctrl2_up_ready;
  wire                execute_ctrl2_down_ready;
  wire                execute_ctrl3_up_ready;
  wire                execute_ctrl3_down_ready;
  wire                fetch_logic_ctrls_0_down_ready;
  wire                execute_ctrl4_up_ready;
  wire                decode_ctrls_0_up_ready;
  wire                fetch_logic_ctrls_1_up_cancel;
  wire                execute_ctrl4_down_ready;
  reg                 decode_ctrls_0_down_ready;
  wire                fetch_logic_ctrls_1_down_ready;
  wire                execute_ctrl5_up_ready;
  wire                fetch_logic_ctrls_2_up_ready;
  wire                fetch_logic_ctrls_2_up_cancel;
  wire                execute_ctrl5_down_ready;
  wire                execute_ctrl4_down_AguPlugin_ATOMIC_lane0;
  wire       [11:0]   execute_ctrl4_down_Decode_STORE_ID_lane0;
  wire       [31:0]   execute_ctrl4_down_MMU_TRANSLATED_lane0;
  wire       [1:0]    execute_ctrl4_down_AguPlugin_SIZE_lane0;
  wire                execute_ctrl4_down_LsuPlugin_logic_LSU_PREFETCH_lane0;
  wire                execute_ctrl4_down_AguPlugin_LOAD_lane0;
  wire                execute_ctrl4_down_RD_ENABLE_lane0;
  reg                 execute_ctrl4_RD_ENABLE_lane0_bypass;
  reg                 execute_ctrl4_LANE_SEL_lane0_bypass;
  wire                execute_ctrl3_down_RD_ENABLE_lane0;
  reg                 execute_ctrl3_RD_ENABLE_lane0_bypass;
  reg                 execute_ctrl3_LANE_SEL_lane0_bypass;
  wire                execute_ctrl2_down_RD_ENABLE_lane0;
  reg                 execute_ctrl2_RD_ENABLE_lane0_bypass;
  reg                 execute_ctrl2_LANE_SEL_lane0_bypass;
  wire                execute_ctrl1_down_RD_ENABLE_lane0;
  reg                 execute_ctrl1_RD_ENABLE_lane0_bypass;
  wire                execute_ctrl1_down_LANE_SEL_lane0;
  reg                 execute_ctrl1_LANE_SEL_lane0_bypass;
  wire                execute_ctrl0_down_RD_ENABLE_lane0;
  reg                 execute_ctrl0_RD_ENABLE_lane0_bypass;
  reg                 execute_ctrl0_LANE_SEL_lane0_bypass;
  wire                execute_ctrl1_down_TRAP_lane0;
  wire       [1:0]    execute_ctrl1_down_late0_SrcPlugin_logic_SRC2_CTRL_lane0;
  wire       [0:0]    execute_ctrl1_down_late0_SrcPlugin_logic_SRC1_CTRL_lane0;
  wire       [1:0]    execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0;
  wire                execute_ctrl1_down_late0_IntAluPlugin_ALU_SLTX_lane0;
  wire                execute_ctrl1_down_late0_IntAluPlugin_ALU_ADD_SUB_lane0;
  wire       [2:0]    execute_ctrl1_down_early0_EnvPlugin_OP_lane0;
  wire                execute_ctrl1_down_LsuPlugin_logic_LSU_PREFETCH_lane0;
  wire                execute_ctrl1_down_AguPlugin_INVALIDATE_lane0;
  wire                execute_ctrl1_down_AguPlugin_CLEAN_lane0;
  wire                execute_ctrl1_down_AguPlugin_FLOAT_lane0;
  wire                execute_ctrl1_down_AguPlugin_ATOMIC_lane0;
  wire                execute_ctrl1_down_AguPlugin_STORE_lane0;
  wire                execute_ctrl1_down_AguPlugin_LOAD_lane0;
  wire                execute_ctrl1_down_CsrAccessPlugin_CSR_CLEAR_lane0;
  wire                execute_ctrl1_down_CsrAccessPlugin_CSR_MASK_lane0;
  wire                execute_ctrl1_down_CsrAccessPlugin_CSR_IMM_lane0;
  wire                execute_ctrl1_down_DivPlugin_REM_lane0;
  wire                execute_ctrl1_down_RsUnsignedPlugin_RS2_SIGNED_lane0;
  wire                execute_ctrl1_down_RsUnsignedPlugin_RS1_SIGNED_lane0;
  wire                execute_ctrl1_down_MulPlugin_HIGH_lane0;
  wire       [1:0]    execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0;
  wire                execute_ctrl1_down_BarrelShifterPlugin_SIGNED_lane0;
  wire                execute_ctrl1_down_BarrelShifterPlugin_LEFT_lane0;
  wire                execute_ctrl1_down_SrcStageables_UNSIGNED_lane0;
  wire                execute_ctrl1_down_BYPASSED_AT_3_lane0;
  wire       [1:0]    execute_ctrl1_down_lane0_IntFormatPlugin_logic_WIDTH_ID_lane0;
  wire                execute_ctrl1_down_lane0_IntFormatPlugin_logic_SIGNED_lane0;
  wire                execute_ctrl1_down_SrcStageables_ZERO_lane0;
  wire                execute_ctrl1_down_SrcStageables_REVERT_lane0;
  wire       [1:0]    execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0;
  wire                execute_ctrl1_down_early0_IntAluPlugin_ALU_SLTX_lane0;
  wire                execute_ctrl1_down_early0_IntAluPlugin_ALU_ADD_SUB_lane0;
  reg                 execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0;
  reg                 execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0;
  reg                 execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0;
  reg                 execute_ctrl1_down_COMPLETION_AT_3_lane0;
  reg                 execute_ctrl1_down_COMPLETION_AT_4_lane0;
  reg                 execute_ctrl1_down_COMPLETION_AT_2_lane0;
  reg                 execute_ctrl1_down_lane0_integer_WriteBackPlugin_SEL_lane0;
  reg                 execute_ctrl1_down_LsuPlugin_logic_FENCE_lane0;
  reg                 execute_ctrl1_down_AguPlugin_SEL_lane0;
  reg                 execute_ctrl1_down_CsrAccessPlugin_SEL_lane0;
  reg                 execute_ctrl1_down_late0_BranchPlugin_SEL_lane0;
  reg                 execute_ctrl1_down_late0_BarrelShifterPlugin_SEL_lane0;
  reg                 execute_ctrl1_down_late0_IntAluPlugin_SEL_lane0;
  reg                 execute_ctrl1_down_early0_EnvPlugin_SEL_lane0;
  reg                 execute_ctrl1_down_early0_DivPlugin_SEL_lane0;
  reg                 execute_ctrl1_down_early0_MulPlugin_SEL_lane0;
  reg                 execute_ctrl1_down_early0_BranchPlugin_SEL_lane0;
  reg                 execute_ctrl1_down_early0_BarrelShifterPlugin_SEL_lane0;
  reg                 execute_ctrl1_down_early0_IntAluPlugin_SEL_lane0;
  wire       [0:0]    execute_ctrl1_down_lane0_LAYER_SEL_lane0;
  wire                execute_ctrl3_down_TRAP_lane0;
  wire                execute_ctrl3_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0;
  wire                execute_ctrl4_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0;
  wire                execute_ctrl2_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0;
  reg        [31:0]   execute_ctrl3_up_integer_RS2_lane0;
  wire       [31:0]   execute_ctrl3_integer_RS2_lane0_bypass;
  wire       [4:0]    execute_ctrl3_down_RS2_PHYS_lane0;
  wire       [31:0]   execute_ctrl2_down_integer_RS2_lane0;
  wire       [31:0]   execute_ctrl2_integer_RS2_lane0_bypass;
  wire       [4:0]    execute_ctrl2_down_RS2_PHYS_lane0;
  wire       [4:0]    execute_ctrl1_down_RS2_PHYS_lane0;
  wire       [4:0]    execute_ctrl0_down_RS2_PHYS_lane0;
  reg        [31:0]   execute_ctrl3_up_integer_RS1_lane0;
  wire       [31:0]   execute_ctrl3_integer_RS1_lane0_bypass;
  wire       [4:0]    execute_ctrl3_down_RS1_PHYS_lane0;
  wire       [31:0]   execute_ctrl2_down_integer_RS1_lane0;
  wire       [31:0]   execute_ctrl2_integer_RS1_lane0_bypass;
  wire       [4:0]    execute_ctrl2_down_RS1_PHYS_lane0;
  wire       [31:0]   execute_ctrl5_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0;
  wire       [4:0]    execute_ctrl5_down_RD_PHYS_lane0;
  reg                 execute_ctrl5_up_RD_ENABLE_lane0;
  reg                 execute_ctrl5_up_LANE_SEL_lane0;
  wire       [4:0]    execute_ctrl3_down_RD_PHYS_lane0;
  wire       [4:0]    execute_ctrl1_down_RS1_PHYS_lane0;
  wire       [4:0]    execute_ctrl0_down_RS1_PHYS_lane0;
  reg                 _zz_1;
  wire                execute_ctrl3_down_MMU_BYPASS_TRANSLATION_lane0;
  wire                execute_ctrl3_down_MMU_ALLOW_EXECUTE_lane0;
  wire                fetch_logic_ctrls_1_down_MMU_BYPASS_TRANSLATION;
  wire                fetch_logic_ctrls_1_down_MMU_ACCESS_FAULT;
  wire                fetch_logic_ctrls_1_down_MMU_PAGE_FAULT;
  wire                fetch_logic_ctrls_1_down_MMU_ALLOW_WRITE;
  wire                fetch_logic_ctrls_1_down_MMU_ALLOW_READ;
  wire                fetch_logic_ctrls_1_down_MMU_ALLOW_EXECUTE;
  wire                fetch_logic_ctrls_1_down_MMU_HAZARD;
  wire                fetch_logic_ctrls_1_down_MMU_REFILL;
  wire                execute_ctrl3_down_CsrAccessPlugin_SEL_lane0;
  wire       [4:0]    execute_ctrl2_down_RD_PHYS_lane0;
  wire                execute_ctrl2_down_CsrAccessPlugin_CSR_CLEAR_lane0;
  wire                execute_ctrl2_down_CsrAccessPlugin_CSR_MASK_lane0;
  wire                execute_ctrl2_down_CsrAccessPlugin_CSR_IMM_lane0;
  wire                execute_ctrl2_down_CsrAccessPlugin_SEL_lane0;
  wire                fetch_logic_ctrls_0_up_isFiring;
  reg        [9:0]    fetch_logic_ctrls_0_up_Fetch_ID;
  wire                fetch_logic_ctrls_0_up_Fetch_PC_FAULT;
  wire       [31:0]   fetch_logic_ctrls_0_up_Fetch_WORD_PC;
  reg                 fetch_logic_ctrls_0_up_ready;
  wire                fetch_logic_ctrls_0_up_valid;
  wire                execute_ctrl5_down_COMMIT_lane0;
  wire                execute_ctrl5_down_isReady;
  wire                execute_ctrl5_down_LANE_SEL_lane0;
  wire                decode_ctrls_0_down_TRAP_0;
  wire                decode_ctrls_1_down_LANE_SEL_0;
  reg                 decode_ctrls_1_LANE_SEL_0_bypass;
  wire                decode_ctrls_0_down_LANE_SEL_0;
  reg                 decode_ctrls_0_LANE_SEL_0_bypass;
  wire                decode_ctrls_0_up_isMoving;
  wire       [9:0]    fetch_logic_ctrls_2_down_Fetch_ID;
  wire                fetch_logic_ctrls_2_down_ready;
  wire                fetch_logic_ctrls_2_down_valid;
  wire                fetch_logic_ctrls_2_down_isValid;
  wire       [0:0]    fetch_logic_ctrls_2_down_Prediction_WORD_SLICES_TAKEN;
  wire       [0:0]    fetch_logic_ctrls_2_down_Prediction_WORD_SLICES_BRANCH;
  wire       [31:0]   fetch_logic_ctrls_2_down_Prediction_WORD_JUMP_PC;
  wire                fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_hitCalc_HIT;
  wire                fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_predict_TAKEN;
  wire       [15:0]   fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_hash;
  wire       [29:0]   fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_pcTarget;
  wire                fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isBranch;
  wire                fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isPush;
  wire                fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isPop;
  wire                fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_taken;
  wire       [0:0]    fetch_logic_ctrls_1_down_BtbPlugin_logic_readCmd_HAZARDS;
  wire                fetch_logic_ctrls_1_up_isValid;
  wire                fetch_logic_ctrls_1_down_BtbPlugin_logic_chunksLogic_0_hitCalc_HIT;
  (* keep , syn_keep *) wire       [15:0]   fetch_logic_ctrls_1_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_hash /* synthesis syn_keep = 1 */ ;
  (* keep , syn_keep *) wire       [29:0]   fetch_logic_ctrls_1_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_pcTarget /* synthesis syn_keep = 1 */ ;
  (* keep , syn_keep *) wire                fetch_logic_ctrls_1_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isBranch /* synthesis syn_keep = 1 */ ;
  (* keep , syn_keep *) wire                fetch_logic_ctrls_1_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isPush /* synthesis syn_keep = 1 */ ;
  (* keep , syn_keep *) wire                fetch_logic_ctrls_1_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isPop /* synthesis syn_keep = 1 */ ;
  (* keep , syn_keep *) wire                fetch_logic_ctrls_1_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_taken /* synthesis syn_keep = 1 */ ;
  wire       [0:0]    fetch_logic_ctrls_0_down_BtbPlugin_logic_readCmd_HAZARDS;
  wire                fetch_logic_ctrls_0_down_isReady;
  wire       [15:0]   execute_ctrl0_down_Decode_UOP_ID_lane0;
  wire                execute_ctrl0_down_isReady;
  wire                execute_ctrl0_down_LANE_SEL_lane0;
  wire       [9:0]    decode_ctrls_1_down_Decode_DOP_ID_0;
  wire                decode_ctrls_1_down_DecoderPlugin_logic_NEED_RM_0;
  wire                decode_ctrls_1_down_DecoderPlugin_logic_NEED_FPU_0;
  wire       [4:0]    execute_ctrl4_down_RD_PHYS_lane0;
  wire                execute_ctrl4_down_lane0_integer_WriteBackPlugin_SEL_lane0;
  reg                 execute_ctrl4_up_RD_ENABLE_lane0;
  wire       [31:0]   execute_ctrl4_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0;
  wire       [31:0]   execute_ctrl4_lane0_integer_WriteBackPlugin_logic_DATA_lane0_bypass;
  reg        [31:0]   execute_ctrl4_up_lane0_integer_WriteBackPlugin_logic_DATA_lane0;
  wire       [15:0]   execute_ctrl3_down_Decode_UOP_ID_lane0;
  wire                execute_ctrl3_down_COMMIT_lane0;
  reg                 execute_ctrl3_up_RD_ENABLE_lane0;
  wire                execute_ctrl3_down_isReady;
  wire                execute_ctrl3_down_LANE_SEL_lane0;
  wire       [31:0]   execute_ctrl3_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0;
  wire       [31:0]   execute_ctrl3_lane0_integer_WriteBackPlugin_logic_DATA_lane0_bypass;
  reg        [31:0]   execute_ctrl3_up_lane0_integer_WriteBackPlugin_logic_DATA_lane0;
  wire                execute_ctrl2_down_LANE_SEL_lane0;
  wire       [31:0]   execute_ctrl2_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0;
  wire       [31:0]   execute_ctrl2_lane0_integer_WriteBackPlugin_logic_DATA_lane0_bypass;
  wire       [0:0]    execute_ctrl0_up_lane0_LAYER_SEL_lane0;
  wire                execute_ctrl0_up_COMPLETED_lane0;
  wire                execute_ctrl0_up_DispatchPlugin_logic_hcs_1_onRs_1_ENABLES_0_lane0;
  wire                execute_ctrl0_up_DispatchPlugin_logic_hcs_1_onRs_0_ENABLES_0_lane0;
  wire                execute_ctrl0_up_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_1_lane0;
  wire                execute_ctrl0_up_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_0_lane0;
  wire                execute_ctrl0_up_DispatchPlugin_logic_hcs_0_onRs_0_ENABLES_0_lane0;
  wire       [4:0]    execute_ctrl0_up_RD_PHYS_lane0;
  reg                 execute_ctrl0_up_RD_ENABLE_lane0;
  wire       [4:0]    execute_ctrl0_up_RS2_PHYS_lane0;
  wire                execute_ctrl0_up_RS2_ENABLE_lane0;
  wire       [4:0]    execute_ctrl0_up_RS1_PHYS_lane0;
  wire                execute_ctrl0_up_RS1_ENABLE_lane0;
  wire       [15:0]   execute_ctrl0_up_Decode_UOP_ID_lane0;
  wire                execute_ctrl0_up_TRAP_lane0;
  wire       [31:0]   execute_ctrl0_up_PC_lane0;
  wire                execute_ctrl0_up_DONT_FLUSH_PRECISE_4_lane0;
  wire                execute_ctrl0_up_DONT_FLUSH_PRECISE_3_lane0;
  wire                execute_ctrl0_up_DispatchPlugin_DONT_FLUSH_FROM_LANES_lane0;
  wire                execute_ctrl0_up_DispatchPlugin_DONT_FLUSH_lane0;
  reg                 execute_ctrl0_up_DispatchPlugin_MAY_FLUSH_lane0;
  wire                execute_ctrl0_up_DispatchPlugin_FENCE_OLDER_lane0;
  wire       [0:0]    execute_ctrl0_up_Prediction_ALIGNED_SLICES_BRANCH_lane0;
  wire       [0:0]    execute_ctrl0_up_Prediction_ALIGNED_SLICES_TAKEN_lane0;
  wire       [31:0]   execute_ctrl0_up_Prediction_ALIGNED_JUMPED_PC_lane0;
  wire                execute_ctrl0_up_Prediction_ALIGNED_JUMPED_lane0;
  wire       [31:0]   execute_ctrl0_up_Decode_UOP_lane0;
  wire                execute_ctrl0_up_LANE_SEL_lane0;
  wire                decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_1_ENABLES_0_0;
  wire                decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_0_ENABLES_0_0;
  wire                decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_1_0;
  wire                decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_0_0;
  wire                decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_0_ENABLES_0_0;
  wire                decode_ctrls_1_down_DONT_FLUSH_PRECISE_4_0;
  wire                decode_ctrls_1_down_DONT_FLUSH_PRECISE_3_0;
  wire                decode_ctrls_1_down_DispatchPlugin_DONT_FLUSH_FROM_LANES_0;
  wire                decode_ctrls_1_down_DispatchPlugin_DONT_FLUSH_0;
  wire                decode_ctrls_1_down_DispatchPlugin_MAY_FLUSH_0;
  wire                decode_ctrls_1_down_DispatchPlugin_FENCE_OLDER_0;
  wire       [0:0]    decode_ctrls_1_down_Prediction_ALIGNED_SLICES_BRANCH_0;
  wire       [0:0]    decode_ctrls_1_down_Prediction_ALIGNED_SLICES_TAKEN_0;
  wire       [31:0]   decode_ctrls_1_down_Prediction_ALIGNED_JUMPED_PC_0;
  wire                decode_ctrls_1_down_DispatchPlugin_logic_LANES_LAYER_HIT_1_0;
  wire                decode_ctrls_1_down_DispatchPlugin_logic_LANES_LAYER_HIT_0_0;
  wire                decode_ctrls_1_up_isValid;
  reg                 decode_ctrls_1_down_ready;
  wire                execute_ctrl2_down_MAY_FLUSH_PRECISE_3_lane0;
  wire                execute_ctrl1_down_MAY_FLUSH_PRECISE_4_lane0;
  wire                execute_ctrl1_down_MAY_FLUSH_PRECISE_3_lane0;
  wire                execute_ctrl2_down_BYPASSED_AT_3_lane0;
  reg        [4:0]    execute_ctrl2_up_RD_PHYS_lane0;
  reg                 execute_ctrl2_up_RD_ENABLE_lane0;
  wire                execute_ctrl1_down_BYPASSED_AT_2_lane0;
  reg        [4:0]    execute_ctrl1_up_RD_PHYS_lane0;
  reg                 execute_ctrl1_up_RD_ENABLE_lane0;
  wire       [31:0]   decode_ctrls_1_down_Decode_UOP_0;
  reg                 decode_ctrls_1_up_TRAP_0;
  reg                 decode_ctrls_1_TRAP_0_bypass;
  wire       [15:0]   decode_ctrls_1_down_Decode_UOP_ID_0;
  wire                decode_ctrls_1_up_isReady;
  wire                decode_ctrls_1_down_TRAP_0;
  wire       [31:0]   decode_ctrls_1_down_PC_0;
  wire                decode_ctrls_1_down_Prediction_ALIGN_REDO_0;
  wire                decode_ctrls_1_down_Prediction_ALIGNED_JUMPED_0;
  reg                 decode_ctrls_1_up_LANE_SEL_0;
  wire       [31:0]   decode_ctrls_1_down_Decode_INSTRUCTION_RAW_0;
  wire                decode_ctrls_1_down_Decode_DECOMPRESSION_FAULT_0;
  wire                decode_ctrls_1_down_Decode_LEGAL_0;
  wire       [4:0]    decode_ctrls_1_down_RD_PHYS_0;
  reg                 decode_ctrls_1_down_RD_ENABLE_0;
  wire       [4:0]    decode_ctrls_1_down_RS2_PHYS_0;
  wire                decode_ctrls_1_down_RS2_ENABLE_0;
  wire       [4:0]    decode_ctrls_1_down_RS1_PHYS_0;
  wire       [31:0]   decode_ctrls_1_down_Decode_INSTRUCTION_0;
  wire                decode_ctrls_1_down_RS1_ENABLE_0;
  wire                decode_ctrls_1_up_isCanceling;
  wire                decode_ctrls_1_up_ready;
  reg                 decode_ctrls_1_up_valid;
  wire                decode_ctrls_1_up_isMoving;
  wire       [31:0]   execute_ctrl4_down_early0_BranchPlugin_pcCalc_PC_LAST_SLICE_lane0;
  wire                execute_ctrl4_down_early0_BranchPlugin_SEL_lane0;
  wire                execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_IS_JALR_lane0;
  wire                execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_IS_JAL_lane0;
  wire                execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_MISSALIGNED_lane0;
  wire                execute_ctrl4_down_late0_BranchPlugin_SEL_lane0;
  wire                execute_ctrl4_down_Prediction_ALIGNED_JUMPED_lane0;
  wire       [31:0]   execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_btb_REAL_TARGET_lane0;
  wire       [31:0]   execute_ctrl4_down_early0_BranchPlugin_pcCalc_PC_FALSE_lane0;
  wire                execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_COND_lane0;
  wire       [31:0]   execute_ctrl4_down_Decode_UOP_lane0;
  wire                execute_ctrl4_down_late0_BranchPlugin_logic_alu_MSB_FAILED_lane0;
  wire       [1:0]    execute_ctrl4_down_BranchPlugin_BRANCH_CTRL_lane0;
  wire                execute_ctrl4_down_late0_BranchPlugin_logic_alu_btb_BAD_TARGET_lane0;
  wire       [31:0]   execute_ctrl4_down_early0_BranchPlugin_pcCalc_PC_TRUE_lane0;
  wire       [31:0]   execute_ctrl4_down_Prediction_ALIGNED_JUMPED_PC_lane0;
  wire                execute_ctrl4_down_late0_BranchPlugin_logic_alu_EQ_lane0;
  wire                execute_ctrl3_down_COMPLETION_AT_3_lane0;
  reg                 execute_ctrl3_up_COMPLETED_lane0;
  wire                execute_ctrl3_down_COMPLETED_lane0;
  wire                execute_ctrl3_COMPLETED_lane0_bypass;
  wire                execute_ctrl4_down_COMPLETION_AT_4_lane0;
  reg                 execute_ctrl4_up_COMPLETED_lane0;
  wire                execute_ctrl4_down_COMPLETED_lane0;
  wire                execute_ctrl4_COMPLETED_lane0_bypass;
  wire                execute_ctrl2_down_COMPLETION_AT_2_lane0;
  reg                 execute_ctrl2_up_COMPLETED_lane0;
  wire                execute_ctrl2_down_COMPLETED_lane0;
  wire                execute_ctrl2_COMPLETED_lane0_bypass;
  reg                 execute_ctrl1_up_LANE_SEL_lane0;
  wire                execute_ctrl2_down_LsuPlugin_logic_pmpPort_logic_NEED_HIT_lane0;
  wire                fetch_logic_ctrls_0_down_FetchL1Plugin_logic_pmpPort_logic_NEED_HIT;
  wire                execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_IS_JALR_lane0;
  wire                execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_IS_JAL_lane0;
  wire                execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_MISSALIGNED_lane0;
  wire                execute_ctrl2_down_early0_BranchPlugin_SEL_lane0;
  wire                execute_ctrl2_down_Prediction_ALIGNED_JUMPED_lane0;
  wire       [31:0]   execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_btb_REAL_TARGET_lane0;
  wire                execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_COND_lane0;
  wire                execute_ctrl2_down_early0_BranchPlugin_logic_alu_MSB_FAILED_lane0;
  wire                execute_ctrl2_down_early0_BranchPlugin_logic_alu_btb_BAD_TARGET_lane0;
  wire       [31:0]   execute_ctrl2_down_Prediction_ALIGNED_JUMPED_PC_lane0;
  wire                execute_ctrl2_down_early0_BranchPlugin_logic_alu_EQ_lane0;
  wire                execute_ctrl4_down_AguPlugin_FLOAT_lane0;
  wire       [31:0]   execute_ctrl4_down_PC_lane0;
  wire                execute_ctrl4_down_isReady;
  wire                execute_ctrl4_down_LANE_SEL_lane0;
  wire                execute_ctrl4_down_LsuPlugin_logic_MMU_FAILURE_lane0;
  reg                 execute_ctrl4_up_COMMIT_lane0;
  wire                execute_ctrl4_down_COMMIT_lane0;
  reg                 execute_ctrl4_COMMIT_lane0_bypass;
  reg                 execute_ctrl4_up_TRAP_lane0;
  wire                execute_ctrl4_down_TRAP_lane0;
  reg                 execute_ctrl4_TRAP_lane0_bypass;
  wire                execute_ctrl4_down_AguPlugin_SEL_lane0;
  wire                execute_ctrl4_down_LsuPlugin_logic_FROM_PREFETCH_lane0;
  wire                execute_ctrl4_down_LsuPlugin_logic_FENCE_lane0;
  wire                execute_ctrl4_down_LsuPlugin_logic_onTrigger_HIT_lane0;
  wire                execute_ctrl4_down_LsuPlugin_logic_preCtrl_MISS_ALIGNED_lane0;
  wire                execute_ctrl4_down_MMU_BYPASS_TRANSLATION_lane0;
  wire                execute_ctrl4_down_AguPlugin_STORE_lane0;
  wire                execute_ctrl4_down_LsuPlugin_logic_onPma_FROM_LSU_MSB_FAILED_lane0;
  wire                execute_ctrl4_down_MMU_HAZARD_lane0;
  wire                execute_ctrl4_down_MMU_REFILL_lane0;
  wire                execute_ctrl4_down_MMU_ACCESS_FAULT_lane0;
  wire                execute_ctrl4_down_LsuPlugin_logic_MMU_PAGE_FAULT_lane0;
  wire                execute_ctrl4_down_LsuPlugin_logic_onPma_IO_RSP_lane0_fault;
  wire                execute_ctrl4_down_LsuPlugin_logic_onPma_IO_RSP_lane0_io;
  wire                execute_ctrl4_down_LsuPlugin_logic_pmpPort_ACCESS_FAULT_lane0;
  wire                execute_ctrl4_down_LsuPlugin_logic_onPma_CACHED_RSP_lane0_fault;
  wire                execute_ctrl4_down_LsuPlugin_logic_onPma_CACHED_RSP_lane0_io;
  wire                execute_ctrl4_down_LsuPlugin_logic_onCtrl_SC_MISS_lane0;
  wire       [31:0]   execute_ctrl4_down_LsuPlugin_logic_onCtrl_loadData_RESULT_lane0;
  wire       [15:0]   execute_ctrl4_down_Decode_UOP_ID_lane0;
  wire       [1:0]    execute_ctrl4_down_LsuL1_SIZE_lane0;
  wire                execute_ctrl4_down_LsuPlugin_logic_onPma_IO_lane0;
  reg        [31:0]   execute_ctrl4_up_integer_RS2_lane0;
  wire                execute_ctrl3_down_MMU_HAZARD_lane0;
  wire                execute_ctrl3_down_MMU_REFILL_lane0;
  wire                execute_ctrl3_down_MMU_ACCESS_FAULT_lane0;
  wire                execute_ctrl3_down_LsuPlugin_logic_MMU_FAILURE_lane0;
  wire                execute_ctrl3_down_MMU_ALLOW_READ_lane0;
  wire                execute_ctrl3_down_MMU_ALLOW_WRITE_lane0;
  wire                execute_ctrl3_down_AguPlugin_STORE_lane0;
  wire                execute_ctrl3_down_MMU_PAGE_FAULT_lane0;
  wire                execute_ctrl3_down_LsuPlugin_logic_MMU_PAGE_FAULT_lane0;
  wire                execute_ctrl3_down_LsuPlugin_logic_onPma_FROM_LSU_MSB_FAILED_lane0;
  wire       [31:0]   execute_ctrl3_down_early0_SrcPlugin_ADD_SUB_lane0;
  wire                execute_ctrl3_down_LsuPlugin_logic_onPma_IO_lane0;
  wire                execute_ctrl3_down_LsuPlugin_logic_FROM_PREFETCH_lane0;
  wire                execute_ctrl3_down_LsuPlugin_logic_FENCE_lane0;
  wire                execute_ctrl3_down_LsuPlugin_logic_FROM_ACCESS_lane0;
  reg                 execute_ctrl3_down_LsuPlugin_logic_onPma_IO_RSP_lane0_fault;
  wire                execute_ctrl3_down_LsuPlugin_logic_onPma_IO_RSP_lane0_io;
  wire                execute_ctrl3_down_LsuPlugin_logic_onPma_CACHED_RSP_lane0_fault;
  wire                execute_ctrl3_down_LsuPlugin_logic_onPma_CACHED_RSP_lane0_io;
  wire                execute_ctrl3_down_LsuPlugin_logic_preCtrl_IS_AMO_lane0;
  wire                execute_ctrl3_down_LsuL1_ATOMIC_lane0;
  wire                execute_ctrl3_down_AguPlugin_SEL_lane0;
  wire                execute_ctrl3_down_LsuPlugin_logic_preCtrl_MISS_ALIGNED_lane0;
  reg                 execute_ctrl4_LsuL1_SEL_lane0_bypass;
  wire                execute_ctrl4_down_LsuPlugin_logic_FROM_LSU_lane0;
  reg                 execute_ctrl4_up_LsuL1_SEL_lane0;
  reg                 execute_ctrl3_LsuL1_SEL_lane0_bypass;
  wire                execute_ctrl3_down_LsuPlugin_logic_FROM_LSU_lane0;
  reg                 execute_ctrl3_up_LsuL1_SEL_lane0;
  wire       [31:0]   execute_ctrl3_down_MMU_TRANSLATED_lane0;
  wire                execute_ctrl2_down_LsuPlugin_logic_FROM_PREFETCH_lane0;
  wire                execute_ctrl2_down_LsuPlugin_logic_FROM_LSU_lane0;
  wire       [11:0]   execute_ctrl2_down_Decode_STORE_ID_lane0;
  wire                execute_ctrl2_down_LsuL1_FLUSH_lane0;
  wire                execute_ctrl2_down_LsuL1_PREFETCH_lane0;
  wire                execute_ctrl2_down_LsuL1_INVALID_lane0;
  wire                execute_ctrl2_down_LsuL1_CLEAN_lane0;
  wire                execute_ctrl2_down_LsuL1_STORE_lane0;
  wire                execute_ctrl2_down_LsuL1_ATOMIC_lane0;
  wire                execute_ctrl2_down_LsuL1_LOAD_lane0;
  wire       [1:0]    execute_ctrl2_down_LsuL1_SIZE_lane0;
  wire       [3:0]    execute_ctrl2_down_LsuL1_MASK_lane0;
  wire                execute_ctrl2_down_LsuL1_SEL_lane0;
  wire                execute_ctrl2_down_AguPlugin_ATOMIC_lane0;
  wire                execute_ctrl2_down_AguPlugin_STORE_lane0;
  wire                execute_ctrl2_down_AguPlugin_LOAD_lane0;
  wire       [1:0]    execute_ctrl2_down_AguPlugin_SIZE_lane0;
  wire                execute_ctrl2_down_AguPlugin_SEL_lane0;
  wire                execute_ctrl2_down_LsuPlugin_logic_FROM_WB_lane0;
  wire                execute_ctrl2_down_LsuPlugin_logic_FROM_ACCESS_lane0;
  wire                execute_ctrl2_down_LsuPlugin_logic_FORCE_PHYSICAL_lane0;
  wire                execute_ctrl3_down_LsuPlugin_logic_onTrigger_HIT_lane0;
  wire       [1:0]    execute_ctrl3_down_LsuL1_SIZE_lane0;
  wire                execute_ctrl3_down_LsuL1_STORE_lane0;
  wire                execute_ctrl3_down_LsuL1_LOAD_lane0;
  wire                execute_ctrl3_down_LsuL1_FLUSH_lane0;
  wire                execute_ctrl3_down_LsuL1_SEL_lane0;
  wire       [31:0]   execute_ctrl0_down_Decode_UOP_lane0;
  wire                decode_ctrls_0_up_isValid;
  wire                decode_ctrls_0_up_valid;
  wire                decode_ctrls_0_up_Prediction_ALIGN_REDO_0;
  wire       [0:0]    decode_ctrls_0_up_Prediction_ALIGNED_SLICES_TAKEN_0;
  wire       [0:0]    decode_ctrls_0_up_Prediction_ALIGNED_SLICES_BRANCH_0;
  wire       [31:0]   decode_ctrls_0_up_Prediction_ALIGNED_JUMPED_PC_0;
  wire                decode_ctrls_0_up_Prediction_ALIGNED_JUMPED_0;
  wire                decode_ctrls_0_up_TRAP_0;
  wire                decode_ctrls_0_up_Prediction_WORD_JUMPED_0;
  wire       [31:0]   decode_ctrls_0_up_Prediction_WORD_JUMP_PC_0;
  wire       [0:0]    decode_ctrls_0_up_Prediction_WORD_SLICES_TAKEN_0;
  wire       [0:0]    decode_ctrls_0_up_Prediction_WORD_SLICES_BRANCH_0;
  wire       [9:0]    decode_ctrls_0_up_Fetch_ID_0;
  wire       [9:0]    decode_ctrls_0_up_Decode_DOP_ID_0;
  wire       [31:0]   decode_ctrls_0_up_PC_0;
  reg        [31:0]   decode_ctrls_0_up_Decode_INSTRUCTION_RAW_0;
  wire                decode_ctrls_0_up_Decode_DECOMPRESSION_FAULT_0;
  wire       [31:0]   decode_ctrls_0_up_Decode_INSTRUCTION_0;
  wire                decode_ctrls_0_up_isFiring;
  wire       [0:0]    fetch_logic_ctrls_2_down_AlignerPlugin_logic_FETCH_LAST;
  wire                fetch_logic_ctrls_2_down_Prediction_WORD_JUMPED;
  wire       [0:0]    fetch_logic_ctrls_2_down_AlignerPlugin_logic_FETCH_MASK;
  (* keep , syn_keep *) wire       [31:0]   execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_LAST_SLICE_lane0 /* synthesis syn_keep = 1 */ ;
  (* keep , syn_keep *) wire       [31:0]   execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_FALSE_lane0 /* synthesis syn_keep = 1 */ ;
  (* keep , syn_keep *) reg        [31:0]   execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_TRUE_lane0 /* synthesis syn_keep = 1 */ ;
  wire       [1:0]    execute_ctrl2_down_BranchPlugin_BRANCH_CTRL_lane0;
  wire                execute_ctrl2_up_COMMIT_lane0;
  wire                execute_ctrl2_down_COMMIT_lane0;
  reg                 execute_ctrl2_COMMIT_lane0_bypass;
  reg                 execute_ctrl2_up_TRAP_lane0;
  wire                execute_ctrl2_down_TRAP_lane0;
  reg                 execute_ctrl2_TRAP_lane0_bypass;
  wire                execute_ctrl2_down_early0_EnvPlugin_SEL_lane0;
  wire       [31:0]   execute_ctrl2_down_Decode_UOP_lane0;
  wire                execute_ctrl4_down_SrcStageables_UNSIGNED_lane0;
  wire                execute_ctrl4_down_SrcStageables_ZERO_lane0;
  wire                execute_ctrl4_down_SrcStageables_REVERT_lane0;
  wire       [31:0]   execute_ctrl3_down_PC_lane0;
  wire       [31:0]   execute_ctrl3_down_integer_RS2_lane0;
  wire       [1:0]    execute_ctrl3_down_late0_SrcPlugin_logic_SRC2_CTRL_lane0;
  wire       [31:0]   execute_ctrl3_down_late0_SrcPlugin_SRC2_lane0;
  wire       [31:0]   execute_ctrl3_down_integer_RS1_lane0;
  wire       [0:0]    execute_ctrl3_down_late0_SrcPlugin_logic_SRC1_CTRL_lane0;
  wire       [31:0]   execute_ctrl3_down_late0_SrcPlugin_SRC1_lane0;
  wire       [31:0]   execute_ctrl3_down_Decode_UOP_lane0;
  reg                 execute_ctrl3_up_LANE_SEL_lane0;
  wire       [1:0]    execute_ctrl4_down_lane0_IntFormatPlugin_logic_WIDTH_ID_lane0;
  wire                execute_ctrl4_down_lane0_IntFormatPlugin_logic_SIGNED_lane0;
  reg                 execute_ctrl4_up_LANE_SEL_lane0;
  wire                execute_ctrl2_down_SrcStageables_UNSIGNED_lane0;
  wire                execute_ctrl2_down_SrcStageables_ZERO_lane0;
  wire                execute_ctrl2_down_SrcStageables_REVERT_lane0;
  wire       [31:0]   execute_ctrl1_down_PC_lane0;
  wire       [31:0]   execute_ctrl1_down_integer_RS2_lane0;
  wire       [1:0]    execute_ctrl1_down_early0_SrcPlugin_logic_SRC2_CTRL_lane0;
  wire       [31:0]   execute_ctrl1_down_early0_SrcPlugin_SRC2_lane0;
  wire       [31:0]   execute_ctrl1_down_integer_RS1_lane0;
  wire       [0:0]    execute_ctrl1_down_early0_SrcPlugin_logic_SRC1_CTRL_lane0;
  wire       [31:0]   execute_ctrl1_down_early0_SrcPlugin_SRC1_lane0;
  wire       [31:0]   execute_ctrl1_down_Decode_UOP_lane0;
  wire       [2:0]    execute_ctrl2_down_early0_EnvPlugin_OP_lane0;
  wire       [31:0]   execute_ctrl2_down_PC_lane0;
  wire       [15:0]   execute_ctrl2_down_Decode_UOP_ID_lane0;
  wire                decode_ctrls_1_lane0_upIsCancel;
  wire                decode_ctrls_1_lane0_downIsCancel;
  wire       [9:0]    decode_ctrls_0_down_Decode_DOP_ID_0;
  wire       [9:0]    decode_ctrls_0_down_Fetch_ID_0;
  wire       [31:0]   decode_ctrls_0_down_PC_0;
  wire                decode_ctrls_0_up_isReady;
  wire                decode_ctrls_0_up_LANE_SEL_0;
  wire                decode_ctrls_0_lane0_upIsCancel;
  wire                decode_ctrls_0_lane0_downIsCancel;
  wire       [9:0]    fetch_logic_ctrls_0_down_Fetch_ID;
  wire       [1:0]    execute_ctrl0_down_AguPlugin_SIZE_lane0;
  wire                fetch_logic_ctrls_2_up_isCanceling;
  wire                fetch_logic_ctrls_2_down_isReady;
  wire                fetch_logic_ctrls_2_down_TRAP;
  wire                fetch_logic_ctrls_2_down_MMU_BYPASS_TRANSLATION;
  wire                fetch_logic_ctrls_2_down_Fetch_PC_FAULT;
  wire                fetch_logic_ctrls_2_down_MMU_HAZARD;
  wire                fetch_logic_ctrls_2_down_MMU_REFILL;
  wire                fetch_logic_ctrls_2_down_MMU_ACCESS_FAULT;
  wire                fetch_logic_ctrls_2_down_MMU_ALLOW_EXECUTE;
  wire                fetch_logic_ctrls_2_down_MMU_PAGE_FAULT;
  wire                fetch_logic_ctrls_2_down_FetchL1Plugin_logic_pmpPort_ACCESS_FAULT;
  wire                fetch_logic_ctrls_2_down_FetchL1Plugin_logic_WAYS_HIT;
  wire                fetch_logic_ctrls_2_up_isCancel;
  wire                fetch_logic_ctrls_2_down_FetchL1Plugin_logic_HAZARD;
  wire                fetch_logic_ctrls_2_down_FetchL1Plugin_logic_WAYS_TAGS_0_loaded;
  wire                fetch_logic_ctrls_2_down_FetchL1Plugin_logic_WAYS_TAGS_0_error;
  wire       [21:0]   fetch_logic_ctrls_2_down_FetchL1Plugin_logic_WAYS_TAGS_0_address;
  wire       [31:0]   fetch_logic_ctrls_2_down_Fetch_WORD_PC;
  wire                fetch_logic_ctrls_2_up_isReady;
  wire                fetch_logic_ctrls_2_up_isValid;
  wire       [31:0]   fetch_logic_ctrls_2_down_MMU_TRANSLATED;
  wire                fetch_logic_ctrls_1_down_FetchL1Plugin_logic_WAYS_HIT;
  wire       [31:0]   fetch_logic_ctrls_1_down_MMU_TRANSLATED;
  wire                fetch_logic_ctrls_1_down_FetchL1Plugin_logic_WAYS_HITS_0;
  wire       [3:0]    fetch_logic_ctrls_1_down_FetchL1Plugin_logic_cmd_TAGS_UPDATE_ADDRESS;
  wire                fetch_logic_ctrls_1_down_FetchL1Plugin_logic_cmd_TAGS_UPDATE;
  wire                fetch_logic_ctrls_1_down_FetchL1Plugin_logic_HAZARD;
  wire       [31:0]   fetch_logic_ctrls_2_down_FetchL1Plugin_logic_BANKS_MUXES_0;
  wire                fetch_logic_ctrls_2_down_FetchL1Plugin_logic_WAYS_HITS_0;
  wire       [31:0]   fetch_logic_ctrls_2_down_Fetch_WORD;
  wire       [31:0]   fetch_logic_ctrls_1_down_Fetch_WORD_PC;
  wire       [31:0]   fetch_logic_ctrls_1_down_FetchL1Plugin_logic_BANKS_MUXES_0;
  wire                fetch_logic_ctrls_1_down_FetchL1Plugin_logic_cmd_PLRU_BYPASS_VALID;
  wire       [3:0]    fetch_logic_ctrls_0_down_FetchL1Plugin_logic_cmd_TAGS_UPDATE_ADDRESS;
  wire                fetch_logic_ctrls_0_down_FetchL1Plugin_logic_cmd_TAGS_UPDATE;
  wire                fetch_logic_ctrls_0_down_FetchL1Plugin_logic_cmd_PLRU_BYPASS_VALID;
  reg                 fetch_logic_ctrls_1_up_valid;
  wire                fetch_logic_ctrls_1_up_ready;
  wire       [31:0]   fetch_logic_ctrls_0_down_Fetch_WORD_PC;
  reg                 _zz_fetch_logic_ctrls_0_haltRequest_FetchL1Plugin_l217;
  wire                fetch_logic_ctrls_1_down_FetchL1Plugin_logic_WAYS_TAGS_0_loaded;
  wire                fetch_logic_ctrls_1_down_FetchL1Plugin_logic_WAYS_TAGS_0_error;
  wire       [21:0]   fetch_logic_ctrls_1_down_FetchL1Plugin_logic_WAYS_TAGS_0_address;
  wire       [31:0]   fetch_logic_ctrls_1_down_FetchL1Plugin_logic_BANKS_WORDS_0;
  reg                 _zz_2;
  wire                fetch_logic_ctrls_0_down_isFiring;
  wire                execute_ctrl4_down_late0_BarrelShifterPlugin_SEL_lane0;
  wire       [31:0]   execute_ctrl4_down_late0_BarrelShifterPlugin_SHIFT_RESULT_lane0;
  wire                execute_ctrl4_down_BarrelShifterPlugin_SIGNED_lane0;
  wire                execute_ctrl4_down_BarrelShifterPlugin_LEFT_lane0;
  wire                execute_ctrl4_down_late0_IntAluPlugin_SEL_lane0;
  wire       [31:0]   execute_ctrl4_down_late0_IntAluPlugin_ALU_RESULT_lane0;
  wire                execute_ctrl4_down_late0_IntAluPlugin_ALU_SLTX_lane0;
  wire                execute_ctrl4_down_late0_SrcPlugin_LESS_lane0;
  wire                execute_ctrl4_down_late0_IntAluPlugin_ALU_ADD_SUB_lane0;
  wire       [31:0]   execute_ctrl4_down_late0_SrcPlugin_ADD_SUB_lane0;
  wire       [31:0]   execute_ctrl4_down_late0_SrcPlugin_SRC2_lane0;
  wire       [31:0]   execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0;
  wire       [1:0]    execute_ctrl4_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0;
  wire       [31:0]   execute_ctrl3_down_DivPlugin_DIV_RESULT_lane0;
  wire                execute_ctrl3_down_early0_DivPlugin_SEL_lane0;
  wire       [31:0]   execute_ctrl2_down_DivPlugin_DIV_RESULT_lane0;
  wire                execute_ctrl2_down_early0_DivPlugin_SEL_lane0;
  reg                 execute_ctrl2_up_LANE_SEL_lane0;
  wire                execute_ctrl2_down_isReady;
  wire                execute_ctrl2_down_DivPlugin_REM_lane0;
  wire       [31:0]   execute_ctrl2_down_RsUnsignedPlugin_RS2_UNSIGNED_lane0;
  wire       [31:0]   execute_ctrl2_down_RsUnsignedPlugin_RS1_UNSIGNED_lane0;
  wire                execute_ctrl2_down_RsUnsignedPlugin_RS2_REVERT_lane0;
  wire                execute_ctrl2_down_RsUnsignedPlugin_RS1_REVERT_lane0;
  wire       [31:0]   execute_ctrl2_down_RsUnsignedPlugin_RS2_FORMATED_lane0;
  wire       [31:0]   execute_ctrl2_down_RsUnsignedPlugin_RS1_FORMATED_lane0;
  wire                execute_ctrl4_down_MulPlugin_HIGH_lane0;
  wire                execute_ctrl4_down_early0_MulPlugin_SEL_lane0;
  wire       [65:0]   execute_ctrl4_down_early0_MulPlugin_logic_steps_1_adders_0_lane0;
  wire       [4:0]    execute_ctrl4_down_early0_MulPlugin_logic_steps_0_adders_1_lane0;
  wire       [62:0]   execute_ctrl4_down_early0_MulPlugin_logic_steps_0_adders_0_lane0;
  wire       [29:0]   execute_ctrl4_down_early0_MulPlugin_logic_mul_VALUES_3_lane0;
  wire       [46:0]   execute_ctrl4_down_early0_MulPlugin_logic_mul_VALUES_2_lane0;
  wire       [46:0]   execute_ctrl4_down_early0_MulPlugin_logic_mul_VALUES_1_lane0;
  wire       [33:0]   execute_ctrl4_down_early0_MulPlugin_logic_mul_VALUES_0_lane0;
  wire       [4:0]    execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0;
  wire       [62:0]   execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0;
  wire       [29:0]   execute_ctrl3_down_early0_MulPlugin_logic_mul_VALUES_3_lane0;
  wire       [46:0]   execute_ctrl3_down_early0_MulPlugin_logic_mul_VALUES_2_lane0;
  wire       [46:0]   execute_ctrl3_down_early0_MulPlugin_logic_mul_VALUES_1_lane0;
  wire       [33:0]   execute_ctrl3_down_early0_MulPlugin_logic_mul_VALUES_0_lane0;
  wire       [29:0]   execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_3_lane0;
  wire       [46:0]   execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_2_lane0;
  wire       [46:0]   execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_1_lane0;
  wire       [33:0]   execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_0_lane0;
  wire                execute_ctrl2_down_RsUnsignedPlugin_RS2_SIGNED_lane0;
  wire       [32:0]   execute_ctrl2_down_MUL_SRC2_lane0;
  wire                execute_ctrl2_down_RsUnsignedPlugin_RS1_SIGNED_lane0;
  wire       [32:0]   execute_ctrl2_down_MUL_SRC1_lane0;
  reg        [31:0]   execute_ctrl2_up_integer_RS2_lane0;
  reg        [31:0]   execute_ctrl2_up_integer_RS1_lane0;
  wire       [31:0]   execute_ctrl4_down_LsuL1_READ_DATA_lane0;
  wire       [31:0]   execute_ctrl4_down_LsuL1Plugin_logic_BYPASSED_DATA_lane0;
  wire       [31:0]   execute_ctrl2_down_LsuL1Plugin_logic_EVENT_WRITE_DATA_lane0;
  wire                execute_ctrl4_down_LsuL1_FLUSH_HIT_lane0;
  wire       [3:0]    execute_ctrl4_down_LsuL1_MASK_lane0;
  wire       [31:0]   execute_ctrl4_down_LsuL1_WRITE_DATA_lane0;
  wire       [31:0]   execute_ctrl4_down_LsuL1_MIXED_ADDRESS_lane0;
  wire       [0:0]    execute_ctrl4_down_LsuL1_WAIT_WRITEBACK_lane0;
  wire       [0:0]    execute_ctrl4_down_LsuL1_WAIT_REFILL_lane0;
  wire                execute_ctrl4_down_LsuL1_SKIP_WRITE_lane0;
  wire                execute_ctrl4_down_LsuL1_SEL_lane0;
  wire                execute_ctrl4_down_LsuL1_INVALID_lane0;
  wire                execute_ctrl4_down_LsuL1_CLEAN_lane0;
  wire                execute_ctrl4_down_LsuL1_REFILL_HIT_lane0;
  wire                execute_ctrl4_down_LsuL1_MISS_UNIQUE_lane0;
  wire                execute_ctrl4_down_LsuL1_FAULT_lane0;
  wire                execute_ctrl4_down_LsuL1_MISS_lane0;
  wire                execute_ctrl4_down_LsuL1_FLUSH_HAZARD_lane0;
  wire                execute_ctrl4_down_LsuL1_HAZARD_lane0;
  wire                execute_ctrl4_down_LsuL1Plugin_logic_HAZARD_FORCED_lane0;
  wire                execute_ctrl4_down_LsuL1_FLUSH_lane0;
  wire                execute_ctrl4_down_LsuL1_ABORD_lane0;
  wire                execute_ctrl4_down_LsuL1_PREFETCH_lane0;
  wire                execute_ctrl4_down_LsuL1_LOAD_lane0;
  wire       [0:0]    execute_ctrl4_down_LsuL1Plugin_logic_BANK_BUSY_REMAPPED_lane0;
  wire       [1:0]    execute_ctrl4_down_LsuL1Plugin_logic_WRITE_TO_READ_HAZARDS_lane0;
  wire       [31:0]   execute_ctrl4_down_LsuL1_PHYSICAL_ADDRESS_lane0;
  wire                execute_ctrl4_down_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_loaded;
  wire       [21:0]   execute_ctrl4_down_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_address;
  wire                execute_ctrl4_down_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_fault;
  wire       [0:0]    execute_ctrl4_down_LsuL1Plugin_logic_SHARED_lane0_dirty;
  wire                execute_ctrl4_down_LsuL1_ATOMIC_lane0;
  wire                execute_ctrl4_down_LsuL1_STORE_lane0;
  wire                execute_ctrl4_down_LsuL1Plugin_logic_NEED_UNIQUE_lane0;
  wire                execute_ctrl4_down_LsuL1Plugin_logic_WAYS_HIT_lane0;
  wire       [0:0]    execute_ctrl3_down_LsuL1Plugin_logic_WAYS_HITS_lane0;
  wire       [0:0]    execute_ctrl3_down_LsuL1Plugin_logic_SHARED_lane0_dirty;
  wire       [0:0]    execute_ctrl3_LsuL1Plugin_logic_SHARED_lane0_bypass_dirty;
  wire       [0:0]    execute_ctrl3_down_LsuL1Plugin_logic_lsu_rt0_SHARED_BYPASS_VALUE_lane0_dirty;
  wire                execute_ctrl3_down_LsuL1Plugin_logic_lsu_rt0_SHARED_BYPASS_VALID_lane0;
  wire                execute_ctrl3_down_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_loaded;
  wire       [21:0]   execute_ctrl3_down_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_address;
  wire                execute_ctrl3_down_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_fault;
  reg        [0:0]    execute_ctrl3_up_LsuL1Plugin_logic_SHARED_lane0_dirty;
  wire       [0:0]    execute_ctrl2_down_LsuL1Plugin_logic_lsu_rt0_SHARED_BYPASS_VALUE_lane0_dirty;
  wire                execute_ctrl2_down_LsuL1Plugin_logic_lsu_rt0_SHARED_BYPASS_VALID_lane0;
  wire       [3:0]    execute_ctrl3_down_LsuL1Plugin_logic_EVENT_WRITE_MASK_lane0;
  wire       [31:0]   execute_ctrl3_down_LsuL1Plugin_logic_EVENT_WRITE_ADDRESS_lane0;
  wire                execute_ctrl3_down_LsuL1Plugin_logic_EVENT_WRITE_VALID_lane0;
  wire       [3:0]    execute_ctrl3_down_LsuL1_MASK_lane0;
  wire       [3:0]    execute_ctrl2_down_LsuL1Plugin_logic_EVENT_WRITE_MASK_lane0;
  wire       [31:0]   execute_ctrl3_down_LsuL1_PHYSICAL_ADDRESS_lane0;
  wire       [31:0]   execute_ctrl2_down_LsuL1Plugin_logic_EVENT_WRITE_ADDRESS_lane0;
  wire                execute_ctrl2_down_LsuL1Plugin_logic_EVENT_WRITE_VALID_lane0;
  reg        [1:0]    execute_ctrl3_down_LsuL1Plugin_logic_WRITE_TO_READ_HAZARDS_lane0;
  wire       [31:0]   execute_ctrl4_down_LsuL1Plugin_logic_BANKS_MUXES_lane0_0;
  wire       [0:0]    execute_ctrl4_down_LsuL1Plugin_logic_WAYS_HITS_lane0;
  wire       [31:0]   execute_ctrl4_down_LsuL1Plugin_logic_MUXED_DATA_lane0;
  wire       [31:0]   execute_ctrl3_down_LsuL1_MIXED_ADDRESS_lane0;
  wire       [31:0]   execute_ctrl3_down_LsuL1Plugin_logic_BANKS_MUXES_lane0_0;
  wire       [0:0]    execute_ctrl3_down_LsuL1Plugin_logic_BANK_BUSY_lane0;
  wire       [0:0]    execute_ctrl3_down_LsuL1Plugin_logic_BANK_BUSY_REMAPPED_lane0;
  wire       [31:0]   execute_ctrl3_down_LsuL1Plugin_logic_BANKS_WORDS_lane0_0;
  wire       [0:0]    execute_ctrl2_down_LsuL1Plugin_logic_BANK_BUSY_lane0;
  wire       [31:0]   execute_ctrl2_down_LsuL1_MIXED_ADDRESS_lane0;
  reg                 _zz_3;
  reg                 _zz_4;
  wire                execute_ctrl2_down_early0_BarrelShifterPlugin_SEL_lane0;
  wire       [31:0]   execute_ctrl2_down_early0_BarrelShifterPlugin_SHIFT_RESULT_lane0;
  wire                execute_ctrl2_down_BarrelShifterPlugin_SIGNED_lane0;
  wire                execute_ctrl2_down_BarrelShifterPlugin_LEFT_lane0;
  wire                execute_ctrl2_down_early0_IntAluPlugin_SEL_lane0;
  wire       [31:0]   execute_ctrl2_down_early0_IntAluPlugin_ALU_RESULT_lane0;
  wire                execute_ctrl2_down_early0_IntAluPlugin_ALU_SLTX_lane0;
  wire                execute_ctrl2_down_early0_SrcPlugin_LESS_lane0;
  wire                execute_ctrl2_down_early0_IntAluPlugin_ALU_ADD_SUB_lane0;
  wire       [31:0]   execute_ctrl2_down_early0_SrcPlugin_ADD_SUB_lane0;
  wire       [31:0]   execute_ctrl2_down_early0_SrcPlugin_SRC2_lane0;
  wire       [31:0]   execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0;
  wire       [1:0]    execute_ctrl2_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0;
  wire                AlignerPlugin_api_singleFetch;
  wire                AlignerPlugin_api_downMoving;
  wire                AlignerPlugin_api_haltIt;
  reg                 DispatchPlugin_api_haltDispatch;
  wire                execute_freeze_valid;
  wire       [0:0]    execute_lane0_api_hartsInflight;
  wire                execute_lane0_ctrls_2_upIsCancel;
  wire                execute_lane0_ctrls_2_downIsCancel;
  wire                CsrRamPlugin_api_holdRead;
  wire                CsrRamPlugin_api_holdWrite;
  reg                 CsrAccessPlugin_bus_decode_exception;
  wire                CsrAccessPlugin_bus_decode_read;
  wire                CsrAccessPlugin_bus_decode_write;
  wire       [11:0]   CsrAccessPlugin_bus_decode_address;
  reg                 CsrAccessPlugin_bus_decode_trap;
  wire                PrivilegedPlugin_api_lsuTriggerBus_load;
  wire                PrivilegedPlugin_api_lsuTriggerBus_store;
  wire       [31:0]   PrivilegedPlugin_api_lsuTriggerBus_virtual;
  wire       [1:0]    PrivilegedPlugin_api_lsuTriggerBus_size;
  wire                PrivilegedPlugin_api_harts_0_allowInterrupts;
  wire                PrivilegedPlugin_api_harts_0_allowException;
  wire                PrivilegedPlugin_api_harts_0_allowEbreakException;
  wire                PrivilegedPlugin_api_harts_0_fpuEnable;
  reg                 TrapPlugin_api_harts_0_redo;
  reg                 TrapPlugin_api_harts_0_askWake;
  reg                 TrapPlugin_api_harts_0_rvTrap;
  wire                TrapPlugin_api_harts_0_fsmBusy;
  wire                BtbPlugin_logic_pcPort_valid;
  wire                BtbPlugin_logic_pcPort_payload_fault;
  wire       [31:0]   BtbPlugin_logic_pcPort_payload_pc;
  wire                PcPlugin_logic_harts_0_aggregator_sortedByPriority_3_laneValid;
  wire                BtbPlugin_logic_flushPort_valid;
  wire                BtbPlugin_logic_flushPort_payload_self;
  wire                FetchL1Plugin_logic_bus_cmd_valid;
  wire                FetchL1Plugin_logic_bus_cmd_ready;
  wire       [31:0]   FetchL1Plugin_logic_bus_cmd_payload_address;
  wire                FetchL1Plugin_logic_bus_cmd_payload_io;
  wire                FetchL1Plugin_logic_bus_rsp_valid;
  wire                FetchL1Plugin_logic_bus_rsp_ready;
  wire       [31:0]   FetchL1Plugin_logic_bus_rsp_payload_data;
  wire                FetchL1Plugin_logic_bus_rsp_payload_error;
  reg                 FetchL1Plugin_logic_trapPort_valid;
  reg                 FetchL1Plugin_logic_trapPort_payload_exception;
  wire       [31:0]   FetchL1Plugin_logic_trapPort_payload_tval;
  wire       [0:0]    decode_logic_trapPending;
  wire       [0:0]    DispatchPlugin_logic_trapPendings;
  wire       [0:0]    execute_lane0_logic_trapPending;
  wire                early0_IntAluPlugin_logic_wb_valid;
  wire       [31:0]   early0_IntAluPlugin_logic_wb_payload;
  (* keep , syn_keep *) reg        [31:0]   early0_IntAluPlugin_logic_alu_bitwise /* synthesis syn_keep = 1 */ ;
  wire       [31:0]   early0_IntAluPlugin_logic_alu_result;
  wire                early0_BarrelShifterPlugin_logic_wb_valid;
  wire       [31:0]   early0_BarrelShifterPlugin_logic_wb_payload;
  wire       [4:0]    early0_BarrelShifterPlugin_logic_shift_amplitude;
  wire       [31:0]   early0_BarrelShifterPlugin_logic_shift_reversed;
  wire       [31:0]   early0_BarrelShifterPlugin_logic_shift_shifted;
  wire       [31:0]   early0_BarrelShifterPlugin_logic_shift_patched;
  wire                early0_BranchPlugin_logic_wb_valid;
  wire       [31:0]   early0_BranchPlugin_logic_wb_payload;
  wire                early0_BranchPlugin_logic_pcPort_valid;
  wire                early0_BranchPlugin_logic_pcPort_payload_fault;
  wire       [31:0]   early0_BranchPlugin_logic_pcPort_payload_pc;
  wire                PcPlugin_logic_harts_0_aggregator_sortedByPriority_2_laneValid;
  wire                early0_BranchPlugin_logic_flushPort_valid;
  reg                 LsuPlugin_logic_trapPort_valid;
  reg                 LsuPlugin_logic_trapPort_payload_exception;
  wire       [31:0]   LsuPlugin_logic_trapPort_payload_tval;
  wire                LsuL1_lockPort_valid;
  wire       [31:0]   LsuL1_lockPort_address;
  reg                 LsuL1_ackUnlock;
  wire                LsuL1Plugin_logic_bus_read_cmd_valid;
  wire                LsuL1Plugin_logic_bus_read_cmd_ready;
  wire       [31:0]   LsuL1Plugin_logic_bus_read_cmd_payload_address;
  wire                LsuL1Plugin_logic_bus_read_rsp_valid;
  wire                LsuL1Plugin_logic_bus_read_rsp_ready;
  wire       [31:0]   LsuL1Plugin_logic_bus_read_rsp_payload_data;
  wire                LsuL1Plugin_logic_bus_read_rsp_payload_error;
  wire                LsuL1Plugin_logic_bus_write_cmd_valid;
  wire                LsuL1Plugin_logic_bus_write_cmd_ready;
  wire                LsuL1Plugin_logic_bus_write_cmd_payload_last;
  wire       [31:0]   LsuL1Plugin_logic_bus_write_cmd_payload_fragment_address;
  wire       [31:0]   LsuL1Plugin_logic_bus_write_cmd_payload_fragment_data;
  wire                LsuL1Plugin_logic_bus_write_rsp_valid;
  wire                LsuL1Plugin_logic_bus_write_rsp_payload_error;
  reg        [0:0]    LsuL1Plugin_logic_refillCompletions;
  wire                LsuL1Plugin_logic_writebackBusy;
  reg        [0:0]    LsuL1Plugin_logic_banksWrite_mask;
  reg        [7:0]    LsuL1Plugin_logic_banksWrite_address;
  reg        [31:0]   LsuL1Plugin_logic_banksWrite_writeData;
  reg        [3:0]    LsuL1Plugin_logic_banksWrite_writeMask;
  reg        [0:0]    LsuL1Plugin_logic_waysWrite_mask;
  reg        [3:0]    LsuL1Plugin_logic_waysWrite_address;
  reg                 LsuL1Plugin_logic_waysWrite_tag_loaded;
  reg        [21:0]   LsuL1Plugin_logic_waysWrite_tag_address;
  reg                 LsuL1Plugin_logic_waysWrite_tag_fault;
  wire                LsuL1Plugin_logic_waysWrite_valid;
  wire                LsuL1Plugin_logic_banks_0_usedByWriteback;
  wire                LsuL1Plugin_logic_banks_0_write_valid;
  wire       [7:0]    LsuL1Plugin_logic_banks_0_write_payload_address;
  wire       [31:0]   LsuL1Plugin_logic_banks_0_write_payload_data;
  wire       [3:0]    LsuL1Plugin_logic_banks_0_write_payload_mask;
  reg                 LsuL1Plugin_logic_banks_0_read_cmd_valid;
  reg        [7:0]    LsuL1Plugin_logic_banks_0_read_cmd_payload;
  (* keep , syn_keep *) wire       [31:0]   LsuL1Plugin_logic_banks_0_read_rsp /* synthesis syn_keep = 1 */ ;
  wire                LsuL1Plugin_logic_ways_0_lsuRead_cmd_valid;
  wire       [3:0]    LsuL1Plugin_logic_ways_0_lsuRead_cmd_payload;
  (* keep , syn_keep *) wire                LsuL1Plugin_logic_ways_0_lsuRead_rsp_loaded /* synthesis syn_keep = 1 */ ;
  (* keep , syn_keep *) wire       [21:0]   LsuL1Plugin_logic_ways_0_lsuRead_rsp_address /* synthesis syn_keep = 1 */ ;
  (* keep , syn_keep *) wire                LsuL1Plugin_logic_ways_0_lsuRead_rsp_fault /* synthesis syn_keep = 1 */ ;
  wire       [23:0]   _zz_LsuL1Plugin_logic_ways_0_lsuRead_rsp_loaded;
  reg                 LsuL1Plugin_logic_shared_write_valid;
  reg        [3:0]    LsuL1Plugin_logic_shared_write_payload_address;
  reg        [0:0]    LsuL1Plugin_logic_shared_write_payload_data_dirty;
  wire                LsuL1Plugin_logic_shared_lsuRead_cmd_valid;
  wire       [3:0]    LsuL1Plugin_logic_shared_lsuRead_cmd_payload;
  (* keep , syn_keep *) wire       [0:0]    LsuL1Plugin_logic_shared_lsuRead_rsp_dirty /* synthesis syn_keep = 1 */ ;
  reg                 LsuL1Plugin_logic_refill_slots_0_valid;
  reg                 LsuL1Plugin_logic_refill_slots_0_dirty;
  reg        [31:0]   LsuL1Plugin_logic_refill_slots_0_address;
  reg                 LsuL1Plugin_logic_refill_slots_0_cmdSent;
  reg                 LsuL1Plugin_logic_refill_slots_0_loadedSet;
  reg                 LsuL1Plugin_logic_refill_slots_0_loaded;
  reg        [0:0]    LsuL1Plugin_logic_refill_slots_0_loadedCounter;
  wire                LsuL1Plugin_logic_refill_slots_0_loadedDone;
  wire                LsuL1Plugin_logic_refill_slots_0_free;
  wire                LsuL1Plugin_logic_refill_slots_0_fire;
  reg        [0:0]    LsuL1Plugin_logic_refill_slots_0_victim;
  wire       [0:0]    LsuL1Plugin_logic_refill_free;
  wire                LsuL1Plugin_logic_refill_full;
  reg                 LsuL1Plugin_logic_refill_push_valid;
  wire       [31:0]   LsuL1Plugin_logic_refill_push_payload_address;
  reg        [0:0]    LsuL1Plugin_logic_refill_push_payload_victim;
  wire                LsuL1Plugin_logic_refill_push_payload_dirty;
  wire                LsuL1Plugin_logic_refill_push_payload_unique;
  wire                LsuL1Plugin_logic_refill_push_payload_data;
  reg        [31:0]   LsuL1Plugin_logic_refill_pushCounter;
  wire                when_LsuL1Plugin_l377;
  wire                when_LsuL1Plugin_l381;
  wire                LsuL1Plugin_logic_refill_read_arbiter_slotsWithId_0_0;
  wire       [0:0]    LsuL1Plugin_logic_refill_read_arbiter_hits;
  wire                LsuL1Plugin_logic_refill_read_arbiter_hit;
  reg        [0:0]    LsuL1Plugin_logic_refill_read_arbiter_oh;
  reg        [0:0]    LsuL1Plugin_logic_refill_read_arbiter_lock;
  wire                when_LsuL1Plugin_l301;
  wire                LsuL1Plugin_logic_bus_read_cmd_fire;
  wire       [31:0]   LsuL1Plugin_logic_refill_read_cmdAddress;
  wire       [31:0]   LsuL1Plugin_logic_refill_read_rspAddress;
  wire                LsuL1Plugin_logic_refill_read_dirty;
  (* keep , syn_keep *) reg        [3:0]    LsuL1Plugin_logic_refill_read_wordIndex /* synthesis syn_keep = 1 */ ;
  wire                LsuL1Plugin_logic_refill_read_rspWithData;
  wire       [0:0]    LsuL1Plugin_logic_refill_read_bankWriteNotif;
  wire                LsuL1Plugin_logic_refill_read_writeReservation_win;
  reg                 LsuL1Plugin_logic_refill_read_writeReservation_take;
  reg                 LsuL1Plugin_logic_refill_read_hadError;
  wire                when_LsuL1Plugin_l450;
  reg                 LsuL1Plugin_logic_refill_read_fire;
  wire                LsuL1Plugin_logic_refill_read_reservation_win;
  reg                 LsuL1Plugin_logic_refill_read_reservation_take;
  wire                LsuL1Plugin_logic_refill_read_faulty;
  wire                when_LsuL1Plugin_l463;
  wire       [0:0]    LsuL1_REFILL_BUSY;
  reg                 LsuL1Plugin_logic_writeback_slots_0_fire;
  reg                 LsuL1Plugin_logic_writeback_slots_0_valid;
  reg                 LsuL1Plugin_logic_writeback_slots_0_busy;
  reg        [31:0]   LsuL1Plugin_logic_writeback_slots_0_address;
  reg                 LsuL1Plugin_logic_writeback_slots_0_readCmdDone;
  reg                 LsuL1Plugin_logic_writeback_slots_0_readRspDone;
  reg                 LsuL1Plugin_logic_writeback_slots_0_victimBufferReady;
  reg                 LsuL1Plugin_logic_writeback_slots_0_writeCmdDone;
  reg        [0:0]    LsuL1Plugin_logic_writeback_slots_0_timer_counter;
  wire                LsuL1Plugin_logic_writeback_slots_0_timer_done;
  wire                when_LsuL1Plugin_l530;
  wire                LsuL1Plugin_logic_writeback_slots_0_free;
  wire       [0:0]    LsuL1_WRITEBACK_BUSY;
  wire       [0:0]    LsuL1Plugin_logic_writeback_free;
  wire                LsuL1Plugin_logic_writeback_full;
  reg                 LsuL1Plugin_logic_writeback_push_valid;
  reg        [31:0]   LsuL1Plugin_logic_writeback_push_payload_address;
  wire                when_LsuL1Plugin_l556;
  wire                when_LsuL1Plugin_l561;
  wire                LsuL1Plugin_logic_writeback_read_arbiter_slotsWithId_0_0;
  wire       [0:0]    LsuL1Plugin_logic_writeback_read_arbiter_hits;
  wire                LsuL1Plugin_logic_writeback_read_arbiter_hit;
  reg        [0:0]    LsuL1Plugin_logic_writeback_read_arbiter_oh;
  reg        [0:0]    LsuL1Plugin_logic_writeback_read_arbiter_lock;
  wire                when_LsuL1Plugin_l301_1;
  wire       [31:0]   LsuL1Plugin_logic_writeback_read_address;
  (* keep , syn_keep *) reg        [3:0]    LsuL1Plugin_logic_writeback_read_wordIndex /* synthesis syn_keep = 1 */ ;
  wire                LsuL1Plugin_logic_writeback_read_slotRead_valid;
  wire                LsuL1Plugin_logic_writeback_read_slotRead_payload_last;
  wire       [3:0]    LsuL1Plugin_logic_writeback_read_slotRead_payload_wordIndex;
  wire                when_LsuL1Plugin_l605;
  reg                 LsuL1Plugin_logic_writeback_read_slotReadLast_valid;
  reg                 LsuL1Plugin_logic_writeback_read_slotReadLast_payload_last;
  reg        [3:0]    LsuL1Plugin_logic_writeback_read_slotReadLast_payload_wordIndex;
  wire       [31:0]   LsuL1Plugin_logic_writeback_read_readedData;
  wire                LsuL1Plugin_logic_writeback_write_arbiter_slotsWithId_0_0;
  wire       [0:0]    LsuL1Plugin_logic_writeback_write_arbiter_hits;
  wire                LsuL1Plugin_logic_writeback_write_arbiter_hit;
  reg        [0:0]    LsuL1Plugin_logic_writeback_write_arbiter_oh;
  reg        [0:0]    LsuL1Plugin_logic_writeback_write_arbiter_lock;
  wire                when_LsuL1Plugin_l301_2;
  (* keep , syn_keep *) reg        [3:0]    LsuL1Plugin_logic_writeback_write_wordIndex /* synthesis syn_keep = 1 */ ;
  wire                LsuL1Plugin_logic_writeback_write_last;
  wire                LsuL1Plugin_logic_writeback_write_bufferRead_valid;
  reg                 LsuL1Plugin_logic_writeback_write_bufferRead_ready;
  wire       [31:0]   LsuL1Plugin_logic_writeback_write_bufferRead_payload_address;
  wire                LsuL1Plugin_logic_writeback_write_bufferRead_payload_last;
  wire                LsuL1Plugin_logic_writeback_write_bufferRead_fire;
  wire                when_LsuL1Plugin_l676;
  wire                LsuL1Plugin_logic_writeback_write_cmd_valid;
  wire                LsuL1Plugin_logic_writeback_write_cmd_ready;
  wire       [31:0]   LsuL1Plugin_logic_writeback_write_cmd_payload_address;
  wire                LsuL1Plugin_logic_writeback_write_cmd_payload_last;
  reg                 LsuL1Plugin_logic_writeback_write_bufferRead_rValid;
  reg        [31:0]   LsuL1Plugin_logic_writeback_write_bufferRead_rData_address;
  reg                 LsuL1Plugin_logic_writeback_write_bufferRead_rData_last;
  wire                when_Stream_l399;
  wire       [3:0]    _zz_LsuL1Plugin_logic_writeback_write_word;
  wire       [31:0]   LsuL1Plugin_logic_writeback_write_word;
  wire       [7:0]    LsuL1Plugin_logic_lsu_rb0_readAddress;
  wire                when_LsuL1Plugin_l718;
  wire                when_LsuL1Plugin_l719;
  wire                execute_lane0_ctrls_3_upIsCancel;
  wire                execute_lane0_ctrls_3_downIsCancel;
  reg                 LsuL1Plugin_logic_lsu_rb1_onBanks_0_busyReg;
  wire                when_LsuL1Plugin_l735;
  wire                execute_lane0_ctrls_4_upIsCancel;
  wire                execute_lane0_ctrls_4_downIsCancel;
  wire                _zz_execute_ctrl4_down_LsuL1Plugin_logic_MUXED_DATA_lane0;
  wire                LsuL1Plugin_logic_lsu_sharedBypassers_0_hit;
  wire                LsuL1Plugin_logic_lsu_ctrl_wayWriteReservation_win;
  reg                 LsuL1Plugin_logic_lsu_ctrl_wayWriteReservation_take;
  wire                LsuL1Plugin_logic_lsu_ctrl_bankWriteReservation_win;
  wire                LsuL1Plugin_logic_lsu_ctrl_bankWriteReservation_take;
  wire                LsuL1Plugin_logic_lsu_ctrl_refillWayNeedWriteback;
  wire       [0:0]    LsuL1Plugin_logic_lsu_ctrl_refillHazards;
  wire       [0:0]    LsuL1Plugin_logic_lsu_ctrl_writebackHazards;
  wire                LsuL1Plugin_logic_lsu_ctrl_refillHazard;
  wire                LsuL1Plugin_logic_lsu_ctrl_writebackHazard;
  wire                LsuL1Plugin_logic_lsu_ctrl_wasDirty;
  wire       [0:0]    LsuL1Plugin_logic_lsu_ctrl_loadedDirties;
  wire                LsuL1Plugin_logic_lsu_ctrl_refillWayWasDirty;
  wire                LsuL1Plugin_logic_lsu_ctrl_writeToReadHazard;
  wire                LsuL1Plugin_logic_lsu_ctrl_bankNotRead;
  wire                LsuL1Plugin_logic_lsu_ctrl_loadHazard;
  wire                LsuL1Plugin_logic_lsu_ctrl_storeHazard;
  wire                LsuL1Plugin_logic_lsu_ctrl_preventSideEffects;
  wire                LsuL1Plugin_logic_lsu_ctrl_flushHazard;
  wire                LsuL1Plugin_logic_lsu_ctrl_coherencyHazard;
  reg                 LsuL1Plugin_logic_lsu_ctrl_hazardReg;
  reg                 LsuL1Plugin_logic_lsu_ctrl_flushHazardReg;
  wire                LsuL1Plugin_logic_lsu_ctrl_canRefill;
  wire                LsuL1Plugin_logic_lsu_ctrl_canFlush;
  wire       [0:0]    LsuL1Plugin_logic_lsu_ctrl_needFlushs;
  wire                LsuL1Plugin_logic_lsu_ctrl_needFlushs_bools_0;
  wire       [0:0]    _zz_LsuL1Plugin_logic_lsu_ctrl_needFlushOh;
  wire       [0:0]    LsuL1Plugin_logic_lsu_ctrl_needFlushOh;
  wire                LsuL1Plugin_logic_lsu_ctrl_isAccess;
  wire                LsuL1Plugin_logic_lsu_ctrl_askRefill;
  wire                LsuL1Plugin_logic_lsu_ctrl_askUpgrade;
  wire                LsuL1Plugin_logic_lsu_ctrl_askFlush;
  wire                LsuL1Plugin_logic_lsu_ctrl_askCbm;
  wire                LsuL1Plugin_logic_lsu_ctrl_doRefill;
  wire                LsuL1Plugin_logic_lsu_ctrl_doUpgrade;
  wire                LsuL1Plugin_logic_lsu_ctrl_doFlush;
  wire                LsuL1Plugin_logic_lsu_ctrl_doWrite;
  wire                LsuL1Plugin_logic_lsu_ctrl_doCbm;
  wire                LsuL1Plugin_logic_lsu_ctrl_doRefillPush;
  wire                when_LsuL1Plugin_l915;
  wire       [2:0]    _zz_13;
  wire                when_LsuL1Plugin_l929;
  wire       [21:0]   _zz_LsuL1Plugin_logic_waysWrite_tag_address;
  wire                when_LsuL1Plugin_l1019;
  reg        [4:0]    LsuL1Plugin_logic_initializer_counter;
  wire                LsuL1Plugin_logic_initializer_done;
  wire                when_LsuL1Plugin_l1219;
  wire                early0_MulPlugin_logic_formatBus_valid;
  wire       [31:0]   early0_MulPlugin_logic_formatBus_payload;
  reg        [60:0]   _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0;
  reg        [60:0]   _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0_1;
  reg        [60:0]   _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0_2;
  reg        [2:0]    _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0;
  reg        [2:0]    _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0_1;
  reg        [2:0]    _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0_2;
  reg        [65:0]   _zz_execute_ctrl4_down_early0_MulPlugin_logic_steps_1_adders_0_lane0;
  reg        [65:0]   _zz_execute_ctrl4_down_early0_MulPlugin_logic_steps_1_adders_0_lane0_1;
  wire                early0_DivPlugin_logic_formatBus_valid;
  wire       [31:0]   early0_DivPlugin_logic_formatBus_payload;
  reg                 early0_DivPlugin_logic_processing_divRevertResult;
  reg                 early0_DivPlugin_logic_processing_cmdSent;
  wire                io_cmd_fire;
  wire                early0_DivPlugin_logic_processing_request;
  wire       [31:0]   early0_DivPlugin_logic_processing_a;
  wire       [31:0]   early0_DivPlugin_logic_processing_b;
  reg                 early0_DivPlugin_logic_processing_unscheduleRequest;
  wire                early0_DivPlugin_logic_processing_freeze;
  wire       [31:0]   early0_DivPlugin_logic_processing_selected;
  wire       [31:0]   _zz_execute_ctrl2_down_DivPlugin_DIV_RESULT_lane0;
  wire                CsrAccessPlugin_logic_wbWi_valid;
  wire       [31:0]   CsrAccessPlugin_logic_wbWi_payload;
  reg                 CsrAccessPlugin_logic_flushPort_valid;
  reg                 PrivilegedPlugin_logic_harts_0_xretAwayFromMachine;
  wire       [0:0]    PrivilegedPlugin_logic_harts_0_commitMask;
  reg                 PrivilegedPlugin_logic_harts_0_int_pending;
  reg        [1:0]    PrivilegedPlugin_logic_harts_0_privilege;
  wire                PrivilegedPlugin_logic_harts_0_withMachinePrivilege;
  wire                PrivilegedPlugin_logic_harts_0_withSupervisorPrivilege;
  wire                PrivilegedPlugin_logic_harts_0_hartRunning;
  wire                PrivilegedPlugin_logic_harts_0_debugMode;
  wire                _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue;
  reg                 PrivilegedPlugin_logic_harts_0_m_status_mie;
  reg                 PrivilegedPlugin_logic_harts_0_m_status_mpie;
  wire       [1:0]    PrivilegedPlugin_logic_harts_0_m_status_mpp;
  wire                PrivilegedPlugin_logic_harts_0_m_status_sd;
  wire                PrivilegedPlugin_logic_harts_0_m_status_tw;
  reg                 PrivilegedPlugin_logic_harts_0_m_status_mprv;
  wire                _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_1;
  reg                 PrivilegedPlugin_logic_harts_0_m_cause_interrupt;
  reg        [3:0]    PrivilegedPlugin_logic_harts_0_m_cause_code;
  wire                _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_2;
  reg                 PrivilegedPlugin_logic_harts_0_m_ip_meip;
  reg                 PrivilegedPlugin_logic_harts_0_m_ip_mtip;
  reg                 PrivilegedPlugin_logic_harts_0_m_ip_msip;
  wire                _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_3;
  reg                 PrivilegedPlugin_logic_harts_0_m_ie_meie;
  reg                 PrivilegedPlugin_logic_harts_0_m_ie_mtie;
  reg                 PrivilegedPlugin_logic_harts_0_m_ie_msie;
  wire                _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_4;
  wire                _zz_when_TrapPlugin_l207;
  wire                _zz_when_TrapPlugin_l207_1;
  wire                _zz_when_TrapPlugin_l207_2;
  reg                 TrapPlugin_logic_fetchL1Invalidate_0_cmd_valid;
  reg                 TrapPlugin_logic_fetchL1Invalidate_0_cmd_ready;
  reg                 TrapPlugin_logic_lsuL1Invalidate_0_cmd_valid;
  wire                TrapPlugin_logic_lsuL1Invalidate_0_cmd_ready;
  reg                 early0_EnvPlugin_logic_trapPort_valid;
  reg                 early0_EnvPlugin_logic_trapPort_payload_exception;
  wire       [31:0]   early0_EnvPlugin_logic_trapPort_payload_tval;
  reg        [3:0]    early0_EnvPlugin_logic_trapPort_payload_code;
  reg        [1:0]    early0_EnvPlugin_logic_trapPort_payload_arg;
  reg                 early0_EnvPlugin_logic_flushPort_valid;
  wire                late0_IntAluPlugin_logic_wb_valid;
  wire       [31:0]   late0_IntAluPlugin_logic_wb_payload;
  (* keep , syn_keep *) reg        [31:0]   late0_IntAluPlugin_logic_alu_bitwise /* synthesis syn_keep = 1 */ ;
  wire       [31:0]   late0_IntAluPlugin_logic_alu_result;
  wire                late0_BarrelShifterPlugin_logic_wb_valid;
  wire       [31:0]   late0_BarrelShifterPlugin_logic_wb_payload;
  wire       [4:0]    late0_BarrelShifterPlugin_logic_shift_amplitude;
  wire       [31:0]   late0_BarrelShifterPlugin_logic_shift_reversed;
  wire       [31:0]   late0_BarrelShifterPlugin_logic_shift_shifted;
  wire       [31:0]   late0_BarrelShifterPlugin_logic_shift_patched;
  wire                late0_BranchPlugin_logic_wb_valid;
  wire       [31:0]   late0_BranchPlugin_logic_wb_payload;
  wire                late0_BranchPlugin_logic_pcPort_valid;
  wire                late0_BranchPlugin_logic_pcPort_payload_fault;
  wire       [31:0]   late0_BranchPlugin_logic_pcPort_payload_pc;
  wire                PcPlugin_logic_harts_0_aggregator_sortedByPriority_1_laneValid;
  wire                late0_BranchPlugin_logic_flushPort_valid;
  wire                WhiteboxerPlugin_logic_fetch_fire;
  reg                 BtbPlugin_logic_memWrite_valid;
  reg        [8:0]    BtbPlugin_logic_memWrite_payload_address;
  reg        [15:0]   BtbPlugin_logic_memWrite_payload_data_0_hash;
  wire       [29:0]   BtbPlugin_logic_memWrite_payload_data_0_pcTarget;
  reg                 BtbPlugin_logic_memWrite_payload_data_0_isBranch;
  reg                 BtbPlugin_logic_memWrite_payload_data_0_isPush;
  reg                 BtbPlugin_logic_memWrite_payload_data_0_isPop;
  reg                 BtbPlugin_logic_memWrite_payload_data_0_taken;
  reg        [0:0]    BtbPlugin_logic_memWrite_payload_mask;
  wire                BtbPlugin_logic_memRead_cmd_valid;
  wire       [8:0]    BtbPlugin_logic_memRead_cmd_payload;
  wire       [15:0]   BtbPlugin_logic_memRead_rsp_0_hash;
  wire       [29:0]   BtbPlugin_logic_memRead_rsp_0_pcTarget;
  wire                BtbPlugin_logic_memRead_rsp_0_isBranch;
  wire                BtbPlugin_logic_memRead_rsp_0_isPush;
  wire                BtbPlugin_logic_memRead_rsp_0_isPop;
  wire                BtbPlugin_logic_memRead_rsp_0_taken;
  wire                BtbPlugin_logic_memDp_wp_valid;
  wire       [8:0]    BtbPlugin_logic_memDp_wp_payload_address;
  wire       [15:0]   BtbPlugin_logic_memDp_wp_payload_data_0_hash;
  wire       [29:0]   BtbPlugin_logic_memDp_wp_payload_data_0_pcTarget;
  wire                BtbPlugin_logic_memDp_wp_payload_data_0_isBranch;
  wire                BtbPlugin_logic_memDp_wp_payload_data_0_isPush;
  wire                BtbPlugin_logic_memDp_wp_payload_data_0_isPop;
  wire                BtbPlugin_logic_memDp_wp_payload_data_0_taken;
  wire       [0:0]    BtbPlugin_logic_memDp_wp_payload_mask;
  wire                BtbPlugin_logic_memDp_rp_cmd_valid;
  wire       [8:0]    BtbPlugin_logic_memDp_rp_cmd_payload;
  wire       [15:0]   BtbPlugin_logic_memDp_rp_rsp_0_hash;
  wire       [29:0]   BtbPlugin_logic_memDp_rp_rsp_0_pcTarget;
  wire                BtbPlugin_logic_memDp_rp_rsp_0_isBranch;
  wire                BtbPlugin_logic_memDp_rp_rsp_0_isPush;
  wire                BtbPlugin_logic_memDp_rp_rsp_0_isPop;
  wire                BtbPlugin_logic_memDp_rp_rsp_0_taken;
  wire       [49:0]   _zz_BtbPlugin_logic_memDp_rp_rsp_0_hash;
  wire                LsuL1Plugin_logic_bus_toWishbone_arbiter_readCmd_valid;
  wire                LsuL1Plugin_logic_bus_toWishbone_arbiter_readCmd_ready;
  wire                LsuL1Plugin_logic_bus_toWishbone_arbiter_readCmd_payload_last;
  wire                LsuL1Plugin_logic_bus_toWishbone_arbiter_readCmd_payload_fragment_write;
  wire       [31:0]   LsuL1Plugin_logic_bus_toWishbone_arbiter_readCmd_payload_fragment_address;
  wire                LsuL1Plugin_logic_bus_toWishbone_arbiter_writeCmd_valid;
  wire                LsuL1Plugin_logic_bus_toWishbone_arbiter_writeCmd_ready;
  wire                LsuL1Plugin_logic_bus_toWishbone_arbiter_writeCmd_payload_last;
  wire                LsuL1Plugin_logic_bus_toWishbone_arbiter_writeCmd_payload_fragment_write;
  wire       [31:0]   LsuL1Plugin_logic_bus_toWishbone_arbiter_writeCmd_payload_fragment_address;
  wire                LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_valid;
  reg                 LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_ready;
  wire                LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_payload_last;
  wire                LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_payload_fragment_write;
  reg        [31:0]   LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_payload_fragment_address;
  wire       [31:0]   LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_payload_fragment_data;
  reg        [3:0]    LsuL1Plugin_logic_bus_toWishbone_arbiter_counter;
  wire                LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_fire;
  wire                LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_valid;
  wire                LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_ready;
  wire                LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_payload_last;
  wire                LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_payload_fragment_write;
  wire       [31:0]   LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_payload_fragment_address;
  wire       [31:0]   LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_payload_fragment_data;
  reg                 LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_rValid;
  reg                 LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_rData_last;
  reg                 LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_rData_fragment_write;
  reg        [31:0]   LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_rData_fragment_address;
  reg        [31:0]   LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_rData_fragment_data;
  wire                when_Stream_l399_1;
  reg        [3:0]    CsrAccessPlugin_bus_decode_trapCode;
  wire                CsrAccessPlugin_bus_read_valid;
  wire                CsrAccessPlugin_bus_read_moving;
  wire       [11:0]   CsrAccessPlugin_bus_read_address;
  reg                 CsrAccessPlugin_bus_read_halt;
  wire       [31:0]   CsrAccessPlugin_bus_read_toWriteBits;
  wire       [31:0]   CsrAccessPlugin_bus_read_data;
  wire                CsrAccessPlugin_bus_write_valid;
  wire                CsrAccessPlugin_bus_write_moving;
  reg                 CsrAccessPlugin_bus_write_halt;
  reg        [31:0]   CsrAccessPlugin_bus_write_bits;
  wire       [11:0]   CsrAccessPlugin_bus_write_address;
  reg        [3:0]    FetchL1Plugin_logic_trapPort_payload_code;
  reg        [1:0]    FetchL1Plugin_logic_trapPort_payload_arg;
  wire                FetchL1Plugin_logic_banks_0_write_valid;
  wire       [7:0]    FetchL1Plugin_logic_banks_0_write_payload_address;
  wire       [31:0]   FetchL1Plugin_logic_banks_0_write_payload_data;
  wire                FetchL1Plugin_logic_banks_0_read_cmd_valid;
  wire       [7:0]    FetchL1Plugin_logic_banks_0_read_cmd_payload;
  (* keep , syn_keep *) wire       [31:0]   FetchL1Plugin_logic_banks_0_read_rsp /* synthesis syn_keep = 1 */ ;
  reg        [0:0]    FetchL1Plugin_logic_waysWrite_mask;
  reg        [3:0]    FetchL1Plugin_logic_waysWrite_address;
  reg                 FetchL1Plugin_logic_waysWrite_tag_loaded;
  reg                 FetchL1Plugin_logic_waysWrite_tag_error;
  reg        [21:0]   FetchL1Plugin_logic_waysWrite_tag_address;
  wire                FetchL1Plugin_logic_ways_0_read_cmd_valid;
  wire       [3:0]    FetchL1Plugin_logic_ways_0_read_cmd_payload;
  (* keep , syn_keep *) wire                FetchL1Plugin_logic_ways_0_read_rsp_loaded /* synthesis syn_keep = 1 */ ;
  (* keep , syn_keep *) wire                FetchL1Plugin_logic_ways_0_read_rsp_error /* synthesis syn_keep = 1 */ ;
  (* keep , syn_keep *) wire       [21:0]   FetchL1Plugin_logic_ways_0_read_rsp_address /* synthesis syn_keep = 1 */ ;
  wire       [23:0]   _zz_FetchL1Plugin_logic_ways_0_read_rsp_loaded;
  reg                 FetchL1Plugin_logic_plru_write_valid;
  reg        [3:0]    FetchL1Plugin_logic_plru_write_payload_address;
  wire                FetchL1Plugin_logic_plru_read_cmd_valid;
  wire       [3:0]    FetchL1Plugin_logic_plru_read_cmd_payload;
  wire                FetchL1Plugin_logic_invalidate_cmd_valid;
  wire                FetchL1Plugin_logic_invalidate_cmd_ready;
  reg                 FetchL1Plugin_logic_invalidate_canStart;
  reg        [4:0]    FetchL1Plugin_logic_invalidate_counter;
  wire       [4:0]    FetchL1Plugin_logic_invalidate_counterIncr;
  wire                FetchL1Plugin_logic_invalidate_done;
  wire                FetchL1Plugin_logic_invalidate_last;
  reg                 FetchL1Plugin_logic_invalidate_firstEver;
  wire                when_FetchL1Plugin_l204;
  wire                when_FetchL1Plugin_l211;
  wire                when_FetchL1Plugin_l216;
  wire                fetch_logic_ctrls_0_haltRequest_FetchL1Plugin_l217;
  reg                 FetchL1Plugin_logic_refill_start_valid;
  wire       [31:0]   FetchL1Plugin_logic_refill_start_address;
  wire                FetchL1Plugin_logic_refill_start_isIo;
  reg                 FetchL1Plugin_logic_refill_slots_0_valid;
  reg                 FetchL1Plugin_logic_refill_slots_0_cmdSent;
  (* keep , syn_keep *) reg        [31:0]   FetchL1Plugin_logic_refill_slots_0_address /* synthesis syn_keep = 1 */ ;
  reg                 FetchL1Plugin_logic_refill_slots_0_isIo;
  reg        [0:0]    FetchL1Plugin_logic_refill_slots_0_priority;
  wire                FetchL1Plugin_logic_refill_slots_0_askCmd;
  reg        [31:0]   FetchL1Plugin_logic_refill_pushCounter;
  wire                FetchL1Plugin_logic_refill_hazard;
  wire                when_FetchL1Plugin_l255;
  wire                when_FetchL1Plugin_l268;
  wire       [0:0]    FetchL1Plugin_logic_refill_onCmd_propoedOh;
  reg                 FetchL1Plugin_logic_refill_onCmd_locked;
  wire                when_FetchL1Plugin_l276;
  reg        [0:0]    FetchL1Plugin_logic_refill_onCmd_lockedOh;
  wire       [0:0]    FetchL1Plugin_logic_refill_onCmd_oh;
  (* keep , syn_keep *) reg        [3:0]    FetchL1Plugin_logic_refill_onRsp_wordIndex /* synthesis syn_keep = 1 */ ;
  wire                FetchL1Plugin_logic_refill_onRsp_holdHarts;
  wire                fetch_logic_ctrls_0_haltRequest_FetchL1Plugin_l297;
  reg                 FetchL1Plugin_logic_refill_onRsp_firstCycle;
  wire                FetchL1Plugin_logic_bus_rsp_fire;
  wire       [31:0]   FetchL1Plugin_logic_refill_onRsp_address;
  wire                when_FetchL1Plugin_l304;
  wire                when_FetchL1Plugin_l330;
  wire                FetchL1Plugin_logic_cmd_doIt;
  wire       [31:0]   FetchL1Plugin_logic_ctrl_pmaPort_cmd_address;
  wire                FetchL1Plugin_logic_ctrl_pmaPort_rsp_fault;
  wire                FetchL1Plugin_logic_ctrl_pmaPort_rsp_io;
  wire                FetchL1Plugin_logic_ctrl_plruLogic_buffer_valid;
  wire       [3:0]    FetchL1Plugin_logic_ctrl_plruLogic_buffer_payload_address;
  reg                 FetchL1Plugin_logic_ctrl_plruLogic_buffer_regNext_valid;
  reg        [3:0]    FetchL1Plugin_logic_ctrl_plruLogic_buffer_regNext_payload_address;
  wire                FetchL1Plugin_logic_ctrl_dataAccessFault;
  reg                 FetchL1Plugin_logic_ctrl_trapSent;
  reg                 FetchL1Plugin_logic_ctrl_allowRefill;
  wire                when_FetchL1Plugin_l474;
  wire                when_FetchL1Plugin_l480;
  wire                when_FetchL1Plugin_l487;
  wire                when_FetchL1Plugin_l520;
  wire                when_FetchL1Plugin_l533;
  wire                when_FetchL1Plugin_l537;
  reg                 FetchL1Plugin_logic_ctrl_firstCycle;
  wire                when_FetchL1Plugin_l541;
  wire                when_FetchL1Plugin_l558;
  reg        [3:0]    LsuPlugin_logic_trapPort_payload_code;
  reg        [1:0]    LsuPlugin_logic_trapPort_payload_arg;
  reg                 LsuPlugin_logic_flushPort_valid;
  wire       [15:0]   LsuPlugin_logic_flushPort_payload_uopId;
  wire                LsuPlugin_logic_flushPort_payload_self;
  wire                LsuPlugin_logic_frontend_defaultsDecodings_0;
  wire                LsuPlugin_logic_frontend_defaultsDecodings_1;
  wire                LsuPlugin_logic_frontend_defaultsDecodings_2;
  wire                LsuPlugin_logic_frontend_defaultsDecodings_3;
  wire                LsuPlugin_logic_frontend_defaultsDecodings_4;
  wire                LsuPlugin_logic_frontend_defaultsDecodings_5;
  wire                LsuPlugin_logic_commitProbe_valid;
  wire       [31:0]   LsuPlugin_logic_commitProbe_payload_pc;
  wire       [31:0]   LsuPlugin_logic_commitProbe_payload_address;
  wire                LsuPlugin_logic_commitProbe_payload_load;
  wire                LsuPlugin_logic_commitProbe_payload_store;
  wire                LsuPlugin_logic_commitProbe_payload_trap;
  wire                LsuPlugin_logic_commitProbe_payload_io;
  wire                LsuPlugin_logic_commitProbe_payload_prefetchFailed;
  wire                LsuPlugin_logic_commitProbe_payload_miss;
  wire                LsuPlugin_logic_iwb_valid;
  wire       [31:0]   LsuPlugin_logic_iwb_payload;
  wire                execute_lane0_ctrls_0_upIsCancel;
  wire                execute_lane0_ctrls_0_downIsCancel;
  wire       [9:0]    WhiteboxerPlugin_logic_fetch_fetchId;
  wire                WhiteboxerPlugin_logic_decodes_0_fire;
  reg                 decode_ctrls_0_up_LANE_SEL_0_regNext;
  wire                when_CtrlLaneApi_l50;
  wire                WhiteboxerPlugin_logic_decodes_0_spawn;
  wire       [63:0]   WhiteboxerPlugin_logic_decodes_0_pc;
  wire       [9:0]    WhiteboxerPlugin_logic_decodes_0_fetchId;
  wire       [9:0]    WhiteboxerPlugin_logic_decodes_0_decodeId;
  wire       [15:0]   early0_BranchPlugin_logic_flushPort_payload_uopId;
  wire                early0_BranchPlugin_logic_flushPort_payload_self;
  reg                 early0_BranchPlugin_logic_trapPort_valid;
  wire                early0_BranchPlugin_logic_trapPort_payload_exception;
  wire       [31:0]   early0_BranchPlugin_logic_trapPort_payload_tval;
  wire       [3:0]    early0_BranchPlugin_logic_trapPort_payload_code;
  wire       [1:0]    early0_BranchPlugin_logic_trapPort_payload_arg;
  wire       [15:0]   CsrAccessPlugin_logic_flushPort_payload_uopId;
  wire                CsrAccessPlugin_logic_flushPort_payload_self;
  reg                 CsrAccessPlugin_logic_trapPort_valid;
  reg                 CsrAccessPlugin_logic_trapPort_payload_exception;
  wire       [31:0]   CsrAccessPlugin_logic_trapPort_payload_tval;
  reg        [3:0]    CsrAccessPlugin_logic_trapPort_payload_code;
  wire       [1:0]    CsrAccessPlugin_logic_trapPort_payload_arg;
  wire       [15:0]   early0_EnvPlugin_logic_flushPort_payload_uopId;
  wire                early0_EnvPlugin_logic_flushPort_payload_self;
  wire       [15:0]   late0_BranchPlugin_logic_flushPort_payload_uopId;
  wire                late0_BranchPlugin_logic_flushPort_payload_self;
  reg                 late0_BranchPlugin_logic_trapPort_valid;
  wire                late0_BranchPlugin_logic_trapPort_payload_exception;
  wire       [31:0]   late0_BranchPlugin_logic_trapPort_payload_tval;
  wire       [3:0]    late0_BranchPlugin_logic_trapPort_payload_code;
  wire       [1:0]    late0_BranchPlugin_logic_trapPort_payload_arg;
  wire       [1:0]    PrivilegedPlugin_logic_defaultTrap_csrPrivilege;
  wire                PrivilegedPlugin_logic_defaultTrap_csrReadOnly;
  wire                when_PrivilegedPlugin_l689;
  wire       [31:0]   FetchL1Plugin_pmaBuilder_addressBits;
  wire                _zz_FetchL1Plugin_logic_ctrl_pmaPort_rsp_io;
  wire                FetchL1Plugin_pmaBuilder_onTransfers_0_addressHit;
  wire                FetchL1Plugin_pmaBuilder_onTransfers_0_argsHit;
  wire                FetchL1Plugin_pmaBuilder_onTransfers_0_hit;
  reg        [3:0]    FetchL1Plugin_logic_bus_toWishbone_counter;
  wire                FetchL1Plugin_logic_bus_toWishbone_pending;
  wire                FetchL1Plugin_logic_bus_toWishbone_lastCycle;
  wire                when_FetchL1Bus_l247;
  wire                when_FetchL1Bus_l250;
  reg                 _zz_FetchL1Plugin_logic_bus_rsp_valid;
  reg        [31:0]   FetchL1WishbonePlugin_logic_bus_DAT_MISO_regNext;
  reg                 FetchL1WishbonePlugin_logic_bus_ERR_regNext;
  reg                 DecoderPlugin_logic_forgetPort_valid;
  reg        [31:0]   DecoderPlugin_logic_forgetPort_payload_pcOnLastSlice;
  wire                execute_lane0_ctrls_1_upIsCancel;
  wire                execute_lane0_ctrls_1_downIsCancel;
  reg        [31:0]   _zz_execute_ctrl1_down_early0_SrcPlugin_SRC1_lane0;
  reg        [31:0]   _zz_execute_ctrl1_down_early0_SrcPlugin_SRC2_lane0;
  reg        [31:0]   early0_SrcPlugin_logic_addsub_combined_rs2Patched;
  wire                lane0_IntFormatPlugin_logic_stages_0_wb_valid;
  wire       [31:0]   lane0_IntFormatPlugin_logic_stages_0_wb_payload;
  wire       [1:0]    lane0_IntFormatPlugin_logic_stages_0_hits;
  wire       [31:0]   lane0_IntFormatPlugin_logic_stages_0_raw;
  wire                lane0_IntFormatPlugin_logic_stages_1_wb_valid;
  reg        [31:0]   lane0_IntFormatPlugin_logic_stages_1_wb_payload;
  wire       [3:0]    lane0_IntFormatPlugin_logic_stages_1_hits;
  wire       [31:0]   lane0_IntFormatPlugin_logic_stages_1_raw;
  wire                lane0_IntFormatPlugin_logic_stages_1_segments_0_sign_sels_0;
  reg                 _zz_lane0_IntFormatPlugin_logic_stages_1_segments_0_sign_value;
  wire                lane0_IntFormatPlugin_logic_stages_1_segments_0_sign_value;
  wire                lane0_IntFormatPlugin_logic_stages_1_segments_0_doIt;
  wire                lane0_IntFormatPlugin_logic_stages_1_segments_1_sign_sels_0;
  wire                lane0_IntFormatPlugin_logic_stages_1_segments_1_sign_sels_1;
  reg                 _zz_lane0_IntFormatPlugin_logic_stages_1_segments_1_sign_value;
  wire                lane0_IntFormatPlugin_logic_stages_1_segments_1_sign_value;
  wire                lane0_IntFormatPlugin_logic_stages_1_segments_1_doIt;
  wire                lane0_IntFormatPlugin_logic_stages_2_wb_valid;
  wire       [31:0]   lane0_IntFormatPlugin_logic_stages_2_wb_payload;
  wire       [1:0]    lane0_IntFormatPlugin_logic_stages_2_hits;
  wire       [31:0]   lane0_IntFormatPlugin_logic_stages_2_raw;
  reg        [31:0]   _zz_execute_ctrl3_down_late0_SrcPlugin_SRC1_lane0;
  reg        [31:0]   _zz_execute_ctrl3_down_late0_SrcPlugin_SRC2_lane0;
  reg        [31:0]   late0_SrcPlugin_logic_addsub_combined_rs2Patched;
  wire       [1:0]    early0_EnvPlugin_logic_exe_privilege;
  wire       [1:0]    early0_EnvPlugin_logic_exe_xretPriv;
  reg                 early0_EnvPlugin_logic_exe_commit;
  wire                early0_EnvPlugin_logic_exe_retKo;
  wire                early0_EnvPlugin_logic_exe_vmaKo;
  wire                when_EnvPlugin_l86;
  wire                when_EnvPlugin_l95;
  wire                when_EnvPlugin_l119;
  wire                when_EnvPlugin_l123;
  reg        [31:0]   early0_BranchPlugin_pcCalc_target_a;
  reg        [31:0]   early0_BranchPlugin_pcCalc_target_b;
  wire       [1:0]    early0_BranchPlugin_pcCalc_slices;
  wire       [0:0]    AlignerPlugin_logic_maskGen_frontMasks_0;
  wire       [0:0]    AlignerPlugin_logic_maskGen_backMasks_0;
  wire       [31:0]   AlignerPlugin_logic_slices_data_0;
  wire       [0:0]    AlignerPlugin_logic_slices_mask;
  wire       [0:0]    AlignerPlugin_logic_slices_last;
  wire       [31:0]   AlignerPlugin_logic_slicesInstructions_0;
  reg        [0:0]    AlignerPlugin_logic_scanners_0_usageMask;
  wire                AlignerPlugin_logic_scanners_0_checker_0_required;
  wire                AlignerPlugin_logic_scanners_0_checker_0_last;
  wire                AlignerPlugin_logic_scanners_0_checker_0_redo;
  wire                AlignerPlugin_logic_scanners_0_checker_0_present;
  wire                AlignerPlugin_logic_scanners_0_checker_0_valid;
  wire                AlignerPlugin_logic_scanners_0_redo;
  wire                AlignerPlugin_logic_scanners_0_valid;
  wire       [0:0]    AlignerPlugin_logic_usedMask_0;
  wire       [0:0]    AlignerPlugin_logic_usedMask_1;
  wire                AlignerPlugin_logic_extractors_0_first;
  wire       [0:0]    AlignerPlugin_logic_extractors_0_usableMask;
  wire                AlignerPlugin_logic_extractors_0_usableMask_bools_0;
  wire       [0:0]    _zz_AlignerPlugin_logic_extractors_0_slicesOh;
  wire       [0:0]    AlignerPlugin_logic_extractors_0_slicesOh;
  reg                 AlignerPlugin_logic_extractors_0_redo;
  wire       [0:0]    AlignerPlugin_logic_extractors_0_localMask;
  reg        [0:0]    AlignerPlugin_logic_extractors_0_usageMask;
  reg                 AlignerPlugin_logic_extractors_0_valid;
  wire       [31:0]   AlignerPlugin_logic_extractors_0_ctx_pc;
  wire       [31:0]   AlignerPlugin_logic_extractors_0_ctx_instruction;
  wire       [9:0]    AlignerPlugin_logic_extractors_0_ctx_hm_Fetch_ID;
  wire       [0:0]    AlignerPlugin_logic_extractors_0_ctx_hm_Prediction_WORD_SLICES_BRANCH;
  wire       [0:0]    AlignerPlugin_logic_extractors_0_ctx_hm_Prediction_WORD_SLICES_TAKEN;
  wire       [31:0]   AlignerPlugin_logic_extractors_0_ctx_hm_Prediction_WORD_JUMP_PC;
  wire                AlignerPlugin_logic_extractors_0_ctx_hm_Prediction_WORD_JUMPED;
  wire                AlignerPlugin_logic_extractors_0_ctx_trap;
  wire                when_AlignerPlugin_l160;
  reg        [9:0]    AlignerPlugin_logic_feeder_harts_0_dopId;
  wire                when_AlignerPlugin_l171;
  wire                AlignerPlugin_logic_feeder_lanes_0_valid;
  wire                AlignerPlugin_logic_feeder_lanes_0_isRvc;
  wire                AlignerPlugin_logic_feeder_lanes_0_onBtb_didPrediction;
  reg        [0:0]    AlignerPlugin_logic_nobuffer_mask;
  wire       [0:0]    AlignerPlugin_logic_nobuffer_remaningMask;
  wire                when_AlignerPlugin_l292;
  wire                LsuPlugin_logic_bus_cmd_valid;
  reg                 LsuPlugin_logic_bus_cmd_ready;
  wire                LsuPlugin_logic_bus_cmd_payload_write;
  wire       [31:0]   LsuPlugin_logic_bus_cmd_payload_address;
  wire       [31:0]   LsuPlugin_logic_bus_cmd_payload_data;
  wire       [1:0]    LsuPlugin_logic_bus_cmd_payload_size;
  wire       [3:0]    LsuPlugin_logic_bus_cmd_payload_mask;
  wire                LsuPlugin_logic_bus_cmd_payload_io;
  wire                LsuPlugin_logic_bus_cmd_payload_fromHart;
  wire       [15:0]   LsuPlugin_logic_bus_cmd_payload_uopId;
  wire                LsuPlugin_logic_bus_rsp_valid;
  wire                LsuPlugin_logic_bus_rsp_payload_error;
  wire       [31:0]   LsuPlugin_logic_bus_rsp_payload_data;
  wire                LsuPlugin_logic_flusher_wantExit;
  reg                 LsuPlugin_logic_flusher_wantStart;
  wire                LsuPlugin_logic_flusher_wantKill;
  reg        [4:0]    LsuPlugin_logic_flusher_cmdCounter;
  wire                LsuPlugin_logic_flusher_inflight;
  reg        [0:0]    LsuPlugin_logic_flusher_waiter;
  wire       [4:0]    LsuPlugin_logic_onAddress0_ls_prefetchOp;
  wire                LsuPlugin_logic_onAddress0_ls_port_valid;
  wire                LsuPlugin_logic_onAddress0_ls_port_ready;
  wire       [2:0]    LsuPlugin_logic_onAddress0_ls_port_payload_op;
  wire       [31:0]   LsuPlugin_logic_onAddress0_ls_port_payload_address;
  wire       [1:0]    LsuPlugin_logic_onAddress0_ls_port_payload_size;
  wire                LsuPlugin_logic_onAddress0_ls_port_payload_load;
  wire                LsuPlugin_logic_onAddress0_ls_port_payload_store;
  wire                LsuPlugin_logic_onAddress0_ls_port_payload_atomic;
  wire                LsuPlugin_logic_onAddress0_ls_port_payload_clean;
  wire                LsuPlugin_logic_onAddress0_ls_port_payload_invalidate;
  wire       [11:0]   LsuPlugin_logic_onAddress0_ls_port_payload_storeId;
  reg        [11:0]   LsuPlugin_logic_onAddress0_ls_storeId;
  wire                LsuPlugin_logic_onAddress0_ls_port_fire;
  wire                LsuPlugin_logic_onAddress0_flush_port_valid;
  wire                LsuPlugin_logic_onAddress0_flush_port_ready;
  wire       [2:0]    LsuPlugin_logic_onAddress0_flush_port_payload_op;
  wire       [31:0]   LsuPlugin_logic_onAddress0_flush_port_payload_address;
  wire       [1:0]    LsuPlugin_logic_onAddress0_flush_port_payload_size;
  wire                LsuPlugin_logic_onAddress0_flush_port_payload_load;
  wire                LsuPlugin_logic_onAddress0_flush_port_payload_store;
  wire                LsuPlugin_logic_onAddress0_flush_port_payload_atomic;
  wire                LsuPlugin_logic_onAddress0_flush_port_payload_clean;
  wire                LsuPlugin_logic_onAddress0_flush_port_payload_invalidate;
  wire       [11:0]   LsuPlugin_logic_onAddress0_flush_port_payload_storeId;
  wire                LsuPlugin_logic_onAddress0_flush_port_fire;
  reg        [3:0]    _zz_execute_ctrl2_down_LsuL1_MASK_lane0;
  wire                when_LsuPlugin_l546;
  wire                when_LsuPlugin_l546_1;
  wire       [31:0]   LsuPlugin_logic_onPma_cached_cmd_address;
  wire       [0:0]    LsuPlugin_logic_onPma_cached_cmd_op;
  wire                LsuPlugin_logic_onPma_cached_rsp_fault;
  wire                LsuPlugin_logic_onPma_cached_rsp_io;
  wire       [31:0]   LsuPlugin_logic_onPma_io_cmd_address;
  wire       [1:0]    LsuPlugin_logic_onPma_io_cmd_size;
  wire       [0:0]    LsuPlugin_logic_onPma_io_cmd_op;
  wire                LsuPlugin_logic_onPma_io_rsp_fault;
  wire                LsuPlugin_logic_onPma_io_rsp_io;
  wire                when_LsuPlugin_l569;
  wire                LsuPlugin_logic_onPma_addressExtension;
  reg                 LsuPlugin_logic_onCtrl_lsuTrap;
  reg        [31:0]   LsuPlugin_logic_onCtrl_writeData;
  wire                LsuPlugin_logic_onCtrl_scMiss;
  reg                 LsuPlugin_logic_onCtrl_io_tooEarly;
  reg                 LsuPlugin_logic_onCtrl_io_allowIt;
  wire                when_LsuPlugin_l595;
  wire                LsuPlugin_logic_onCtrl_io_doIt;
  reg                 LsuPlugin_logic_onCtrl_io_doItReg;
  reg                 LsuPlugin_logic_onCtrl_io_cmdSent;
  wire                LsuPlugin_logic_bus_cmd_fire;
  wire                when_LsuPlugin_l599;
  wire                LsuPlugin_logic_bus_rsp_toStream_valid;
  wire                LsuPlugin_logic_bus_rsp_toStream_ready;
  wire                LsuPlugin_logic_bus_rsp_toStream_payload_error;
  wire       [31:0]   LsuPlugin_logic_bus_rsp_toStream_payload_data;
  wire                LsuPlugin_logic_onCtrl_io_rsp_valid;
  wire                LsuPlugin_logic_onCtrl_io_rsp_ready;
  wire                LsuPlugin_logic_onCtrl_io_rsp_payload_error;
  wire       [31:0]   LsuPlugin_logic_onCtrl_io_rsp_payload_data;
  reg                 LsuPlugin_logic_bus_rsp_toStream_rValid;
  wire                LsuPlugin_logic_onCtrl_io_rsp_fire;
  reg                 LsuPlugin_logic_bus_rsp_toStream_rData_error;
  reg        [31:0]   LsuPlugin_logic_bus_rsp_toStream_rData_data;
  wire                LsuPlugin_logic_onCtrl_io_freezeIt;
  wire       [31:0]   LsuPlugin_logic_onCtrl_loadData_input;
  wire       [7:0]    LsuPlugin_logic_onCtrl_loadData_splited_0;
  wire       [7:0]    LsuPlugin_logic_onCtrl_loadData_splited_1;
  wire       [7:0]    LsuPlugin_logic_onCtrl_loadData_splited_2;
  wire       [7:0]    LsuPlugin_logic_onCtrl_loadData_splited_3;
  reg        [31:0]   LsuPlugin_logic_onCtrl_loadData_shited;
  wire       [31:0]   LsuPlugin_logic_onCtrl_storeData_mapping_0_1;
  wire       [31:0]   LsuPlugin_logic_onCtrl_storeData_mapping_1_1;
  wire       [31:0]   LsuPlugin_logic_onCtrl_storeData_mapping_2_1;
  reg        [31:0]   _zz_execute_ctrl4_down_LsuL1_WRITE_DATA_lane0;
  wire                LsuPlugin_logic_onCtrl_traps_accessFault;
  wire                LsuPlugin_logic_onCtrl_traps_l1Failed;
  wire                LsuPlugin_logic_onCtrl_traps_pmaFault;
  wire                when_LsuPlugin_l804;
  wire                when_LsuPlugin_l831;
  wire                when_LsuPlugin_l859;
  wire                LsuPlugin_logic_onCtrl_mmuNeeded;
  wire                when_LsuPlugin_l899;
  reg        [0:0]    LsuPlugin_logic_onCtrl_hartRegulation_refill;
  reg                 LsuPlugin_logic_onCtrl_hartRegulation_valid;
  wire                when_LsuPlugin_l259;
  wire                when_LsuPlugin_l943;
  wire                when_LsuPlugin_l263;
  wire                LsuPlugin_logic_onWb_storeFire;
  wire                LsuPlugin_logic_onWb_storeBroadcast;
  wire                CsrRamPlugin_setup_initPort_valid;
  wire                CsrRamPlugin_setup_initPort_ready;
  wire       [1:0]    CsrRamPlugin_setup_initPort_address;
  wire       [31:0]   CsrRamPlugin_setup_initPort_data;
  wire                early0_BranchPlugin_logic_alu_expectedMsb;
  wire       [2:0]    switch_Misc_l242;
  reg                 _zz_execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_COND_lane0;
  reg                 _zz_execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_COND_lane0_1;
  wire                early0_BranchPlugin_logic_jumpLogic_wrongCond;
  wire                early0_BranchPlugin_logic_jumpLogic_needFix;
  wire                early0_BranchPlugin_logic_jumpLogic_doIt;
  wire                when_BranchPlugin_l251;
  wire                early0_BranchPlugin_logic_jumpLogic_rdLink;
  wire                early0_BranchPlugin_logic_jumpLogic_rs1Link;
  wire                early0_BranchPlugin_logic_jumpLogic_rdEquRs1;
  wire                PmpPlugin_logic_isMachine;
  wire                PmpPlugin_logic_instructionShouldHit;
  wire                PmpPlugin_logic_dataShouldHit;
  wire                FetchL1Plugin_logic_pmpPort_logic_dataShouldHitPort;
  wire       [19:0]   FetchL1Plugin_logic_pmpPort_logic_torCmpAddress;
  wire                LsuPlugin_logic_pmpPort_logic_dataShouldHitPort;
  wire       [19:0]   LsuPlugin_logic_pmpPort_logic_torCmpAddress;
  wire                LsuCachelessWishbonePlugin_logic_bridge_cmdStage_valid;
  wire                LsuCachelessWishbonePlugin_logic_bridge_cmdStage_ready;
  wire                LsuCachelessWishbonePlugin_logic_bridge_cmdStage_payload_write;
  wire       [31:0]   LsuCachelessWishbonePlugin_logic_bridge_cmdStage_payload_address;
  wire       [31:0]   LsuCachelessWishbonePlugin_logic_bridge_cmdStage_payload_data;
  wire       [1:0]    LsuCachelessWishbonePlugin_logic_bridge_cmdStage_payload_size;
  wire       [3:0]    LsuCachelessWishbonePlugin_logic_bridge_cmdStage_payload_mask;
  wire                LsuCachelessWishbonePlugin_logic_bridge_cmdStage_payload_io;
  wire                LsuCachelessWishbonePlugin_logic_bridge_cmdStage_payload_fromHart;
  wire       [15:0]   LsuCachelessWishbonePlugin_logic_bridge_cmdStage_payload_uopId;
  reg                 LsuPlugin_logic_bus_cmd_rValid;
  reg                 LsuPlugin_logic_bus_cmd_rData_write;
  reg        [31:0]   LsuPlugin_logic_bus_cmd_rData_address;
  reg        [31:0]   LsuPlugin_logic_bus_cmd_rData_data;
  reg        [1:0]    LsuPlugin_logic_bus_cmd_rData_size;
  reg        [3:0]    LsuPlugin_logic_bus_cmd_rData_mask;
  reg                 LsuPlugin_logic_bus_cmd_rData_io;
  reg                 LsuPlugin_logic_bus_cmd_rData_fromHart;
  reg        [15:0]   LsuPlugin_logic_bus_cmd_rData_uopId;
  wire                when_Stream_l399_2;
  wire       [31:0]   LsuPlugin_pmaBuilder_l1_addressBits;
  wire       [0:0]    LsuPlugin_pmaBuilder_l1_argsBits;
  wire                _zz_LsuPlugin_logic_onPma_cached_rsp_io;
  wire                LsuPlugin_pmaBuilder_l1_onTransfers_0_addressHit;
  wire                LsuPlugin_pmaBuilder_l1_onTransfers_0_argsHit;
  wire                LsuPlugin_pmaBuilder_l1_onTransfers_0_hit;
  wire       [31:0]   LsuPlugin_pmaBuilder_io_addressBits;
  wire       [2:0]    LsuPlugin_pmaBuilder_io_argsBits;
  wire                LsuPlugin_pmaBuilder_io_onTransfers_0_addressHit;
  wire                LsuPlugin_pmaBuilder_io_onTransfers_0_argsHit;
  wire                LsuPlugin_pmaBuilder_io_onTransfers_0_hit;
  wire                CsrRamPlugin_csrMapper_read_valid;
  wire                CsrRamPlugin_csrMapper_read_ready;
  wire       [1:0]    CsrRamPlugin_csrMapper_read_address;
  wire       [31:0]   CsrRamPlugin_csrMapper_read_data;
  wire                CsrRamPlugin_csrMapper_write_valid;
  wire                CsrRamPlugin_csrMapper_write_ready;
  wire       [1:0]    CsrRamPlugin_csrMapper_write_address;
  wire       [31:0]   CsrRamPlugin_csrMapper_write_data;
  wire                late0_BranchPlugin_logic_alu_expectedMsb;
  wire       [2:0]    switch_Misc_l242_1;
  reg                 _zz_execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_COND_lane0;
  reg                 _zz_execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_COND_lane0_1;
  wire                late0_BranchPlugin_logic_jumpLogic_wrongCond;
  wire                late0_BranchPlugin_logic_jumpLogic_needFix;
  wire                late0_BranchPlugin_logic_jumpLogic_doIt;
  wire                when_BranchPlugin_l251_1;
  wire                late0_BranchPlugin_logic_jumpLogic_rdLink;
  wire                late0_BranchPlugin_logic_jumpLogic_rs1Link;
  wire                late0_BranchPlugin_logic_jumpLogic_rdEquRs1;
  wire                late0_BranchPlugin_logic_jumpLogic_learn_valid;
  wire                late0_BranchPlugin_logic_jumpLogic_learn_ready;
  wire       [31:0]   late0_BranchPlugin_logic_jumpLogic_learn_payload_pcOnLastSlice;
  wire       [31:0]   late0_BranchPlugin_logic_jumpLogic_learn_payload_pcTarget;
  wire                late0_BranchPlugin_logic_jumpLogic_learn_payload_taken;
  wire                late0_BranchPlugin_logic_jumpLogic_learn_payload_isBranch;
  wire                late0_BranchPlugin_logic_jumpLogic_learn_payload_isPush;
  wire                late0_BranchPlugin_logic_jumpLogic_learn_payload_isPop;
  wire                late0_BranchPlugin_logic_jumpLogic_learn_payload_wasWrong;
  wire                late0_BranchPlugin_logic_jumpLogic_learn_payload_badPredictedTarget;
  wire       [15:0]   late0_BranchPlugin_logic_jumpLogic_learn_payload_uopId;
  wire                LearnPlugin_logic_learn_valid;
  wire       [31:0]   LearnPlugin_logic_learn_payload_pcOnLastSlice;
  wire       [31:0]   LearnPlugin_logic_learn_payload_pcTarget;
  wire                LearnPlugin_logic_learn_payload_taken;
  wire                LearnPlugin_logic_learn_payload_isBranch;
  wire                LearnPlugin_logic_learn_payload_isPush;
  wire                LearnPlugin_logic_learn_payload_isPop;
  wire                LearnPlugin_logic_learn_payload_wasWrong;
  wire                LearnPlugin_logic_learn_payload_badPredictedTarget;
  wire       [15:0]   LearnPlugin_logic_learn_payload_uopId;
  wire                LearnPlugin_logic_buffered_0_valid;
  wire                LearnPlugin_logic_buffered_0_ready;
  wire       [31:0]   LearnPlugin_logic_buffered_0_payload_pcOnLastSlice;
  wire       [31:0]   LearnPlugin_logic_buffered_0_payload_pcTarget;
  wire                LearnPlugin_logic_buffered_0_payload_taken;
  wire                LearnPlugin_logic_buffered_0_payload_isBranch;
  wire                LearnPlugin_logic_buffered_0_payload_isPush;
  wire                LearnPlugin_logic_buffered_0_payload_isPop;
  wire                LearnPlugin_logic_buffered_0_payload_wasWrong;
  wire                LearnPlugin_logic_buffered_0_payload_badPredictedTarget;
  wire       [15:0]   LearnPlugin_logic_buffered_0_payload_uopId;
  wire                LearnPlugin_logic_arbitrated_valid;
  wire                LearnPlugin_logic_arbitrated_ready;
  wire       [31:0]   LearnPlugin_logic_arbitrated_payload_pcOnLastSlice;
  wire       [31:0]   LearnPlugin_logic_arbitrated_payload_pcTarget;
  wire                LearnPlugin_logic_arbitrated_payload_taken;
  wire                LearnPlugin_logic_arbitrated_payload_isBranch;
  wire                LearnPlugin_logic_arbitrated_payload_isPush;
  wire                LearnPlugin_logic_arbitrated_payload_isPop;
  wire                LearnPlugin_logic_arbitrated_payload_wasWrong;
  wire                LearnPlugin_logic_arbitrated_payload_badPredictedTarget;
  wire       [15:0]   LearnPlugin_logic_arbitrated_payload_uopId;
  wire                LearnPlugin_logic_arbitrated_toFlow_valid;
  wire       [31:0]   LearnPlugin_logic_arbitrated_toFlow_payload_pcOnLastSlice;
  wire       [31:0]   LearnPlugin_logic_arbitrated_toFlow_payload_pcTarget;
  wire                LearnPlugin_logic_arbitrated_toFlow_payload_taken;
  wire                LearnPlugin_logic_arbitrated_toFlow_payload_isBranch;
  wire                LearnPlugin_logic_arbitrated_toFlow_payload_isPush;
  wire                LearnPlugin_logic_arbitrated_toFlow_payload_isPop;
  wire                LearnPlugin_logic_arbitrated_toFlow_payload_wasWrong;
  wire                LearnPlugin_logic_arbitrated_toFlow_payload_badPredictedTarget;
  wire       [15:0]   LearnPlugin_logic_arbitrated_toFlow_payload_uopId;
  reg        [15:0]   DecoderPlugin_logic_harts_0_uopId;
  wire                when_DecoderPlugin_l143;
  wire       [0:0]    DecoderPlugin_logic_interrupt_async;
  wire                when_DecoderPlugin_l151;
  reg        [0:0]    DecoderPlugin_logic_interrupt_buffered;
  wire                _zz_decode_ctrls_1_down_DispatchPlugin_MAY_FLUSH_0;
  wire                _zz_decode_ctrls_1_down_DispatchPlugin_logic_LANES_LAYER_HIT_1_0;
  wire                DecoderPlugin_logic_laneLogic_0_interruptPending;
  reg                 DecoderPlugin_logic_laneLogic_0_trapPort_valid;
  reg                 DecoderPlugin_logic_laneLogic_0_trapPort_payload_exception;
  wire       [31:0]   DecoderPlugin_logic_laneLogic_0_trapPort_payload_tval;
  reg        [3:0]    DecoderPlugin_logic_laneLogic_0_trapPort_payload_code;
  wire       [1:0]    DecoderPlugin_logic_laneLogic_0_trapPort_payload_arg;
  wire       [0:0]    DecoderPlugin_logic_laneLogic_0_trapPort_payload_laneAge;
  wire                DecoderPlugin_logic_laneLogic_0_fixer_isJb;
  wire                DecoderPlugin_logic_laneLogic_0_fixer_doIt;
  wire                DecoderPlugin_logic_laneLogic_0_completionPort_valid;
  wire       [15:0]   DecoderPlugin_logic_laneLogic_0_completionPort_payload_uopId;
  wire                DecoderPlugin_logic_laneLogic_0_completionPort_payload_trap;
  wire                DecoderPlugin_logic_laneLogic_0_completionPort_payload_commit;
  reg                 decode_ctrls_1_up_LANE_SEL_0_regNext;
  wire                when_CtrlLaneApi_l50_1;
  wire                when_DecoderPlugin_l229;
  wire                DecoderPlugin_logic_laneLogic_0_flushPort_valid;
  wire       [15:0]   DecoderPlugin_logic_laneLogic_0_flushPort_payload_uopId;
  wire                DecoderPlugin_logic_laneLogic_0_flushPort_payload_self;
  wire                when_DecoderPlugin_l247;
  wire       [15:0]   DecoderPlugin_logic_laneLogic_0_uopIdBase;
  wire                DispatchPlugin_logic_candidates_0_ctx_valid;
  reg        [1:0]    DispatchPlugin_logic_candidates_0_ctx_laneLayerHits;
  wire       [31:0]   DispatchPlugin_logic_candidates_0_ctx_uop;
  wire                DispatchPlugin_logic_candidates_0_ctx_hm_Prediction_ALIGNED_JUMPED;
  wire       [31:0]   DispatchPlugin_logic_candidates_0_ctx_hm_Prediction_ALIGNED_JUMPED_PC;
  wire       [0:0]    DispatchPlugin_logic_candidates_0_ctx_hm_Prediction_ALIGNED_SLICES_TAKEN;
  wire       [0:0]    DispatchPlugin_logic_candidates_0_ctx_hm_Prediction_ALIGNED_SLICES_BRANCH;
  wire                DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_FENCE_OLDER;
  wire                DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_MAY_FLUSH;
  wire                DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_DONT_FLUSH;
  wire                DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_DONT_FLUSH_FROM_LANES;
  wire                DispatchPlugin_logic_candidates_0_ctx_hm_DONT_FLUSH_PRECISE_3;
  wire                DispatchPlugin_logic_candidates_0_ctx_hm_DONT_FLUSH_PRECISE_4;
  wire       [31:0]   DispatchPlugin_logic_candidates_0_ctx_hm_PC;
  wire                DispatchPlugin_logic_candidates_0_ctx_hm_TRAP;
  wire       [15:0]   DispatchPlugin_logic_candidates_0_ctx_hm_Decode_UOP_ID;
  wire                DispatchPlugin_logic_candidates_0_ctx_hm_RS1_ENABLE;
  wire       [4:0]    DispatchPlugin_logic_candidates_0_ctx_hm_RS1_PHYS;
  wire                DispatchPlugin_logic_candidates_0_ctx_hm_RS2_ENABLE;
  wire       [4:0]    DispatchPlugin_logic_candidates_0_ctx_hm_RS2_PHYS;
  wire                DispatchPlugin_logic_candidates_0_ctx_hm_RD_ENABLE;
  wire       [4:0]    DispatchPlugin_logic_candidates_0_ctx_hm_RD_PHYS;
  wire                DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_logic_hcs_0_onRs_0_ENABLES_0;
  wire                DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_0;
  wire                DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_1;
  wire                DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_logic_hcs_1_onRs_0_ENABLES_0;
  wire                DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_logic_hcs_1_onRs_1_ENABLES_0;
  wire                DispatchPlugin_logic_candidates_0_fire;
  wire                DispatchPlugin_logic_candidates_0_cancel;
  reg        [1:0]    DispatchPlugin_logic_candidates_0_rsHazards;
  reg        [1:0]    DispatchPlugin_logic_candidates_0_reservationHazards;
  wire                DispatchPlugin_logic_candidates_0_flushHazards;
  wire                DispatchPlugin_logic_candidates_0_fenceOlderHazards;
  wire                DispatchPlugin_logic_candidates_0_moving;
  wire                DispatchPlugin_logic_rsHazardChecker_0_onLl_0_onRs_0_hazard;
  wire                DispatchPlugin_logic_rsHazardChecker_0_onLl_0_onRs_1_hazard;
  wire                DispatchPlugin_logic_rsHazardChecker_0_onLl_1_onRs_0_hazard;
  wire                DispatchPlugin_logic_rsHazardChecker_0_onLl_1_onRs_1_hazard;
  wire                DispatchPlugin_logic_reservationChecker_0_onLl_0_hit;
  wire                DispatchPlugin_logic_reservationChecker_0_onLl_1_hit;
  wire                DispatchPlugin_logic_flushChecker_0_executeCheck_0_hits_0;
  wire                DispatchPlugin_logic_flushChecker_0_executeCheck_0_hits_1;
  wire                DispatchPlugin_logic_flushChecker_0_oldersHazard;
  wire       [0:0]    DispatchPlugin_logic_fenceChecker_olderInflights;
  wire                DispatchPlugin_logic_feeds_0_sending;
  reg                 DispatchPlugin_logic_feeds_0_sent;
  wire                when_DispatchPlugin_l368;
  wire       [0:0]    DispatchPlugin_logic_scheduler_eusFree_0;
  wire       [0:0]    DispatchPlugin_logic_scheduler_eusFree_1;
  wire       [0:0]    DispatchPlugin_logic_scheduler_hartFree_0;
  wire       [0:0]    DispatchPlugin_logic_scheduler_hartFree_1;
  wire                DispatchPlugin_logic_scheduler_arbiters_0_candHazard;
  wire       [1:0]    DispatchPlugin_logic_scheduler_arbiters_0_layersHits;
  wire       [1:0]    _zz_DispatchPlugin_logic_scheduler_arbiters_0_layersHits_bools_0;
  wire                DispatchPlugin_logic_scheduler_arbiters_0_layersHits_bools_0;
  wire                DispatchPlugin_logic_scheduler_arbiters_0_layersHits_bools_1;
  reg        [1:0]    _zz_DispatchPlugin_logic_scheduler_arbiters_0_layerOh;
  wire       [1:0]    DispatchPlugin_logic_scheduler_arbiters_0_layerOh;
  wire       [0:0]    DispatchPlugin_logic_scheduler_arbiters_0_eusOh;
  wire                DispatchPlugin_logic_scheduler_arbiters_0_doIt;
  wire       [0:0]    DispatchPlugin_logic_inserter_0_oh;
  wire                DispatchPlugin_logic_inserter_0_trap;
  wire                when_DispatchPlugin_l439;
  wire       [1:0]    DispatchPlugin_logic_inserter_0_layerOhUnfiltred;
  wire       [0:0]    DispatchPlugin_logic_inserter_0_layer_0_0;
  wire                DispatchPlugin_logic_inserter_0_layer_0_1;
  wire       [0:0]    DispatchPlugin_logic_inserter_0_layer_1_0;
  wire                DispatchPlugin_logic_inserter_0_layer_1_1;
  wire       [1:0]    _zz_execute_ctrl0_up_lane0_LAYER_SEL_lane0;
  wire       [1:0]    CsrRamPlugin_csrMapper_ramAddress;
  wire       [11:0]   _zz_CsrRamPlugin_csrMapper_ramAddress;
  reg                 CsrRamPlugin_csrMapper_withRead;
  wire                when_CsrRamPlugin_l85;
  reg                 CsrRamPlugin_csrMapper_doWrite;
  reg                 CsrRamPlugin_csrMapper_fired;
  wire                when_CsrRamPlugin_l92;
  wire                when_CsrRamPlugin_l96;
  wire       [15:0]   BtbPlugin_logic_onLearn_hash;
  wire       [1:0]    lane0_integer_WriteBackPlugin_logic_stages_0_hits;
  wire       [31:0]   lane0_integer_WriteBackPlugin_logic_stages_0_muxed;
  wire                lane0_integer_WriteBackPlugin_logic_stages_0_write_valid;
  wire       [15:0]   lane0_integer_WriteBackPlugin_logic_stages_0_write_payload_uopId;
  wire       [31:0]   lane0_integer_WriteBackPlugin_logic_stages_0_write_payload_data;
  wire       [0:0]    lane0_integer_WriteBackPlugin_logic_stages_1_hits;
  wire       [31:0]   lane0_integer_WriteBackPlugin_logic_stages_1_muxed;
  wire       [31:0]   lane0_integer_WriteBackPlugin_logic_stages_1_merged;
  wire                lane0_integer_WriteBackPlugin_logic_stages_1_write_valid;
  wire       [15:0]   lane0_integer_WriteBackPlugin_logic_stages_1_write_payload_uopId;
  wire       [31:0]   lane0_integer_WriteBackPlugin_logic_stages_1_write_payload_data;
  wire       [1:0]    lane0_integer_WriteBackPlugin_logic_stages_2_hits;
  wire       [31:0]   lane0_integer_WriteBackPlugin_logic_stages_2_muxed;
  wire       [31:0]   lane0_integer_WriteBackPlugin_logic_stages_2_merged;
  wire                lane0_integer_WriteBackPlugin_logic_stages_2_write_valid;
  wire       [15:0]   lane0_integer_WriteBackPlugin_logic_stages_2_write_payload_uopId;
  wire       [31:0]   lane0_integer_WriteBackPlugin_logic_stages_2_write_payload_data;
  wire                lane0_integer_WriteBackPlugin_logic_write_port_valid;
  wire       [4:0]    lane0_integer_WriteBackPlugin_logic_write_port_address;
  wire       [31:0]   lane0_integer_WriteBackPlugin_logic_write_port_data;
  wire       [15:0]   lane0_integer_WriteBackPlugin_logic_write_port_uopId;
  wire                _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_1_ENABLES_0_0;
  wire                _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_0_0;
  wire                _zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_4_0;
  wire                _zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_4_0_1;
  wire                TrapPlugin_logic_initHold;
  reg                 decode_ctrls_1_up_LANE_SEL_0_regNext_1;
  wire                when_CtrlLaneApi_l50_2;
  wire                WhiteboxerPlugin_logic_serializeds_0_fire;
  wire       [9:0]    WhiteboxerPlugin_logic_serializeds_0_decodeId;
  wire       [15:0]   WhiteboxerPlugin_logic_serializeds_0_microOpId;
  wire       [31:0]   WhiteboxerPlugin_logic_serializeds_0_microOp;
  reg                 execute_ctrl0_down_LANE_SEL_lane0_regNext;
  wire                when_CtrlLaneApi_l50_3;
  wire                WhiteboxerPlugin_logic_dispatches_0_fire;
  wire       [15:0]   WhiteboxerPlugin_logic_dispatches_0_microOpId;
  reg                 execute_ctrl2_down_LANE_SEL_lane0_regNext;
  wire                when_CtrlLaneApi_l50_4;
  wire                WhiteboxerPlugin_logic_executes_0_fire;
  wire       [15:0]   WhiteboxerPlugin_logic_executes_0_microOpId;
  wire                WhiteboxerPlugin_logic_csr_access_valid;
  wire       [15:0]   WhiteboxerPlugin_logic_csr_access_payload_uopId;
  wire       [11:0]   WhiteboxerPlugin_logic_csr_access_payload_address;
  wire       [31:0]   WhiteboxerPlugin_logic_csr_access_payload_write;
  wire       [31:0]   WhiteboxerPlugin_logic_csr_access_payload_read;
  wire                WhiteboxerPlugin_logic_csr_access_payload_writeDone;
  wire                WhiteboxerPlugin_logic_csr_access_payload_readDone;
  wire       [15:0]   BtbPlugin_logic_onForget_hash;
  wire                fetch_logic_ctrls_0_haltRequest_BtbPlugin_l200;
  wire       [0:0]    BtbPlugin_logic_applyIt_chunksMask;
  wire       [0:0]    BtbPlugin_logic_applyIt_chunksTakenOh;
  wire                BtbPlugin_logic_applyIt_needIt;
  reg                 BtbPlugin_logic_applyIt_correctionSent;
  wire                when_BtbPlugin_l233;
  wire                BtbPlugin_logic_applyIt_doIt;
  wire       [15:0]   BtbPlugin_logic_applyIt_entry_hash;
  wire       [29:0]   BtbPlugin_logic_applyIt_entry_pcTarget;
  wire                BtbPlugin_logic_applyIt_entry_isBranch;
  wire                BtbPlugin_logic_applyIt_entry_isPush;
  wire                BtbPlugin_logic_applyIt_entry_isPop;
  wire                BtbPlugin_logic_applyIt_entry_taken;
  wire       [29:0]   BtbPlugin_logic_applyIt_pcTarget;
  reg                 TrapPlugin_logic_harts_0_crsPorts_read_valid;
  wire                TrapPlugin_logic_harts_0_crsPorts_read_ready;
  reg        [1:0]    TrapPlugin_logic_harts_0_crsPorts_read_address;
  wire       [31:0]   TrapPlugin_logic_harts_0_crsPorts_read_data;
  wire                AlignerPlugin_logic_nobuffer_flushIt;
  wire                when_AlignerPlugin_l298;
  wire                decode_logic_flushes_0_onLanes_0_doIt;
  wire                decode_logic_flushes_1_onLanes_0_doIt;
  reg                 TrapPlugin_logic_harts_0_crsPorts_write_valid;
  wire                TrapPlugin_logic_harts_0_crsPorts_write_ready;
  reg        [1:0]    TrapPlugin_logic_harts_0_crsPorts_write_address;
  reg        [31:0]   TrapPlugin_logic_harts_0_crsPorts_write_data;
  reg                 TrapPlugin_logic_harts_0_interrupt_valid;
  reg        [3:0]    TrapPlugin_logic_harts_0_interrupt_code;
  reg        [1:0]    TrapPlugin_logic_harts_0_interrupt_targetPrivilege;
  wire                when_TrapPlugin_l201;
  wire                when_TrapPlugin_l207;
  wire                when_TrapPlugin_l207_1;
  wire                when_TrapPlugin_l207_2;
  reg                 TrapPlugin_logic_harts_0_interrupt_validBuffer;
  wire                TrapPlugin_logic_harts_0_interrupt_pendingInterrupt;
  wire                when_TrapPlugin_l226;
  wire                _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_valid;
  wire                _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_3_valid;
  wire                _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_valid;
  wire                _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_valid_1;
  wire                _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_valid_2;
  wire                _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_valid_1;
  wire                _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_2_valid;
  wire                TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_valid;
  wire                TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_payload_exception;
  wire       [31:0]   TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_payload_tval;
  wire       [3:0]    TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_payload_code;
  wire       [1:0]    TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_payload_arg;
  wire       [1:0]    _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_payload_exception;
  wire       [38:0]   _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_payload_exception_1;
  wire                TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_valid;
  wire                TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception;
  wire       [31:0]   TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_tval;
  wire       [3:0]    TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_code;
  wire       [1:0]    TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_arg;
  wire       [2:0]    _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception;
  wire       [38:0]   _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_1;
  wire                TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_2_valid;
  wire                TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_2_payload_exception;
  wire       [31:0]   TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_2_payload_tval;
  wire       [3:0]    TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_2_payload_code;
  wire       [1:0]    TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_2_payload_arg;
  wire                TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_3_valid;
  wire                TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_3_payload_exception;
  wire       [31:0]   TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_3_payload_tval;
  wire       [3:0]    TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_3_payload_code;
  wire       [1:0]    TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_3_payload_arg;
  wire       [3:0]    _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh;
  wire                _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh_1;
  wire                _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh_2;
  wire                _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh_3;
  reg        [3:0]    _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh_4;
  wire       [3:0]    TrapPlugin_logic_harts_0_trap_pending_arbiter_oh;
  wire                TrapPlugin_logic_harts_0_trap_pending_arbiter_down_valid;
  wire                TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_exception;
  wire       [31:0]   TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_tval;
  wire       [3:0]    TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_code;
  wire       [1:0]    TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_arg;
  wire       [38:0]   _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_exception;
  reg                 TrapPlugin_logic_harts_0_trap_pending_state_exception;
  reg        [31:0]   TrapPlugin_logic_harts_0_trap_pending_state_tval;
  reg        [3:0]    TrapPlugin_logic_harts_0_trap_pending_state_code;
  reg        [1:0]    TrapPlugin_logic_harts_0_trap_pending_state_arg;
  reg        [31:0]   TrapPlugin_logic_harts_0_trap_pending_pc;
  reg        [0:0]    TrapPlugin_logic_harts_0_trap_pending_slices;
  wire       [1:0]    TrapPlugin_logic_harts_0_trap_pending_xret_sourcePrivilege;
  wire       [1:0]    TrapPlugin_logic_harts_0_trap_pending_xret_targetPrivilege;
  wire       [1:0]    TrapPlugin_logic_harts_0_trap_exception_exceptionTargetPrivilegeUncapped;
  wire       [3:0]    TrapPlugin_logic_harts_0_trap_exception_code;
  wire       [1:0]    TrapPlugin_logic_harts_0_trap_exception_targetPrivilege;
  wire                execute_lane0_ctrls_5_upIsCancel;
  wire                execute_lane0_ctrls_5_downIsCancel;
  wire       [0:0]    TrapPlugin_logic_harts_0_trap_trigger_oh;
  wire                TrapPlugin_logic_harts_0_trap_trigger_valid;
  reg                 TrapPlugin_logic_harts_0_trap_whitebox_trap;
  reg                 TrapPlugin_logic_harts_0_trap_whitebox_interrupt;
  reg        [3:0]    TrapPlugin_logic_harts_0_trap_whitebox_code;
  reg                 TrapPlugin_logic_harts_0_trap_pcPort_valid;
  wire                TrapPlugin_logic_harts_0_trap_pcPort_payload_fault;
  reg        [31:0]   TrapPlugin_logic_harts_0_trap_pcPort_payload_pc;
  wire                PcPlugin_logic_harts_0_aggregator_sortedByPriority_0_laneValid;
  wire                TrapPlugin_logic_harts_0_trap_fsm_wantExit;
  reg                 TrapPlugin_logic_harts_0_trap_fsm_wantStart;
  wire                TrapPlugin_logic_harts_0_trap_fsm_wantKill;
  wire                TrapPlugin_logic_harts_0_trap_fsm_inflightTrap;
  wire                TrapPlugin_logic_harts_0_trap_fsm_holdPort;
  reg                 TrapPlugin_logic_harts_0_trap_fsm_wfi;
  reg                 TrapPlugin_logic_harts_0_trap_fsm_buffer_sampleIt;
  reg                 TrapPlugin_logic_harts_0_trap_fsm_buffer_i_valid;
  reg        [3:0]    TrapPlugin_logic_harts_0_trap_fsm_buffer_i_code;
  reg        [1:0]    TrapPlugin_logic_harts_0_trap_fsm_buffer_i_targetPrivilege;
  wire                TrapPlugin_logic_harts_0_trap_fsm_buffer_trap_interrupt;
  wire       [1:0]    TrapPlugin_logic_harts_0_trap_fsm_buffer_trap_targetPrivilege;
  wire       [31:0]   TrapPlugin_logic_harts_0_trap_fsm_buffer_trap_tval;
  wire       [3:0]    TrapPlugin_logic_harts_0_trap_fsm_buffer_trap_code;
  wire                TrapPlugin_logic_harts_0_trap_fsm_resetToRunConditions_0;
  reg        [31:0]   TrapPlugin_logic_harts_0_trap_fsm_jumpTarget;
  wire       [0:0]    TrapPlugin_logic_harts_0_trap_fsm_jumpOffset;
  reg                 TrapPlugin_logic_harts_0_trap_fsm_trapEnterDebug;
  wire                TrapPlugin_logic_harts_0_trap_fsm_triggerEbreak;
  reg                 TrapPlugin_logic_harts_0_trap_fsm_triggerEbreakReg;
  wire                when_TrapPlugin_l556;
  reg        [31:0]   TrapPlugin_logic_harts_0_trap_fsm_readed;
  wire       [1:0]    TrapPlugin_logic_harts_0_trap_fsm_xretPrivilege;
  wire                PcPlugin_logic_forcedSpawn;
  reg        [9:0]    PcPlugin_logic_harts_0_self_id;
  wire                PcPlugin_logic_harts_0_self_flow_valid;
  wire                PcPlugin_logic_harts_0_self_flow_payload_fault;
  wire       [31:0]   PcPlugin_logic_harts_0_self_flow_payload_pc;
  wire                PcPlugin_logic_harts_0_aggregator_sortedByPriority_4_laneValid;
  reg                 PcPlugin_logic_harts_0_self_increment;
  reg                 PcPlugin_logic_harts_0_self_fault;
  reg        [31:0]   PcPlugin_logic_harts_0_self_state;
  wire       [31:0]   PcPlugin_logic_harts_0_self_pc;
  wire                PcPlugin_logic_harts_0_aggregator_valids_0;
  wire                PcPlugin_logic_harts_0_aggregator_valids_1;
  wire                PcPlugin_logic_harts_0_aggregator_valids_2;
  wire                PcPlugin_logic_harts_0_aggregator_valids_3;
  wire                PcPlugin_logic_harts_0_aggregator_valids_4;
  wire       [4:0]    _zz_PcPlugin_logic_harts_0_aggregator_oh;
  wire                _zz_PcPlugin_logic_harts_0_aggregator_oh_1;
  wire                _zz_PcPlugin_logic_harts_0_aggregator_oh_2;
  wire                _zz_PcPlugin_logic_harts_0_aggregator_oh_3;
  wire                _zz_PcPlugin_logic_harts_0_aggregator_oh_4;
  reg        [4:0]    _zz_PcPlugin_logic_harts_0_aggregator_oh_5;
  wire       [4:0]    PcPlugin_logic_harts_0_aggregator_oh;
  wire       [31:0]   PcPlugin_logic_harts_0_aggregator_target;
  wire                PcPlugin_logic_harts_0_aggregator_fault;
  wire                _zz_PcPlugin_logic_harts_0_aggregator_target;
  wire                _zz_PcPlugin_logic_harts_0_aggregator_target_1;
  wire                _zz_PcPlugin_logic_harts_0_aggregator_target_2;
  wire                _zz_PcPlugin_logic_harts_0_aggregator_target_3;
  wire                _zz_PcPlugin_logic_harts_0_aggregator_target_4;
  wire                PcPlugin_logic_harts_0_holdComb;
  reg                 PcPlugin_logic_harts_0_holdReg;
  wire                PcPlugin_logic_harts_0_output_valid;
  wire                PcPlugin_logic_harts_0_output_ready;
  reg        [31:0]   PcPlugin_logic_harts_0_output_payload_pc;
  wire                PcPlugin_logic_harts_0_output_payload_fault;
  wire                PcPlugin_logic_harts_0_output_fire;
  wire                PcPlugin_logic_holdHalter_doIt;
  wire                fetch_logic_ctrls_0_haltRequest_PcPlugin_l133;
  wire                CsrAccessPlugin_logic_fsm_wantExit;
  reg                 CsrAccessPlugin_logic_fsm_wantStart;
  wire                CsrAccessPlugin_logic_fsm_wantKill;
  reg                 REG_CSR_1952;
  reg                 REG_CSR_1953;
  reg                 REG_CSR_1954;
  reg                 REG_CSR_3857;
  reg                 REG_CSR_3858;
  reg                 REG_CSR_3859;
  reg                 REG_CSR_3860;
  reg                 REG_CSR_769;
  reg                 REG_CSR_768;
  reg                 REG_CSR_834;
  reg                 REG_CSR_836;
  reg                 REG_CSR_772;
  reg                 REG_CSR_PrivilegedPlugin_logic_readAnyWriteLegal_tvecFilter;
  reg                 REG_CSR_PrivilegedPlugin_logic_readAnyWriteLegal_epcFilter;
  reg                 REG_CSR_CsrRamPlugin_csrMapper_selFilter;
  reg                 REG_CSR_CsrAccessPlugin_logic_trapNextOnWriteFilter;
  reg                 CsrAccessPlugin_logic_fsm_interface_read;
  reg                 CsrAccessPlugin_logic_fsm_interface_write;
  wire       [31:0]   CsrAccessPlugin_logic_fsm_interface_rs1;
  reg        [31:0]   CsrAccessPlugin_logic_fsm_interface_aluInput;
  reg        [31:0]   CsrAccessPlugin_logic_fsm_interface_csrValue;
  reg        [31:0]   CsrAccessPlugin_logic_fsm_interface_onWriteBits;
  wire       [15:0]   CsrAccessPlugin_logic_fsm_interface_uopId;
  wire       [31:0]   CsrAccessPlugin_logic_fsm_interface_uop;
  wire                CsrAccessPlugin_logic_fsm_interface_doImm;
  wire                CsrAccessPlugin_logic_fsm_interface_doMask;
  wire                CsrAccessPlugin_logic_fsm_interface_doClear;
  wire       [4:0]    CsrAccessPlugin_logic_fsm_interface_rdPhys;
  wire                CsrAccessPlugin_logic_fsm_interface_rdEnable;
  reg                 CsrAccessPlugin_logic_fsm_interface_fire;
  wire       [11:0]   CsrAccessPlugin_logic_fsm_inject_csrAddress;
  wire                CsrAccessPlugin_logic_fsm_inject_immZero;
  wire                CsrAccessPlugin_logic_fsm_inject_srcZero;
  wire                CsrAccessPlugin_logic_fsm_inject_csrWrite;
  wire                CsrAccessPlugin_logic_fsm_inject_csrRead;
  wire                COMB_CSR_1952;
  wire                COMB_CSR_1953;
  wire                COMB_CSR_1954;
  wire                COMB_CSR_3857;
  wire                COMB_CSR_3858;
  wire                COMB_CSR_3859;
  wire                COMB_CSR_3860;
  wire                COMB_CSR_769;
  wire                COMB_CSR_768;
  wire                COMB_CSR_834;
  wire                COMB_CSR_836;
  wire                COMB_CSR_772;
  wire                COMB_CSR_PrivilegedPlugin_logic_readAnyWriteLegal_tvecFilter;
  wire                COMB_CSR_PrivilegedPlugin_logic_readAnyWriteLegal_epcFilter;
  wire                COMB_CSR_CsrRamPlugin_csrMapper_selFilter;
  wire                COMB_CSR_CsrAccessPlugin_logic_trapNextOnWriteFilter;
  wire                CsrAccessPlugin_logic_fsm_inject_implemented;
  wire                CsrAccessPlugin_logic_fsm_inject_onDecodeDo;
  wire                when_CsrAccessPlugin_l155;
  wire                CsrAccessPlugin_logic_fsm_inject_trap;
  reg                 CsrAccessPlugin_logic_fsm_inject_unfreeze;
  wire                CsrAccessPlugin_logic_fsm_inject_freeze;
  reg                 CsrAccessPlugin_logic_fsm_inject_flushReg;
  wire                when_CsrAccessPlugin_l197;
  reg                 CsrAccessPlugin_logic_fsm_inject_sampled;
  reg                 CsrAccessPlugin_logic_fsm_inject_trapReg;
  reg                 CsrAccessPlugin_logic_fsm_inject_busTrapReg;
  reg        [3:0]    CsrAccessPlugin_logic_fsm_inject_busTrapCodeReg;
  reg                 CsrAccessPlugin_logic_fsm_readLogic_onReadsDo;
  reg                 CsrAccessPlugin_logic_fsm_readLogic_onReadsFireDo;
  wire                when_CsrAccessPlugin_l252;
  wire       [31:0]   CsrAccessPlugin_logic_fsm_readLogic_csrValue;
  wire       [31:0]   CsrAccessPlugin_logic_fsm_writeLogic_alu_mask;
  wire       [31:0]   CsrAccessPlugin_logic_fsm_writeLogic_alu_masked;
  wire       [31:0]   CsrAccessPlugin_logic_fsm_writeLogic_alu_result;
  reg                 CsrAccessPlugin_logic_fsm_writeLogic_onWritesDo;
  reg                 CsrAccessPlugin_logic_fsm_writeLogic_onWritesFireDo;
  wire                when_CsrAccessPlugin_l346;
  wire                when_CsrAccessPlugin_l346_1;
  wire                when_CsrAccessPlugin_l346_2;
  wire                when_CsrAccessPlugin_l343;
  wire                when_CsrAccessPlugin_l343_1;
  wire                when_CsrAccessPlugin_l343_2;
  wire                fetch_logic_flushes_0_doIt;
  wire                fetch_logic_ctrls_1_throwWhen_FetchPipelinePlugin_l48;
  wire                fetch_logic_flushes_1_doIt;
  wire                fetch_logic_ctrls_2_forgetsSingleRequest_FetchPipelinePlugin_l50;
  wire       [2:0]    CsrRamPlugin_logic_writeLogic_hits;
  wire                CsrRamPlugin_logic_writeLogic_hit;
  wire       [2:0]    CsrRamPlugin_logic_writeLogic_hits_ohFirst_input;
  wire       [2:0]    CsrRamPlugin_logic_writeLogic_hits_ohFirst_masked;
  wire       [2:0]    CsrRamPlugin_logic_writeLogic_oh;
  wire                CsrRamPlugin_logic_writeLogic_port_valid;
  wire       [1:0]    CsrRamPlugin_logic_writeLogic_port_payload_address;
  wire       [31:0]   CsrRamPlugin_logic_writeLogic_port_payload_data;
  wire                _zz_TrapPlugin_logic_harts_0_crsPorts_write_ready;
  wire                _zz_CsrRamPlugin_csrMapper_write_ready;
  wire                _zz_CsrRamPlugin_setup_initPort_ready;
  wire       [1:0]    CsrRamPlugin_logic_readLogic_hits;
  wire                CsrRamPlugin_logic_readLogic_hit;
  wire       [1:0]    CsrRamPlugin_logic_readLogic_hits_ohFirst_input;
  wire       [1:0]    CsrRamPlugin_logic_readLogic_hits_ohFirst_masked;
  wire       [1:0]    CsrRamPlugin_logic_readLogic_oh;
  wire                _zz_CsrRamPlugin_logic_readLogic_sel;
  wire       [0:0]    CsrRamPlugin_logic_readLogic_sel;
  wire                CsrRamPlugin_logic_readLogic_port_cmd_valid;
  wire       [1:0]    CsrRamPlugin_logic_readLogic_port_cmd_payload;
  wire       [31:0]   CsrRamPlugin_logic_readLogic_port_rsp;
  reg        [1:0]    CsrRamPlugin_logic_readLogic_ohReg;
  reg                 CsrRamPlugin_logic_readLogic_busy;
  reg        [2:0]    CsrRamPlugin_logic_flush_counter;
  wire                CsrRamPlugin_logic_flush_done;
  wire                execute_lane0_bypasser_integer_RS1_port_valid;
  wire       [4:0]    execute_lane0_bypasser_integer_RS1_port_address;
  wire       [31:0]   execute_lane0_bypasser_integer_RS1_port_data;
  reg        [4:0]    execute_lane0_bypasser_integer_RS1_bypassEnables;
  wire       [4:0]    _zz_execute_lane0_bypasser_integer_RS1_bypassEnables_bools_0;
  wire                execute_lane0_bypasser_integer_RS1_bypassEnables_bools_0;
  wire                execute_lane0_bypasser_integer_RS1_bypassEnables_bools_1;
  wire                execute_lane0_bypasser_integer_RS1_bypassEnables_bools_2;
  wire                execute_lane0_bypasser_integer_RS1_bypassEnables_bools_3;
  wire                execute_lane0_bypasser_integer_RS1_bypassEnables_bools_4;
  reg        [4:0]    _zz_execute_lane0_bypasser_integer_RS1_sel;
  wire                execute_lane0_bypasser_integer_RS1_bypassEnables_range_0_to_1;
  wire                execute_lane0_bypasser_integer_RS1_bypassEnables_range_0_to_2;
  wire                execute_lane0_bypasser_integer_RS1_bypassEnables_range_0_to_3;
  wire       [4:0]    execute_lane0_bypasser_integer_RS1_sel;
  wire       [3:0]    _zz_execute_ctrl1_down_integer_RS1_lane0;
  (* keep , syn_keep *) reg        [31:0]   _zz_execute_ctrl1_down_integer_RS1_lane0_1 /* synthesis syn_keep = 1 */ ;
  wire                when_ExecuteLanePlugin_l196;
  wire                execute_lane0_bypasser_integer_RS1_along_bypasses_0_checks_0_selfHit;
  wire                execute_lane0_bypasser_integer_RS1_along_bypasses_0_checks_0_youngerHits_0;
  wire                execute_lane0_bypasser_integer_RS1_along_bypasses_0_checks_0_hit;
  wire                execute_lane0_bypasser_integer_RS1_along_bypasses_0_checks_1_selfHit;
  wire                execute_lane0_bypasser_integer_RS1_along_bypasses_0_checks_1_hit;
  wire       [1:0]    execute_lane0_bypasser_integer_RS1_along_bypasses_0_hits;
  wire       [2:0]    _zz_execute_ctrl2_integer_RS1_lane0_bypass;
  wire                execute_lane0_bypasser_integer_RS1_along_bypasses_1_checks_0_selfHit;
  wire                execute_lane0_bypasser_integer_RS1_along_bypasses_1_checks_0_hit;
  wire       [0:0]    execute_lane0_bypasser_integer_RS1_along_bypasses_1_hits;
  wire       [1:0]    _zz_execute_ctrl3_integer_RS1_lane0_bypass;
  wire                execute_lane0_bypasser_integer_RS2_port_valid;
  wire       [4:0]    execute_lane0_bypasser_integer_RS2_port_address;
  wire       [31:0]   execute_lane0_bypasser_integer_RS2_port_data;
  reg        [4:0]    execute_lane0_bypasser_integer_RS2_bypassEnables;
  wire       [4:0]    _zz_execute_lane0_bypasser_integer_RS2_bypassEnables_bools_0;
  wire                execute_lane0_bypasser_integer_RS2_bypassEnables_bools_0;
  wire                execute_lane0_bypasser_integer_RS2_bypassEnables_bools_1;
  wire                execute_lane0_bypasser_integer_RS2_bypassEnables_bools_2;
  wire                execute_lane0_bypasser_integer_RS2_bypassEnables_bools_3;
  wire                execute_lane0_bypasser_integer_RS2_bypassEnables_bools_4;
  reg        [4:0]    _zz_execute_lane0_bypasser_integer_RS2_sel;
  wire                execute_lane0_bypasser_integer_RS2_bypassEnables_range_0_to_1;
  wire                execute_lane0_bypasser_integer_RS2_bypassEnables_range_0_to_2;
  wire                execute_lane0_bypasser_integer_RS2_bypassEnables_range_0_to_3;
  wire       [4:0]    execute_lane0_bypasser_integer_RS2_sel;
  wire       [3:0]    _zz_execute_ctrl1_down_integer_RS2_lane0;
  (* keep , syn_keep *) reg        [31:0]   _zz_execute_ctrl1_down_integer_RS2_lane0_1 /* synthesis syn_keep = 1 */ ;
  wire                when_ExecuteLanePlugin_l196_1;
  wire                execute_lane0_bypasser_integer_RS2_along_bypasses_0_checks_0_selfHit;
  wire                execute_lane0_bypasser_integer_RS2_along_bypasses_0_checks_0_youngerHits_0;
  wire                execute_lane0_bypasser_integer_RS2_along_bypasses_0_checks_0_hit;
  wire                execute_lane0_bypasser_integer_RS2_along_bypasses_0_checks_1_selfHit;
  wire                execute_lane0_bypasser_integer_RS2_along_bypasses_0_checks_1_hit;
  wire       [1:0]    execute_lane0_bypasser_integer_RS2_along_bypasses_0_hits;
  wire       [2:0]    _zz_execute_ctrl2_integer_RS2_lane0_bypass;
  wire                execute_lane0_bypasser_integer_RS2_along_bypasses_1_checks_0_selfHit;
  wire                execute_lane0_bypasser_integer_RS2_along_bypasses_1_checks_0_hit;
  wire       [0:0]    execute_lane0_bypasser_integer_RS2_along_bypasses_1_hits;
  wire       [1:0]    _zz_execute_ctrl3_integer_RS2_lane0_bypass;
  wire                execute_lane0_logic_completions_onCtrl_0_port_valid;
  wire       [15:0]   execute_lane0_logic_completions_onCtrl_0_port_payload_uopId;
  wire                execute_lane0_logic_completions_onCtrl_0_port_payload_trap;
  wire                execute_lane0_logic_completions_onCtrl_0_port_payload_commit;
  wire                execute_lane0_logic_completions_onCtrl_1_port_valid;
  wire       [15:0]   execute_lane0_logic_completions_onCtrl_1_port_payload_uopId;
  wire                execute_lane0_logic_completions_onCtrl_1_port_payload_trap;
  wire                execute_lane0_logic_completions_onCtrl_1_port_payload_commit;
  wire                execute_lane0_logic_completions_onCtrl_2_port_valid;
  wire       [15:0]   execute_lane0_logic_completions_onCtrl_2_port_payload_uopId;
  wire                execute_lane0_logic_completions_onCtrl_2_port_payload_trap;
  wire                execute_lane0_logic_completions_onCtrl_2_port_payload_commit;
  wire       [32:0]   execute_lane0_logic_decoding_decodingBits;
  wire                _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0;
  wire                _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0;
  wire                _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0_1;
  wire                _zz_execute_ctrl1_down_late0_BranchPlugin_SEL_lane0;
  wire                _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0_1;
  wire                _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0_2;
  wire                _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0;
  wire                _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0_1;
  wire                _zz_execute_ctrl1_down_AguPlugin_LOAD_lane0;
  wire                _zz_execute_ctrl1_down_lane0_integer_WriteBackPlugin_SEL_lane0;
  wire                _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0_2;
  wire                _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0_3;
  wire                _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0_4;
  wire                _zz_execute_ctrl1_down_BYPASSED_AT_3_lane0;
  wire                _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0_2;
  wire                _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0_3;
  wire                _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_ADD_SUB_lane0;
  wire                _zz_execute_ctrl1_down_late0_SrcPlugin_logic_SRC2_CTRL_lane0;
  wire                _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_SLTX_lane0;
  wire                _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0;
  wire                _zz_execute_ctrl1_down_BarrelShifterPlugin_LEFT_lane0;
  wire                _zz_execute_ctrl1_down_CsrAccessPlugin_CSR_CLEAR_lane0;
  wire       [1:0]    _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0;
  wire       [1:0]    _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_1;
  wire       [1:0]    _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_2;
  wire                _zz_execute_ctrl1_down_late0_SrcPlugin_logic_SRC2_CTRL_lane0_1;
  wire                _zz_execute_ctrl1_down_CsrAccessPlugin_CSR_MASK_lane0;
  wire                _zz_execute_ctrl1_down_BYPASSED_AT_3_lane0_1;
  wire       [1:0]    _zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0;
  wire       [1:0]    _zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_1;
  wire       [1:0]    _zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_2;
  wire                _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0;
  wire       [2:0]    _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_1;
  wire       [2:0]    _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_2;
  wire       [2:0]    _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_3;
  wire       [1:0]    _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_1;
  wire       [1:0]    _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_2;
  wire       [1:0]    _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_3;
  wire                when_ExecuteLanePlugin_l306;
  wire                when_ExecuteLanePlugin_l306_1;
  wire                when_ExecuteLanePlugin_l306_2;
  wire                when_ExecuteLanePlugin_l306_3;
  wire                when_ExecuteLanePlugin_l306_4;
  wire                WhiteboxerPlugin_logic_csr_port_valid;
  wire       [15:0]   WhiteboxerPlugin_logic_csr_port_payload_uopId;
  wire       [11:0]   WhiteboxerPlugin_logic_csr_port_payload_address;
  wire       [31:0]   WhiteboxerPlugin_logic_csr_port_payload_write;
  wire       [31:0]   WhiteboxerPlugin_logic_csr_port_payload_read;
  wire                WhiteboxerPlugin_logic_csr_port_payload_writeDone;
  wire                WhiteboxerPlugin_logic_csr_port_payload_readDone;
  wire                WhiteboxerPlugin_logic_rfWrites_ports_0_valid;
  wire       [15:0]   WhiteboxerPlugin_logic_rfWrites_ports_0_payload_uopId;
  wire       [31:0]   WhiteboxerPlugin_logic_rfWrites_ports_0_payload_data;
  wire                WhiteboxerPlugin_logic_rfWrites_ports_1_valid;
  wire       [15:0]   WhiteboxerPlugin_logic_rfWrites_ports_1_payload_uopId;
  wire       [31:0]   WhiteboxerPlugin_logic_rfWrites_ports_1_payload_data;
  wire                WhiteboxerPlugin_logic_rfWrites_ports_2_valid;
  wire       [15:0]   WhiteboxerPlugin_logic_rfWrites_ports_2_payload_uopId;
  wire       [31:0]   WhiteboxerPlugin_logic_rfWrites_ports_2_payload_data;
  wire                WhiteboxerPlugin_logic_completions_ports_0_valid;
  wire       [15:0]   WhiteboxerPlugin_logic_completions_ports_0_payload_uopId;
  wire                WhiteboxerPlugin_logic_completions_ports_0_payload_trap;
  wire                WhiteboxerPlugin_logic_completions_ports_0_payload_commit;
  wire                WhiteboxerPlugin_logic_completions_ports_1_valid;
  wire       [15:0]   WhiteboxerPlugin_logic_completions_ports_1_payload_uopId;
  wire                WhiteboxerPlugin_logic_completions_ports_1_payload_trap;
  wire                WhiteboxerPlugin_logic_completions_ports_1_payload_commit;
  wire                WhiteboxerPlugin_logic_completions_ports_2_valid;
  wire       [15:0]   WhiteboxerPlugin_logic_completions_ports_2_payload_uopId;
  wire                WhiteboxerPlugin_logic_completions_ports_2_payload_trap;
  wire                WhiteboxerPlugin_logic_completions_ports_2_payload_commit;
  wire                WhiteboxerPlugin_logic_completions_ports_3_valid;
  wire       [15:0]   WhiteboxerPlugin_logic_completions_ports_3_payload_uopId;
  wire                WhiteboxerPlugin_logic_completions_ports_3_payload_trap;
  wire                WhiteboxerPlugin_logic_completions_ports_3_payload_commit;
  wire                WhiteboxerPlugin_logic_commits_ports_0_oh_0;
  wire                WhiteboxerPlugin_logic_commits_ports_0_valid;
  wire       [31:0]   WhiteboxerPlugin_logic_commits_ports_0_pc;
  wire       [31:0]   WhiteboxerPlugin_logic_commits_ports_0_uop;
  wire                WhiteboxerPlugin_logic_reschedules_flushes_0_valid;
  wire                WhiteboxerPlugin_logic_reschedules_flushes_0_payload_self;
  wire                WhiteboxerPlugin_logic_reschedules_flushes_1_valid;
  wire       [15:0]   WhiteboxerPlugin_logic_reschedules_flushes_1_payload_uopId;
  wire                WhiteboxerPlugin_logic_reschedules_flushes_1_payload_self;
  wire                WhiteboxerPlugin_logic_reschedules_flushes_2_valid;
  wire       [15:0]   WhiteboxerPlugin_logic_reschedules_flushes_2_payload_uopId;
  wire                WhiteboxerPlugin_logic_reschedules_flushes_2_payload_self;
  wire                WhiteboxerPlugin_logic_reschedules_flushes_3_valid;
  wire       [15:0]   WhiteboxerPlugin_logic_reschedules_flushes_3_payload_uopId;
  wire                WhiteboxerPlugin_logic_reschedules_flushes_3_payload_self;
  wire                WhiteboxerPlugin_logic_reschedules_flushes_4_valid;
  wire       [15:0]   WhiteboxerPlugin_logic_reschedules_flushes_4_payload_uopId;
  wire                WhiteboxerPlugin_logic_reschedules_flushes_4_payload_self;
  wire                WhiteboxerPlugin_logic_reschedules_flushes_5_valid;
  wire       [15:0]   WhiteboxerPlugin_logic_reschedules_flushes_5_payload_uopId;
  wire                WhiteboxerPlugin_logic_reschedules_flushes_5_payload_self;
  wire                WhiteboxerPlugin_logic_reschedules_flushes_6_valid;
  wire       [15:0]   WhiteboxerPlugin_logic_reschedules_flushes_6_payload_uopId;
  wire                WhiteboxerPlugin_logic_reschedules_flushes_6_payload_self;
  wire                late0_BranchPlugin_logic_jumpLogic_learn_asFlow_valid;
  wire       [31:0]   late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_pcOnLastSlice;
  wire       [31:0]   late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_pcTarget;
  wire                late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_taken;
  wire                late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_isBranch;
  wire                late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_isPush;
  wire                late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_isPop;
  wire                late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_wasWrong;
  wire                late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_badPredictedTarget;
  wire       [15:0]   late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_uopId;
  wire                WhiteboxerPlugin_logic_prediction_learns_0_valid;
  wire       [31:0]   WhiteboxerPlugin_logic_prediction_learns_0_payload_pcOnLastSlice;
  wire       [31:0]   WhiteboxerPlugin_logic_prediction_learns_0_payload_pcTarget;
  wire                WhiteboxerPlugin_logic_prediction_learns_0_payload_taken;
  wire                WhiteboxerPlugin_logic_prediction_learns_0_payload_isBranch;
  wire                WhiteboxerPlugin_logic_prediction_learns_0_payload_isPush;
  wire                WhiteboxerPlugin_logic_prediction_learns_0_payload_isPop;
  wire                WhiteboxerPlugin_logic_prediction_learns_0_payload_wasWrong;
  wire                WhiteboxerPlugin_logic_prediction_learns_0_payload_badPredictedTarget;
  wire       [15:0]   WhiteboxerPlugin_logic_prediction_learns_0_payload_uopId;
  wire                WhiteboxerPlugin_logic_loadExecute_fire;
  wire       [15:0]   WhiteboxerPlugin_logic_loadExecute_uopId;
  wire       [1:0]    WhiteboxerPlugin_logic_loadExecute_size;
  wire       [31:0]   WhiteboxerPlugin_logic_loadExecute_address;
  wire       [31:0]   WhiteboxerPlugin_logic_loadExecute_data;
  wire                WhiteboxerPlugin_logic_storeCommit_fire;
  wire       [15:0]   WhiteboxerPlugin_logic_storeCommit_uopId;
  wire       [11:0]   WhiteboxerPlugin_logic_storeCommit_storeId;
  wire       [1:0]    WhiteboxerPlugin_logic_storeCommit_size;
  wire       [31:0]   WhiteboxerPlugin_logic_storeCommit_address;
  wire       [31:0]   WhiteboxerPlugin_logic_storeCommit_data;
  wire                WhiteboxerPlugin_logic_storeCommit_amo;
  wire                WhiteboxerPlugin_logic_storeConditional_fire;
  wire       [15:0]   WhiteboxerPlugin_logic_storeConditional_uopId;
  wire                WhiteboxerPlugin_logic_storeConditional_miss;
  wire                WhiteboxerPlugin_logic_storeBroadcast_fire;
  wire       [11:0]   WhiteboxerPlugin_logic_storeBroadcast_storeId;
  wire                integer_RegFilePlugin_logic_writeMerges_0_bus_valid;
  wire       [4:0]    integer_RegFilePlugin_logic_writeMerges_0_bus_address;
  wire       [31:0]   integer_RegFilePlugin_logic_writeMerges_0_bus_data;
  wire       [15:0]   integer_RegFilePlugin_logic_writeMerges_0_bus_uopId;
  reg        [5:0]    integer_RegFilePlugin_logic_initalizer_counter;
  wire                integer_RegFilePlugin_logic_initalizer_done;
  wire                when_RegFilePlugin_l130;
  wire                integer_write_0_valid /* verilator public */ ;
  wire       [4:0]    integer_write_0_address /* verilator public */ ;
  wire       [31:0]   integer_write_0_data /* verilator public */ ;
  wire       [15:0]   integer_write_0_uopId /* verilator public */ ;
  wire       [0:0]    WhiteboxerPlugin_logic_wfi;
  wire                WhiteboxerPlugin_logic_perf_executeFreezed;
  wire                WhiteboxerPlugin_logic_perf_dispatchHazards;
  wire       [0:0]    WhiteboxerPlugin_logic_perf_candidatesCount;
  wire       [0:0]    WhiteboxerPlugin_logic_perf_dispatchFeedCount;
  reg                 _zz_WhiteboxerPlugin_logic_perf_executeFreezedCounter;
  reg        [59:0]   _zz_WhiteboxerPlugin_logic_perf_executeFreezedCounter_1;
  reg        [59:0]   _zz_WhiteboxerPlugin_logic_perf_executeFreezedCounter_2;
  wire       [59:0]   WhiteboxerPlugin_logic_perf_executeFreezedCounter;
  reg                 _zz_WhiteboxerPlugin_logic_perf_dispatchHazardsCounter;
  reg        [59:0]   _zz_WhiteboxerPlugin_logic_perf_dispatchHazardsCounter_1;
  reg        [59:0]   _zz_WhiteboxerPlugin_logic_perf_dispatchHazardsCounter_2;
  wire       [59:0]   WhiteboxerPlugin_logic_perf_dispatchHazardsCounter;
  wire                when_Utils_l586;
  reg                 _zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_0;
  reg        [59:0]   _zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_0_1;
  reg        [59:0]   _zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_0_2;
  wire       [59:0]   WhiteboxerPlugin_logic_perf_candidatesCountCounters_0;
  wire                when_Utils_l586_1;
  reg                 _zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_1;
  reg        [59:0]   _zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_1_1;
  reg        [59:0]   _zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_1_2;
  wire       [59:0]   WhiteboxerPlugin_logic_perf_candidatesCountCounters_1;
  wire                when_Utils_l586_2;
  reg                 _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_0;
  reg        [59:0]   _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_0_1;
  reg        [59:0]   _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_0_2;
  wire       [59:0]   WhiteboxerPlugin_logic_perf_dispatchFeedCounters_0;
  wire                when_Utils_l586_3;
  reg                 _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_1;
  reg        [59:0]   _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_1_1;
  reg        [59:0]   _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_1_2;
  wire       [59:0]   WhiteboxerPlugin_logic_perf_dispatchFeedCounters_1;
  wire                WhiteboxerPlugin_logic_trap_ports_0_valid;
  wire                WhiteboxerPlugin_logic_trap_ports_0_interrupt;
  wire       [3:0]    WhiteboxerPlugin_logic_trap_ports_0_cause;
  wire                fetch_logic_ctrls_2_up_forgetOne;
  wire                fetch_logic_ctrls_1_up_forgetOne;
  wire                when_CtrlLink_l150;
  wire                when_CtrlLink_l157;
  wire                when_StageLink_l67;
  wire                when_DecodePipelinePlugin_l70;
  reg        [1:0]    LsuPlugin_logic_flusher_stateReg;
  reg        [1:0]    LsuPlugin_logic_flusher_stateNext;
  wire                when_LsuPlugin_l363;
  wire                when_LsuPlugin_l371;
  wire                LsuPlugin_logic_flusher_onExit_IDLE;
  wire                LsuPlugin_logic_flusher_onExit_CMD;
  wire                LsuPlugin_logic_flusher_onExit_COMPLETION;
  wire                LsuPlugin_logic_flusher_onEntry_IDLE;
  wire                LsuPlugin_logic_flusher_onEntry_CMD;
  wire                LsuPlugin_logic_flusher_onEntry_COMPLETION;
  reg        [3:0]    TrapPlugin_logic_harts_0_trap_fsm_stateReg;
  reg        [3:0]    TrapPlugin_logic_harts_0_trap_fsm_stateNext;
  wire                when_TrapPlugin_l409;
  wire                when_TrapPlugin_l654;
  wire       [1:0]    switch_TrapPlugin_l655;
  wire                when_TrapPlugin_l362;
  wire                TrapPlugin_logic_harts_0_trap_fsm_onExit_RESET;
  wire                TrapPlugin_logic_harts_0_trap_fsm_onExit_RUNNING;
  wire                TrapPlugin_logic_harts_0_trap_fsm_onExit_PROCESS_1;
  wire                TrapPlugin_logic_harts_0_trap_fsm_onExit_TRAP_EPC;
  wire                TrapPlugin_logic_harts_0_trap_fsm_onExit_TRAP_TVAL;
  wire                TrapPlugin_logic_harts_0_trap_fsm_onExit_TRAP_TVEC;
  wire                TrapPlugin_logic_harts_0_trap_fsm_onExit_TRAP_APPLY;
  wire                TrapPlugin_logic_harts_0_trap_fsm_onExit_XRET_EPC;
  wire                TrapPlugin_logic_harts_0_trap_fsm_onExit_XRET_APPLY;
  wire                TrapPlugin_logic_harts_0_trap_fsm_onExit_JUMP;
  wire                TrapPlugin_logic_harts_0_trap_fsm_onExit_LSU_FLUSH;
  wire                TrapPlugin_logic_harts_0_trap_fsm_onExit_FETCH_FLUSH;
  wire                TrapPlugin_logic_harts_0_trap_fsm_onEntry_RESET;
  wire                TrapPlugin_logic_harts_0_trap_fsm_onEntry_RUNNING;
  wire                TrapPlugin_logic_harts_0_trap_fsm_onEntry_PROCESS_1;
  wire                TrapPlugin_logic_harts_0_trap_fsm_onEntry_TRAP_EPC;
  wire                TrapPlugin_logic_harts_0_trap_fsm_onEntry_TRAP_TVAL;
  wire                TrapPlugin_logic_harts_0_trap_fsm_onEntry_TRAP_TVEC;
  wire                TrapPlugin_logic_harts_0_trap_fsm_onEntry_TRAP_APPLY;
  wire                TrapPlugin_logic_harts_0_trap_fsm_onEntry_XRET_EPC;
  wire                TrapPlugin_logic_harts_0_trap_fsm_onEntry_XRET_APPLY;
  wire                TrapPlugin_logic_harts_0_trap_fsm_onEntry_JUMP;
  wire                TrapPlugin_logic_harts_0_trap_fsm_onEntry_LSU_FLUSH;
  wire                TrapPlugin_logic_harts_0_trap_fsm_onEntry_FETCH_FLUSH;
  reg        [1:0]    CsrAccessPlugin_logic_fsm_stateReg;
  reg        [1:0]    CsrAccessPlugin_logic_fsm_stateNext;
  wire                when_CsrAccessPlugin_l296;
  wire                when_CsrAccessPlugin_l325;
  wire                when_CsrAccessPlugin_l212;
  wire                CsrAccessPlugin_logic_fsm_onExit_IDLE;
  wire                CsrAccessPlugin_logic_fsm_onExit_READ;
  wire                CsrAccessPlugin_logic_fsm_onExit_WRITE;
  wire                CsrAccessPlugin_logic_fsm_onExit_COMPLETION;
  wire                CsrAccessPlugin_logic_fsm_onEntry_IDLE;
  wire                CsrAccessPlugin_logic_fsm_onEntry_READ;
  wire                CsrAccessPlugin_logic_fsm_onEntry_WRITE;
  wire                CsrAccessPlugin_logic_fsm_onEntry_COMPLETION;
  `ifndef SYNTHESIS
  reg [39:0] execute_ctrl3_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string;
  reg [31:0] execute_ctrl3_down_BranchPlugin_BRANCH_CTRL_lane0_string;
  reg [39:0] execute_ctrl4_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string;
  reg [31:0] execute_ctrl4_up_BranchPlugin_BRANCH_CTRL_lane0_string;
  reg [39:0] execute_ctrl2_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string;
  reg [39:0] execute_ctrl3_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string;
  reg [31:0] execute_ctrl3_up_BranchPlugin_BRANCH_CTRL_lane0_string;
  reg [39:0] execute_ctrl2_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string;
  reg [79:0] execute_ctrl2_up_early0_EnvPlugin_OP_lane0_string;
  reg [31:0] execute_ctrl2_up_BranchPlugin_BRANCH_CTRL_lane0_string;
  reg [39:0] execute_ctrl2_up_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string;
  reg [39:0] execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string;
  reg [79:0] execute_ctrl1_down_early0_EnvPlugin_OP_lane0_string;
  reg [31:0] execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_string;
  reg [39:0] execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string;
  reg [31:0] execute_ctrl4_down_BranchPlugin_BRANCH_CTRL_lane0_string;
  reg [31:0] execute_ctrl2_down_BranchPlugin_BRANCH_CTRL_lane0_string;
  reg [79:0] execute_ctrl2_down_early0_EnvPlugin_OP_lane0_string;
  reg [39:0] execute_ctrl4_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string;
  reg [39:0] execute_ctrl2_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string;
  reg [95:0] LsuPlugin_logic_onAddress0_ls_port_payload_op_string;
  reg [95:0] LsuPlugin_logic_onAddress0_flush_port_payload_op_string;
  reg [39:0] _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string;
  reg [39:0] _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_1_string;
  reg [39:0] _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_2_string;
  reg [31:0] _zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_string;
  reg [31:0] _zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_1_string;
  reg [31:0] _zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_2_string;
  reg [79:0] _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_1_string;
  reg [79:0] _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_2_string;
  reg [79:0] _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_3_string;
  reg [39:0] _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_1_string;
  reg [39:0] _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_2_string;
  reg [39:0] _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_3_string;
  reg [79:0] LsuPlugin_logic_flusher_stateReg_string;
  reg [79:0] LsuPlugin_logic_flusher_stateNext_string;
  reg [87:0] TrapPlugin_logic_harts_0_trap_fsm_stateReg_string;
  reg [87:0] TrapPlugin_logic_harts_0_trap_fsm_stateNext_string;
  reg [79:0] CsrAccessPlugin_logic_fsm_stateReg_string;
  reg [79:0] CsrAccessPlugin_logic_fsm_stateNext_string;
  `endif

  reg [7:0] LsuL1Plugin_logic_banks_0_mem_symbol0 [0:255];
  reg [7:0] LsuL1Plugin_logic_banks_0_mem_symbol1 [0:255];
  reg [7:0] LsuL1Plugin_logic_banks_0_mem_symbol2 [0:255];
  reg [7:0] LsuL1Plugin_logic_banks_0_mem_symbol3 [0:255];
  reg [7:0] _zz_LsuL1Plugin_logic_banks_0_memsymbol_read;
  reg [7:0] _zz_LsuL1Plugin_logic_banks_0_memsymbol_read_1;
  reg [7:0] _zz_LsuL1Plugin_logic_banks_0_memsymbol_read_2;
  reg [7:0] _zz_LsuL1Plugin_logic_banks_0_memsymbol_read_3;
  reg [23:0] LsuL1Plugin_logic_ways_0_mem [0:15];
  reg [0:0] LsuL1Plugin_logic_shared_mem [0:15];
  reg [31:0] LsuL1Plugin_logic_writeback_victimBuffer [0:15];
  (* ram_style = "block" *) reg [49:0] BtbPlugin_logic_mem [0:511];
  reg [31:0] FetchL1Plugin_logic_banks_0_mem [0:255];
  reg [23:0] FetchL1Plugin_logic_ways_0_mem [0:15];
  reg [31:0] CsrRamPlugin_logic_mem [0:3];
  function [1:0] zz_FetchL1Plugin_logic_trapPort_payload_arg(input dummy);
    begin
      zz_FetchL1Plugin_logic_trapPort_payload_arg = 2'b00;
      zz_FetchL1Plugin_logic_trapPort_payload_arg[1 : 0] = 2'b10;
    end
  endfunction
  wire [1:0] _zz_26;

  assign _zz_when_1 = (! FetchL1Plugin_logic_refill_slots_0_valid);
  assign _zz_early0_IntAluPlugin_logic_alu_result = (early0_IntAluPlugin_logic_alu_bitwise | _zz_early0_IntAluPlugin_logic_alu_result_1);
  assign _zz_early0_IntAluPlugin_logic_alu_result_1 = (execute_ctrl2_down_early0_IntAluPlugin_ALU_ADD_SUB_lane0 ? execute_ctrl2_down_early0_SrcPlugin_ADD_SUB_lane0 : 32'h0);
  assign _zz_early0_IntAluPlugin_logic_alu_result_2 = (execute_ctrl2_down_early0_IntAluPlugin_ALU_SLTX_lane0 ? _zz_early0_IntAluPlugin_logic_alu_result_3 : 32'h0);
  assign _zz_early0_IntAluPlugin_logic_alu_result_3 = _zz_early0_IntAluPlugin_logic_alu_result_4;
  assign _zz_early0_IntAluPlugin_logic_alu_result_5 = execute_ctrl2_down_early0_SrcPlugin_LESS_lane0;
  assign _zz_early0_IntAluPlugin_logic_alu_result_4 = {31'd0, _zz_early0_IntAluPlugin_logic_alu_result_5};
  assign _zz_early0_BarrelShifterPlugin_logic_shift_amplitude = execute_ctrl2_down_early0_SrcPlugin_SRC2_lane0[4 : 0];
  assign _zz_early0_BarrelShifterPlugin_logic_shift_reversed = {execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[0],{execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[1],{execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[2],{execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[3],{execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[4],{execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[5],{execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[6],{execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[7],{execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[8],{_zz_early0_BarrelShifterPlugin_logic_shift_reversed_1,{_zz_early0_BarrelShifterPlugin_logic_shift_reversed_2,_zz_early0_BarrelShifterPlugin_logic_shift_reversed_3}}}}}}}}}}};
  assign _zz_early0_BarrelShifterPlugin_logic_shift_shifted = ($signed(_zz_early0_BarrelShifterPlugin_logic_shift_shifted_1) >>> early0_BarrelShifterPlugin_logic_shift_amplitude);
  assign _zz_early0_BarrelShifterPlugin_logic_shift_shifted_1 = {(execute_ctrl2_down_BarrelShifterPlugin_SIGNED_lane0 && execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[31]),early0_BarrelShifterPlugin_logic_shift_reversed};
  assign _zz_early0_BarrelShifterPlugin_logic_shift_patched = {early0_BarrelShifterPlugin_logic_shift_shifted[0],{early0_BarrelShifterPlugin_logic_shift_shifted[1],{early0_BarrelShifterPlugin_logic_shift_shifted[2],{early0_BarrelShifterPlugin_logic_shift_shifted[3],{early0_BarrelShifterPlugin_logic_shift_shifted[4],{early0_BarrelShifterPlugin_logic_shift_shifted[5],{early0_BarrelShifterPlugin_logic_shift_shifted[6],{early0_BarrelShifterPlugin_logic_shift_shifted[7],{early0_BarrelShifterPlugin_logic_shift_shifted[8],{_zz_early0_BarrelShifterPlugin_logic_shift_patched_1,{_zz_early0_BarrelShifterPlugin_logic_shift_patched_2,_zz_early0_BarrelShifterPlugin_logic_shift_patched_3}}}}}}}}}}};
  assign _zz_LsuL1Plugin_logic_writeback_read_wordIndex_1 = LsuL1Plugin_logic_writeback_read_slotRead_valid;
  assign _zz_LsuL1Plugin_logic_writeback_read_wordIndex = {3'd0, _zz_LsuL1Plugin_logic_writeback_read_wordIndex_1};
  assign _zz_LsuL1Plugin_logic_writeback_write_wordIndex_1 = (LsuL1Plugin_logic_writeback_write_bufferRead_fire && 1'b1);
  assign _zz_LsuL1Plugin_logic_writeback_write_wordIndex = {3'd0, _zz_LsuL1Plugin_logic_writeback_write_wordIndex_1};
  assign _zz_LsuL1Plugin_logic_lsu_ctrl_refillWayNeedWriteback = (execute_ctrl4_down_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_loaded & execute_ctrl4_down_LsuL1Plugin_logic_SHARED_lane0_dirty);
  assign _zz_LsuL1Plugin_logic_lsu_ctrl_doWrite = (_zz_execute_ctrl4_down_LsuL1Plugin_logic_MUXED_DATA_lane0 ? (1'b1 && (! execute_ctrl4_down_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_fault)) : 1'b0);
  assign _zz_when = 1'b1;
  assign _zz_LsuL1Plugin_logic_shared_write_payload_data_dirty = 1'b0;
  assign _zz_execute_ctrl2_down_MUL_SRC1_lane0 = {(execute_ctrl2_down_RsUnsignedPlugin_RS1_SIGNED_lane0 && execute_ctrl2_up_integer_RS1_lane0[31]),execute_ctrl2_up_integer_RS1_lane0};
  assign _zz_execute_ctrl2_down_MUL_SRC2_lane0 = {(execute_ctrl2_down_RsUnsignedPlugin_RS2_SIGNED_lane0 && execute_ctrl2_up_integer_RS2_lane0[31]),execute_ctrl2_up_integer_RS2_lane0};
  assign _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_1_lane0_1 = ($signed(_zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_1_lane0_2) * $signed(_zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_1_lane0_3));
  assign _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_1_lane0 = {{13{_zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_1_lane0_1[33]}}, _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_1_lane0_1};
  assign _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_1_lane0_2 = {1'b0,execute_ctrl2_down_MUL_SRC1_lane0[16 : 0]};
  assign _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_1_lane0_3 = execute_ctrl2_down_MUL_SRC2_lane0[32 : 17];
  assign _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_2_lane0_1 = ($signed(_zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_2_lane0_2) * $signed(_zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_2_lane0_3));
  assign _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_2_lane0 = {{13{_zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_2_lane0_1[33]}}, _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_2_lane0_1};
  assign _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_2_lane0_2 = execute_ctrl2_down_MUL_SRC1_lane0[32 : 17];
  assign _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_2_lane0_3 = {1'b0,execute_ctrl2_down_MUL_SRC2_lane0[16 : 0]};
  assign _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_3_lane0_1 = ($signed(_zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_3_lane0_2) * $signed(_zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_3_lane0_3));
  assign _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_3_lane0 = _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_3_lane0_1[29:0];
  assign _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_3_lane0_2 = execute_ctrl2_down_MUL_SRC1_lane0[32 : 17];
  assign _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_3_lane0_3 = execute_ctrl2_down_MUL_SRC2_lane0[32 : 17];
  assign _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0_3 = (_zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0_4 + _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0_5);
  assign _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0_4 = {2'd0, _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0};
  assign _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0_5 = {2'd0, _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0_1};
  assign _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0_6 = {2'd0, _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0_2};
  assign _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0_3 = (_zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0_4 + _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0_5);
  assign _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0_4 = {2'd0, _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0};
  assign _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0_5 = {2'd0, _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0_1};
  assign _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0_6 = {2'd0, _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0_2};
  assign _zz_execute_ctrl2_down_RsUnsignedPlugin_RS1_UNSIGNED_lane0_1 = execute_ctrl2_down_RsUnsignedPlugin_RS1_REVERT_lane0;
  assign _zz_execute_ctrl2_down_RsUnsignedPlugin_RS1_UNSIGNED_lane0 = {31'd0, _zz_execute_ctrl2_down_RsUnsignedPlugin_RS1_UNSIGNED_lane0_1};
  assign _zz_execute_ctrl2_down_RsUnsignedPlugin_RS2_UNSIGNED_lane0_1 = execute_ctrl2_down_RsUnsignedPlugin_RS2_REVERT_lane0;
  assign _zz_execute_ctrl2_down_RsUnsignedPlugin_RS2_UNSIGNED_lane0 = {31'd0, _zz_execute_ctrl2_down_RsUnsignedPlugin_RS2_UNSIGNED_lane0_1};
  assign _zz_execute_ctrl2_down_DivPlugin_DIV_RESULT_lane0_1 = ((early0_DivPlugin_logic_processing_divRevertResult ? (~ _zz_execute_ctrl2_down_DivPlugin_DIV_RESULT_lane0) : _zz_execute_ctrl2_down_DivPlugin_DIV_RESULT_lane0) + _zz_execute_ctrl2_down_DivPlugin_DIV_RESULT_lane0_2);
  assign _zz_execute_ctrl2_down_DivPlugin_DIV_RESULT_lane0_3 = early0_DivPlugin_logic_processing_divRevertResult;
  assign _zz_execute_ctrl2_down_DivPlugin_DIV_RESULT_lane0_2 = {31'd0, _zz_execute_ctrl2_down_DivPlugin_DIV_RESULT_lane0_3};
  assign _zz_late0_IntAluPlugin_logic_alu_result = (late0_IntAluPlugin_logic_alu_bitwise | _zz_late0_IntAluPlugin_logic_alu_result_1);
  assign _zz_late0_IntAluPlugin_logic_alu_result_1 = (execute_ctrl4_down_late0_IntAluPlugin_ALU_ADD_SUB_lane0 ? execute_ctrl4_down_late0_SrcPlugin_ADD_SUB_lane0 : 32'h0);
  assign _zz_late0_IntAluPlugin_logic_alu_result_2 = (execute_ctrl4_down_late0_IntAluPlugin_ALU_SLTX_lane0 ? _zz_late0_IntAluPlugin_logic_alu_result_3 : 32'h0);
  assign _zz_late0_IntAluPlugin_logic_alu_result_3 = _zz_late0_IntAluPlugin_logic_alu_result_4;
  assign _zz_late0_IntAluPlugin_logic_alu_result_5 = execute_ctrl4_down_late0_SrcPlugin_LESS_lane0;
  assign _zz_late0_IntAluPlugin_logic_alu_result_4 = {31'd0, _zz_late0_IntAluPlugin_logic_alu_result_5};
  assign _zz_late0_BarrelShifterPlugin_logic_shift_amplitude = execute_ctrl4_down_late0_SrcPlugin_SRC2_lane0[4 : 0];
  assign _zz_late0_BarrelShifterPlugin_logic_shift_reversed = {execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[0],{execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[1],{execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[2],{execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[3],{execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[4],{execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[5],{execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[6],{execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[7],{execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[8],{_zz_late0_BarrelShifterPlugin_logic_shift_reversed_1,{_zz_late0_BarrelShifterPlugin_logic_shift_reversed_2,_zz_late0_BarrelShifterPlugin_logic_shift_reversed_3}}}}}}}}}}};
  assign _zz_late0_BarrelShifterPlugin_logic_shift_shifted = ($signed(_zz_late0_BarrelShifterPlugin_logic_shift_shifted_1) >>> late0_BarrelShifterPlugin_logic_shift_amplitude);
  assign _zz_late0_BarrelShifterPlugin_logic_shift_shifted_1 = {(execute_ctrl4_down_BarrelShifterPlugin_SIGNED_lane0 && execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[31]),late0_BarrelShifterPlugin_logic_shift_reversed};
  assign _zz_late0_BarrelShifterPlugin_logic_shift_patched = {late0_BarrelShifterPlugin_logic_shift_shifted[0],{late0_BarrelShifterPlugin_logic_shift_shifted[1],{late0_BarrelShifterPlugin_logic_shift_shifted[2],{late0_BarrelShifterPlugin_logic_shift_shifted[3],{late0_BarrelShifterPlugin_logic_shift_shifted[4],{late0_BarrelShifterPlugin_logic_shift_shifted[5],{late0_BarrelShifterPlugin_logic_shift_shifted[6],{late0_BarrelShifterPlugin_logic_shift_shifted[7],{late0_BarrelShifterPlugin_logic_shift_shifted[8],{_zz_late0_BarrelShifterPlugin_logic_shift_patched_1,{_zz_late0_BarrelShifterPlugin_logic_shift_patched_2,_zz_late0_BarrelShifterPlugin_logic_shift_patched_3}}}}}}}}}}};
  assign _zz_FetchL1Plugin_logic_ctrl_dataAccessFault = (fetch_logic_ctrls_2_down_FetchL1Plugin_logic_WAYS_HITS_0 ? fetch_logic_ctrls_2_down_FetchL1Plugin_logic_WAYS_TAGS_0_error : 1'b0);
  assign _zz_WhiteboxerPlugin_logic_decodes_0_pc = {32'd0, decode_ctrls_0_down_PC_0};
  assign _zz_FetchL1Plugin_pmaBuilder_onTransfers_0_addressHit = (|_zz_FetchL1Plugin_logic_ctrl_pmaPort_rsp_io);
  assign _zz_FetchL1Plugin_logic_ctrl_pmaPort_rsp_io_1 = (|_zz_FetchL1Plugin_logic_ctrl_pmaPort_rsp_io);
  assign _zz_FetchL1WishbonePlugin_logic_bus_ADR = (FetchL1Plugin_logic_bus_cmd_payload_address >>> 3'd6);
  assign _zz__zz_execute_ctrl1_down_early0_SrcPlugin_SRC2_lane0 = execute_ctrl1_down_Decode_UOP_lane0[31 : 20];
  assign _zz__zz_execute_ctrl1_down_early0_SrcPlugin_SRC2_lane0_1 = {execute_ctrl1_down_Decode_UOP_lane0[31 : 25],execute_ctrl1_down_Decode_UOP_lane0[11 : 7]};
  assign _zz_execute_ctrl2_down_early0_SrcPlugin_ADD_SUB_lane0 = ($signed(execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0) + $signed(early0_SrcPlugin_logic_addsub_combined_rs2Patched));
  assign _zz_execute_ctrl2_down_early0_SrcPlugin_ADD_SUB_lane0_1 = _zz_execute_ctrl2_down_early0_SrcPlugin_ADD_SUB_lane0_2;
  assign _zz_execute_ctrl2_down_early0_SrcPlugin_ADD_SUB_lane0_3 = execute_ctrl2_down_SrcStageables_REVERT_lane0;
  assign _zz_execute_ctrl2_down_early0_SrcPlugin_ADD_SUB_lane0_2 = {31'd0, _zz_execute_ctrl2_down_early0_SrcPlugin_ADD_SUB_lane0_3};
  assign _zz__zz_execute_ctrl3_down_late0_SrcPlugin_SRC2_lane0 = execute_ctrl3_down_Decode_UOP_lane0[31 : 20];
  assign _zz_execute_ctrl4_down_late0_SrcPlugin_ADD_SUB_lane0 = ($signed(execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0) + $signed(late0_SrcPlugin_logic_addsub_combined_rs2Patched));
  assign _zz_execute_ctrl4_down_late0_SrcPlugin_ADD_SUB_lane0_1 = _zz_execute_ctrl4_down_late0_SrcPlugin_ADD_SUB_lane0_2;
  assign _zz_execute_ctrl4_down_late0_SrcPlugin_ADD_SUB_lane0_3 = execute_ctrl4_down_SrcStageables_REVERT_lane0;
  assign _zz_execute_ctrl4_down_late0_SrcPlugin_ADD_SUB_lane0_2 = {31'd0, _zz_execute_ctrl4_down_late0_SrcPlugin_ADD_SUB_lane0_3};
  assign _zz_early0_EnvPlugin_logic_trapPort_payload_code = {2'd0, early0_EnvPlugin_logic_exe_privilege};
  assign _zz_early0_BranchPlugin_pcCalc_target_b = {{{{execute_ctrl2_down_Decode_UOP_lane0[31],execute_ctrl2_down_Decode_UOP_lane0[19 : 12]},execute_ctrl2_down_Decode_UOP_lane0[20]},execute_ctrl2_down_Decode_UOP_lane0[30 : 21]},1'b0};
  assign _zz_early0_BranchPlugin_pcCalc_target_b_1 = execute_ctrl2_down_Decode_UOP_lane0[31 : 20];
  assign _zz_early0_BranchPlugin_pcCalc_target_b_2 = {{{{execute_ctrl2_down_Decode_UOP_lane0[31],execute_ctrl2_down_Decode_UOP_lane0[7]},execute_ctrl2_down_Decode_UOP_lane0[30 : 25]},execute_ctrl2_down_Decode_UOP_lane0[11 : 8]},1'b0};
  assign _zz_early0_BranchPlugin_pcCalc_slices_1 = 1'b0;
  assign _zz_early0_BranchPlugin_pcCalc_slices = {1'd0, _zz_early0_BranchPlugin_pcCalc_slices_1};
  assign _zz_execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_TRUE_lane0 = ($signed(early0_BranchPlugin_pcCalc_target_a) + $signed(early0_BranchPlugin_pcCalc_target_b));
  assign _zz_execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_FALSE_lane0_1 = ({2'd0,early0_BranchPlugin_pcCalc_slices} <<< 2'd2);
  assign _zz_execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_FALSE_lane0 = {28'd0, _zz_execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_FALSE_lane0_1};
  assign _zz_execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_LAST_SLICE_lane0_1 = 2'b00;
  assign _zz_execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_LAST_SLICE_lane0 = {30'd0, _zz_execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_LAST_SLICE_lane0_1};
  assign _zz_LsuPlugin_logic_onAddress0_ls_storeId_1 = LsuPlugin_logic_onAddress0_ls_port_fire;
  assign _zz_LsuPlugin_logic_onAddress0_ls_storeId = {11'd0, _zz_LsuPlugin_logic_onAddress0_ls_storeId_1};
  assign _zz_LsuPlugin_logic_onAddress0_flush_port_payload_address = ({6'd0,LsuPlugin_logic_flusher_cmdCounter} <<< 3'd6);
  assign _zz_LsuPlugin_logic_trapPort_payload_code = (execute_ctrl4_down_LsuPlugin_logic_preCtrl_MISS_ALIGNED_lane0 ? (execute_ctrl4_down_LsuL1_STORE_lane0 ? 3'b110 : 3'b100) : 3'b000);
  assign _zz_LsuPlugin_logic_flusher_cmdCounter = execute_ctrl4_down_LsuL1_MIXED_ADDRESS_lane0[9 : 6];
  assign _zz_LsuPlugin_pmaBuilder_l1_onTransfers_0_addressHit = (|_zz_LsuPlugin_logic_onPma_cached_rsp_io);
  assign _zz_LsuPlugin_logic_onPma_cached_rsp_io_1 = (|_zz_LsuPlugin_logic_onPma_cached_rsp_io);
  assign _zz_LsuPlugin_pmaBuilder_io_onTransfers_0_addressHit = (|((LsuPlugin_pmaBuilder_io_addressBits & 32'h0) == 32'h0));
  assign _zz_LsuPlugin_logic_onPma_io_rsp_io = (|((LsuPlugin_pmaBuilder_io_addressBits & 32'h80000000) == 32'h0));
  assign _zz_decode_ctrls_1_down_RS1_ENABLE_0 = (|{((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h00000044) == 32'h0),{_zz_decode_ctrls_1_down_DispatchPlugin_MAY_FLUSH_0,{((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h00006004) == 32'h00002000),((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h00005004) == 32'h00001000)}}});
  assign _zz_decode_ctrls_1_down_RS2_ENABLE_0 = (|{((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h00000034) == 32'h00000020),((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h00000064) == 32'h00000020)});
  assign _zz_decode_ctrls_1_down_RD_ENABLE_0 = (|{_zz_decode_ctrls_1_down_DispatchPlugin_logic_LANES_LAYER_HIT_1_0,{((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h00001010) == 32'h00001010),{((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h00002010) == 32'h00002010),{((decode_ctrls_1_down_Decode_INSTRUCTION_0 & _zz_decode_ctrls_1_down_RD_ENABLE_0_1) == 32'h00000010),{(_zz_decode_ctrls_1_down_RD_ENABLE_0_2 == _zz_decode_ctrls_1_down_RD_ENABLE_0_3),(_zz_decode_ctrls_1_down_RD_ENABLE_0_4 == _zz_decode_ctrls_1_down_RD_ENABLE_0_5)}}}}});
  assign _zz_DecoderPlugin_logic_laneLogic_0_fixer_isJb = (|((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h00000050) == 32'h00000040));
  assign _zz_DecoderPlugin_logic_forgetPort_payload_pcOnLastSlice_1 = ((! decode_ctrls_1_down_Prediction_ALIGN_REDO_0) ? 2'b00 : 2'b00);
  assign _zz_DecoderPlugin_logic_forgetPort_payload_pcOnLastSlice = {30'd0, _zz_DecoderPlugin_logic_forgetPort_payload_pcOnLastSlice_1};
  assign _zz_BtbPlugin_logic_memWrite_payload_address = (LearnPlugin_logic_learn_payload_pcOnLastSlice >>> 2'd2);
  assign _zz_decode_ctrls_1_down_DecoderPlugin_logic_NEED_FPU_0 = _zz_decode_ctrls_1_down_DecoderPlugin_logic_NEED_FPU_0_1[0];
  assign _zz_decode_ctrls_1_down_DecoderPlugin_logic_NEED_FPU_0_1 = 1'b0;
  assign _zz_decode_ctrls_1_down_DecoderPlugin_logic_NEED_RM_0 = _zz_decode_ctrls_1_down_DecoderPlugin_logic_NEED_RM_0_1[0];
  assign _zz_decode_ctrls_1_down_DecoderPlugin_logic_NEED_RM_0_1 = 1'b0;
  assign _zz_decode_ctrls_1_down_DispatchPlugin_logic_LANES_LAYER_HIT_0_0 = _zz_decode_ctrls_1_down_DispatchPlugin_logic_LANES_LAYER_HIT_0_0_1[0];
  assign _zz_decode_ctrls_1_down_DispatchPlugin_logic_LANES_LAYER_HIT_0_0_1 = (|_zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_1_ENABLES_0_0);
  assign _zz_decode_ctrls_1_down_DispatchPlugin_logic_LANES_LAYER_HIT_1_0_1 = _zz_decode_ctrls_1_down_DispatchPlugin_logic_LANES_LAYER_HIT_1_0_2[0];
  assign _zz_decode_ctrls_1_down_DispatchPlugin_logic_LANES_LAYER_HIT_1_0_2 = (|{_zz_decode_ctrls_1_down_DispatchPlugin_logic_LANES_LAYER_HIT_1_0,{((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h00000030) == 32'h00000010),{((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h0000004c) == 32'h00000004),{((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h02000050) == 32'h00000010),((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h00000054) == 32'h00000040)}}}});
  assign _zz_decode_ctrls_1_down_DispatchPlugin_MAY_FLUSH_0_1 = _zz_decode_ctrls_1_down_DispatchPlugin_MAY_FLUSH_0_2[0];
  assign _zz_decode_ctrls_1_down_DispatchPlugin_MAY_FLUSH_0_2 = (|{_zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_0_0,{((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h00001010) == 32'h00001000),_zz_decode_ctrls_1_down_DispatchPlugin_MAY_FLUSH_0}});
  assign _zz_decode_ctrls_1_down_DispatchPlugin_DONT_FLUSH_0 = _zz_decode_ctrls_1_down_DispatchPlugin_DONT_FLUSH_0_1[0];
  assign _zz_decode_ctrls_1_down_DispatchPlugin_DONT_FLUSH_0_1 = (|{_zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_4_0_1,_zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_4_0});
  assign _zz_decode_ctrls_1_down_DispatchPlugin_DONT_FLUSH_FROM_LANES_0 = _zz_decode_ctrls_1_down_DispatchPlugin_DONT_FLUSH_FROM_LANES_0_1[0];
  assign _zz_decode_ctrls_1_down_DispatchPlugin_DONT_FLUSH_FROM_LANES_0_1 = (|{_zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_4_0_1,_zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_4_0});
  assign _zz_decode_ctrls_1_down_DispatchPlugin_FENCE_OLDER_0 = _zz_decode_ctrls_1_down_DispatchPlugin_FENCE_OLDER_0_1[0];
  assign _zz_decode_ctrls_1_down_DispatchPlugin_FENCE_OLDER_0_1 = (|{_zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_4_0_1,_zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_4_0});
  assign _zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_3_0 = _zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_3_0_1[0];
  assign _zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_3_0_1 = (|{_zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_4_0_1,_zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_4_0});
  assign _zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_4_0_2 = _zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_4_0_3[0];
  assign _zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_4_0_3 = (|{_zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_4_0_1,_zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_4_0});
  assign _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_0_ENABLES_0_0 = _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_0_ENABLES_0_0_1[0];
  assign _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_0_ENABLES_0_0_1 = (|_zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_1_ENABLES_0_0);
  assign _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_0_0_1 = _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_0_0_2[0];
  assign _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_0_0_2 = (|{_zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_0_0,((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h00000010) == 32'h00000010)});
  assign _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_1_0 = _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_1_0_1[0];
  assign _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_1_0_1 = (|_zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_1_ENABLES_0_0);
  assign _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_0_ENABLES_0_0 = _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_0_ENABLES_0_0_1[0];
  assign _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_0_ENABLES_0_0_1 = (|_zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_1_ENABLES_0_0);
  assign _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_1_ENABLES_0_0_1 = _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_1_ENABLES_0_0_2[0];
  assign _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_1_ENABLES_0_0_2 = (|_zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_1_ENABLES_0_0);
  assign _zz_BtbPlugin_logic_memWrite_payload_address_1 = (DecoderPlugin_logic_forgetPort_payload_pcOnLastSlice >>> 2'd2);
  assign _zz_BtbPlugin_logic_memRead_cmd_payload = (fetch_logic_ctrls_0_down_Fetch_WORD_PC >>> 2'd2);
  assign _zz_TrapPlugin_logic_harts_0_trap_fsm_jumpTarget_1 = ({2'd0,TrapPlugin_logic_harts_0_trap_fsm_jumpOffset} <<< 2'd2);
  assign _zz_TrapPlugin_logic_harts_0_trap_fsm_jumpTarget = {29'd0, _zz_TrapPlugin_logic_harts_0_trap_fsm_jumpTarget_1};
  assign _zz_PcPlugin_logic_harts_0_self_pc_1 = (PcPlugin_logic_harts_0_self_increment ? 3'b100 : 3'b000);
  assign _zz_PcPlugin_logic_harts_0_self_pc = {29'd0, _zz_PcPlugin_logic_harts_0_self_pc_1};
  assign _zz_PcPlugin_logic_harts_0_aggregator_fault = ((((_zz_PcPlugin_logic_harts_0_aggregator_target ? TrapPlugin_logic_harts_0_trap_pcPort_payload_fault : 1'b0) | (_zz_PcPlugin_logic_harts_0_aggregator_target_1 ? late0_BranchPlugin_logic_pcPort_payload_fault : 1'b0)) | ((_zz_PcPlugin_logic_harts_0_aggregator_target_2 ? early0_BranchPlugin_logic_pcPort_payload_fault : 1'b0) | (_zz_PcPlugin_logic_harts_0_aggregator_target_3 ? BtbPlugin_logic_pcPort_payload_fault : 1'b0))) | (_zz_PcPlugin_logic_harts_0_aggregator_target_4 ? PcPlugin_logic_harts_0_self_flow_payload_fault : 1'b0));
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_6 = ((_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue && REG_CSR_3858) ? 6'h2e : 6'h0);
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_5 = {26'd0, _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_6};
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_9 = ({7'd0,(_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_1 ? PrivilegedPlugin_logic_harts_0_m_status_mpie : 1'b0)} <<< 3'd7);
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_8 = {24'd0, _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_9};
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_11 = ({3'd0,(_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_1 ? PrivilegedPlugin_logic_harts_0_m_status_mie : 1'b0)} <<< 2'd3);
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_10 = {28'd0, _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_11};
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_13 = ({11'd0,(_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_1 ? PrivilegedPlugin_logic_harts_0_m_status_mpp : 2'b00)} <<< 4'd11);
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_12 = {19'd0, _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_13};
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_14 = ({31'd0,(_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_1 ? PrivilegedPlugin_logic_harts_0_m_status_sd : 1'b0)} <<< 5'd31);
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_16 = ({17'd0,(_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_1 ? PrivilegedPlugin_logic_harts_0_m_status_mprv : 1'b0)} <<< 5'd17);
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_15 = {14'd0, _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_16};
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_17 = ({31'd0,(_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_2 ? PrivilegedPlugin_logic_harts_0_m_cause_interrupt : 1'b0)} <<< 5'd31);
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_19 = (_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_2 ? PrivilegedPlugin_logic_harts_0_m_cause_code : 4'b0000);
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_18 = {28'd0, _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_19};
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_21 = ({11'd0,(_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_3 ? PrivilegedPlugin_logic_harts_0_m_ip_meip : 1'b0)} <<< 4'd11);
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_20 = {20'd0, _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_21};
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_23 = ({7'd0,(_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_3 ? PrivilegedPlugin_logic_harts_0_m_ip_mtip : 1'b0)} <<< 3'd7);
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_22 = {24'd0, _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_23};
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_25 = ({3'd0,(_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_3 ? PrivilegedPlugin_logic_harts_0_m_ip_msip : 1'b0)} <<< 2'd3);
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_24 = {28'd0, _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_25};
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_27 = ({11'd0,(_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_4 ? PrivilegedPlugin_logic_harts_0_m_ie_meie : 1'b0)} <<< 4'd11);
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_26 = {20'd0, _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_27};
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_29 = ({7'd0,(_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_4 ? PrivilegedPlugin_logic_harts_0_m_ie_mtie : 1'b0)} <<< 3'd7);
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_28 = {24'd0, _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_29};
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_31 = ({3'd0,(_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_4 ? PrivilegedPlugin_logic_harts_0_m_ie_msie : 1'b0)} <<< 2'd3);
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_30 = {28'd0, _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_31};
  assign _zz_CsrAccessPlugin_logic_fsm_writeLogic_alu_mask_1 = CsrAccessPlugin_logic_fsm_interface_uop[19 : 15];
  assign _zz_CsrAccessPlugin_logic_fsm_writeLogic_alu_mask = {27'd0, _zz_CsrAccessPlugin_logic_fsm_writeLogic_alu_mask_1};
  assign _zz_CsrRamPlugin_logic_writeLogic_hits_ohFirst_masked = (CsrRamPlugin_logic_writeLogic_hits_ohFirst_input - 3'b001);
  assign _zz_CsrRamPlugin_logic_readLogic_hits_ohFirst_masked = (CsrRamPlugin_logic_readLogic_hits_ohFirst_input - 2'b01);
  assign _zz_CsrRamPlugin_logic_flush_counter_1 = (! CsrRamPlugin_logic_flush_done);
  assign _zz_CsrRamPlugin_logic_flush_counter = {2'd0, _zz_CsrRamPlugin_logic_flush_counter_1};
  assign _zz_execute_ctrl1_down_early0_IntAluPlugin_SEL_lane0 = _zz_execute_ctrl1_down_early0_IntAluPlugin_SEL_lane0_1[0];
  assign _zz_execute_ctrl1_down_early0_IntAluPlugin_SEL_lane0_1 = (|{((execute_lane0_logic_decoding_decodingBits & 33'h100002030) == 33'h100002010),{((execute_lane0_logic_decoding_decodingBits & 33'h10000004c) == 33'h100000004),{((execute_lane0_logic_decoding_decodingBits & 33'h100001030) == 33'h100000010),{((execute_lane0_logic_decoding_decodingBits & _zz_execute_ctrl1_down_early0_IntAluPlugin_SEL_lane0_2) == 33'h100002010),((execute_lane0_logic_decoding_decodingBits & _zz_execute_ctrl1_down_early0_IntAluPlugin_SEL_lane0_3) == 33'h100000010)}}}});
  assign _zz_execute_ctrl1_down_early0_BarrelShifterPlugin_SEL_lane0 = _zz_execute_ctrl1_down_early0_BarrelShifterPlugin_SEL_lane0_1[0];
  assign _zz_execute_ctrl1_down_early0_BarrelShifterPlugin_SEL_lane0_1 = (|{((execute_lane0_logic_decoding_decodingBits & 33'h100003034) == 33'h100001010),((execute_lane0_logic_decoding_decodingBits & 33'h102003054) == 33'h100001010)});
  assign _zz_execute_ctrl1_down_early0_BranchPlugin_SEL_lane0 = _zz_execute_ctrl1_down_early0_BranchPlugin_SEL_lane0_1[0];
  assign _zz_execute_ctrl1_down_early0_BranchPlugin_SEL_lane0_1 = (|_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0);
  assign _zz_execute_ctrl1_down_early0_MulPlugin_SEL_lane0 = _zz_execute_ctrl1_down_early0_MulPlugin_SEL_lane0_1[0];
  assign _zz_execute_ctrl1_down_early0_MulPlugin_SEL_lane0_1 = (|((execute_lane0_logic_decoding_decodingBits & 33'h002004074) == 33'h002000030));
  assign _zz_execute_ctrl1_down_early0_DivPlugin_SEL_lane0 = _zz_execute_ctrl1_down_early0_DivPlugin_SEL_lane0_1[0];
  assign _zz_execute_ctrl1_down_early0_DivPlugin_SEL_lane0_1 = (|_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0);
  assign _zz_execute_ctrl1_down_early0_EnvPlugin_SEL_lane0 = _zz_execute_ctrl1_down_early0_EnvPlugin_SEL_lane0_1[0];
  assign _zz_execute_ctrl1_down_early0_EnvPlugin_SEL_lane0_1 = (|{_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0_1,((execute_lane0_logic_decoding_decodingBits & 33'h000003050) == 33'h000000050)});
  assign _zz_execute_ctrl1_down_late0_IntAluPlugin_SEL_lane0 = _zz_execute_ctrl1_down_late0_IntAluPlugin_SEL_lane0_1[0];
  assign _zz_execute_ctrl1_down_late0_IntAluPlugin_SEL_lane0_1 = (|{((execute_lane0_logic_decoding_decodingBits & 33'h100000044) == 33'h000000004),{((execute_lane0_logic_decoding_decodingBits & 33'h100002040) == 33'h000002000),((execute_lane0_logic_decoding_decodingBits & 33'h100001040) == 33'h0)}});
  assign _zz_execute_ctrl1_down_late0_BarrelShifterPlugin_SEL_lane0 = _zz_execute_ctrl1_down_late0_BarrelShifterPlugin_SEL_lane0_1[0];
  assign _zz_execute_ctrl1_down_late0_BarrelShifterPlugin_SEL_lane0_1 = (|((execute_lane0_logic_decoding_decodingBits & 33'h100003044) == 33'h000001000));
  assign _zz_execute_ctrl1_down_late0_BranchPlugin_SEL_lane0_1 = _zz_execute_ctrl1_down_late0_BranchPlugin_SEL_lane0_2[0];
  assign _zz_execute_ctrl1_down_late0_BranchPlugin_SEL_lane0_2 = (|_zz_execute_ctrl1_down_late0_BranchPlugin_SEL_lane0);
  assign _zz_execute_ctrl1_down_CsrAccessPlugin_SEL_lane0 = _zz_execute_ctrl1_down_CsrAccessPlugin_SEL_lane0_1[0];
  assign _zz_execute_ctrl1_down_CsrAccessPlugin_SEL_lane0_1 = (|{_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0_2,_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0_1});
  assign _zz_execute_ctrl1_down_AguPlugin_SEL_lane0 = _zz_execute_ctrl1_down_AguPlugin_SEL_lane0_1[0];
  assign _zz_execute_ctrl1_down_AguPlugin_SEL_lane0_1 = (|{_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0_1,_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0});
  assign _zz_execute_ctrl1_down_LsuPlugin_logic_FENCE_lane0 = _zz_execute_ctrl1_down_LsuPlugin_logic_FENCE_lane0_1[0];
  assign _zz_execute_ctrl1_down_LsuPlugin_logic_FENCE_lane0_1 = (|((execute_lane0_logic_decoding_decodingBits & 33'h000001048) == 33'h000000008));
  assign _zz_execute_ctrl1_down_lane0_integer_WriteBackPlugin_SEL_lane0_1 = _zz_execute_ctrl1_down_lane0_integer_WriteBackPlugin_SEL_lane0_2[0];
  assign _zz_execute_ctrl1_down_lane0_integer_WriteBackPlugin_SEL_lane0_2 = (|{((execute_lane0_logic_decoding_decodingBits & 33'h000000048) == 33'h000000048),{((execute_lane0_logic_decoding_decodingBits & 33'h000001010) == 33'h000001010),{((execute_lane0_logic_decoding_decodingBits & 33'h000002010) == 33'h000002010),{((execute_lane0_logic_decoding_decodingBits & 33'h000000050) == 33'h000000010),{_zz_execute_ctrl1_down_lane0_integer_WriteBackPlugin_SEL_lane0,_zz_execute_ctrl1_down_AguPlugin_LOAD_lane0}}}}});
  assign _zz_execute_ctrl1_down_COMPLETION_AT_2_lane0 = _zz_execute_ctrl1_down_COMPLETION_AT_2_lane0_1[0];
  assign _zz_execute_ctrl1_down_COMPLETION_AT_2_lane0_1 = (|{_zz_execute_ctrl1_down_BYPASSED_AT_3_lane0,{_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0_1,{_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0,{_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0_4,{_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0_3,_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0_2}}}}});
  assign _zz_execute_ctrl1_down_COMPLETION_AT_4_lane0 = _zz_execute_ctrl1_down_COMPLETION_AT_4_lane0_1[0];
  assign _zz_execute_ctrl1_down_COMPLETION_AT_4_lane0_1 = (|{_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0_3,{_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0_1,{_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0,_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0_2}}});
  assign _zz_execute_ctrl1_down_COMPLETION_AT_3_lane0 = _zz_execute_ctrl1_down_COMPLETION_AT_3_lane0_1[0];
  assign _zz_execute_ctrl1_down_COMPLETION_AT_3_lane0_1 = (|{_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0_2,{_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0_1,_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0}});
  assign _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0_5 = _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0_6[0];
  assign _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0_6 = (|{_zz_execute_ctrl1_down_BYPASSED_AT_3_lane0,{_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0_1,{_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0,{_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0_4,{_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0_3,_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0_2}}}}});
  assign _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0_4 = _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0_5[0];
  assign _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0_5 = (|{_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0_3,{_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0_1,{_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0,_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0_2}}});
  assign _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0_3 = _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0_4[0];
  assign _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0_4 = (|{_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0_2,{_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0_1,_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0}});
  assign _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_ADD_SUB_lane0 = _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_ADD_SUB_lane0_1[0];
  assign _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_ADD_SUB_lane0_1 = (|{_zz_execute_ctrl1_down_late0_SrcPlugin_logic_SRC2_CTRL_lane0,_zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_ADD_SUB_lane0});
  assign _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_SLTX_lane0 = _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_SLTX_lane0_1[0];
  assign _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_SLTX_lane0_1 = (|_zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_SLTX_lane0);
  assign _zz_execute_ctrl1_down_SrcStageables_REVERT_lane0 = _zz_execute_ctrl1_down_SrcStageables_REVERT_lane0_1[0];
  assign _zz_execute_ctrl1_down_SrcStageables_REVERT_lane0_1 = (|{((execute_lane0_logic_decoding_decodingBits & 33'h000000040) == 33'h000000040),{((execute_lane0_logic_decoding_decodingBits & 33'h000002014) == 33'h000002010),((execute_lane0_logic_decoding_decodingBits & 33'h040000034) == 33'h040000030)}});
  assign _zz_execute_ctrl1_down_SrcStageables_ZERO_lane0 = _zz_execute_ctrl1_down_SrcStageables_ZERO_lane0_1[0];
  assign _zz_execute_ctrl1_down_SrcStageables_ZERO_lane0_1 = (|((execute_lane0_logic_decoding_decodingBits & 33'h000000024) == 33'h000000024));
  assign _zz_execute_ctrl1_down_lane0_IntFormatPlugin_logic_SIGNED_lane0 = _zz_execute_ctrl1_down_lane0_IntFormatPlugin_logic_SIGNED_lane0_1[0];
  assign _zz_execute_ctrl1_down_lane0_IntFormatPlugin_logic_SIGNED_lane0_1 = (|((execute_lane0_logic_decoding_decodingBits & 33'h000004010) == 33'h0));
  assign _zz_execute_ctrl1_down_BYPASSED_AT_2_lane0 = _zz_execute_ctrl1_down_BYPASSED_AT_2_lane0_1[0];
  assign _zz_execute_ctrl1_down_BYPASSED_AT_2_lane0_1 = (|{_zz_execute_ctrl1_down_BYPASSED_AT_3_lane0_1,{_zz_execute_ctrl1_down_BYPASSED_AT_3_lane0,((execute_lane0_logic_decoding_decodingBits & 33'h102000060) == 33'h100000020)}});
  assign _zz_execute_ctrl1_down_BYPASSED_AT_3_lane0_2 = _zz_execute_ctrl1_down_BYPASSED_AT_3_lane0_3[0];
  assign _zz_execute_ctrl1_down_BYPASSED_AT_3_lane0_3 = (|{((execute_lane0_logic_decoding_decodingBits & 33'h100000040) == 33'h100000040),{_zz_execute_ctrl1_down_BYPASSED_AT_3_lane0_1,{((execute_lane0_logic_decoding_decodingBits & 33'h100004010) == 33'h100004010),{_zz_execute_ctrl1_down_BYPASSED_AT_3_lane0,((execute_lane0_logic_decoding_decodingBits & 33'h102000020) == 33'h100000020)}}}});
  assign _zz_execute_ctrl1_down_MAY_FLUSH_PRECISE_3_lane0 = _zz_execute_ctrl1_down_MAY_FLUSH_PRECISE_3_lane0_1[0];
  assign _zz_execute_ctrl1_down_MAY_FLUSH_PRECISE_3_lane0_1 = (|{_zz_execute_ctrl1_down_late0_BranchPlugin_SEL_lane0,_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0});
  assign _zz_execute_ctrl1_down_MAY_FLUSH_PRECISE_4_lane0 = _zz_execute_ctrl1_down_MAY_FLUSH_PRECISE_4_lane0_1[0];
  assign _zz_execute_ctrl1_down_MAY_FLUSH_PRECISE_4_lane0_1 = (|{_zz_execute_ctrl1_down_late0_BranchPlugin_SEL_lane0,_zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0});
  assign _zz_execute_ctrl1_down_SrcStageables_UNSIGNED_lane0 = _zz_execute_ctrl1_down_SrcStageables_UNSIGNED_lane0_1[0];
  assign _zz_execute_ctrl1_down_SrcStageables_UNSIGNED_lane0_1 = (|{((execute_lane0_logic_decoding_decodingBits & 33'h000002010) == 33'h000002000),((execute_lane0_logic_decoding_decodingBits & 33'h000005000) == 33'h000001000)});
  assign _zz_execute_ctrl1_down_BarrelShifterPlugin_LEFT_lane0_1 = _zz_execute_ctrl1_down_BarrelShifterPlugin_LEFT_lane0_2[0];
  assign _zz_execute_ctrl1_down_BarrelShifterPlugin_LEFT_lane0_2 = (|_zz_execute_ctrl1_down_BarrelShifterPlugin_LEFT_lane0);
  assign _zz_execute_ctrl1_down_BarrelShifterPlugin_SIGNED_lane0 = _zz_execute_ctrl1_down_BarrelShifterPlugin_SIGNED_lane0_1[0];
  assign _zz_execute_ctrl1_down_BarrelShifterPlugin_SIGNED_lane0_1 = (|((execute_lane0_logic_decoding_decodingBits & 33'h040000000) == 33'h040000000));
  assign _zz_execute_ctrl1_down_MulPlugin_HIGH_lane0 = _zz_execute_ctrl1_down_MulPlugin_HIGH_lane0_1[0];
  assign _zz_execute_ctrl1_down_MulPlugin_HIGH_lane0_1 = (|{_zz_execute_ctrl1_down_CsrAccessPlugin_CSR_CLEAR_lane0,_zz_execute_ctrl1_down_CsrAccessPlugin_CSR_MASK_lane0});
  assign _zz_execute_ctrl1_down_RsUnsignedPlugin_RS1_SIGNED_lane0 = _zz_execute_ctrl1_down_RsUnsignedPlugin_RS1_SIGNED_lane0_1[0];
  assign _zz_execute_ctrl1_down_RsUnsignedPlugin_RS1_SIGNED_lane0_1 = (|{((execute_lane0_logic_decoding_decodingBits & 33'h000001000) == 33'h0),_zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_ADD_SUB_lane0});
  assign _zz_execute_ctrl1_down_RsUnsignedPlugin_RS2_SIGNED_lane0 = _zz_execute_ctrl1_down_RsUnsignedPlugin_RS2_SIGNED_lane0_1[0];
  assign _zz_execute_ctrl1_down_RsUnsignedPlugin_RS2_SIGNED_lane0_1 = (|{((execute_lane0_logic_decoding_decodingBits & 33'h000005000) == 33'h000004000),_zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_ADD_SUB_lane0});
  assign _zz_execute_ctrl1_down_DivPlugin_REM_lane0 = _zz_execute_ctrl1_down_DivPlugin_REM_lane0_1[0];
  assign _zz_execute_ctrl1_down_DivPlugin_REM_lane0_1 = (|_zz_execute_ctrl1_down_CsrAccessPlugin_CSR_MASK_lane0);
  assign _zz_execute_ctrl1_down_CsrAccessPlugin_CSR_IMM_lane0 = _zz_execute_ctrl1_down_CsrAccessPlugin_CSR_IMM_lane0_1[0];
  assign _zz_execute_ctrl1_down_CsrAccessPlugin_CSR_IMM_lane0_1 = (|((execute_lane0_logic_decoding_decodingBits & 33'h000004000) == 33'h000004000));
  assign _zz_execute_ctrl1_down_CsrAccessPlugin_CSR_MASK_lane0_1 = _zz_execute_ctrl1_down_CsrAccessPlugin_CSR_MASK_lane0_2[0];
  assign _zz_execute_ctrl1_down_CsrAccessPlugin_CSR_MASK_lane0_2 = (|_zz_execute_ctrl1_down_CsrAccessPlugin_CSR_MASK_lane0);
  assign _zz_execute_ctrl1_down_CsrAccessPlugin_CSR_CLEAR_lane0_1 = _zz_execute_ctrl1_down_CsrAccessPlugin_CSR_CLEAR_lane0_2[0];
  assign _zz_execute_ctrl1_down_CsrAccessPlugin_CSR_CLEAR_lane0_2 = (|_zz_execute_ctrl1_down_CsrAccessPlugin_CSR_CLEAR_lane0);
  assign _zz_execute_ctrl1_down_AguPlugin_LOAD_lane0_1 = _zz_execute_ctrl1_down_AguPlugin_LOAD_lane0_2[0];
  assign _zz_execute_ctrl1_down_AguPlugin_LOAD_lane0_2 = (|_zz_execute_ctrl1_down_AguPlugin_LOAD_lane0);
  assign _zz_execute_ctrl1_down_AguPlugin_STORE_lane0 = _zz_execute_ctrl1_down_AguPlugin_STORE_lane0_1[0];
  assign _zz_execute_ctrl1_down_AguPlugin_STORE_lane0_1 = (|((execute_lane0_logic_decoding_decodingBits & 33'h000000020) == 33'h000000020));
  assign _zz_execute_ctrl1_down_AguPlugin_ATOMIC_lane0 = _zz_execute_ctrl1_down_AguPlugin_ATOMIC_lane0_1[0];
  assign _zz_execute_ctrl1_down_AguPlugin_ATOMIC_lane0_1 = 1'b0;
  assign _zz_execute_ctrl1_down_AguPlugin_FLOAT_lane0 = _zz_execute_ctrl1_down_AguPlugin_FLOAT_lane0_1[0];
  assign _zz_execute_ctrl1_down_AguPlugin_FLOAT_lane0_1 = 1'b0;
  assign _zz_execute_ctrl1_down_AguPlugin_CLEAN_lane0 = _zz_execute_ctrl1_down_AguPlugin_CLEAN_lane0_1[0];
  assign _zz_execute_ctrl1_down_AguPlugin_CLEAN_lane0_1 = 1'b0;
  assign _zz_execute_ctrl1_down_AguPlugin_INVALIDATE_lane0 = _zz_execute_ctrl1_down_AguPlugin_INVALIDATE_lane0_1[0];
  assign _zz_execute_ctrl1_down_AguPlugin_INVALIDATE_lane0_1 = 1'b0;
  assign _zz_execute_ctrl1_down_LsuPlugin_logic_LSU_PREFETCH_lane0 = _zz_execute_ctrl1_down_LsuPlugin_logic_LSU_PREFETCH_lane0_1[0];
  assign _zz_execute_ctrl1_down_LsuPlugin_logic_LSU_PREFETCH_lane0_1 = 1'b0;
  assign _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_ADD_SUB_lane0_1 = _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_ADD_SUB_lane0_2[0];
  assign _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_ADD_SUB_lane0_2 = (|{_zz_execute_ctrl1_down_late0_SrcPlugin_logic_SRC2_CTRL_lane0,_zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_ADD_SUB_lane0});
  assign _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_SLTX_lane0_1 = _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_SLTX_lane0_2[0];
  assign _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_SLTX_lane0_2 = (|_zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_SLTX_lane0);
  assign _zz_WhiteboxerPlugin_logic_csr_access_payload_address = CsrAccessPlugin_logic_fsm_interface_uop;
  assign _zz__zz_WhiteboxerPlugin_logic_perf_executeFreezedCounter_1_1 = _zz_WhiteboxerPlugin_logic_perf_executeFreezedCounter;
  assign _zz__zz_WhiteboxerPlugin_logic_perf_executeFreezedCounter_1 = {59'd0, _zz__zz_WhiteboxerPlugin_logic_perf_executeFreezedCounter_1_1};
  assign _zz__zz_WhiteboxerPlugin_logic_perf_dispatchHazardsCounter_1_1 = _zz_WhiteboxerPlugin_logic_perf_dispatchHazardsCounter;
  assign _zz__zz_WhiteboxerPlugin_logic_perf_dispatchHazardsCounter_1 = {59'd0, _zz__zz_WhiteboxerPlugin_logic_perf_dispatchHazardsCounter_1_1};
  assign _zz__zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_0_1_1 = _zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_0;
  assign _zz__zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_0_1 = {59'd0, _zz__zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_0_1_1};
  assign _zz__zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_1_1_1 = _zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_1;
  assign _zz__zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_1_1 = {59'd0, _zz__zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_1_1_1};
  assign _zz__zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_0_1_1 = _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_0;
  assign _zz__zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_0_1 = {59'd0, _zz__zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_0_1_1};
  assign _zz__zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_1_1_1 = _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_1;
  assign _zz__zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_1_1 = {59'd0, _zz__zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_1_1_1};
  assign _zz_LsuL1Plugin_logic_ways_0_mem_port = {LsuL1Plugin_logic_waysWrite_tag_fault,{LsuL1Plugin_logic_waysWrite_tag_address,LsuL1Plugin_logic_waysWrite_tag_loaded}};
  assign _zz_LsuL1Plugin_logic_ways_0_mem_port_1 = LsuL1Plugin_logic_waysWrite_mask[0];
  assign _zz_LsuL1Plugin_logic_writeback_victimBuffer_port = LsuL1Plugin_logic_writeback_read_slotReadLast_payload_wordIndex;
  assign _zz_BtbPlugin_logic_mem_port = {BtbPlugin_logic_memDp_wp_payload_data_0_taken,{BtbPlugin_logic_memDp_wp_payload_data_0_isPop,{BtbPlugin_logic_memDp_wp_payload_data_0_isPush,{BtbPlugin_logic_memDp_wp_payload_data_0_isBranch,{BtbPlugin_logic_memDp_wp_payload_data_0_pcTarget,BtbPlugin_logic_memDp_wp_payload_data_0_hash}}}}};
  assign _zz_FetchL1Plugin_logic_ways_0_mem_port = {FetchL1Plugin_logic_waysWrite_tag_address,{FetchL1Plugin_logic_waysWrite_tag_error,FetchL1Plugin_logic_waysWrite_tag_loaded}};
  assign _zz_FetchL1Plugin_logic_ways_0_mem_port_1 = FetchL1Plugin_logic_waysWrite_mask[0];
  assign _zz_23 = _zz_execute_ctrl4_down_LsuL1Plugin_logic_MUXED_DATA_lane0;
  assign _zz_25 = {_zz_13[2],{_zz_13[1],_zz_13[0]}};
  assign _zz_LsuPlugin_logic_onCtrl_loadData_shited_1 = execute_ctrl4_down_LsuL1_MIXED_ADDRESS_lane0[1 : 0];
  assign _zz_LsuPlugin_logic_onCtrl_loadData_shited_3 = execute_ctrl4_down_LsuL1_MIXED_ADDRESS_lane0[1 : 1];
  assign _zz_WhiteboxerPlugin_logic_perf_candidatesCount_1 = DispatchPlugin_logic_candidates_0_ctx_valid;
  assign _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCount_1 = decode_ctrls_1_up_LANE_SEL_0;
  assign _zz_early0_BarrelShifterPlugin_logic_shift_reversed_1 = execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[9];
  assign _zz_early0_BarrelShifterPlugin_logic_shift_reversed_2 = execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[10];
  assign _zz_early0_BarrelShifterPlugin_logic_shift_reversed_3 = {execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[11],{execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[12],{execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[13],{execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[14],{execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[15],{execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[16],{execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[17],{execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[18],{execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[19],{_zz_early0_BarrelShifterPlugin_logic_shift_reversed_4,{_zz_early0_BarrelShifterPlugin_logic_shift_reversed_5,_zz_early0_BarrelShifterPlugin_logic_shift_reversed_6}}}}}}}}}}};
  assign _zz_early0_BarrelShifterPlugin_logic_shift_reversed_4 = execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[20];
  assign _zz_early0_BarrelShifterPlugin_logic_shift_reversed_5 = execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[21];
  assign _zz_early0_BarrelShifterPlugin_logic_shift_reversed_6 = {execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[22],{execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[23],{execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[24],{execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[25],{execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[26],{execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[27],{execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[28],{execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[29],{execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[30],execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[31]}}}}}}}}};
  assign _zz_early0_BarrelShifterPlugin_logic_shift_patched_1 = early0_BarrelShifterPlugin_logic_shift_shifted[9];
  assign _zz_early0_BarrelShifterPlugin_logic_shift_patched_2 = early0_BarrelShifterPlugin_logic_shift_shifted[10];
  assign _zz_early0_BarrelShifterPlugin_logic_shift_patched_3 = {early0_BarrelShifterPlugin_logic_shift_shifted[11],{early0_BarrelShifterPlugin_logic_shift_shifted[12],{early0_BarrelShifterPlugin_logic_shift_shifted[13],{early0_BarrelShifterPlugin_logic_shift_shifted[14],{early0_BarrelShifterPlugin_logic_shift_shifted[15],{early0_BarrelShifterPlugin_logic_shift_shifted[16],{early0_BarrelShifterPlugin_logic_shift_shifted[17],{early0_BarrelShifterPlugin_logic_shift_shifted[18],{early0_BarrelShifterPlugin_logic_shift_shifted[19],{_zz_early0_BarrelShifterPlugin_logic_shift_patched_4,{_zz_early0_BarrelShifterPlugin_logic_shift_patched_5,_zz_early0_BarrelShifterPlugin_logic_shift_patched_6}}}}}}}}}}};
  assign _zz_early0_BarrelShifterPlugin_logic_shift_patched_4 = early0_BarrelShifterPlugin_logic_shift_shifted[20];
  assign _zz_early0_BarrelShifterPlugin_logic_shift_patched_5 = early0_BarrelShifterPlugin_logic_shift_shifted[21];
  assign _zz_early0_BarrelShifterPlugin_logic_shift_patched_6 = {early0_BarrelShifterPlugin_logic_shift_shifted[22],{early0_BarrelShifterPlugin_logic_shift_shifted[23],{early0_BarrelShifterPlugin_logic_shift_shifted[24],{early0_BarrelShifterPlugin_logic_shift_shifted[25],{early0_BarrelShifterPlugin_logic_shift_shifted[26],{early0_BarrelShifterPlugin_logic_shift_shifted[27],{early0_BarrelShifterPlugin_logic_shift_shifted[28],{early0_BarrelShifterPlugin_logic_shift_shifted[29],{early0_BarrelShifterPlugin_logic_shift_shifted[30],early0_BarrelShifterPlugin_logic_shift_shifted[31]}}}}}}}}};
  assign _zz_late0_BarrelShifterPlugin_logic_shift_reversed_1 = execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[9];
  assign _zz_late0_BarrelShifterPlugin_logic_shift_reversed_2 = execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[10];
  assign _zz_late0_BarrelShifterPlugin_logic_shift_reversed_3 = {execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[11],{execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[12],{execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[13],{execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[14],{execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[15],{execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[16],{execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[17],{execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[18],{execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[19],{_zz_late0_BarrelShifterPlugin_logic_shift_reversed_4,{_zz_late0_BarrelShifterPlugin_logic_shift_reversed_5,_zz_late0_BarrelShifterPlugin_logic_shift_reversed_6}}}}}}}}}}};
  assign _zz_late0_BarrelShifterPlugin_logic_shift_reversed_4 = execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[20];
  assign _zz_late0_BarrelShifterPlugin_logic_shift_reversed_5 = execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[21];
  assign _zz_late0_BarrelShifterPlugin_logic_shift_reversed_6 = {execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[22],{execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[23],{execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[24],{execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[25],{execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[26],{execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[27],{execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[28],{execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[29],{execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[30],execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[31]}}}}}}}}};
  assign _zz_late0_BarrelShifterPlugin_logic_shift_patched_1 = late0_BarrelShifterPlugin_logic_shift_shifted[9];
  assign _zz_late0_BarrelShifterPlugin_logic_shift_patched_2 = late0_BarrelShifterPlugin_logic_shift_shifted[10];
  assign _zz_late0_BarrelShifterPlugin_logic_shift_patched_3 = {late0_BarrelShifterPlugin_logic_shift_shifted[11],{late0_BarrelShifterPlugin_logic_shift_shifted[12],{late0_BarrelShifterPlugin_logic_shift_shifted[13],{late0_BarrelShifterPlugin_logic_shift_shifted[14],{late0_BarrelShifterPlugin_logic_shift_shifted[15],{late0_BarrelShifterPlugin_logic_shift_shifted[16],{late0_BarrelShifterPlugin_logic_shift_shifted[17],{late0_BarrelShifterPlugin_logic_shift_shifted[18],{late0_BarrelShifterPlugin_logic_shift_shifted[19],{_zz_late0_BarrelShifterPlugin_logic_shift_patched_4,{_zz_late0_BarrelShifterPlugin_logic_shift_patched_5,_zz_late0_BarrelShifterPlugin_logic_shift_patched_6}}}}}}}}}}};
  assign _zz_late0_BarrelShifterPlugin_logic_shift_patched_4 = late0_BarrelShifterPlugin_logic_shift_shifted[20];
  assign _zz_late0_BarrelShifterPlugin_logic_shift_patched_5 = late0_BarrelShifterPlugin_logic_shift_shifted[21];
  assign _zz_late0_BarrelShifterPlugin_logic_shift_patched_6 = {late0_BarrelShifterPlugin_logic_shift_shifted[22],{late0_BarrelShifterPlugin_logic_shift_shifted[23],{late0_BarrelShifterPlugin_logic_shift_shifted[24],{late0_BarrelShifterPlugin_logic_shift_shifted[25],{late0_BarrelShifterPlugin_logic_shift_shifted[26],{late0_BarrelShifterPlugin_logic_shift_shifted[27],{late0_BarrelShifterPlugin_logic_shift_shifted[28],{late0_BarrelShifterPlugin_logic_shift_shifted[29],{late0_BarrelShifterPlugin_logic_shift_shifted[30],late0_BarrelShifterPlugin_logic_shift_shifted[31]}}}}}}}}};
  assign _zz_LsuPlugin_logic_onPma_io_rsp_fault = 32'hffff0000;
  assign _zz_LsuPlugin_logic_onPma_io_rsp_fault_1 = 32'hffffe000;
  assign _zz_decode_ctrls_1_down_RD_ENABLE_0_1 = 32'h00000050;
  assign _zz_decode_ctrls_1_down_RD_ENABLE_0_2 = (decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h0000000c);
  assign _zz_decode_ctrls_1_down_RD_ENABLE_0_3 = 32'h00000004;
  assign _zz_decode_ctrls_1_down_RD_ENABLE_0_4 = (decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h00000028);
  assign _zz_decode_ctrls_1_down_RD_ENABLE_0_5 = 32'h0;
  assign _zz_decode_ctrls_1_down_Decode_LEGAL_0 = 32'h0000107f;
  assign _zz_decode_ctrls_1_down_Decode_LEGAL_0_1 = (decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h0000207f);
  assign _zz_decode_ctrls_1_down_Decode_LEGAL_0_2 = 32'h00002073;
  assign _zz_decode_ctrls_1_down_Decode_LEGAL_0_3 = ((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h0000407f) == 32'h00004063);
  assign _zz_decode_ctrls_1_down_Decode_LEGAL_0_4 = ((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h0000207f) == 32'h00002013);
  assign _zz_decode_ctrls_1_down_Decode_LEGAL_0_5 = {((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h0000107f) == 32'h00000013),{((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h0000603f) == 32'h00000023),{((decode_ctrls_1_down_Decode_INSTRUCTION_0 & _zz_decode_ctrls_1_down_Decode_LEGAL_0_6) == 32'h00000003),{(_zz_decode_ctrls_1_down_Decode_LEGAL_0_7 == _zz_decode_ctrls_1_down_Decode_LEGAL_0_8),{_zz_decode_ctrls_1_down_Decode_LEGAL_0_9,{_zz_decode_ctrls_1_down_Decode_LEGAL_0_10,_zz_decode_ctrls_1_down_Decode_LEGAL_0_11}}}}}};
  assign _zz_decode_ctrls_1_down_Decode_LEGAL_0_6 = 32'h0000207f;
  assign _zz_decode_ctrls_1_down_Decode_LEGAL_0_7 = (decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h0000505f);
  assign _zz_decode_ctrls_1_down_Decode_LEGAL_0_8 = 32'h00000003;
  assign _zz_decode_ctrls_1_down_Decode_LEGAL_0_9 = ((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h0000707b) == 32'h00000063);
  assign _zz_decode_ctrls_1_down_Decode_LEGAL_0_10 = ((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h0000607f) == 32'h0000000f);
  assign _zz_decode_ctrls_1_down_Decode_LEGAL_0_11 = {((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'hfc00007f) == 32'h00000033),{((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'hfc00305f) == 32'h00001013),{((decode_ctrls_1_down_Decode_INSTRUCTION_0 & _zz_decode_ctrls_1_down_Decode_LEGAL_0_12) == 32'h00005013),{(_zz_decode_ctrls_1_down_Decode_LEGAL_0_13 == _zz_decode_ctrls_1_down_Decode_LEGAL_0_14),{_zz_decode_ctrls_1_down_Decode_LEGAL_0_15,{_zz_decode_ctrls_1_down_Decode_LEGAL_0_16,_zz_decode_ctrls_1_down_Decode_LEGAL_0_17}}}}}};
  assign _zz_decode_ctrls_1_down_Decode_LEGAL_0_12 = 32'hbc00707f;
  assign _zz_decode_ctrls_1_down_Decode_LEGAL_0_13 = (decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'hbe00707f);
  assign _zz_decode_ctrls_1_down_Decode_LEGAL_0_14 = 32'h00005033;
  assign _zz_decode_ctrls_1_down_Decode_LEGAL_0_15 = ((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'hbe00707f) == 32'h00000033);
  assign _zz_decode_ctrls_1_down_Decode_LEGAL_0_16 = ((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'hffefffff) == 32'h00000073);
  assign _zz_decode_ctrls_1_down_Decode_LEGAL_0_17 = {((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'hffffffff) == 32'h10500073),((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'hffffffff) == 32'h30200073)};
  assign _zz_decode_logic_flushes_1_onLanes_0_doIt = 1'b1;
  assign _zz_decode_logic_flushes_1_onLanes_0_doIt_1 = (early0_BranchPlugin_logic_flushPort_valid && 1'b1);
  assign _zz_decode_logic_flushes_1_onLanes_0_doIt_2 = (LsuPlugin_logic_flushPort_valid && 1'b1);
  assign _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception = 1'b0;
  assign _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_1 = 1'b0;
  assign _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_2 = (_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_valid_2 && 1'b0);
  assign _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_3 = (_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_valid && 1'b0);
  assign _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_4 = (_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_valid_2 && 1'b0);
  assign _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_5 = (_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_valid_1 && 1'b0);
  assign _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_1_1 = early0_EnvPlugin_logic_trapPort_payload_exception;
  assign _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_1_2 = early0_BranchPlugin_logic_trapPort_payload_exception;
  assign _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_exception = {TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_payload_tval,TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_payload_exception};
  assign _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_exception_1 = {TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_tval,TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception};
  assign _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_exception_2 = {TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_2_payload_tval,TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_2_payload_exception};
  assign _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_exception_3 = {TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_3_payload_tval,TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_3_payload_exception};
  assign _zz_CsrAccessPlugin_logic_fsm_inject_implemented = COMB_CSR_3859;
  assign _zz_CsrAccessPlugin_logic_fsm_inject_implemented_1 = {COMB_CSR_3858,{COMB_CSR_3857,{COMB_CSR_1954,{COMB_CSR_1953,COMB_CSR_1952}}}};
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_7 = 32'h40001100;
  assign _zz_fetch_logic_flushes_0_doIt = 1'b1;
  assign _zz_fetch_logic_flushes_0_doIt_1 = 1'b1;
  assign _zz_fetch_logic_flushes_1_doIt = 1'b1;
  assign _zz_fetch_logic_flushes_1_doIt_1 = (BtbPlugin_logic_flushPort_valid && 1'b1);
  assign _zz_fetch_logic_flushes_1_doIt_2 = (1'b0 || (1'b1 && BtbPlugin_logic_flushPort_payload_self));
  assign _zz_execute_ctrl1_down_early0_IntAluPlugin_SEL_lane0_2 = 33'h102002050;
  assign _zz_execute_ctrl1_down_early0_IntAluPlugin_SEL_lane0_3 = 33'h102001050;
  assign _zz_when_ExecuteLanePlugin_l306_2 = 1'b1;
  assign _zz_when_ExecuteLanePlugin_l306_2_1 = 1'b1;
  assign _zz_when_ExecuteLanePlugin_l306_2_2 = 1'b0;
  assign _zz_when_ExecuteLanePlugin_l306_2_3 = (1'b1 && CsrAccessPlugin_logic_flushPort_payload_self);
  assign _zz_when_ExecuteLanePlugin_l306_2_4 = (early0_BranchPlugin_logic_flushPort_valid && 1'b1);
  assign _zz_when_ExecuteLanePlugin_l306_2_5 = (1'b0 || (1'b1 && early0_BranchPlugin_logic_flushPort_payload_self));
  assign _zz_when_ExecuteLanePlugin_l306_2_6 = 1'b1;
  always @(*) begin
    LsuL1Plugin_logic_banks_0_mem_spinal_port1 = {_zz_LsuL1Plugin_logic_banks_0_memsymbol_read_3, _zz_LsuL1Plugin_logic_banks_0_memsymbol_read_2, _zz_LsuL1Plugin_logic_banks_0_memsymbol_read_1, _zz_LsuL1Plugin_logic_banks_0_memsymbol_read};
  end
  always @(posedge clk) begin
    if(LsuL1Plugin_logic_banks_0_write_payload_mask[0] && LsuL1Plugin_logic_banks_0_write_valid) begin
      LsuL1Plugin_logic_banks_0_mem_symbol0[LsuL1Plugin_logic_banks_0_write_payload_address] <= LsuL1Plugin_logic_banks_0_write_payload_data[7 : 0];
    end
    if(LsuL1Plugin_logic_banks_0_write_payload_mask[1] && LsuL1Plugin_logic_banks_0_write_valid) begin
      LsuL1Plugin_logic_banks_0_mem_symbol1[LsuL1Plugin_logic_banks_0_write_payload_address] <= LsuL1Plugin_logic_banks_0_write_payload_data[15 : 8];
    end
    if(LsuL1Plugin_logic_banks_0_write_payload_mask[2] && LsuL1Plugin_logic_banks_0_write_valid) begin
      LsuL1Plugin_logic_banks_0_mem_symbol2[LsuL1Plugin_logic_banks_0_write_payload_address] <= LsuL1Plugin_logic_banks_0_write_payload_data[23 : 16];
    end
    if(LsuL1Plugin_logic_banks_0_write_payload_mask[3] && LsuL1Plugin_logic_banks_0_write_valid) begin
      LsuL1Plugin_logic_banks_0_mem_symbol3[LsuL1Plugin_logic_banks_0_write_payload_address] <= LsuL1Plugin_logic_banks_0_write_payload_data[31 : 24];
    end
  end

  always @(posedge clk) begin
    if(LsuL1Plugin_logic_banks_0_read_cmd_valid) begin
      _zz_LsuL1Plugin_logic_banks_0_memsymbol_read <= LsuL1Plugin_logic_banks_0_mem_symbol0[LsuL1Plugin_logic_banks_0_read_cmd_payload];
      _zz_LsuL1Plugin_logic_banks_0_memsymbol_read_1 <= LsuL1Plugin_logic_banks_0_mem_symbol1[LsuL1Plugin_logic_banks_0_read_cmd_payload];
      _zz_LsuL1Plugin_logic_banks_0_memsymbol_read_2 <= LsuL1Plugin_logic_banks_0_mem_symbol2[LsuL1Plugin_logic_banks_0_read_cmd_payload];
      _zz_LsuL1Plugin_logic_banks_0_memsymbol_read_3 <= LsuL1Plugin_logic_banks_0_mem_symbol3[LsuL1Plugin_logic_banks_0_read_cmd_payload];
    end
  end

  always @(posedge clk) begin
    if(_zz_LsuL1Plugin_logic_ways_0_mem_port_1) begin
      LsuL1Plugin_logic_ways_0_mem[LsuL1Plugin_logic_waysWrite_address] <= _zz_LsuL1Plugin_logic_ways_0_mem_port;
    end
  end

  always @(posedge clk) begin
    if(LsuL1Plugin_logic_ways_0_lsuRead_cmd_valid) begin
      LsuL1Plugin_logic_ways_0_mem_spinal_port1 <= LsuL1Plugin_logic_ways_0_mem[LsuL1Plugin_logic_ways_0_lsuRead_cmd_payload];
    end
  end

  always @(posedge clk) begin
    if(_zz_4) begin
      LsuL1Plugin_logic_shared_mem[LsuL1Plugin_logic_shared_write_payload_address] <= LsuL1Plugin_logic_shared_write_payload_data_dirty;
    end
  end

  always @(posedge clk) begin
    if(LsuL1Plugin_logic_shared_lsuRead_cmd_valid) begin
      LsuL1Plugin_logic_shared_mem_spinal_port1 <= LsuL1Plugin_logic_shared_mem[LsuL1Plugin_logic_shared_lsuRead_cmd_payload];
    end
  end

  always @(posedge clk) begin
    if(_zz_3) begin
      LsuL1Plugin_logic_writeback_victimBuffer[_zz_LsuL1Plugin_logic_writeback_victimBuffer_port] <= LsuL1Plugin_logic_writeback_read_readedData;
    end
  end

  always @(posedge clk) begin
    if(LsuL1Plugin_logic_writeback_write_bufferRead_ready) begin
      LsuL1Plugin_logic_writeback_victimBuffer_spinal_port1 <= LsuL1Plugin_logic_writeback_victimBuffer[_zz_LsuL1Plugin_logic_writeback_write_word];
    end
  end

  always @(posedge clk) begin
    if(BtbPlugin_logic_memDp_wp_payload_mask[0] && BtbPlugin_logic_memDp_wp_valid) begin
      BtbPlugin_logic_mem[BtbPlugin_logic_memDp_wp_payload_address] <= _zz_BtbPlugin_logic_mem_port;
    end
  end

  always @(posedge clk) begin
    if(BtbPlugin_logic_memDp_rp_cmd_valid) begin
      BtbPlugin_logic_mem_spinal_port1 <= BtbPlugin_logic_mem[BtbPlugin_logic_memDp_rp_cmd_payload];
    end
  end

  always @(posedge clk) begin
    if(_zz_2) begin
      FetchL1Plugin_logic_banks_0_mem[FetchL1Plugin_logic_banks_0_write_payload_address] <= FetchL1Plugin_logic_banks_0_write_payload_data;
    end
  end

  always @(posedge clk) begin
    if(FetchL1Plugin_logic_banks_0_read_cmd_valid) begin
      FetchL1Plugin_logic_banks_0_mem_spinal_port1 <= FetchL1Plugin_logic_banks_0_mem[FetchL1Plugin_logic_banks_0_read_cmd_payload];
    end
  end

  always @(posedge clk) begin
    if(_zz_FetchL1Plugin_logic_ways_0_mem_port_1) begin
      FetchL1Plugin_logic_ways_0_mem[FetchL1Plugin_logic_waysWrite_address] <= _zz_FetchL1Plugin_logic_ways_0_mem_port;
    end
  end

  always @(posedge clk) begin
    if(FetchL1Plugin_logic_ways_0_read_cmd_valid) begin
      FetchL1Plugin_logic_ways_0_mem_spinal_port1 <= FetchL1Plugin_logic_ways_0_mem[FetchL1Plugin_logic_ways_0_read_cmd_payload];
    end
  end

  always @(posedge clk) begin
    if(_zz_1) begin
      CsrRamPlugin_logic_mem[CsrRamPlugin_logic_writeLogic_port_payload_address] <= CsrRamPlugin_logic_writeLogic_port_payload_data;
    end
  end

  always @(posedge clk) begin
    if(CsrRamPlugin_logic_readLogic_port_cmd_valid) begin
      CsrRamPlugin_logic_mem_spinal_port1 <= CsrRamPlugin_logic_mem[CsrRamPlugin_logic_readLogic_port_cmd_payload];
    end
  end

  DivRadix early0_DivPlugin_logic_processing_div (
    .io_flush                  (execute_ctrl2_down_isReady                                       ), //i
    .io_cmd_valid              (early0_DivPlugin_logic_processing_div_io_cmd_valid               ), //i
    .io_cmd_ready              (early0_DivPlugin_logic_processing_div_io_cmd_ready               ), //o
    .io_cmd_payload_a          (early0_DivPlugin_logic_processing_a[31:0]                        ), //i
    .io_cmd_payload_b          (early0_DivPlugin_logic_processing_b[31:0]                        ), //i
    .io_cmd_payload_normalized (1'b0                                                             ), //i
    .io_cmd_payload_iterations (5'bxxxxx                                                         ), //i
    .io_rsp_valid              (early0_DivPlugin_logic_processing_div_io_rsp_valid               ), //o
    .io_rsp_ready              (1'b0                                                             ), //i
    .io_rsp_payload_result     (early0_DivPlugin_logic_processing_div_io_rsp_payload_result[31:0]), //o
    .io_rsp_payload_remain     (early0_DivPlugin_logic_processing_div_io_rsp_payload_remain[31:0]), //o
    .clk                       (clk                                                              ), //i
    .reset                     (reset                                                            )  //i
  );
  StreamArbiter LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter (
    .io_inputs_0_valid                    (LsuL1Plugin_logic_bus_toWishbone_arbiter_readCmd_valid                                   ), //i
    .io_inputs_0_ready                    (LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_inputs_0_ready                       ), //o
    .io_inputs_0_payload_last             (LsuL1Plugin_logic_bus_toWishbone_arbiter_readCmd_payload_last                            ), //i
    .io_inputs_0_payload_fragment_write   (LsuL1Plugin_logic_bus_toWishbone_arbiter_readCmd_payload_fragment_write                  ), //i
    .io_inputs_0_payload_fragment_address (LsuL1Plugin_logic_bus_toWishbone_arbiter_readCmd_payload_fragment_address[31:0]          ), //i
    .io_inputs_1_valid                    (LsuL1Plugin_logic_bus_toWishbone_arbiter_writeCmd_valid                                  ), //i
    .io_inputs_1_ready                    (LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_inputs_1_ready                       ), //o
    .io_inputs_1_payload_last             (LsuL1Plugin_logic_bus_toWishbone_arbiter_writeCmd_payload_last                           ), //i
    .io_inputs_1_payload_fragment_write   (LsuL1Plugin_logic_bus_toWishbone_arbiter_writeCmd_payload_fragment_write                 ), //i
    .io_inputs_1_payload_fragment_address (LsuL1Plugin_logic_bus_toWishbone_arbiter_writeCmd_payload_fragment_address[31:0]         ), //i
    .io_output_valid                      (LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_output_valid                         ), //o
    .io_output_ready                      (LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_output_ready                         ), //i
    .io_output_payload_last               (LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_output_payload_last                  ), //o
    .io_output_payload_fragment_write     (LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_output_payload_fragment_write        ), //o
    .io_output_payload_fragment_address   (LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_output_payload_fragment_address[31:0]), //o
    .io_chosen                            (LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_chosen                               ), //o
    .io_chosenOH                          (LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_chosenOH[1:0]                        ), //o
    .clk                                  (clk                                                                                      ), //i
    .reset                                (reset                                                                                    )  //i
  );
  StreamArbiter_1 LsuPlugin_logic_flusher_arbiter (
    .io_inputs_0_valid (TrapPlugin_logic_lsuL1Invalidate_0_cmd_valid     ), //i
    .io_inputs_0_ready (LsuPlugin_logic_flusher_arbiter_io_inputs_0_ready), //o
    .io_output_valid   (LsuPlugin_logic_flusher_arbiter_io_output_valid  ), //o
    .io_output_ready   (LsuPlugin_logic_flusher_arbiter_io_output_ready  ), //i
    .io_chosenOH       (LsuPlugin_logic_flusher_arbiter_io_chosenOH      ), //o
    .clk               (clk                                              ), //i
    .reset             (reset                                            )  //i
  );
  StreamArbiter_2 LsuPlugin_logic_onAddress0_arbiter (
    .io_inputs_0_valid              (LsuPlugin_logic_onAddress0_ls_port_valid                          ), //i
    .io_inputs_0_ready              (LsuPlugin_logic_onAddress0_arbiter_io_inputs_0_ready              ), //o
    .io_inputs_0_payload_op         (LsuPlugin_logic_onAddress0_ls_port_payload_op[2:0]                ), //i
    .io_inputs_0_payload_address    (LsuPlugin_logic_onAddress0_ls_port_payload_address[31:0]          ), //i
    .io_inputs_0_payload_size       (LsuPlugin_logic_onAddress0_ls_port_payload_size[1:0]              ), //i
    .io_inputs_0_payload_load       (LsuPlugin_logic_onAddress0_ls_port_payload_load                   ), //i
    .io_inputs_0_payload_store      (LsuPlugin_logic_onAddress0_ls_port_payload_store                  ), //i
    .io_inputs_0_payload_atomic     (LsuPlugin_logic_onAddress0_ls_port_payload_atomic                 ), //i
    .io_inputs_0_payload_clean      (LsuPlugin_logic_onAddress0_ls_port_payload_clean                  ), //i
    .io_inputs_0_payload_invalidate (LsuPlugin_logic_onAddress0_ls_port_payload_invalidate             ), //i
    .io_inputs_0_payload_storeId    (LsuPlugin_logic_onAddress0_ls_port_payload_storeId[11:0]          ), //i
    .io_inputs_1_valid              (LsuPlugin_logic_onAddress0_flush_port_valid                       ), //i
    .io_inputs_1_ready              (LsuPlugin_logic_onAddress0_arbiter_io_inputs_1_ready              ), //o
    .io_inputs_1_payload_op         (LsuPlugin_logic_onAddress0_flush_port_payload_op[2:0]             ), //i
    .io_inputs_1_payload_address    (LsuPlugin_logic_onAddress0_flush_port_payload_address[31:0]       ), //i
    .io_inputs_1_payload_size       (LsuPlugin_logic_onAddress0_flush_port_payload_size[1:0]           ), //i
    .io_inputs_1_payload_load       (LsuPlugin_logic_onAddress0_flush_port_payload_load                ), //i
    .io_inputs_1_payload_store      (LsuPlugin_logic_onAddress0_flush_port_payload_store               ), //i
    .io_inputs_1_payload_atomic     (LsuPlugin_logic_onAddress0_flush_port_payload_atomic              ), //i
    .io_inputs_1_payload_clean      (LsuPlugin_logic_onAddress0_flush_port_payload_clean               ), //i
    .io_inputs_1_payload_invalidate (LsuPlugin_logic_onAddress0_flush_port_payload_invalidate          ), //i
    .io_inputs_1_payload_storeId    (LsuPlugin_logic_onAddress0_flush_port_payload_storeId[11:0]       ), //i
    .io_output_valid                (LsuPlugin_logic_onAddress0_arbiter_io_output_valid                ), //o
    .io_output_ready                (LsuPlugin_logic_onAddress0_arbiter_io_output_ready                ), //i
    .io_output_payload_op           (LsuPlugin_logic_onAddress0_arbiter_io_output_payload_op[2:0]      ), //o
    .io_output_payload_address      (LsuPlugin_logic_onAddress0_arbiter_io_output_payload_address[31:0]), //o
    .io_output_payload_size         (LsuPlugin_logic_onAddress0_arbiter_io_output_payload_size[1:0]    ), //o
    .io_output_payload_load         (LsuPlugin_logic_onAddress0_arbiter_io_output_payload_load         ), //o
    .io_output_payload_store        (LsuPlugin_logic_onAddress0_arbiter_io_output_payload_store        ), //o
    .io_output_payload_atomic       (LsuPlugin_logic_onAddress0_arbiter_io_output_payload_atomic       ), //o
    .io_output_payload_clean        (LsuPlugin_logic_onAddress0_arbiter_io_output_payload_clean        ), //o
    .io_output_payload_invalidate   (LsuPlugin_logic_onAddress0_arbiter_io_output_payload_invalidate   ), //o
    .io_output_payload_storeId      (LsuPlugin_logic_onAddress0_arbiter_io_output_payload_storeId[11:0]), //o
    .io_chosen                      (LsuPlugin_logic_onAddress0_arbiter_io_chosen                      ), //o
    .io_chosenOH                    (LsuPlugin_logic_onAddress0_arbiter_io_chosenOH[1:0]               ), //o
    .clk                            (clk                                                               ), //i
    .reset                          (reset                                                             )  //i
  );
  StreamArbiter_3 streamArbiter_4 (
    .io_inputs_0_valid                      (LearnPlugin_logic_buffered_0_valid                      ), //i
    .io_inputs_0_ready                      (streamArbiter_4_io_inputs_0_ready                       ), //o
    .io_inputs_0_payload_pcOnLastSlice      (LearnPlugin_logic_buffered_0_payload_pcOnLastSlice[31:0]), //i
    .io_inputs_0_payload_pcTarget           (LearnPlugin_logic_buffered_0_payload_pcTarget[31:0]     ), //i
    .io_inputs_0_payload_taken              (LearnPlugin_logic_buffered_0_payload_taken              ), //i
    .io_inputs_0_payload_isBranch           (LearnPlugin_logic_buffered_0_payload_isBranch           ), //i
    .io_inputs_0_payload_isPush             (LearnPlugin_logic_buffered_0_payload_isPush             ), //i
    .io_inputs_0_payload_isPop              (LearnPlugin_logic_buffered_0_payload_isPop              ), //i
    .io_inputs_0_payload_wasWrong           (LearnPlugin_logic_buffered_0_payload_wasWrong           ), //i
    .io_inputs_0_payload_badPredictedTarget (LearnPlugin_logic_buffered_0_payload_badPredictedTarget ), //i
    .io_inputs_0_payload_uopId              (LearnPlugin_logic_buffered_0_payload_uopId[15:0]        ), //i
    .io_output_valid                        (streamArbiter_4_io_output_valid                         ), //o
    .io_output_ready                        (LearnPlugin_logic_arbitrated_ready                      ), //i
    .io_output_payload_pcOnLastSlice        (streamArbiter_4_io_output_payload_pcOnLastSlice[31:0]   ), //o
    .io_output_payload_pcTarget             (streamArbiter_4_io_output_payload_pcTarget[31:0]        ), //o
    .io_output_payload_taken                (streamArbiter_4_io_output_payload_taken                 ), //o
    .io_output_payload_isBranch             (streamArbiter_4_io_output_payload_isBranch              ), //o
    .io_output_payload_isPush               (streamArbiter_4_io_output_payload_isPush                ), //o
    .io_output_payload_isPop                (streamArbiter_4_io_output_payload_isPop                 ), //o
    .io_output_payload_wasWrong             (streamArbiter_4_io_output_payload_wasWrong              ), //o
    .io_output_payload_badPredictedTarget   (streamArbiter_4_io_output_payload_badPredictedTarget    ), //o
    .io_output_payload_uopId                (streamArbiter_4_io_output_payload_uopId[15:0]           ), //o
    .io_chosenOH                            (streamArbiter_4_io_chosenOH                             ), //o
    .clk                                    (clk                                                     ), //i
    .reset                                  (reset                                                   )  //i
  );
  RegFileMem integer_RegFilePlugin_logic_regfile_fpga (
    .io_writes_0_valid   (integer_RegFilePlugin_logic_regfile_fpga_io_writes_0_valid       ), //i
    .io_writes_0_address (integer_RegFilePlugin_logic_regfile_fpga_io_writes_0_address[4:0]), //i
    .io_writes_0_data    (integer_RegFilePlugin_logic_regfile_fpga_io_writes_0_data[31:0]  ), //i
    .io_writes_0_uopId   (integer_RegFilePlugin_logic_writeMerges_0_bus_uopId[15:0]        ), //i
    .io_reads_0_valid    (execute_lane0_bypasser_integer_RS1_port_valid                    ), //i
    .io_reads_0_address  (execute_lane0_bypasser_integer_RS1_port_address[4:0]             ), //i
    .io_reads_0_data     (integer_RegFilePlugin_logic_regfile_fpga_io_reads_0_data[31:0]   ), //o
    .io_reads_1_valid    (execute_lane0_bypasser_integer_RS2_port_valid                    ), //i
    .io_reads_1_address  (execute_lane0_bypasser_integer_RS2_port_address[4:0]             ), //i
    .io_reads_1_data     (integer_RegFilePlugin_logic_regfile_fpga_io_reads_1_data[31:0]   ), //o
    .clk                 (clk                                                              ), //i
    .reset               (reset                                                            )  //i
  );
  always @(*) begin
    case(_zz_23)
      1'b0 : _zz_22 = 1'b0;
      default : _zz_22 = 1'b1;
    endcase
  end

  always @(*) begin
    case(_zz_25)
      3'b000 : _zz_24 = 2'b00;
      3'b001 : _zz_24 = 2'b01;
      3'b010 : _zz_24 = 2'b01;
      3'b011 : _zz_24 = 2'b10;
      3'b100 : _zz_24 = 2'b01;
      3'b101 : _zz_24 = 2'b10;
      3'b110 : _zz_24 = 2'b10;
      default : _zz_24 = 2'b11;
    endcase
  end

  always @(*) begin
    case(_zz_LsuPlugin_logic_onCtrl_loadData_shited_1)
      2'b00 : _zz_LsuPlugin_logic_onCtrl_loadData_shited = LsuPlugin_logic_onCtrl_loadData_splited_0;
      2'b01 : _zz_LsuPlugin_logic_onCtrl_loadData_shited = LsuPlugin_logic_onCtrl_loadData_splited_1;
      2'b10 : _zz_LsuPlugin_logic_onCtrl_loadData_shited = LsuPlugin_logic_onCtrl_loadData_splited_2;
      default : _zz_LsuPlugin_logic_onCtrl_loadData_shited = LsuPlugin_logic_onCtrl_loadData_splited_3;
    endcase
  end

  always @(*) begin
    case(_zz_LsuPlugin_logic_onCtrl_loadData_shited_3)
      1'b0 : _zz_LsuPlugin_logic_onCtrl_loadData_shited_2 = LsuPlugin_logic_onCtrl_loadData_splited_1;
      default : _zz_LsuPlugin_logic_onCtrl_loadData_shited_2 = LsuPlugin_logic_onCtrl_loadData_splited_3;
    endcase
  end

  always @(*) begin
    case(CsrRamPlugin_logic_readLogic_sel)
      1'b0 : _zz_CsrRamPlugin_logic_readLogic_port_cmd_payload = TrapPlugin_logic_harts_0_crsPorts_read_address;
      default : _zz_CsrRamPlugin_logic_readLogic_port_cmd_payload = CsrRamPlugin_csrMapper_read_address;
    endcase
  end

  always @(*) begin
    case(_zz_WhiteboxerPlugin_logic_perf_candidatesCount_1)
      1'b0 : _zz_WhiteboxerPlugin_logic_perf_candidatesCount = 1'b0;
      default : _zz_WhiteboxerPlugin_logic_perf_candidatesCount = 1'b1;
    endcase
  end

  always @(*) begin
    case(_zz_WhiteboxerPlugin_logic_perf_dispatchFeedCount_1)
      1'b0 : _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCount = 1'b0;
      default : _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCount = 1'b1;
    endcase
  end

  `ifndef SYNTHESIS
  always @(*) begin
    case(execute_ctrl3_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0)
      IntAluPlugin_AluBitwiseCtrlEnum_XOR_1 : execute_ctrl3_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "XOR_1";
      IntAluPlugin_AluBitwiseCtrlEnum_OR_1 : execute_ctrl3_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "OR_1 ";
      IntAluPlugin_AluBitwiseCtrlEnum_AND_1 : execute_ctrl3_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "AND_1";
      IntAluPlugin_AluBitwiseCtrlEnum_ZERO : execute_ctrl3_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "ZERO ";
      default : execute_ctrl3_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "?????";
    endcase
  end
  always @(*) begin
    case(execute_ctrl3_down_BranchPlugin_BRANCH_CTRL_lane0)
      BranchPlugin_BranchCtrlEnum_B : execute_ctrl3_down_BranchPlugin_BRANCH_CTRL_lane0_string = "B   ";
      BranchPlugin_BranchCtrlEnum_JAL : execute_ctrl3_down_BranchPlugin_BRANCH_CTRL_lane0_string = "JAL ";
      BranchPlugin_BranchCtrlEnum_JALR : execute_ctrl3_down_BranchPlugin_BRANCH_CTRL_lane0_string = "JALR";
      default : execute_ctrl3_down_BranchPlugin_BRANCH_CTRL_lane0_string = "????";
    endcase
  end
  always @(*) begin
    case(execute_ctrl4_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0)
      IntAluPlugin_AluBitwiseCtrlEnum_XOR_1 : execute_ctrl4_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "XOR_1";
      IntAluPlugin_AluBitwiseCtrlEnum_OR_1 : execute_ctrl4_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "OR_1 ";
      IntAluPlugin_AluBitwiseCtrlEnum_AND_1 : execute_ctrl4_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "AND_1";
      IntAluPlugin_AluBitwiseCtrlEnum_ZERO : execute_ctrl4_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "ZERO ";
      default : execute_ctrl4_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "?????";
    endcase
  end
  always @(*) begin
    case(execute_ctrl4_up_BranchPlugin_BRANCH_CTRL_lane0)
      BranchPlugin_BranchCtrlEnum_B : execute_ctrl4_up_BranchPlugin_BRANCH_CTRL_lane0_string = "B   ";
      BranchPlugin_BranchCtrlEnum_JAL : execute_ctrl4_up_BranchPlugin_BRANCH_CTRL_lane0_string = "JAL ";
      BranchPlugin_BranchCtrlEnum_JALR : execute_ctrl4_up_BranchPlugin_BRANCH_CTRL_lane0_string = "JALR";
      default : execute_ctrl4_up_BranchPlugin_BRANCH_CTRL_lane0_string = "????";
    endcase
  end
  always @(*) begin
    case(execute_ctrl2_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0)
      IntAluPlugin_AluBitwiseCtrlEnum_XOR_1 : execute_ctrl2_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "XOR_1";
      IntAluPlugin_AluBitwiseCtrlEnum_OR_1 : execute_ctrl2_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "OR_1 ";
      IntAluPlugin_AluBitwiseCtrlEnum_AND_1 : execute_ctrl2_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "AND_1";
      IntAluPlugin_AluBitwiseCtrlEnum_ZERO : execute_ctrl2_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "ZERO ";
      default : execute_ctrl2_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "?????";
    endcase
  end
  always @(*) begin
    case(execute_ctrl3_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0)
      IntAluPlugin_AluBitwiseCtrlEnum_XOR_1 : execute_ctrl3_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "XOR_1";
      IntAluPlugin_AluBitwiseCtrlEnum_OR_1 : execute_ctrl3_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "OR_1 ";
      IntAluPlugin_AluBitwiseCtrlEnum_AND_1 : execute_ctrl3_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "AND_1";
      IntAluPlugin_AluBitwiseCtrlEnum_ZERO : execute_ctrl3_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "ZERO ";
      default : execute_ctrl3_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "?????";
    endcase
  end
  always @(*) begin
    case(execute_ctrl3_up_BranchPlugin_BRANCH_CTRL_lane0)
      BranchPlugin_BranchCtrlEnum_B : execute_ctrl3_up_BranchPlugin_BRANCH_CTRL_lane0_string = "B   ";
      BranchPlugin_BranchCtrlEnum_JAL : execute_ctrl3_up_BranchPlugin_BRANCH_CTRL_lane0_string = "JAL ";
      BranchPlugin_BranchCtrlEnum_JALR : execute_ctrl3_up_BranchPlugin_BRANCH_CTRL_lane0_string = "JALR";
      default : execute_ctrl3_up_BranchPlugin_BRANCH_CTRL_lane0_string = "????";
    endcase
  end
  always @(*) begin
    case(execute_ctrl2_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0)
      IntAluPlugin_AluBitwiseCtrlEnum_XOR_1 : execute_ctrl2_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "XOR_1";
      IntAluPlugin_AluBitwiseCtrlEnum_OR_1 : execute_ctrl2_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "OR_1 ";
      IntAluPlugin_AluBitwiseCtrlEnum_AND_1 : execute_ctrl2_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "AND_1";
      IntAluPlugin_AluBitwiseCtrlEnum_ZERO : execute_ctrl2_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "ZERO ";
      default : execute_ctrl2_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "?????";
    endcase
  end
  always @(*) begin
    case(execute_ctrl2_up_early0_EnvPlugin_OP_lane0)
      EnvPluginOp_ECALL : execute_ctrl2_up_early0_EnvPlugin_OP_lane0_string = "ECALL     ";
      EnvPluginOp_EBREAK : execute_ctrl2_up_early0_EnvPlugin_OP_lane0_string = "EBREAK    ";
      EnvPluginOp_PRIV_RET : execute_ctrl2_up_early0_EnvPlugin_OP_lane0_string = "PRIV_RET  ";
      EnvPluginOp_FENCE_I : execute_ctrl2_up_early0_EnvPlugin_OP_lane0_string = "FENCE_I   ";
      EnvPluginOp_SFENCE_VMA : execute_ctrl2_up_early0_EnvPlugin_OP_lane0_string = "SFENCE_VMA";
      EnvPluginOp_WFI : execute_ctrl2_up_early0_EnvPlugin_OP_lane0_string = "WFI       ";
      default : execute_ctrl2_up_early0_EnvPlugin_OP_lane0_string = "??????????";
    endcase
  end
  always @(*) begin
    case(execute_ctrl2_up_BranchPlugin_BRANCH_CTRL_lane0)
      BranchPlugin_BranchCtrlEnum_B : execute_ctrl2_up_BranchPlugin_BRANCH_CTRL_lane0_string = "B   ";
      BranchPlugin_BranchCtrlEnum_JAL : execute_ctrl2_up_BranchPlugin_BRANCH_CTRL_lane0_string = "JAL ";
      BranchPlugin_BranchCtrlEnum_JALR : execute_ctrl2_up_BranchPlugin_BRANCH_CTRL_lane0_string = "JALR";
      default : execute_ctrl2_up_BranchPlugin_BRANCH_CTRL_lane0_string = "????";
    endcase
  end
  always @(*) begin
    case(execute_ctrl2_up_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0)
      IntAluPlugin_AluBitwiseCtrlEnum_XOR_1 : execute_ctrl2_up_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "XOR_1";
      IntAluPlugin_AluBitwiseCtrlEnum_OR_1 : execute_ctrl2_up_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "OR_1 ";
      IntAluPlugin_AluBitwiseCtrlEnum_AND_1 : execute_ctrl2_up_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "AND_1";
      IntAluPlugin_AluBitwiseCtrlEnum_ZERO : execute_ctrl2_up_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "ZERO ";
      default : execute_ctrl2_up_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "?????";
    endcase
  end
  always @(*) begin
    case(execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0)
      IntAluPlugin_AluBitwiseCtrlEnum_XOR_1 : execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "XOR_1";
      IntAluPlugin_AluBitwiseCtrlEnum_OR_1 : execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "OR_1 ";
      IntAluPlugin_AluBitwiseCtrlEnum_AND_1 : execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "AND_1";
      IntAluPlugin_AluBitwiseCtrlEnum_ZERO : execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "ZERO ";
      default : execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "?????";
    endcase
  end
  always @(*) begin
    case(execute_ctrl1_down_early0_EnvPlugin_OP_lane0)
      EnvPluginOp_ECALL : execute_ctrl1_down_early0_EnvPlugin_OP_lane0_string = "ECALL     ";
      EnvPluginOp_EBREAK : execute_ctrl1_down_early0_EnvPlugin_OP_lane0_string = "EBREAK    ";
      EnvPluginOp_PRIV_RET : execute_ctrl1_down_early0_EnvPlugin_OP_lane0_string = "PRIV_RET  ";
      EnvPluginOp_FENCE_I : execute_ctrl1_down_early0_EnvPlugin_OP_lane0_string = "FENCE_I   ";
      EnvPluginOp_SFENCE_VMA : execute_ctrl1_down_early0_EnvPlugin_OP_lane0_string = "SFENCE_VMA";
      EnvPluginOp_WFI : execute_ctrl1_down_early0_EnvPlugin_OP_lane0_string = "WFI       ";
      default : execute_ctrl1_down_early0_EnvPlugin_OP_lane0_string = "??????????";
    endcase
  end
  always @(*) begin
    case(execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0)
      BranchPlugin_BranchCtrlEnum_B : execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_string = "B   ";
      BranchPlugin_BranchCtrlEnum_JAL : execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_string = "JAL ";
      BranchPlugin_BranchCtrlEnum_JALR : execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_string = "JALR";
      default : execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_string = "????";
    endcase
  end
  always @(*) begin
    case(execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0)
      IntAluPlugin_AluBitwiseCtrlEnum_XOR_1 : execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "XOR_1";
      IntAluPlugin_AluBitwiseCtrlEnum_OR_1 : execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "OR_1 ";
      IntAluPlugin_AluBitwiseCtrlEnum_AND_1 : execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "AND_1";
      IntAluPlugin_AluBitwiseCtrlEnum_ZERO : execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "ZERO ";
      default : execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "?????";
    endcase
  end
  always @(*) begin
    case(execute_ctrl4_down_BranchPlugin_BRANCH_CTRL_lane0)
      BranchPlugin_BranchCtrlEnum_B : execute_ctrl4_down_BranchPlugin_BRANCH_CTRL_lane0_string = "B   ";
      BranchPlugin_BranchCtrlEnum_JAL : execute_ctrl4_down_BranchPlugin_BRANCH_CTRL_lane0_string = "JAL ";
      BranchPlugin_BranchCtrlEnum_JALR : execute_ctrl4_down_BranchPlugin_BRANCH_CTRL_lane0_string = "JALR";
      default : execute_ctrl4_down_BranchPlugin_BRANCH_CTRL_lane0_string = "????";
    endcase
  end
  always @(*) begin
    case(execute_ctrl2_down_BranchPlugin_BRANCH_CTRL_lane0)
      BranchPlugin_BranchCtrlEnum_B : execute_ctrl2_down_BranchPlugin_BRANCH_CTRL_lane0_string = "B   ";
      BranchPlugin_BranchCtrlEnum_JAL : execute_ctrl2_down_BranchPlugin_BRANCH_CTRL_lane0_string = "JAL ";
      BranchPlugin_BranchCtrlEnum_JALR : execute_ctrl2_down_BranchPlugin_BRANCH_CTRL_lane0_string = "JALR";
      default : execute_ctrl2_down_BranchPlugin_BRANCH_CTRL_lane0_string = "????";
    endcase
  end
  always @(*) begin
    case(execute_ctrl2_down_early0_EnvPlugin_OP_lane0)
      EnvPluginOp_ECALL : execute_ctrl2_down_early0_EnvPlugin_OP_lane0_string = "ECALL     ";
      EnvPluginOp_EBREAK : execute_ctrl2_down_early0_EnvPlugin_OP_lane0_string = "EBREAK    ";
      EnvPluginOp_PRIV_RET : execute_ctrl2_down_early0_EnvPlugin_OP_lane0_string = "PRIV_RET  ";
      EnvPluginOp_FENCE_I : execute_ctrl2_down_early0_EnvPlugin_OP_lane0_string = "FENCE_I   ";
      EnvPluginOp_SFENCE_VMA : execute_ctrl2_down_early0_EnvPlugin_OP_lane0_string = "SFENCE_VMA";
      EnvPluginOp_WFI : execute_ctrl2_down_early0_EnvPlugin_OP_lane0_string = "WFI       ";
      default : execute_ctrl2_down_early0_EnvPlugin_OP_lane0_string = "??????????";
    endcase
  end
  always @(*) begin
    case(execute_ctrl4_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0)
      IntAluPlugin_AluBitwiseCtrlEnum_XOR_1 : execute_ctrl4_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "XOR_1";
      IntAluPlugin_AluBitwiseCtrlEnum_OR_1 : execute_ctrl4_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "OR_1 ";
      IntAluPlugin_AluBitwiseCtrlEnum_AND_1 : execute_ctrl4_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "AND_1";
      IntAluPlugin_AluBitwiseCtrlEnum_ZERO : execute_ctrl4_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "ZERO ";
      default : execute_ctrl4_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "?????";
    endcase
  end
  always @(*) begin
    case(execute_ctrl2_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0)
      IntAluPlugin_AluBitwiseCtrlEnum_XOR_1 : execute_ctrl2_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "XOR_1";
      IntAluPlugin_AluBitwiseCtrlEnum_OR_1 : execute_ctrl2_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "OR_1 ";
      IntAluPlugin_AluBitwiseCtrlEnum_AND_1 : execute_ctrl2_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "AND_1";
      IntAluPlugin_AluBitwiseCtrlEnum_ZERO : execute_ctrl2_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "ZERO ";
      default : execute_ctrl2_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "?????";
    endcase
  end
  always @(*) begin
    case(LsuPlugin_logic_onAddress0_ls_port_payload_op)
      LsuL1CmdOpcode_LSU : LsuPlugin_logic_onAddress0_ls_port_payload_op_string = "LSU         ";
      LsuL1CmdOpcode_ACCESS_1 : LsuPlugin_logic_onAddress0_ls_port_payload_op_string = "ACCESS_1    ";
      LsuL1CmdOpcode_STORE_BUFFER : LsuPlugin_logic_onAddress0_ls_port_payload_op_string = "STORE_BUFFER";
      LsuL1CmdOpcode_FLUSH : LsuPlugin_logic_onAddress0_ls_port_payload_op_string = "FLUSH       ";
      LsuL1CmdOpcode_PREFETCH : LsuPlugin_logic_onAddress0_ls_port_payload_op_string = "PREFETCH    ";
      default : LsuPlugin_logic_onAddress0_ls_port_payload_op_string = "????????????";
    endcase
  end
  always @(*) begin
    case(LsuPlugin_logic_onAddress0_flush_port_payload_op)
      LsuL1CmdOpcode_LSU : LsuPlugin_logic_onAddress0_flush_port_payload_op_string = "LSU         ";
      LsuL1CmdOpcode_ACCESS_1 : LsuPlugin_logic_onAddress0_flush_port_payload_op_string = "ACCESS_1    ";
      LsuL1CmdOpcode_STORE_BUFFER : LsuPlugin_logic_onAddress0_flush_port_payload_op_string = "STORE_BUFFER";
      LsuL1CmdOpcode_FLUSH : LsuPlugin_logic_onAddress0_flush_port_payload_op_string = "FLUSH       ";
      LsuL1CmdOpcode_PREFETCH : LsuPlugin_logic_onAddress0_flush_port_payload_op_string = "PREFETCH    ";
      default : LsuPlugin_logic_onAddress0_flush_port_payload_op_string = "????????????";
    endcase
  end
  always @(*) begin
    case(_zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0)
      IntAluPlugin_AluBitwiseCtrlEnum_XOR_1 : _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "XOR_1";
      IntAluPlugin_AluBitwiseCtrlEnum_OR_1 : _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "OR_1 ";
      IntAluPlugin_AluBitwiseCtrlEnum_AND_1 : _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "AND_1";
      IntAluPlugin_AluBitwiseCtrlEnum_ZERO : _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "ZERO ";
      default : _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_string = "?????";
    endcase
  end
  always @(*) begin
    case(_zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_1)
      IntAluPlugin_AluBitwiseCtrlEnum_XOR_1 : _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_1_string = "XOR_1";
      IntAluPlugin_AluBitwiseCtrlEnum_OR_1 : _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_1_string = "OR_1 ";
      IntAluPlugin_AluBitwiseCtrlEnum_AND_1 : _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_1_string = "AND_1";
      IntAluPlugin_AluBitwiseCtrlEnum_ZERO : _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_1_string = "ZERO ";
      default : _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_1_string = "?????";
    endcase
  end
  always @(*) begin
    case(_zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_2)
      IntAluPlugin_AluBitwiseCtrlEnum_XOR_1 : _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_2_string = "XOR_1";
      IntAluPlugin_AluBitwiseCtrlEnum_OR_1 : _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_2_string = "OR_1 ";
      IntAluPlugin_AluBitwiseCtrlEnum_AND_1 : _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_2_string = "AND_1";
      IntAluPlugin_AluBitwiseCtrlEnum_ZERO : _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_2_string = "ZERO ";
      default : _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_2_string = "?????";
    endcase
  end
  always @(*) begin
    case(_zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0)
      BranchPlugin_BranchCtrlEnum_B : _zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_string = "B   ";
      BranchPlugin_BranchCtrlEnum_JAL : _zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_string = "JAL ";
      BranchPlugin_BranchCtrlEnum_JALR : _zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_string = "JALR";
      default : _zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_string = "????";
    endcase
  end
  always @(*) begin
    case(_zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_1)
      BranchPlugin_BranchCtrlEnum_B : _zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_1_string = "B   ";
      BranchPlugin_BranchCtrlEnum_JAL : _zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_1_string = "JAL ";
      BranchPlugin_BranchCtrlEnum_JALR : _zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_1_string = "JALR";
      default : _zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_1_string = "????";
    endcase
  end
  always @(*) begin
    case(_zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_2)
      BranchPlugin_BranchCtrlEnum_B : _zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_2_string = "B   ";
      BranchPlugin_BranchCtrlEnum_JAL : _zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_2_string = "JAL ";
      BranchPlugin_BranchCtrlEnum_JALR : _zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_2_string = "JALR";
      default : _zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_2_string = "????";
    endcase
  end
  always @(*) begin
    case(_zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_1)
      EnvPluginOp_ECALL : _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_1_string = "ECALL     ";
      EnvPluginOp_EBREAK : _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_1_string = "EBREAK    ";
      EnvPluginOp_PRIV_RET : _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_1_string = "PRIV_RET  ";
      EnvPluginOp_FENCE_I : _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_1_string = "FENCE_I   ";
      EnvPluginOp_SFENCE_VMA : _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_1_string = "SFENCE_VMA";
      EnvPluginOp_WFI : _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_1_string = "WFI       ";
      default : _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_1_string = "??????????";
    endcase
  end
  always @(*) begin
    case(_zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_2)
      EnvPluginOp_ECALL : _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_2_string = "ECALL     ";
      EnvPluginOp_EBREAK : _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_2_string = "EBREAK    ";
      EnvPluginOp_PRIV_RET : _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_2_string = "PRIV_RET  ";
      EnvPluginOp_FENCE_I : _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_2_string = "FENCE_I   ";
      EnvPluginOp_SFENCE_VMA : _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_2_string = "SFENCE_VMA";
      EnvPluginOp_WFI : _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_2_string = "WFI       ";
      default : _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_2_string = "??????????";
    endcase
  end
  always @(*) begin
    case(_zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_3)
      EnvPluginOp_ECALL : _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_3_string = "ECALL     ";
      EnvPluginOp_EBREAK : _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_3_string = "EBREAK    ";
      EnvPluginOp_PRIV_RET : _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_3_string = "PRIV_RET  ";
      EnvPluginOp_FENCE_I : _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_3_string = "FENCE_I   ";
      EnvPluginOp_SFENCE_VMA : _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_3_string = "SFENCE_VMA";
      EnvPluginOp_WFI : _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_3_string = "WFI       ";
      default : _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_3_string = "??????????";
    endcase
  end
  always @(*) begin
    case(_zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_1)
      IntAluPlugin_AluBitwiseCtrlEnum_XOR_1 : _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_1_string = "XOR_1";
      IntAluPlugin_AluBitwiseCtrlEnum_OR_1 : _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_1_string = "OR_1 ";
      IntAluPlugin_AluBitwiseCtrlEnum_AND_1 : _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_1_string = "AND_1";
      IntAluPlugin_AluBitwiseCtrlEnum_ZERO : _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_1_string = "ZERO ";
      default : _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_1_string = "?????";
    endcase
  end
  always @(*) begin
    case(_zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_2)
      IntAluPlugin_AluBitwiseCtrlEnum_XOR_1 : _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_2_string = "XOR_1";
      IntAluPlugin_AluBitwiseCtrlEnum_OR_1 : _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_2_string = "OR_1 ";
      IntAluPlugin_AluBitwiseCtrlEnum_AND_1 : _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_2_string = "AND_1";
      IntAluPlugin_AluBitwiseCtrlEnum_ZERO : _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_2_string = "ZERO ";
      default : _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_2_string = "?????";
    endcase
  end
  always @(*) begin
    case(_zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_3)
      IntAluPlugin_AluBitwiseCtrlEnum_XOR_1 : _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_3_string = "XOR_1";
      IntAluPlugin_AluBitwiseCtrlEnum_OR_1 : _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_3_string = "OR_1 ";
      IntAluPlugin_AluBitwiseCtrlEnum_AND_1 : _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_3_string = "AND_1";
      IntAluPlugin_AluBitwiseCtrlEnum_ZERO : _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_3_string = "ZERO ";
      default : _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_3_string = "?????";
    endcase
  end
  always @(*) begin
    case(LsuPlugin_logic_flusher_stateReg)
      LsuPlugin_logic_flusher_IDLE : LsuPlugin_logic_flusher_stateReg_string = "IDLE      ";
      LsuPlugin_logic_flusher_CMD : LsuPlugin_logic_flusher_stateReg_string = "CMD       ";
      LsuPlugin_logic_flusher_COMPLETION : LsuPlugin_logic_flusher_stateReg_string = "COMPLETION";
      default : LsuPlugin_logic_flusher_stateReg_string = "??????????";
    endcase
  end
  always @(*) begin
    case(LsuPlugin_logic_flusher_stateNext)
      LsuPlugin_logic_flusher_IDLE : LsuPlugin_logic_flusher_stateNext_string = "IDLE      ";
      LsuPlugin_logic_flusher_CMD : LsuPlugin_logic_flusher_stateNext_string = "CMD       ";
      LsuPlugin_logic_flusher_COMPLETION : LsuPlugin_logic_flusher_stateNext_string = "COMPLETION";
      default : LsuPlugin_logic_flusher_stateNext_string = "??????????";
    endcase
  end
  always @(*) begin
    case(TrapPlugin_logic_harts_0_trap_fsm_stateReg)
      TrapPlugin_logic_harts_0_trap_fsm_RESET : TrapPlugin_logic_harts_0_trap_fsm_stateReg_string = "RESET      ";
      TrapPlugin_logic_harts_0_trap_fsm_RUNNING : TrapPlugin_logic_harts_0_trap_fsm_stateReg_string = "RUNNING    ";
      TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1 : TrapPlugin_logic_harts_0_trap_fsm_stateReg_string = "PROCESS_1  ";
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC : TrapPlugin_logic_harts_0_trap_fsm_stateReg_string = "TRAP_EPC   ";
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL : TrapPlugin_logic_harts_0_trap_fsm_stateReg_string = "TRAP_TVAL  ";
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC : TrapPlugin_logic_harts_0_trap_fsm_stateReg_string = "TRAP_TVEC  ";
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY : TrapPlugin_logic_harts_0_trap_fsm_stateReg_string = "TRAP_APPLY ";
      TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC : TrapPlugin_logic_harts_0_trap_fsm_stateReg_string = "XRET_EPC   ";
      TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY : TrapPlugin_logic_harts_0_trap_fsm_stateReg_string = "XRET_APPLY ";
      TrapPlugin_logic_harts_0_trap_fsm_JUMP : TrapPlugin_logic_harts_0_trap_fsm_stateReg_string = "JUMP       ";
      TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH : TrapPlugin_logic_harts_0_trap_fsm_stateReg_string = "LSU_FLUSH  ";
      TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH : TrapPlugin_logic_harts_0_trap_fsm_stateReg_string = "FETCH_FLUSH";
      default : TrapPlugin_logic_harts_0_trap_fsm_stateReg_string = "???????????";
    endcase
  end
  always @(*) begin
    case(TrapPlugin_logic_harts_0_trap_fsm_stateNext)
      TrapPlugin_logic_harts_0_trap_fsm_RESET : TrapPlugin_logic_harts_0_trap_fsm_stateNext_string = "RESET      ";
      TrapPlugin_logic_harts_0_trap_fsm_RUNNING : TrapPlugin_logic_harts_0_trap_fsm_stateNext_string = "RUNNING    ";
      TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1 : TrapPlugin_logic_harts_0_trap_fsm_stateNext_string = "PROCESS_1  ";
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC : TrapPlugin_logic_harts_0_trap_fsm_stateNext_string = "TRAP_EPC   ";
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL : TrapPlugin_logic_harts_0_trap_fsm_stateNext_string = "TRAP_TVAL  ";
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC : TrapPlugin_logic_harts_0_trap_fsm_stateNext_string = "TRAP_TVEC  ";
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY : TrapPlugin_logic_harts_0_trap_fsm_stateNext_string = "TRAP_APPLY ";
      TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC : TrapPlugin_logic_harts_0_trap_fsm_stateNext_string = "XRET_EPC   ";
      TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY : TrapPlugin_logic_harts_0_trap_fsm_stateNext_string = "XRET_APPLY ";
      TrapPlugin_logic_harts_0_trap_fsm_JUMP : TrapPlugin_logic_harts_0_trap_fsm_stateNext_string = "JUMP       ";
      TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH : TrapPlugin_logic_harts_0_trap_fsm_stateNext_string = "LSU_FLUSH  ";
      TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH : TrapPlugin_logic_harts_0_trap_fsm_stateNext_string = "FETCH_FLUSH";
      default : TrapPlugin_logic_harts_0_trap_fsm_stateNext_string = "???????????";
    endcase
  end
  always @(*) begin
    case(CsrAccessPlugin_logic_fsm_stateReg)
      CsrAccessPlugin_logic_fsm_IDLE : CsrAccessPlugin_logic_fsm_stateReg_string = "IDLE      ";
      CsrAccessPlugin_logic_fsm_READ : CsrAccessPlugin_logic_fsm_stateReg_string = "READ      ";
      CsrAccessPlugin_logic_fsm_WRITE : CsrAccessPlugin_logic_fsm_stateReg_string = "WRITE     ";
      CsrAccessPlugin_logic_fsm_COMPLETION : CsrAccessPlugin_logic_fsm_stateReg_string = "COMPLETION";
      default : CsrAccessPlugin_logic_fsm_stateReg_string = "??????????";
    endcase
  end
  always @(*) begin
    case(CsrAccessPlugin_logic_fsm_stateNext)
      CsrAccessPlugin_logic_fsm_IDLE : CsrAccessPlugin_logic_fsm_stateNext_string = "IDLE      ";
      CsrAccessPlugin_logic_fsm_READ : CsrAccessPlugin_logic_fsm_stateNext_string = "READ      ";
      CsrAccessPlugin_logic_fsm_WRITE : CsrAccessPlugin_logic_fsm_stateNext_string = "WRITE     ";
      CsrAccessPlugin_logic_fsm_COMPLETION : CsrAccessPlugin_logic_fsm_stateNext_string = "COMPLETION";
      default : CsrAccessPlugin_logic_fsm_stateNext_string = "??????????";
    endcase
  end
  `endif

  assign execute_ctrl4_down_RD_ENABLE_lane0 = execute_ctrl4_RD_ENABLE_lane0_bypass;
  always @(*) begin
    execute_ctrl4_RD_ENABLE_lane0_bypass = execute_ctrl4_up_RD_ENABLE_lane0;
    if(when_ExecuteLanePlugin_l306_4) begin
      execute_ctrl4_RD_ENABLE_lane0_bypass = 1'b0;
    end
  end

  assign execute_ctrl4_down_LANE_SEL_lane0 = execute_ctrl4_LANE_SEL_lane0_bypass;
  always @(*) begin
    execute_ctrl4_LANE_SEL_lane0_bypass = execute_ctrl4_up_LANE_SEL_lane0;
    if(when_ExecuteLanePlugin_l306_4) begin
      execute_ctrl4_LANE_SEL_lane0_bypass = 1'b0;
    end
  end

  assign execute_ctrl3_down_RD_ENABLE_lane0 = execute_ctrl3_RD_ENABLE_lane0_bypass;
  always @(*) begin
    execute_ctrl3_RD_ENABLE_lane0_bypass = execute_ctrl3_up_RD_ENABLE_lane0;
    if(when_ExecuteLanePlugin_l306_3) begin
      execute_ctrl3_RD_ENABLE_lane0_bypass = 1'b0;
    end
  end

  assign execute_ctrl3_down_LANE_SEL_lane0 = execute_ctrl3_LANE_SEL_lane0_bypass;
  always @(*) begin
    execute_ctrl3_LANE_SEL_lane0_bypass = execute_ctrl3_up_LANE_SEL_lane0;
    if(when_ExecuteLanePlugin_l306_3) begin
      execute_ctrl3_LANE_SEL_lane0_bypass = 1'b0;
    end
  end

  assign execute_ctrl2_down_RD_ENABLE_lane0 = execute_ctrl2_RD_ENABLE_lane0_bypass;
  always @(*) begin
    execute_ctrl2_RD_ENABLE_lane0_bypass = execute_ctrl2_up_RD_ENABLE_lane0;
    if(when_ExecuteLanePlugin_l306_2) begin
      execute_ctrl2_RD_ENABLE_lane0_bypass = 1'b0;
    end
  end

  assign execute_ctrl2_down_LANE_SEL_lane0 = execute_ctrl2_LANE_SEL_lane0_bypass;
  always @(*) begin
    execute_ctrl2_LANE_SEL_lane0_bypass = execute_ctrl2_up_LANE_SEL_lane0;
    if(when_ExecuteLanePlugin_l306_2) begin
      execute_ctrl2_LANE_SEL_lane0_bypass = 1'b0;
    end
  end

  assign execute_ctrl1_down_RD_ENABLE_lane0 = execute_ctrl1_RD_ENABLE_lane0_bypass;
  always @(*) begin
    execute_ctrl1_RD_ENABLE_lane0_bypass = execute_ctrl1_up_RD_ENABLE_lane0;
    if(when_ExecuteLanePlugin_l306_1) begin
      execute_ctrl1_RD_ENABLE_lane0_bypass = 1'b0;
    end
  end

  assign execute_ctrl1_down_LANE_SEL_lane0 = execute_ctrl1_LANE_SEL_lane0_bypass;
  always @(*) begin
    execute_ctrl1_LANE_SEL_lane0_bypass = execute_ctrl1_up_LANE_SEL_lane0;
    if(when_ExecuteLanePlugin_l306_1) begin
      execute_ctrl1_LANE_SEL_lane0_bypass = 1'b0;
    end
  end

  assign execute_ctrl0_down_RD_ENABLE_lane0 = execute_ctrl0_RD_ENABLE_lane0_bypass;
  always @(*) begin
    execute_ctrl0_RD_ENABLE_lane0_bypass = execute_ctrl0_up_RD_ENABLE_lane0;
    if(when_ExecuteLanePlugin_l306) begin
      execute_ctrl0_RD_ENABLE_lane0_bypass = 1'b0;
    end
  end

  assign execute_ctrl0_down_LANE_SEL_lane0 = execute_ctrl0_LANE_SEL_lane0_bypass;
  always @(*) begin
    execute_ctrl0_LANE_SEL_lane0_bypass = execute_ctrl0_up_LANE_SEL_lane0;
    if(when_ExecuteLanePlugin_l306) begin
      execute_ctrl0_LANE_SEL_lane0_bypass = 1'b0;
    end
  end

  assign execute_ctrl3_down_integer_RS2_lane0 = execute_ctrl3_integer_RS2_lane0_bypass;
  assign execute_ctrl2_down_integer_RS2_lane0 = execute_ctrl2_integer_RS2_lane0_bypass;
  assign execute_ctrl3_down_integer_RS1_lane0 = execute_ctrl3_integer_RS1_lane0_bypass;
  assign execute_ctrl2_down_integer_RS1_lane0 = execute_ctrl2_integer_RS1_lane0_bypass;
  always @(*) begin
    _zz_1 = 1'b0;
    if(CsrRamPlugin_logic_writeLogic_port_valid) begin
      _zz_1 = 1'b1;
    end
  end

  assign decode_ctrls_1_down_LANE_SEL_0 = decode_ctrls_1_LANE_SEL_0_bypass;
  always @(*) begin
    decode_ctrls_1_LANE_SEL_0_bypass = decode_ctrls_1_up_LANE_SEL_0;
    if(decode_logic_flushes_1_onLanes_0_doIt) begin
      decode_ctrls_1_LANE_SEL_0_bypass = 1'b0;
    end
  end

  assign decode_ctrls_0_down_LANE_SEL_0 = decode_ctrls_0_LANE_SEL_0_bypass;
  always @(*) begin
    decode_ctrls_0_LANE_SEL_0_bypass = decode_ctrls_0_up_LANE_SEL_0;
    if(decode_logic_flushes_0_onLanes_0_doIt) begin
      decode_ctrls_0_LANE_SEL_0_bypass = 1'b0;
    end
  end

  assign execute_ctrl4_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0 = execute_ctrl4_lane0_integer_WriteBackPlugin_logic_DATA_lane0_bypass;
  assign execute_ctrl3_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0 = execute_ctrl3_lane0_integer_WriteBackPlugin_logic_DATA_lane0_bypass;
  assign execute_ctrl2_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0 = execute_ctrl2_lane0_integer_WriteBackPlugin_logic_DATA_lane0_bypass;
  assign decode_ctrls_1_down_TRAP_0 = decode_ctrls_1_TRAP_0_bypass;
  always @(*) begin
    decode_ctrls_1_TRAP_0_bypass = decode_ctrls_1_up_TRAP_0;
    if(when_DecoderPlugin_l229) begin
      decode_ctrls_1_TRAP_0_bypass = 1'b1;
    end
  end

  assign execute_ctrl3_down_COMPLETED_lane0 = execute_ctrl3_COMPLETED_lane0_bypass;
  assign execute_ctrl4_down_COMPLETED_lane0 = execute_ctrl4_COMPLETED_lane0_bypass;
  assign execute_ctrl2_down_COMPLETED_lane0 = execute_ctrl2_COMPLETED_lane0_bypass;
  assign execute_ctrl4_down_COMMIT_lane0 = execute_ctrl4_COMMIT_lane0_bypass;
  always @(*) begin
    execute_ctrl4_COMMIT_lane0_bypass = execute_ctrl4_up_COMMIT_lane0;
    if(when_LsuPlugin_l859) begin
      if(LsuPlugin_logic_onCtrl_lsuTrap) begin
        execute_ctrl4_COMMIT_lane0_bypass = 1'b0;
      end
    end
    if(when_BranchPlugin_l251_1) begin
      execute_ctrl4_COMMIT_lane0_bypass = 1'b0;
    end
  end

  assign execute_ctrl4_down_TRAP_lane0 = execute_ctrl4_TRAP_lane0_bypass;
  always @(*) begin
    execute_ctrl4_TRAP_lane0_bypass = execute_ctrl4_up_TRAP_lane0;
    if(when_LsuPlugin_l859) begin
      if(LsuPlugin_logic_onCtrl_lsuTrap) begin
        execute_ctrl4_TRAP_lane0_bypass = 1'b1;
      end
    end
    if(when_BranchPlugin_l251_1) begin
      execute_ctrl4_TRAP_lane0_bypass = 1'b1;
    end
  end

  assign execute_ctrl4_down_LsuL1_SEL_lane0 = execute_ctrl4_LsuL1_SEL_lane0_bypass;
  always @(*) begin
    execute_ctrl4_LsuL1_SEL_lane0_bypass = execute_ctrl4_up_LsuL1_SEL_lane0;
    if(when_LsuPlugin_l546_1) begin
      execute_ctrl4_LsuL1_SEL_lane0_bypass = 1'b0;
    end
  end

  assign execute_ctrl3_down_LsuL1_SEL_lane0 = execute_ctrl3_LsuL1_SEL_lane0_bypass;
  always @(*) begin
    execute_ctrl3_LsuL1_SEL_lane0_bypass = execute_ctrl3_up_LsuL1_SEL_lane0;
    if(when_LsuPlugin_l546) begin
      execute_ctrl3_LsuL1_SEL_lane0_bypass = 1'b0;
    end
  end

  assign execute_ctrl2_down_COMMIT_lane0 = execute_ctrl2_COMMIT_lane0_bypass;
  always @(*) begin
    execute_ctrl2_COMMIT_lane0_bypass = execute_ctrl2_up_COMMIT_lane0;
    if(when_EnvPlugin_l119) begin
      if(when_EnvPlugin_l123) begin
        execute_ctrl2_COMMIT_lane0_bypass = 1'b0;
      end
    end
    if(when_BranchPlugin_l251) begin
      execute_ctrl2_COMMIT_lane0_bypass = 1'b0;
    end
    case(CsrAccessPlugin_logic_fsm_stateReg)
      CsrAccessPlugin_logic_fsm_READ : begin
      end
      CsrAccessPlugin_logic_fsm_WRITE : begin
      end
      CsrAccessPlugin_logic_fsm_COMPLETION : begin
      end
      default : begin
        if(CsrAccessPlugin_logic_fsm_inject_onDecodeDo) begin
          if(CsrAccessPlugin_logic_fsm_inject_sampled) begin
            if(CsrAccessPlugin_logic_fsm_inject_trapReg) begin
              execute_ctrl2_COMMIT_lane0_bypass = 1'b0;
            end
          end
        end
      end
    endcase
  end

  assign execute_ctrl2_down_TRAP_lane0 = execute_ctrl2_TRAP_lane0_bypass;
  always @(*) begin
    execute_ctrl2_TRAP_lane0_bypass = execute_ctrl2_up_TRAP_lane0;
    if(when_EnvPlugin_l119) begin
      execute_ctrl2_TRAP_lane0_bypass = 1'b1;
    end
    if(when_BranchPlugin_l251) begin
      execute_ctrl2_TRAP_lane0_bypass = 1'b1;
    end
    if(CsrAccessPlugin_logic_fsm_inject_flushReg) begin
      execute_ctrl2_TRAP_lane0_bypass = 1'b1;
    end
    case(CsrAccessPlugin_logic_fsm_stateReg)
      CsrAccessPlugin_logic_fsm_READ : begin
      end
      CsrAccessPlugin_logic_fsm_WRITE : begin
      end
      CsrAccessPlugin_logic_fsm_COMPLETION : begin
      end
      default : begin
        if(CsrAccessPlugin_logic_fsm_inject_onDecodeDo) begin
          if(CsrAccessPlugin_logic_fsm_inject_sampled) begin
            if(CsrAccessPlugin_logic_fsm_inject_trapReg) begin
              execute_ctrl2_TRAP_lane0_bypass = 1'b1;
            end else begin
              if(CsrAccessPlugin_logic_fsm_inject_busTrapReg) begin
                execute_ctrl2_TRAP_lane0_bypass = 1'b1;
              end
            end
          end
        end
      end
    endcase
  end

  always @(*) begin
    _zz_fetch_logic_ctrls_0_haltRequest_FetchL1Plugin_l217 = 1'b0;
    if(when_FetchL1Plugin_l216) begin
      _zz_fetch_logic_ctrls_0_haltRequest_FetchL1Plugin_l217 = 1'b1;
    end
  end

  always @(*) begin
    _zz_2 = 1'b0;
    if(FetchL1Plugin_logic_banks_0_write_valid) begin
      _zz_2 = 1'b1;
    end
  end

  assign execute_ctrl3_down_LsuL1Plugin_logic_SHARED_lane0_dirty = execute_ctrl3_LsuL1Plugin_logic_SHARED_lane0_bypass_dirty;
  always @(*) begin
    _zz_3 = 1'b0;
    if(LsuL1Plugin_logic_writeback_read_slotReadLast_valid) begin
      _zz_3 = 1'b1;
    end
  end

  always @(*) begin
    _zz_4 = 1'b0;
    if(LsuL1Plugin_logic_shared_write_valid) begin
      _zz_4 = 1'b1;
    end
  end

  assign AlignerPlugin_api_singleFetch = 1'b0;
  assign AlignerPlugin_api_haltIt = 1'b0;
  always @(*) begin
    DispatchPlugin_api_haltDispatch = 1'b0;
    if(LsuPlugin_logic_onCtrl_hartRegulation_valid) begin
      DispatchPlugin_api_haltDispatch = 1'b1;
    end
  end

  assign CsrRamPlugin_api_holdRead = 1'b0;
  assign CsrRamPlugin_api_holdWrite = 1'b0;
  assign PrivilegedPlugin_api_harts_0_allowInterrupts = 1'b1;
  assign PrivilegedPlugin_api_harts_0_allowException = 1'b1;
  assign PrivilegedPlugin_api_harts_0_allowEbreakException = 1'b1;
  assign PrivilegedPlugin_api_harts_0_fpuEnable = 1'b0;
  always @(*) begin
    TrapPlugin_api_harts_0_redo = 1'b0;
    case(TrapPlugin_logic_harts_0_trap_fsm_stateReg)
      TrapPlugin_logic_harts_0_trap_fsm_RUNNING : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1 : begin
        if(!when_TrapPlugin_l409) begin
          case(TrapPlugin_logic_harts_0_trap_pending_state_code)
            4'b0000 : begin
            end
            4'b0001 : begin
            end
            4'b0010 : begin
            end
            4'b0100 : begin
              TrapPlugin_api_harts_0_redo = 1'b1;
            end
            4'b0101 : begin
            end
            4'b1000 : begin
            end
            4'b0110 : begin
            end
            default : begin
            end
          endcase
        end
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_JUMP : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH : begin
      end
      default : begin
      end
    endcase
  end

  always @(*) begin
    TrapPlugin_api_harts_0_askWake = 1'b0;
    if(when_TrapPlugin_l226) begin
      TrapPlugin_api_harts_0_askWake = 1'b1;
    end
  end

  always @(*) begin
    TrapPlugin_api_harts_0_rvTrap = 1'b0;
    case(TrapPlugin_logic_harts_0_trap_fsm_stateReg)
      TrapPlugin_logic_harts_0_trap_fsm_RUNNING : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1 : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY : begin
        TrapPlugin_api_harts_0_rvTrap = 1'b1;
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_JUMP : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH : begin
      end
      default : begin
      end
    endcase
  end

  always @(*) begin
    case(execute_ctrl2_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0)
      IntAluPlugin_AluBitwiseCtrlEnum_AND_1 : begin
        early0_IntAluPlugin_logic_alu_bitwise = (execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0 & execute_ctrl2_down_early0_SrcPlugin_SRC2_lane0);
      end
      IntAluPlugin_AluBitwiseCtrlEnum_OR_1 : begin
        early0_IntAluPlugin_logic_alu_bitwise = (execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0 | execute_ctrl2_down_early0_SrcPlugin_SRC2_lane0);
      end
      IntAluPlugin_AluBitwiseCtrlEnum_XOR_1 : begin
        early0_IntAluPlugin_logic_alu_bitwise = (execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0 ^ execute_ctrl2_down_early0_SrcPlugin_SRC2_lane0);
      end
      default : begin
        early0_IntAluPlugin_logic_alu_bitwise = 32'h0;
      end
    endcase
  end

  assign early0_IntAluPlugin_logic_alu_result = (_zz_early0_IntAluPlugin_logic_alu_result | _zz_early0_IntAluPlugin_logic_alu_result_2);
  assign execute_ctrl2_down_early0_IntAluPlugin_ALU_RESULT_lane0 = early0_IntAluPlugin_logic_alu_result;
  assign early0_IntAluPlugin_logic_wb_valid = execute_ctrl2_down_early0_IntAluPlugin_SEL_lane0;
  assign early0_IntAluPlugin_logic_wb_payload = execute_ctrl2_down_early0_IntAluPlugin_ALU_RESULT_lane0;
  assign early0_BarrelShifterPlugin_logic_shift_amplitude = _zz_early0_BarrelShifterPlugin_logic_shift_amplitude;
  assign early0_BarrelShifterPlugin_logic_shift_reversed = (execute_ctrl2_down_BarrelShifterPlugin_LEFT_lane0 ? _zz_early0_BarrelShifterPlugin_logic_shift_reversed : execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0);
  assign early0_BarrelShifterPlugin_logic_shift_shifted = _zz_early0_BarrelShifterPlugin_logic_shift_shifted[31:0];
  assign early0_BarrelShifterPlugin_logic_shift_patched = (execute_ctrl2_down_BarrelShifterPlugin_LEFT_lane0 ? _zz_early0_BarrelShifterPlugin_logic_shift_patched : early0_BarrelShifterPlugin_logic_shift_shifted);
  assign execute_ctrl2_down_early0_BarrelShifterPlugin_SHIFT_RESULT_lane0 = early0_BarrelShifterPlugin_logic_shift_patched;
  assign early0_BarrelShifterPlugin_logic_wb_valid = execute_ctrl2_down_early0_BarrelShifterPlugin_SEL_lane0;
  assign early0_BarrelShifterPlugin_logic_wb_payload = execute_ctrl2_down_early0_BarrelShifterPlugin_SHIFT_RESULT_lane0;
  always @(*) begin
    LsuL1_ackUnlock = 1'b0;
    if(LsuPlugin_logic_onCtrl_io_cmdSent) begin
      LsuL1_ackUnlock = 1'b1;
    end
  end

  always @(*) begin
    LsuL1Plugin_logic_banksWrite_address = 8'bxxxxxxxx;
    LsuL1Plugin_logic_banksWrite_address = {LsuL1Plugin_logic_refill_read_rspAddress[9 : 6],LsuL1Plugin_logic_refill_read_wordIndex};
    if(LsuL1Plugin_logic_lsu_ctrl_bankWriteReservation_win) begin
      LsuL1Plugin_logic_banksWrite_address = execute_ctrl4_down_LsuL1_PHYSICAL_ADDRESS_lane0[9 : 2];
    end
  end

  always @(*) begin
    LsuL1Plugin_logic_banksWrite_writeData = 32'bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx;
    LsuL1Plugin_logic_banksWrite_writeData = LsuL1Plugin_logic_bus_read_rsp_payload_data;
    if(LsuL1Plugin_logic_lsu_ctrl_bankWriteReservation_win) begin
      LsuL1Plugin_logic_banksWrite_writeData[31 : 0] = execute_ctrl4_down_LsuL1_WRITE_DATA_lane0;
    end
  end

  always @(*) begin
    LsuL1Plugin_logic_banksWrite_writeMask = 4'bxxxx;
    LsuL1Plugin_logic_banksWrite_writeMask = 4'b1111;
    if(LsuL1Plugin_logic_lsu_ctrl_bankWriteReservation_win) begin
      LsuL1Plugin_logic_banksWrite_writeMask = 4'b0000;
      if(_zz_when[0]) begin
        LsuL1Plugin_logic_banksWrite_writeMask[3 : 0] = execute_ctrl4_down_LsuL1_MASK_lane0;
      end
    end
    if(LsuL1Plugin_logic_lsu_ctrl_preventSideEffects) begin
      if(LsuL1Plugin_logic_lsu_ctrl_bankWriteReservation_win) begin
        LsuL1Plugin_logic_banksWrite_writeMask = 4'b0000;
      end
    end
  end

  always @(*) begin
    LsuL1Plugin_logic_waysWrite_mask = 1'b0;
    if(LsuL1Plugin_logic_bus_read_rsp_valid) begin
      if(when_LsuL1Plugin_l463) begin
        LsuL1Plugin_logic_waysWrite_mask[0] = 1'b1;
      end
    end
    if(LsuL1Plugin_logic_lsu_ctrl_doFlush) begin
      LsuL1Plugin_logic_waysWrite_mask = LsuL1Plugin_logic_lsu_ctrl_needFlushOh;
    end
    if(LsuL1Plugin_logic_lsu_ctrl_preventSideEffects) begin
      if(LsuL1Plugin_logic_lsu_ctrl_wayWriteReservation_win) begin
        LsuL1Plugin_logic_waysWrite_mask = 1'b0;
      end
    end
    if(when_LsuL1Plugin_l1219) begin
      LsuL1Plugin_logic_waysWrite_mask = 1'b1;
    end
  end

  always @(*) begin
    LsuL1Plugin_logic_waysWrite_address = 4'bxxxx;
    if(LsuL1Plugin_logic_bus_read_rsp_valid) begin
      if(when_LsuL1Plugin_l463) begin
        LsuL1Plugin_logic_waysWrite_address = LsuL1Plugin_logic_refill_read_rspAddress[9 : 6];
      end
    end
    if(LsuL1Plugin_logic_lsu_ctrl_doFlush) begin
      LsuL1Plugin_logic_waysWrite_address = execute_ctrl4_down_LsuL1_MIXED_ADDRESS_lane0[9 : 6];
    end
    if(when_LsuL1Plugin_l1219) begin
      LsuL1Plugin_logic_waysWrite_address = LsuL1Plugin_logic_initializer_counter[3:0];
    end
  end

  always @(*) begin
    LsuL1Plugin_logic_waysWrite_tag_loaded = 1'bx;
    if(LsuL1Plugin_logic_bus_read_rsp_valid) begin
      if(when_LsuL1Plugin_l463) begin
        LsuL1Plugin_logic_waysWrite_tag_loaded = 1'b1;
      end
    end
    if(LsuL1Plugin_logic_lsu_ctrl_doFlush) begin
      LsuL1Plugin_logic_waysWrite_tag_loaded = 1'b1;
    end
    if(when_LsuL1Plugin_l1219) begin
      LsuL1Plugin_logic_waysWrite_tag_loaded = 1'b0;
    end
  end

  always @(*) begin
    LsuL1Plugin_logic_waysWrite_tag_address = 22'bxxxxxxxxxxxxxxxxxxxxxx;
    if(LsuL1Plugin_logic_bus_read_rsp_valid) begin
      if(when_LsuL1Plugin_l463) begin
        LsuL1Plugin_logic_waysWrite_tag_address = LsuL1Plugin_logic_refill_read_rspAddress[31 : 10];
      end
    end
    if(LsuL1Plugin_logic_lsu_ctrl_doFlush) begin
      LsuL1Plugin_logic_waysWrite_tag_address = _zz_LsuL1Plugin_logic_waysWrite_tag_address;
    end
  end

  always @(*) begin
    LsuL1Plugin_logic_waysWrite_tag_fault = 1'bx;
    if(LsuL1Plugin_logic_bus_read_rsp_valid) begin
      if(when_LsuL1Plugin_l463) begin
        LsuL1Plugin_logic_waysWrite_tag_fault = LsuL1Plugin_logic_refill_read_faulty;
      end
    end
    if(LsuL1Plugin_logic_lsu_ctrl_doFlush) begin
      LsuL1Plugin_logic_waysWrite_tag_fault = execute_ctrl4_down_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_fault;
    end
  end

  assign LsuL1Plugin_logic_waysWrite_valid = (|LsuL1Plugin_logic_waysWrite_mask);
  assign LsuL1Plugin_logic_banks_0_write_valid = LsuL1Plugin_logic_banksWrite_mask[0];
  assign LsuL1Plugin_logic_banks_0_write_payload_address = LsuL1Plugin_logic_banksWrite_address;
  assign LsuL1Plugin_logic_banks_0_write_payload_data = LsuL1Plugin_logic_banksWrite_writeData;
  assign LsuL1Plugin_logic_banks_0_write_payload_mask = LsuL1Plugin_logic_banksWrite_writeMask;
  assign LsuL1Plugin_logic_banks_0_read_rsp = LsuL1Plugin_logic_banks_0_mem_spinal_port1;
  assign _zz_LsuL1Plugin_logic_ways_0_lsuRead_rsp_loaded = LsuL1Plugin_logic_ways_0_mem_spinal_port1;
  assign LsuL1Plugin_logic_ways_0_lsuRead_rsp_loaded = _zz_LsuL1Plugin_logic_ways_0_lsuRead_rsp_loaded[0];
  assign LsuL1Plugin_logic_ways_0_lsuRead_rsp_address = _zz_LsuL1Plugin_logic_ways_0_lsuRead_rsp_loaded[22 : 1];
  assign LsuL1Plugin_logic_ways_0_lsuRead_rsp_fault = _zz_LsuL1Plugin_logic_ways_0_lsuRead_rsp_loaded[23];
  assign LsuL1Plugin_logic_shared_lsuRead_rsp_dirty = LsuL1Plugin_logic_shared_mem_spinal_port1[0 : 0];
  always @(*) begin
    LsuL1Plugin_logic_refill_slots_0_loadedSet = 1'b0;
    if(LsuL1Plugin_logic_bus_read_rsp_valid) begin
      if(when_LsuL1Plugin_l463) begin
        LsuL1Plugin_logic_refill_slots_0_loadedSet = 1'b1;
      end
    end
  end

  assign LsuL1Plugin_logic_refill_slots_0_loadedDone = (LsuL1Plugin_logic_refill_slots_0_loadedCounter == 1'b1);
  assign LsuL1Plugin_logic_refill_slots_0_free = ((! LsuL1Plugin_logic_refill_slots_0_valid) && 1'b1);
  assign LsuL1Plugin_logic_refill_slots_0_fire = ((! execute_freeze_valid) && LsuL1Plugin_logic_refill_slots_0_loadedDone);
  assign LsuL1Plugin_logic_refill_free = LsuL1Plugin_logic_refill_slots_0_free;
  assign LsuL1Plugin_logic_refill_full = (&(! LsuL1Plugin_logic_refill_slots_0_free));
  assign when_LsuL1Plugin_l377 = (LsuL1Plugin_logic_refill_push_valid && LsuL1Plugin_logic_refill_free[0]);
  assign when_LsuL1Plugin_l381 = LsuL1Plugin_logic_refill_free[0];
  assign LsuL1Plugin_logic_refill_read_arbiter_slotsWithId_0_0 = ((LsuL1Plugin_logic_refill_slots_0_valid && (! LsuL1Plugin_logic_refill_slots_0_cmdSent)) && (LsuL1Plugin_logic_refill_slots_0_victim == 1'b0));
  assign LsuL1Plugin_logic_refill_read_arbiter_hits = LsuL1Plugin_logic_refill_read_arbiter_slotsWithId_0_0;
  assign LsuL1Plugin_logic_refill_read_arbiter_hit = (|LsuL1Plugin_logic_refill_read_arbiter_hits);
  always @(*) begin
    LsuL1Plugin_logic_refill_read_arbiter_oh = (LsuL1Plugin_logic_refill_read_arbiter_hits & 1'b1);
    if(when_LsuL1Plugin_l301) begin
      LsuL1Plugin_logic_refill_read_arbiter_oh = LsuL1Plugin_logic_refill_read_arbiter_lock;
    end
  end

  assign when_LsuL1Plugin_l301 = (|LsuL1Plugin_logic_refill_read_arbiter_lock);
  assign LsuL1Plugin_logic_bus_read_cmd_fire = (LsuL1Plugin_logic_bus_read_cmd_valid && LsuL1Plugin_logic_bus_read_cmd_ready);
  assign LsuL1Plugin_logic_refill_read_cmdAddress = {LsuL1Plugin_logic_refill_slots_0_address[31 : 6],6'h0};
  assign LsuL1Plugin_logic_bus_read_cmd_valid = LsuL1Plugin_logic_refill_read_arbiter_hit;
  assign LsuL1Plugin_logic_bus_read_cmd_payload_address = LsuL1Plugin_logic_refill_read_cmdAddress;
  assign LsuL1Plugin_logic_refill_read_rspAddress = LsuL1Plugin_logic_refill_slots_0_address;
  assign LsuL1Plugin_logic_refill_read_dirty = LsuL1Plugin_logic_refill_slots_0_dirty;
  assign LsuL1Plugin_logic_refill_read_rspWithData = 1'b1;
  always @(*) begin
    LsuL1Plugin_logic_refill_read_writeReservation_take = 1'b0;
    if(LsuL1Plugin_logic_bus_read_rsp_valid) begin
      LsuL1Plugin_logic_refill_read_writeReservation_take = 1'b1;
    end
  end

  assign LsuL1Plugin_logic_refill_read_bankWriteNotif[0] = ((LsuL1Plugin_logic_bus_read_rsp_valid && LsuL1Plugin_logic_refill_read_rspWithData) && 1'b1);
  always @(*) begin
    LsuL1Plugin_logic_banksWrite_mask[0] = LsuL1Plugin_logic_refill_read_bankWriteNotif[0];
    if(LsuL1Plugin_logic_lsu_ctrl_bankWriteReservation_win) begin
      if(when_LsuL1Plugin_l929) begin
        LsuL1Plugin_logic_banksWrite_mask[0] = (1'b1 && LsuL1Plugin_logic_lsu_ctrl_doWrite);
      end
    end
  end

  assign when_LsuL1Plugin_l450 = (LsuL1Plugin_logic_bus_read_rsp_valid && LsuL1Plugin_logic_bus_read_rsp_payload_error);
  always @(*) begin
    LsuL1Plugin_logic_refill_read_fire = 1'b0;
    if(LsuL1Plugin_logic_bus_read_rsp_valid) begin
      if(when_LsuL1Plugin_l463) begin
        LsuL1Plugin_logic_refill_read_fire = 1'b1;
      end
    end
  end

  always @(*) begin
    LsuL1Plugin_logic_refill_read_reservation_take = 1'b0;
    if(LsuL1Plugin_logic_bus_read_rsp_valid) begin
      if(when_LsuL1Plugin_l463) begin
        LsuL1Plugin_logic_refill_read_reservation_take = 1'b1;
      end
    end
  end

  assign LsuL1Plugin_logic_refill_read_faulty = (LsuL1Plugin_logic_refill_read_hadError || LsuL1Plugin_logic_bus_read_rsp_payload_error);
  always @(*) begin
    LsuL1Plugin_logic_refillCompletions = 1'b0;
    if(LsuL1Plugin_logic_bus_read_rsp_valid) begin
      if(when_LsuL1Plugin_l463) begin
        LsuL1Plugin_logic_refillCompletions[0] = 1'b1;
      end
    end
  end

  assign LsuL1Plugin_logic_bus_read_rsp_ready = 1'b1;
  assign when_LsuL1Plugin_l463 = ((LsuL1Plugin_logic_refill_read_wordIndex == 4'b1111) || (! LsuL1Plugin_logic_refill_read_rspWithData));
  assign LsuL1_REFILL_BUSY = ((! LsuL1Plugin_logic_refill_slots_0_loaded) && (! LsuL1Plugin_logic_refill_slots_0_loadedSet));
  always @(*) begin
    LsuL1Plugin_logic_writeback_slots_0_fire = 1'b0;
    if(LsuL1Plugin_logic_bus_write_rsp_valid) begin
      LsuL1Plugin_logic_writeback_slots_0_fire = 1'b1;
    end
  end

  assign LsuL1Plugin_logic_writeback_slots_0_timer_done = (LsuL1Plugin_logic_writeback_slots_0_timer_counter == 1'b1);
  assign when_LsuL1Plugin_l530 = (LsuL1Plugin_logic_writeback_slots_0_timer_done && (LsuL1Plugin_logic_writeback_slots_0_fire || (! LsuL1Plugin_logic_writeback_slots_0_busy)));
  assign LsuL1Plugin_logic_writeback_slots_0_free = (! LsuL1Plugin_logic_writeback_slots_0_valid);
  assign LsuL1_WRITEBACK_BUSY = (LsuL1Plugin_logic_writeback_slots_0_valid || LsuL1Plugin_logic_writeback_slots_0_fire);
  assign LsuL1Plugin_logic_writebackBusy = (|LsuL1Plugin_logic_writeback_slots_0_valid);
  assign LsuL1Plugin_logic_writeback_free = LsuL1Plugin_logic_writeback_slots_0_free;
  assign LsuL1Plugin_logic_writeback_full = (&(! LsuL1Plugin_logic_writeback_slots_0_free));
  always @(*) begin
    LsuL1Plugin_logic_writeback_push_valid = 1'b0;
    if(LsuL1Plugin_logic_lsu_ctrl_doFlush) begin
      LsuL1Plugin_logic_writeback_push_valid = 1'b1;
    end
    if(LsuL1Plugin_logic_lsu_ctrl_doRefill) begin
      LsuL1Plugin_logic_writeback_push_valid = LsuL1Plugin_logic_lsu_ctrl_refillWayNeedWriteback;
    end
    if(LsuL1Plugin_logic_lsu_ctrl_preventSideEffects) begin
      LsuL1Plugin_logic_writeback_push_valid = 1'b0;
    end
  end

  always @(*) begin
    LsuL1Plugin_logic_writeback_push_payload_address = 32'bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx;
    if(LsuL1Plugin_logic_lsu_ctrl_doFlush) begin
      LsuL1Plugin_logic_writeback_push_payload_address = ({6'd0,{_zz_LsuL1Plugin_logic_waysWrite_tag_address,execute_ctrl4_down_LsuL1_MIXED_ADDRESS_lane0[9 : 6]}} <<< 3'd6);
    end
    if(LsuL1Plugin_logic_lsu_ctrl_doRefill) begin
      LsuL1Plugin_logic_writeback_push_payload_address = ({6'd0,{execute_ctrl4_down_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_address,execute_ctrl4_down_LsuL1_MIXED_ADDRESS_lane0[9 : 6]}} <<< 3'd6);
    end
  end

  assign when_LsuL1Plugin_l556 = (LsuL1Plugin_logic_writeback_free[0] && LsuL1Plugin_logic_writeback_push_valid);
  assign when_LsuL1Plugin_l561 = LsuL1Plugin_logic_writeback_free[0];
  assign LsuL1Plugin_logic_writeback_read_arbiter_slotsWithId_0_0 = (LsuL1Plugin_logic_writeback_slots_0_valid && (! LsuL1Plugin_logic_writeback_slots_0_readCmdDone));
  assign LsuL1Plugin_logic_writeback_read_arbiter_hits = LsuL1Plugin_logic_writeback_read_arbiter_slotsWithId_0_0;
  assign LsuL1Plugin_logic_writeback_read_arbiter_hit = (|LsuL1Plugin_logic_writeback_read_arbiter_hits);
  always @(*) begin
    LsuL1Plugin_logic_writeback_read_arbiter_oh = (LsuL1Plugin_logic_writeback_read_arbiter_hits & 1'b1);
    if(when_LsuL1Plugin_l301_1) begin
      LsuL1Plugin_logic_writeback_read_arbiter_oh = LsuL1Plugin_logic_writeback_read_arbiter_lock;
    end
  end

  assign when_LsuL1Plugin_l301_1 = (|LsuL1Plugin_logic_writeback_read_arbiter_lock);
  assign LsuL1Plugin_logic_writeback_read_address = LsuL1Plugin_logic_writeback_slots_0_address;
  assign LsuL1Plugin_logic_writeback_read_slotRead_valid = LsuL1Plugin_logic_writeback_read_arbiter_hit;
  assign LsuL1Plugin_logic_writeback_read_slotRead_payload_wordIndex = LsuL1Plugin_logic_writeback_read_wordIndex;
  assign LsuL1Plugin_logic_writeback_read_slotRead_payload_last = (LsuL1Plugin_logic_writeback_read_wordIndex == 4'b1111);
  assign when_LsuL1Plugin_l605 = (LsuL1Plugin_logic_writeback_read_slotRead_valid && LsuL1Plugin_logic_writeback_read_slotRead_payload_last);
  always @(*) begin
    LsuL1Plugin_logic_banks_0_read_cmd_valid = LsuL1Plugin_logic_banks_0_usedByWriteback;
    if(when_LsuL1Plugin_l718) begin
      LsuL1Plugin_logic_banks_0_read_cmd_valid = 1'b1;
    end
  end

  assign LsuL1Plugin_logic_banks_0_usedByWriteback = (LsuL1Plugin_logic_writeback_read_slotRead_valid && 1'b1);
  always @(*) begin
    LsuL1Plugin_logic_banks_0_read_cmd_payload = {LsuL1Plugin_logic_writeback_read_address[9 : 6],LsuL1Plugin_logic_writeback_read_wordIndex};
    if(when_LsuL1Plugin_l719) begin
      LsuL1Plugin_logic_banks_0_read_cmd_payload = LsuL1Plugin_logic_lsu_rb0_readAddress;
    end
  end

  assign LsuL1Plugin_logic_writeback_read_readedData = LsuL1Plugin_logic_banks_0_read_rsp;
  assign LsuL1Plugin_logic_writeback_write_arbiter_slotsWithId_0_0 = ((LsuL1Plugin_logic_writeback_slots_0_valid && LsuL1Plugin_logic_writeback_slots_0_victimBufferReady) && (! LsuL1Plugin_logic_writeback_slots_0_writeCmdDone));
  assign LsuL1Plugin_logic_writeback_write_arbiter_hits = LsuL1Plugin_logic_writeback_write_arbiter_slotsWithId_0_0;
  assign LsuL1Plugin_logic_writeback_write_arbiter_hit = (|LsuL1Plugin_logic_writeback_write_arbiter_hits);
  always @(*) begin
    LsuL1Plugin_logic_writeback_write_arbiter_oh = (LsuL1Plugin_logic_writeback_write_arbiter_hits & 1'b1);
    if(when_LsuL1Plugin_l301_2) begin
      LsuL1Plugin_logic_writeback_write_arbiter_oh = LsuL1Plugin_logic_writeback_write_arbiter_lock;
    end
  end

  assign when_LsuL1Plugin_l301_2 = (|LsuL1Plugin_logic_writeback_write_arbiter_lock);
  assign LsuL1Plugin_logic_writeback_write_last = (LsuL1Plugin_logic_writeback_write_wordIndex == 4'b1111);
  assign LsuL1Plugin_logic_writeback_write_bufferRead_valid = LsuL1Plugin_logic_writeback_write_arbiter_hit;
  assign LsuL1Plugin_logic_writeback_write_bufferRead_payload_last = LsuL1Plugin_logic_writeback_write_last;
  assign LsuL1Plugin_logic_writeback_write_bufferRead_payload_address = LsuL1Plugin_logic_writeback_slots_0_address;
  assign LsuL1Plugin_logic_writeback_write_bufferRead_fire = (LsuL1Plugin_logic_writeback_write_bufferRead_valid && LsuL1Plugin_logic_writeback_write_bufferRead_ready);
  assign when_LsuL1Plugin_l676 = (LsuL1Plugin_logic_writeback_write_bufferRead_fire && LsuL1Plugin_logic_writeback_write_last);
  always @(*) begin
    LsuL1Plugin_logic_writeback_write_bufferRead_ready = LsuL1Plugin_logic_writeback_write_cmd_ready;
    if(when_Stream_l399) begin
      LsuL1Plugin_logic_writeback_write_bufferRead_ready = 1'b1;
    end
  end

  assign when_Stream_l399 = (! LsuL1Plugin_logic_writeback_write_cmd_valid);
  assign LsuL1Plugin_logic_writeback_write_cmd_valid = LsuL1Plugin_logic_writeback_write_bufferRead_rValid;
  assign LsuL1Plugin_logic_writeback_write_cmd_payload_address = LsuL1Plugin_logic_writeback_write_bufferRead_rData_address;
  assign LsuL1Plugin_logic_writeback_write_cmd_payload_last = LsuL1Plugin_logic_writeback_write_bufferRead_rData_last;
  assign _zz_LsuL1Plugin_logic_writeback_write_word = LsuL1Plugin_logic_writeback_write_wordIndex;
  assign LsuL1Plugin_logic_writeback_write_word = LsuL1Plugin_logic_writeback_victimBuffer_spinal_port1;
  assign LsuL1Plugin_logic_bus_write_cmd_valid = LsuL1Plugin_logic_writeback_write_cmd_valid;
  assign LsuL1Plugin_logic_writeback_write_cmd_ready = LsuL1Plugin_logic_bus_write_cmd_ready;
  assign LsuL1Plugin_logic_bus_write_cmd_payload_fragment_address = LsuL1Plugin_logic_writeback_write_cmd_payload_address;
  assign LsuL1Plugin_logic_bus_write_cmd_payload_fragment_data = LsuL1Plugin_logic_writeback_write_word;
  assign LsuL1Plugin_logic_bus_write_cmd_payload_last = LsuL1Plugin_logic_writeback_write_cmd_payload_last;
  assign LsuL1Plugin_logic_lsu_rb0_readAddress = execute_ctrl2_down_LsuL1_MIXED_ADDRESS_lane0[9 : 2];
  assign execute_ctrl2_down_LsuL1Plugin_logic_BANK_BUSY_lane0[0] = LsuL1Plugin_logic_banks_0_usedByWriteback;
  assign when_LsuL1Plugin_l718 = (! execute_freeze_valid);
  assign when_LsuL1Plugin_l719 = (! LsuL1Plugin_logic_banks_0_usedByWriteback);
  assign when_LsuL1Plugin_l735 = (! execute_freeze_valid);
  assign execute_ctrl3_down_LsuL1Plugin_logic_BANKS_WORDS_lane0_0 = LsuL1Plugin_logic_banks_0_read_rsp;
  assign execute_ctrl3_down_LsuL1Plugin_logic_BANK_BUSY_REMAPPED_lane0[0] = (execute_ctrl3_down_LsuL1Plugin_logic_BANK_BUSY_lane0[0] || LsuL1Plugin_logic_lsu_rb1_onBanks_0_busyReg);
  assign execute_ctrl3_down_LsuL1Plugin_logic_BANKS_MUXES_lane0_0 = execute_ctrl3_down_LsuL1Plugin_logic_BANKS_WORDS_lane0_0[31 : 0];
  assign _zz_execute_ctrl4_down_LsuL1Plugin_logic_MUXED_DATA_lane0 = execute_ctrl4_down_LsuL1Plugin_logic_WAYS_HITS_lane0[0];
  assign execute_ctrl4_down_LsuL1Plugin_logic_MUXED_DATA_lane0 = (_zz_execute_ctrl4_down_LsuL1Plugin_logic_MUXED_DATA_lane0 ? execute_ctrl4_down_LsuL1Plugin_logic_BANKS_MUXES_lane0_0 : 32'h0);
  always @(*) begin
    execute_ctrl3_down_LsuL1Plugin_logic_WRITE_TO_READ_HAZARDS_lane0[0] = ((execute_ctrl2_down_LsuL1Plugin_logic_EVENT_WRITE_VALID_lane0 && (execute_ctrl2_down_LsuL1Plugin_logic_EVENT_WRITE_ADDRESS_lane0[31 : 2] == execute_ctrl3_down_LsuL1_PHYSICAL_ADDRESS_lane0[31 : 2])) && (|(execute_ctrl2_down_LsuL1Plugin_logic_EVENT_WRITE_MASK_lane0 & execute_ctrl3_down_LsuL1_MASK_lane0)));
    execute_ctrl3_down_LsuL1Plugin_logic_WRITE_TO_READ_HAZARDS_lane0[1] = ((execute_ctrl3_down_LsuL1Plugin_logic_EVENT_WRITE_VALID_lane0 && (execute_ctrl3_down_LsuL1Plugin_logic_EVENT_WRITE_ADDRESS_lane0[31 : 2] == execute_ctrl3_down_LsuL1_PHYSICAL_ADDRESS_lane0[31 : 2])) && (|(execute_ctrl3_down_LsuL1Plugin_logic_EVENT_WRITE_MASK_lane0 & execute_ctrl3_down_LsuL1_MASK_lane0)));
  end

  assign LsuL1Plugin_logic_shared_lsuRead_cmd_valid = (! execute_freeze_valid);
  assign LsuL1Plugin_logic_shared_lsuRead_cmd_payload = execute_ctrl2_down_LsuL1_MIXED_ADDRESS_lane0[9 : 6];
  assign execute_ctrl2_down_LsuL1Plugin_logic_lsu_rt0_SHARED_BYPASS_VALID_lane0 = (LsuL1Plugin_logic_shared_write_valid && (LsuL1Plugin_logic_shared_write_payload_address == execute_ctrl2_down_LsuL1_MIXED_ADDRESS_lane0[9 : 6]));
  assign execute_ctrl2_down_LsuL1Plugin_logic_lsu_rt0_SHARED_BYPASS_VALUE_lane0_dirty = LsuL1Plugin_logic_shared_write_payload_data_dirty;
  assign LsuL1Plugin_logic_ways_0_lsuRead_cmd_valid = (! execute_freeze_valid);
  assign LsuL1Plugin_logic_ways_0_lsuRead_cmd_payload = execute_ctrl2_down_LsuL1_MIXED_ADDRESS_lane0[9 : 6];
  always @(*) begin
    execute_ctrl3_up_LsuL1Plugin_logic_SHARED_lane0_dirty = LsuL1Plugin_logic_shared_lsuRead_rsp_dirty;
    if(execute_ctrl3_down_LsuL1Plugin_logic_lsu_rt0_SHARED_BYPASS_VALID_lane0) begin
      execute_ctrl3_up_LsuL1Plugin_logic_SHARED_lane0_dirty = execute_ctrl3_down_LsuL1Plugin_logic_lsu_rt0_SHARED_BYPASS_VALUE_lane0_dirty;
    end
  end

  assign execute_ctrl3_down_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_loaded = LsuL1Plugin_logic_ways_0_lsuRead_rsp_loaded;
  assign execute_ctrl3_down_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_address = LsuL1Plugin_logic_ways_0_lsuRead_rsp_address;
  assign execute_ctrl3_down_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_fault = LsuL1Plugin_logic_ways_0_lsuRead_rsp_fault;
  assign LsuL1Plugin_logic_lsu_sharedBypassers_0_hit = (LsuL1Plugin_logic_shared_write_valid && (LsuL1Plugin_logic_shared_write_payload_address == execute_ctrl3_down_LsuL1_MIXED_ADDRESS_lane0[9 : 6]));
  assign execute_ctrl3_LsuL1Plugin_logic_SHARED_lane0_bypass_dirty = (LsuL1Plugin_logic_lsu_sharedBypassers_0_hit ? LsuL1Plugin_logic_shared_write_payload_data_dirty : execute_ctrl3_up_LsuL1Plugin_logic_SHARED_lane0_dirty);
  assign execute_ctrl3_down_LsuL1Plugin_logic_WAYS_HITS_lane0[0] = (execute_ctrl3_down_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_loaded && (execute_ctrl3_down_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_address == execute_ctrl3_down_LsuL1_PHYSICAL_ADDRESS_lane0[31 : 10]));
  assign execute_ctrl4_down_LsuL1Plugin_logic_WAYS_HIT_lane0 = (|execute_ctrl4_down_LsuL1Plugin_logic_WAYS_HITS_lane0);
  assign execute_ctrl4_down_LsuL1Plugin_logic_NEED_UNIQUE_lane0 = (execute_ctrl4_down_LsuL1_STORE_lane0 || execute_ctrl4_down_LsuL1_ATOMIC_lane0);
  always @(*) begin
    LsuL1Plugin_logic_lsu_ctrl_wayWriteReservation_take = 1'b0;
    if(LsuL1Plugin_logic_lsu_ctrl_doFlush) begin
      LsuL1Plugin_logic_lsu_ctrl_wayWriteReservation_take = 1'b1;
    end
  end

  assign LsuL1Plugin_logic_lsu_ctrl_bankWriteReservation_take = 1'b0;
  assign LsuL1Plugin_logic_lsu_ctrl_refillWayNeedWriteback = _zz_LsuL1Plugin_logic_lsu_ctrl_refillWayNeedWriteback[0];
  assign LsuL1Plugin_logic_lsu_ctrl_refillHazards = (LsuL1Plugin_logic_refill_slots_0_valid && (LsuL1Plugin_logic_refill_slots_0_address[9 : 6] == execute_ctrl4_down_LsuL1_PHYSICAL_ADDRESS_lane0[9 : 6]));
  assign LsuL1Plugin_logic_lsu_ctrl_writebackHazards = (LsuL1Plugin_logic_writeback_slots_0_valid && (LsuL1Plugin_logic_writeback_slots_0_address[9 : 6] == execute_ctrl4_down_LsuL1_PHYSICAL_ADDRESS_lane0[9 : 6]));
  assign LsuL1Plugin_logic_lsu_ctrl_refillHazard = (|LsuL1Plugin_logic_lsu_ctrl_refillHazards);
  assign LsuL1Plugin_logic_lsu_ctrl_writebackHazard = (|LsuL1Plugin_logic_lsu_ctrl_writebackHazards);
  assign LsuL1Plugin_logic_lsu_ctrl_wasDirty = (|(execute_ctrl4_down_LsuL1Plugin_logic_SHARED_lane0_dirty & execute_ctrl4_down_LsuL1Plugin_logic_WAYS_HITS_lane0));
  assign LsuL1Plugin_logic_lsu_ctrl_loadedDirties = (execute_ctrl4_down_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_loaded & execute_ctrl4_down_LsuL1Plugin_logic_SHARED_lane0_dirty);
  assign LsuL1Plugin_logic_lsu_ctrl_refillWayWasDirty = LsuL1Plugin_logic_lsu_ctrl_loadedDirties[0];
  assign LsuL1Plugin_logic_lsu_ctrl_writeToReadHazard = (|execute_ctrl4_down_LsuL1Plugin_logic_WRITE_TO_READ_HAZARDS_lane0);
  assign LsuL1Plugin_logic_lsu_ctrl_bankNotRead = (|(execute_ctrl4_down_LsuL1Plugin_logic_BANK_BUSY_REMAPPED_lane0 & execute_ctrl4_down_LsuL1Plugin_logic_WAYS_HITS_lane0));
  assign LsuL1Plugin_logic_lsu_ctrl_loadHazard = ((execute_ctrl4_down_LsuL1_LOAD_lane0 && (! execute_ctrl4_down_LsuL1_PREFETCH_lane0)) && (LsuL1Plugin_logic_lsu_ctrl_bankNotRead || LsuL1Plugin_logic_lsu_ctrl_writeToReadHazard));
  assign LsuL1Plugin_logic_lsu_ctrl_storeHazard = ((execute_ctrl4_down_LsuL1_STORE_lane0 && (! execute_ctrl4_down_LsuL1_PREFETCH_lane0)) && (! LsuL1Plugin_logic_lsu_ctrl_bankWriteReservation_win));
  assign LsuL1Plugin_logic_lsu_ctrl_preventSideEffects = (execute_ctrl4_down_LsuL1_ABORD_lane0 || execute_freeze_valid);
  assign LsuL1Plugin_logic_lsu_ctrl_flushHazard = (execute_ctrl4_down_LsuL1_FLUSH_lane0 && (! LsuL1Plugin_logic_lsu_ctrl_wayWriteReservation_win));
  assign LsuL1Plugin_logic_lsu_ctrl_coherencyHazard = 1'b0;
  assign execute_ctrl4_down_LsuL1Plugin_logic_HAZARD_FORCED_lane0 = 1'b0;
  assign execute_ctrl4_down_LsuL1_HAZARD_lane0 = (((((LsuL1Plugin_logic_lsu_ctrl_hazardReg || LsuL1Plugin_logic_lsu_ctrl_loadHazard) || LsuL1Plugin_logic_lsu_ctrl_refillHazard) || LsuL1Plugin_logic_lsu_ctrl_storeHazard) || LsuL1Plugin_logic_lsu_ctrl_coherencyHazard) || execute_ctrl4_down_LsuL1Plugin_logic_HAZARD_FORCED_lane0);
  assign execute_ctrl4_down_LsuL1_FLUSH_HAZARD_lane0 = (LsuL1Plugin_logic_lsu_ctrl_flushHazardReg || LsuL1Plugin_logic_lsu_ctrl_flushHazard);
  assign execute_ctrl4_down_LsuL1_MISS_lane0 = (! execute_ctrl4_down_LsuL1Plugin_logic_WAYS_HIT_lane0);
  assign execute_ctrl4_down_LsuL1_FAULT_lane0 = ((execute_ctrl4_down_LsuL1Plugin_logic_WAYS_HIT_lane0 && (|(execute_ctrl4_down_LsuL1Plugin_logic_WAYS_HITS_lane0 & execute_ctrl4_down_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_fault))) && (! execute_ctrl4_down_LsuL1_FLUSH_lane0));
  assign execute_ctrl4_down_LsuL1_MISS_UNIQUE_lane0 = ((execute_ctrl4_down_LsuL1Plugin_logic_WAYS_HIT_lane0 && execute_ctrl4_down_LsuL1Plugin_logic_NEED_UNIQUE_lane0) && 1'b0);
  assign execute_ctrl4_down_LsuL1_REFILL_HIT_lane0 = LsuL1Plugin_logic_lsu_ctrl_refillHazard;
  assign LsuL1Plugin_logic_lsu_ctrl_canRefill = (((! (LsuL1Plugin_logic_lsu_ctrl_refillWayNeedWriteback && LsuL1Plugin_logic_writeback_full)) && (! LsuL1Plugin_logic_refill_full)) && (! LsuL1Plugin_logic_lsu_ctrl_writebackHazard));
  assign LsuL1Plugin_logic_lsu_ctrl_canFlush = (((LsuL1Plugin_logic_lsu_ctrl_wayWriteReservation_win && (! LsuL1Plugin_logic_writeback_full)) && (! (|LsuL1Plugin_logic_refill_slots_0_valid))) && (! LsuL1Plugin_logic_lsu_ctrl_writebackHazard));
  assign LsuL1Plugin_logic_lsu_ctrl_needFlushs = LsuL1Plugin_logic_lsu_ctrl_loadedDirties;
  assign LsuL1Plugin_logic_lsu_ctrl_needFlushs_bools_0 = LsuL1Plugin_logic_lsu_ctrl_needFlushs[0];
  assign _zz_LsuL1Plugin_logic_lsu_ctrl_needFlushOh[0] = (LsuL1Plugin_logic_lsu_ctrl_needFlushs_bools_0 && (! 1'b0));
  assign LsuL1Plugin_logic_lsu_ctrl_needFlushOh = _zz_LsuL1Plugin_logic_lsu_ctrl_needFlushOh;
  assign LsuL1Plugin_logic_lsu_ctrl_isAccess = (((! execute_ctrl4_down_LsuL1_FLUSH_lane0) && (! execute_ctrl4_down_LsuL1_CLEAN_lane0)) && (! execute_ctrl4_down_LsuL1_INVALID_lane0));
  assign LsuL1Plugin_logic_lsu_ctrl_askRefill = ((LsuL1Plugin_logic_lsu_ctrl_isAccess && execute_ctrl4_down_LsuL1_MISS_lane0) && LsuL1Plugin_logic_lsu_ctrl_canRefill);
  assign LsuL1Plugin_logic_lsu_ctrl_askUpgrade = ((LsuL1Plugin_logic_lsu_ctrl_isAccess && execute_ctrl4_down_LsuL1_MISS_UNIQUE_lane0) && LsuL1Plugin_logic_lsu_ctrl_canRefill);
  assign LsuL1Plugin_logic_lsu_ctrl_askFlush = ((execute_ctrl4_down_LsuL1_FLUSH_lane0 && LsuL1Plugin_logic_lsu_ctrl_canFlush) && (|LsuL1Plugin_logic_lsu_ctrl_needFlushs));
  assign LsuL1Plugin_logic_lsu_ctrl_askCbm = (execute_ctrl4_down_LsuL1Plugin_logic_WAYS_HIT_lane0 && (execute_ctrl4_down_LsuL1_INVALID_lane0 || (execute_ctrl4_down_LsuL1_CLEAN_lane0 && LsuL1Plugin_logic_lsu_ctrl_wasDirty)));
  assign LsuL1Plugin_logic_lsu_ctrl_doRefill = (execute_ctrl4_down_LsuL1_SEL_lane0 && LsuL1Plugin_logic_lsu_ctrl_askRefill);
  assign LsuL1Plugin_logic_lsu_ctrl_doUpgrade = (execute_ctrl4_down_LsuL1_SEL_lane0 && LsuL1Plugin_logic_lsu_ctrl_askUpgrade);
  assign LsuL1Plugin_logic_lsu_ctrl_doFlush = (execute_ctrl4_down_LsuL1_SEL_lane0 && LsuL1Plugin_logic_lsu_ctrl_askFlush);
  assign LsuL1Plugin_logic_lsu_ctrl_doWrite = ((((execute_ctrl4_down_LsuL1_SEL_lane0 && execute_ctrl4_down_LsuL1_STORE_lane0) && execute_ctrl4_down_LsuL1Plugin_logic_WAYS_HIT_lane0) && _zz_LsuL1Plugin_logic_lsu_ctrl_doWrite[0]) && (! execute_ctrl4_down_LsuL1_SKIP_WRITE_lane0));
  assign LsuL1Plugin_logic_lsu_ctrl_doCbm = (((((execute_ctrl4_down_LsuL1_SEL_lane0 && LsuL1Plugin_logic_lsu_ctrl_askCbm) && LsuL1Plugin_logic_lsu_ctrl_wayWriteReservation_win) && (! LsuL1Plugin_logic_writeback_full)) && (! LsuL1Plugin_logic_lsu_ctrl_refillHazard)) && (! LsuL1Plugin_logic_lsu_ctrl_writebackHazard));
  assign LsuL1Plugin_logic_lsu_ctrl_doRefillPush = (LsuL1Plugin_logic_lsu_ctrl_doRefill || LsuL1Plugin_logic_lsu_ctrl_doUpgrade);
  always @(*) begin
    LsuL1Plugin_logic_refill_push_valid = LsuL1Plugin_logic_lsu_ctrl_doRefillPush;
    if(LsuL1Plugin_logic_lsu_ctrl_preventSideEffects) begin
      LsuL1Plugin_logic_refill_push_valid = 1'b0;
    end
  end

  assign LsuL1Plugin_logic_refill_push_payload_address = execute_ctrl4_down_LsuL1_PHYSICAL_ADDRESS_lane0;
  assign LsuL1Plugin_logic_refill_push_payload_unique = execute_ctrl4_down_LsuL1Plugin_logic_NEED_UNIQUE_lane0;
  assign LsuL1Plugin_logic_refill_push_payload_data = LsuL1Plugin_logic_lsu_ctrl_askRefill;
  always @(*) begin
    LsuL1Plugin_logic_refill_push_payload_victim = ((LsuL1Plugin_logic_lsu_ctrl_refillWayNeedWriteback && LsuL1Plugin_logic_lsu_ctrl_refillWayWasDirty) ? LsuL1Plugin_logic_writeback_free : 1'b0);
    if(LsuL1Plugin_logic_lsu_ctrl_askUpgrade) begin
      LsuL1Plugin_logic_refill_push_payload_victim = 1'b0;
    end
  end

  assign LsuL1Plugin_logic_refill_push_payload_dirty = execute_ctrl4_down_LsuL1_STORE_lane0;
  assign execute_ctrl4_down_LsuL1_WAIT_REFILL_lane0 = (LsuL1Plugin_logic_lsu_ctrl_refillHazards | (((! execute_ctrl4_down_LsuL1_HAZARD_lane0) && (LsuL1Plugin_logic_lsu_ctrl_askRefill || LsuL1Plugin_logic_lsu_ctrl_askUpgrade)) ? (LsuL1Plugin_logic_refill_full ? 1'b1 : LsuL1Plugin_logic_refill_free) : 1'b0));
  assign execute_ctrl4_down_LsuL1_WAIT_WRITEBACK_lane0 = 1'b0;
  assign when_LsuL1Plugin_l915 = (execute_ctrl4_down_LsuL1_SEL_lane0 && (! execute_ctrl4_down_LsuL1_ABORD_lane0));
  assign _zz_13 = {LsuL1Plugin_logic_lsu_ctrl_askRefill,{LsuL1Plugin_logic_lsu_ctrl_doUpgrade,LsuL1Plugin_logic_lsu_ctrl_doFlush}};
  always @(*) begin
    LsuL1Plugin_logic_shared_write_valid = 1'b0;
    if(LsuL1Plugin_logic_lsu_ctrl_doFlush) begin
      LsuL1Plugin_logic_shared_write_valid = 1'b1;
    end
    if(LsuL1Plugin_logic_lsu_ctrl_doRefill) begin
      LsuL1Plugin_logic_shared_write_valid = 1'b1;
    end
    if(when_LsuL1Plugin_l1019) begin
      LsuL1Plugin_logic_shared_write_valid = 1'b1;
    end
    if(LsuL1Plugin_logic_lsu_ctrl_preventSideEffects) begin
      LsuL1Plugin_logic_shared_write_valid = 1'b0;
    end
    if(when_LsuL1Plugin_l1219) begin
      LsuL1Plugin_logic_shared_write_valid = 1'b1;
    end
  end

  always @(*) begin
    LsuL1Plugin_logic_shared_write_payload_address = execute_ctrl4_down_LsuL1_MIXED_ADDRESS_lane0[9 : 6];
    if(when_LsuL1Plugin_l1219) begin
      LsuL1Plugin_logic_shared_write_payload_address = LsuL1Plugin_logic_initializer_counter[3:0];
    end
  end

  always @(*) begin
    LsuL1Plugin_logic_shared_write_payload_data_dirty = ((execute_ctrl4_down_LsuL1Plugin_logic_SHARED_lane0_dirty | (LsuL1Plugin_logic_lsu_ctrl_doWrite ? execute_ctrl4_down_LsuL1Plugin_logic_WAYS_HITS_lane0 : 1'b0)) & (~ ((LsuL1Plugin_logic_lsu_ctrl_doRefill ? 1'b1 : 1'b0) | (LsuL1Plugin_logic_lsu_ctrl_doFlush ? LsuL1Plugin_logic_lsu_ctrl_needFlushOh : 1'b0))));
    if(when_LsuL1Plugin_l1219) begin
      LsuL1Plugin_logic_shared_write_payload_data_dirty = _zz_LsuL1Plugin_logic_shared_write_payload_data_dirty[0 : 0];
    end
  end

  assign when_LsuL1Plugin_l929 = execute_ctrl4_down_LsuL1Plugin_logic_WAYS_HITS_lane0[0];
  assign execute_ctrl4_down_LsuL1_FLUSH_HIT_lane0 = (|LsuL1Plugin_logic_lsu_ctrl_needFlushs);
  assign _zz_LsuL1Plugin_logic_waysWrite_tag_address = execute_ctrl4_down_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_address;
  assign execute_ctrl2_down_LsuL1Plugin_logic_EVENT_WRITE_VALID_lane0 = LsuL1Plugin_logic_lsu_ctrl_doWrite;
  assign execute_ctrl2_down_LsuL1Plugin_logic_EVENT_WRITE_ADDRESS_lane0 = execute_ctrl4_down_LsuL1_PHYSICAL_ADDRESS_lane0;
  assign execute_ctrl2_down_LsuL1Plugin_logic_EVENT_WRITE_DATA_lane0 = execute_ctrl4_down_LsuL1_WRITE_DATA_lane0;
  assign execute_ctrl2_down_LsuL1Plugin_logic_EVENT_WRITE_MASK_lane0 = execute_ctrl4_down_LsuL1_MASK_lane0;
  assign when_LsuL1Plugin_l1019 = ((execute_ctrl4_down_LsuL1_SEL_lane0 && (! execute_ctrl4_down_LsuL1_HAZARD_lane0)) && (! execute_ctrl4_down_LsuL1_MISS_lane0));
  assign execute_ctrl4_down_LsuL1Plugin_logic_BYPASSED_DATA_lane0 = execute_ctrl4_down_LsuL1Plugin_logic_MUXED_DATA_lane0;
  assign execute_ctrl4_down_LsuL1_READ_DATA_lane0 = execute_ctrl4_down_LsuL1Plugin_logic_BYPASSED_DATA_lane0;
  assign LsuL1Plugin_logic_initializer_done = LsuL1Plugin_logic_initializer_counter[4];
  assign when_LsuL1Plugin_l1219 = (! LsuL1Plugin_logic_initializer_done);
  assign LsuL1Plugin_logic_refill_read_reservation_win = (! 1'b0);
  assign LsuL1Plugin_logic_lsu_ctrl_wayWriteReservation_win = (! (|LsuL1Plugin_logic_refill_read_reservation_take));
  assign LsuL1Plugin_logic_refill_read_writeReservation_win = (! 1'b0);
  assign LsuL1Plugin_logic_lsu_ctrl_bankWriteReservation_win = (! (|LsuL1Plugin_logic_refill_read_writeReservation_take));
  assign execute_ctrl2_down_MUL_SRC1_lane0 = _zz_execute_ctrl2_down_MUL_SRC1_lane0;
  assign execute_ctrl2_down_MUL_SRC2_lane0 = _zz_execute_ctrl2_down_MUL_SRC2_lane0;
  assign execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_0_lane0 = (execute_ctrl2_down_MUL_SRC1_lane0[16 : 0] * execute_ctrl2_down_MUL_SRC2_lane0[16 : 0]);
  assign execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_1_lane0 = _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_1_lane0;
  assign execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_2_lane0 = _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_2_lane0;
  assign execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_3_lane0 = _zz_execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_3_lane0;
  always @(*) begin
    _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0 = 61'h0;
    _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0[33 : 0] = execute_ctrl3_down_early0_MulPlugin_logic_mul_VALUES_0_lane0[33 : 0];
    _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0[60 : 34] = execute_ctrl3_down_early0_MulPlugin_logic_mul_VALUES_3_lane0[26 : 0];
  end

  always @(*) begin
    _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0_1 = 61'h0;
    _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0_1[60 : 17] = execute_ctrl3_down_early0_MulPlugin_logic_mul_VALUES_1_lane0[43 : 0];
  end

  always @(*) begin
    _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0_2 = 61'h0;
    _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0_2[60 : 17] = execute_ctrl3_down_early0_MulPlugin_logic_mul_VALUES_2_lane0[43 : 0];
  end

  always @(*) begin
    _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0 = 3'b000;
    _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0[2 : 0] = execute_ctrl3_down_early0_MulPlugin_logic_mul_VALUES_3_lane0[29 : 27];
  end

  always @(*) begin
    _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0_1 = 3'b000;
    _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0_1[2 : 0] = execute_ctrl3_down_early0_MulPlugin_logic_mul_VALUES_1_lane0[46 : 44];
  end

  always @(*) begin
    _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0_2 = 3'b000;
    _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0_2[2 : 0] = execute_ctrl3_down_early0_MulPlugin_logic_mul_VALUES_2_lane0[46 : 44];
  end

  assign execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0 = (_zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0_3 + _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0_6);
  assign execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0 = (_zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0_3 + _zz_execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0_6);
  always @(*) begin
    _zz_execute_ctrl4_down_early0_MulPlugin_logic_steps_1_adders_0_lane0 = 66'h0;
    _zz_execute_ctrl4_down_early0_MulPlugin_logic_steps_1_adders_0_lane0[62 : 0] = execute_ctrl4_down_early0_MulPlugin_logic_steps_0_adders_0_lane0[62 : 0];
  end

  always @(*) begin
    _zz_execute_ctrl4_down_early0_MulPlugin_logic_steps_1_adders_0_lane0_1 = 66'h0;
    _zz_execute_ctrl4_down_early0_MulPlugin_logic_steps_1_adders_0_lane0_1[65 : 61] = execute_ctrl4_down_early0_MulPlugin_logic_steps_0_adders_1_lane0[4 : 0];
  end

  assign execute_ctrl4_down_early0_MulPlugin_logic_steps_1_adders_0_lane0 = (_zz_execute_ctrl4_down_early0_MulPlugin_logic_steps_1_adders_0_lane0 + _zz_execute_ctrl4_down_early0_MulPlugin_logic_steps_1_adders_0_lane0_1);
  assign early0_MulPlugin_logic_formatBus_valid = execute_ctrl4_down_early0_MulPlugin_SEL_lane0;
  assign early0_MulPlugin_logic_formatBus_payload = (execute_ctrl4_down_MulPlugin_HIGH_lane0 ? execute_ctrl4_down_early0_MulPlugin_logic_steps_1_adders_0_lane0[63 : 32] : execute_ctrl4_down_early0_MulPlugin_logic_steps_1_adders_0_lane0[31 : 0]);
  assign execute_ctrl2_down_RsUnsignedPlugin_RS1_FORMATED_lane0 = execute_ctrl2_up_integer_RS1_lane0;
  assign execute_ctrl2_down_RsUnsignedPlugin_RS2_FORMATED_lane0 = execute_ctrl2_up_integer_RS2_lane0;
  assign execute_ctrl2_down_RsUnsignedPlugin_RS1_REVERT_lane0 = (execute_ctrl2_down_RsUnsignedPlugin_RS1_SIGNED_lane0 && execute_ctrl2_down_RsUnsignedPlugin_RS1_FORMATED_lane0[31]);
  assign execute_ctrl2_down_RsUnsignedPlugin_RS2_REVERT_lane0 = (execute_ctrl2_down_RsUnsignedPlugin_RS2_SIGNED_lane0 && execute_ctrl2_down_RsUnsignedPlugin_RS2_FORMATED_lane0[31]);
  assign execute_ctrl2_down_RsUnsignedPlugin_RS1_UNSIGNED_lane0 = ((execute_ctrl2_down_RsUnsignedPlugin_RS1_REVERT_lane0 ? (~ execute_ctrl2_down_RsUnsignedPlugin_RS1_FORMATED_lane0) : execute_ctrl2_down_RsUnsignedPlugin_RS1_FORMATED_lane0) + _zz_execute_ctrl2_down_RsUnsignedPlugin_RS1_UNSIGNED_lane0);
  assign execute_ctrl2_down_RsUnsignedPlugin_RS2_UNSIGNED_lane0 = ((execute_ctrl2_down_RsUnsignedPlugin_RS2_REVERT_lane0 ? (~ execute_ctrl2_down_RsUnsignedPlugin_RS2_FORMATED_lane0) : execute_ctrl2_down_RsUnsignedPlugin_RS2_FORMATED_lane0) + _zz_execute_ctrl2_down_RsUnsignedPlugin_RS2_UNSIGNED_lane0);
  assign io_cmd_fire = (early0_DivPlugin_logic_processing_div_io_cmd_valid && early0_DivPlugin_logic_processing_div_io_cmd_ready);
  assign early0_DivPlugin_logic_processing_request = (execute_ctrl2_up_LANE_SEL_lane0 && execute_ctrl2_down_early0_DivPlugin_SEL_lane0);
  assign early0_DivPlugin_logic_processing_a = execute_ctrl2_down_RsUnsignedPlugin_RS1_UNSIGNED_lane0;
  assign early0_DivPlugin_logic_processing_b = execute_ctrl2_down_RsUnsignedPlugin_RS2_UNSIGNED_lane0;
  assign early0_DivPlugin_logic_processing_div_io_cmd_valid = (early0_DivPlugin_logic_processing_request && (! early0_DivPlugin_logic_processing_cmdSent));
  assign early0_DivPlugin_logic_processing_freeze = ((early0_DivPlugin_logic_processing_request && (! early0_DivPlugin_logic_processing_div_io_rsp_valid)) && (! early0_DivPlugin_logic_processing_unscheduleRequest));
  assign early0_DivPlugin_logic_processing_selected = (execute_ctrl2_down_DivPlugin_REM_lane0 ? early0_DivPlugin_logic_processing_div_io_rsp_payload_remain : early0_DivPlugin_logic_processing_div_io_rsp_payload_result);
  assign _zz_execute_ctrl2_down_DivPlugin_DIV_RESULT_lane0 = early0_DivPlugin_logic_processing_selected;
  assign execute_ctrl2_down_DivPlugin_DIV_RESULT_lane0 = _zz_execute_ctrl2_down_DivPlugin_DIV_RESULT_lane0_1;
  assign early0_DivPlugin_logic_formatBus_valid = execute_ctrl3_down_early0_DivPlugin_SEL_lane0;
  assign early0_DivPlugin_logic_formatBus_payload = execute_ctrl3_down_DivPlugin_DIV_RESULT_lane0;
  always @(*) begin
    PrivilegedPlugin_logic_harts_0_xretAwayFromMachine = 1'b0;
    case(TrapPlugin_logic_harts_0_trap_fsm_stateReg)
      TrapPlugin_logic_harts_0_trap_fsm_RUNNING : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1 : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY : begin
        if(when_TrapPlugin_l654) begin
          PrivilegedPlugin_logic_harts_0_xretAwayFromMachine = 1'b1;
        end
      end
      TrapPlugin_logic_harts_0_trap_fsm_JUMP : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH : begin
      end
      default : begin
      end
    endcase
  end

  always @(*) begin
    PrivilegedPlugin_logic_harts_0_int_pending = 1'b0;
    if(TrapPlugin_logic_harts_0_interrupt_pendingInterrupt) begin
      PrivilegedPlugin_logic_harts_0_int_pending = 1'b1;
    end
  end

  assign PrivilegedPlugin_logic_harts_0_withMachinePrivilege = (2'b11 <= PrivilegedPlugin_logic_harts_0_privilege);
  assign PrivilegedPlugin_logic_harts_0_withSupervisorPrivilege = (2'b01 <= PrivilegedPlugin_logic_harts_0_privilege);
  assign PrivilegedPlugin_logic_harts_0_hartRunning = 1'b1;
  assign PrivilegedPlugin_logic_harts_0_debugMode = (! PrivilegedPlugin_logic_harts_0_hartRunning);
  assign PrivilegedPlugin_logic_harts_0_m_status_mpp = 2'b11;
  assign PrivilegedPlugin_logic_harts_0_m_status_sd = 1'b0;
  assign PrivilegedPlugin_logic_harts_0_m_status_tw = 1'b0;
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_1 = (_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue && REG_CSR_768);
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_2 = (_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue && REG_CSR_834);
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_3 = (_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue && REG_CSR_836);
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_4 = (_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue && REG_CSR_772);
  assign _zz_when_TrapPlugin_l207 = (PrivilegedPlugin_logic_harts_0_m_ip_mtip && PrivilegedPlugin_logic_harts_0_m_ie_mtie);
  assign _zz_when_TrapPlugin_l207_1 = (PrivilegedPlugin_logic_harts_0_m_ip_msip && PrivilegedPlugin_logic_harts_0_m_ie_msie);
  assign _zz_when_TrapPlugin_l207_2 = (PrivilegedPlugin_logic_harts_0_m_ip_meip && PrivilegedPlugin_logic_harts_0_m_ie_meie);
  always @(*) begin
    case(execute_ctrl4_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0)
      IntAluPlugin_AluBitwiseCtrlEnum_AND_1 : begin
        late0_IntAluPlugin_logic_alu_bitwise = (execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0 & execute_ctrl4_down_late0_SrcPlugin_SRC2_lane0);
      end
      IntAluPlugin_AluBitwiseCtrlEnum_OR_1 : begin
        late0_IntAluPlugin_logic_alu_bitwise = (execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0 | execute_ctrl4_down_late0_SrcPlugin_SRC2_lane0);
      end
      IntAluPlugin_AluBitwiseCtrlEnum_XOR_1 : begin
        late0_IntAluPlugin_logic_alu_bitwise = (execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0 ^ execute_ctrl4_down_late0_SrcPlugin_SRC2_lane0);
      end
      default : begin
        late0_IntAluPlugin_logic_alu_bitwise = 32'h0;
      end
    endcase
  end

  assign late0_IntAluPlugin_logic_alu_result = (_zz_late0_IntAluPlugin_logic_alu_result | _zz_late0_IntAluPlugin_logic_alu_result_2);
  assign execute_ctrl4_down_late0_IntAluPlugin_ALU_RESULT_lane0 = late0_IntAluPlugin_logic_alu_result;
  assign late0_IntAluPlugin_logic_wb_valid = execute_ctrl4_down_late0_IntAluPlugin_SEL_lane0;
  assign late0_IntAluPlugin_logic_wb_payload = execute_ctrl4_down_late0_IntAluPlugin_ALU_RESULT_lane0;
  assign late0_BarrelShifterPlugin_logic_shift_amplitude = _zz_late0_BarrelShifterPlugin_logic_shift_amplitude;
  assign late0_BarrelShifterPlugin_logic_shift_reversed = (execute_ctrl4_down_BarrelShifterPlugin_LEFT_lane0 ? _zz_late0_BarrelShifterPlugin_logic_shift_reversed : execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0);
  assign late0_BarrelShifterPlugin_logic_shift_shifted = _zz_late0_BarrelShifterPlugin_logic_shift_shifted[31:0];
  assign late0_BarrelShifterPlugin_logic_shift_patched = (execute_ctrl4_down_BarrelShifterPlugin_LEFT_lane0 ? _zz_late0_BarrelShifterPlugin_logic_shift_patched : late0_BarrelShifterPlugin_logic_shift_shifted);
  assign execute_ctrl4_down_late0_BarrelShifterPlugin_SHIFT_RESULT_lane0 = late0_BarrelShifterPlugin_logic_shift_patched;
  assign late0_BarrelShifterPlugin_logic_wb_valid = execute_ctrl4_down_late0_BarrelShifterPlugin_SEL_lane0;
  assign late0_BarrelShifterPlugin_logic_wb_payload = execute_ctrl4_down_late0_BarrelShifterPlugin_SHIFT_RESULT_lane0;
  assign WhiteboxerPlugin_logic_fetch_fire = fetch_logic_ctrls_0_down_isFiring;
  assign BtbPlugin_logic_memDp_wp_valid = BtbPlugin_logic_memWrite_valid;
  assign BtbPlugin_logic_memDp_wp_payload_address = BtbPlugin_logic_memWrite_payload_address;
  assign BtbPlugin_logic_memDp_wp_payload_data_0_hash = BtbPlugin_logic_memWrite_payload_data_0_hash;
  assign BtbPlugin_logic_memDp_wp_payload_data_0_pcTarget = BtbPlugin_logic_memWrite_payload_data_0_pcTarget;
  assign BtbPlugin_logic_memDp_wp_payload_data_0_isBranch = BtbPlugin_logic_memWrite_payload_data_0_isBranch;
  assign BtbPlugin_logic_memDp_wp_payload_data_0_isPush = BtbPlugin_logic_memWrite_payload_data_0_isPush;
  assign BtbPlugin_logic_memDp_wp_payload_data_0_isPop = BtbPlugin_logic_memWrite_payload_data_0_isPop;
  assign BtbPlugin_logic_memDp_wp_payload_data_0_taken = BtbPlugin_logic_memWrite_payload_data_0_taken;
  assign BtbPlugin_logic_memDp_wp_payload_mask = BtbPlugin_logic_memWrite_payload_mask;
  assign _zz_BtbPlugin_logic_memDp_rp_rsp_0_hash = BtbPlugin_logic_mem_spinal_port1[49 : 0];
  assign BtbPlugin_logic_memDp_rp_rsp_0_hash = _zz_BtbPlugin_logic_memDp_rp_rsp_0_hash[15 : 0];
  assign BtbPlugin_logic_memDp_rp_rsp_0_pcTarget = _zz_BtbPlugin_logic_memDp_rp_rsp_0_hash[45 : 16];
  assign BtbPlugin_logic_memDp_rp_rsp_0_isBranch = _zz_BtbPlugin_logic_memDp_rp_rsp_0_hash[46];
  assign BtbPlugin_logic_memDp_rp_rsp_0_isPush = _zz_BtbPlugin_logic_memDp_rp_rsp_0_hash[47];
  assign BtbPlugin_logic_memDp_rp_rsp_0_isPop = _zz_BtbPlugin_logic_memDp_rp_rsp_0_hash[48];
  assign BtbPlugin_logic_memDp_rp_rsp_0_taken = _zz_BtbPlugin_logic_memDp_rp_rsp_0_hash[49];
  assign BtbPlugin_logic_memDp_rp_cmd_valid = BtbPlugin_logic_memRead_cmd_valid;
  assign BtbPlugin_logic_memDp_rp_cmd_payload = BtbPlugin_logic_memRead_cmd_payload;
  assign BtbPlugin_logic_memRead_rsp_0_hash = BtbPlugin_logic_memDp_rp_rsp_0_hash;
  assign BtbPlugin_logic_memRead_rsp_0_pcTarget = BtbPlugin_logic_memDp_rp_rsp_0_pcTarget;
  assign BtbPlugin_logic_memRead_rsp_0_isBranch = BtbPlugin_logic_memDp_rp_rsp_0_isBranch;
  assign BtbPlugin_logic_memRead_rsp_0_isPush = BtbPlugin_logic_memDp_rp_rsp_0_isPush;
  assign BtbPlugin_logic_memRead_rsp_0_isPop = BtbPlugin_logic_memDp_rp_rsp_0_isPop;
  assign BtbPlugin_logic_memRead_rsp_0_taken = BtbPlugin_logic_memDp_rp_rsp_0_taken;
  assign LsuL1Plugin_logic_bus_toWishbone_arbiter_readCmd_valid = LsuL1Plugin_logic_bus_read_cmd_valid;
  assign LsuL1Plugin_logic_bus_read_cmd_ready = LsuL1Plugin_logic_bus_toWishbone_arbiter_readCmd_ready;
  assign LsuL1Plugin_logic_bus_toWishbone_arbiter_readCmd_payload_last = 1'b1;
  assign LsuL1Plugin_logic_bus_toWishbone_arbiter_readCmd_payload_fragment_write = 1'b0;
  assign LsuL1Plugin_logic_bus_toWishbone_arbiter_readCmd_payload_fragment_address = LsuL1Plugin_logic_bus_read_cmd_payload_address;
  assign LsuL1Plugin_logic_bus_toWishbone_arbiter_writeCmd_valid = LsuL1Plugin_logic_bus_write_cmd_valid;
  assign LsuL1Plugin_logic_bus_write_cmd_ready = LsuL1Plugin_logic_bus_toWishbone_arbiter_writeCmd_ready;
  assign LsuL1Plugin_logic_bus_toWishbone_arbiter_writeCmd_payload_last = LsuL1Plugin_logic_bus_write_cmd_payload_last;
  assign LsuL1Plugin_logic_bus_toWishbone_arbiter_writeCmd_payload_fragment_write = 1'b1;
  assign LsuL1Plugin_logic_bus_toWishbone_arbiter_writeCmd_payload_fragment_address = LsuL1Plugin_logic_bus_write_cmd_payload_fragment_address;
  assign LsuL1Plugin_logic_bus_toWishbone_arbiter_readCmd_ready = LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_inputs_0_ready;
  assign LsuL1Plugin_logic_bus_toWishbone_arbiter_writeCmd_ready = LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_inputs_1_ready;
  assign LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_fire = (LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_valid && LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_ready);
  assign LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_output_ready = (LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_ready && (LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_payload_last == LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_output_payload_last));
  assign LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_valid = LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_output_valid;
  assign LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_payload_fragment_write = LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_output_payload_fragment_write;
  always @(*) begin
    LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_payload_fragment_address = LsuL1Plugin_logic_bus_toWishbone_arbiter_arbiter_io_output_payload_fragment_address;
    LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_payload_fragment_address[5 : 2] = LsuL1Plugin_logic_bus_toWishbone_arbiter_counter;
  end

  assign LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_payload_fragment_data = LsuL1Plugin_logic_bus_write_cmd_payload_fragment_data;
  assign LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_payload_last = (&LsuL1Plugin_logic_bus_toWishbone_arbiter_counter);
  always @(*) begin
    LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_ready = LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_ready;
    if(when_Stream_l399_1) begin
      LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_ready = 1'b1;
    end
  end

  assign when_Stream_l399_1 = (! LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_valid);
  assign LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_valid = LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_rValid;
  assign LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_payload_last = LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_rData_last;
  assign LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_payload_fragment_write = LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_rData_fragment_write;
  assign LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_payload_fragment_address = LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_rData_fragment_address;
  assign LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_payload_fragment_data = LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_rData_fragment_data;
  assign LsuL1WishbonePlugin_logic_bus_ADR = (LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_payload_fragment_address >>> 2'd2);
  assign LsuL1WishbonePlugin_logic_bus_CTI = (LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_payload_last ? 3'b111 : 3'b010);
  assign LsuL1WishbonePlugin_logic_bus_BTE = 2'b00;
  assign LsuL1WishbonePlugin_logic_bus_SEL = 4'b1111;
  assign LsuL1WishbonePlugin_logic_bus_WE = LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_payload_fragment_write;
  assign LsuL1WishbonePlugin_logic_bus_DAT_MOSI = LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_payload_fragment_data;
  assign LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_ready = (LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_valid && (LsuL1WishbonePlugin_logic_bus_ACK || LsuL1WishbonePlugin_logic_bus_ERR));
  assign LsuL1WishbonePlugin_logic_bus_CYC = LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_valid;
  assign LsuL1WishbonePlugin_logic_bus_STB = LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_valid;
  assign LsuL1Plugin_logic_bus_read_rsp_valid = ((LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_valid && (! LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_payload_fragment_write)) && (LsuL1WishbonePlugin_logic_bus_ACK || LsuL1WishbonePlugin_logic_bus_ERR));
  assign LsuL1Plugin_logic_bus_read_rsp_payload_error = LsuL1WishbonePlugin_logic_bus_ERR;
  assign LsuL1Plugin_logic_bus_read_rsp_payload_data = LsuL1WishbonePlugin_logic_bus_DAT_MISO;
  assign LsuL1Plugin_logic_bus_write_rsp_valid = (((LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_valid && LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_payload_fragment_write) && LsuL1Plugin_logic_bus_toWishbone_arbiter_buffered_payload_last) && (LsuL1WishbonePlugin_logic_bus_ACK || LsuL1WishbonePlugin_logic_bus_ERR));
  assign LsuL1Plugin_logic_bus_write_rsp_payload_error = LsuL1WishbonePlugin_logic_bus_ERR;
  always @(*) begin
    CsrAccessPlugin_bus_decode_exception = 1'b0;
    if(when_PrivilegedPlugin_l689) begin
      CsrAccessPlugin_bus_decode_exception = 1'b1;
    end
  end

  always @(*) begin
    CsrAccessPlugin_bus_decode_trap = 1'b0;
    if(when_CsrAccessPlugin_l155) begin
      if(CsrAccessPlugin_bus_decode_write) begin
        CsrAccessPlugin_bus_decode_trap = 1'b1;
      end
    end
  end

  always @(*) begin
    CsrAccessPlugin_bus_decode_trapCode = 4'bxxxx;
    if(when_CsrAccessPlugin_l155) begin
      if(CsrAccessPlugin_bus_decode_write) begin
        CsrAccessPlugin_bus_decode_trapCode = 4'b0101;
      end
    end
  end

  always @(*) begin
    CsrAccessPlugin_bus_read_halt = 1'b0;
    if(when_CsrRamPlugin_l85) begin
      CsrAccessPlugin_bus_read_halt = 1'b1;
    end
  end

  always @(*) begin
    CsrAccessPlugin_bus_write_halt = 1'b0;
    if(when_CsrRamPlugin_l96) begin
      CsrAccessPlugin_bus_write_halt = 1'b1;
    end
  end

  assign FetchL1Plugin_logic_banks_0_read_rsp = FetchL1Plugin_logic_banks_0_mem_spinal_port1;
  assign fetch_logic_ctrls_1_down_FetchL1Plugin_logic_BANKS_WORDS_0 = FetchL1Plugin_logic_banks_0_read_rsp;
  always @(*) begin
    FetchL1Plugin_logic_waysWrite_mask = 1'b0;
    if(when_FetchL1Plugin_l204) begin
      FetchL1Plugin_logic_waysWrite_mask = 1'b1;
    end
    if(FetchL1Plugin_logic_invalidate_done) begin
      if(when_FetchL1Plugin_l304) begin
        FetchL1Plugin_logic_waysWrite_mask[0] = 1'b1;
      end
    end
  end

  always @(*) begin
    FetchL1Plugin_logic_waysWrite_address = 4'bxxxx;
    if(when_FetchL1Plugin_l204) begin
      FetchL1Plugin_logic_waysWrite_address = FetchL1Plugin_logic_invalidate_counter[3:0];
    end
    if(FetchL1Plugin_logic_invalidate_done) begin
      FetchL1Plugin_logic_waysWrite_address = FetchL1Plugin_logic_refill_onRsp_address[9 : 6];
    end
  end

  always @(*) begin
    FetchL1Plugin_logic_waysWrite_tag_loaded = 1'bx;
    if(when_FetchL1Plugin_l204) begin
      FetchL1Plugin_logic_waysWrite_tag_loaded = 1'b0;
    end
    if(FetchL1Plugin_logic_invalidate_done) begin
      FetchL1Plugin_logic_waysWrite_tag_loaded = 1'b1;
    end
  end

  always @(*) begin
    FetchL1Plugin_logic_waysWrite_tag_error = 1'bx;
    if(FetchL1Plugin_logic_invalidate_done) begin
      FetchL1Plugin_logic_waysWrite_tag_error = (FetchL1Plugin_logic_bus_rsp_valid && FetchL1Plugin_logic_bus_rsp_payload_error);
    end
  end

  always @(*) begin
    FetchL1Plugin_logic_waysWrite_tag_address = 22'bxxxxxxxxxxxxxxxxxxxxxx;
    if(FetchL1Plugin_logic_invalidate_done) begin
      FetchL1Plugin_logic_waysWrite_tag_address = FetchL1Plugin_logic_refill_onRsp_address[31 : 10];
    end
  end

  assign _zz_FetchL1Plugin_logic_ways_0_read_rsp_loaded = FetchL1Plugin_logic_ways_0_mem_spinal_port1;
  assign FetchL1Plugin_logic_ways_0_read_rsp_loaded = _zz_FetchL1Plugin_logic_ways_0_read_rsp_loaded[0];
  assign FetchL1Plugin_logic_ways_0_read_rsp_error = _zz_FetchL1Plugin_logic_ways_0_read_rsp_loaded[1];
  assign FetchL1Plugin_logic_ways_0_read_rsp_address = _zz_FetchL1Plugin_logic_ways_0_read_rsp_loaded[23 : 2];
  assign fetch_logic_ctrls_1_down_FetchL1Plugin_logic_WAYS_TAGS_0_loaded = FetchL1Plugin_logic_ways_0_read_rsp_loaded;
  assign fetch_logic_ctrls_1_down_FetchL1Plugin_logic_WAYS_TAGS_0_error = FetchL1Plugin_logic_ways_0_read_rsp_error;
  assign fetch_logic_ctrls_1_down_FetchL1Plugin_logic_WAYS_TAGS_0_address = FetchL1Plugin_logic_ways_0_read_rsp_address;
  assign FetchL1Plugin_logic_invalidate_cmd_valid = (|TrapPlugin_logic_fetchL1Invalidate_0_cmd_valid);
  always @(*) begin
    FetchL1Plugin_logic_invalidate_canStart = 1'b1;
    if(when_FetchL1Plugin_l268) begin
      FetchL1Plugin_logic_invalidate_canStart = 1'b0;
    end
  end

  assign FetchL1Plugin_logic_invalidate_counterIncr = (FetchL1Plugin_logic_invalidate_counter + 5'h01);
  assign FetchL1Plugin_logic_invalidate_done = FetchL1Plugin_logic_invalidate_counter[4];
  assign FetchL1Plugin_logic_invalidate_last = FetchL1Plugin_logic_invalidate_counterIncr[4];
  assign when_FetchL1Plugin_l204 = (! FetchL1Plugin_logic_invalidate_done);
  assign when_FetchL1Plugin_l211 = ((FetchL1Plugin_logic_invalidate_done && FetchL1Plugin_logic_invalidate_cmd_valid) && FetchL1Plugin_logic_invalidate_canStart);
  always @(*) begin
    TrapPlugin_logic_fetchL1Invalidate_0_cmd_ready = 1'b0;
    if(when_FetchL1Plugin_l216) begin
      if(FetchL1Plugin_logic_invalidate_last) begin
        TrapPlugin_logic_fetchL1Invalidate_0_cmd_ready = 1'b1;
      end
    end
  end

  assign when_FetchL1Plugin_l216 = (! FetchL1Plugin_logic_invalidate_done);
  assign fetch_logic_ctrls_0_haltRequest_FetchL1Plugin_l217 = _zz_fetch_logic_ctrls_0_haltRequest_FetchL1Plugin_l217;
  assign FetchL1Plugin_logic_refill_slots_0_askCmd = (FetchL1Plugin_logic_refill_slots_0_valid && (! FetchL1Plugin_logic_refill_slots_0_cmdSent));
  assign FetchL1Plugin_logic_refill_hazard = (|(FetchL1Plugin_logic_refill_slots_0_valid && (FetchL1Plugin_logic_refill_slots_0_address[9 : 6] == FetchL1Plugin_logic_refill_start_address[9 : 6])));
  assign when_FetchL1Plugin_l255 = ((FetchL1Plugin_logic_refill_start_valid && FetchL1Plugin_logic_invalidate_done) && (! FetchL1Plugin_logic_refill_hazard));
  assign when_FetchL1Plugin_l268 = ((|FetchL1Plugin_logic_refill_slots_0_valid) || FetchL1Plugin_logic_refill_start_valid);
  assign FetchL1Plugin_logic_refill_onCmd_propoedOh = (FetchL1Plugin_logic_refill_slots_0_askCmd && 1'b1);
  assign when_FetchL1Plugin_l276 = (! FetchL1Plugin_logic_refill_onCmd_locked);
  assign FetchL1Plugin_logic_refill_onCmd_oh = (FetchL1Plugin_logic_refill_onCmd_locked ? FetchL1Plugin_logic_refill_onCmd_lockedOh : FetchL1Plugin_logic_refill_onCmd_propoedOh);
  assign FetchL1Plugin_logic_bus_cmd_valid = (|FetchL1Plugin_logic_refill_onCmd_oh);
  assign FetchL1Plugin_logic_bus_cmd_payload_address = {FetchL1Plugin_logic_refill_slots_0_address[31 : 6],6'h0};
  assign FetchL1Plugin_logic_bus_cmd_payload_io = FetchL1Plugin_logic_refill_slots_0_isIo;
  assign FetchL1Plugin_logic_refill_onRsp_holdHarts = ((|FetchL1Plugin_logic_waysWrite_mask) || (|((FetchL1Plugin_logic_refill_slots_0_valid && (FetchL1Plugin_logic_refill_slots_0_address[9 : 6] == fetch_logic_ctrls_0_down_Fetch_WORD_PC[9 : 6])) && (! (1'b1 && (fetch_logic_ctrls_0_down_Fetch_WORD_PC[5 : 2] < FetchL1Plugin_logic_refill_onRsp_wordIndex))))));
  assign fetch_logic_ctrls_0_haltRequest_FetchL1Plugin_l297 = FetchL1Plugin_logic_refill_onRsp_holdHarts;
  assign FetchL1Plugin_logic_bus_rsp_fire = (FetchL1Plugin_logic_bus_rsp_valid && FetchL1Plugin_logic_bus_rsp_ready);
  assign FetchL1Plugin_logic_refill_onRsp_address = FetchL1Plugin_logic_refill_slots_0_address;
  assign when_FetchL1Plugin_l304 = (FetchL1Plugin_logic_bus_rsp_valid && (FetchL1Plugin_logic_refill_onRsp_firstCycle || FetchL1Plugin_logic_bus_rsp_payload_error));
  assign FetchL1Plugin_logic_banks_0_write_valid = (FetchL1Plugin_logic_bus_rsp_valid && 1'b1);
  assign FetchL1Plugin_logic_banks_0_write_payload_address = {FetchL1Plugin_logic_refill_onRsp_address[9 : 6],FetchL1Plugin_logic_refill_onRsp_wordIndex};
  assign FetchL1Plugin_logic_banks_0_write_payload_data = FetchL1Plugin_logic_bus_rsp_payload_data;
  assign FetchL1Plugin_logic_bus_rsp_ready = 1'b1;
  assign when_FetchL1Plugin_l330 = (FetchL1Plugin_logic_refill_onRsp_wordIndex == 4'b1111);
  assign FetchL1Plugin_logic_cmd_doIt = (fetch_logic_ctrls_1_up_ready || ((! fetch_logic_ctrls_1_up_valid) && 1'b1));
  assign FetchL1Plugin_logic_banks_0_read_cmd_valid = FetchL1Plugin_logic_cmd_doIt;
  assign FetchL1Plugin_logic_banks_0_read_cmd_payload = fetch_logic_ctrls_0_down_Fetch_WORD_PC[9 : 2];
  assign FetchL1Plugin_logic_ways_0_read_cmd_valid = FetchL1Plugin_logic_cmd_doIt;
  assign FetchL1Plugin_logic_ways_0_read_cmd_payload = fetch_logic_ctrls_0_down_Fetch_WORD_PC[9 : 6];
  assign FetchL1Plugin_logic_plru_read_cmd_valid = FetchL1Plugin_logic_cmd_doIt;
  assign FetchL1Plugin_logic_plru_read_cmd_payload = fetch_logic_ctrls_0_down_Fetch_WORD_PC[9 : 6];
  assign fetch_logic_ctrls_0_down_FetchL1Plugin_logic_cmd_PLRU_BYPASS_VALID = (FetchL1Plugin_logic_plru_write_valid && (FetchL1Plugin_logic_plru_write_payload_address == FetchL1Plugin_logic_plru_read_cmd_payload));
  assign fetch_logic_ctrls_0_down_FetchL1Plugin_logic_cmd_TAGS_UPDATE = (|FetchL1Plugin_logic_waysWrite_mask);
  assign fetch_logic_ctrls_0_down_FetchL1Plugin_logic_cmd_TAGS_UPDATE_ADDRESS = FetchL1Plugin_logic_waysWrite_address;
  assign fetch_logic_ctrls_1_down_FetchL1Plugin_logic_BANKS_MUXES_0 = fetch_logic_ctrls_1_down_FetchL1Plugin_logic_BANKS_WORDS_0[31 : 0];
  assign fetch_logic_ctrls_2_down_Fetch_WORD = (fetch_logic_ctrls_2_down_FetchL1Plugin_logic_WAYS_HITS_0 ? fetch_logic_ctrls_2_down_FetchL1Plugin_logic_BANKS_MUXES_0 : 32'h0);
  assign fetch_logic_ctrls_1_down_FetchL1Plugin_logic_HAZARD = (fetch_logic_ctrls_1_down_FetchL1Plugin_logic_cmd_TAGS_UPDATE && (fetch_logic_ctrls_1_down_FetchL1Plugin_logic_cmd_TAGS_UPDATE_ADDRESS == fetch_logic_ctrls_1_down_Fetch_WORD_PC[9 : 6]));
  assign fetch_logic_ctrls_1_down_FetchL1Plugin_logic_WAYS_HITS_0 = (fetch_logic_ctrls_1_down_FetchL1Plugin_logic_WAYS_TAGS_0_loaded && (fetch_logic_ctrls_1_down_FetchL1Plugin_logic_WAYS_TAGS_0_address == fetch_logic_ctrls_1_down_MMU_TRANSLATED[31 : 10]));
  assign fetch_logic_ctrls_1_down_FetchL1Plugin_logic_WAYS_HIT = (|fetch_logic_ctrls_1_down_FetchL1Plugin_logic_WAYS_HITS_0);
  assign FetchL1Plugin_logic_ctrl_pmaPort_cmd_address = fetch_logic_ctrls_2_down_MMU_TRANSLATED;
  always @(*) begin
    FetchL1Plugin_logic_plru_write_valid = FetchL1Plugin_logic_ctrl_plruLogic_buffer_regNext_valid;
    if(when_FetchL1Plugin_l558) begin
      FetchL1Plugin_logic_plru_write_valid = 1'b1;
    end
  end

  always @(*) begin
    FetchL1Plugin_logic_plru_write_payload_address = FetchL1Plugin_logic_ctrl_plruLogic_buffer_regNext_payload_address;
    if(when_FetchL1Plugin_l558) begin
      FetchL1Plugin_logic_plru_write_payload_address = FetchL1Plugin_logic_invalidate_counter[3:0];
    end
  end

  assign FetchL1Plugin_logic_ctrl_plruLogic_buffer_valid = (fetch_logic_ctrls_2_up_isValid && fetch_logic_ctrls_2_up_isReady);
  assign FetchL1Plugin_logic_ctrl_plruLogic_buffer_payload_address = fetch_logic_ctrls_2_down_Fetch_WORD_PC[9 : 6];
  assign FetchL1Plugin_logic_ctrl_dataAccessFault = (_zz_FetchL1Plugin_logic_ctrl_dataAccessFault[0] && (! fetch_logic_ctrls_2_down_FetchL1Plugin_logic_HAZARD));
  always @(*) begin
    FetchL1Plugin_logic_trapPort_valid = 1'b0;
    if(when_FetchL1Plugin_l474) begin
      FetchL1Plugin_logic_trapPort_valid = 1'b1;
    end
    if(when_FetchL1Plugin_l480) begin
      FetchL1Plugin_logic_trapPort_valid = 1'b1;
    end
    if(when_FetchL1Plugin_l487) begin
      FetchL1Plugin_logic_trapPort_valid = 1'b1;
    end
    if(fetch_logic_ctrls_2_down_MMU_ACCESS_FAULT) begin
      FetchL1Plugin_logic_trapPort_valid = 1'b1;
    end
    if(fetch_logic_ctrls_2_down_MMU_REFILL) begin
      FetchL1Plugin_logic_trapPort_valid = 1'b1;
    end
    if(fetch_logic_ctrls_2_down_MMU_HAZARD) begin
      FetchL1Plugin_logic_trapPort_valid = 1'b1;
    end
    if(fetch_logic_ctrls_2_down_Fetch_PC_FAULT) begin
      FetchL1Plugin_logic_trapPort_valid = 1'b1;
    end
    if(when_FetchL1Plugin_l533) begin
      FetchL1Plugin_logic_trapPort_valid = 1'b0;
    end
  end

  assign FetchL1Plugin_logic_trapPort_payload_tval = fetch_logic_ctrls_2_down_Fetch_WORD_PC;
  always @(*) begin
    FetchL1Plugin_logic_trapPort_payload_exception = 1'bx;
    if(when_FetchL1Plugin_l474) begin
      FetchL1Plugin_logic_trapPort_payload_exception = 1'b0;
    end
    if(when_FetchL1Plugin_l480) begin
      FetchL1Plugin_logic_trapPort_payload_exception = 1'b1;
    end
    if(when_FetchL1Plugin_l487) begin
      FetchL1Plugin_logic_trapPort_payload_exception = 1'b1;
    end
    if(fetch_logic_ctrls_2_down_MMU_ACCESS_FAULT) begin
      FetchL1Plugin_logic_trapPort_payload_exception = 1'b1;
    end
    if(fetch_logic_ctrls_2_down_MMU_REFILL) begin
      FetchL1Plugin_logic_trapPort_payload_exception = 1'b0;
    end
    if(fetch_logic_ctrls_2_down_MMU_HAZARD) begin
      FetchL1Plugin_logic_trapPort_payload_exception = 1'b0;
    end
    if(fetch_logic_ctrls_2_down_Fetch_PC_FAULT) begin
      FetchL1Plugin_logic_trapPort_payload_exception = 1'b1;
    end
  end

  always @(*) begin
    FetchL1Plugin_logic_trapPort_payload_code = 4'bxxxx;
    if(when_FetchL1Plugin_l474) begin
      FetchL1Plugin_logic_trapPort_payload_code = 4'b0100;
    end
    if(when_FetchL1Plugin_l480) begin
      FetchL1Plugin_logic_trapPort_payload_code = 4'b0001;
    end
    if(when_FetchL1Plugin_l487) begin
      FetchL1Plugin_logic_trapPort_payload_code = 4'b1100;
    end
    if(fetch_logic_ctrls_2_down_MMU_ACCESS_FAULT) begin
      FetchL1Plugin_logic_trapPort_payload_code = 4'b0001;
    end
    if(fetch_logic_ctrls_2_down_MMU_REFILL) begin
      FetchL1Plugin_logic_trapPort_payload_code = 4'b0111;
    end
    if(fetch_logic_ctrls_2_down_MMU_HAZARD) begin
      FetchL1Plugin_logic_trapPort_payload_code = 4'b0100;
    end
    if(fetch_logic_ctrls_2_down_Fetch_PC_FAULT) begin
      FetchL1Plugin_logic_trapPort_payload_code = 4'b0001;
      if(when_FetchL1Plugin_l520) begin
        FetchL1Plugin_logic_trapPort_payload_code = 4'b1100;
      end
    end
  end

  assign _zz_26 = zz_FetchL1Plugin_logic_trapPort_payload_arg(1'b0);
  always @(*) FetchL1Plugin_logic_trapPort_payload_arg = _zz_26;
  always @(*) begin
    FetchL1Plugin_logic_ctrl_allowRefill = ((! fetch_logic_ctrls_2_down_FetchL1Plugin_logic_WAYS_HIT) && (! fetch_logic_ctrls_2_down_FetchL1Plugin_logic_HAZARD));
    if(when_FetchL1Plugin_l480) begin
      FetchL1Plugin_logic_ctrl_allowRefill = 1'b0;
    end
    if(when_FetchL1Plugin_l487) begin
      FetchL1Plugin_logic_ctrl_allowRefill = 1'b0;
    end
    if(fetch_logic_ctrls_2_down_MMU_ACCESS_FAULT) begin
      FetchL1Plugin_logic_ctrl_allowRefill = 1'b0;
    end
    if(fetch_logic_ctrls_2_down_MMU_REFILL) begin
      FetchL1Plugin_logic_ctrl_allowRefill = 1'b0;
    end
    if(fetch_logic_ctrls_2_down_MMU_HAZARD) begin
      FetchL1Plugin_logic_ctrl_allowRefill = 1'b0;
    end
    if(fetch_logic_ctrls_2_down_Fetch_PC_FAULT) begin
      FetchL1Plugin_logic_ctrl_allowRefill = 1'b0;
    end
  end

  assign when_FetchL1Plugin_l474 = ((! fetch_logic_ctrls_2_down_FetchL1Plugin_logic_WAYS_HIT) || fetch_logic_ctrls_2_down_FetchL1Plugin_logic_HAZARD);
  assign when_FetchL1Plugin_l480 = ((FetchL1Plugin_logic_ctrl_dataAccessFault || FetchL1Plugin_logic_ctrl_pmaPort_rsp_fault) || fetch_logic_ctrls_2_down_FetchL1Plugin_logic_pmpPort_ACCESS_FAULT);
  assign when_FetchL1Plugin_l487 = (fetch_logic_ctrls_2_down_MMU_PAGE_FAULT || (! fetch_logic_ctrls_2_down_MMU_ALLOW_EXECUTE));
  assign when_FetchL1Plugin_l520 = (! fetch_logic_ctrls_2_down_MMU_BYPASS_TRANSLATION);
  always @(*) begin
    FetchL1Plugin_logic_refill_start_valid = (FetchL1Plugin_logic_ctrl_allowRefill && (! FetchL1Plugin_logic_ctrl_trapSent));
    if(when_FetchL1Plugin_l537) begin
      FetchL1Plugin_logic_refill_start_valid = 1'b0;
    end
  end

  assign FetchL1Plugin_logic_refill_start_address = fetch_logic_ctrls_2_down_MMU_TRANSLATED;
  assign FetchL1Plugin_logic_refill_start_isIo = FetchL1Plugin_logic_ctrl_pmaPort_rsp_io;
  assign fetch_logic_ctrls_2_down_TRAP = (FetchL1Plugin_logic_trapPort_valid || FetchL1Plugin_logic_ctrl_trapSent);
  assign when_FetchL1Plugin_l533 = ((! fetch_logic_ctrls_2_up_isValid) || FetchL1Plugin_logic_ctrl_trapSent);
  assign when_FetchL1Plugin_l537 = ((! fetch_logic_ctrls_2_up_isValid) && 1'b1);
  assign when_FetchL1Plugin_l541 = (((! fetch_logic_ctrls_2_up_isValid) || fetch_logic_ctrls_2_down_isReady) || fetch_logic_ctrls_2_up_isCanceling);
  assign when_FetchL1Plugin_l558 = (! FetchL1Plugin_logic_invalidate_done);
  assign LsuPlugin_logic_frontend_defaultsDecodings_0 = 1'b0;
  assign LsuPlugin_logic_frontend_defaultsDecodings_1 = 1'b0;
  assign LsuPlugin_logic_frontend_defaultsDecodings_2 = 1'b0;
  assign LsuPlugin_logic_frontend_defaultsDecodings_3 = 1'b0;
  assign LsuPlugin_logic_frontend_defaultsDecodings_4 = 1'b0;
  assign LsuPlugin_logic_frontend_defaultsDecodings_5 = 1'b0;
  assign WhiteboxerPlugin_logic_fetch_fetchId = fetch_logic_ctrls_0_down_Fetch_ID;
  assign WhiteboxerPlugin_logic_decodes_0_fire = ((decode_ctrls_0_up_LANE_SEL_0 && decode_ctrls_0_up_isReady) && (! decode_ctrls_0_lane0_upIsCancel));
  assign when_CtrlLaneApi_l50 = (decode_ctrls_0_up_isReady || decode_ctrls_0_lane0_upIsCancel);
  assign WhiteboxerPlugin_logic_decodes_0_spawn = (decode_ctrls_0_up_LANE_SEL_0 && (! decode_ctrls_0_up_LANE_SEL_0_regNext));
  assign WhiteboxerPlugin_logic_decodes_0_pc = _zz_WhiteboxerPlugin_logic_decodes_0_pc;
  assign WhiteboxerPlugin_logic_decodes_0_fetchId = decode_ctrls_0_down_Fetch_ID_0;
  assign WhiteboxerPlugin_logic_decodes_0_decodeId = decode_ctrls_0_down_Decode_DOP_ID_0;
  always @(*) begin
    early0_EnvPlugin_logic_flushPort_valid = 1'b0;
    if(when_EnvPlugin_l119) begin
      early0_EnvPlugin_logic_flushPort_valid = 1'b1;
    end
  end

  assign early0_EnvPlugin_logic_flushPort_payload_uopId = execute_ctrl2_down_Decode_UOP_ID_lane0;
  assign early0_EnvPlugin_logic_flushPort_payload_self = 1'b0;
  always @(*) begin
    early0_EnvPlugin_logic_trapPort_valid = 1'b0;
    if(when_EnvPlugin_l119) begin
      early0_EnvPlugin_logic_trapPort_valid = 1'b1;
    end
  end

  always @(*) begin
    early0_EnvPlugin_logic_trapPort_payload_exception = 1'b1;
    case(execute_ctrl2_down_early0_EnvPlugin_OP_lane0)
      EnvPluginOp_PRIV_RET : begin
        if(when_EnvPlugin_l86) begin
          early0_EnvPlugin_logic_trapPort_payload_exception = 1'b0;
        end
      end
      EnvPluginOp_WFI : begin
        if(when_EnvPlugin_l95) begin
          early0_EnvPlugin_logic_trapPort_payload_exception = 1'b0;
        end
      end
      EnvPluginOp_FENCE_I : begin
        early0_EnvPlugin_logic_trapPort_payload_exception = 1'b0;
      end
      default : begin
      end
    endcase
  end

  assign early0_EnvPlugin_logic_trapPort_payload_tval = ((execute_ctrl2_down_early0_EnvPlugin_OP_lane0 == EnvPluginOp_EBREAK) ? execute_ctrl2_down_PC_lane0 : 32'h0);
  always @(*) begin
    early0_EnvPlugin_logic_trapPort_payload_code = 4'b0010;
    case(execute_ctrl2_down_early0_EnvPlugin_OP_lane0)
      EnvPluginOp_EBREAK : begin
        early0_EnvPlugin_logic_trapPort_payload_code = 4'b0011;
      end
      EnvPluginOp_ECALL : begin
        early0_EnvPlugin_logic_trapPort_payload_code = (_zz_early0_EnvPlugin_logic_trapPort_payload_code | 4'b1000);
      end
      EnvPluginOp_PRIV_RET : begin
        if(when_EnvPlugin_l86) begin
          early0_EnvPlugin_logic_trapPort_payload_code = 4'b0001;
        end
      end
      EnvPluginOp_WFI : begin
        if(when_EnvPlugin_l95) begin
          early0_EnvPlugin_logic_trapPort_payload_code = 4'b1000;
        end
      end
      EnvPluginOp_FENCE_I : begin
        early0_EnvPlugin_logic_trapPort_payload_code = 4'b0010;
      end
      default : begin
      end
    endcase
  end

  always @(*) begin
    early0_EnvPlugin_logic_trapPort_payload_arg = 2'bxx;
    case(execute_ctrl2_down_early0_EnvPlugin_OP_lane0)
      EnvPluginOp_PRIV_RET : begin
        if(when_EnvPlugin_l86) begin
          early0_EnvPlugin_logic_trapPort_payload_arg[1 : 0] = early0_EnvPlugin_logic_exe_xretPriv;
        end
      end
      default : begin
      end
    endcase
  end

  assign PrivilegedPlugin_logic_defaultTrap_csrPrivilege = CsrAccessPlugin_bus_decode_address[9 : 8];
  assign PrivilegedPlugin_logic_defaultTrap_csrReadOnly = (CsrAccessPlugin_bus_decode_address[11 : 10] == 2'b11);
  assign when_PrivilegedPlugin_l689 = ((PrivilegedPlugin_logic_defaultTrap_csrReadOnly && CsrAccessPlugin_bus_decode_write) || (PrivilegedPlugin_logic_harts_0_privilege < PrivilegedPlugin_logic_defaultTrap_csrPrivilege));
  assign FetchL1Plugin_pmaBuilder_addressBits = FetchL1Plugin_logic_ctrl_pmaPort_cmd_address;
  assign _zz_FetchL1Plugin_logic_ctrl_pmaPort_rsp_io = ((FetchL1Plugin_pmaBuilder_addressBits & 32'h0) == 32'h0);
  assign FetchL1Plugin_pmaBuilder_onTransfers_0_addressHit = _zz_FetchL1Plugin_pmaBuilder_onTransfers_0_addressHit[0];
  assign FetchL1Plugin_pmaBuilder_onTransfers_0_argsHit = (|1'b1);
  assign FetchL1Plugin_pmaBuilder_onTransfers_0_hit = (FetchL1Plugin_pmaBuilder_onTransfers_0_argsHit && FetchL1Plugin_pmaBuilder_onTransfers_0_addressHit);
  assign FetchL1Plugin_logic_ctrl_pmaPort_rsp_fault = (! ((|{((FetchL1Plugin_pmaBuilder_addressBits & 32'hff000000) == 32'h10000000),((FetchL1Plugin_pmaBuilder_addressBits & 32'hff000000) == 32'h20000000)}) && (|FetchL1Plugin_pmaBuilder_onTransfers_0_hit)));
  assign FetchL1Plugin_logic_ctrl_pmaPort_rsp_io = (! _zz_FetchL1Plugin_logic_ctrl_pmaPort_rsp_io_1[0]);
  assign FetchL1Plugin_logic_bus_toWishbone_pending = (FetchL1Plugin_logic_bus_toWishbone_counter != 4'b0000);
  assign FetchL1Plugin_logic_bus_toWishbone_lastCycle = (&FetchL1Plugin_logic_bus_toWishbone_counter);
  assign FetchL1WishbonePlugin_logic_bus_ADR = {_zz_FetchL1WishbonePlugin_logic_bus_ADR,FetchL1Plugin_logic_bus_toWishbone_counter};
  assign FetchL1WishbonePlugin_logic_bus_CTI = (FetchL1Plugin_logic_bus_toWishbone_lastCycle ? 3'b111 : 3'b010);
  assign FetchL1WishbonePlugin_logic_bus_BTE = 2'b00;
  assign FetchL1WishbonePlugin_logic_bus_SEL = 4'b1111;
  assign FetchL1WishbonePlugin_logic_bus_WE = 1'b0;
  assign FetchL1WishbonePlugin_logic_bus_DAT_MOSI = 32'bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx;
  always @(*) begin
    FetchL1WishbonePlugin_logic_bus_CYC = 1'b0;
    if(when_FetchL1Bus_l247) begin
      FetchL1WishbonePlugin_logic_bus_CYC = 1'b1;
    end
  end

  always @(*) begin
    FetchL1WishbonePlugin_logic_bus_STB = 1'b0;
    if(when_FetchL1Bus_l247) begin
      FetchL1WishbonePlugin_logic_bus_STB = 1'b1;
    end
  end

  assign when_FetchL1Bus_l247 = (FetchL1Plugin_logic_bus_cmd_valid || FetchL1Plugin_logic_bus_toWishbone_pending);
  assign when_FetchL1Bus_l250 = (FetchL1WishbonePlugin_logic_bus_ACK || FetchL1WishbonePlugin_logic_bus_ERR);
  assign FetchL1Plugin_logic_bus_cmd_ready = ((FetchL1Plugin_logic_bus_cmd_valid && FetchL1Plugin_logic_bus_toWishbone_lastCycle) && (FetchL1WishbonePlugin_logic_bus_ACK || FetchL1WishbonePlugin_logic_bus_ERR));
  assign FetchL1Plugin_logic_bus_rsp_valid = _zz_FetchL1Plugin_logic_bus_rsp_valid;
  assign FetchL1Plugin_logic_bus_rsp_payload_data = FetchL1WishbonePlugin_logic_bus_DAT_MISO_regNext;
  assign FetchL1Plugin_logic_bus_rsp_payload_error = FetchL1WishbonePlugin_logic_bus_ERR_regNext;
  always @(*) begin
    DecoderPlugin_logic_forgetPort_valid = 1'b0;
    if(DecoderPlugin_logic_laneLogic_0_fixer_doIt) begin
      DecoderPlugin_logic_forgetPort_valid = 1'b1;
    end
  end

  always @(*) begin
    DecoderPlugin_logic_forgetPort_payload_pcOnLastSlice = 32'bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx;
    if(DecoderPlugin_logic_laneLogic_0_fixer_doIt) begin
      DecoderPlugin_logic_forgetPort_payload_pcOnLastSlice = (decode_ctrls_1_down_PC_0 + _zz_DecoderPlugin_logic_forgetPort_payload_pcOnLastSlice);
    end
  end

  always @(*) begin
    _zz_execute_ctrl1_down_early0_SrcPlugin_SRC1_lane0 = 32'bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx;
    case(execute_ctrl1_down_early0_SrcPlugin_logic_SRC1_CTRL_lane0)
      1'b0 : begin
        _zz_execute_ctrl1_down_early0_SrcPlugin_SRC1_lane0 = execute_ctrl1_down_integer_RS1_lane0;
      end
      default : begin
        _zz_execute_ctrl1_down_early0_SrcPlugin_SRC1_lane0 = {execute_ctrl1_down_Decode_UOP_lane0[31 : 12],12'h0};
      end
    endcase
  end

  assign execute_ctrl1_down_early0_SrcPlugin_SRC1_lane0 = _zz_execute_ctrl1_down_early0_SrcPlugin_SRC1_lane0;
  always @(*) begin
    _zz_execute_ctrl1_down_early0_SrcPlugin_SRC2_lane0 = 32'bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx;
    case(execute_ctrl1_down_early0_SrcPlugin_logic_SRC2_CTRL_lane0)
      2'b00 : begin
        _zz_execute_ctrl1_down_early0_SrcPlugin_SRC2_lane0 = execute_ctrl1_down_integer_RS2_lane0;
      end
      2'b01 : begin
        _zz_execute_ctrl1_down_early0_SrcPlugin_SRC2_lane0 = {{20{_zz__zz_execute_ctrl1_down_early0_SrcPlugin_SRC2_lane0[11]}}, _zz__zz_execute_ctrl1_down_early0_SrcPlugin_SRC2_lane0};
      end
      2'b10 : begin
        _zz_execute_ctrl1_down_early0_SrcPlugin_SRC2_lane0 = execute_ctrl1_down_PC_lane0;
      end
      default : begin
        _zz_execute_ctrl1_down_early0_SrcPlugin_SRC2_lane0 = {{20{_zz__zz_execute_ctrl1_down_early0_SrcPlugin_SRC2_lane0_1[11]}}, _zz__zz_execute_ctrl1_down_early0_SrcPlugin_SRC2_lane0_1};
      end
    endcase
  end

  assign execute_ctrl1_down_early0_SrcPlugin_SRC2_lane0 = _zz_execute_ctrl1_down_early0_SrcPlugin_SRC2_lane0;
  always @(*) begin
    early0_SrcPlugin_logic_addsub_combined_rs2Patched = execute_ctrl2_down_early0_SrcPlugin_SRC2_lane0;
    if(execute_ctrl2_down_SrcStageables_REVERT_lane0) begin
      early0_SrcPlugin_logic_addsub_combined_rs2Patched = (~ execute_ctrl2_down_early0_SrcPlugin_SRC2_lane0);
    end
    if(execute_ctrl2_down_SrcStageables_ZERO_lane0) begin
      early0_SrcPlugin_logic_addsub_combined_rs2Patched = 32'h0;
    end
  end

  assign execute_ctrl2_down_early0_SrcPlugin_ADD_SUB_lane0 = ($signed(_zz_execute_ctrl2_down_early0_SrcPlugin_ADD_SUB_lane0) + $signed(_zz_execute_ctrl2_down_early0_SrcPlugin_ADD_SUB_lane0_1));
  assign execute_ctrl2_down_early0_SrcPlugin_LESS_lane0 = ((execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[31] == execute_ctrl2_down_early0_SrcPlugin_SRC2_lane0[31]) ? execute_ctrl2_down_early0_SrcPlugin_ADD_SUB_lane0[31] : (execute_ctrl2_down_SrcStageables_UNSIGNED_lane0 ? execute_ctrl2_down_early0_SrcPlugin_SRC2_lane0[31] : execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0[31]));
  assign lane0_IntFormatPlugin_logic_stages_0_hits = {early0_BarrelShifterPlugin_logic_wb_valid,early0_IntAluPlugin_logic_wb_valid};
  assign lane0_IntFormatPlugin_logic_stages_0_wb_valid = (execute_ctrl2_up_LANE_SEL_lane0 && (|lane0_IntFormatPlugin_logic_stages_0_hits));
  assign lane0_IntFormatPlugin_logic_stages_0_raw = ((lane0_IntFormatPlugin_logic_stages_0_hits[0] ? early0_IntAluPlugin_logic_wb_payload : 32'h0) | (lane0_IntFormatPlugin_logic_stages_0_hits[1] ? early0_BarrelShifterPlugin_logic_wb_payload : 32'h0));
  assign lane0_IntFormatPlugin_logic_stages_0_wb_payload = lane0_IntFormatPlugin_logic_stages_0_raw;
  assign lane0_IntFormatPlugin_logic_stages_1_hits = {LsuPlugin_logic_iwb_valid,{late0_BarrelShifterPlugin_logic_wb_valid,{late0_IntAluPlugin_logic_wb_valid,early0_MulPlugin_logic_formatBus_valid}}};
  assign lane0_IntFormatPlugin_logic_stages_1_wb_valid = (execute_ctrl4_up_LANE_SEL_lane0 && (|lane0_IntFormatPlugin_logic_stages_1_hits));
  assign lane0_IntFormatPlugin_logic_stages_1_raw = (((lane0_IntFormatPlugin_logic_stages_1_hits[0] ? early0_MulPlugin_logic_formatBus_payload : 32'h0) | (lane0_IntFormatPlugin_logic_stages_1_hits[1] ? late0_IntAluPlugin_logic_wb_payload : 32'h0)) | ((lane0_IntFormatPlugin_logic_stages_1_hits[2] ? late0_BarrelShifterPlugin_logic_wb_payload : 32'h0) | (lane0_IntFormatPlugin_logic_stages_1_hits[3] ? LsuPlugin_logic_iwb_payload : 32'h0)));
  always @(*) begin
    lane0_IntFormatPlugin_logic_stages_1_wb_payload = lane0_IntFormatPlugin_logic_stages_1_raw;
    if(lane0_IntFormatPlugin_logic_stages_1_segments_0_doIt) begin
      lane0_IntFormatPlugin_logic_stages_1_wb_payload[15 : 8] = {8{lane0_IntFormatPlugin_logic_stages_1_segments_0_sign_value}};
    end
    if(lane0_IntFormatPlugin_logic_stages_1_segments_1_doIt) begin
      lane0_IntFormatPlugin_logic_stages_1_wb_payload[31 : 16] = {16{lane0_IntFormatPlugin_logic_stages_1_segments_1_sign_value}};
    end
  end

  assign lane0_IntFormatPlugin_logic_stages_1_segments_0_sign_sels_0 = lane0_IntFormatPlugin_logic_stages_1_raw[7];
  always @(*) begin
    _zz_lane0_IntFormatPlugin_logic_stages_1_segments_0_sign_value = 1'bx;
    case(execute_ctrl4_down_lane0_IntFormatPlugin_logic_WIDTH_ID_lane0)
      2'b00 : begin
        _zz_lane0_IntFormatPlugin_logic_stages_1_segments_0_sign_value = lane0_IntFormatPlugin_logic_stages_1_segments_0_sign_sels_0;
      end
      default : begin
      end
    endcase
  end

  assign lane0_IntFormatPlugin_logic_stages_1_segments_0_sign_value = (execute_ctrl4_down_lane0_IntFormatPlugin_logic_SIGNED_lane0 && _zz_lane0_IntFormatPlugin_logic_stages_1_segments_0_sign_value);
  assign lane0_IntFormatPlugin_logic_stages_1_segments_0_doIt = (execute_ctrl4_down_lane0_IntFormatPlugin_logic_WIDTH_ID_lane0 < 2'b01);
  assign lane0_IntFormatPlugin_logic_stages_1_segments_1_sign_sels_0 = lane0_IntFormatPlugin_logic_stages_1_raw[7];
  assign lane0_IntFormatPlugin_logic_stages_1_segments_1_sign_sels_1 = lane0_IntFormatPlugin_logic_stages_1_raw[15];
  always @(*) begin
    _zz_lane0_IntFormatPlugin_logic_stages_1_segments_1_sign_value = 1'bx;
    case(execute_ctrl4_down_lane0_IntFormatPlugin_logic_WIDTH_ID_lane0)
      2'b00 : begin
        _zz_lane0_IntFormatPlugin_logic_stages_1_segments_1_sign_value = lane0_IntFormatPlugin_logic_stages_1_segments_1_sign_sels_0;
      end
      2'b01 : begin
        _zz_lane0_IntFormatPlugin_logic_stages_1_segments_1_sign_value = lane0_IntFormatPlugin_logic_stages_1_segments_1_sign_sels_1;
      end
      default : begin
      end
    endcase
  end

  assign lane0_IntFormatPlugin_logic_stages_1_segments_1_sign_value = (execute_ctrl4_down_lane0_IntFormatPlugin_logic_SIGNED_lane0 && _zz_lane0_IntFormatPlugin_logic_stages_1_segments_1_sign_value);
  assign lane0_IntFormatPlugin_logic_stages_1_segments_1_doIt = (execute_ctrl4_down_lane0_IntFormatPlugin_logic_WIDTH_ID_lane0 < 2'b10);
  assign lane0_IntFormatPlugin_logic_stages_2_hits = {CsrAccessPlugin_logic_wbWi_valid,early0_DivPlugin_logic_formatBus_valid};
  assign lane0_IntFormatPlugin_logic_stages_2_wb_valid = (execute_ctrl3_up_LANE_SEL_lane0 && (|lane0_IntFormatPlugin_logic_stages_2_hits));
  assign lane0_IntFormatPlugin_logic_stages_2_raw = ((lane0_IntFormatPlugin_logic_stages_2_hits[0] ? early0_DivPlugin_logic_formatBus_payload : 32'h0) | (lane0_IntFormatPlugin_logic_stages_2_hits[1] ? CsrAccessPlugin_logic_wbWi_payload : 32'h0));
  assign lane0_IntFormatPlugin_logic_stages_2_wb_payload = lane0_IntFormatPlugin_logic_stages_2_raw;
  always @(*) begin
    _zz_execute_ctrl3_down_late0_SrcPlugin_SRC1_lane0 = 32'bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx;
    case(execute_ctrl3_down_late0_SrcPlugin_logic_SRC1_CTRL_lane0)
      1'b0 : begin
        _zz_execute_ctrl3_down_late0_SrcPlugin_SRC1_lane0 = execute_ctrl3_down_integer_RS1_lane0;
      end
      default : begin
        _zz_execute_ctrl3_down_late0_SrcPlugin_SRC1_lane0 = {execute_ctrl3_down_Decode_UOP_lane0[31 : 12],12'h0};
      end
    endcase
  end

  assign execute_ctrl3_down_late0_SrcPlugin_SRC1_lane0 = _zz_execute_ctrl3_down_late0_SrcPlugin_SRC1_lane0;
  always @(*) begin
    _zz_execute_ctrl3_down_late0_SrcPlugin_SRC2_lane0 = 32'bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx;
    case(execute_ctrl3_down_late0_SrcPlugin_logic_SRC2_CTRL_lane0)
      2'b00 : begin
        _zz_execute_ctrl3_down_late0_SrcPlugin_SRC2_lane0 = execute_ctrl3_down_integer_RS2_lane0;
      end
      2'b01 : begin
        _zz_execute_ctrl3_down_late0_SrcPlugin_SRC2_lane0 = {{20{_zz__zz_execute_ctrl3_down_late0_SrcPlugin_SRC2_lane0[11]}}, _zz__zz_execute_ctrl3_down_late0_SrcPlugin_SRC2_lane0};
      end
      2'b10 : begin
        _zz_execute_ctrl3_down_late0_SrcPlugin_SRC2_lane0 = execute_ctrl3_down_PC_lane0;
      end
      default : begin
      end
    endcase
  end

  assign execute_ctrl3_down_late0_SrcPlugin_SRC2_lane0 = _zz_execute_ctrl3_down_late0_SrcPlugin_SRC2_lane0;
  always @(*) begin
    late0_SrcPlugin_logic_addsub_combined_rs2Patched = execute_ctrl4_down_late0_SrcPlugin_SRC2_lane0;
    if(execute_ctrl4_down_SrcStageables_REVERT_lane0) begin
      late0_SrcPlugin_logic_addsub_combined_rs2Patched = (~ execute_ctrl4_down_late0_SrcPlugin_SRC2_lane0);
    end
    if(execute_ctrl4_down_SrcStageables_ZERO_lane0) begin
      late0_SrcPlugin_logic_addsub_combined_rs2Patched = 32'h0;
    end
  end

  assign execute_ctrl4_down_late0_SrcPlugin_ADD_SUB_lane0 = ($signed(_zz_execute_ctrl4_down_late0_SrcPlugin_ADD_SUB_lane0) + $signed(_zz_execute_ctrl4_down_late0_SrcPlugin_ADD_SUB_lane0_1));
  assign execute_ctrl4_down_late0_SrcPlugin_LESS_lane0 = ((execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[31] == execute_ctrl4_down_late0_SrcPlugin_SRC2_lane0[31]) ? execute_ctrl4_down_late0_SrcPlugin_ADD_SUB_lane0[31] : (execute_ctrl4_down_SrcStageables_UNSIGNED_lane0 ? execute_ctrl4_down_late0_SrcPlugin_SRC2_lane0[31] : execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0[31]));
  assign early0_EnvPlugin_logic_exe_privilege = PrivilegedPlugin_logic_harts_0_privilege;
  assign early0_EnvPlugin_logic_exe_xretPriv = execute_ctrl2_down_Decode_UOP_lane0[29 : 28];
  always @(*) begin
    early0_EnvPlugin_logic_exe_commit = 1'b0;
    case(execute_ctrl2_down_early0_EnvPlugin_OP_lane0)
      EnvPluginOp_PRIV_RET : begin
        if(when_EnvPlugin_l86) begin
          early0_EnvPlugin_logic_exe_commit = 1'b1;
        end
      end
      EnvPluginOp_WFI : begin
        if(when_EnvPlugin_l95) begin
          early0_EnvPlugin_logic_exe_commit = 1'b1;
        end
      end
      EnvPluginOp_FENCE_I : begin
        early0_EnvPlugin_logic_exe_commit = 1'b1;
      end
      default : begin
      end
    endcase
  end

  assign early0_EnvPlugin_logic_exe_retKo = 1'b0;
  assign early0_EnvPlugin_logic_exe_vmaKo = 1'b0;
  assign when_EnvPlugin_l86 = ((early0_EnvPlugin_logic_exe_xretPriv <= PrivilegedPlugin_logic_harts_0_privilege) && (! early0_EnvPlugin_logic_exe_retKo));
  assign when_EnvPlugin_l95 = ((early0_EnvPlugin_logic_exe_privilege == 2'b11) || ((! PrivilegedPlugin_logic_harts_0_m_status_tw) && (1'b1 || (early0_EnvPlugin_logic_exe_privilege == 2'b01))));
  assign when_EnvPlugin_l119 = (execute_ctrl2_up_LANE_SEL_lane0 && execute_ctrl2_down_early0_EnvPlugin_SEL_lane0);
  assign when_EnvPlugin_l123 = (! early0_EnvPlugin_logic_exe_commit);
  always @(*) begin
    case(execute_ctrl2_down_BranchPlugin_BRANCH_CTRL_lane0)
      BranchPlugin_BranchCtrlEnum_JALR : begin
        early0_BranchPlugin_pcCalc_target_a = execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0;
      end
      default : begin
        early0_BranchPlugin_pcCalc_target_a = execute_ctrl2_down_PC_lane0;
      end
    endcase
  end

  always @(*) begin
    case(execute_ctrl2_down_BranchPlugin_BRANCH_CTRL_lane0)
      BranchPlugin_BranchCtrlEnum_JAL : begin
        early0_BranchPlugin_pcCalc_target_b = {{11{_zz_early0_BranchPlugin_pcCalc_target_b[20]}}, _zz_early0_BranchPlugin_pcCalc_target_b};
      end
      BranchPlugin_BranchCtrlEnum_JALR : begin
        early0_BranchPlugin_pcCalc_target_b = {{20{_zz_early0_BranchPlugin_pcCalc_target_b_1[11]}}, _zz_early0_BranchPlugin_pcCalc_target_b_1};
      end
      default : begin
        early0_BranchPlugin_pcCalc_target_b = {{19{_zz_early0_BranchPlugin_pcCalc_target_b_2[12]}}, _zz_early0_BranchPlugin_pcCalc_target_b_2};
      end
    endcase
  end

  assign early0_BranchPlugin_pcCalc_slices = (_zz_early0_BranchPlugin_pcCalc_slices + {1'b0,1'b1});
  always @(*) begin
    execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_TRUE_lane0 = _zz_execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_TRUE_lane0;
    execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_TRUE_lane0[0] = 1'b0;
  end

  assign execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_FALSE_lane0 = (execute_ctrl2_down_PC_lane0 + _zz_execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_FALSE_lane0);
  assign execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_LAST_SLICE_lane0 = (execute_ctrl2_down_PC_lane0 + _zz_execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_LAST_SLICE_lane0);
  assign AlignerPlugin_logic_maskGen_frontMasks_0 = 1'b1;
  assign AlignerPlugin_logic_maskGen_backMasks_0 = 1'b1;
  assign fetch_logic_ctrls_2_down_AlignerPlugin_logic_FETCH_MASK = (AlignerPlugin_logic_maskGen_frontMasks_0 & ((! fetch_logic_ctrls_2_down_Prediction_WORD_JUMPED) ? 1'b1 : AlignerPlugin_logic_maskGen_backMasks_0));
  assign fetch_logic_ctrls_2_down_AlignerPlugin_logic_FETCH_LAST = ((fetch_logic_ctrls_2_up_isValid && fetch_logic_ctrls_2_down_Prediction_WORD_JUMPED) ? 1'b1 : 1'b0);
  assign AlignerPlugin_logic_slicesInstructions_0 = AlignerPlugin_logic_slices_data_0;
  always @(*) begin
    AlignerPlugin_logic_scanners_0_usageMask = 1'b0;
    AlignerPlugin_logic_scanners_0_usageMask[0] = AlignerPlugin_logic_scanners_0_checker_0_required;
  end

  assign AlignerPlugin_logic_scanners_0_checker_0_required = 1'b1;
  assign AlignerPlugin_logic_scanners_0_checker_0_last = (AlignerPlugin_logic_slices_data_0[1 : 0] != 2'b11);
  assign AlignerPlugin_logic_scanners_0_checker_0_redo = 1'b0;
  assign AlignerPlugin_logic_scanners_0_checker_0_present = AlignerPlugin_logic_slices_mask[0];
  assign AlignerPlugin_logic_scanners_0_checker_0_valid = AlignerPlugin_logic_scanners_0_checker_0_present;
  assign AlignerPlugin_logic_scanners_0_redo = (|AlignerPlugin_logic_scanners_0_checker_0_redo);
  assign AlignerPlugin_logic_scanners_0_valid = (AlignerPlugin_logic_scanners_0_checker_0_valid && (1'b1 || (|AlignerPlugin_logic_scanners_0_checker_0_redo)));
  assign AlignerPlugin_logic_usedMask_0 = 1'b0;
  assign AlignerPlugin_logic_extractors_0_first = 1'b1;
  assign AlignerPlugin_logic_extractors_0_usableMask = (AlignerPlugin_logic_scanners_0_valid && (! AlignerPlugin_logic_usedMask_0[0]));
  assign AlignerPlugin_logic_extractors_0_usableMask_bools_0 = AlignerPlugin_logic_extractors_0_usableMask[0];
  assign _zz_AlignerPlugin_logic_extractors_0_slicesOh[0] = (AlignerPlugin_logic_extractors_0_usableMask_bools_0 && (! 1'b0));
  assign AlignerPlugin_logic_extractors_0_slicesOh = _zz_AlignerPlugin_logic_extractors_0_slicesOh;
  always @(*) begin
    AlignerPlugin_logic_extractors_0_redo = AlignerPlugin_logic_scanners_0_redo;
    if(when_AlignerPlugin_l160) begin
      AlignerPlugin_logic_extractors_0_redo = 1'b0;
    end
  end

  assign AlignerPlugin_logic_extractors_0_localMask = AlignerPlugin_logic_scanners_0_checker_0_required;
  always @(*) begin
    AlignerPlugin_logic_extractors_0_usageMask = AlignerPlugin_logic_scanners_0_usageMask;
    if(when_AlignerPlugin_l160) begin
      AlignerPlugin_logic_extractors_0_usageMask = 1'b0;
    end
  end

  assign AlignerPlugin_logic_usedMask_1 = (AlignerPlugin_logic_usedMask_0 | AlignerPlugin_logic_extractors_0_usageMask);
  always @(*) begin
    AlignerPlugin_logic_extractors_0_valid = (|AlignerPlugin_logic_extractors_0_slicesOh);
    if(when_AlignerPlugin_l160) begin
      AlignerPlugin_logic_extractors_0_valid = 1'b0;
    end
  end

  assign when_AlignerPlugin_l160 = (AlignerPlugin_api_haltIt || (AlignerPlugin_api_singleFetch && (! AlignerPlugin_logic_extractors_0_first)));
  assign when_AlignerPlugin_l171 = (decode_ctrls_0_up_isFiring && 1'b1);
  assign AlignerPlugin_logic_feeder_lanes_0_valid = AlignerPlugin_logic_extractors_0_valid;
  assign decode_ctrls_0_up_LANE_SEL_0 = AlignerPlugin_logic_feeder_lanes_0_valid;
  assign decode_ctrls_0_up_Decode_INSTRUCTION_0 = AlignerPlugin_logic_extractors_0_ctx_instruction;
  assign decode_ctrls_0_up_Decode_DECOMPRESSION_FAULT_0 = 1'b0;
  always @(*) begin
    decode_ctrls_0_up_Decode_INSTRUCTION_RAW_0 = AlignerPlugin_logic_extractors_0_ctx_instruction;
    if(AlignerPlugin_logic_feeder_lanes_0_isRvc) begin
      decode_ctrls_0_up_Decode_INSTRUCTION_RAW_0[31 : 16] = 16'h0;
    end
  end

  assign AlignerPlugin_logic_feeder_lanes_0_isRvc = (AlignerPlugin_logic_extractors_0_ctx_instruction[1 : 0] != 2'b11);
  assign decode_ctrls_0_up_PC_0 = AlignerPlugin_logic_extractors_0_ctx_pc;
  assign decode_ctrls_0_up_Decode_DOP_ID_0 = AlignerPlugin_logic_feeder_harts_0_dopId;
  assign decode_ctrls_0_up_Fetch_ID_0 = AlignerPlugin_logic_extractors_0_ctx_hm_Fetch_ID;
  assign decode_ctrls_0_up_Prediction_WORD_SLICES_BRANCH_0 = AlignerPlugin_logic_extractors_0_ctx_hm_Prediction_WORD_SLICES_BRANCH;
  assign decode_ctrls_0_up_Prediction_WORD_SLICES_TAKEN_0 = AlignerPlugin_logic_extractors_0_ctx_hm_Prediction_WORD_SLICES_TAKEN;
  assign decode_ctrls_0_up_Prediction_WORD_JUMP_PC_0 = AlignerPlugin_logic_extractors_0_ctx_hm_Prediction_WORD_JUMP_PC;
  assign decode_ctrls_0_up_Prediction_WORD_JUMPED_0 = AlignerPlugin_logic_extractors_0_ctx_hm_Prediction_WORD_JUMPED;
  assign decode_ctrls_0_up_TRAP_0 = AlignerPlugin_logic_extractors_0_ctx_trap;
  assign AlignerPlugin_logic_feeder_lanes_0_onBtb_didPrediction = 1'b1;
  assign decode_ctrls_0_up_Prediction_ALIGNED_JUMPED_0 = (decode_ctrls_0_up_Prediction_WORD_JUMPED_0 && AlignerPlugin_logic_feeder_lanes_0_onBtb_didPrediction);
  assign decode_ctrls_0_up_Prediction_ALIGNED_JUMPED_PC_0 = decode_ctrls_0_up_Prediction_WORD_JUMP_PC_0;
  assign decode_ctrls_0_up_Prediction_ALIGNED_SLICES_BRANCH_0 = decode_ctrls_0_up_Prediction_WORD_SLICES_BRANCH_0;
  assign decode_ctrls_0_up_Prediction_ALIGNED_SLICES_TAKEN_0 = decode_ctrls_0_up_Prediction_WORD_SLICES_TAKEN_0;
  assign decode_ctrls_0_up_Prediction_ALIGN_REDO_0 = AlignerPlugin_logic_extractors_0_redo;
  assign decode_ctrls_0_up_valid = (|AlignerPlugin_logic_feeder_lanes_0_valid);
  assign AlignerPlugin_logic_nobuffer_remaningMask = (AlignerPlugin_logic_nobuffer_mask & (~ AlignerPlugin_logic_usedMask_1));
  assign when_AlignerPlugin_l292 = (decode_ctrls_0_up_isValid && decode_ctrls_0_up_isReady);
  assign execute_ctrl0_down_AguPlugin_SIZE_lane0 = execute_ctrl0_down_Decode_UOP_lane0[13 : 12];
  assign LsuPlugin_logic_flusher_wantExit = 1'b0;
  always @(*) begin
    LsuPlugin_logic_flusher_wantStart = 1'b0;
    case(LsuPlugin_logic_flusher_stateReg)
      LsuPlugin_logic_flusher_CMD : begin
      end
      LsuPlugin_logic_flusher_COMPLETION : begin
      end
      default : begin
        LsuPlugin_logic_flusher_wantStart = 1'b1;
      end
    endcase
  end

  assign LsuPlugin_logic_flusher_wantKill = 1'b0;
  assign TrapPlugin_logic_lsuL1Invalidate_0_cmd_ready = LsuPlugin_logic_flusher_arbiter_io_inputs_0_ready;
  assign LsuPlugin_logic_flusher_inflight = (|{(execute_ctrl4_down_LsuL1_SEL_lane0 && execute_ctrl4_down_LsuL1_FLUSH_lane0),(execute_ctrl3_down_LsuL1_SEL_lane0 && execute_ctrl3_down_LsuL1_FLUSH_lane0)});
  always @(*) begin
    LsuPlugin_logic_flusher_arbiter_io_output_ready = 1'b0;
    case(LsuPlugin_logic_flusher_stateReg)
      LsuPlugin_logic_flusher_CMD : begin
      end
      LsuPlugin_logic_flusher_COMPLETION : begin
        if(when_LsuPlugin_l371) begin
          LsuPlugin_logic_flusher_arbiter_io_output_ready = 1'b1;
        end
      end
      default : begin
      end
    endcase
  end

  assign PrivilegedPlugin_api_lsuTriggerBus_load = execute_ctrl3_down_LsuL1_LOAD_lane0;
  assign PrivilegedPlugin_api_lsuTriggerBus_store = execute_ctrl3_down_LsuL1_STORE_lane0;
  assign PrivilegedPlugin_api_lsuTriggerBus_virtual = execute_ctrl3_down_LsuL1_MIXED_ADDRESS_lane0;
  assign PrivilegedPlugin_api_lsuTriggerBus_size = execute_ctrl3_down_LsuL1_SIZE_lane0;
  assign execute_ctrl3_down_LsuPlugin_logic_onTrigger_HIT_lane0 = 1'b0;
  assign execute_ctrl2_down_LsuPlugin_logic_FORCE_PHYSICAL_lane0 = (execute_ctrl2_down_LsuPlugin_logic_FROM_ACCESS_lane0 || execute_ctrl2_down_LsuPlugin_logic_FROM_WB_lane0);
  assign LsuPlugin_logic_onAddress0_ls_prefetchOp = execute_ctrl2_down_Decode_UOP_lane0[24 : 20];
  assign LsuPlugin_logic_onAddress0_ls_port_valid = (execute_ctrl2_up_LANE_SEL_lane0 && execute_ctrl2_down_AguPlugin_SEL_lane0);
  assign LsuPlugin_logic_onAddress0_ls_port_payload_address = execute_ctrl2_down_early0_SrcPlugin_ADD_SUB_lane0;
  assign LsuPlugin_logic_onAddress0_ls_port_payload_size = execute_ctrl2_down_AguPlugin_SIZE_lane0;
  assign LsuPlugin_logic_onAddress0_ls_port_payload_load = execute_ctrl2_down_AguPlugin_LOAD_lane0;
  assign LsuPlugin_logic_onAddress0_ls_port_payload_store = execute_ctrl2_down_AguPlugin_STORE_lane0;
  assign LsuPlugin_logic_onAddress0_ls_port_payload_atomic = execute_ctrl2_down_AguPlugin_ATOMIC_lane0;
  assign LsuPlugin_logic_onAddress0_ls_port_payload_clean = 1'b0;
  assign LsuPlugin_logic_onAddress0_ls_port_payload_invalidate = 1'b0;
  assign LsuPlugin_logic_onAddress0_ls_port_payload_op = LsuL1CmdOpcode_LSU;
  assign LsuPlugin_logic_onAddress0_ls_port_fire = (LsuPlugin_logic_onAddress0_ls_port_valid && LsuPlugin_logic_onAddress0_ls_port_ready);
  assign LsuPlugin_logic_onAddress0_ls_port_payload_storeId = LsuPlugin_logic_onAddress0_ls_storeId;
  assign LsuPlugin_logic_onAddress0_flush_port_valid = ((LsuPlugin_logic_flusher_stateReg == LsuPlugin_logic_flusher_CMD) && (! LsuPlugin_logic_flusher_cmdCounter[4]));
  assign LsuPlugin_logic_onAddress0_flush_port_payload_address = {21'd0, _zz_LsuPlugin_logic_onAddress0_flush_port_payload_address};
  assign LsuPlugin_logic_onAddress0_flush_port_payload_size = 2'b00;
  assign LsuPlugin_logic_onAddress0_flush_port_payload_load = 1'b0;
  assign LsuPlugin_logic_onAddress0_flush_port_payload_store = 1'b0;
  assign LsuPlugin_logic_onAddress0_flush_port_payload_atomic = 1'b0;
  assign LsuPlugin_logic_onAddress0_flush_port_payload_clean = 1'b0;
  assign LsuPlugin_logic_onAddress0_flush_port_payload_invalidate = 1'b0;
  assign LsuPlugin_logic_onAddress0_flush_port_payload_op = LsuL1CmdOpcode_FLUSH;
  assign LsuPlugin_logic_onAddress0_flush_port_payload_storeId = 12'h0;
  assign LsuPlugin_logic_onAddress0_flush_port_fire = (LsuPlugin_logic_onAddress0_flush_port_valid && LsuPlugin_logic_onAddress0_flush_port_ready);
  assign LsuPlugin_logic_onAddress0_ls_port_ready = LsuPlugin_logic_onAddress0_arbiter_io_inputs_0_ready;
  assign LsuPlugin_logic_onAddress0_flush_port_ready = LsuPlugin_logic_onAddress0_arbiter_io_inputs_1_ready;
  assign LsuPlugin_logic_onAddress0_arbiter_io_output_ready = (! execute_freeze_valid);
  assign execute_ctrl2_down_LsuL1_SEL_lane0 = LsuPlugin_logic_onAddress0_arbiter_io_output_valid;
  assign execute_ctrl2_down_LsuL1_MIXED_ADDRESS_lane0 = LsuPlugin_logic_onAddress0_arbiter_io_output_payload_address;
  always @(*) begin
    _zz_execute_ctrl2_down_LsuL1_MASK_lane0 = 4'bxxxx;
    case(LsuPlugin_logic_onAddress0_arbiter_io_output_payload_size)
      2'b00 : begin
        _zz_execute_ctrl2_down_LsuL1_MASK_lane0 = 4'b0001;
      end
      2'b01 : begin
        _zz_execute_ctrl2_down_LsuL1_MASK_lane0 = 4'b0011;
      end
      2'b10 : begin
        _zz_execute_ctrl2_down_LsuL1_MASK_lane0 = 4'b1111;
      end
      default : begin
      end
    endcase
  end

  assign execute_ctrl2_down_LsuL1_MASK_lane0 = (_zz_execute_ctrl2_down_LsuL1_MASK_lane0 <<< LsuPlugin_logic_onAddress0_arbiter_io_output_payload_address[1 : 0]);
  assign execute_ctrl2_down_LsuL1_SIZE_lane0 = LsuPlugin_logic_onAddress0_arbiter_io_output_payload_size;
  assign execute_ctrl2_down_LsuL1_LOAD_lane0 = LsuPlugin_logic_onAddress0_arbiter_io_output_payload_load;
  assign execute_ctrl2_down_LsuL1_ATOMIC_lane0 = LsuPlugin_logic_onAddress0_arbiter_io_output_payload_atomic;
  assign execute_ctrl2_down_LsuL1_STORE_lane0 = LsuPlugin_logic_onAddress0_arbiter_io_output_payload_store;
  assign execute_ctrl2_down_LsuL1_CLEAN_lane0 = LsuPlugin_logic_onAddress0_arbiter_io_output_payload_clean;
  assign execute_ctrl2_down_LsuL1_INVALID_lane0 = LsuPlugin_logic_onAddress0_arbiter_io_output_payload_invalidate;
  assign execute_ctrl2_down_LsuL1_PREFETCH_lane0 = (LsuPlugin_logic_onAddress0_arbiter_io_output_payload_op == LsuL1CmdOpcode_PREFETCH);
  assign execute_ctrl2_down_LsuL1_FLUSH_lane0 = (LsuPlugin_logic_onAddress0_arbiter_io_output_payload_op == LsuL1CmdOpcode_FLUSH);
  assign execute_ctrl2_down_Decode_STORE_ID_lane0 = LsuPlugin_logic_onAddress0_arbiter_io_output_payload_storeId;
  assign execute_ctrl2_down_LsuPlugin_logic_FROM_ACCESS_lane0 = (LsuPlugin_logic_onAddress0_arbiter_io_output_payload_op == LsuL1CmdOpcode_ACCESS_1);
  assign execute_ctrl2_down_LsuPlugin_logic_FROM_WB_lane0 = (LsuPlugin_logic_onAddress0_arbiter_io_output_payload_op == LsuL1CmdOpcode_STORE_BUFFER);
  assign execute_ctrl2_down_LsuPlugin_logic_FROM_LSU_lane0 = (LsuPlugin_logic_onAddress0_arbiter_io_output_payload_op == LsuL1CmdOpcode_LSU);
  assign execute_ctrl2_down_LsuPlugin_logic_FROM_PREFETCH_lane0 = (LsuPlugin_logic_onAddress0_arbiter_io_output_payload_op == LsuL1CmdOpcode_PREFETCH);
  assign execute_ctrl3_down_LsuL1_PHYSICAL_ADDRESS_lane0 = execute_ctrl3_down_MMU_TRANSLATED_lane0;
  assign when_LsuPlugin_l546 = (execute_ctrl3_down_LsuPlugin_logic_FROM_LSU_lane0 && (! execute_ctrl3_up_LANE_SEL_lane0));
  assign when_LsuPlugin_l546_1 = (execute_ctrl4_down_LsuPlugin_logic_FROM_LSU_lane0 && (! execute_ctrl4_up_LANE_SEL_lane0));
  assign execute_ctrl3_down_LsuPlugin_logic_preCtrl_MISS_ALIGNED_lane0 = (|{((execute_ctrl3_down_LsuL1_SIZE_lane0 == 2'b10) && (execute_ctrl3_down_LsuL1_MIXED_ADDRESS_lane0[1 : 0] != 2'b00)),((execute_ctrl3_down_LsuL1_SIZE_lane0 == 2'b01) && (execute_ctrl3_down_LsuL1_MIXED_ADDRESS_lane0[0 : 0] != 1'b0))});
  assign execute_ctrl3_down_LsuPlugin_logic_preCtrl_IS_AMO_lane0 = (((execute_ctrl3_down_AguPlugin_SEL_lane0 && execute_ctrl3_down_LsuL1_ATOMIC_lane0) && execute_ctrl3_down_LsuL1_STORE_lane0) && execute_ctrl3_down_LsuL1_LOAD_lane0);
  assign LsuPlugin_logic_onPma_cached_cmd_address = execute_ctrl3_down_MMU_TRANSLATED_lane0;
  assign LsuPlugin_logic_onPma_cached_cmd_op[0] = execute_ctrl3_down_LsuL1_STORE_lane0;
  assign LsuPlugin_logic_onPma_io_cmd_address = execute_ctrl3_down_MMU_TRANSLATED_lane0;
  assign LsuPlugin_logic_onPma_io_cmd_size = execute_ctrl3_down_LsuL1_SIZE_lane0;
  assign LsuPlugin_logic_onPma_io_cmd_op[0] = execute_ctrl3_down_LsuL1_STORE_lane0;
  assign execute_ctrl3_down_LsuPlugin_logic_onPma_CACHED_RSP_lane0_fault = LsuPlugin_logic_onPma_cached_rsp_fault;
  assign execute_ctrl3_down_LsuPlugin_logic_onPma_CACHED_RSP_lane0_io = LsuPlugin_logic_onPma_cached_rsp_io;
  always @(*) begin
    execute_ctrl3_down_LsuPlugin_logic_onPma_IO_RSP_lane0_fault = LsuPlugin_logic_onPma_io_rsp_fault;
    if(when_LsuPlugin_l569) begin
      execute_ctrl3_down_LsuPlugin_logic_onPma_IO_RSP_lane0_fault = 1'b1;
    end
  end

  assign execute_ctrl3_down_LsuPlugin_logic_onPma_IO_RSP_lane0_io = LsuPlugin_logic_onPma_io_rsp_io;
  assign when_LsuPlugin_l569 = (execute_ctrl3_down_LsuL1_ATOMIC_lane0 || execute_ctrl3_down_LsuPlugin_logic_FROM_ACCESS_lane0);
  assign execute_ctrl3_down_LsuPlugin_logic_onPma_IO_lane0 = (((execute_ctrl3_down_LsuPlugin_logic_onPma_CACHED_RSP_lane0_fault && (! execute_ctrl3_down_LsuPlugin_logic_onPma_IO_RSP_lane0_fault)) && (! execute_ctrl3_down_LsuPlugin_logic_FENCE_lane0)) && (! execute_ctrl3_down_LsuPlugin_logic_FROM_PREFETCH_lane0));
  assign LsuPlugin_logic_onPma_addressExtension = 1'b0;
  assign execute_ctrl3_down_LsuPlugin_logic_onPma_FROM_LSU_MSB_FAILED_lane0 = (execute_ctrl3_down_LsuPlugin_logic_FROM_LSU_lane0 && 1'b0);
  assign execute_ctrl3_down_LsuPlugin_logic_MMU_PAGE_FAULT_lane0 = (execute_ctrl3_down_MMU_PAGE_FAULT_lane0 || (execute_ctrl3_down_AguPlugin_STORE_lane0 ? (! execute_ctrl3_down_MMU_ALLOW_WRITE_lane0) : (! execute_ctrl3_down_MMU_ALLOW_READ_lane0)));
  assign execute_ctrl3_down_LsuPlugin_logic_MMU_FAILURE_lane0 = ((((execute_ctrl3_down_LsuPlugin_logic_MMU_PAGE_FAULT_lane0 || execute_ctrl3_down_MMU_ACCESS_FAULT_lane0) || execute_ctrl3_down_MMU_REFILL_lane0) || execute_ctrl3_down_MMU_HAZARD_lane0) || execute_ctrl3_down_LsuPlugin_logic_onPma_FROM_LSU_MSB_FAILED_lane0);
  always @(*) begin
    LsuPlugin_logic_onCtrl_lsuTrap = 1'b0;
    if(LsuPlugin_logic_onCtrl_traps_accessFault) begin
      LsuPlugin_logic_onCtrl_lsuTrap = 1'b1;
    end
    if(LsuPlugin_logic_onCtrl_traps_l1Failed) begin
      LsuPlugin_logic_onCtrl_lsuTrap = 1'b1;
    end
    if(LsuPlugin_logic_onCtrl_traps_pmaFault) begin
      LsuPlugin_logic_onCtrl_lsuTrap = 1'b1;
    end
    if(execute_ctrl4_down_LsuPlugin_logic_MMU_PAGE_FAULT_lane0) begin
      LsuPlugin_logic_onCtrl_lsuTrap = 1'b1;
    end
    if(execute_ctrl4_down_MMU_ACCESS_FAULT_lane0) begin
      LsuPlugin_logic_onCtrl_lsuTrap = 1'b1;
    end
    if(execute_ctrl4_down_MMU_REFILL_lane0) begin
      LsuPlugin_logic_onCtrl_lsuTrap = 1'b1;
    end
    if(execute_ctrl4_down_MMU_HAZARD_lane0) begin
      LsuPlugin_logic_onCtrl_lsuTrap = 1'b1;
    end
    if(execute_ctrl4_down_LsuPlugin_logic_onPma_FROM_LSU_MSB_FAILED_lane0) begin
      LsuPlugin_logic_onCtrl_lsuTrap = 1'b1;
    end
    if(execute_ctrl4_down_LsuPlugin_logic_preCtrl_MISS_ALIGNED_lane0) begin
      LsuPlugin_logic_onCtrl_lsuTrap = 1'b1;
    end
    if(execute_ctrl4_down_LsuPlugin_logic_onTrigger_HIT_lane0) begin
      LsuPlugin_logic_onCtrl_lsuTrap = 1'b1;
    end
    if(when_LsuPlugin_l831) begin
      LsuPlugin_logic_onCtrl_lsuTrap = 1'b0;
    end
  end

  always @(*) begin
    LsuPlugin_logic_onCtrl_writeData = 32'bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx;
    LsuPlugin_logic_onCtrl_writeData[31 : 0] = execute_ctrl4_up_integer_RS2_lane0;
  end

  assign when_LsuPlugin_l595 = (((((! LsuPlugin_logic_onCtrl_lsuTrap) && (! execute_lane0_ctrls_4_upIsCancel)) && execute_ctrl4_down_LsuPlugin_logic_FROM_LSU_lane0) && (! execute_ctrl4_down_LsuL1_CLEAN_lane0)) && (! execute_ctrl4_down_LsuL1_INVALID_lane0));
  assign LsuPlugin_logic_onCtrl_io_doIt = ((execute_ctrl4_up_LANE_SEL_lane0 && execute_ctrl4_down_LsuL1_SEL_lane0) && execute_ctrl4_down_LsuPlugin_logic_onPma_IO_lane0);
  assign LsuPlugin_logic_bus_cmd_fire = (LsuPlugin_logic_bus_cmd_valid && LsuPlugin_logic_bus_cmd_ready);
  assign when_LsuPlugin_l599 = (! execute_freeze_valid);
  assign LsuPlugin_logic_bus_cmd_valid = (((LsuPlugin_logic_onCtrl_io_doItReg && (! LsuPlugin_logic_onCtrl_io_cmdSent)) && LsuPlugin_logic_onCtrl_io_allowIt) && (! LsuPlugin_logic_onCtrl_io_tooEarly));
  assign LsuPlugin_logic_bus_cmd_payload_write = execute_ctrl4_down_LsuL1_STORE_lane0;
  assign LsuPlugin_logic_bus_cmd_payload_address = execute_ctrl4_down_LsuL1_PHYSICAL_ADDRESS_lane0;
  assign LsuPlugin_logic_bus_cmd_payload_data = execute_ctrl4_down_LsuL1_WRITE_DATA_lane0;
  assign LsuPlugin_logic_bus_cmd_payload_size = execute_ctrl4_down_LsuL1_SIZE_lane0;
  assign LsuPlugin_logic_bus_cmd_payload_mask = execute_ctrl4_down_LsuL1_MASK_lane0;
  assign LsuPlugin_logic_bus_cmd_payload_io = 1'b1;
  assign LsuPlugin_logic_bus_cmd_payload_fromHart = 1'b1;
  assign LsuPlugin_logic_bus_cmd_payload_uopId = execute_ctrl4_down_Decode_UOP_ID_lane0;
  assign LsuPlugin_logic_bus_rsp_toStream_valid = LsuPlugin_logic_bus_rsp_valid;
  assign LsuPlugin_logic_bus_rsp_toStream_payload_error = LsuPlugin_logic_bus_rsp_payload_error;
  assign LsuPlugin_logic_bus_rsp_toStream_payload_data = LsuPlugin_logic_bus_rsp_payload_data;
  assign LsuPlugin_logic_onCtrl_io_rsp_fire = (LsuPlugin_logic_onCtrl_io_rsp_valid && LsuPlugin_logic_onCtrl_io_rsp_ready);
  assign LsuPlugin_logic_bus_rsp_toStream_ready = (! LsuPlugin_logic_bus_rsp_toStream_rValid);
  assign LsuPlugin_logic_onCtrl_io_rsp_valid = LsuPlugin_logic_bus_rsp_toStream_rValid;
  assign LsuPlugin_logic_onCtrl_io_rsp_payload_error = LsuPlugin_logic_bus_rsp_toStream_rData_error;
  assign LsuPlugin_logic_onCtrl_io_rsp_payload_data = LsuPlugin_logic_bus_rsp_toStream_rData_data;
  assign LsuPlugin_logic_onCtrl_io_rsp_ready = (! execute_freeze_valid);
  assign LsuPlugin_logic_onCtrl_io_freezeIt = (LsuPlugin_logic_onCtrl_io_doIt && (LsuPlugin_logic_onCtrl_io_tooEarly || ((! LsuPlugin_logic_onCtrl_io_rsp_valid) && LsuPlugin_logic_onCtrl_io_allowIt)));
  assign LsuPlugin_logic_onCtrl_loadData_input = (LsuPlugin_logic_onCtrl_io_cmdSent ? LsuPlugin_logic_onCtrl_io_rsp_payload_data : execute_ctrl4_down_LsuL1_READ_DATA_lane0);
  assign LsuPlugin_logic_onCtrl_loadData_splited_0 = LsuPlugin_logic_onCtrl_loadData_input[7 : 0];
  assign LsuPlugin_logic_onCtrl_loadData_splited_1 = LsuPlugin_logic_onCtrl_loadData_input[15 : 8];
  assign LsuPlugin_logic_onCtrl_loadData_splited_2 = LsuPlugin_logic_onCtrl_loadData_input[23 : 16];
  assign LsuPlugin_logic_onCtrl_loadData_splited_3 = LsuPlugin_logic_onCtrl_loadData_input[31 : 24];
  always @(*) begin
    LsuPlugin_logic_onCtrl_loadData_shited[7 : 0] = _zz_LsuPlugin_logic_onCtrl_loadData_shited;
    LsuPlugin_logic_onCtrl_loadData_shited[15 : 8] = _zz_LsuPlugin_logic_onCtrl_loadData_shited_2;
    LsuPlugin_logic_onCtrl_loadData_shited[23 : 16] = LsuPlugin_logic_onCtrl_loadData_splited_2;
    LsuPlugin_logic_onCtrl_loadData_shited[31 : 24] = LsuPlugin_logic_onCtrl_loadData_splited_3;
  end

  assign execute_ctrl4_down_LsuPlugin_logic_onCtrl_loadData_RESULT_lane0 = LsuPlugin_logic_onCtrl_loadData_shited;
  assign LsuPlugin_logic_onCtrl_storeData_mapping_0_1 = {4{LsuPlugin_logic_onCtrl_writeData[7 : 0]}};
  assign LsuPlugin_logic_onCtrl_storeData_mapping_1_1 = {2{LsuPlugin_logic_onCtrl_writeData[15 : 0]}};
  assign LsuPlugin_logic_onCtrl_storeData_mapping_2_1 = {1{LsuPlugin_logic_onCtrl_writeData[31 : 0]}};
  always @(*) begin
    _zz_execute_ctrl4_down_LsuL1_WRITE_DATA_lane0 = 32'bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx;
    case(execute_ctrl4_down_LsuL1_SIZE_lane0)
      2'b00 : begin
        _zz_execute_ctrl4_down_LsuL1_WRITE_DATA_lane0 = LsuPlugin_logic_onCtrl_storeData_mapping_0_1;
      end
      2'b01 : begin
        _zz_execute_ctrl4_down_LsuL1_WRITE_DATA_lane0 = LsuPlugin_logic_onCtrl_storeData_mapping_1_1;
      end
      2'b10 : begin
        _zz_execute_ctrl4_down_LsuL1_WRITE_DATA_lane0 = LsuPlugin_logic_onCtrl_storeData_mapping_2_1;
      end
      default : begin
      end
    endcase
  end

  assign execute_ctrl4_down_LsuL1_WRITE_DATA_lane0 = _zz_execute_ctrl4_down_LsuL1_WRITE_DATA_lane0;
  assign execute_ctrl4_down_LsuPlugin_logic_onCtrl_SC_MISS_lane0 = LsuPlugin_logic_onCtrl_scMiss;
  assign LsuPlugin_logic_onCtrl_scMiss = 1'b0;
  assign LsuL1_lockPort_valid = 1'b0;
  assign LsuL1_lockPort_address = 32'h0;
  always @(*) begin
    LsuPlugin_logic_flushPort_valid = 1'b0;
    if(when_LsuPlugin_l859) begin
      if(LsuPlugin_logic_onCtrl_lsuTrap) begin
        LsuPlugin_logic_flushPort_valid = 1'b1;
      end
    end
  end

  assign LsuPlugin_logic_flushPort_payload_uopId = execute_ctrl4_down_Decode_UOP_ID_lane0;
  assign LsuPlugin_logic_flushPort_payload_self = 1'b0;
  always @(*) begin
    LsuPlugin_logic_trapPort_valid = 1'b0;
    if(when_LsuPlugin_l859) begin
      if(LsuPlugin_logic_onCtrl_lsuTrap) begin
        LsuPlugin_logic_trapPort_valid = 1'b1;
      end
    end
  end

  assign LsuPlugin_logic_trapPort_payload_tval = execute_ctrl4_down_LsuL1_MIXED_ADDRESS_lane0;
  always @(*) begin
    LsuPlugin_logic_trapPort_payload_exception = 1'bx;
    if(LsuPlugin_logic_onCtrl_traps_accessFault) begin
      LsuPlugin_logic_trapPort_payload_exception = 1'b1;
    end
    if(LsuPlugin_logic_onCtrl_traps_l1Failed) begin
      LsuPlugin_logic_trapPort_payload_exception = 1'b0;
    end
    if(LsuPlugin_logic_onCtrl_traps_pmaFault) begin
      LsuPlugin_logic_trapPort_payload_exception = 1'b1;
    end
    if(execute_ctrl4_down_LsuPlugin_logic_MMU_PAGE_FAULT_lane0) begin
      LsuPlugin_logic_trapPort_payload_exception = 1'b1;
    end
    if(execute_ctrl4_down_MMU_ACCESS_FAULT_lane0) begin
      LsuPlugin_logic_trapPort_payload_exception = 1'b1;
    end
    if(execute_ctrl4_down_MMU_REFILL_lane0) begin
      LsuPlugin_logic_trapPort_payload_exception = 1'b0;
    end
    if(execute_ctrl4_down_MMU_HAZARD_lane0) begin
      LsuPlugin_logic_trapPort_payload_exception = 1'b0;
    end
    if(execute_ctrl4_down_LsuPlugin_logic_onPma_FROM_LSU_MSB_FAILED_lane0) begin
      LsuPlugin_logic_trapPort_payload_exception = 1'b1;
    end
    if(execute_ctrl4_down_LsuPlugin_logic_preCtrl_MISS_ALIGNED_lane0) begin
      LsuPlugin_logic_trapPort_payload_exception = 1'b1;
    end
    if(execute_ctrl4_down_LsuPlugin_logic_onTrigger_HIT_lane0) begin
      LsuPlugin_logic_trapPort_payload_exception = 1'b0;
    end
  end

  always @(*) begin
    LsuPlugin_logic_trapPort_payload_code = 4'bxxxx;
    if(LsuPlugin_logic_onCtrl_traps_accessFault) begin
      LsuPlugin_logic_trapPort_payload_code = 4'b0101;
      if(execute_ctrl4_down_LsuL1_STORE_lane0) begin
        LsuPlugin_logic_trapPort_payload_code[1] = 1'b1;
      end
    end
    if(LsuPlugin_logic_onCtrl_traps_l1Failed) begin
      LsuPlugin_logic_trapPort_payload_code = 4'b0100;
    end
    if(LsuPlugin_logic_onCtrl_traps_pmaFault) begin
      LsuPlugin_logic_trapPort_payload_code = 4'b0101;
      if(execute_ctrl4_down_LsuL1_STORE_lane0) begin
        LsuPlugin_logic_trapPort_payload_code[1] = 1'b1;
      end
    end
    if(execute_ctrl4_down_LsuPlugin_logic_MMU_PAGE_FAULT_lane0) begin
      LsuPlugin_logic_trapPort_payload_code = 4'b1101;
      if(execute_ctrl4_down_LsuL1_STORE_lane0) begin
        LsuPlugin_logic_trapPort_payload_code[1] = 1'b1;
      end
    end
    if(execute_ctrl4_down_MMU_ACCESS_FAULT_lane0) begin
      LsuPlugin_logic_trapPort_payload_code = 4'b0101;
      if(execute_ctrl4_down_LsuL1_STORE_lane0) begin
        LsuPlugin_logic_trapPort_payload_code[1] = 1'b1;
      end
    end
    if(execute_ctrl4_down_MMU_REFILL_lane0) begin
      LsuPlugin_logic_trapPort_payload_code = 4'b0111;
    end
    if(execute_ctrl4_down_MMU_HAZARD_lane0) begin
      LsuPlugin_logic_trapPort_payload_code = 4'b0100;
    end
    if(execute_ctrl4_down_LsuPlugin_logic_onPma_FROM_LSU_MSB_FAILED_lane0) begin
      LsuPlugin_logic_trapPort_payload_code = 4'b0101;
      if(execute_ctrl4_down_AguPlugin_STORE_lane0) begin
        LsuPlugin_logic_trapPort_payload_code[1] = 1'b1;
      end
      if(when_LsuPlugin_l804) begin
        LsuPlugin_logic_trapPort_payload_code[3] = 1'b1;
      end
    end
    if(execute_ctrl4_down_LsuPlugin_logic_preCtrl_MISS_ALIGNED_lane0) begin
      LsuPlugin_logic_trapPort_payload_code = {1'd0, _zz_LsuPlugin_logic_trapPort_payload_code};
    end
    if(execute_ctrl4_down_LsuPlugin_logic_onTrigger_HIT_lane0) begin
      LsuPlugin_logic_trapPort_payload_code = 4'b0011;
    end
  end

  always @(*) begin
    LsuPlugin_logic_trapPort_payload_arg = 2'b00;
    LsuPlugin_logic_trapPort_payload_arg[1 : 0] = (execute_ctrl4_down_LsuL1_STORE_lane0 ? 2'b01 : 2'b00);
  end

  assign LsuPlugin_logic_onCtrl_traps_accessFault = ((execute_ctrl4_down_LsuPlugin_logic_onPma_CACHED_RSP_lane0_fault ? (LsuPlugin_logic_onCtrl_io_rsp_valid && LsuPlugin_logic_onCtrl_io_rsp_payload_error) : execute_ctrl4_down_LsuL1_FAULT_lane0) || execute_ctrl4_down_LsuPlugin_logic_pmpPort_ACCESS_FAULT_lane0);
  assign LsuPlugin_logic_onCtrl_traps_l1Failed = ((! execute_ctrl4_down_LsuPlugin_logic_onPma_CACHED_RSP_lane0_fault) && (execute_ctrl4_down_LsuL1_HAZARD_lane0 || ((execute_ctrl4_down_LsuL1_MISS_lane0 || execute_ctrl4_down_LsuL1_MISS_UNIQUE_lane0) && (execute_ctrl4_down_LsuL1_LOAD_lane0 || execute_ctrl4_down_LsuL1_STORE_lane0))));
  assign LsuPlugin_logic_onCtrl_traps_pmaFault = (execute_ctrl4_down_LsuPlugin_logic_onPma_CACHED_RSP_lane0_fault && execute_ctrl4_down_LsuPlugin_logic_onPma_IO_RSP_lane0_fault);
  assign when_LsuPlugin_l804 = (! execute_ctrl4_down_MMU_BYPASS_TRANSLATION_lane0);
  assign when_LsuPlugin_l831 = (execute_ctrl4_down_LsuPlugin_logic_FENCE_lane0 || execute_ctrl4_down_LsuPlugin_logic_FROM_PREFETCH_lane0);
  assign when_LsuPlugin_l859 = (execute_ctrl4_up_LANE_SEL_lane0 && execute_ctrl4_down_AguPlugin_SEL_lane0);
  assign LsuPlugin_logic_onCtrl_mmuNeeded = (execute_ctrl4_down_LsuPlugin_logic_FROM_LSU_lane0 || execute_ctrl4_down_LsuPlugin_logic_FROM_PREFETCH_lane0);
  assign execute_ctrl4_down_LsuL1_ABORD_lane0 = (|{(LsuPlugin_logic_onCtrl_mmuNeeded && execute_ctrl4_down_LsuPlugin_logic_MMU_FAILURE_lane0),{(execute_ctrl4_down_LsuPlugin_logic_FROM_LSU_lane0 && (((! execute_ctrl4_up_LANE_SEL_lane0) || execute_lane0_ctrls_4_upIsCancel) || execute_ctrl4_down_LsuPlugin_logic_FENCE_lane0)),{((! execute_ctrl4_down_LsuL1_FLUSH_lane0) && execute_ctrl4_down_LsuPlugin_logic_onPma_CACHED_RSP_lane0_fault),{execute_ctrl4_down_LsuL1_FLUSH_HAZARD_lane0,execute_ctrl4_down_LsuL1_HAZARD_lane0}}}});
  assign execute_ctrl4_down_LsuL1_SKIP_WRITE_lane0 = (|{execute_ctrl4_down_LsuPlugin_logic_FROM_PREFETCH_lane0,{(execute_ctrl4_down_LsuPlugin_logic_FROM_LSU_lane0 && (execute_ctrl4_down_LsuPlugin_logic_onTrigger_HIT_lane0 || execute_ctrl4_down_LsuPlugin_logic_pmpPort_ACCESS_FAULT_lane0)),{execute_ctrl4_down_LsuPlugin_logic_preCtrl_MISS_ALIGNED_lane0,{execute_ctrl4_down_LsuL1_FAULT_lane0,(execute_ctrl4_down_LsuL1_MISS_lane0 || execute_ctrl4_down_LsuL1_MISS_UNIQUE_lane0)}}}});
  assign when_LsuPlugin_l899 = ((execute_ctrl4_down_LsuL1_SEL_lane0 && execute_ctrl4_down_LsuL1_FLUSH_lane0) && ((execute_ctrl4_down_LsuL1_FLUSH_HIT_lane0 || execute_ctrl4_down_LsuL1_HAZARD_lane0) || execute_ctrl4_down_LsuL1_FLUSH_HAZARD_lane0));
  assign when_LsuPlugin_l259 = (|(LsuPlugin_logic_onCtrl_hartRegulation_refill & (~ LsuL1_REFILL_BUSY)));
  assign when_LsuPlugin_l943 = ((((((execute_ctrl4_up_LANE_SEL_lane0 && execute_ctrl4_down_AguPlugin_SEL_lane0) && (! execute_ctrl4_down_LsuPlugin_logic_FROM_PREFETCH_lane0)) && (! execute_ctrl4_down_LsuPlugin_logic_onPma_IO_lane0)) && (! execute_ctrl4_down_LsuPlugin_logic_FENCE_lane0)) && 1'b1) && ((execute_ctrl4_down_LsuL1_HAZARD_lane0 || execute_ctrl4_down_LsuL1_MISS_lane0) || execute_ctrl4_down_LsuL1_MISS_UNIQUE_lane0));
  assign when_LsuPlugin_l263 = (|execute_ctrl4_down_LsuL1_WAIT_REFILL_lane0);
  assign LsuPlugin_logic_commitProbe_valid = (((execute_ctrl4_down_LANE_SEL_lane0 && execute_ctrl4_down_isReady) && (! execute_lane0_ctrls_4_downIsCancel)) && (execute_ctrl4_down_AguPlugin_SEL_lane0 ? execute_ctrl4_down_LsuPlugin_logic_FROM_LSU_lane0 : (execute_ctrl4_down_LsuPlugin_logic_FROM_PREFETCH_lane0 && execute_ctrl4_down_LsuL1_HAZARD_lane0)));
  assign LsuPlugin_logic_commitProbe_payload_address = execute_ctrl4_down_LsuL1_MIXED_ADDRESS_lane0;
  assign LsuPlugin_logic_commitProbe_payload_load = execute_ctrl4_down_LsuL1_LOAD_lane0;
  assign LsuPlugin_logic_commitProbe_payload_store = execute_ctrl4_down_LsuL1_STORE_lane0;
  assign LsuPlugin_logic_commitProbe_payload_trap = LsuPlugin_logic_onCtrl_lsuTrap;
  assign LsuPlugin_logic_commitProbe_payload_miss = ((execute_ctrl4_down_LsuL1_MISS_lane0 && (! execute_ctrl4_down_LsuL1_HAZARD_lane0)) && (! execute_ctrl4_down_LsuPlugin_logic_MMU_FAILURE_lane0));
  assign LsuPlugin_logic_commitProbe_payload_io = execute_ctrl4_down_LsuPlugin_logic_onPma_IO_lane0;
  assign LsuPlugin_logic_commitProbe_payload_prefetchFailed = execute_ctrl4_down_LsuPlugin_logic_FROM_PREFETCH_lane0;
  assign LsuPlugin_logic_commitProbe_payload_pc = execute_ctrl4_down_PC_lane0;
  assign LsuPlugin_logic_iwb_valid = (execute_ctrl4_down_AguPlugin_SEL_lane0 && (! execute_ctrl4_down_AguPlugin_FLOAT_lane0));
  assign LsuPlugin_logic_iwb_payload = execute_ctrl4_down_LsuPlugin_logic_onCtrl_loadData_RESULT_lane0;
  assign LsuPlugin_logic_onWb_storeFire = ((((((execute_ctrl4_down_LANE_SEL_lane0 && execute_ctrl4_down_isReady) && (! execute_lane0_ctrls_4_downIsCancel)) && execute_ctrl4_down_AguPlugin_SEL_lane0) && execute_ctrl4_down_LsuL1_STORE_lane0) && (! execute_ctrl4_down_LsuPlugin_logic_onPma_IO_lane0)) && (! execute_ctrl4_down_LsuPlugin_logic_FROM_PREFETCH_lane0));
  assign LsuPlugin_logic_onWb_storeBroadcast = (((((((execute_ctrl4_down_isReady && execute_ctrl4_down_LsuL1_SEL_lane0) && execute_ctrl4_down_LsuL1_STORE_lane0) && (! execute_ctrl4_down_LsuL1_ABORD_lane0)) && (! execute_ctrl4_down_LsuL1_SKIP_WRITE_lane0)) && (! execute_ctrl4_down_LsuL1_MISS_lane0)) && (! execute_ctrl4_down_LsuL1_MISS_UNIQUE_lane0)) && (! execute_ctrl4_down_LsuL1_HAZARD_lane0));
  assign execute_ctrl2_down_early0_BranchPlugin_logic_alu_EQ_lane0 = ($signed(execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0) == $signed(execute_ctrl2_down_early0_SrcPlugin_SRC2_lane0));
  assign execute_ctrl2_down_early0_BranchPlugin_logic_alu_btb_BAD_TARGET_lane0 = (execute_ctrl2_down_Prediction_ALIGNED_JUMPED_PC_lane0 != execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_TRUE_lane0);
  assign early0_BranchPlugin_logic_alu_expectedMsb = 1'b0;
  assign execute_ctrl2_down_early0_BranchPlugin_logic_alu_MSB_FAILED_lane0 = ((execute_ctrl2_down_BranchPlugin_BRANCH_CTRL_lane0 == BranchPlugin_BranchCtrlEnum_JALR) && 1'b0);
  assign switch_Misc_l242 = execute_ctrl2_down_Decode_UOP_lane0[14 : 12];
  always @(*) begin
    casez(switch_Misc_l242)
      3'b000 : begin
        _zz_execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_COND_lane0 = execute_ctrl2_down_early0_BranchPlugin_logic_alu_EQ_lane0;
      end
      3'b001 : begin
        _zz_execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_COND_lane0 = (! execute_ctrl2_down_early0_BranchPlugin_logic_alu_EQ_lane0);
      end
      3'b1?1 : begin
        _zz_execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_COND_lane0 = (! execute_ctrl2_down_early0_SrcPlugin_LESS_lane0);
      end
      default : begin
        _zz_execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_COND_lane0 = execute_ctrl2_down_early0_SrcPlugin_LESS_lane0;
      end
    endcase
  end

  always @(*) begin
    case(execute_ctrl2_down_BranchPlugin_BRANCH_CTRL_lane0)
      BranchPlugin_BranchCtrlEnum_JALR : begin
        _zz_execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_COND_lane0_1 = 1'b1;
      end
      BranchPlugin_BranchCtrlEnum_JAL : begin
        _zz_execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_COND_lane0_1 = 1'b1;
      end
      default : begin
        _zz_execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_COND_lane0_1 = _zz_execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_COND_lane0;
      end
    endcase
  end

  assign execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_COND_lane0 = _zz_execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_COND_lane0_1;
  assign execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_btb_REAL_TARGET_lane0 = (execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_COND_lane0 ? execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_TRUE_lane0 : execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_FALSE_lane0);
  assign early0_BranchPlugin_logic_jumpLogic_wrongCond = (execute_ctrl2_down_Prediction_ALIGNED_JUMPED_lane0 != execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_COND_lane0);
  assign early0_BranchPlugin_logic_jumpLogic_needFix = ((early0_BranchPlugin_logic_jumpLogic_wrongCond || (execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_COND_lane0 && execute_ctrl2_down_early0_BranchPlugin_logic_alu_btb_BAD_TARGET_lane0)) || execute_ctrl2_down_early0_BranchPlugin_logic_alu_MSB_FAILED_lane0);
  assign early0_BranchPlugin_logic_jumpLogic_doIt = ((execute_ctrl2_up_LANE_SEL_lane0 && execute_ctrl2_down_early0_BranchPlugin_SEL_lane0) && early0_BranchPlugin_logic_jumpLogic_needFix);
  assign early0_BranchPlugin_logic_pcPort_valid = early0_BranchPlugin_logic_jumpLogic_doIt;
  assign early0_BranchPlugin_logic_pcPort_payload_fault = execute_ctrl2_down_early0_BranchPlugin_logic_alu_MSB_FAILED_lane0;
  assign early0_BranchPlugin_logic_pcPort_payload_pc = execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_btb_REAL_TARGET_lane0;
  assign early0_BranchPlugin_logic_flushPort_valid = early0_BranchPlugin_logic_jumpLogic_doIt;
  assign early0_BranchPlugin_logic_flushPort_payload_uopId = execute_ctrl2_down_Decode_UOP_ID_lane0;
  assign early0_BranchPlugin_logic_flushPort_payload_self = 1'b0;
  assign execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_MISSALIGNED_lane0 = ((execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_TRUE_lane0[1 : 0] != 2'b00) && execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_COND_lane0);
  always @(*) begin
    early0_BranchPlugin_logic_trapPort_valid = 1'b0;
    if(when_BranchPlugin_l251) begin
      early0_BranchPlugin_logic_trapPort_valid = 1'b1;
    end
  end

  assign early0_BranchPlugin_logic_trapPort_payload_exception = 1'b1;
  assign early0_BranchPlugin_logic_trapPort_payload_code = 4'b0000;
  assign early0_BranchPlugin_logic_trapPort_payload_tval = execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_TRUE_lane0;
  assign early0_BranchPlugin_logic_trapPort_payload_arg = 2'b00;
  assign when_BranchPlugin_l251 = (early0_BranchPlugin_logic_jumpLogic_doIt && execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_MISSALIGNED_lane0);
  assign execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_IS_JAL_lane0 = (execute_ctrl2_down_BranchPlugin_BRANCH_CTRL_lane0 == BranchPlugin_BranchCtrlEnum_JAL);
  assign execute_ctrl2_down_early0_BranchPlugin_logic_jumpLogic_IS_JALR_lane0 = (execute_ctrl2_down_BranchPlugin_BRANCH_CTRL_lane0 == BranchPlugin_BranchCtrlEnum_JALR);
  assign early0_BranchPlugin_logic_jumpLogic_rdLink = (|{(execute_ctrl2_down_Decode_UOP_lane0[11 : 7] == 5'h05),(execute_ctrl2_down_Decode_UOP_lane0[11 : 7] == 5'h01)});
  assign early0_BranchPlugin_logic_jumpLogic_rs1Link = (|{(execute_ctrl2_down_Decode_UOP_lane0[19 : 15] == 5'h05),(execute_ctrl2_down_Decode_UOP_lane0[19 : 15] == 5'h01)});
  assign early0_BranchPlugin_logic_jumpLogic_rdEquRs1 = (execute_ctrl2_down_Decode_UOP_lane0[11 : 7] == execute_ctrl2_down_Decode_UOP_lane0[19 : 15]);
  assign early0_BranchPlugin_logic_wb_valid = execute_ctrl2_down_early0_BranchPlugin_SEL_lane0;
  assign early0_BranchPlugin_logic_wb_payload = execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_FALSE_lane0;
  assign PmpPlugin_logic_isMachine = (PrivilegedPlugin_logic_harts_0_privilege == 2'b11);
  assign PmpPlugin_logic_instructionShouldHit = (! PmpPlugin_logic_isMachine);
  assign PmpPlugin_logic_dataShouldHit = ((! PmpPlugin_logic_isMachine) || (PrivilegedPlugin_logic_harts_0_m_status_mprv && (PrivilegedPlugin_logic_harts_0_m_status_mpp != 2'b11)));
  assign FetchL1Plugin_logic_pmpPort_logic_dataShouldHitPort = (PmpPlugin_logic_dataShouldHit || 1'b0);
  assign FetchL1Plugin_logic_pmpPort_logic_torCmpAddress = (fetch_logic_ctrls_1_down_MMU_TRANSLATED >>> 4'd12);
  assign fetch_logic_ctrls_0_down_FetchL1Plugin_logic_pmpPort_logic_NEED_HIT = ((PmpPlugin_logic_instructionShouldHit && 1'b1) || (FetchL1Plugin_logic_pmpPort_logic_dataShouldHitPort && (1'b0 || 1'b0)));
  assign fetch_logic_ctrls_2_down_FetchL1Plugin_logic_pmpPort_ACCESS_FAULT = 1'b0;
  assign LsuPlugin_logic_pmpPort_logic_dataShouldHitPort = (PmpPlugin_logic_dataShouldHit || execute_ctrl2_down_LsuPlugin_logic_FROM_ACCESS_lane0);
  assign LsuPlugin_logic_pmpPort_logic_torCmpAddress = (execute_ctrl3_down_MMU_TRANSLATED_lane0 >>> 4'd12);
  assign execute_ctrl2_down_LsuPlugin_logic_pmpPort_logic_NEED_HIT_lane0 = ((PmpPlugin_logic_instructionShouldHit && 1'b0) || (LsuPlugin_logic_pmpPort_logic_dataShouldHitPort && (execute_ctrl2_down_LsuL1_LOAD_lane0 || execute_ctrl2_down_LsuL1_STORE_lane0)));
  assign execute_ctrl4_down_LsuPlugin_logic_pmpPort_ACCESS_FAULT_lane0 = 1'b0;
  always @(*) begin
    LsuPlugin_logic_bus_cmd_ready = LsuCachelessWishbonePlugin_logic_bridge_cmdStage_ready;
    if(when_Stream_l399_2) begin
      LsuPlugin_logic_bus_cmd_ready = 1'b1;
    end
  end

  assign when_Stream_l399_2 = (! LsuCachelessWishbonePlugin_logic_bridge_cmdStage_valid);
  assign LsuCachelessWishbonePlugin_logic_bridge_cmdStage_valid = LsuPlugin_logic_bus_cmd_rValid;
  assign LsuCachelessWishbonePlugin_logic_bridge_cmdStage_payload_write = LsuPlugin_logic_bus_cmd_rData_write;
  assign LsuCachelessWishbonePlugin_logic_bridge_cmdStage_payload_address = LsuPlugin_logic_bus_cmd_rData_address;
  assign LsuCachelessWishbonePlugin_logic_bridge_cmdStage_payload_data = LsuPlugin_logic_bus_cmd_rData_data;
  assign LsuCachelessWishbonePlugin_logic_bridge_cmdStage_payload_size = LsuPlugin_logic_bus_cmd_rData_size;
  assign LsuCachelessWishbonePlugin_logic_bridge_cmdStage_payload_mask = LsuPlugin_logic_bus_cmd_rData_mask;
  assign LsuCachelessWishbonePlugin_logic_bridge_cmdStage_payload_io = LsuPlugin_logic_bus_cmd_rData_io;
  assign LsuCachelessWishbonePlugin_logic_bridge_cmdStage_payload_fromHart = LsuPlugin_logic_bus_cmd_rData_fromHart;
  assign LsuCachelessWishbonePlugin_logic_bridge_cmdStage_payload_uopId = LsuPlugin_logic_bus_cmd_rData_uopId;
  assign LsuCachelessWishbonePlugin_logic_bridge_down_ADR = (LsuCachelessWishbonePlugin_logic_bridge_cmdStage_payload_address >>> 2'd2);
  assign LsuCachelessWishbonePlugin_logic_bridge_down_CTI = 3'b000;
  assign LsuCachelessWishbonePlugin_logic_bridge_down_BTE = 2'b00;
  assign LsuCachelessWishbonePlugin_logic_bridge_down_SEL = LsuCachelessWishbonePlugin_logic_bridge_cmdStage_payload_mask;
  assign LsuCachelessWishbonePlugin_logic_bridge_down_WE = LsuCachelessWishbonePlugin_logic_bridge_cmdStage_payload_write;
  assign LsuCachelessWishbonePlugin_logic_bridge_down_DAT_MOSI = LsuCachelessWishbonePlugin_logic_bridge_cmdStage_payload_data;
  assign LsuCachelessWishbonePlugin_logic_bridge_cmdStage_ready = (LsuCachelessWishbonePlugin_logic_bridge_cmdStage_valid && (LsuCachelessWishbonePlugin_logic_bridge_down_ACK || LsuCachelessWishbonePlugin_logic_bridge_down_ERR));
  assign LsuCachelessWishbonePlugin_logic_bridge_down_CYC = LsuCachelessWishbonePlugin_logic_bridge_cmdStage_valid;
  assign LsuCachelessWishbonePlugin_logic_bridge_down_STB = LsuCachelessWishbonePlugin_logic_bridge_cmdStage_valid;
  assign LsuPlugin_logic_bus_rsp_valid = (LsuCachelessWishbonePlugin_logic_bridge_cmdStage_valid && (LsuCachelessWishbonePlugin_logic_bridge_down_ACK || LsuCachelessWishbonePlugin_logic_bridge_down_ERR));
  assign LsuPlugin_logic_bus_rsp_payload_data = LsuCachelessWishbonePlugin_logic_bridge_down_DAT_MISO;
  assign LsuPlugin_logic_bus_rsp_payload_error = LsuCachelessWishbonePlugin_logic_bridge_down_ERR;
  assign LsuPlugin_pmaBuilder_l1_addressBits = LsuPlugin_logic_onPma_cached_cmd_address;
  assign LsuPlugin_pmaBuilder_l1_argsBits = LsuPlugin_logic_onPma_cached_cmd_op;
  assign _zz_LsuPlugin_logic_onPma_cached_rsp_io = ((LsuPlugin_pmaBuilder_l1_addressBits & 32'h0) == 32'h0);
  assign LsuPlugin_pmaBuilder_l1_onTransfers_0_addressHit = _zz_LsuPlugin_pmaBuilder_l1_onTransfers_0_addressHit[0];
  assign LsuPlugin_pmaBuilder_l1_onTransfers_0_argsHit = (|((LsuPlugin_pmaBuilder_l1_argsBits & 1'b0) == 1'b0));
  assign LsuPlugin_pmaBuilder_l1_onTransfers_0_hit = (LsuPlugin_pmaBuilder_l1_onTransfers_0_argsHit && LsuPlugin_pmaBuilder_l1_onTransfers_0_addressHit);
  assign LsuPlugin_logic_onPma_cached_rsp_fault = (! ((|{((LsuPlugin_pmaBuilder_l1_addressBits & 32'hff000000) == 32'h10000000),{((LsuPlugin_pmaBuilder_l1_addressBits & 32'hff000000) == 32'h20000000),((LsuPlugin_pmaBuilder_l1_addressBits & 32'hffffe000) == 32'h0)}}) && (|LsuPlugin_pmaBuilder_l1_onTransfers_0_hit)));
  assign LsuPlugin_logic_onPma_cached_rsp_io = (! _zz_LsuPlugin_logic_onPma_cached_rsp_io_1[0]);
  assign LsuPlugin_pmaBuilder_io_addressBits = LsuPlugin_logic_onPma_io_cmd_address;
  assign LsuPlugin_pmaBuilder_io_argsBits = {LsuPlugin_logic_onPma_io_cmd_size,LsuPlugin_logic_onPma_io_cmd_op};
  assign LsuPlugin_pmaBuilder_io_onTransfers_0_addressHit = _zz_LsuPlugin_pmaBuilder_io_onTransfers_0_addressHit[0];
  assign LsuPlugin_pmaBuilder_io_onTransfers_0_argsHit = (|((LsuPlugin_pmaBuilder_io_argsBits & 3'b000) == 3'b000));
  assign LsuPlugin_pmaBuilder_io_onTransfers_0_hit = (LsuPlugin_pmaBuilder_io_onTransfers_0_argsHit && LsuPlugin_pmaBuilder_io_onTransfers_0_addressHit);
  assign LsuPlugin_logic_onPma_io_rsp_fault = (! ((|{((LsuPlugin_pmaBuilder_io_addressBits & 32'hff000000) == 32'h10000000),{((LsuPlugin_pmaBuilder_io_addressBits & 32'hff000000) == 32'h20000000),{((LsuPlugin_pmaBuilder_io_addressBits & _zz_LsuPlugin_logic_onPma_io_rsp_fault) == 32'hf0000000),((LsuPlugin_pmaBuilder_io_addressBits & _zz_LsuPlugin_logic_onPma_io_rsp_fault_1) == 32'h0)}}}) && (|LsuPlugin_pmaBuilder_io_onTransfers_0_hit)));
  assign LsuPlugin_logic_onPma_io_rsp_io = (! _zz_LsuPlugin_logic_onPma_io_rsp_io[0]);
  assign execute_ctrl2_COMPLETED_lane0_bypass = (execute_ctrl2_up_COMPLETED_lane0 || execute_ctrl2_down_COMPLETION_AT_2_lane0);
  assign execute_ctrl4_COMPLETED_lane0_bypass = (execute_ctrl4_up_COMPLETED_lane0 || execute_ctrl4_down_COMPLETION_AT_4_lane0);
  assign execute_ctrl3_COMPLETED_lane0_bypass = (execute_ctrl3_up_COMPLETED_lane0 || execute_ctrl3_down_COMPLETION_AT_3_lane0);
  assign execute_lane0_api_hartsInflight[0] = (|{(execute_ctrl4_up_LANE_SEL_lane0 && 1'b1),{(execute_ctrl3_up_LANE_SEL_lane0 && 1'b1),{(execute_ctrl2_up_LANE_SEL_lane0 && 1'b1),(execute_ctrl1_up_LANE_SEL_lane0 && 1'b1)}}});
  assign execute_ctrl4_down_late0_BranchPlugin_logic_alu_EQ_lane0 = ($signed(execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0) == $signed(execute_ctrl4_down_late0_SrcPlugin_SRC2_lane0));
  assign execute_ctrl4_down_late0_BranchPlugin_logic_alu_btb_BAD_TARGET_lane0 = (execute_ctrl4_down_Prediction_ALIGNED_JUMPED_PC_lane0 != execute_ctrl4_down_early0_BranchPlugin_pcCalc_PC_TRUE_lane0);
  assign late0_BranchPlugin_logic_alu_expectedMsb = 1'b0;
  assign execute_ctrl4_down_late0_BranchPlugin_logic_alu_MSB_FAILED_lane0 = ((execute_ctrl4_down_BranchPlugin_BRANCH_CTRL_lane0 == BranchPlugin_BranchCtrlEnum_JALR) && 1'b0);
  assign switch_Misc_l242_1 = execute_ctrl4_down_Decode_UOP_lane0[14 : 12];
  always @(*) begin
    casez(switch_Misc_l242_1)
      3'b000 : begin
        _zz_execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_COND_lane0 = execute_ctrl4_down_late0_BranchPlugin_logic_alu_EQ_lane0;
      end
      3'b001 : begin
        _zz_execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_COND_lane0 = (! execute_ctrl4_down_late0_BranchPlugin_logic_alu_EQ_lane0);
      end
      3'b1?1 : begin
        _zz_execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_COND_lane0 = (! execute_ctrl4_down_late0_SrcPlugin_LESS_lane0);
      end
      default : begin
        _zz_execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_COND_lane0 = execute_ctrl4_down_late0_SrcPlugin_LESS_lane0;
      end
    endcase
  end

  always @(*) begin
    case(execute_ctrl4_down_BranchPlugin_BRANCH_CTRL_lane0)
      BranchPlugin_BranchCtrlEnum_JALR : begin
        _zz_execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_COND_lane0_1 = 1'b1;
      end
      BranchPlugin_BranchCtrlEnum_JAL : begin
        _zz_execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_COND_lane0_1 = 1'b1;
      end
      default : begin
        _zz_execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_COND_lane0_1 = _zz_execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_COND_lane0;
      end
    endcase
  end

  assign execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_COND_lane0 = _zz_execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_COND_lane0_1;
  assign execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_btb_REAL_TARGET_lane0 = (execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_COND_lane0 ? execute_ctrl4_down_early0_BranchPlugin_pcCalc_PC_TRUE_lane0 : execute_ctrl4_down_early0_BranchPlugin_pcCalc_PC_FALSE_lane0);
  assign late0_BranchPlugin_logic_jumpLogic_wrongCond = (execute_ctrl4_down_Prediction_ALIGNED_JUMPED_lane0 != execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_COND_lane0);
  assign late0_BranchPlugin_logic_jumpLogic_needFix = ((late0_BranchPlugin_logic_jumpLogic_wrongCond || (execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_COND_lane0 && execute_ctrl4_down_late0_BranchPlugin_logic_alu_btb_BAD_TARGET_lane0)) || execute_ctrl4_down_late0_BranchPlugin_logic_alu_MSB_FAILED_lane0);
  assign late0_BranchPlugin_logic_jumpLogic_doIt = ((execute_ctrl4_up_LANE_SEL_lane0 && execute_ctrl4_down_late0_BranchPlugin_SEL_lane0) && late0_BranchPlugin_logic_jumpLogic_needFix);
  assign late0_BranchPlugin_logic_pcPort_valid = late0_BranchPlugin_logic_jumpLogic_doIt;
  assign late0_BranchPlugin_logic_pcPort_payload_fault = execute_ctrl4_down_late0_BranchPlugin_logic_alu_MSB_FAILED_lane0;
  assign late0_BranchPlugin_logic_pcPort_payload_pc = execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_btb_REAL_TARGET_lane0;
  assign late0_BranchPlugin_logic_flushPort_valid = late0_BranchPlugin_logic_jumpLogic_doIt;
  assign late0_BranchPlugin_logic_flushPort_payload_uopId = execute_ctrl4_down_Decode_UOP_ID_lane0;
  assign late0_BranchPlugin_logic_flushPort_payload_self = 1'b0;
  assign execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_MISSALIGNED_lane0 = ((execute_ctrl4_down_early0_BranchPlugin_pcCalc_PC_TRUE_lane0[1 : 0] != 2'b00) && execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_COND_lane0);
  always @(*) begin
    late0_BranchPlugin_logic_trapPort_valid = 1'b0;
    if(when_BranchPlugin_l251_1) begin
      late0_BranchPlugin_logic_trapPort_valid = 1'b1;
    end
  end

  assign late0_BranchPlugin_logic_trapPort_payload_exception = 1'b1;
  assign late0_BranchPlugin_logic_trapPort_payload_code = 4'b0000;
  assign late0_BranchPlugin_logic_trapPort_payload_tval = execute_ctrl4_down_early0_BranchPlugin_pcCalc_PC_TRUE_lane0;
  assign late0_BranchPlugin_logic_trapPort_payload_arg = 2'b00;
  assign when_BranchPlugin_l251_1 = (late0_BranchPlugin_logic_jumpLogic_doIt && execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_MISSALIGNED_lane0);
  assign execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_IS_JAL_lane0 = (execute_ctrl4_down_BranchPlugin_BRANCH_CTRL_lane0 == BranchPlugin_BranchCtrlEnum_JAL);
  assign execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_IS_JALR_lane0 = (execute_ctrl4_down_BranchPlugin_BRANCH_CTRL_lane0 == BranchPlugin_BranchCtrlEnum_JALR);
  assign late0_BranchPlugin_logic_jumpLogic_rdLink = (|{(execute_ctrl4_down_Decode_UOP_lane0[11 : 7] == 5'h05),(execute_ctrl4_down_Decode_UOP_lane0[11 : 7] == 5'h01)});
  assign late0_BranchPlugin_logic_jumpLogic_rs1Link = (|{(execute_ctrl4_down_Decode_UOP_lane0[19 : 15] == 5'h05),(execute_ctrl4_down_Decode_UOP_lane0[19 : 15] == 5'h01)});
  assign late0_BranchPlugin_logic_jumpLogic_rdEquRs1 = (execute_ctrl4_down_Decode_UOP_lane0[11 : 7] == execute_ctrl4_down_Decode_UOP_lane0[19 : 15]);
  assign late0_BranchPlugin_logic_jumpLogic_learn_valid = (((execute_ctrl4_up_LANE_SEL_lane0 && execute_ctrl4_down_isReady) && (! execute_lane0_ctrls_4_upIsCancel)) && (|{execute_ctrl4_down_late0_BranchPlugin_SEL_lane0,execute_ctrl4_down_early0_BranchPlugin_SEL_lane0}));
  assign late0_BranchPlugin_logic_jumpLogic_learn_payload_taken = execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_COND_lane0;
  assign late0_BranchPlugin_logic_jumpLogic_learn_payload_pcTarget = execute_ctrl4_down_early0_BranchPlugin_pcCalc_PC_TRUE_lane0;
  assign late0_BranchPlugin_logic_jumpLogic_learn_payload_pcOnLastSlice = execute_ctrl4_down_early0_BranchPlugin_pcCalc_PC_LAST_SLICE_lane0;
  assign late0_BranchPlugin_logic_jumpLogic_learn_payload_isBranch = (execute_ctrl4_down_BranchPlugin_BRANCH_CTRL_lane0 == BranchPlugin_BranchCtrlEnum_B);
  assign late0_BranchPlugin_logic_jumpLogic_learn_payload_isPush = ((execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_IS_JAL_lane0 || execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_IS_JALR_lane0) && late0_BranchPlugin_logic_jumpLogic_rdLink);
  assign late0_BranchPlugin_logic_jumpLogic_learn_payload_isPop = (execute_ctrl4_down_late0_BranchPlugin_logic_jumpLogic_IS_JALR_lane0 && (((! late0_BranchPlugin_logic_jumpLogic_rdLink) && late0_BranchPlugin_logic_jumpLogic_rs1Link) || ((late0_BranchPlugin_logic_jumpLogic_rdLink && late0_BranchPlugin_logic_jumpLogic_rs1Link) && (! late0_BranchPlugin_logic_jumpLogic_rdEquRs1))));
  assign late0_BranchPlugin_logic_jumpLogic_learn_payload_wasWrong = late0_BranchPlugin_logic_jumpLogic_needFix;
  assign late0_BranchPlugin_logic_jumpLogic_learn_payload_badPredictedTarget = execute_ctrl4_down_late0_BranchPlugin_logic_alu_btb_BAD_TARGET_lane0;
  assign late0_BranchPlugin_logic_jumpLogic_learn_payload_uopId = execute_ctrl4_down_Decode_UOP_ID_lane0;
  assign late0_BranchPlugin_logic_wb_valid = execute_ctrl4_down_late0_BranchPlugin_SEL_lane0;
  assign late0_BranchPlugin_logic_wb_payload = execute_ctrl4_down_early0_BranchPlugin_pcCalc_PC_FALSE_lane0;
  assign LearnPlugin_logic_buffered_0_valid = late0_BranchPlugin_logic_jumpLogic_learn_valid;
  assign late0_BranchPlugin_logic_jumpLogic_learn_ready = LearnPlugin_logic_buffered_0_ready;
  assign LearnPlugin_logic_buffered_0_payload_pcOnLastSlice = late0_BranchPlugin_logic_jumpLogic_learn_payload_pcOnLastSlice;
  assign LearnPlugin_logic_buffered_0_payload_pcTarget = late0_BranchPlugin_logic_jumpLogic_learn_payload_pcTarget;
  assign LearnPlugin_logic_buffered_0_payload_taken = late0_BranchPlugin_logic_jumpLogic_learn_payload_taken;
  assign LearnPlugin_logic_buffered_0_payload_isBranch = late0_BranchPlugin_logic_jumpLogic_learn_payload_isBranch;
  assign LearnPlugin_logic_buffered_0_payload_isPush = late0_BranchPlugin_logic_jumpLogic_learn_payload_isPush;
  assign LearnPlugin_logic_buffered_0_payload_isPop = late0_BranchPlugin_logic_jumpLogic_learn_payload_isPop;
  assign LearnPlugin_logic_buffered_0_payload_wasWrong = late0_BranchPlugin_logic_jumpLogic_learn_payload_wasWrong;
  assign LearnPlugin_logic_buffered_0_payload_badPredictedTarget = late0_BranchPlugin_logic_jumpLogic_learn_payload_badPredictedTarget;
  assign LearnPlugin_logic_buffered_0_payload_uopId = late0_BranchPlugin_logic_jumpLogic_learn_payload_uopId;
  assign LearnPlugin_logic_buffered_0_ready = streamArbiter_4_io_inputs_0_ready;
  assign LearnPlugin_logic_arbitrated_valid = streamArbiter_4_io_output_valid;
  assign LearnPlugin_logic_arbitrated_payload_pcOnLastSlice = streamArbiter_4_io_output_payload_pcOnLastSlice;
  assign LearnPlugin_logic_arbitrated_payload_pcTarget = streamArbiter_4_io_output_payload_pcTarget;
  assign LearnPlugin_logic_arbitrated_payload_taken = streamArbiter_4_io_output_payload_taken;
  assign LearnPlugin_logic_arbitrated_payload_isBranch = streamArbiter_4_io_output_payload_isBranch;
  assign LearnPlugin_logic_arbitrated_payload_isPush = streamArbiter_4_io_output_payload_isPush;
  assign LearnPlugin_logic_arbitrated_payload_isPop = streamArbiter_4_io_output_payload_isPop;
  assign LearnPlugin_logic_arbitrated_payload_wasWrong = streamArbiter_4_io_output_payload_wasWrong;
  assign LearnPlugin_logic_arbitrated_payload_badPredictedTarget = streamArbiter_4_io_output_payload_badPredictedTarget;
  assign LearnPlugin_logic_arbitrated_payload_uopId = streamArbiter_4_io_output_payload_uopId;
  assign LearnPlugin_logic_arbitrated_ready = 1'b1;
  assign LearnPlugin_logic_arbitrated_toFlow_valid = LearnPlugin_logic_arbitrated_valid;
  assign LearnPlugin_logic_arbitrated_toFlow_payload_pcOnLastSlice = LearnPlugin_logic_arbitrated_payload_pcOnLastSlice;
  assign LearnPlugin_logic_arbitrated_toFlow_payload_pcTarget = LearnPlugin_logic_arbitrated_payload_pcTarget;
  assign LearnPlugin_logic_arbitrated_toFlow_payload_taken = LearnPlugin_logic_arbitrated_payload_taken;
  assign LearnPlugin_logic_arbitrated_toFlow_payload_isBranch = LearnPlugin_logic_arbitrated_payload_isBranch;
  assign LearnPlugin_logic_arbitrated_toFlow_payload_isPush = LearnPlugin_logic_arbitrated_payload_isPush;
  assign LearnPlugin_logic_arbitrated_toFlow_payload_isPop = LearnPlugin_logic_arbitrated_payload_isPop;
  assign LearnPlugin_logic_arbitrated_toFlow_payload_wasWrong = LearnPlugin_logic_arbitrated_payload_wasWrong;
  assign LearnPlugin_logic_arbitrated_toFlow_payload_badPredictedTarget = LearnPlugin_logic_arbitrated_payload_badPredictedTarget;
  assign LearnPlugin_logic_arbitrated_toFlow_payload_uopId = LearnPlugin_logic_arbitrated_payload_uopId;
  assign LearnPlugin_logic_learn_valid = LearnPlugin_logic_arbitrated_toFlow_valid;
  assign LearnPlugin_logic_learn_payload_pcOnLastSlice = LearnPlugin_logic_arbitrated_toFlow_payload_pcOnLastSlice;
  assign LearnPlugin_logic_learn_payload_pcTarget = LearnPlugin_logic_arbitrated_toFlow_payload_pcTarget;
  assign LearnPlugin_logic_learn_payload_taken = LearnPlugin_logic_arbitrated_toFlow_payload_taken;
  assign LearnPlugin_logic_learn_payload_isBranch = LearnPlugin_logic_arbitrated_toFlow_payload_isBranch;
  assign LearnPlugin_logic_learn_payload_isPush = LearnPlugin_logic_arbitrated_toFlow_payload_isPush;
  assign LearnPlugin_logic_learn_payload_isPop = LearnPlugin_logic_arbitrated_toFlow_payload_isPop;
  assign LearnPlugin_logic_learn_payload_wasWrong = LearnPlugin_logic_arbitrated_toFlow_payload_wasWrong;
  assign LearnPlugin_logic_learn_payload_badPredictedTarget = LearnPlugin_logic_arbitrated_toFlow_payload_badPredictedTarget;
  assign LearnPlugin_logic_learn_payload_uopId = LearnPlugin_logic_arbitrated_toFlow_payload_uopId;
  assign when_DecoderPlugin_l143 = (decode_ctrls_1_up_isMoving && 1'b1);
  assign DecoderPlugin_logic_interrupt_async = PrivilegedPlugin_logic_harts_0_int_pending;
  assign when_DecoderPlugin_l151 = (((! decode_ctrls_1_up_valid) || decode_ctrls_1_up_ready) || decode_ctrls_1_up_isCanceling);
  assign _zz_decode_ctrls_1_down_DispatchPlugin_MAY_FLUSH_0 = ((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h00000018) == 32'h0);
  assign decode_ctrls_1_down_RS1_ENABLE_0 = _zz_decode_ctrls_1_down_RS1_ENABLE_0[0];
  assign decode_ctrls_1_down_RS1_PHYS_0 = decode_ctrls_1_down_Decode_INSTRUCTION_0[19 : 15];
  assign decode_ctrls_1_down_RS2_ENABLE_0 = _zz_decode_ctrls_1_down_RS2_ENABLE_0[0];
  assign decode_ctrls_1_down_RS2_PHYS_0 = decode_ctrls_1_down_Decode_INSTRUCTION_0[24 : 20];
  assign _zz_decode_ctrls_1_down_DispatchPlugin_logic_LANES_LAYER_HIT_1_0 = ((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h00000048) == 32'h00000048);
  always @(*) begin
    decode_ctrls_1_down_RD_ENABLE_0 = _zz_decode_ctrls_1_down_RD_ENABLE_0[0];
    if(when_DecoderPlugin_l247) begin
      decode_ctrls_1_down_RD_ENABLE_0 = 1'b0;
    end
  end

  assign decode_ctrls_1_down_RD_PHYS_0 = decode_ctrls_1_down_Decode_INSTRUCTION_0[11 : 7];
  assign decode_ctrls_1_down_Decode_LEGAL_0 = ((|{((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h0000005f) == 32'h00000017),{((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h0000007f) == 32'h0000006f),{((decode_ctrls_1_down_Decode_INSTRUCTION_0 & _zz_decode_ctrls_1_down_Decode_LEGAL_0) == 32'h00001073),{(_zz_decode_ctrls_1_down_Decode_LEGAL_0_1 == _zz_decode_ctrls_1_down_Decode_LEGAL_0_2),{_zz_decode_ctrls_1_down_Decode_LEGAL_0_3,{_zz_decode_ctrls_1_down_Decode_LEGAL_0_4,_zz_decode_ctrls_1_down_Decode_LEGAL_0_5}}}}}}) && (! decode_ctrls_1_down_Decode_DECOMPRESSION_FAULT_0));
  assign DecoderPlugin_logic_laneLogic_0_interruptPending = DecoderPlugin_logic_interrupt_buffered[0];
  always @(*) begin
    DecoderPlugin_logic_laneLogic_0_trapPort_valid = 1'b0;
    if(when_DecoderPlugin_l229) begin
      DecoderPlugin_logic_laneLogic_0_trapPort_valid = ((! decode_ctrls_1_up_TRAP_0) || DecoderPlugin_logic_laneLogic_0_interruptPending);
      if(DecoderPlugin_logic_laneLogic_0_fixer_doIt) begin
        DecoderPlugin_logic_laneLogic_0_trapPort_valid = 1'b1;
      end
    end
  end

  always @(*) begin
    DecoderPlugin_logic_laneLogic_0_trapPort_payload_exception = 1'b1;
    if(DecoderPlugin_logic_laneLogic_0_fixer_doIt) begin
      DecoderPlugin_logic_laneLogic_0_trapPort_payload_exception = 1'b0;
    end
    if(DecoderPlugin_logic_laneLogic_0_interruptPending) begin
      DecoderPlugin_logic_laneLogic_0_trapPort_payload_exception = 1'b0;
    end
  end

  assign DecoderPlugin_logic_laneLogic_0_trapPort_payload_tval = decode_ctrls_1_down_Decode_INSTRUCTION_RAW_0;
  always @(*) begin
    DecoderPlugin_logic_laneLogic_0_trapPort_payload_code = 4'b0010;
    if(DecoderPlugin_logic_laneLogic_0_fixer_doIt) begin
      DecoderPlugin_logic_laneLogic_0_trapPort_payload_code = 4'b0100;
    end
    if(DecoderPlugin_logic_laneLogic_0_interruptPending) begin
      DecoderPlugin_logic_laneLogic_0_trapPort_payload_code = 4'b0000;
    end
  end

  assign DecoderPlugin_logic_laneLogic_0_trapPort_payload_laneAge = 1'b0;
  assign DecoderPlugin_logic_laneLogic_0_trapPort_payload_arg = 2'b00;
  assign DecoderPlugin_logic_laneLogic_0_fixer_isJb = _zz_DecoderPlugin_logic_laneLogic_0_fixer_isJb[0];
  assign DecoderPlugin_logic_laneLogic_0_fixer_doIt = (decode_ctrls_1_up_LANE_SEL_0 && ((decode_ctrls_1_down_Prediction_ALIGNED_JUMPED_0 && (! DecoderPlugin_logic_laneLogic_0_fixer_isJb)) || decode_ctrls_1_down_Prediction_ALIGN_REDO_0));
  assign when_CtrlLaneApi_l50_1 = (decode_ctrls_1_up_isReady || decode_ctrls_1_lane0_upIsCancel);
  assign DecoderPlugin_logic_laneLogic_0_completionPort_valid = ((decode_ctrls_1_up_LANE_SEL_0 && decode_ctrls_1_down_TRAP_0) && (decode_ctrls_1_up_LANE_SEL_0 && (! decode_ctrls_1_up_LANE_SEL_0_regNext)));
  assign DecoderPlugin_logic_laneLogic_0_completionPort_payload_uopId = decode_ctrls_1_down_Decode_UOP_ID_0;
  assign DecoderPlugin_logic_laneLogic_0_completionPort_payload_trap = 1'b1;
  assign DecoderPlugin_logic_laneLogic_0_completionPort_payload_commit = 1'b0;
  assign when_DecoderPlugin_l229 = (decode_ctrls_1_up_LANE_SEL_0 && (((! decode_ctrls_1_down_Decode_LEGAL_0) || DecoderPlugin_logic_laneLogic_0_interruptPending) || DecoderPlugin_logic_laneLogic_0_fixer_doIt));
  assign DecoderPlugin_logic_laneLogic_0_flushPort_valid = (decode_ctrls_1_up_LANE_SEL_0 && decode_ctrls_1_down_TRAP_0);
  assign DecoderPlugin_logic_laneLogic_0_flushPort_payload_uopId = decode_ctrls_1_down_Decode_UOP_ID_0;
  assign DecoderPlugin_logic_laneLogic_0_flushPort_payload_self = 1'b0;
  assign when_DecoderPlugin_l247 = ((decode_ctrls_1_down_Decode_INSTRUCTION_0[11 : 7] == 5'h0) && (|1'b1));
  assign decode_ctrls_1_down_Decode_UOP_0 = decode_ctrls_1_down_Decode_INSTRUCTION_0;
  assign DecoderPlugin_logic_laneLogic_0_uopIdBase = DecoderPlugin_logic_harts_0_uopId;
  assign decode_ctrls_1_down_Decode_UOP_ID_0 = (DecoderPlugin_logic_laneLogic_0_uopIdBase + 16'h0);
  assign DispatchPlugin_logic_trapPendings[0] = 1'b0;
  assign DispatchPlugin_logic_candidates_0_moving = (((! DispatchPlugin_logic_candidates_0_ctx_valid) || DispatchPlugin_logic_candidates_0_fire) || DispatchPlugin_logic_candidates_0_cancel);
  assign DispatchPlugin_logic_rsHazardChecker_0_onLl_0_onRs_0_hazard = (DispatchPlugin_logic_candidates_0_ctx_hm_RS1_ENABLE && (|{((((DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_logic_hcs_0_onRs_0_ENABLES_0 && execute_ctrl2_up_RD_ENABLE_lane0) && (execute_ctrl2_up_RD_PHYS_lane0 == DispatchPlugin_logic_candidates_0_ctx_hm_RS1_PHYS)) && 1'b1) && (! execute_ctrl2_down_BYPASSED_AT_3_lane0)),((((DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_logic_hcs_0_onRs_0_ENABLES_0 && execute_ctrl1_up_RD_ENABLE_lane0) && (execute_ctrl1_up_RD_PHYS_lane0 == DispatchPlugin_logic_candidates_0_ctx_hm_RS1_PHYS)) && 1'b1) && (! execute_ctrl1_down_BYPASSED_AT_2_lane0))}));
  assign DispatchPlugin_logic_rsHazardChecker_0_onLl_0_onRs_1_hazard = (DispatchPlugin_logic_candidates_0_ctx_hm_RS2_ENABLE && (|{((((DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_0 && execute_ctrl2_up_RD_ENABLE_lane0) && (execute_ctrl2_up_RD_PHYS_lane0 == DispatchPlugin_logic_candidates_0_ctx_hm_RS2_PHYS)) && 1'b1) && (! execute_ctrl2_down_BYPASSED_AT_3_lane0)),((((DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_0 && execute_ctrl1_up_RD_ENABLE_lane0) && (execute_ctrl1_up_RD_PHYS_lane0 == DispatchPlugin_logic_candidates_0_ctx_hm_RS2_PHYS)) && 1'b1) && (! execute_ctrl1_down_BYPASSED_AT_2_lane0))}));
  always @(*) begin
    DispatchPlugin_logic_candidates_0_rsHazards[0] = (|{DispatchPlugin_logic_rsHazardChecker_0_onLl_0_onRs_1_hazard,DispatchPlugin_logic_rsHazardChecker_0_onLl_0_onRs_0_hazard});
    DispatchPlugin_logic_candidates_0_rsHazards[1] = (|{DispatchPlugin_logic_rsHazardChecker_0_onLl_1_onRs_1_hazard,DispatchPlugin_logic_rsHazardChecker_0_onLl_1_onRs_0_hazard});
  end

  assign DispatchPlugin_logic_rsHazardChecker_0_onLl_1_onRs_0_hazard = (DispatchPlugin_logic_candidates_0_ctx_hm_RS1_ENABLE && 1'b0);
  assign DispatchPlugin_logic_rsHazardChecker_0_onLl_1_onRs_1_hazard = (DispatchPlugin_logic_candidates_0_ctx_hm_RS2_ENABLE && 1'b0);
  assign DispatchPlugin_logic_reservationChecker_0_onLl_0_hit = 1'b0;
  always @(*) begin
    DispatchPlugin_logic_candidates_0_reservationHazards[0] = DispatchPlugin_logic_reservationChecker_0_onLl_0_hit;
    DispatchPlugin_logic_candidates_0_reservationHazards[1] = DispatchPlugin_logic_reservationChecker_0_onLl_1_hit;
  end

  assign DispatchPlugin_logic_reservationChecker_0_onLl_1_hit = 1'b0;
  assign DispatchPlugin_logic_flushChecker_0_executeCheck_0_hits_0 = (|{(((DispatchPlugin_logic_candidates_0_ctx_hm_DONT_FLUSH_PRECISE_4 && execute_ctrl1_up_LANE_SEL_lane0) && 1'b1) && execute_ctrl1_down_MAY_FLUSH_PRECISE_4_lane0),(((DispatchPlugin_logic_candidates_0_ctx_hm_DONT_FLUSH_PRECISE_3 && execute_ctrl1_up_LANE_SEL_lane0) && 1'b1) && execute_ctrl1_down_MAY_FLUSH_PRECISE_3_lane0)});
  assign DispatchPlugin_logic_flushChecker_0_executeCheck_0_hits_1 = (|(((DispatchPlugin_logic_candidates_0_ctx_hm_DONT_FLUSH_PRECISE_3 && execute_ctrl2_up_LANE_SEL_lane0) && 1'b1) && execute_ctrl2_down_MAY_FLUSH_PRECISE_3_lane0));
  assign DispatchPlugin_logic_flushChecker_0_oldersHazard = 1'b0;
  assign DispatchPlugin_logic_candidates_0_flushHazards = ((|{DispatchPlugin_logic_flushChecker_0_executeCheck_0_hits_1,DispatchPlugin_logic_flushChecker_0_executeCheck_0_hits_0}) || (DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_DONT_FLUSH_FROM_LANES && DispatchPlugin_logic_flushChecker_0_oldersHazard));
  assign DispatchPlugin_logic_fenceChecker_olderInflights = (|execute_lane0_api_hartsInflight[0]);
  assign DispatchPlugin_logic_candidates_0_fenceOlderHazards = (DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_FENCE_OLDER && (DispatchPlugin_logic_fenceChecker_olderInflights[0] || 1'b0));
  always @(*) begin
    decode_ctrls_1_down_ready = 1'b1;
    if(when_DispatchPlugin_l368) begin
      decode_ctrls_1_down_ready = 1'b0;
    end
  end

  assign DispatchPlugin_logic_feeds_0_sending = DispatchPlugin_logic_candidates_0_fire;
  assign DispatchPlugin_logic_candidates_0_cancel = decode_ctrls_1_lane0_upIsCancel;
  assign DispatchPlugin_logic_candidates_0_ctx_valid = ((decode_ctrls_1_up_isValid && decode_ctrls_1_up_LANE_SEL_0) && (! DispatchPlugin_logic_feeds_0_sent));
  always @(*) begin
    DispatchPlugin_logic_candidates_0_ctx_laneLayerHits = {decode_ctrls_1_down_DispatchPlugin_logic_LANES_LAYER_HIT_1_0,decode_ctrls_1_down_DispatchPlugin_logic_LANES_LAYER_HIT_0_0};
    if(decode_ctrls_1_down_TRAP_0) begin
      DispatchPlugin_logic_candidates_0_ctx_laneLayerHits = 2'b01;
    end
  end

  assign DispatchPlugin_logic_candidates_0_ctx_uop = decode_ctrls_1_down_Decode_UOP_0;
  assign DispatchPlugin_logic_candidates_0_ctx_hm_Prediction_ALIGNED_JUMPED = decode_ctrls_1_down_Prediction_ALIGNED_JUMPED_0;
  assign DispatchPlugin_logic_candidates_0_ctx_hm_Prediction_ALIGNED_JUMPED_PC = decode_ctrls_1_down_Prediction_ALIGNED_JUMPED_PC_0;
  assign DispatchPlugin_logic_candidates_0_ctx_hm_Prediction_ALIGNED_SLICES_TAKEN = decode_ctrls_1_down_Prediction_ALIGNED_SLICES_TAKEN_0;
  assign DispatchPlugin_logic_candidates_0_ctx_hm_Prediction_ALIGNED_SLICES_BRANCH = decode_ctrls_1_down_Prediction_ALIGNED_SLICES_BRANCH_0;
  assign DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_FENCE_OLDER = decode_ctrls_1_down_DispatchPlugin_FENCE_OLDER_0;
  assign DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_MAY_FLUSH = decode_ctrls_1_down_DispatchPlugin_MAY_FLUSH_0;
  assign DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_DONT_FLUSH = decode_ctrls_1_down_DispatchPlugin_DONT_FLUSH_0;
  assign DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_DONT_FLUSH_FROM_LANES = decode_ctrls_1_down_DispatchPlugin_DONT_FLUSH_FROM_LANES_0;
  assign DispatchPlugin_logic_candidates_0_ctx_hm_DONT_FLUSH_PRECISE_3 = decode_ctrls_1_down_DONT_FLUSH_PRECISE_3_0;
  assign DispatchPlugin_logic_candidates_0_ctx_hm_DONT_FLUSH_PRECISE_4 = decode_ctrls_1_down_DONT_FLUSH_PRECISE_4_0;
  assign DispatchPlugin_logic_candidates_0_ctx_hm_PC = decode_ctrls_1_down_PC_0;
  assign DispatchPlugin_logic_candidates_0_ctx_hm_TRAP = decode_ctrls_1_down_TRAP_0;
  assign DispatchPlugin_logic_candidates_0_ctx_hm_Decode_UOP_ID = decode_ctrls_1_down_Decode_UOP_ID_0;
  assign DispatchPlugin_logic_candidates_0_ctx_hm_RS1_ENABLE = decode_ctrls_1_down_RS1_ENABLE_0;
  assign DispatchPlugin_logic_candidates_0_ctx_hm_RS1_PHYS = decode_ctrls_1_down_RS1_PHYS_0;
  assign DispatchPlugin_logic_candidates_0_ctx_hm_RS2_ENABLE = decode_ctrls_1_down_RS2_ENABLE_0;
  assign DispatchPlugin_logic_candidates_0_ctx_hm_RS2_PHYS = decode_ctrls_1_down_RS2_PHYS_0;
  assign DispatchPlugin_logic_candidates_0_ctx_hm_RD_ENABLE = decode_ctrls_1_down_RD_ENABLE_0;
  assign DispatchPlugin_logic_candidates_0_ctx_hm_RD_PHYS = decode_ctrls_1_down_RD_PHYS_0;
  assign DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_logic_hcs_0_onRs_0_ENABLES_0 = decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_0_ENABLES_0_0;
  assign DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_0 = decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_0_0;
  assign DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_1 = decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_1_0;
  assign DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_logic_hcs_1_onRs_0_ENABLES_0 = decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_0_ENABLES_0_0;
  assign DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_logic_hcs_1_onRs_1_ENABLES_0 = decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_1_ENABLES_0_0;
  assign when_DispatchPlugin_l368 = ((decode_ctrls_1_up_LANE_SEL_0 && (! DispatchPlugin_logic_feeds_0_sent)) && (! DispatchPlugin_logic_candidates_0_fire));
  assign DispatchPlugin_logic_scheduler_eusFree_0 = 1'b1;
  assign DispatchPlugin_logic_scheduler_hartFree_0 = 1'b1;
  assign DispatchPlugin_logic_scheduler_arbiters_0_candHazard = 1'b0;
  assign DispatchPlugin_logic_scheduler_arbiters_0_layersHits = (((DispatchPlugin_logic_candidates_0_ctx_laneLayerHits & (~ DispatchPlugin_logic_candidates_0_rsHazards)) & (~ DispatchPlugin_logic_candidates_0_reservationHazards)) & {DispatchPlugin_logic_scheduler_eusFree_0[0],DispatchPlugin_logic_scheduler_eusFree_0[0]});
  assign _zz_DispatchPlugin_logic_scheduler_arbiters_0_layersHits_bools_0 = DispatchPlugin_logic_scheduler_arbiters_0_layersHits;
  assign DispatchPlugin_logic_scheduler_arbiters_0_layersHits_bools_0 = _zz_DispatchPlugin_logic_scheduler_arbiters_0_layersHits_bools_0[0];
  assign DispatchPlugin_logic_scheduler_arbiters_0_layersHits_bools_1 = _zz_DispatchPlugin_logic_scheduler_arbiters_0_layersHits_bools_0[1];
  always @(*) begin
    _zz_DispatchPlugin_logic_scheduler_arbiters_0_layerOh[0] = (DispatchPlugin_logic_scheduler_arbiters_0_layersHits_bools_0 && (! 1'b0));
    _zz_DispatchPlugin_logic_scheduler_arbiters_0_layerOh[1] = (DispatchPlugin_logic_scheduler_arbiters_0_layersHits_bools_1 && (! DispatchPlugin_logic_scheduler_arbiters_0_layersHits_bools_0));
  end

  assign DispatchPlugin_logic_scheduler_arbiters_0_layerOh = _zz_DispatchPlugin_logic_scheduler_arbiters_0_layerOh;
  assign DispatchPlugin_logic_scheduler_arbiters_0_eusOh = (|{DispatchPlugin_logic_scheduler_arbiters_0_layerOh[1],DispatchPlugin_logic_scheduler_arbiters_0_layerOh[0]});
  assign DispatchPlugin_logic_scheduler_arbiters_0_doIt = (((((DispatchPlugin_logic_candidates_0_ctx_valid && (! DispatchPlugin_logic_candidates_0_flushHazards)) && (! DispatchPlugin_logic_candidates_0_fenceOlderHazards)) && (|DispatchPlugin_logic_scheduler_arbiters_0_layerOh)) && DispatchPlugin_logic_scheduler_hartFree_0[0]) && (! DispatchPlugin_logic_scheduler_arbiters_0_candHazard));
  assign DispatchPlugin_logic_scheduler_eusFree_1 = (DispatchPlugin_logic_scheduler_eusFree_0 & ((! DispatchPlugin_logic_scheduler_arbiters_0_doIt) ? 1'b1 : (~ DispatchPlugin_logic_scheduler_arbiters_0_eusOh)));
  assign DispatchPlugin_logic_scheduler_hartFree_1 = (DispatchPlugin_logic_scheduler_hartFree_0 & (((! DispatchPlugin_logic_candidates_0_ctx_valid) || DispatchPlugin_logic_scheduler_arbiters_0_doIt) ? 1'b1 : (~ 1'b1)));
  assign DispatchPlugin_logic_candidates_0_fire = ((DispatchPlugin_logic_scheduler_arbiters_0_doIt && (! execute_freeze_valid)) && (! DispatchPlugin_api_haltDispatch));
  assign DispatchPlugin_logic_inserter_0_oh = (DispatchPlugin_logic_scheduler_arbiters_0_doIt && DispatchPlugin_logic_scheduler_arbiters_0_eusOh[0]);
  assign DispatchPlugin_logic_inserter_0_trap = DispatchPlugin_logic_candidates_0_ctx_hm_TRAP;
  assign execute_ctrl0_up_LANE_SEL_lane0 = (((|DispatchPlugin_logic_inserter_0_oh) && (! DispatchPlugin_logic_candidates_0_cancel)) && (! DispatchPlugin_api_haltDispatch));
  assign execute_ctrl0_up_Decode_UOP_lane0 = DispatchPlugin_logic_candidates_0_ctx_uop;
  assign execute_ctrl0_up_Prediction_ALIGNED_JUMPED_lane0 = DispatchPlugin_logic_candidates_0_ctx_hm_Prediction_ALIGNED_JUMPED;
  assign execute_ctrl0_up_Prediction_ALIGNED_JUMPED_PC_lane0 = DispatchPlugin_logic_candidates_0_ctx_hm_Prediction_ALIGNED_JUMPED_PC;
  assign execute_ctrl0_up_Prediction_ALIGNED_SLICES_TAKEN_lane0 = DispatchPlugin_logic_candidates_0_ctx_hm_Prediction_ALIGNED_SLICES_TAKEN;
  assign execute_ctrl0_up_Prediction_ALIGNED_SLICES_BRANCH_lane0 = DispatchPlugin_logic_candidates_0_ctx_hm_Prediction_ALIGNED_SLICES_BRANCH;
  assign execute_ctrl0_up_DispatchPlugin_FENCE_OLDER_lane0 = DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_FENCE_OLDER;
  always @(*) begin
    execute_ctrl0_up_DispatchPlugin_MAY_FLUSH_lane0 = DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_MAY_FLUSH;
    if(when_DispatchPlugin_l439) begin
      execute_ctrl0_up_DispatchPlugin_MAY_FLUSH_lane0 = 1'b0;
    end
  end

  assign execute_ctrl0_up_DispatchPlugin_DONT_FLUSH_lane0 = DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_DONT_FLUSH;
  assign execute_ctrl0_up_DispatchPlugin_DONT_FLUSH_FROM_LANES_lane0 = DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_DONT_FLUSH_FROM_LANES;
  assign execute_ctrl0_up_DONT_FLUSH_PRECISE_3_lane0 = DispatchPlugin_logic_candidates_0_ctx_hm_DONT_FLUSH_PRECISE_3;
  assign execute_ctrl0_up_DONT_FLUSH_PRECISE_4_lane0 = DispatchPlugin_logic_candidates_0_ctx_hm_DONT_FLUSH_PRECISE_4;
  assign execute_ctrl0_up_PC_lane0 = DispatchPlugin_logic_candidates_0_ctx_hm_PC;
  assign execute_ctrl0_up_TRAP_lane0 = DispatchPlugin_logic_candidates_0_ctx_hm_TRAP;
  assign execute_ctrl0_up_Decode_UOP_ID_lane0 = DispatchPlugin_logic_candidates_0_ctx_hm_Decode_UOP_ID;
  assign execute_ctrl0_up_RS1_ENABLE_lane0 = DispatchPlugin_logic_candidates_0_ctx_hm_RS1_ENABLE;
  assign execute_ctrl0_up_RS1_PHYS_lane0 = DispatchPlugin_logic_candidates_0_ctx_hm_RS1_PHYS;
  assign execute_ctrl0_up_RS2_ENABLE_lane0 = DispatchPlugin_logic_candidates_0_ctx_hm_RS2_ENABLE;
  assign execute_ctrl0_up_RS2_PHYS_lane0 = DispatchPlugin_logic_candidates_0_ctx_hm_RS2_PHYS;
  always @(*) begin
    execute_ctrl0_up_RD_ENABLE_lane0 = DispatchPlugin_logic_candidates_0_ctx_hm_RD_ENABLE;
    if(when_DispatchPlugin_l439) begin
      execute_ctrl0_up_RD_ENABLE_lane0 = 1'b0;
    end
  end

  assign execute_ctrl0_up_RD_PHYS_lane0 = DispatchPlugin_logic_candidates_0_ctx_hm_RD_PHYS;
  assign execute_ctrl0_up_DispatchPlugin_logic_hcs_0_onRs_0_ENABLES_0_lane0 = DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_logic_hcs_0_onRs_0_ENABLES_0;
  assign execute_ctrl0_up_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_0_lane0 = DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_0;
  assign execute_ctrl0_up_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_1_lane0 = DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_1;
  assign execute_ctrl0_up_DispatchPlugin_logic_hcs_1_onRs_0_ENABLES_0_lane0 = DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_logic_hcs_1_onRs_0_ENABLES_0;
  assign execute_ctrl0_up_DispatchPlugin_logic_hcs_1_onRs_1_ENABLES_0_lane0 = DispatchPlugin_logic_candidates_0_ctx_hm_DispatchPlugin_logic_hcs_1_onRs_1_ENABLES_0;
  assign when_DispatchPlugin_l439 = ((! execute_ctrl0_up_LANE_SEL_lane0) || DispatchPlugin_logic_inserter_0_trap);
  assign execute_ctrl0_up_COMPLETED_lane0 = DispatchPlugin_logic_inserter_0_trap;
  assign DispatchPlugin_logic_inserter_0_layerOhUnfiltred = (DispatchPlugin_logic_inserter_0_oh[0] ? DispatchPlugin_logic_scheduler_arbiters_0_layerOh : 2'b00);
  assign DispatchPlugin_logic_inserter_0_layer_0_0 = 1'b1;
  assign DispatchPlugin_logic_inserter_0_layer_0_1 = DispatchPlugin_logic_inserter_0_layerOhUnfiltred[0];
  assign DispatchPlugin_logic_inserter_0_layer_1_0 = 1'b0;
  assign DispatchPlugin_logic_inserter_0_layer_1_1 = DispatchPlugin_logic_inserter_0_layerOhUnfiltred[1];
  assign _zz_execute_ctrl0_up_lane0_LAYER_SEL_lane0 = {DispatchPlugin_logic_inserter_0_layer_1_1,DispatchPlugin_logic_inserter_0_layer_0_1};
  assign execute_ctrl0_up_lane0_LAYER_SEL_lane0 = ((_zz_execute_ctrl0_up_lane0_LAYER_SEL_lane0[0] ? DispatchPlugin_logic_inserter_0_layer_0_0 : 1'b0) | (_zz_execute_ctrl0_up_lane0_LAYER_SEL_lane0[1] ? DispatchPlugin_logic_inserter_0_layer_1_0 : 1'b0));
  assign _zz_CsrRamPlugin_csrMapper_ramAddress = CsrAccessPlugin_bus_decode_address;
  assign CsrRamPlugin_csrMapper_ramAddress = {(|{((_zz_CsrRamPlugin_csrMapper_ramAddress & 12'h002) == 12'h002),((_zz_CsrRamPlugin_csrMapper_ramAddress & 12'h040) == 12'h0)}),(|((_zz_CsrRamPlugin_csrMapper_ramAddress & 12'h003) == 12'h001))};
  always @(*) begin
    CsrRamPlugin_csrMapper_withRead = 1'b0;
    if(when_CsrAccessPlugin_l252) begin
      CsrRamPlugin_csrMapper_withRead = 1'b1;
    end
  end

  assign CsrRamPlugin_csrMapper_read_valid = (CsrRamPlugin_csrMapper_withRead && (! CsrRamPlugin_api_holdRead));
  assign CsrRamPlugin_csrMapper_read_address = CsrRamPlugin_csrMapper_ramAddress;
  assign when_CsrRamPlugin_l85 = (CsrRamPlugin_csrMapper_withRead && (! CsrRamPlugin_csrMapper_read_ready));
  always @(*) begin
    CsrRamPlugin_csrMapper_doWrite = 1'b0;
    if(when_CsrAccessPlugin_l343_2) begin
      CsrRamPlugin_csrMapper_doWrite = 1'b1;
    end
  end

  assign when_CsrRamPlugin_l92 = (CsrRamPlugin_csrMapper_write_valid && CsrRamPlugin_csrMapper_write_ready);
  assign CsrRamPlugin_csrMapper_write_valid = ((CsrRamPlugin_csrMapper_doWrite && (! CsrRamPlugin_csrMapper_fired)) && (! CsrRamPlugin_api_holdWrite));
  assign CsrRamPlugin_csrMapper_write_address = CsrRamPlugin_csrMapper_ramAddress;
  assign CsrRamPlugin_csrMapper_write_data = CsrAccessPlugin_bus_write_bits;
  assign when_CsrRamPlugin_l96 = ((CsrRamPlugin_csrMapper_doWrite && (! CsrRamPlugin_csrMapper_fired)) && (! CsrRamPlugin_csrMapper_write_ready));
  assign BtbPlugin_logic_onLearn_hash = LearnPlugin_logic_learn_payload_pcOnLastSlice[26 : 11];
  always @(*) begin
    BtbPlugin_logic_memWrite_valid = (LearnPlugin_logic_learn_valid && (LearnPlugin_logic_learn_payload_wasWrong || LearnPlugin_logic_learn_payload_badPredictedTarget));
    if(DecoderPlugin_logic_forgetPort_valid) begin
      BtbPlugin_logic_memWrite_valid = DecoderPlugin_logic_forgetPort_valid;
    end
  end

  always @(*) begin
    BtbPlugin_logic_memWrite_payload_address = _zz_BtbPlugin_logic_memWrite_payload_address[8:0];
    if(DecoderPlugin_logic_forgetPort_valid) begin
      BtbPlugin_logic_memWrite_payload_address = _zz_BtbPlugin_logic_memWrite_payload_address_1[8:0];
    end
  end

  always @(*) begin
    BtbPlugin_logic_memWrite_payload_mask = 1'b1;
    if(DecoderPlugin_logic_forgetPort_valid) begin
      BtbPlugin_logic_memWrite_payload_mask = 1'b1;
    end
  end

  always @(*) begin
    BtbPlugin_logic_memWrite_payload_data_0_hash = BtbPlugin_logic_onLearn_hash;
    if(DecoderPlugin_logic_forgetPort_valid) begin
      BtbPlugin_logic_memWrite_payload_data_0_hash = (~ BtbPlugin_logic_onForget_hash);
    end
  end

  assign BtbPlugin_logic_memWrite_payload_data_0_pcTarget = (LearnPlugin_logic_learn_payload_pcTarget >>> 2'd2);
  always @(*) begin
    BtbPlugin_logic_memWrite_payload_data_0_isBranch = LearnPlugin_logic_learn_payload_isBranch;
    if(DecoderPlugin_logic_forgetPort_valid) begin
      BtbPlugin_logic_memWrite_payload_data_0_isBranch = 1'b0;
    end
  end

  always @(*) begin
    BtbPlugin_logic_memWrite_payload_data_0_isPush = LearnPlugin_logic_learn_payload_isPush;
    if(DecoderPlugin_logic_forgetPort_valid) begin
      BtbPlugin_logic_memWrite_payload_data_0_isPush = 1'b0;
    end
  end

  always @(*) begin
    BtbPlugin_logic_memWrite_payload_data_0_isPop = LearnPlugin_logic_learn_payload_isPop;
    if(DecoderPlugin_logic_forgetPort_valid) begin
      BtbPlugin_logic_memWrite_payload_data_0_isPop = 1'b0;
    end
  end

  always @(*) begin
    BtbPlugin_logic_memWrite_payload_data_0_taken = LearnPlugin_logic_learn_payload_taken;
    if(DecoderPlugin_logic_forgetPort_valid) begin
      BtbPlugin_logic_memWrite_payload_data_0_taken = 1'b0;
    end
  end

  assign lane0_integer_WriteBackPlugin_logic_stages_0_hits = {lane0_IntFormatPlugin_logic_stages_0_wb_valid,early0_BranchPlugin_logic_wb_valid};
  assign lane0_integer_WriteBackPlugin_logic_stages_0_muxed = ((lane0_integer_WriteBackPlugin_logic_stages_0_hits[0] ? early0_BranchPlugin_logic_wb_payload : 32'h0) | (lane0_integer_WriteBackPlugin_logic_stages_0_hits[1] ? lane0_IntFormatPlugin_logic_stages_0_wb_payload : 32'h0));
  assign execute_ctrl2_lane0_integer_WriteBackPlugin_logic_DATA_lane0_bypass = lane0_integer_WriteBackPlugin_logic_stages_0_muxed;
  assign lane0_integer_WriteBackPlugin_logic_stages_0_write_valid = (((((execute_ctrl2_down_LANE_SEL_lane0 && execute_ctrl2_down_isReady) && (! execute_lane0_ctrls_2_downIsCancel)) && (|lane0_integer_WriteBackPlugin_logic_stages_0_hits)) && execute_ctrl2_up_RD_ENABLE_lane0) && execute_ctrl2_down_COMMIT_lane0);
  assign lane0_integer_WriteBackPlugin_logic_stages_0_write_payload_uopId = execute_ctrl2_down_Decode_UOP_ID_lane0;
  assign lane0_integer_WriteBackPlugin_logic_stages_0_write_payload_data = lane0_integer_WriteBackPlugin_logic_stages_0_muxed;
  assign lane0_integer_WriteBackPlugin_logic_stages_1_hits = lane0_IntFormatPlugin_logic_stages_2_wb_valid;
  assign lane0_integer_WriteBackPlugin_logic_stages_1_muxed = (lane0_integer_WriteBackPlugin_logic_stages_1_hits[0] ? lane0_IntFormatPlugin_logic_stages_2_wb_payload : 32'h0);
  assign lane0_integer_WriteBackPlugin_logic_stages_1_merged = (execute_ctrl3_up_lane0_integer_WriteBackPlugin_logic_DATA_lane0 | lane0_integer_WriteBackPlugin_logic_stages_1_muxed);
  assign execute_ctrl3_lane0_integer_WriteBackPlugin_logic_DATA_lane0_bypass = lane0_integer_WriteBackPlugin_logic_stages_1_merged;
  assign lane0_integer_WriteBackPlugin_logic_stages_1_write_valid = (((((execute_ctrl3_down_LANE_SEL_lane0 && execute_ctrl3_down_isReady) && (! execute_lane0_ctrls_3_downIsCancel)) && (|lane0_integer_WriteBackPlugin_logic_stages_1_hits)) && execute_ctrl3_up_RD_ENABLE_lane0) && execute_ctrl3_down_COMMIT_lane0);
  assign lane0_integer_WriteBackPlugin_logic_stages_1_write_payload_uopId = execute_ctrl3_down_Decode_UOP_ID_lane0;
  assign lane0_integer_WriteBackPlugin_logic_stages_1_write_payload_data = lane0_integer_WriteBackPlugin_logic_stages_1_muxed;
  assign lane0_integer_WriteBackPlugin_logic_stages_2_hits = {lane0_IntFormatPlugin_logic_stages_1_wb_valid,late0_BranchPlugin_logic_wb_valid};
  assign lane0_integer_WriteBackPlugin_logic_stages_2_muxed = ((lane0_integer_WriteBackPlugin_logic_stages_2_hits[0] ? late0_BranchPlugin_logic_wb_payload : 32'h0) | (lane0_integer_WriteBackPlugin_logic_stages_2_hits[1] ? lane0_IntFormatPlugin_logic_stages_1_wb_payload : 32'h0));
  assign lane0_integer_WriteBackPlugin_logic_stages_2_merged = (execute_ctrl4_up_lane0_integer_WriteBackPlugin_logic_DATA_lane0 | lane0_integer_WriteBackPlugin_logic_stages_2_muxed);
  assign execute_ctrl4_lane0_integer_WriteBackPlugin_logic_DATA_lane0_bypass = lane0_integer_WriteBackPlugin_logic_stages_2_merged;
  assign lane0_integer_WriteBackPlugin_logic_stages_2_write_valid = (((((execute_ctrl4_down_LANE_SEL_lane0 && execute_ctrl4_down_isReady) && (! execute_lane0_ctrls_4_downIsCancel)) && (|lane0_integer_WriteBackPlugin_logic_stages_2_hits)) && execute_ctrl4_up_RD_ENABLE_lane0) && execute_ctrl4_down_COMMIT_lane0);
  assign lane0_integer_WriteBackPlugin_logic_stages_2_write_payload_uopId = execute_ctrl4_down_Decode_UOP_ID_lane0;
  assign lane0_integer_WriteBackPlugin_logic_stages_2_write_payload_data = lane0_integer_WriteBackPlugin_logic_stages_2_muxed;
  assign lane0_integer_WriteBackPlugin_logic_write_port_valid = (((((execute_ctrl4_up_LANE_SEL_lane0 && execute_ctrl4_down_isReady) && (! execute_lane0_ctrls_4_upIsCancel)) && execute_ctrl4_up_RD_ENABLE_lane0) && execute_ctrl4_down_lane0_integer_WriteBackPlugin_SEL_lane0) && execute_ctrl4_down_COMMIT_lane0);
  assign lane0_integer_WriteBackPlugin_logic_write_port_address = execute_ctrl4_down_RD_PHYS_lane0;
  assign lane0_integer_WriteBackPlugin_logic_write_port_data = execute_ctrl4_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0;
  assign lane0_integer_WriteBackPlugin_logic_write_port_uopId = execute_ctrl4_down_Decode_UOP_ID_lane0;
  assign decode_ctrls_1_down_DecoderPlugin_logic_NEED_FPU_0 = _zz_decode_ctrls_1_down_DecoderPlugin_logic_NEED_FPU_0[0];
  assign decode_ctrls_1_down_DecoderPlugin_logic_NEED_RM_0 = _zz_decode_ctrls_1_down_DecoderPlugin_logic_NEED_RM_0[0];
  assign _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_1_ENABLES_0_0 = ((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h0) == 32'h0);
  assign decode_ctrls_1_down_DispatchPlugin_logic_LANES_LAYER_HIT_0_0 = _zz_decode_ctrls_1_down_DispatchPlugin_logic_LANES_LAYER_HIT_0_0[0];
  assign decode_ctrls_1_down_DispatchPlugin_logic_LANES_LAYER_HIT_1_0 = _zz_decode_ctrls_1_down_DispatchPlugin_logic_LANES_LAYER_HIT_1_0_1[0];
  assign _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_0_0 = ((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h00000040) == 32'h00000040);
  assign decode_ctrls_1_down_DispatchPlugin_MAY_FLUSH_0 = _zz_decode_ctrls_1_down_DispatchPlugin_MAY_FLUSH_0_1[0];
  assign _zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_4_0 = ((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h00002050) == 32'h00002050);
  assign _zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_4_0_1 = ((decode_ctrls_1_down_Decode_INSTRUCTION_0 & 32'h00001050) == 32'h00001050);
  assign decode_ctrls_1_down_DispatchPlugin_DONT_FLUSH_0 = _zz_decode_ctrls_1_down_DispatchPlugin_DONT_FLUSH_0[0];
  assign decode_ctrls_1_down_DispatchPlugin_DONT_FLUSH_FROM_LANES_0 = _zz_decode_ctrls_1_down_DispatchPlugin_DONT_FLUSH_FROM_LANES_0[0];
  assign decode_ctrls_1_down_DispatchPlugin_FENCE_OLDER_0 = _zz_decode_ctrls_1_down_DispatchPlugin_FENCE_OLDER_0[0];
  assign decode_ctrls_1_down_DONT_FLUSH_PRECISE_3_0 = _zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_3_0[0];
  assign decode_ctrls_1_down_DONT_FLUSH_PRECISE_4_0 = _zz_decode_ctrls_1_down_DONT_FLUSH_PRECISE_4_0_2[0];
  assign decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_0_ENABLES_0_0 = _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_0_ENABLES_0_0[0];
  assign decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_0_0 = _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_0_0_1[0];
  assign decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_1_0 = _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_0_onRs_1_ENABLES_1_0[0];
  assign decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_0_ENABLES_0_0 = _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_0_ENABLES_0_0[0];
  assign decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_1_ENABLES_0_0 = _zz_decode_ctrls_1_down_DispatchPlugin_logic_hcs_1_onRs_1_ENABLES_0_0_1[0];
  assign when_CtrlLaneApi_l50_2 = (decode_ctrls_1_up_isReady || decode_ctrls_1_lane0_upIsCancel);
  assign WhiteboxerPlugin_logic_serializeds_0_fire = (decode_ctrls_1_up_LANE_SEL_0 && (! decode_ctrls_1_up_LANE_SEL_0_regNext_1));
  assign WhiteboxerPlugin_logic_serializeds_0_decodeId = decode_ctrls_1_down_Decode_DOP_ID_0;
  assign WhiteboxerPlugin_logic_serializeds_0_microOpId = decode_ctrls_1_down_Decode_UOP_ID_0;
  assign WhiteboxerPlugin_logic_serializeds_0_microOp = decode_ctrls_1_down_Decode_UOP_0;
  assign when_CtrlLaneApi_l50_3 = (execute_ctrl0_down_isReady || execute_lane0_ctrls_0_downIsCancel);
  assign WhiteboxerPlugin_logic_dispatches_0_fire = (execute_ctrl0_down_LANE_SEL_lane0 && (! execute_ctrl0_down_LANE_SEL_lane0_regNext));
  assign WhiteboxerPlugin_logic_dispatches_0_microOpId = execute_ctrl0_down_Decode_UOP_ID_lane0;
  assign when_CtrlLaneApi_l50_4 = (execute_ctrl2_down_isReady || execute_lane0_ctrls_2_downIsCancel);
  assign WhiteboxerPlugin_logic_executes_0_fire = ((execute_ctrl2_down_LANE_SEL_lane0 && (! execute_ctrl2_down_LANE_SEL_lane0_regNext)) && execute_ctrl2_down_COMMIT_lane0);
  assign WhiteboxerPlugin_logic_executes_0_microOpId = execute_ctrl2_down_Decode_UOP_ID_lane0;
  assign BtbPlugin_logic_onForget_hash = DecoderPlugin_logic_forgetPort_payload_pcOnLastSlice[26 : 11];
  assign BtbPlugin_logic_memRead_cmd_valid = fetch_logic_ctrls_0_down_isReady;
  assign BtbPlugin_logic_memRead_cmd_payload = _zz_BtbPlugin_logic_memRead_cmd_payload[8:0];
  assign fetch_logic_ctrls_0_down_BtbPlugin_logic_readCmd_HAZARDS = ((BtbPlugin_logic_memWrite_valid && (BtbPlugin_logic_memWrite_payload_address == BtbPlugin_logic_memRead_cmd_payload)) ? BtbPlugin_logic_memWrite_payload_mask : 1'b0);
  assign fetch_logic_ctrls_0_haltRequest_BtbPlugin_l200 = BtbPlugin_logic_memWrite_valid;
  assign fetch_logic_ctrls_1_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_hash = BtbPlugin_logic_memRead_rsp_0_hash;
  assign fetch_logic_ctrls_1_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_pcTarget = BtbPlugin_logic_memRead_rsp_0_pcTarget;
  assign fetch_logic_ctrls_1_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isBranch = BtbPlugin_logic_memRead_rsp_0_isBranch;
  assign fetch_logic_ctrls_1_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isPush = BtbPlugin_logic_memRead_rsp_0_isPush;
  assign fetch_logic_ctrls_1_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isPop = BtbPlugin_logic_memRead_rsp_0_isPop;
  assign fetch_logic_ctrls_1_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_taken = BtbPlugin_logic_memRead_rsp_0_taken;
  assign fetch_logic_ctrls_1_down_BtbPlugin_logic_chunksLogic_0_hitCalc_HIT = ((fetch_logic_ctrls_1_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_hash == fetch_logic_ctrls_1_down_Fetch_WORD_PC[26 : 11]) && 1'b1);
  assign fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_predict_TAKEN = ((! fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isBranch) || fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_taken);
  assign BtbPlugin_logic_applyIt_chunksMask = (fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_hitCalc_HIT && 1'b1);
  assign BtbPlugin_logic_applyIt_chunksTakenOh = (fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_predict_TAKEN & BtbPlugin_logic_applyIt_chunksMask);
  assign BtbPlugin_logic_applyIt_needIt = (fetch_logic_ctrls_2_up_isValid && (|BtbPlugin_logic_applyIt_chunksTakenOh));
  assign when_BtbPlugin_l233 = (fetch_logic_ctrls_2_up_isReady || fetch_logic_ctrls_2_up_isCancel);
  assign BtbPlugin_logic_applyIt_doIt = (BtbPlugin_logic_applyIt_needIt && (! BtbPlugin_logic_applyIt_correctionSent));
  assign BtbPlugin_logic_applyIt_entry_hash = fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_hash;
  assign BtbPlugin_logic_applyIt_entry_pcTarget = fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_pcTarget;
  assign BtbPlugin_logic_applyIt_entry_isBranch = fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isBranch;
  assign BtbPlugin_logic_applyIt_entry_isPush = fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isPush;
  assign BtbPlugin_logic_applyIt_entry_isPop = fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isPop;
  assign BtbPlugin_logic_applyIt_entry_taken = fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_taken;
  assign BtbPlugin_logic_applyIt_pcTarget = BtbPlugin_logic_applyIt_entry_pcTarget;
  assign BtbPlugin_logic_flushPort_valid = BtbPlugin_logic_applyIt_doIt;
  assign BtbPlugin_logic_flushPort_payload_self = 1'b0;
  assign BtbPlugin_logic_pcPort_valid = BtbPlugin_logic_applyIt_doIt;
  assign BtbPlugin_logic_pcPort_payload_fault = 1'b0;
  assign BtbPlugin_logic_pcPort_payload_pc = ({2'd0,BtbPlugin_logic_applyIt_pcTarget} <<< 2'd2);
  assign fetch_logic_ctrls_2_down_Prediction_WORD_JUMPED = BtbPlugin_logic_applyIt_needIt;
  assign fetch_logic_ctrls_2_down_Prediction_WORD_JUMP_PC = ({2'd0,BtbPlugin_logic_applyIt_pcTarget} <<< 2'd2);
  assign fetch_logic_ctrls_2_down_Prediction_WORD_SLICES_BRANCH[0] = ((fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_hitCalc_HIT && fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isBranch) && 1'b1);
  assign fetch_logic_ctrls_2_down_Prediction_WORD_SLICES_TAKEN[0] = fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_predict_TAKEN;
  assign AlignerPlugin_logic_nobuffer_flushIt = (|{(DecoderPlugin_logic_laneLogic_0_flushPort_valid && 1'b1),{(late0_BranchPlugin_logic_flushPort_valid && 1'b1),{(early0_EnvPlugin_logic_flushPort_valid && 1'b1),{(CsrAccessPlugin_logic_flushPort_valid && 1'b1),{(early0_BranchPlugin_logic_flushPort_valid && 1'b1),(LsuPlugin_logic_flushPort_valid && 1'b1)}}}}});
  assign when_AlignerPlugin_l298 = ((AlignerPlugin_logic_nobuffer_flushIt || (! fetch_logic_ctrls_2_down_isValid)) || fetch_logic_ctrls_2_down_isReady);
  assign AlignerPlugin_logic_slices_data_0 = fetch_logic_ctrls_2_down_Fetch_WORD[31 : 0];
  assign AlignerPlugin_logic_slices_mask = ((fetch_logic_ctrls_2_down_valid ? fetch_logic_ctrls_2_down_AlignerPlugin_logic_FETCH_MASK : 1'b0) & 1'b1);
  assign AlignerPlugin_logic_slices_last = 1'b0;
  assign fetch_logic_ctrls_2_down_ready = ((! fetch_logic_ctrls_2_down_valid) || ((decode_ctrls_0_up_isReady && (! AlignerPlugin_api_haltIt)) && (AlignerPlugin_logic_nobuffer_remaningMask == 1'b0)));
  assign AlignerPlugin_logic_extractors_0_ctx_instruction = AlignerPlugin_logic_slicesInstructions_0;
  assign AlignerPlugin_logic_extractors_0_ctx_pc = fetch_logic_ctrls_2_down_Fetch_WORD_PC;
  assign AlignerPlugin_logic_extractors_0_ctx_trap = fetch_logic_ctrls_2_down_TRAP;
  assign AlignerPlugin_logic_extractors_0_ctx_hm_Fetch_ID = fetch_logic_ctrls_2_down_Fetch_ID;
  assign AlignerPlugin_logic_extractors_0_ctx_hm_Prediction_WORD_SLICES_BRANCH = fetch_logic_ctrls_2_down_Prediction_WORD_SLICES_BRANCH;
  assign AlignerPlugin_logic_extractors_0_ctx_hm_Prediction_WORD_SLICES_TAKEN = fetch_logic_ctrls_2_down_Prediction_WORD_SLICES_TAKEN;
  assign AlignerPlugin_logic_extractors_0_ctx_hm_Prediction_WORD_JUMP_PC = fetch_logic_ctrls_2_down_Prediction_WORD_JUMP_PC;
  assign AlignerPlugin_logic_extractors_0_ctx_hm_Prediction_WORD_JUMPED = fetch_logic_ctrls_2_down_Prediction_WORD_JUMPED;
  assign AlignerPlugin_api_downMoving = decode_ctrls_0_up_isMoving;
  always @(*) begin
    TrapPlugin_logic_harts_0_crsPorts_read_valid = 1'b0;
    case(TrapPlugin_logic_harts_0_trap_fsm_stateReg)
      TrapPlugin_logic_harts_0_trap_fsm_RUNNING : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1 : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC : begin
        TrapPlugin_logic_harts_0_crsPorts_read_valid = 1'b1;
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC : begin
        TrapPlugin_logic_harts_0_crsPorts_read_valid = 1'b1;
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_JUMP : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH : begin
      end
      default : begin
      end
    endcase
  end

  always @(*) begin
    TrapPlugin_logic_harts_0_crsPorts_read_address = 2'bxx;
    case(TrapPlugin_logic_harts_0_trap_fsm_stateReg)
      TrapPlugin_logic_harts_0_trap_fsm_RUNNING : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1 : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC : begin
        TrapPlugin_logic_harts_0_crsPorts_read_address = 2'b11;
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC : begin
        TrapPlugin_logic_harts_0_crsPorts_read_address = 2'b01;
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_JUMP : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH : begin
      end
      default : begin
      end
    endcase
  end

  assign decode_logic_flushes_0_onLanes_0_doIt = (|{(DecoderPlugin_logic_laneLogic_0_flushPort_valid && 1'b1),{(late0_BranchPlugin_logic_flushPort_valid && 1'b1),{(early0_EnvPlugin_logic_flushPort_valid && 1'b1),{(CsrAccessPlugin_logic_flushPort_valid && 1'b1),{(early0_BranchPlugin_logic_flushPort_valid && 1'b1),(LsuPlugin_logic_flushPort_valid && 1'b1)}}}}});
  assign decode_ctrls_0_lane0_downIsCancel = 1'b0;
  assign decode_ctrls_0_lane0_upIsCancel = decode_logic_flushes_0_onLanes_0_doIt;
  assign decode_logic_flushes_1_onLanes_0_doIt = (|{((DecoderPlugin_logic_laneLogic_0_flushPort_valid && 1'b1) && (1'b0 || (1'b1 && DecoderPlugin_logic_laneLogic_0_flushPort_payload_self))),{(late0_BranchPlugin_logic_flushPort_valid && 1'b1),{(early0_EnvPlugin_logic_flushPort_valid && 1'b1),{(CsrAccessPlugin_logic_flushPort_valid && _zz_decode_logic_flushes_1_onLanes_0_doIt),{_zz_decode_logic_flushes_1_onLanes_0_doIt_1,_zz_decode_logic_flushes_1_onLanes_0_doIt_2}}}}});
  assign decode_ctrls_1_lane0_downIsCancel = 1'b0;
  assign decode_ctrls_1_lane0_upIsCancel = decode_logic_flushes_1_onLanes_0_doIt;
  assign decode_logic_trapPending[0] = (|{((decode_ctrls_1_up_LANE_SEL_0 && 1'b1) && decode_ctrls_1_down_TRAP_0),((decode_ctrls_0_up_LANE_SEL_0 && 1'b1) && decode_ctrls_0_down_TRAP_0)});
  always @(*) begin
    TrapPlugin_logic_harts_0_crsPorts_write_valid = 1'b0;
    case(TrapPlugin_logic_harts_0_trap_fsm_stateReg)
      TrapPlugin_logic_harts_0_trap_fsm_RUNNING : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1 : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC : begin
        TrapPlugin_logic_harts_0_crsPorts_write_valid = 1'b1;
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL : begin
        TrapPlugin_logic_harts_0_crsPorts_write_valid = 1'b1;
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_JUMP : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH : begin
      end
      default : begin
      end
    endcase
  end

  always @(*) begin
    TrapPlugin_logic_harts_0_crsPorts_write_address = 2'bxx;
    case(TrapPlugin_logic_harts_0_trap_fsm_stateReg)
      TrapPlugin_logic_harts_0_trap_fsm_RUNNING : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1 : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC : begin
        TrapPlugin_logic_harts_0_crsPorts_write_address = 2'b01;
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL : begin
        TrapPlugin_logic_harts_0_crsPorts_write_address = 2'b10;
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_JUMP : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH : begin
      end
      default : begin
      end
    endcase
  end

  always @(*) begin
    TrapPlugin_logic_harts_0_crsPorts_write_data = 32'bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx;
    case(TrapPlugin_logic_harts_0_trap_fsm_stateReg)
      TrapPlugin_logic_harts_0_trap_fsm_RUNNING : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1 : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC : begin
        TrapPlugin_logic_harts_0_crsPorts_write_data = TrapPlugin_logic_harts_0_trap_pending_pc;
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL : begin
        TrapPlugin_logic_harts_0_crsPorts_write_data = TrapPlugin_logic_harts_0_trap_fsm_buffer_trap_tval;
        if(TrapPlugin_logic_harts_0_trap_fsm_triggerEbreakReg) begin
          TrapPlugin_logic_harts_0_crsPorts_write_data = TrapPlugin_logic_harts_0_trap_pending_pc;
        end
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_JUMP : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH : begin
      end
      default : begin
      end
    endcase
  end

  always @(*) begin
    TrapPlugin_logic_harts_0_interrupt_valid = 1'b0;
    if(when_TrapPlugin_l201) begin
      if(when_TrapPlugin_l207) begin
        TrapPlugin_logic_harts_0_interrupt_valid = 1'b1;
      end
      if(when_TrapPlugin_l207_1) begin
        TrapPlugin_logic_harts_0_interrupt_valid = 1'b1;
      end
      if(when_TrapPlugin_l207_2) begin
        TrapPlugin_logic_harts_0_interrupt_valid = 1'b1;
      end
    end
  end

  always @(*) begin
    TrapPlugin_logic_harts_0_interrupt_code = 4'bxxxx;
    if(when_TrapPlugin_l201) begin
      if(when_TrapPlugin_l207) begin
        TrapPlugin_logic_harts_0_interrupt_code = 4'b0111;
      end
      if(when_TrapPlugin_l207_1) begin
        TrapPlugin_logic_harts_0_interrupt_code = 4'b0011;
      end
      if(when_TrapPlugin_l207_2) begin
        TrapPlugin_logic_harts_0_interrupt_code = 4'b1011;
      end
    end
  end

  always @(*) begin
    TrapPlugin_logic_harts_0_interrupt_targetPrivilege = 2'bxx;
    if(when_TrapPlugin_l201) begin
      if(when_TrapPlugin_l207) begin
        TrapPlugin_logic_harts_0_interrupt_targetPrivilege = 2'b11;
      end
      if(when_TrapPlugin_l207_1) begin
        TrapPlugin_logic_harts_0_interrupt_targetPrivilege = 2'b11;
      end
      if(when_TrapPlugin_l207_2) begin
        TrapPlugin_logic_harts_0_interrupt_targetPrivilege = 2'b11;
      end
    end
  end

  assign when_TrapPlugin_l201 = (PrivilegedPlugin_logic_harts_0_m_status_mie || (! PrivilegedPlugin_logic_harts_0_withMachinePrivilege));
  assign when_TrapPlugin_l207 = ((_zz_when_TrapPlugin_l207 && 1'b1) && (! 1'b0));
  assign when_TrapPlugin_l207_1 = ((_zz_when_TrapPlugin_l207_1 && 1'b1) && (! 1'b0));
  assign when_TrapPlugin_l207_2 = ((_zz_when_TrapPlugin_l207_2 && 1'b1) && (! 1'b0));
  assign TrapPlugin_logic_harts_0_interrupt_pendingInterrupt = (TrapPlugin_logic_harts_0_interrupt_validBuffer && PrivilegedPlugin_api_harts_0_allowInterrupts);
  assign when_TrapPlugin_l226 = (|{_zz_when_TrapPlugin_l207_2,{_zz_when_TrapPlugin_l207_1,_zz_when_TrapPlugin_l207}});
  assign _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_valid = (early0_EnvPlugin_logic_trapPort_valid && 1'b1);
  assign _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_3_valid = (FetchL1Plugin_logic_trapPort_valid && 1'b1);
  assign _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_valid = (LsuPlugin_logic_trapPort_valid && 1'b1);
  assign _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_valid_1 = (early0_BranchPlugin_logic_trapPort_valid && 1'b1);
  assign _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_valid_2 = (CsrAccessPlugin_logic_trapPort_valid && 1'b1);
  assign _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_valid_1 = (late0_BranchPlugin_logic_trapPort_valid && 1'b1);
  assign _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_2_valid = (DecoderPlugin_logic_laneLogic_0_trapPort_valid && 1'b1);
  assign _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_payload_exception = {(_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_valid_1 && (&(! (_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_valid && 1'b0)))),(_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_valid && (&(! (_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_valid_1 && 1'b0))))};
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_valid = (|{_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_valid_1,_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_valid});
  assign _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_payload_exception_1 = ((_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_payload_exception[0] ? {LsuPlugin_logic_trapPort_payload_arg,{LsuPlugin_logic_trapPort_payload_code,{LsuPlugin_logic_trapPort_payload_tval,LsuPlugin_logic_trapPort_payload_exception}}} : 39'h0) | (_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_payload_exception[1] ? {late0_BranchPlugin_logic_trapPort_payload_arg,{late0_BranchPlugin_logic_trapPort_payload_code,{late0_BranchPlugin_logic_trapPort_payload_tval,late0_BranchPlugin_logic_trapPort_payload_exception}}} : 39'h0));
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_payload_exception = _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_payload_exception_1[0];
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_payload_tval = _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_payload_exception_1[32 : 1];
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_payload_code = _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_payload_exception_1[36 : 33];
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_payload_arg = _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_payload_exception_1[38 : 37];
  assign _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception = {(_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_valid_2 && (&{(! (_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_valid_1 && _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception)),(! (_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_valid && _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_1))})),{(_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_valid_1 && (&{(! _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_2),(! _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_3)})),(_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_valid && (&{(! _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_4),(! _zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_5)}))}};
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_valid = (|{_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_valid_2,{_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_valid_1,_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_valid}});
  assign _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_1 = (((_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception[0] ? {early0_EnvPlugin_logic_trapPort_payload_arg,{early0_EnvPlugin_logic_trapPort_payload_code,{early0_EnvPlugin_logic_trapPort_payload_tval,_zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_1_1}}} : 39'h0) | (_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception[1] ? {early0_BranchPlugin_logic_trapPort_payload_arg,{early0_BranchPlugin_logic_trapPort_payload_code,{early0_BranchPlugin_logic_trapPort_payload_tval,_zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_1_2}}} : 39'h0)) | (_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception[2] ? {CsrAccessPlugin_logic_trapPort_payload_arg,{CsrAccessPlugin_logic_trapPort_payload_code,{CsrAccessPlugin_logic_trapPort_payload_tval,CsrAccessPlugin_logic_trapPort_payload_exception}}} : 39'h0));
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception = _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_1[0];
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_tval = _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_1[32 : 1];
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_code = _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_1[36 : 33];
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_arg = _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_exception_1[38 : 37];
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_2_valid = (|_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_2_valid);
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_2_payload_exception = DecoderPlugin_logic_laneLogic_0_trapPort_payload_exception;
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_2_payload_tval = DecoderPlugin_logic_laneLogic_0_trapPort_payload_tval;
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_2_payload_code = DecoderPlugin_logic_laneLogic_0_trapPort_payload_code;
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_2_payload_arg = DecoderPlugin_logic_laneLogic_0_trapPort_payload_arg;
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_3_valid = (|_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_3_valid);
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_3_payload_exception = FetchL1Plugin_logic_trapPort_payload_exception;
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_3_payload_tval = FetchL1Plugin_logic_trapPort_payload_tval;
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_3_payload_code = FetchL1Plugin_logic_trapPort_payload_code;
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_3_payload_arg = FetchL1Plugin_logic_trapPort_payload_arg;
  assign _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh = {TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_3_valid,{TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_2_valid,{TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_valid,TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_valid}}};
  assign _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh_1 = _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh[0];
  assign _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh_2 = _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh[1];
  assign _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh_3 = _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh[2];
  always @(*) begin
    _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh_4[0] = (_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh_1 && (! 1'b0));
    _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh_4[1] = (_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh_2 && (! _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh_1));
    _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh_4[2] = (_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh_3 && (! (|{_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh_2,_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh_1})));
    _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh_4[3] = (_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh[3] && (! (|{_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh_3,{_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh_2,_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh_1}})));
  end

  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_oh = _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_oh_4;
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_down_valid = (|{_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_2_valid,{_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_valid_1,{_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_valid_2,{_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_valid_1,{_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_valid,{_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_3_valid,_zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_valid}}}}}});
  assign _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_exception = (((TrapPlugin_logic_harts_0_trap_pending_arbiter_oh[0] ? {TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_payload_arg,{TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_0_payload_code,_zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_exception}} : 39'h0) | (TrapPlugin_logic_harts_0_trap_pending_arbiter_oh[1] ? {TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_arg,{TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_1_payload_code,_zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_exception_1}} : 39'h0)) | ((TrapPlugin_logic_harts_0_trap_pending_arbiter_oh[2] ? {TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_2_payload_arg,{TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_2_payload_code,_zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_exception_2}} : 39'h0) | (TrapPlugin_logic_harts_0_trap_pending_arbiter_oh[3] ? {TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_3_payload_arg,{TrapPlugin_logic_harts_0_trap_pending_arbiter_ports_3_payload_code,_zz__zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_exception_3}} : 39'h0)));
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_exception = _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_exception[0];
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_tval = _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_exception[32 : 1];
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_code = _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_exception[36 : 33];
  assign TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_arg = _zz_TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_exception[38 : 37];
  assign TrapPlugin_logic_harts_0_trap_pending_xret_sourcePrivilege = TrapPlugin_logic_harts_0_trap_pending_state_arg[1 : 0];
  assign TrapPlugin_logic_harts_0_trap_pending_xret_targetPrivilege = PrivilegedPlugin_logic_harts_0_m_status_mpp;
  assign TrapPlugin_logic_harts_0_trap_exception_exceptionTargetPrivilegeUncapped = 2'b11;
  assign TrapPlugin_logic_harts_0_trap_exception_code = TrapPlugin_logic_harts_0_trap_pending_state_code;
  assign TrapPlugin_logic_harts_0_trap_exception_targetPrivilege = ((PrivilegedPlugin_logic_harts_0_privilege < TrapPlugin_logic_harts_0_trap_exception_exceptionTargetPrivilegeUncapped) ? TrapPlugin_logic_harts_0_trap_exception_exceptionTargetPrivilegeUncapped : PrivilegedPlugin_logic_harts_0_privilege);
  assign PrivilegedPlugin_logic_harts_0_commitMask = (((execute_ctrl5_down_LANE_SEL_lane0 && execute_ctrl5_down_isReady) && (! execute_lane0_ctrls_5_downIsCancel)) && execute_ctrl5_down_COMMIT_lane0);
  assign TrapPlugin_logic_harts_0_trap_trigger_oh = (((execute_ctrl4_down_LANE_SEL_lane0 && execute_ctrl4_down_isReady) && (! execute_lane0_ctrls_4_downIsCancel)) && execute_ctrl4_down_TRAP_lane0);
  assign TrapPlugin_logic_harts_0_trap_trigger_valid = (|TrapPlugin_logic_harts_0_trap_trigger_oh);
  always @(*) begin
    TrapPlugin_logic_harts_0_trap_whitebox_trap = 1'b0;
    case(TrapPlugin_logic_harts_0_trap_fsm_stateReg)
      TrapPlugin_logic_harts_0_trap_fsm_RUNNING : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1 : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY : begin
        TrapPlugin_logic_harts_0_trap_whitebox_trap = 1'b1;
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_JUMP : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH : begin
      end
      default : begin
      end
    endcase
  end

  always @(*) begin
    TrapPlugin_logic_harts_0_trap_whitebox_interrupt = 1'bx;
    case(TrapPlugin_logic_harts_0_trap_fsm_stateReg)
      TrapPlugin_logic_harts_0_trap_fsm_RUNNING : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1 : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY : begin
        TrapPlugin_logic_harts_0_trap_whitebox_interrupt = TrapPlugin_logic_harts_0_trap_fsm_buffer_trap_interrupt;
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_JUMP : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH : begin
      end
      default : begin
      end
    endcase
  end

  always @(*) begin
    TrapPlugin_logic_harts_0_trap_whitebox_code = 4'bxxxx;
    case(TrapPlugin_logic_harts_0_trap_fsm_stateReg)
      TrapPlugin_logic_harts_0_trap_fsm_RUNNING : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1 : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY : begin
        TrapPlugin_logic_harts_0_trap_whitebox_code = TrapPlugin_logic_harts_0_trap_fsm_buffer_trap_code;
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_JUMP : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH : begin
      end
      default : begin
      end
    endcase
  end

  always @(*) begin
    TrapPlugin_logic_harts_0_trap_pcPort_valid = 1'b0;
    case(TrapPlugin_logic_harts_0_trap_fsm_stateReg)
      TrapPlugin_logic_harts_0_trap_fsm_RUNNING : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1 : begin
        if(!when_TrapPlugin_l409) begin
          case(TrapPlugin_logic_harts_0_trap_pending_state_code)
            4'b0000 : begin
              TrapPlugin_logic_harts_0_trap_pcPort_valid = 1'b1;
            end
            4'b0001 : begin
            end
            4'b0010 : begin
            end
            4'b0100 : begin
            end
            4'b0101 : begin
            end
            4'b1000 : begin
            end
            4'b0110 : begin
            end
            default : begin
            end
          endcase
        end
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY : begin
        TrapPlugin_logic_harts_0_trap_pcPort_valid = 1'b1;
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY : begin
        TrapPlugin_logic_harts_0_trap_pcPort_valid = 1'b1;
      end
      TrapPlugin_logic_harts_0_trap_fsm_JUMP : begin
        TrapPlugin_logic_harts_0_trap_pcPort_valid = 1'b1;
      end
      TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH : begin
      end
      default : begin
      end
    endcase
  end

  assign TrapPlugin_logic_harts_0_trap_pcPort_payload_fault = 1'b0;
  always @(*) begin
    TrapPlugin_logic_harts_0_trap_pcPort_payload_pc = 32'bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx;
    case(TrapPlugin_logic_harts_0_trap_fsm_stateReg)
      TrapPlugin_logic_harts_0_trap_fsm_RUNNING : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1 : begin
        if(!when_TrapPlugin_l409) begin
          case(TrapPlugin_logic_harts_0_trap_pending_state_code)
            4'b0000 : begin
              TrapPlugin_logic_harts_0_trap_pcPort_payload_pc = TrapPlugin_logic_harts_0_trap_pending_pc;
            end
            4'b0001 : begin
            end
            4'b0010 : begin
            end
            4'b0100 : begin
            end
            4'b0101 : begin
            end
            4'b1000 : begin
            end
            4'b0110 : begin
            end
            default : begin
            end
          endcase
        end
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY : begin
        TrapPlugin_logic_harts_0_trap_pcPort_payload_pc = TrapPlugin_logic_harts_0_trap_fsm_readed;
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY : begin
        TrapPlugin_logic_harts_0_trap_pcPort_payload_pc = TrapPlugin_logic_harts_0_trap_fsm_readed;
      end
      TrapPlugin_logic_harts_0_trap_fsm_JUMP : begin
        TrapPlugin_logic_harts_0_trap_pcPort_payload_pc = TrapPlugin_logic_harts_0_trap_fsm_jumpTarget;
      end
      TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH : begin
      end
      default : begin
      end
    endcase
  end

  assign TrapPlugin_logic_harts_0_trap_fsm_wantExit = 1'b0;
  always @(*) begin
    TrapPlugin_logic_harts_0_trap_fsm_wantStart = 1'b0;
    case(TrapPlugin_logic_harts_0_trap_fsm_stateReg)
      TrapPlugin_logic_harts_0_trap_fsm_RUNNING : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1 : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_JUMP : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH : begin
      end
      default : begin
        TrapPlugin_logic_harts_0_trap_fsm_wantStart = 1'b1;
      end
    endcase
  end

  assign TrapPlugin_logic_harts_0_trap_fsm_wantKill = 1'b0;
  assign TrapPlugin_logic_harts_0_trap_fsm_inflightTrap = (|{execute_lane0_logic_trapPending[0],{DispatchPlugin_logic_trapPendings[0],decode_logic_trapPending[0]}});
  assign TrapPlugin_logic_harts_0_trap_fsm_holdPort = (TrapPlugin_logic_harts_0_trap_fsm_inflightTrap || (! (TrapPlugin_logic_harts_0_trap_fsm_stateReg == TrapPlugin_logic_harts_0_trap_fsm_RUNNING)));
  assign TrapPlugin_api_harts_0_fsmBusy = (! (TrapPlugin_logic_harts_0_trap_fsm_stateReg == TrapPlugin_logic_harts_0_trap_fsm_RUNNING));
  always @(*) begin
    TrapPlugin_logic_harts_0_trap_fsm_wfi = 1'b0;
    case(TrapPlugin_logic_harts_0_trap_fsm_stateReg)
      TrapPlugin_logic_harts_0_trap_fsm_RUNNING : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1 : begin
        if(!when_TrapPlugin_l409) begin
          case(TrapPlugin_logic_harts_0_trap_pending_state_code)
            4'b0000 : begin
            end
            4'b0001 : begin
            end
            4'b0010 : begin
            end
            4'b0100 : begin
            end
            4'b0101 : begin
            end
            4'b1000 : begin
              TrapPlugin_logic_harts_0_trap_fsm_wfi = 1'b1;
            end
            4'b0110 : begin
            end
            default : begin
            end
          endcase
        end
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_JUMP : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH : begin
      end
      default : begin
      end
    endcase
  end

  always @(*) begin
    TrapPlugin_logic_harts_0_trap_fsm_buffer_sampleIt = 1'b0;
    case(TrapPlugin_logic_harts_0_trap_fsm_stateReg)
      TrapPlugin_logic_harts_0_trap_fsm_RUNNING : begin
        if(TrapPlugin_logic_harts_0_trap_trigger_valid) begin
          TrapPlugin_logic_harts_0_trap_fsm_buffer_sampleIt = 1'b1;
        end
      end
      TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1 : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_JUMP : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH : begin
      end
      default : begin
      end
    endcase
  end

  assign TrapPlugin_logic_harts_0_trap_fsm_buffer_trap_interrupt = ((TrapPlugin_logic_harts_0_trap_pending_state_code == 4'b0000) && TrapPlugin_logic_harts_0_trap_fsm_buffer_i_valid);
  assign TrapPlugin_logic_harts_0_trap_fsm_buffer_trap_targetPrivilege = (TrapPlugin_logic_harts_0_trap_fsm_buffer_trap_interrupt ? TrapPlugin_logic_harts_0_trap_fsm_buffer_i_targetPrivilege : TrapPlugin_logic_harts_0_trap_exception_targetPrivilege);
  assign TrapPlugin_logic_harts_0_trap_fsm_buffer_trap_tval = ((! TrapPlugin_logic_harts_0_trap_fsm_buffer_trap_interrupt) ? TrapPlugin_logic_harts_0_trap_pending_state_tval : 32'h0);
  assign TrapPlugin_logic_harts_0_trap_fsm_buffer_trap_code = (TrapPlugin_logic_harts_0_trap_fsm_buffer_trap_interrupt ? TrapPlugin_logic_harts_0_trap_fsm_buffer_i_code : TrapPlugin_logic_harts_0_trap_pending_state_code);
  assign TrapPlugin_logic_harts_0_trap_fsm_resetToRunConditions_0 = (! TrapPlugin_logic_initHold);
  assign TrapPlugin_logic_harts_0_trap_fsm_jumpOffset = ((|{(TrapPlugin_logic_harts_0_trap_pending_state_code == 4'b1000),{(TrapPlugin_logic_harts_0_trap_pending_state_code == 4'b0110),{(TrapPlugin_logic_harts_0_trap_pending_state_code == 4'b0010),(TrapPlugin_logic_harts_0_trap_pending_state_code == 4'b0101)}}}) ? TrapPlugin_logic_harts_0_trap_pending_slices : 1'b0);
  always @(*) begin
    TrapPlugin_logic_fetchL1Invalidate_0_cmd_valid = 1'b0;
    case(TrapPlugin_logic_harts_0_trap_fsm_stateReg)
      TrapPlugin_logic_harts_0_trap_fsm_RUNNING : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1 : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_JUMP : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH : begin
        TrapPlugin_logic_fetchL1Invalidate_0_cmd_valid = 1'b1;
      end
      default : begin
      end
    endcase
  end

  always @(*) begin
    TrapPlugin_logic_lsuL1Invalidate_0_cmd_valid = 1'b0;
    case(TrapPlugin_logic_harts_0_trap_fsm_stateReg)
      TrapPlugin_logic_harts_0_trap_fsm_RUNNING : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1 : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_JUMP : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH : begin
        TrapPlugin_logic_lsuL1Invalidate_0_cmd_valid = 1'b1;
      end
      TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH : begin
      end
      default : begin
      end
    endcase
  end

  assign TrapPlugin_logic_harts_0_trap_fsm_triggerEbreak = 1'b0;
  assign when_TrapPlugin_l556 = (TrapPlugin_logic_harts_0_crsPorts_read_valid && TrapPlugin_logic_harts_0_crsPorts_read_ready);
  assign TrapPlugin_logic_harts_0_trap_fsm_xretPrivilege = TrapPlugin_logic_harts_0_trap_pending_state_arg[1 : 0];
  assign PcPlugin_logic_forcedSpawn = (|{TrapPlugin_logic_harts_0_trap_pcPort_valid,{late0_BranchPlugin_logic_pcPort_valid,{early0_BranchPlugin_logic_pcPort_valid,BtbPlugin_logic_pcPort_valid}}});
  assign PcPlugin_logic_harts_0_self_pc = (PcPlugin_logic_harts_0_self_state + _zz_PcPlugin_logic_harts_0_self_pc);
  assign PcPlugin_logic_harts_0_self_flow_valid = 1'b1;
  assign PcPlugin_logic_harts_0_self_flow_payload_fault = PcPlugin_logic_harts_0_self_fault;
  assign PcPlugin_logic_harts_0_self_flow_payload_pc = PcPlugin_logic_harts_0_self_pc;
  assign PcPlugin_logic_harts_0_aggregator_sortedByPriority_3_laneValid = 1'b1;
  assign PcPlugin_logic_harts_0_aggregator_sortedByPriority_2_laneValid = 1'b1;
  assign PcPlugin_logic_harts_0_aggregator_sortedByPriority_1_laneValid = 1'b1;
  assign PcPlugin_logic_harts_0_aggregator_sortedByPriority_0_laneValid = 1'b1;
  assign PcPlugin_logic_harts_0_aggregator_sortedByPriority_4_laneValid = 1'b1;
  assign PcPlugin_logic_harts_0_aggregator_valids_0 = ((TrapPlugin_logic_harts_0_trap_pcPort_valid && 1'b1) && PcPlugin_logic_harts_0_aggregator_sortedByPriority_0_laneValid);
  assign PcPlugin_logic_harts_0_aggregator_valids_1 = ((late0_BranchPlugin_logic_pcPort_valid && 1'b1) && PcPlugin_logic_harts_0_aggregator_sortedByPriority_1_laneValid);
  assign PcPlugin_logic_harts_0_aggregator_valids_2 = ((early0_BranchPlugin_logic_pcPort_valid && 1'b1) && PcPlugin_logic_harts_0_aggregator_sortedByPriority_2_laneValid);
  assign PcPlugin_logic_harts_0_aggregator_valids_3 = ((BtbPlugin_logic_pcPort_valid && 1'b1) && PcPlugin_logic_harts_0_aggregator_sortedByPriority_3_laneValid);
  assign PcPlugin_logic_harts_0_aggregator_valids_4 = ((PcPlugin_logic_harts_0_self_flow_valid && 1'b1) && PcPlugin_logic_harts_0_aggregator_sortedByPriority_4_laneValid);
  assign _zz_PcPlugin_logic_harts_0_aggregator_oh = {PcPlugin_logic_harts_0_aggregator_valids_4,{PcPlugin_logic_harts_0_aggregator_valids_3,{PcPlugin_logic_harts_0_aggregator_valids_2,{PcPlugin_logic_harts_0_aggregator_valids_1,PcPlugin_logic_harts_0_aggregator_valids_0}}}};
  assign _zz_PcPlugin_logic_harts_0_aggregator_oh_1 = _zz_PcPlugin_logic_harts_0_aggregator_oh[0];
  assign _zz_PcPlugin_logic_harts_0_aggregator_oh_2 = _zz_PcPlugin_logic_harts_0_aggregator_oh[1];
  assign _zz_PcPlugin_logic_harts_0_aggregator_oh_3 = _zz_PcPlugin_logic_harts_0_aggregator_oh[2];
  assign _zz_PcPlugin_logic_harts_0_aggregator_oh_4 = _zz_PcPlugin_logic_harts_0_aggregator_oh[3];
  always @(*) begin
    _zz_PcPlugin_logic_harts_0_aggregator_oh_5[0] = (_zz_PcPlugin_logic_harts_0_aggregator_oh_1 && (! 1'b0));
    _zz_PcPlugin_logic_harts_0_aggregator_oh_5[1] = (_zz_PcPlugin_logic_harts_0_aggregator_oh_2 && (! _zz_PcPlugin_logic_harts_0_aggregator_oh_1));
    _zz_PcPlugin_logic_harts_0_aggregator_oh_5[2] = (_zz_PcPlugin_logic_harts_0_aggregator_oh_3 && (! (|{_zz_PcPlugin_logic_harts_0_aggregator_oh_2,_zz_PcPlugin_logic_harts_0_aggregator_oh_1})));
    _zz_PcPlugin_logic_harts_0_aggregator_oh_5[3] = (_zz_PcPlugin_logic_harts_0_aggregator_oh_4 && (! (|{_zz_PcPlugin_logic_harts_0_aggregator_oh_3,{_zz_PcPlugin_logic_harts_0_aggregator_oh_2,_zz_PcPlugin_logic_harts_0_aggregator_oh_1}})));
    _zz_PcPlugin_logic_harts_0_aggregator_oh_5[4] = (_zz_PcPlugin_logic_harts_0_aggregator_oh[4] && (! (|{_zz_PcPlugin_logic_harts_0_aggregator_oh_4,{_zz_PcPlugin_logic_harts_0_aggregator_oh_3,{_zz_PcPlugin_logic_harts_0_aggregator_oh_2,_zz_PcPlugin_logic_harts_0_aggregator_oh_1}}})));
  end

  assign PcPlugin_logic_harts_0_aggregator_oh = _zz_PcPlugin_logic_harts_0_aggregator_oh_5;
  assign _zz_PcPlugin_logic_harts_0_aggregator_target = PcPlugin_logic_harts_0_aggregator_oh[0];
  assign _zz_PcPlugin_logic_harts_0_aggregator_target_1 = PcPlugin_logic_harts_0_aggregator_oh[1];
  assign _zz_PcPlugin_logic_harts_0_aggregator_target_2 = PcPlugin_logic_harts_0_aggregator_oh[2];
  assign _zz_PcPlugin_logic_harts_0_aggregator_target_3 = PcPlugin_logic_harts_0_aggregator_oh[3];
  assign _zz_PcPlugin_logic_harts_0_aggregator_target_4 = PcPlugin_logic_harts_0_aggregator_oh[4];
  assign PcPlugin_logic_harts_0_aggregator_target = ((((_zz_PcPlugin_logic_harts_0_aggregator_target ? TrapPlugin_logic_harts_0_trap_pcPort_payload_pc : 32'h0) | (_zz_PcPlugin_logic_harts_0_aggregator_target_1 ? late0_BranchPlugin_logic_pcPort_payload_pc : 32'h0)) | ((_zz_PcPlugin_logic_harts_0_aggregator_target_2 ? early0_BranchPlugin_logic_pcPort_payload_pc : 32'h0) | (_zz_PcPlugin_logic_harts_0_aggregator_target_3 ? BtbPlugin_logic_pcPort_payload_pc : 32'h0))) | (_zz_PcPlugin_logic_harts_0_aggregator_target_4 ? PcPlugin_logic_harts_0_self_flow_payload_pc : 32'h0));
  assign PcPlugin_logic_harts_0_aggregator_fault = _zz_PcPlugin_logic_harts_0_aggregator_fault[0];
  assign PcPlugin_logic_harts_0_holdComb = (|TrapPlugin_logic_harts_0_trap_fsm_holdPort);
  assign PcPlugin_logic_harts_0_output_valid = (! PcPlugin_logic_harts_0_holdReg);
  assign PcPlugin_logic_harts_0_output_payload_fault = PcPlugin_logic_harts_0_aggregator_fault;
  always @(*) begin
    PcPlugin_logic_harts_0_output_payload_pc = PcPlugin_logic_harts_0_aggregator_target;
    PcPlugin_logic_harts_0_output_payload_pc[1 : 0] = 2'b00;
  end

  assign PcPlugin_logic_harts_0_output_fire = (PcPlugin_logic_harts_0_output_valid && PcPlugin_logic_harts_0_output_ready);
  assign fetch_logic_ctrls_0_up_valid = PcPlugin_logic_harts_0_output_valid;
  assign PcPlugin_logic_harts_0_output_ready = fetch_logic_ctrls_0_up_ready;
  assign fetch_logic_ctrls_0_up_Fetch_WORD_PC = PcPlugin_logic_harts_0_output_payload_pc;
  assign fetch_logic_ctrls_0_up_Fetch_PC_FAULT = PcPlugin_logic_harts_0_output_payload_fault;
  always @(*) begin
    fetch_logic_ctrls_0_up_Fetch_ID = 10'bxxxxxxxxxx;
    fetch_logic_ctrls_0_up_Fetch_ID = PcPlugin_logic_harts_0_self_id;
  end

  assign PcPlugin_logic_holdHalter_doIt = PcPlugin_logic_harts_0_holdComb;
  assign fetch_logic_ctrls_0_haltRequest_PcPlugin_l133 = PcPlugin_logic_holdHalter_doIt;
  assign CsrAccessPlugin_logic_fsm_wantExit = 1'b0;
  always @(*) begin
    CsrAccessPlugin_logic_fsm_wantStart = 1'b0;
    case(CsrAccessPlugin_logic_fsm_stateReg)
      CsrAccessPlugin_logic_fsm_READ : begin
      end
      CsrAccessPlugin_logic_fsm_WRITE : begin
      end
      CsrAccessPlugin_logic_fsm_COMPLETION : begin
      end
      default : begin
        CsrAccessPlugin_logic_fsm_wantStart = 1'b1;
      end
    endcase
  end

  assign CsrAccessPlugin_logic_fsm_wantKill = 1'b0;
  always @(*) begin
    CsrAccessPlugin_logic_fsm_interface_fire = 1'b0;
    case(CsrAccessPlugin_logic_fsm_stateReg)
      CsrAccessPlugin_logic_fsm_READ : begin
      end
      CsrAccessPlugin_logic_fsm_WRITE : begin
      end
      CsrAccessPlugin_logic_fsm_COMPLETION : begin
        if(execute_ctrl2_down_isReady) begin
          CsrAccessPlugin_logic_fsm_interface_fire = 1'b1;
        end
      end
      default : begin
      end
    endcase
  end

  assign CsrAccessPlugin_logic_fsm_inject_csrAddress = execute_ctrl2_down_Decode_UOP_lane0[31 : 20];
  assign CsrAccessPlugin_logic_fsm_inject_immZero = (execute_ctrl2_down_Decode_UOP_lane0[19 : 15] == 5'h0);
  assign CsrAccessPlugin_logic_fsm_inject_srcZero = (execute_ctrl2_down_CsrAccessPlugin_CSR_IMM_lane0 ? CsrAccessPlugin_logic_fsm_inject_immZero : (execute_ctrl2_down_Decode_UOP_lane0[19 : 15] == 5'h0));
  assign CsrAccessPlugin_logic_fsm_inject_csrWrite = (! (execute_ctrl2_down_CsrAccessPlugin_CSR_MASK_lane0 && CsrAccessPlugin_logic_fsm_inject_srcZero));
  assign CsrAccessPlugin_logic_fsm_inject_csrRead = (! ((! execute_ctrl2_down_CsrAccessPlugin_CSR_MASK_lane0) && (! execute_ctrl2_up_RD_ENABLE_lane0)));
  assign COMB_CSR_1952 = (CsrAccessPlugin_logic_fsm_inject_csrAddress == 12'h7a0);
  assign COMB_CSR_1953 = (CsrAccessPlugin_logic_fsm_inject_csrAddress == 12'h7a1);
  assign COMB_CSR_1954 = (CsrAccessPlugin_logic_fsm_inject_csrAddress == 12'h7a2);
  assign COMB_CSR_3857 = (CsrAccessPlugin_logic_fsm_inject_csrAddress == 12'hf11);
  assign COMB_CSR_3858 = (CsrAccessPlugin_logic_fsm_inject_csrAddress == 12'hf12);
  assign COMB_CSR_3859 = (CsrAccessPlugin_logic_fsm_inject_csrAddress == 12'hf13);
  assign COMB_CSR_3860 = (CsrAccessPlugin_logic_fsm_inject_csrAddress == 12'hf14);
  assign COMB_CSR_769 = (CsrAccessPlugin_logic_fsm_inject_csrAddress == 12'h301);
  assign COMB_CSR_768 = (CsrAccessPlugin_logic_fsm_inject_csrAddress == 12'h300);
  assign COMB_CSR_834 = (CsrAccessPlugin_logic_fsm_inject_csrAddress == 12'h342);
  assign COMB_CSR_836 = (CsrAccessPlugin_logic_fsm_inject_csrAddress == 12'h344);
  assign COMB_CSR_772 = (CsrAccessPlugin_logic_fsm_inject_csrAddress == 12'h304);
  assign COMB_CSR_PrivilegedPlugin_logic_readAnyWriteLegal_tvecFilter = (|(CsrAccessPlugin_logic_fsm_inject_csrAddress == 12'h305));
  assign COMB_CSR_PrivilegedPlugin_logic_readAnyWriteLegal_epcFilter = (|(CsrAccessPlugin_logic_fsm_inject_csrAddress == 12'h341));
  assign COMB_CSR_CsrRamPlugin_csrMapper_selFilter = (|{(CsrAccessPlugin_logic_fsm_inject_csrAddress == 12'h340),{(CsrAccessPlugin_logic_fsm_inject_csrAddress == 12'h341),{(CsrAccessPlugin_logic_fsm_inject_csrAddress == 12'h343),(CsrAccessPlugin_logic_fsm_inject_csrAddress == 12'h305)}}});
  assign COMB_CSR_CsrAccessPlugin_logic_trapNextOnWriteFilter = (|(CsrAccessPlugin_logic_fsm_inject_csrAddress == 12'h300));
  assign CsrAccessPlugin_logic_fsm_inject_implemented = (|{COMB_CSR_CsrAccessPlugin_logic_trapNextOnWriteFilter,{COMB_CSR_CsrRamPlugin_csrMapper_selFilter,{COMB_CSR_PrivilegedPlugin_logic_readAnyWriteLegal_epcFilter,{COMB_CSR_PrivilegedPlugin_logic_readAnyWriteLegal_tvecFilter,{COMB_CSR_772,{COMB_CSR_836,{COMB_CSR_834,{COMB_CSR_768,{COMB_CSR_769,{COMB_CSR_3860,{_zz_CsrAccessPlugin_logic_fsm_inject_implemented,_zz_CsrAccessPlugin_logic_fsm_inject_implemented_1}}}}}}}}}}});
  assign CsrAccessPlugin_logic_fsm_inject_onDecodeDo = ((execute_ctrl2_up_LANE_SEL_lane0 && execute_ctrl2_down_CsrAccessPlugin_SEL_lane0) && (CsrAccessPlugin_logic_fsm_stateReg == CsrAccessPlugin_logic_fsm_IDLE));
  assign when_CsrAccessPlugin_l155 = (CsrAccessPlugin_logic_fsm_inject_onDecodeDo && COMB_CSR_CsrAccessPlugin_logic_trapNextOnWriteFilter);
  assign CsrAccessPlugin_logic_fsm_inject_trap = ((! CsrAccessPlugin_logic_fsm_inject_implemented) || CsrAccessPlugin_bus_decode_exception);
  assign CsrAccessPlugin_bus_decode_read = CsrAccessPlugin_logic_fsm_inject_csrRead;
  assign CsrAccessPlugin_bus_decode_write = CsrAccessPlugin_logic_fsm_inject_csrWrite;
  assign CsrAccessPlugin_bus_decode_address = CsrAccessPlugin_logic_fsm_inject_csrAddress;
  assign CsrAccessPlugin_logic_fsm_interface_uopId = execute_ctrl2_down_Decode_UOP_ID_lane0;
  assign CsrAccessPlugin_logic_fsm_interface_rs1 = execute_ctrl2_up_integer_RS1_lane0;
  assign CsrAccessPlugin_logic_fsm_interface_uop = execute_ctrl2_down_Decode_UOP_lane0;
  assign CsrAccessPlugin_logic_fsm_interface_doImm = execute_ctrl2_down_CsrAccessPlugin_CSR_IMM_lane0;
  assign CsrAccessPlugin_logic_fsm_interface_doMask = execute_ctrl2_down_CsrAccessPlugin_CSR_MASK_lane0;
  assign CsrAccessPlugin_logic_fsm_interface_doClear = execute_ctrl2_down_CsrAccessPlugin_CSR_CLEAR_lane0;
  assign CsrAccessPlugin_logic_fsm_interface_rdEnable = execute_ctrl2_up_RD_ENABLE_lane0;
  assign CsrAccessPlugin_logic_fsm_interface_rdPhys = execute_ctrl2_down_RD_PHYS_lane0;
  assign CsrAccessPlugin_logic_fsm_inject_freeze = ((execute_ctrl2_up_LANE_SEL_lane0 && execute_ctrl2_down_CsrAccessPlugin_SEL_lane0) && (! CsrAccessPlugin_logic_fsm_inject_unfreeze));
  always @(*) begin
    CsrAccessPlugin_logic_flushPort_valid = 1'b0;
    if(CsrAccessPlugin_logic_fsm_inject_flushReg) begin
      CsrAccessPlugin_logic_flushPort_valid = 1'b1;
    end
    case(CsrAccessPlugin_logic_fsm_stateReg)
      CsrAccessPlugin_logic_fsm_READ : begin
      end
      CsrAccessPlugin_logic_fsm_WRITE : begin
      end
      CsrAccessPlugin_logic_fsm_COMPLETION : begin
      end
      default : begin
        if(CsrAccessPlugin_logic_fsm_inject_onDecodeDo) begin
          if(CsrAccessPlugin_logic_fsm_inject_sampled) begin
            if(CsrAccessPlugin_logic_fsm_inject_trapReg) begin
              CsrAccessPlugin_logic_flushPort_valid = 1'b1;
            end else begin
              if(CsrAccessPlugin_logic_fsm_inject_busTrapReg) begin
                CsrAccessPlugin_logic_flushPort_valid = 1'b1;
              end
            end
          end
        end
      end
    endcase
  end

  assign CsrAccessPlugin_logic_flushPort_payload_uopId = execute_ctrl2_down_Decode_UOP_ID_lane0;
  assign CsrAccessPlugin_logic_flushPort_payload_self = 1'b0;
  always @(*) begin
    CsrAccessPlugin_logic_trapPort_valid = 1'b0;
    case(CsrAccessPlugin_logic_fsm_stateReg)
      CsrAccessPlugin_logic_fsm_READ : begin
      end
      CsrAccessPlugin_logic_fsm_WRITE : begin
      end
      CsrAccessPlugin_logic_fsm_COMPLETION : begin
      end
      default : begin
        if(CsrAccessPlugin_logic_fsm_inject_onDecodeDo) begin
          if(CsrAccessPlugin_logic_fsm_inject_sampled) begin
            if(CsrAccessPlugin_logic_fsm_inject_trapReg) begin
              CsrAccessPlugin_logic_trapPort_valid = 1'b1;
            end else begin
              if(CsrAccessPlugin_logic_fsm_inject_busTrapReg) begin
                CsrAccessPlugin_logic_trapPort_valid = 1'b1;
              end
            end
          end
        end
      end
    endcase
  end

  always @(*) begin
    CsrAccessPlugin_logic_trapPort_payload_exception = 1'b1;
    case(CsrAccessPlugin_logic_fsm_stateReg)
      CsrAccessPlugin_logic_fsm_READ : begin
      end
      CsrAccessPlugin_logic_fsm_WRITE : begin
      end
      CsrAccessPlugin_logic_fsm_COMPLETION : begin
      end
      default : begin
        if(CsrAccessPlugin_logic_fsm_inject_onDecodeDo) begin
          if(CsrAccessPlugin_logic_fsm_inject_sampled) begin
            if(!CsrAccessPlugin_logic_fsm_inject_trapReg) begin
              if(CsrAccessPlugin_logic_fsm_inject_busTrapReg) begin
                CsrAccessPlugin_logic_trapPort_payload_exception = 1'b0;
              end
            end
          end
        end
      end
    endcase
  end

  always @(*) begin
    CsrAccessPlugin_logic_trapPort_payload_code = 4'b0010;
    case(CsrAccessPlugin_logic_fsm_stateReg)
      CsrAccessPlugin_logic_fsm_READ : begin
      end
      CsrAccessPlugin_logic_fsm_WRITE : begin
      end
      CsrAccessPlugin_logic_fsm_COMPLETION : begin
      end
      default : begin
        if(CsrAccessPlugin_logic_fsm_inject_onDecodeDo) begin
          if(CsrAccessPlugin_logic_fsm_inject_sampled) begin
            if(!CsrAccessPlugin_logic_fsm_inject_trapReg) begin
              if(CsrAccessPlugin_logic_fsm_inject_busTrapReg) begin
                CsrAccessPlugin_logic_trapPort_payload_code = CsrAccessPlugin_logic_fsm_inject_busTrapCodeReg;
              end
            end
          end
        end
      end
    endcase
  end

  assign CsrAccessPlugin_logic_trapPort_payload_tval = execute_ctrl2_down_Decode_UOP_lane0;
  assign CsrAccessPlugin_logic_trapPort_payload_arg = 2'b00;
  assign when_CsrAccessPlugin_l197 = (! execute_freeze_valid);
  always @(*) begin
    CsrAccessPlugin_logic_fsm_readLogic_onReadsDo = 1'b0;
    case(CsrAccessPlugin_logic_fsm_stateReg)
      CsrAccessPlugin_logic_fsm_READ : begin
        CsrAccessPlugin_logic_fsm_readLogic_onReadsDo = CsrAccessPlugin_logic_fsm_interface_read;
      end
      CsrAccessPlugin_logic_fsm_WRITE : begin
      end
      CsrAccessPlugin_logic_fsm_COMPLETION : begin
      end
      default : begin
      end
    endcase
  end

  always @(*) begin
    CsrAccessPlugin_logic_fsm_readLogic_onReadsFireDo = 1'b0;
    case(CsrAccessPlugin_logic_fsm_stateReg)
      CsrAccessPlugin_logic_fsm_READ : begin
        if(when_CsrAccessPlugin_l296) begin
          CsrAccessPlugin_logic_fsm_readLogic_onReadsFireDo = CsrAccessPlugin_logic_fsm_interface_read;
        end
      end
      CsrAccessPlugin_logic_fsm_WRITE : begin
      end
      CsrAccessPlugin_logic_fsm_COMPLETION : begin
      end
      default : begin
      end
    endcase
  end

  assign CsrAccessPlugin_bus_read_valid = CsrAccessPlugin_logic_fsm_readLogic_onReadsDo;
  assign CsrAccessPlugin_bus_read_address = CsrAccessPlugin_logic_fsm_interface_uop[31 : 20];
  assign CsrAccessPlugin_bus_read_moving = (! CsrAccessPlugin_bus_read_halt);
  assign when_CsrAccessPlugin_l252 = (CsrAccessPlugin_logic_fsm_readLogic_onReadsDo && REG_CSR_CsrRamPlugin_csrMapper_selFilter);
  assign CsrAccessPlugin_logic_fsm_readLogic_csrValue = (((((32'h0 | _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_5) | (32'h0 | 32'h0)) | ((((_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue && REG_CSR_769) ? _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_7 : 32'h0) | _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_8) | (_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_10 | _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_12))) | (((_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_14 | _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_15) | (_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_17 | _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_18)) | ((_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_20 | _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_22) | (_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_24 | _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_26)))) | ((_zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_28 | _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue_30) | (CsrRamPlugin_csrMapper_withRead ? CsrRamPlugin_csrMapper_read_data : 32'h0)));
  assign CsrAccessPlugin_bus_read_data = CsrAccessPlugin_logic_fsm_readLogic_csrValue;
  assign CsrAccessPlugin_bus_read_toWriteBits = CsrAccessPlugin_logic_fsm_readLogic_csrValue;
  assign _zz_CsrAccessPlugin_logic_fsm_readLogic_csrValue = 1'b1;
  assign CsrAccessPlugin_bus_write_moving = (! CsrAccessPlugin_bus_write_halt);
  assign CsrAccessPlugin_logic_fsm_writeLogic_alu_mask = (CsrAccessPlugin_logic_fsm_interface_doImm ? _zz_CsrAccessPlugin_logic_fsm_writeLogic_alu_mask : CsrAccessPlugin_logic_fsm_interface_rs1);
  assign CsrAccessPlugin_logic_fsm_writeLogic_alu_masked = (CsrAccessPlugin_logic_fsm_interface_doClear ? (CsrAccessPlugin_logic_fsm_interface_aluInput & (~ CsrAccessPlugin_logic_fsm_writeLogic_alu_mask)) : (CsrAccessPlugin_logic_fsm_interface_aluInput | CsrAccessPlugin_logic_fsm_writeLogic_alu_mask));
  assign CsrAccessPlugin_logic_fsm_writeLogic_alu_result = (CsrAccessPlugin_logic_fsm_interface_doMask ? CsrAccessPlugin_logic_fsm_writeLogic_alu_masked : CsrAccessPlugin_logic_fsm_writeLogic_alu_mask);
  always @(*) begin
    CsrAccessPlugin_bus_write_bits = CsrAccessPlugin_logic_fsm_writeLogic_alu_result;
    if(when_CsrAccessPlugin_l343) begin
      CsrAccessPlugin_bus_write_bits[1 : 0] = 2'b00;
    end
    if(when_CsrAccessPlugin_l343_1) begin
      CsrAccessPlugin_bus_write_bits[1 : 0] = 2'b00;
    end
  end

  assign CsrAccessPlugin_bus_write_address = CsrAccessPlugin_logic_fsm_interface_uop[31 : 20];
  always @(*) begin
    CsrAccessPlugin_logic_fsm_writeLogic_onWritesDo = 1'b0;
    case(CsrAccessPlugin_logic_fsm_stateReg)
      CsrAccessPlugin_logic_fsm_READ : begin
      end
      CsrAccessPlugin_logic_fsm_WRITE : begin
        CsrAccessPlugin_logic_fsm_writeLogic_onWritesDo = CsrAccessPlugin_logic_fsm_interface_write;
      end
      CsrAccessPlugin_logic_fsm_COMPLETION : begin
      end
      default : begin
      end
    endcase
  end

  always @(*) begin
    CsrAccessPlugin_logic_fsm_writeLogic_onWritesFireDo = 1'b0;
    case(CsrAccessPlugin_logic_fsm_stateReg)
      CsrAccessPlugin_logic_fsm_READ : begin
      end
      CsrAccessPlugin_logic_fsm_WRITE : begin
        if(when_CsrAccessPlugin_l325) begin
          CsrAccessPlugin_logic_fsm_writeLogic_onWritesFireDo = CsrAccessPlugin_logic_fsm_interface_write;
        end
      end
      CsrAccessPlugin_logic_fsm_COMPLETION : begin
      end
      default : begin
      end
    endcase
  end

  assign CsrAccessPlugin_bus_write_valid = CsrAccessPlugin_logic_fsm_writeLogic_onWritesDo;
  assign when_CsrAccessPlugin_l346 = (CsrAccessPlugin_logic_fsm_writeLogic_onWritesFireDo && REG_CSR_768);
  assign when_CsrAccessPlugin_l346_1 = (CsrAccessPlugin_logic_fsm_writeLogic_onWritesFireDo && REG_CSR_834);
  assign when_CsrAccessPlugin_l346_2 = (CsrAccessPlugin_logic_fsm_writeLogic_onWritesFireDo && REG_CSR_772);
  assign when_CsrAccessPlugin_l343 = (CsrAccessPlugin_logic_fsm_writeLogic_onWritesDo && REG_CSR_PrivilegedPlugin_logic_readAnyWriteLegal_tvecFilter);
  assign when_CsrAccessPlugin_l343_1 = (CsrAccessPlugin_logic_fsm_writeLogic_onWritesDo && REG_CSR_PrivilegedPlugin_logic_readAnyWriteLegal_epcFilter);
  assign when_CsrAccessPlugin_l343_2 = (CsrAccessPlugin_logic_fsm_writeLogic_onWritesDo && REG_CSR_CsrRamPlugin_csrMapper_selFilter);
  assign CsrAccessPlugin_logic_wbWi_valid = execute_ctrl3_down_CsrAccessPlugin_SEL_lane0;
  assign CsrAccessPlugin_logic_wbWi_payload = CsrAccessPlugin_logic_fsm_interface_csrValue;
  assign fetch_logic_ctrls_1_down_MMU_REFILL = 1'b0;
  assign fetch_logic_ctrls_1_down_MMU_HAZARD = 1'b0;
  assign fetch_logic_ctrls_1_down_MMU_TRANSLATED = fetch_logic_ctrls_1_down_Fetch_WORD_PC;
  assign fetch_logic_ctrls_1_down_MMU_ALLOW_EXECUTE = 1'b1;
  assign fetch_logic_ctrls_1_down_MMU_ALLOW_READ = 1'b1;
  assign fetch_logic_ctrls_1_down_MMU_ALLOW_WRITE = 1'b1;
  assign fetch_logic_ctrls_1_down_MMU_PAGE_FAULT = 1'b0;
  assign fetch_logic_ctrls_1_down_MMU_ACCESS_FAULT = 1'b0;
  assign fetch_logic_ctrls_1_down_MMU_BYPASS_TRANSLATION = 1'b1;
  assign execute_ctrl3_down_MMU_REFILL_lane0 = 1'b0;
  assign execute_ctrl3_down_MMU_HAZARD_lane0 = 1'b0;
  assign execute_ctrl3_down_MMU_TRANSLATED_lane0 = execute_ctrl3_down_LsuL1_MIXED_ADDRESS_lane0;
  assign execute_ctrl3_down_MMU_ALLOW_EXECUTE_lane0 = 1'b1;
  assign execute_ctrl3_down_MMU_ALLOW_READ_lane0 = 1'b1;
  assign execute_ctrl3_down_MMU_ALLOW_WRITE_lane0 = 1'b1;
  assign execute_ctrl3_down_MMU_PAGE_FAULT_lane0 = 1'b0;
  assign execute_ctrl3_down_MMU_ACCESS_FAULT_lane0 = 1'b0;
  assign execute_ctrl3_down_MMU_BYPASS_TRANSLATION_lane0 = 1'b1;
  assign fetch_logic_flushes_0_doIt = (|{(DecoderPlugin_logic_laneLogic_0_flushPort_valid && 1'b1),{(late0_BranchPlugin_logic_flushPort_valid && 1'b1),{(early0_EnvPlugin_logic_flushPort_valid && 1'b1),{(CsrAccessPlugin_logic_flushPort_valid && 1'b1),{(early0_BranchPlugin_logic_flushPort_valid && 1'b1),{(LsuPlugin_logic_flushPort_valid && _zz_fetch_logic_flushes_0_doIt),(BtbPlugin_logic_flushPort_valid && _zz_fetch_logic_flushes_0_doIt_1)}}}}}});
  assign fetch_logic_ctrls_1_throwWhen_FetchPipelinePlugin_l48 = fetch_logic_flushes_0_doIt;
  assign fetch_logic_flushes_1_doIt = (|{(DecoderPlugin_logic_laneLogic_0_flushPort_valid && 1'b1),{(late0_BranchPlugin_logic_flushPort_valid && 1'b1),{(early0_EnvPlugin_logic_flushPort_valid && 1'b1),{(CsrAccessPlugin_logic_flushPort_valid && 1'b1),{(early0_BranchPlugin_logic_flushPort_valid && 1'b1),{(LsuPlugin_logic_flushPort_valid && _zz_fetch_logic_flushes_1_doIt),(_zz_fetch_logic_flushes_1_doIt_1 && _zz_fetch_logic_flushes_1_doIt_2)}}}}}});
  assign fetch_logic_ctrls_2_forgetsSingleRequest_FetchPipelinePlugin_l50 = fetch_logic_flushes_1_doIt;
  assign CsrRamPlugin_logic_writeLogic_hits = {CsrRamPlugin_setup_initPort_valid,{CsrRamPlugin_csrMapper_write_valid,TrapPlugin_logic_harts_0_crsPorts_write_valid}};
  assign CsrRamPlugin_logic_writeLogic_hit = (|CsrRamPlugin_logic_writeLogic_hits);
  assign CsrRamPlugin_logic_writeLogic_hits_ohFirst_input = CsrRamPlugin_logic_writeLogic_hits;
  assign CsrRamPlugin_logic_writeLogic_hits_ohFirst_masked = (CsrRamPlugin_logic_writeLogic_hits_ohFirst_input & (~ _zz_CsrRamPlugin_logic_writeLogic_hits_ohFirst_masked));
  assign CsrRamPlugin_logic_writeLogic_oh = CsrRamPlugin_logic_writeLogic_hits_ohFirst_masked;
  assign _zz_TrapPlugin_logic_harts_0_crsPorts_write_ready = CsrRamPlugin_logic_writeLogic_oh[0];
  assign _zz_CsrRamPlugin_csrMapper_write_ready = CsrRamPlugin_logic_writeLogic_oh[1];
  assign _zz_CsrRamPlugin_setup_initPort_ready = CsrRamPlugin_logic_writeLogic_oh[2];
  assign CsrRamPlugin_logic_writeLogic_port_valid = CsrRamPlugin_logic_writeLogic_hit;
  assign CsrRamPlugin_logic_writeLogic_port_payload_address = (((_zz_TrapPlugin_logic_harts_0_crsPorts_write_ready ? TrapPlugin_logic_harts_0_crsPorts_write_address : 2'b00) | (_zz_CsrRamPlugin_csrMapper_write_ready ? CsrRamPlugin_csrMapper_write_address : 2'b00)) | (_zz_CsrRamPlugin_setup_initPort_ready ? CsrRamPlugin_setup_initPort_address : 2'b00));
  assign CsrRamPlugin_logic_writeLogic_port_payload_data = (((_zz_TrapPlugin_logic_harts_0_crsPorts_write_ready ? TrapPlugin_logic_harts_0_crsPorts_write_data : 32'h0) | (_zz_CsrRamPlugin_csrMapper_write_ready ? CsrRamPlugin_csrMapper_write_data : 32'h0)) | (_zz_CsrRamPlugin_setup_initPort_ready ? CsrRamPlugin_setup_initPort_data : 32'h0));
  assign TrapPlugin_logic_harts_0_crsPorts_write_ready = _zz_TrapPlugin_logic_harts_0_crsPorts_write_ready;
  assign CsrRamPlugin_csrMapper_write_ready = _zz_CsrRamPlugin_csrMapper_write_ready;
  assign CsrRamPlugin_setup_initPort_ready = _zz_CsrRamPlugin_setup_initPort_ready;
  assign CsrRamPlugin_logic_readLogic_hits = {CsrRamPlugin_csrMapper_read_valid,TrapPlugin_logic_harts_0_crsPorts_read_valid};
  assign CsrRamPlugin_logic_readLogic_hit = (|CsrRamPlugin_logic_readLogic_hits);
  assign CsrRamPlugin_logic_readLogic_hits_ohFirst_input = CsrRamPlugin_logic_readLogic_hits;
  assign CsrRamPlugin_logic_readLogic_hits_ohFirst_masked = (CsrRamPlugin_logic_readLogic_hits_ohFirst_input & (~ _zz_CsrRamPlugin_logic_readLogic_hits_ohFirst_masked));
  assign CsrRamPlugin_logic_readLogic_oh = CsrRamPlugin_logic_readLogic_hits_ohFirst_masked;
  assign _zz_CsrRamPlugin_logic_readLogic_sel = CsrRamPlugin_logic_readLogic_oh[1];
  assign CsrRamPlugin_logic_readLogic_sel = _zz_CsrRamPlugin_logic_readLogic_sel;
  assign CsrRamPlugin_logic_readLogic_port_rsp = CsrRamPlugin_logic_mem_spinal_port1;
  assign CsrRamPlugin_logic_readLogic_port_cmd_valid = (((|CsrRamPlugin_logic_readLogic_oh) && (! CsrRamPlugin_logic_writeLogic_port_valid)) && (! CsrRamPlugin_logic_readLogic_busy));
  assign CsrRamPlugin_logic_readLogic_port_cmd_payload = _zz_CsrRamPlugin_logic_readLogic_port_cmd_payload;
  assign TrapPlugin_logic_harts_0_crsPorts_read_ready = CsrRamPlugin_logic_readLogic_ohReg[0];
  assign CsrRamPlugin_csrMapper_read_ready = CsrRamPlugin_logic_readLogic_ohReg[1];
  assign TrapPlugin_logic_harts_0_crsPorts_read_data = CsrRamPlugin_logic_readLogic_port_rsp;
  assign CsrRamPlugin_csrMapper_read_data = CsrRamPlugin_logic_readLogic_port_rsp;
  assign CsrRamPlugin_logic_flush_done = CsrRamPlugin_logic_flush_counter[2];
  assign CsrRamPlugin_setup_initPort_valid = (! CsrRamPlugin_logic_flush_done);
  assign CsrRamPlugin_setup_initPort_address = CsrRamPlugin_logic_flush_counter[1:0];
  assign CsrRamPlugin_setup_initPort_data = 32'h0;
  assign execute_lane0_bypasser_integer_RS1_port_valid = (! execute_freeze_valid);
  assign execute_lane0_bypasser_integer_RS1_port_address = execute_ctrl0_down_RS1_PHYS_lane0;
  always @(*) begin
    execute_lane0_bypasser_integer_RS1_bypassEnables[0] = (((execute_ctrl2_up_LANE_SEL_lane0 && execute_ctrl2_up_RD_ENABLE_lane0) && (execute_ctrl2_down_RD_PHYS_lane0 == execute_ctrl1_down_RS1_PHYS_lane0)) && 1'b1);
    execute_lane0_bypasser_integer_RS1_bypassEnables[1] = (((execute_ctrl3_up_LANE_SEL_lane0 && execute_ctrl3_up_RD_ENABLE_lane0) && (execute_ctrl3_down_RD_PHYS_lane0 == execute_ctrl1_down_RS1_PHYS_lane0)) && 1'b1);
    execute_lane0_bypasser_integer_RS1_bypassEnables[2] = (((execute_ctrl4_up_LANE_SEL_lane0 && execute_ctrl4_up_RD_ENABLE_lane0) && (execute_ctrl4_down_RD_PHYS_lane0 == execute_ctrl1_down_RS1_PHYS_lane0)) && 1'b1);
    execute_lane0_bypasser_integer_RS1_bypassEnables[3] = (((execute_ctrl5_up_LANE_SEL_lane0 && execute_ctrl5_up_RD_ENABLE_lane0) && (execute_ctrl5_down_RD_PHYS_lane0 == execute_ctrl1_down_RS1_PHYS_lane0)) && 1'b1);
    execute_lane0_bypasser_integer_RS1_bypassEnables[4] = 1'b1;
  end

  assign _zz_execute_lane0_bypasser_integer_RS1_bypassEnables_bools_0 = execute_lane0_bypasser_integer_RS1_bypassEnables;
  assign execute_lane0_bypasser_integer_RS1_bypassEnables_bools_0 = _zz_execute_lane0_bypasser_integer_RS1_bypassEnables_bools_0[0];
  assign execute_lane0_bypasser_integer_RS1_bypassEnables_bools_1 = _zz_execute_lane0_bypasser_integer_RS1_bypassEnables_bools_0[1];
  assign execute_lane0_bypasser_integer_RS1_bypassEnables_bools_2 = _zz_execute_lane0_bypasser_integer_RS1_bypassEnables_bools_0[2];
  assign execute_lane0_bypasser_integer_RS1_bypassEnables_bools_3 = _zz_execute_lane0_bypasser_integer_RS1_bypassEnables_bools_0[3];
  assign execute_lane0_bypasser_integer_RS1_bypassEnables_bools_4 = _zz_execute_lane0_bypasser_integer_RS1_bypassEnables_bools_0[4];
  always @(*) begin
    _zz_execute_lane0_bypasser_integer_RS1_sel[0] = (execute_lane0_bypasser_integer_RS1_bypassEnables_bools_0 && (! 1'b0));
    _zz_execute_lane0_bypasser_integer_RS1_sel[1] = (execute_lane0_bypasser_integer_RS1_bypassEnables_bools_1 && (! execute_lane0_bypasser_integer_RS1_bypassEnables_bools_0));
    _zz_execute_lane0_bypasser_integer_RS1_sel[2] = (execute_lane0_bypasser_integer_RS1_bypassEnables_bools_2 && (! execute_lane0_bypasser_integer_RS1_bypassEnables_range_0_to_1));
    _zz_execute_lane0_bypasser_integer_RS1_sel[3] = (execute_lane0_bypasser_integer_RS1_bypassEnables_bools_3 && (! execute_lane0_bypasser_integer_RS1_bypassEnables_range_0_to_2));
    _zz_execute_lane0_bypasser_integer_RS1_sel[4] = (execute_lane0_bypasser_integer_RS1_bypassEnables_bools_4 && (! execute_lane0_bypasser_integer_RS1_bypassEnables_range_0_to_3));
  end

  assign execute_lane0_bypasser_integer_RS1_bypassEnables_range_0_to_1 = (|{execute_lane0_bypasser_integer_RS1_bypassEnables_bools_1,execute_lane0_bypasser_integer_RS1_bypassEnables_bools_0});
  assign execute_lane0_bypasser_integer_RS1_bypassEnables_range_0_to_2 = (|{execute_lane0_bypasser_integer_RS1_bypassEnables_bools_2,{execute_lane0_bypasser_integer_RS1_bypassEnables_bools_1,execute_lane0_bypasser_integer_RS1_bypassEnables_bools_0}});
  assign execute_lane0_bypasser_integer_RS1_bypassEnables_range_0_to_3 = (|{execute_lane0_bypasser_integer_RS1_bypassEnables_bools_3,{execute_lane0_bypasser_integer_RS1_bypassEnables_bools_2,{execute_lane0_bypasser_integer_RS1_bypassEnables_bools_1,execute_lane0_bypasser_integer_RS1_bypassEnables_bools_0}}});
  assign execute_lane0_bypasser_integer_RS1_sel = _zz_execute_lane0_bypasser_integer_RS1_sel;
  assign _zz_execute_ctrl1_down_integer_RS1_lane0 = execute_lane0_bypasser_integer_RS1_sel[4 : 1];
  always @(*) begin
    _zz_execute_ctrl1_down_integer_RS1_lane0_1 = (((_zz_execute_ctrl1_down_integer_RS1_lane0[0] ? execute_ctrl3_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0 : 32'h0) | (_zz_execute_ctrl1_down_integer_RS1_lane0[1] ? execute_ctrl4_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0 : 32'h0)) | ((_zz_execute_ctrl1_down_integer_RS1_lane0[2] ? execute_ctrl5_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0 : 32'h0) | (_zz_execute_ctrl1_down_integer_RS1_lane0[3] ? execute_lane0_bypasser_integer_RS1_port_data : 32'h0)));
    if(when_ExecuteLanePlugin_l196) begin
      _zz_execute_ctrl1_down_integer_RS1_lane0_1 = execute_ctrl2_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0;
    end
  end

  assign execute_ctrl1_down_integer_RS1_lane0 = _zz_execute_ctrl1_down_integer_RS1_lane0_1;
  assign when_ExecuteLanePlugin_l196 = execute_lane0_bypasser_integer_RS1_sel[0];
  assign execute_lane0_bypasser_integer_RS1_along_bypasses_0_checks_0_selfHit = (((execute_ctrl4_up_LANE_SEL_lane0 && execute_ctrl4_up_RD_ENABLE_lane0) && (execute_ctrl4_down_RD_PHYS_lane0 == execute_ctrl2_down_RS1_PHYS_lane0)) && 1'b1);
  assign execute_lane0_bypasser_integer_RS1_along_bypasses_0_checks_0_youngerHits_0 = (((execute_ctrl3_up_LANE_SEL_lane0 && execute_ctrl3_up_RD_ENABLE_lane0) && (execute_ctrl3_down_RD_PHYS_lane0 == execute_ctrl2_down_RS1_PHYS_lane0)) && 1'b1);
  assign execute_lane0_bypasser_integer_RS1_along_bypasses_0_checks_0_hit = (execute_lane0_bypasser_integer_RS1_along_bypasses_0_checks_0_selfHit && (! (|execute_lane0_bypasser_integer_RS1_along_bypasses_0_checks_0_youngerHits_0)));
  assign execute_lane0_bypasser_integer_RS1_along_bypasses_0_checks_1_selfHit = (((execute_ctrl3_up_LANE_SEL_lane0 && execute_ctrl3_up_RD_ENABLE_lane0) && (execute_ctrl3_down_RD_PHYS_lane0 == execute_ctrl2_down_RS1_PHYS_lane0)) && 1'b1);
  assign execute_lane0_bypasser_integer_RS1_along_bypasses_0_checks_1_hit = (execute_lane0_bypasser_integer_RS1_along_bypasses_0_checks_1_selfHit && (! 1'b0));
  assign execute_lane0_bypasser_integer_RS1_along_bypasses_0_hits = {execute_lane0_bypasser_integer_RS1_along_bypasses_0_checks_1_hit,execute_lane0_bypasser_integer_RS1_along_bypasses_0_checks_0_hit};
  assign _zz_execute_ctrl2_integer_RS1_lane0_bypass = {execute_lane0_bypasser_integer_RS1_along_bypasses_0_hits,(! (|execute_lane0_bypasser_integer_RS1_along_bypasses_0_hits))};
  assign execute_ctrl2_integer_RS1_lane0_bypass = (((_zz_execute_ctrl2_integer_RS1_lane0_bypass[0] ? execute_ctrl2_up_integer_RS1_lane0 : 32'h0) | (_zz_execute_ctrl2_integer_RS1_lane0_bypass[1] ? execute_ctrl4_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0 : 32'h0)) | (_zz_execute_ctrl2_integer_RS1_lane0_bypass[2] ? execute_ctrl3_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0 : 32'h0));
  assign execute_lane0_bypasser_integer_RS1_along_bypasses_1_checks_0_selfHit = (((execute_ctrl4_up_LANE_SEL_lane0 && execute_ctrl4_up_RD_ENABLE_lane0) && (execute_ctrl4_down_RD_PHYS_lane0 == execute_ctrl3_down_RS1_PHYS_lane0)) && 1'b1);
  assign execute_lane0_bypasser_integer_RS1_along_bypasses_1_checks_0_hit = (execute_lane0_bypasser_integer_RS1_along_bypasses_1_checks_0_selfHit && (! 1'b0));
  assign execute_lane0_bypasser_integer_RS1_along_bypasses_1_hits = execute_lane0_bypasser_integer_RS1_along_bypasses_1_checks_0_hit;
  assign _zz_execute_ctrl3_integer_RS1_lane0_bypass = {execute_lane0_bypasser_integer_RS1_along_bypasses_1_hits,(! (|execute_lane0_bypasser_integer_RS1_along_bypasses_1_hits))};
  assign execute_ctrl3_integer_RS1_lane0_bypass = ((_zz_execute_ctrl3_integer_RS1_lane0_bypass[0] ? execute_ctrl3_up_integer_RS1_lane0 : 32'h0) | (_zz_execute_ctrl3_integer_RS1_lane0_bypass[1] ? execute_ctrl4_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0 : 32'h0));
  assign execute_lane0_bypasser_integer_RS2_port_valid = (! execute_freeze_valid);
  assign execute_lane0_bypasser_integer_RS2_port_address = execute_ctrl0_down_RS2_PHYS_lane0;
  always @(*) begin
    execute_lane0_bypasser_integer_RS2_bypassEnables[0] = (((execute_ctrl2_up_LANE_SEL_lane0 && execute_ctrl2_up_RD_ENABLE_lane0) && (execute_ctrl2_down_RD_PHYS_lane0 == execute_ctrl1_down_RS2_PHYS_lane0)) && 1'b1);
    execute_lane0_bypasser_integer_RS2_bypassEnables[1] = (((execute_ctrl3_up_LANE_SEL_lane0 && execute_ctrl3_up_RD_ENABLE_lane0) && (execute_ctrl3_down_RD_PHYS_lane0 == execute_ctrl1_down_RS2_PHYS_lane0)) && 1'b1);
    execute_lane0_bypasser_integer_RS2_bypassEnables[2] = (((execute_ctrl4_up_LANE_SEL_lane0 && execute_ctrl4_up_RD_ENABLE_lane0) && (execute_ctrl4_down_RD_PHYS_lane0 == execute_ctrl1_down_RS2_PHYS_lane0)) && 1'b1);
    execute_lane0_bypasser_integer_RS2_bypassEnables[3] = (((execute_ctrl5_up_LANE_SEL_lane0 && execute_ctrl5_up_RD_ENABLE_lane0) && (execute_ctrl5_down_RD_PHYS_lane0 == execute_ctrl1_down_RS2_PHYS_lane0)) && 1'b1);
    execute_lane0_bypasser_integer_RS2_bypassEnables[4] = 1'b1;
  end

  assign _zz_execute_lane0_bypasser_integer_RS2_bypassEnables_bools_0 = execute_lane0_bypasser_integer_RS2_bypassEnables;
  assign execute_lane0_bypasser_integer_RS2_bypassEnables_bools_0 = _zz_execute_lane0_bypasser_integer_RS2_bypassEnables_bools_0[0];
  assign execute_lane0_bypasser_integer_RS2_bypassEnables_bools_1 = _zz_execute_lane0_bypasser_integer_RS2_bypassEnables_bools_0[1];
  assign execute_lane0_bypasser_integer_RS2_bypassEnables_bools_2 = _zz_execute_lane0_bypasser_integer_RS2_bypassEnables_bools_0[2];
  assign execute_lane0_bypasser_integer_RS2_bypassEnables_bools_3 = _zz_execute_lane0_bypasser_integer_RS2_bypassEnables_bools_0[3];
  assign execute_lane0_bypasser_integer_RS2_bypassEnables_bools_4 = _zz_execute_lane0_bypasser_integer_RS2_bypassEnables_bools_0[4];
  always @(*) begin
    _zz_execute_lane0_bypasser_integer_RS2_sel[0] = (execute_lane0_bypasser_integer_RS2_bypassEnables_bools_0 && (! 1'b0));
    _zz_execute_lane0_bypasser_integer_RS2_sel[1] = (execute_lane0_bypasser_integer_RS2_bypassEnables_bools_1 && (! execute_lane0_bypasser_integer_RS2_bypassEnables_bools_0));
    _zz_execute_lane0_bypasser_integer_RS2_sel[2] = (execute_lane0_bypasser_integer_RS2_bypassEnables_bools_2 && (! execute_lane0_bypasser_integer_RS2_bypassEnables_range_0_to_1));
    _zz_execute_lane0_bypasser_integer_RS2_sel[3] = (execute_lane0_bypasser_integer_RS2_bypassEnables_bools_3 && (! execute_lane0_bypasser_integer_RS2_bypassEnables_range_0_to_2));
    _zz_execute_lane0_bypasser_integer_RS2_sel[4] = (execute_lane0_bypasser_integer_RS2_bypassEnables_bools_4 && (! execute_lane0_bypasser_integer_RS2_bypassEnables_range_0_to_3));
  end

  assign execute_lane0_bypasser_integer_RS2_bypassEnables_range_0_to_1 = (|{execute_lane0_bypasser_integer_RS2_bypassEnables_bools_1,execute_lane0_bypasser_integer_RS2_bypassEnables_bools_0});
  assign execute_lane0_bypasser_integer_RS2_bypassEnables_range_0_to_2 = (|{execute_lane0_bypasser_integer_RS2_bypassEnables_bools_2,{execute_lane0_bypasser_integer_RS2_bypassEnables_bools_1,execute_lane0_bypasser_integer_RS2_bypassEnables_bools_0}});
  assign execute_lane0_bypasser_integer_RS2_bypassEnables_range_0_to_3 = (|{execute_lane0_bypasser_integer_RS2_bypassEnables_bools_3,{execute_lane0_bypasser_integer_RS2_bypassEnables_bools_2,{execute_lane0_bypasser_integer_RS2_bypassEnables_bools_1,execute_lane0_bypasser_integer_RS2_bypassEnables_bools_0}}});
  assign execute_lane0_bypasser_integer_RS2_sel = _zz_execute_lane0_bypasser_integer_RS2_sel;
  assign _zz_execute_ctrl1_down_integer_RS2_lane0 = execute_lane0_bypasser_integer_RS2_sel[4 : 1];
  always @(*) begin
    _zz_execute_ctrl1_down_integer_RS2_lane0_1 = (((_zz_execute_ctrl1_down_integer_RS2_lane0[0] ? execute_ctrl3_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0 : 32'h0) | (_zz_execute_ctrl1_down_integer_RS2_lane0[1] ? execute_ctrl4_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0 : 32'h0)) | ((_zz_execute_ctrl1_down_integer_RS2_lane0[2] ? execute_ctrl5_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0 : 32'h0) | (_zz_execute_ctrl1_down_integer_RS2_lane0[3] ? execute_lane0_bypasser_integer_RS2_port_data : 32'h0)));
    if(when_ExecuteLanePlugin_l196_1) begin
      _zz_execute_ctrl1_down_integer_RS2_lane0_1 = execute_ctrl2_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0;
    end
  end

  assign execute_ctrl1_down_integer_RS2_lane0 = _zz_execute_ctrl1_down_integer_RS2_lane0_1;
  assign when_ExecuteLanePlugin_l196_1 = execute_lane0_bypasser_integer_RS2_sel[0];
  assign execute_lane0_bypasser_integer_RS2_along_bypasses_0_checks_0_selfHit = (((execute_ctrl4_up_LANE_SEL_lane0 && execute_ctrl4_up_RD_ENABLE_lane0) && (execute_ctrl4_down_RD_PHYS_lane0 == execute_ctrl2_down_RS2_PHYS_lane0)) && 1'b1);
  assign execute_lane0_bypasser_integer_RS2_along_bypasses_0_checks_0_youngerHits_0 = (((execute_ctrl3_up_LANE_SEL_lane0 && execute_ctrl3_up_RD_ENABLE_lane0) && (execute_ctrl3_down_RD_PHYS_lane0 == execute_ctrl2_down_RS2_PHYS_lane0)) && 1'b1);
  assign execute_lane0_bypasser_integer_RS2_along_bypasses_0_checks_0_hit = (execute_lane0_bypasser_integer_RS2_along_bypasses_0_checks_0_selfHit && (! (|execute_lane0_bypasser_integer_RS2_along_bypasses_0_checks_0_youngerHits_0)));
  assign execute_lane0_bypasser_integer_RS2_along_bypasses_0_checks_1_selfHit = (((execute_ctrl3_up_LANE_SEL_lane0 && execute_ctrl3_up_RD_ENABLE_lane0) && (execute_ctrl3_down_RD_PHYS_lane0 == execute_ctrl2_down_RS2_PHYS_lane0)) && 1'b1);
  assign execute_lane0_bypasser_integer_RS2_along_bypasses_0_checks_1_hit = (execute_lane0_bypasser_integer_RS2_along_bypasses_0_checks_1_selfHit && (! 1'b0));
  assign execute_lane0_bypasser_integer_RS2_along_bypasses_0_hits = {execute_lane0_bypasser_integer_RS2_along_bypasses_0_checks_1_hit,execute_lane0_bypasser_integer_RS2_along_bypasses_0_checks_0_hit};
  assign _zz_execute_ctrl2_integer_RS2_lane0_bypass = {execute_lane0_bypasser_integer_RS2_along_bypasses_0_hits,(! (|execute_lane0_bypasser_integer_RS2_along_bypasses_0_hits))};
  assign execute_ctrl2_integer_RS2_lane0_bypass = (((_zz_execute_ctrl2_integer_RS2_lane0_bypass[0] ? execute_ctrl2_up_integer_RS2_lane0 : 32'h0) | (_zz_execute_ctrl2_integer_RS2_lane0_bypass[1] ? execute_ctrl4_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0 : 32'h0)) | (_zz_execute_ctrl2_integer_RS2_lane0_bypass[2] ? execute_ctrl3_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0 : 32'h0));
  assign execute_lane0_bypasser_integer_RS2_along_bypasses_1_checks_0_selfHit = (((execute_ctrl4_up_LANE_SEL_lane0 && execute_ctrl4_up_RD_ENABLE_lane0) && (execute_ctrl4_down_RD_PHYS_lane0 == execute_ctrl3_down_RS2_PHYS_lane0)) && 1'b1);
  assign execute_lane0_bypasser_integer_RS2_along_bypasses_1_checks_0_hit = (execute_lane0_bypasser_integer_RS2_along_bypasses_1_checks_0_selfHit && (! 1'b0));
  assign execute_lane0_bypasser_integer_RS2_along_bypasses_1_hits = execute_lane0_bypasser_integer_RS2_along_bypasses_1_checks_0_hit;
  assign _zz_execute_ctrl3_integer_RS2_lane0_bypass = {execute_lane0_bypasser_integer_RS2_along_bypasses_1_hits,(! (|execute_lane0_bypasser_integer_RS2_along_bypasses_1_hits))};
  assign execute_ctrl3_integer_RS2_lane0_bypass = ((_zz_execute_ctrl3_integer_RS2_lane0_bypass[0] ? execute_ctrl3_up_integer_RS2_lane0 : 32'h0) | (_zz_execute_ctrl3_integer_RS2_lane0_bypass[1] ? execute_ctrl4_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0 : 32'h0));
  assign execute_lane0_logic_completions_onCtrl_0_port_valid = (((execute_ctrl2_down_LANE_SEL_lane0 && execute_ctrl2_down_isReady) && (! execute_lane0_ctrls_2_downIsCancel)) && execute_ctrl2_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0);
  assign execute_lane0_logic_completions_onCtrl_0_port_payload_uopId = execute_ctrl2_down_Decode_UOP_ID_lane0;
  assign execute_lane0_logic_completions_onCtrl_0_port_payload_trap = execute_ctrl2_down_TRAP_lane0;
  assign execute_lane0_logic_completions_onCtrl_0_port_payload_commit = execute_ctrl2_down_COMMIT_lane0;
  assign execute_lane0_logic_completions_onCtrl_1_port_valid = (((execute_ctrl4_down_LANE_SEL_lane0 && execute_ctrl4_down_isReady) && (! execute_lane0_ctrls_4_downIsCancel)) && execute_ctrl4_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0);
  assign execute_lane0_logic_completions_onCtrl_1_port_payload_uopId = execute_ctrl4_down_Decode_UOP_ID_lane0;
  assign execute_lane0_logic_completions_onCtrl_1_port_payload_trap = execute_ctrl4_down_TRAP_lane0;
  assign execute_lane0_logic_completions_onCtrl_1_port_payload_commit = execute_ctrl4_down_COMMIT_lane0;
  assign execute_lane0_logic_completions_onCtrl_2_port_valid = (((execute_ctrl3_down_LANE_SEL_lane0 && execute_ctrl3_down_isReady) && (! execute_lane0_ctrls_3_downIsCancel)) && execute_ctrl3_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0);
  assign execute_lane0_logic_completions_onCtrl_2_port_payload_uopId = execute_ctrl3_down_Decode_UOP_ID_lane0;
  assign execute_lane0_logic_completions_onCtrl_2_port_payload_trap = execute_ctrl3_down_TRAP_lane0;
  assign execute_lane0_logic_completions_onCtrl_2_port_payload_commit = execute_ctrl3_down_COMMIT_lane0;
  assign execute_lane0_logic_decoding_decodingBits = {execute_ctrl1_down_lane0_LAYER_SEL_lane0,execute_ctrl1_down_Decode_UOP_lane0};
  always @(*) begin
    execute_ctrl1_down_early0_IntAluPlugin_SEL_lane0 = _zz_execute_ctrl1_down_early0_IntAluPlugin_SEL_lane0[0];
    if(execute_ctrl1_down_TRAP_lane0) begin
      execute_ctrl1_down_early0_IntAluPlugin_SEL_lane0 = 1'b0;
    end
  end

  always @(*) begin
    execute_ctrl1_down_early0_BarrelShifterPlugin_SEL_lane0 = _zz_execute_ctrl1_down_early0_BarrelShifterPlugin_SEL_lane0[0];
    if(execute_ctrl1_down_TRAP_lane0) begin
      execute_ctrl1_down_early0_BarrelShifterPlugin_SEL_lane0 = 1'b0;
    end
  end

  assign _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0 = ((execute_lane0_logic_decoding_decodingBits & 33'h100000050) == 33'h100000040);
  always @(*) begin
    execute_ctrl1_down_early0_BranchPlugin_SEL_lane0 = _zz_execute_ctrl1_down_early0_BranchPlugin_SEL_lane0[0];
    if(execute_ctrl1_down_TRAP_lane0) begin
      execute_ctrl1_down_early0_BranchPlugin_SEL_lane0 = 1'b0;
    end
  end

  always @(*) begin
    execute_ctrl1_down_early0_MulPlugin_SEL_lane0 = _zz_execute_ctrl1_down_early0_MulPlugin_SEL_lane0[0];
    if(execute_ctrl1_down_TRAP_lane0) begin
      execute_ctrl1_down_early0_MulPlugin_SEL_lane0 = 1'b0;
    end
  end

  assign _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0 = ((execute_lane0_logic_decoding_decodingBits & 33'h002004064) == 33'h002004020);
  always @(*) begin
    execute_ctrl1_down_early0_DivPlugin_SEL_lane0 = _zz_execute_ctrl1_down_early0_DivPlugin_SEL_lane0[0];
    if(execute_ctrl1_down_TRAP_lane0) begin
      execute_ctrl1_down_early0_DivPlugin_SEL_lane0 = 1'b0;
    end
  end

  assign _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0_1 = ((execute_lane0_logic_decoding_decodingBits & 33'h000001048) == 33'h000001008);
  always @(*) begin
    execute_ctrl1_down_early0_EnvPlugin_SEL_lane0 = _zz_execute_ctrl1_down_early0_EnvPlugin_SEL_lane0[0];
    if(execute_ctrl1_down_TRAP_lane0) begin
      execute_ctrl1_down_early0_EnvPlugin_SEL_lane0 = 1'b0;
    end
  end

  always @(*) begin
    execute_ctrl1_down_late0_IntAluPlugin_SEL_lane0 = _zz_execute_ctrl1_down_late0_IntAluPlugin_SEL_lane0[0];
    if(execute_ctrl1_down_TRAP_lane0) begin
      execute_ctrl1_down_late0_IntAluPlugin_SEL_lane0 = 1'b0;
    end
  end

  always @(*) begin
    execute_ctrl1_down_late0_BarrelShifterPlugin_SEL_lane0 = _zz_execute_ctrl1_down_late0_BarrelShifterPlugin_SEL_lane0[0];
    if(execute_ctrl1_down_TRAP_lane0) begin
      execute_ctrl1_down_late0_BarrelShifterPlugin_SEL_lane0 = 1'b0;
    end
  end

  assign _zz_execute_ctrl1_down_late0_BranchPlugin_SEL_lane0 = ((execute_lane0_logic_decoding_decodingBits & 33'h100000010) == 33'h0);
  always @(*) begin
    execute_ctrl1_down_late0_BranchPlugin_SEL_lane0 = _zz_execute_ctrl1_down_late0_BranchPlugin_SEL_lane0_1[0];
    if(execute_ctrl1_down_TRAP_lane0) begin
      execute_ctrl1_down_late0_BranchPlugin_SEL_lane0 = 1'b0;
    end
  end

  assign _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0_1 = ((execute_lane0_logic_decoding_decodingBits & 33'h000002050) == 33'h000002050);
  assign _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0_2 = ((execute_lane0_logic_decoding_decodingBits & 33'h000001050) == 33'h000001050);
  always @(*) begin
    execute_ctrl1_down_CsrAccessPlugin_SEL_lane0 = _zz_execute_ctrl1_down_CsrAccessPlugin_SEL_lane0[0];
    if(execute_ctrl1_down_TRAP_lane0) begin
      execute_ctrl1_down_CsrAccessPlugin_SEL_lane0 = 1'b0;
    end
  end

  assign _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0 = ((execute_lane0_logic_decoding_decodingBits & 33'h000000058) == 33'h0);
  assign _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0_1 = ((execute_lane0_logic_decoding_decodingBits & 33'h000001050) == 33'h0);
  always @(*) begin
    execute_ctrl1_down_AguPlugin_SEL_lane0 = _zz_execute_ctrl1_down_AguPlugin_SEL_lane0[0];
    if(execute_ctrl1_down_TRAP_lane0) begin
      execute_ctrl1_down_AguPlugin_SEL_lane0 = 1'b0;
    end
  end

  always @(*) begin
    execute_ctrl1_down_LsuPlugin_logic_FENCE_lane0 = _zz_execute_ctrl1_down_LsuPlugin_logic_FENCE_lane0[0];
    if(execute_ctrl1_down_TRAP_lane0) begin
      execute_ctrl1_down_LsuPlugin_logic_FENCE_lane0 = 1'b0;
    end
  end

  assign _zz_execute_ctrl1_down_AguPlugin_LOAD_lane0 = ((execute_lane0_logic_decoding_decodingBits & 33'h000000028) == 33'h0);
  assign _zz_execute_ctrl1_down_lane0_integer_WriteBackPlugin_SEL_lane0 = ((execute_lane0_logic_decoding_decodingBits & 33'h00000000c) == 33'h000000004);
  always @(*) begin
    execute_ctrl1_down_lane0_integer_WriteBackPlugin_SEL_lane0 = _zz_execute_ctrl1_down_lane0_integer_WriteBackPlugin_SEL_lane0_1[0];
    if(execute_ctrl1_down_TRAP_lane0) begin
      execute_ctrl1_down_lane0_integer_WriteBackPlugin_SEL_lane0 = 1'b0;
    end
  end

  assign _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0_2 = ((execute_lane0_logic_decoding_decodingBits & 33'h100003040) == 33'h100000040);
  assign _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0_3 = ((execute_lane0_logic_decoding_decodingBits & 33'h102000050) == 33'h100000010);
  assign _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0_4 = ((execute_lane0_logic_decoding_decodingBits & 33'h10000000c) == 33'h100000004);
  assign _zz_execute_ctrl1_down_BYPASSED_AT_3_lane0 = ((execute_lane0_logic_decoding_decodingBits & 33'h100000030) == 33'h100000010);
  always @(*) begin
    execute_ctrl1_down_COMPLETION_AT_2_lane0 = _zz_execute_ctrl1_down_COMPLETION_AT_2_lane0[0];
    if(execute_ctrl1_down_TRAP_lane0) begin
      execute_ctrl1_down_COMPLETION_AT_2_lane0 = 1'b0;
    end
  end

  assign _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0_2 = ((execute_lane0_logic_decoding_decodingBits & 33'h002004064) == 33'h002000020);
  assign _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0_3 = ((execute_lane0_logic_decoding_decodingBits & 33'h100000000) == 33'h0);
  always @(*) begin
    execute_ctrl1_down_COMPLETION_AT_4_lane0 = _zz_execute_ctrl1_down_COMPLETION_AT_4_lane0[0];
    if(execute_ctrl1_down_TRAP_lane0) begin
      execute_ctrl1_down_COMPLETION_AT_4_lane0 = 1'b0;
    end
  end

  always @(*) begin
    execute_ctrl1_down_COMPLETION_AT_3_lane0 = _zz_execute_ctrl1_down_COMPLETION_AT_3_lane0[0];
    if(execute_ctrl1_down_TRAP_lane0) begin
      execute_ctrl1_down_COMPLETION_AT_3_lane0 = 1'b0;
    end
  end

  always @(*) begin
    execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0 = _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0_5[0];
    if(execute_ctrl1_down_TRAP_lane0) begin
      execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0 = 1'b0;
    end
  end

  always @(*) begin
    execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0 = _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0_4[0];
    if(execute_ctrl1_down_TRAP_lane0) begin
      execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0 = 1'b0;
    end
  end

  always @(*) begin
    execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0 = _zz_execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0_3[0];
    if(execute_ctrl1_down_TRAP_lane0) begin
      execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0 = 1'b0;
    end
  end

  assign _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_ADD_SUB_lane0 = ((execute_lane0_logic_decoding_decodingBits & 33'h000006000) == 33'h0);
  assign _zz_execute_ctrl1_down_late0_SrcPlugin_logic_SRC2_CTRL_lane0 = ((execute_lane0_logic_decoding_decodingBits & 33'h000000004) == 33'h000000004);
  assign execute_ctrl1_down_early0_IntAluPlugin_ALU_ADD_SUB_lane0 = _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_ADD_SUB_lane0[0];
  assign _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_SLTX_lane0 = ((execute_lane0_logic_decoding_decodingBits & 33'h000006004) == 33'h000002000);
  assign execute_ctrl1_down_early0_IntAluPlugin_ALU_SLTX_lane0 = _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_SLTX_lane0[0];
  assign _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0 = ((execute_lane0_logic_decoding_decodingBits & 33'h000003000) == 33'h000002000);
  assign _zz_execute_ctrl1_down_BarrelShifterPlugin_LEFT_lane0 = ((execute_lane0_logic_decoding_decodingBits & 33'h000004000) == 33'h0);
  assign _zz_execute_ctrl1_down_CsrAccessPlugin_CSR_CLEAR_lane0 = ((execute_lane0_logic_decoding_decodingBits & 33'h000001000) == 33'h000001000);
  assign _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_1 = {(|{_zz_execute_ctrl1_down_CsrAccessPlugin_CSR_CLEAR_lane0,{_zz_execute_ctrl1_down_late0_SrcPlugin_logic_SRC2_CTRL_lane0,_zz_execute_ctrl1_down_BarrelShifterPlugin_LEFT_lane0}}),(|{_zz_execute_ctrl1_down_late0_SrcPlugin_logic_SRC2_CTRL_lane0,{_zz_execute_ctrl1_down_BarrelShifterPlugin_LEFT_lane0,_zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0}})};
  assign _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0 = _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_1;
  assign _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_2 = _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0;
  assign execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0 = _zz_execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_2;
  assign execute_ctrl1_down_SrcStageables_REVERT_lane0 = _zz_execute_ctrl1_down_SrcStageables_REVERT_lane0[0];
  assign execute_ctrl1_down_SrcStageables_ZERO_lane0 = _zz_execute_ctrl1_down_SrcStageables_ZERO_lane0[0];
  assign execute_ctrl1_down_early0_SrcPlugin_logic_SRC1_CTRL_lane0 = (|((execute_lane0_logic_decoding_decodingBits & 33'h000000044) == 33'h000000004));
  assign _zz_execute_ctrl1_down_late0_SrcPlugin_logic_SRC2_CTRL_lane0_1 = ((execute_lane0_logic_decoding_decodingBits & 33'h000000024) == 33'h0);
  assign execute_ctrl1_down_early0_SrcPlugin_logic_SRC2_CTRL_lane0 = {(|{_zz_execute_ctrl1_down_late0_SrcPlugin_logic_SRC2_CTRL_lane0,((execute_lane0_logic_decoding_decodingBits & 33'h000000070) == 33'h000000020)}),(|{((execute_lane0_logic_decoding_decodingBits & 33'h000000050) == 33'h0),_zz_execute_ctrl1_down_late0_SrcPlugin_logic_SRC2_CTRL_lane0_1})};
  assign execute_ctrl1_down_lane0_IntFormatPlugin_logic_SIGNED_lane0 = _zz_execute_ctrl1_down_lane0_IntFormatPlugin_logic_SIGNED_lane0[0];
  assign _zz_execute_ctrl1_down_CsrAccessPlugin_CSR_MASK_lane0 = ((execute_lane0_logic_decoding_decodingBits & 33'h000002000) == 33'h000002000);
  assign execute_ctrl1_down_lane0_IntFormatPlugin_logic_WIDTH_ID_lane0 = {(|{((execute_lane0_logic_decoding_decodingBits & 33'h000000010) == 33'h000000010),_zz_execute_ctrl1_down_CsrAccessPlugin_CSR_MASK_lane0}),(|((execute_lane0_logic_decoding_decodingBits & 33'h000001010) == 33'h000001000))};
  assign _zz_execute_ctrl1_down_BYPASSED_AT_3_lane0_1 = ((execute_lane0_logic_decoding_decodingBits & 33'h100000004) == 33'h100000004);
  assign execute_ctrl1_down_BYPASSED_AT_2_lane0 = _zz_execute_ctrl1_down_BYPASSED_AT_2_lane0[0];
  assign execute_ctrl1_down_BYPASSED_AT_3_lane0 = _zz_execute_ctrl1_down_BYPASSED_AT_3_lane0_2[0];
  assign execute_ctrl1_down_MAY_FLUSH_PRECISE_3_lane0 = _zz_execute_ctrl1_down_MAY_FLUSH_PRECISE_3_lane0[0];
  assign execute_ctrl1_down_MAY_FLUSH_PRECISE_4_lane0 = _zz_execute_ctrl1_down_MAY_FLUSH_PRECISE_4_lane0[0];
  assign execute_ctrl1_down_SrcStageables_UNSIGNED_lane0 = _zz_execute_ctrl1_down_SrcStageables_UNSIGNED_lane0[0];
  assign execute_ctrl1_down_BarrelShifterPlugin_LEFT_lane0 = _zz_execute_ctrl1_down_BarrelShifterPlugin_LEFT_lane0_1[0];
  assign execute_ctrl1_down_BarrelShifterPlugin_SIGNED_lane0 = _zz_execute_ctrl1_down_BarrelShifterPlugin_SIGNED_lane0[0];
  assign _zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_1 = {(|_zz_execute_ctrl1_down_lane0_integer_WriteBackPlugin_SEL_lane0),(|((execute_lane0_logic_decoding_decodingBits & 33'h000000008) == 33'h000000008))};
  assign _zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0 = _zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_1;
  assign _zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_2 = _zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0;
  assign execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0 = _zz_execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0_2;
  assign execute_ctrl1_down_MulPlugin_HIGH_lane0 = _zz_execute_ctrl1_down_MulPlugin_HIGH_lane0[0];
  assign execute_ctrl1_down_RsUnsignedPlugin_RS1_SIGNED_lane0 = _zz_execute_ctrl1_down_RsUnsignedPlugin_RS1_SIGNED_lane0[0];
  assign execute_ctrl1_down_RsUnsignedPlugin_RS2_SIGNED_lane0 = _zz_execute_ctrl1_down_RsUnsignedPlugin_RS2_SIGNED_lane0[0];
  assign execute_ctrl1_down_DivPlugin_REM_lane0 = _zz_execute_ctrl1_down_DivPlugin_REM_lane0[0];
  assign execute_ctrl1_down_CsrAccessPlugin_CSR_IMM_lane0 = _zz_execute_ctrl1_down_CsrAccessPlugin_CSR_IMM_lane0[0];
  assign execute_ctrl1_down_CsrAccessPlugin_CSR_MASK_lane0 = _zz_execute_ctrl1_down_CsrAccessPlugin_CSR_MASK_lane0_1[0];
  assign execute_ctrl1_down_CsrAccessPlugin_CSR_CLEAR_lane0 = _zz_execute_ctrl1_down_CsrAccessPlugin_CSR_CLEAR_lane0_1[0];
  assign execute_ctrl1_down_AguPlugin_LOAD_lane0 = _zz_execute_ctrl1_down_AguPlugin_LOAD_lane0_1[0];
  assign execute_ctrl1_down_AguPlugin_STORE_lane0 = _zz_execute_ctrl1_down_AguPlugin_STORE_lane0[0];
  assign execute_ctrl1_down_AguPlugin_ATOMIC_lane0 = _zz_execute_ctrl1_down_AguPlugin_ATOMIC_lane0[0];
  assign execute_ctrl1_down_AguPlugin_FLOAT_lane0 = _zz_execute_ctrl1_down_AguPlugin_FLOAT_lane0[0];
  assign execute_ctrl1_down_AguPlugin_CLEAN_lane0 = _zz_execute_ctrl1_down_AguPlugin_CLEAN_lane0[0];
  assign execute_ctrl1_down_AguPlugin_INVALIDATE_lane0 = _zz_execute_ctrl1_down_AguPlugin_INVALIDATE_lane0[0];
  assign execute_ctrl1_down_LsuPlugin_logic_LSU_PREFETCH_lane0 = _zz_execute_ctrl1_down_LsuPlugin_logic_LSU_PREFETCH_lane0[0];
  assign _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0 = ((execute_lane0_logic_decoding_decodingBits & 33'h000000040) == 33'h0);
  assign _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_2 = {(|((execute_lane0_logic_decoding_decodingBits & 33'h030001000) == 33'h010000000)),{(|{((execute_lane0_logic_decoding_decodingBits & 33'h020000000) == 33'h020000000),_zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0}),(|{((execute_lane0_logic_decoding_decodingBits & 33'h000100000) == 33'h000100000),_zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0})}};
  assign _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_1 = _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_2;
  assign _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_3 = _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_1;
  assign execute_ctrl1_down_early0_EnvPlugin_OP_lane0 = _zz_execute_ctrl1_down_early0_EnvPlugin_OP_lane0_3;
  assign execute_ctrl1_down_late0_IntAluPlugin_ALU_ADD_SUB_lane0 = _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_ADD_SUB_lane0_1[0];
  assign execute_ctrl1_down_late0_IntAluPlugin_ALU_SLTX_lane0 = _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_SLTX_lane0_1[0];
  assign _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_2 = {(|{_zz_execute_ctrl1_down_CsrAccessPlugin_CSR_CLEAR_lane0,{_zz_execute_ctrl1_down_late0_SrcPlugin_logic_SRC2_CTRL_lane0,_zz_execute_ctrl1_down_BarrelShifterPlugin_LEFT_lane0}}),(|{_zz_execute_ctrl1_down_late0_SrcPlugin_logic_SRC2_CTRL_lane0,{_zz_execute_ctrl1_down_BarrelShifterPlugin_LEFT_lane0,_zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0}})};
  assign _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_1 = _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_2;
  assign _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_3 = _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_1;
  assign execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0 = _zz_execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0_3;
  assign execute_ctrl1_down_late0_SrcPlugin_logic_SRC1_CTRL_lane0 = (|_zz_execute_ctrl1_down_late0_SrcPlugin_logic_SRC2_CTRL_lane0);
  assign execute_ctrl1_down_late0_SrcPlugin_logic_SRC2_CTRL_lane0 = {(|_zz_execute_ctrl1_down_late0_SrcPlugin_logic_SRC2_CTRL_lane0),(|_zz_execute_ctrl1_down_late0_SrcPlugin_logic_SRC2_CTRL_lane0_1)};
  assign when_ExecuteLanePlugin_l306 = (|{(late0_BranchPlugin_logic_flushPort_valid && 1'b1),{(early0_EnvPlugin_logic_flushPort_valid && 1'b1),{(CsrAccessPlugin_logic_flushPort_valid && 1'b1),{(early0_BranchPlugin_logic_flushPort_valid && 1'b1),(LsuPlugin_logic_flushPort_valid && 1'b1)}}}});
  assign execute_lane0_ctrls_0_downIsCancel = 1'b0;
  assign execute_lane0_ctrls_0_upIsCancel = when_ExecuteLanePlugin_l306;
  assign when_ExecuteLanePlugin_l306_1 = (|{(late0_BranchPlugin_logic_flushPort_valid && 1'b1),{(early0_EnvPlugin_logic_flushPort_valid && 1'b1),{(CsrAccessPlugin_logic_flushPort_valid && 1'b1),{(early0_BranchPlugin_logic_flushPort_valid && 1'b1),(LsuPlugin_logic_flushPort_valid && 1'b1)}}}});
  assign execute_lane0_ctrls_1_downIsCancel = 1'b0;
  assign execute_lane0_ctrls_1_upIsCancel = when_ExecuteLanePlugin_l306_1;
  assign when_ExecuteLanePlugin_l306_2 = (|{(late0_BranchPlugin_logic_flushPort_valid && 1'b1),{((early0_EnvPlugin_logic_flushPort_valid && 1'b1) && (1'b0 || (_zz_when_ExecuteLanePlugin_l306_2 && early0_EnvPlugin_logic_flushPort_payload_self))),{((CsrAccessPlugin_logic_flushPort_valid && _zz_when_ExecuteLanePlugin_l306_2_1) && (_zz_when_ExecuteLanePlugin_l306_2_2 || _zz_when_ExecuteLanePlugin_l306_2_3)),{(_zz_when_ExecuteLanePlugin_l306_2_4 && _zz_when_ExecuteLanePlugin_l306_2_5),(LsuPlugin_logic_flushPort_valid && _zz_when_ExecuteLanePlugin_l306_2_6)}}}});
  assign execute_lane0_ctrls_2_downIsCancel = 1'b0;
  assign execute_lane0_ctrls_2_upIsCancel = when_ExecuteLanePlugin_l306_2;
  assign when_ExecuteLanePlugin_l306_3 = (|{(late0_BranchPlugin_logic_flushPort_valid && 1'b1),(LsuPlugin_logic_flushPort_valid && 1'b1)});
  assign execute_lane0_ctrls_3_downIsCancel = 1'b0;
  assign execute_lane0_ctrls_3_upIsCancel = when_ExecuteLanePlugin_l306_3;
  assign when_ExecuteLanePlugin_l306_4 = (|{((late0_BranchPlugin_logic_flushPort_valid && 1'b1) && (1'b0 || (1'b1 && late0_BranchPlugin_logic_flushPort_payload_self))),((LsuPlugin_logic_flushPort_valid && 1'b1) && (1'b0 || (1'b1 && LsuPlugin_logic_flushPort_payload_self)))});
  assign execute_lane0_ctrls_4_downIsCancel = 1'b0;
  assign execute_lane0_ctrls_4_upIsCancel = when_ExecuteLanePlugin_l306_4;
  assign execute_lane0_ctrls_5_downIsCancel = 1'b0;
  assign execute_lane0_ctrls_5_upIsCancel = 1'b0;
  assign execute_lane0_logic_trapPending[0] = (|{((execute_ctrl4_up_LANE_SEL_lane0 && 1'b1) && execute_ctrl4_down_TRAP_lane0),{((execute_ctrl3_up_LANE_SEL_lane0 && 1'b1) && execute_ctrl3_down_TRAP_lane0),{((execute_ctrl2_up_LANE_SEL_lane0 && 1'b1) && execute_ctrl2_down_TRAP_lane0),((execute_ctrl1_up_LANE_SEL_lane0 && 1'b1) && execute_ctrl1_down_TRAP_lane0)}}});
  assign execute_ctrl2_up_COMMIT_lane0 = (! execute_ctrl2_up_TRAP_lane0);
  assign WhiteboxerPlugin_logic_csr_access_valid = CsrAccessPlugin_logic_fsm_interface_fire;
  assign WhiteboxerPlugin_logic_csr_access_payload_uopId = CsrAccessPlugin_logic_fsm_interface_uopId;
  assign WhiteboxerPlugin_logic_csr_access_payload_address = _zz_WhiteboxerPlugin_logic_csr_access_payload_address[31 : 20];
  assign WhiteboxerPlugin_logic_csr_access_payload_write = CsrAccessPlugin_logic_fsm_interface_onWriteBits;
  assign WhiteboxerPlugin_logic_csr_access_payload_read = CsrAccessPlugin_logic_fsm_interface_csrValue;
  assign WhiteboxerPlugin_logic_csr_access_payload_writeDone = CsrAccessPlugin_logic_fsm_interface_write;
  assign WhiteboxerPlugin_logic_csr_access_payload_readDone = CsrAccessPlugin_logic_fsm_interface_read;
  assign WhiteboxerPlugin_logic_csr_port_valid = WhiteboxerPlugin_logic_csr_access_valid;
  assign WhiteboxerPlugin_logic_csr_port_payload_uopId = WhiteboxerPlugin_logic_csr_access_payload_uopId;
  assign WhiteboxerPlugin_logic_csr_port_payload_address = WhiteboxerPlugin_logic_csr_access_payload_address;
  assign WhiteboxerPlugin_logic_csr_port_payload_write = WhiteboxerPlugin_logic_csr_access_payload_write;
  assign WhiteboxerPlugin_logic_csr_port_payload_read = WhiteboxerPlugin_logic_csr_access_payload_read;
  assign WhiteboxerPlugin_logic_csr_port_payload_writeDone = WhiteboxerPlugin_logic_csr_access_payload_writeDone;
  assign WhiteboxerPlugin_logic_csr_port_payload_readDone = WhiteboxerPlugin_logic_csr_access_payload_readDone;
  assign WhiteboxerPlugin_logic_rfWrites_ports_0_valid = lane0_integer_WriteBackPlugin_logic_stages_0_write_valid;
  assign WhiteboxerPlugin_logic_rfWrites_ports_0_payload_uopId = lane0_integer_WriteBackPlugin_logic_stages_0_write_payload_uopId;
  assign WhiteboxerPlugin_logic_rfWrites_ports_0_payload_data = lane0_integer_WriteBackPlugin_logic_stages_0_write_payload_data;
  assign WhiteboxerPlugin_logic_rfWrites_ports_1_valid = lane0_integer_WriteBackPlugin_logic_stages_1_write_valid;
  assign WhiteboxerPlugin_logic_rfWrites_ports_1_payload_uopId = lane0_integer_WriteBackPlugin_logic_stages_1_write_payload_uopId;
  assign WhiteboxerPlugin_logic_rfWrites_ports_1_payload_data = lane0_integer_WriteBackPlugin_logic_stages_1_write_payload_data;
  assign WhiteboxerPlugin_logic_rfWrites_ports_2_valid = lane0_integer_WriteBackPlugin_logic_stages_2_write_valid;
  assign WhiteboxerPlugin_logic_rfWrites_ports_2_payload_uopId = lane0_integer_WriteBackPlugin_logic_stages_2_write_payload_uopId;
  assign WhiteboxerPlugin_logic_rfWrites_ports_2_payload_data = lane0_integer_WriteBackPlugin_logic_stages_2_write_payload_data;
  assign WhiteboxerPlugin_logic_completions_ports_0_valid = DecoderPlugin_logic_laneLogic_0_completionPort_valid;
  assign WhiteboxerPlugin_logic_completions_ports_0_payload_uopId = DecoderPlugin_logic_laneLogic_0_completionPort_payload_uopId;
  assign WhiteboxerPlugin_logic_completions_ports_0_payload_trap = DecoderPlugin_logic_laneLogic_0_completionPort_payload_trap;
  assign WhiteboxerPlugin_logic_completions_ports_0_payload_commit = DecoderPlugin_logic_laneLogic_0_completionPort_payload_commit;
  assign WhiteboxerPlugin_logic_completions_ports_1_valid = execute_lane0_logic_completions_onCtrl_0_port_valid;
  assign WhiteboxerPlugin_logic_completions_ports_1_payload_uopId = execute_lane0_logic_completions_onCtrl_0_port_payload_uopId;
  assign WhiteboxerPlugin_logic_completions_ports_1_payload_trap = execute_lane0_logic_completions_onCtrl_0_port_payload_trap;
  assign WhiteboxerPlugin_logic_completions_ports_1_payload_commit = execute_lane0_logic_completions_onCtrl_0_port_payload_commit;
  assign WhiteboxerPlugin_logic_completions_ports_2_valid = execute_lane0_logic_completions_onCtrl_1_port_valid;
  assign WhiteboxerPlugin_logic_completions_ports_2_payload_uopId = execute_lane0_logic_completions_onCtrl_1_port_payload_uopId;
  assign WhiteboxerPlugin_logic_completions_ports_2_payload_trap = execute_lane0_logic_completions_onCtrl_1_port_payload_trap;
  assign WhiteboxerPlugin_logic_completions_ports_2_payload_commit = execute_lane0_logic_completions_onCtrl_1_port_payload_commit;
  assign WhiteboxerPlugin_logic_completions_ports_3_valid = execute_lane0_logic_completions_onCtrl_2_port_valid;
  assign WhiteboxerPlugin_logic_completions_ports_3_payload_uopId = execute_lane0_logic_completions_onCtrl_2_port_payload_uopId;
  assign WhiteboxerPlugin_logic_completions_ports_3_payload_trap = execute_lane0_logic_completions_onCtrl_2_port_payload_trap;
  assign WhiteboxerPlugin_logic_completions_ports_3_payload_commit = execute_lane0_logic_completions_onCtrl_2_port_payload_commit;
  assign WhiteboxerPlugin_logic_commits_ports_0_oh_0 = ((((execute_ctrl4_down_LANE_SEL_lane0 && execute_ctrl4_down_isReady) && (! execute_lane0_ctrls_4_downIsCancel)) && execute_ctrl4_down_COMMIT_lane0) && 1'b1);
  assign WhiteboxerPlugin_logic_commits_ports_0_valid = (|WhiteboxerPlugin_logic_commits_ports_0_oh_0);
  assign WhiteboxerPlugin_logic_commits_ports_0_pc = (WhiteboxerPlugin_logic_commits_ports_0_oh_0 ? execute_ctrl4_down_PC_lane0 : 32'h0);
  assign WhiteboxerPlugin_logic_commits_ports_0_uop = (WhiteboxerPlugin_logic_commits_ports_0_oh_0 ? execute_ctrl4_down_Decode_UOP_lane0 : 32'h0);
  assign WhiteboxerPlugin_logic_reschedules_flushes_0_valid = BtbPlugin_logic_flushPort_valid;
  assign WhiteboxerPlugin_logic_reschedules_flushes_0_payload_self = BtbPlugin_logic_flushPort_payload_self;
  assign WhiteboxerPlugin_logic_reschedules_flushes_1_valid = LsuPlugin_logic_flushPort_valid;
  assign WhiteboxerPlugin_logic_reschedules_flushes_1_payload_uopId = LsuPlugin_logic_flushPort_payload_uopId;
  assign WhiteboxerPlugin_logic_reschedules_flushes_1_payload_self = LsuPlugin_logic_flushPort_payload_self;
  assign WhiteboxerPlugin_logic_reschedules_flushes_2_valid = early0_BranchPlugin_logic_flushPort_valid;
  assign WhiteboxerPlugin_logic_reschedules_flushes_2_payload_uopId = early0_BranchPlugin_logic_flushPort_payload_uopId;
  assign WhiteboxerPlugin_logic_reschedules_flushes_2_payload_self = early0_BranchPlugin_logic_flushPort_payload_self;
  assign WhiteboxerPlugin_logic_reschedules_flushes_3_valid = CsrAccessPlugin_logic_flushPort_valid;
  assign WhiteboxerPlugin_logic_reschedules_flushes_3_payload_uopId = CsrAccessPlugin_logic_flushPort_payload_uopId;
  assign WhiteboxerPlugin_logic_reschedules_flushes_3_payload_self = CsrAccessPlugin_logic_flushPort_payload_self;
  assign WhiteboxerPlugin_logic_reschedules_flushes_4_valid = early0_EnvPlugin_logic_flushPort_valid;
  assign WhiteboxerPlugin_logic_reschedules_flushes_4_payload_uopId = early0_EnvPlugin_logic_flushPort_payload_uopId;
  assign WhiteboxerPlugin_logic_reschedules_flushes_4_payload_self = early0_EnvPlugin_logic_flushPort_payload_self;
  assign WhiteboxerPlugin_logic_reschedules_flushes_5_valid = late0_BranchPlugin_logic_flushPort_valid;
  assign WhiteboxerPlugin_logic_reschedules_flushes_5_payload_uopId = late0_BranchPlugin_logic_flushPort_payload_uopId;
  assign WhiteboxerPlugin_logic_reschedules_flushes_5_payload_self = late0_BranchPlugin_logic_flushPort_payload_self;
  assign WhiteboxerPlugin_logic_reschedules_flushes_6_valid = DecoderPlugin_logic_laneLogic_0_flushPort_valid;
  assign WhiteboxerPlugin_logic_reschedules_flushes_6_payload_uopId = DecoderPlugin_logic_laneLogic_0_flushPort_payload_uopId;
  assign WhiteboxerPlugin_logic_reschedules_flushes_6_payload_self = DecoderPlugin_logic_laneLogic_0_flushPort_payload_self;
  assign late0_BranchPlugin_logic_jumpLogic_learn_asFlow_valid = late0_BranchPlugin_logic_jumpLogic_learn_valid;
  assign late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_pcOnLastSlice = late0_BranchPlugin_logic_jumpLogic_learn_payload_pcOnLastSlice;
  assign late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_pcTarget = late0_BranchPlugin_logic_jumpLogic_learn_payload_pcTarget;
  assign late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_taken = late0_BranchPlugin_logic_jumpLogic_learn_payload_taken;
  assign late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_isBranch = late0_BranchPlugin_logic_jumpLogic_learn_payload_isBranch;
  assign late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_isPush = late0_BranchPlugin_logic_jumpLogic_learn_payload_isPush;
  assign late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_isPop = late0_BranchPlugin_logic_jumpLogic_learn_payload_isPop;
  assign late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_wasWrong = late0_BranchPlugin_logic_jumpLogic_learn_payload_wasWrong;
  assign late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_badPredictedTarget = late0_BranchPlugin_logic_jumpLogic_learn_payload_badPredictedTarget;
  assign late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_uopId = late0_BranchPlugin_logic_jumpLogic_learn_payload_uopId;
  assign WhiteboxerPlugin_logic_prediction_learns_0_valid = late0_BranchPlugin_logic_jumpLogic_learn_asFlow_valid;
  assign WhiteboxerPlugin_logic_prediction_learns_0_payload_pcOnLastSlice = late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_pcOnLastSlice;
  assign WhiteboxerPlugin_logic_prediction_learns_0_payload_pcTarget = late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_pcTarget;
  assign WhiteboxerPlugin_logic_prediction_learns_0_payload_taken = late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_taken;
  assign WhiteboxerPlugin_logic_prediction_learns_0_payload_isBranch = late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_isBranch;
  assign WhiteboxerPlugin_logic_prediction_learns_0_payload_isPush = late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_isPush;
  assign WhiteboxerPlugin_logic_prediction_learns_0_payload_isPop = late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_isPop;
  assign WhiteboxerPlugin_logic_prediction_learns_0_payload_wasWrong = late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_wasWrong;
  assign WhiteboxerPlugin_logic_prediction_learns_0_payload_badPredictedTarget = late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_badPredictedTarget;
  assign WhiteboxerPlugin_logic_prediction_learns_0_payload_uopId = late0_BranchPlugin_logic_jumpLogic_learn_asFlow_payload_uopId;
  assign WhiteboxerPlugin_logic_loadExecute_fire = (((((((execute_ctrl4_down_LANE_SEL_lane0 && execute_ctrl4_down_isReady) && (! execute_lane0_ctrls_4_downIsCancel)) && execute_ctrl4_down_AguPlugin_SEL_lane0) && execute_ctrl4_down_AguPlugin_LOAD_lane0) && (! execute_ctrl4_down_LsuPlugin_logic_LSU_PREFETCH_lane0)) && (! execute_ctrl4_down_TRAP_lane0)) && (! execute_ctrl4_down_LsuPlugin_logic_onPma_IO_lane0));
  assign WhiteboxerPlugin_logic_loadExecute_uopId = execute_ctrl4_down_Decode_UOP_ID_lane0;
  assign WhiteboxerPlugin_logic_loadExecute_size = execute_ctrl4_down_AguPlugin_SIZE_lane0;
  assign WhiteboxerPlugin_logic_loadExecute_address = execute_ctrl4_down_LsuL1_PHYSICAL_ADDRESS_lane0;
  assign WhiteboxerPlugin_logic_loadExecute_data = lane0_IntFormatPlugin_logic_stages_1_wb_payload;
  assign WhiteboxerPlugin_logic_storeCommit_fire = LsuPlugin_logic_onWb_storeFire;
  assign WhiteboxerPlugin_logic_storeCommit_uopId = execute_ctrl4_down_Decode_UOP_ID_lane0;
  assign WhiteboxerPlugin_logic_storeCommit_size = execute_ctrl4_down_AguPlugin_SIZE_lane0;
  assign WhiteboxerPlugin_logic_storeCommit_address = execute_ctrl4_down_MMU_TRANSLATED_lane0;
  assign WhiteboxerPlugin_logic_storeCommit_data = execute_ctrl4_down_LsuL1_WRITE_DATA_lane0;
  assign WhiteboxerPlugin_logic_storeCommit_storeId = execute_ctrl4_down_Decode_STORE_ID_lane0;
  assign WhiteboxerPlugin_logic_storeCommit_amo = 1'b0;
  assign WhiteboxerPlugin_logic_storeConditional_fire = (((((execute_ctrl4_down_LANE_SEL_lane0 && execute_ctrl4_down_isReady) && (! execute_lane0_ctrls_4_downIsCancel)) && execute_ctrl4_down_AguPlugin_SEL_lane0) && (execute_ctrl4_down_AguPlugin_ATOMIC_lane0 && (! execute_ctrl4_down_AguPlugin_LOAD_lane0))) && (! execute_ctrl4_down_TRAP_lane0));
  assign WhiteboxerPlugin_logic_storeConditional_uopId = execute_ctrl4_down_Decode_UOP_ID_lane0;
  assign WhiteboxerPlugin_logic_storeConditional_miss = execute_ctrl4_down_LsuPlugin_logic_onCtrl_SC_MISS_lane0;
  assign WhiteboxerPlugin_logic_storeBroadcast_fire = LsuPlugin_logic_onWb_storeBroadcast;
  assign WhiteboxerPlugin_logic_storeBroadcast_storeId = execute_ctrl4_down_Decode_STORE_ID_lane0;
  assign integer_RegFilePlugin_logic_writeMerges_0_bus_valid = (|lane0_integer_WriteBackPlugin_logic_write_port_valid);
  assign integer_RegFilePlugin_logic_writeMerges_0_bus_address = lane0_integer_WriteBackPlugin_logic_write_port_address;
  assign integer_RegFilePlugin_logic_writeMerges_0_bus_data = lane0_integer_WriteBackPlugin_logic_write_port_data;
  assign integer_RegFilePlugin_logic_writeMerges_0_bus_uopId = lane0_integer_WriteBackPlugin_logic_write_port_uopId;
  assign execute_lane0_bypasser_integer_RS1_port_data = integer_RegFilePlugin_logic_regfile_fpga_io_reads_0_data;
  assign execute_lane0_bypasser_integer_RS2_port_data = integer_RegFilePlugin_logic_regfile_fpga_io_reads_1_data;
  always @(*) begin
    integer_RegFilePlugin_logic_regfile_fpga_io_writes_0_valid = integer_RegFilePlugin_logic_writeMerges_0_bus_valid;
    if(when_RegFilePlugin_l130) begin
      integer_RegFilePlugin_logic_regfile_fpga_io_writes_0_valid = 1'b1;
    end
  end

  always @(*) begin
    integer_RegFilePlugin_logic_regfile_fpga_io_writes_0_address = integer_RegFilePlugin_logic_writeMerges_0_bus_address;
    if(when_RegFilePlugin_l130) begin
      integer_RegFilePlugin_logic_regfile_fpga_io_writes_0_address = integer_RegFilePlugin_logic_initalizer_counter[4:0];
    end
  end

  always @(*) begin
    integer_RegFilePlugin_logic_regfile_fpga_io_writes_0_data = integer_RegFilePlugin_logic_writeMerges_0_bus_data;
    if(when_RegFilePlugin_l130) begin
      integer_RegFilePlugin_logic_regfile_fpga_io_writes_0_data = 32'h0;
    end
  end

  assign integer_RegFilePlugin_logic_initalizer_done = integer_RegFilePlugin_logic_initalizer_counter[5];
  assign when_RegFilePlugin_l130 = (! integer_RegFilePlugin_logic_initalizer_done);
  assign integer_write_0_valid = integer_RegFilePlugin_logic_writeMerges_0_bus_valid;
  assign integer_write_0_address = integer_RegFilePlugin_logic_writeMerges_0_bus_address;
  assign integer_write_0_data = integer_RegFilePlugin_logic_writeMerges_0_bus_data;
  assign integer_write_0_uopId = integer_RegFilePlugin_logic_writeMerges_0_bus_uopId;
  assign execute_freeze_valid = (|{CsrAccessPlugin_logic_fsm_inject_freeze,{LsuPlugin_logic_onCtrl_io_freezeIt,early0_DivPlugin_logic_processing_freeze}});
  assign execute_ctrl5_down_ready = (! execute_freeze_valid);
  assign TrapPlugin_logic_initHold = (|{(! CsrRamPlugin_logic_flush_done),{((! LsuL1Plugin_logic_initializer_done) || 1'b0),{(! integer_RegFilePlugin_logic_initalizer_done),{(FetchL1Plugin_logic_invalidate_firstEver || 1'b0),1'b0}}}});
  assign WhiteboxerPlugin_logic_wfi = TrapPlugin_logic_harts_0_trap_fsm_wfi;
  assign WhiteboxerPlugin_logic_perf_executeFreezed = execute_freeze_valid;
  assign WhiteboxerPlugin_logic_perf_dispatchHazards = (|(DispatchPlugin_logic_candidates_0_ctx_valid && (! DispatchPlugin_logic_candidates_0_fire)));
  assign WhiteboxerPlugin_logic_perf_candidatesCount = _zz_WhiteboxerPlugin_logic_perf_candidatesCount;
  assign WhiteboxerPlugin_logic_perf_dispatchFeedCount = _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCount;
  always @(*) begin
    _zz_WhiteboxerPlugin_logic_perf_executeFreezedCounter = 1'b0;
    if(WhiteboxerPlugin_logic_perf_executeFreezed) begin
      _zz_WhiteboxerPlugin_logic_perf_executeFreezedCounter = 1'b1;
    end
  end

  always @(*) begin
    _zz_WhiteboxerPlugin_logic_perf_executeFreezedCounter_1 = (_zz_WhiteboxerPlugin_logic_perf_executeFreezedCounter_2 + _zz__zz_WhiteboxerPlugin_logic_perf_executeFreezedCounter_1);
    if(1'b0) begin
      _zz_WhiteboxerPlugin_logic_perf_executeFreezedCounter_1 = 60'h0;
    end
  end

  assign WhiteboxerPlugin_logic_perf_executeFreezedCounter = _zz_WhiteboxerPlugin_logic_perf_executeFreezedCounter_2;
  always @(*) begin
    _zz_WhiteboxerPlugin_logic_perf_dispatchHazardsCounter = 1'b0;
    if(WhiteboxerPlugin_logic_perf_dispatchHazards) begin
      _zz_WhiteboxerPlugin_logic_perf_dispatchHazardsCounter = 1'b1;
    end
  end

  always @(*) begin
    _zz_WhiteboxerPlugin_logic_perf_dispatchHazardsCounter_1 = (_zz_WhiteboxerPlugin_logic_perf_dispatchHazardsCounter_2 + _zz__zz_WhiteboxerPlugin_logic_perf_dispatchHazardsCounter_1);
    if(1'b0) begin
      _zz_WhiteboxerPlugin_logic_perf_dispatchHazardsCounter_1 = 60'h0;
    end
  end

  assign WhiteboxerPlugin_logic_perf_dispatchHazardsCounter = _zz_WhiteboxerPlugin_logic_perf_dispatchHazardsCounter_2;
  assign when_Utils_l586 = (WhiteboxerPlugin_logic_perf_candidatesCount == 1'b0);
  always @(*) begin
    _zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_0 = 1'b0;
    if(when_Utils_l586) begin
      _zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_0 = 1'b1;
    end
  end

  always @(*) begin
    _zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_0_1 = (_zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_0_2 + _zz__zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_0_1);
    if(1'b0) begin
      _zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_0_1 = 60'h0;
    end
  end

  assign WhiteboxerPlugin_logic_perf_candidatesCountCounters_0 = _zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_0_2;
  assign when_Utils_l586_1 = (WhiteboxerPlugin_logic_perf_candidatesCount == 1'b1);
  always @(*) begin
    _zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_1 = 1'b0;
    if(when_Utils_l586_1) begin
      _zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_1 = 1'b1;
    end
  end

  always @(*) begin
    _zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_1_1 = (_zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_1_2 + _zz__zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_1_1);
    if(1'b0) begin
      _zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_1_1 = 60'h0;
    end
  end

  assign WhiteboxerPlugin_logic_perf_candidatesCountCounters_1 = _zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_1_2;
  assign when_Utils_l586_2 = (WhiteboxerPlugin_logic_perf_dispatchFeedCount == 1'b0);
  always @(*) begin
    _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_0 = 1'b0;
    if(when_Utils_l586_2) begin
      _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_0 = 1'b1;
    end
  end

  always @(*) begin
    _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_0_1 = (_zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_0_2 + _zz__zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_0_1);
    if(1'b0) begin
      _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_0_1 = 60'h0;
    end
  end

  assign WhiteboxerPlugin_logic_perf_dispatchFeedCounters_0 = _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_0_2;
  assign when_Utils_l586_3 = (WhiteboxerPlugin_logic_perf_dispatchFeedCount == 1'b1);
  always @(*) begin
    _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_1 = 1'b0;
    if(when_Utils_l586_3) begin
      _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_1 = 1'b1;
    end
  end

  always @(*) begin
    _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_1_1 = (_zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_1_2 + _zz__zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_1_1);
    if(1'b0) begin
      _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_1_1 = 60'h0;
    end
  end

  assign WhiteboxerPlugin_logic_perf_dispatchFeedCounters_1 = _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_1_2;
  assign WhiteboxerPlugin_logic_trap_ports_0_valid = TrapPlugin_logic_harts_0_trap_whitebox_trap;
  assign WhiteboxerPlugin_logic_trap_ports_0_interrupt = TrapPlugin_logic_harts_0_trap_whitebox_interrupt;
  assign WhiteboxerPlugin_logic_trap_ports_0_cause = TrapPlugin_logic_harts_0_trap_whitebox_code;
  assign fetch_logic_ctrls_2_up_forgetOne = (|fetch_logic_ctrls_2_forgetsSingleRequest_FetchPipelinePlugin_l50);
  assign fetch_logic_ctrls_2_up_cancel = (|fetch_logic_flushes_1_doIt);
  assign fetch_logic_ctrls_1_up_forgetOne = (|fetch_logic_ctrls_1_throwWhen_FetchPipelinePlugin_l48);
  assign fetch_logic_ctrls_1_up_cancel = (|fetch_logic_ctrls_1_throwWhen_FetchPipelinePlugin_l48);
  assign fetch_logic_ctrls_0_down_ready = fetch_logic_ctrls_1_up_ready;
  assign fetch_logic_ctrls_1_down_ready = fetch_logic_ctrls_2_up_ready;
  always @(*) begin
    fetch_logic_ctrls_0_down_valid = fetch_logic_ctrls_0_up_valid;
    if(when_CtrlLink_l150) begin
      fetch_logic_ctrls_0_down_valid = 1'b0;
    end
  end

  always @(*) begin
    fetch_logic_ctrls_0_up_ready = fetch_logic_ctrls_0_down_isReady;
    if(when_CtrlLink_l150) begin
      fetch_logic_ctrls_0_up_ready = 1'b0;
    end
  end

  assign when_CtrlLink_l150 = (|{fetch_logic_ctrls_0_haltRequest_PcPlugin_l133,{fetch_logic_ctrls_0_haltRequest_BtbPlugin_l200,{fetch_logic_ctrls_0_haltRequest_FetchL1Plugin_l297,fetch_logic_ctrls_0_haltRequest_FetchL1Plugin_l217}}});
  assign fetch_logic_ctrls_0_down_Fetch_WORD_PC = fetch_logic_ctrls_0_up_Fetch_WORD_PC;
  assign fetch_logic_ctrls_0_down_Fetch_PC_FAULT = fetch_logic_ctrls_0_up_Fetch_PC_FAULT;
  assign fetch_logic_ctrls_0_down_Fetch_ID = fetch_logic_ctrls_0_up_Fetch_ID;
  always @(*) begin
    fetch_logic_ctrls_1_down_valid = fetch_logic_ctrls_1_up_valid;
    if(when_CtrlLink_l157) begin
      fetch_logic_ctrls_1_down_valid = 1'b0;
    end
  end

  assign fetch_logic_ctrls_1_up_ready = fetch_logic_ctrls_1_down_isReady;
  assign when_CtrlLink_l157 = (|fetch_logic_ctrls_1_throwWhen_FetchPipelinePlugin_l48);
  assign fetch_logic_ctrls_1_down_Fetch_WORD_PC = fetch_logic_ctrls_1_up_Fetch_WORD_PC;
  assign fetch_logic_ctrls_1_down_Fetch_PC_FAULT = fetch_logic_ctrls_1_up_Fetch_PC_FAULT;
  assign fetch_logic_ctrls_1_down_Fetch_ID = fetch_logic_ctrls_1_up_Fetch_ID;
  assign fetch_logic_ctrls_1_down_FetchL1Plugin_logic_cmd_PLRU_BYPASS_VALID = fetch_logic_ctrls_1_up_FetchL1Plugin_logic_cmd_PLRU_BYPASS_VALID;
  assign fetch_logic_ctrls_1_down_FetchL1Plugin_logic_cmd_TAGS_UPDATE = fetch_logic_ctrls_1_up_FetchL1Plugin_logic_cmd_TAGS_UPDATE;
  assign fetch_logic_ctrls_1_down_FetchL1Plugin_logic_cmd_TAGS_UPDATE_ADDRESS = fetch_logic_ctrls_1_up_FetchL1Plugin_logic_cmd_TAGS_UPDATE_ADDRESS;
  assign fetch_logic_ctrls_1_down_BtbPlugin_logic_readCmd_HAZARDS = fetch_logic_ctrls_1_up_BtbPlugin_logic_readCmd_HAZARDS;
  assign fetch_logic_ctrls_2_down_valid = fetch_logic_ctrls_2_up_valid;
  assign fetch_logic_ctrls_2_up_ready = fetch_logic_ctrls_2_down_isReady;
  assign fetch_logic_ctrls_2_down_Fetch_WORD_PC = fetch_logic_ctrls_2_up_Fetch_WORD_PC;
  assign fetch_logic_ctrls_2_down_Fetch_PC_FAULT = fetch_logic_ctrls_2_up_Fetch_PC_FAULT;
  assign fetch_logic_ctrls_2_down_Fetch_ID = fetch_logic_ctrls_2_up_Fetch_ID;
  assign fetch_logic_ctrls_2_down_FetchL1Plugin_logic_WAYS_TAGS_0_loaded = fetch_logic_ctrls_2_up_FetchL1Plugin_logic_WAYS_TAGS_0_loaded;
  assign fetch_logic_ctrls_2_down_FetchL1Plugin_logic_WAYS_TAGS_0_error = fetch_logic_ctrls_2_up_FetchL1Plugin_logic_WAYS_TAGS_0_error;
  assign fetch_logic_ctrls_2_down_FetchL1Plugin_logic_WAYS_TAGS_0_address = fetch_logic_ctrls_2_up_FetchL1Plugin_logic_WAYS_TAGS_0_address;
  assign fetch_logic_ctrls_2_down_FetchL1Plugin_logic_BANKS_MUXES_0 = fetch_logic_ctrls_2_up_FetchL1Plugin_logic_BANKS_MUXES_0;
  assign fetch_logic_ctrls_2_down_FetchL1Plugin_logic_HAZARD = fetch_logic_ctrls_2_up_FetchL1Plugin_logic_HAZARD;
  assign fetch_logic_ctrls_2_down_FetchL1Plugin_logic_WAYS_HITS_0 = fetch_logic_ctrls_2_up_FetchL1Plugin_logic_WAYS_HITS_0;
  assign fetch_logic_ctrls_2_down_MMU_TRANSLATED = fetch_logic_ctrls_2_up_MMU_TRANSLATED;
  assign fetch_logic_ctrls_2_down_FetchL1Plugin_logic_WAYS_HIT = fetch_logic_ctrls_2_up_FetchL1Plugin_logic_WAYS_HIT;
  assign fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_hash = fetch_logic_ctrls_2_up_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_hash;
  assign fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_pcTarget = fetch_logic_ctrls_2_up_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_pcTarget;
  assign fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isBranch = fetch_logic_ctrls_2_up_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isBranch;
  assign fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isPush = fetch_logic_ctrls_2_up_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isPush;
  assign fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isPop = fetch_logic_ctrls_2_up_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isPop;
  assign fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_taken = fetch_logic_ctrls_2_up_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_taken;
  assign fetch_logic_ctrls_2_down_BtbPlugin_logic_chunksLogic_0_hitCalc_HIT = fetch_logic_ctrls_2_up_BtbPlugin_logic_chunksLogic_0_hitCalc_HIT;
  assign fetch_logic_ctrls_2_down_MMU_REFILL = fetch_logic_ctrls_2_up_MMU_REFILL;
  assign fetch_logic_ctrls_2_down_MMU_HAZARD = fetch_logic_ctrls_2_up_MMU_HAZARD;
  assign fetch_logic_ctrls_2_down_MMU_ALLOW_EXECUTE = fetch_logic_ctrls_2_up_MMU_ALLOW_EXECUTE;
  assign fetch_logic_ctrls_2_down_MMU_PAGE_FAULT = fetch_logic_ctrls_2_up_MMU_PAGE_FAULT;
  assign fetch_logic_ctrls_2_down_MMU_ACCESS_FAULT = fetch_logic_ctrls_2_up_MMU_ACCESS_FAULT;
  assign fetch_logic_ctrls_2_down_MMU_BYPASS_TRANSLATION = fetch_logic_ctrls_2_up_MMU_BYPASS_TRANSLATION;
  always @(*) begin
    decode_ctrls_0_down_ready = decode_ctrls_1_up_ready;
    if(when_StageLink_l67) begin
      decode_ctrls_0_down_ready = 1'b1;
    end
  end

  assign when_StageLink_l67 = (! decode_ctrls_1_up_isValid);
  assign when_DecodePipelinePlugin_l70 = ((! decode_ctrls_1_up_isReady) && decode_ctrls_1_lane0_upIsCancel);
  assign decode_ctrls_0_down_valid = decode_ctrls_0_up_valid;
  assign decode_ctrls_0_up_ready = decode_ctrls_0_down_isReady;
  assign decode_ctrls_0_down_Decode_INSTRUCTION_0 = decode_ctrls_0_up_Decode_INSTRUCTION_0;
  assign decode_ctrls_0_down_Decode_DECOMPRESSION_FAULT_0 = decode_ctrls_0_up_Decode_DECOMPRESSION_FAULT_0;
  assign decode_ctrls_0_down_Decode_INSTRUCTION_RAW_0 = decode_ctrls_0_up_Decode_INSTRUCTION_RAW_0;
  assign decode_ctrls_0_down_PC_0 = decode_ctrls_0_up_PC_0;
  assign decode_ctrls_0_down_Decode_DOP_ID_0 = decode_ctrls_0_up_Decode_DOP_ID_0;
  assign decode_ctrls_0_down_Fetch_ID_0 = decode_ctrls_0_up_Fetch_ID_0;
  assign decode_ctrls_0_down_TRAP_0 = decode_ctrls_0_up_TRAP_0;
  assign decode_ctrls_0_down_Prediction_ALIGNED_JUMPED_0 = decode_ctrls_0_up_Prediction_ALIGNED_JUMPED_0;
  assign decode_ctrls_0_down_Prediction_ALIGNED_JUMPED_PC_0 = decode_ctrls_0_up_Prediction_ALIGNED_JUMPED_PC_0;
  assign decode_ctrls_0_down_Prediction_ALIGNED_SLICES_BRANCH_0 = decode_ctrls_0_up_Prediction_ALIGNED_SLICES_BRANCH_0;
  assign decode_ctrls_0_down_Prediction_ALIGNED_SLICES_TAKEN_0 = decode_ctrls_0_up_Prediction_ALIGNED_SLICES_TAKEN_0;
  assign decode_ctrls_0_down_Prediction_ALIGN_REDO_0 = decode_ctrls_0_up_Prediction_ALIGN_REDO_0;
  assign decode_ctrls_1_down_valid = decode_ctrls_1_up_valid;
  assign decode_ctrls_1_up_ready = decode_ctrls_1_down_isReady;
  assign decode_ctrls_1_down_Decode_INSTRUCTION_0 = decode_ctrls_1_up_Decode_INSTRUCTION_0;
  assign decode_ctrls_1_down_Decode_DECOMPRESSION_FAULT_0 = decode_ctrls_1_up_Decode_DECOMPRESSION_FAULT_0;
  assign decode_ctrls_1_down_Decode_INSTRUCTION_RAW_0 = decode_ctrls_1_up_Decode_INSTRUCTION_RAW_0;
  assign decode_ctrls_1_down_PC_0 = decode_ctrls_1_up_PC_0;
  assign decode_ctrls_1_down_Decode_DOP_ID_0 = decode_ctrls_1_up_Decode_DOP_ID_0;
  assign decode_ctrls_1_down_Prediction_ALIGNED_JUMPED_0 = decode_ctrls_1_up_Prediction_ALIGNED_JUMPED_0;
  assign decode_ctrls_1_down_Prediction_ALIGNED_JUMPED_PC_0 = decode_ctrls_1_up_Prediction_ALIGNED_JUMPED_PC_0;
  assign decode_ctrls_1_down_Prediction_ALIGNED_SLICES_BRANCH_0 = decode_ctrls_1_up_Prediction_ALIGNED_SLICES_BRANCH_0;
  assign decode_ctrls_1_down_Prediction_ALIGNED_SLICES_TAKEN_0 = decode_ctrls_1_up_Prediction_ALIGNED_SLICES_TAKEN_0;
  assign decode_ctrls_1_down_Prediction_ALIGN_REDO_0 = decode_ctrls_1_up_Prediction_ALIGN_REDO_0;
  assign execute_ctrl0_down_ready = execute_ctrl1_up_ready;
  assign execute_ctrl1_down_ready = execute_ctrl2_up_ready;
  assign execute_ctrl2_down_ready = execute_ctrl3_up_ready;
  assign execute_ctrl3_down_ready = execute_ctrl4_up_ready;
  assign execute_ctrl4_down_ready = execute_ctrl5_up_ready;
  assign execute_ctrl0_up_ready = execute_ctrl0_down_isReady;
  assign execute_ctrl0_down_Decode_UOP_lane0 = execute_ctrl0_up_Decode_UOP_lane0;
  assign execute_ctrl0_down_Prediction_ALIGNED_JUMPED_lane0 = execute_ctrl0_up_Prediction_ALIGNED_JUMPED_lane0;
  assign execute_ctrl0_down_Prediction_ALIGNED_JUMPED_PC_lane0 = execute_ctrl0_up_Prediction_ALIGNED_JUMPED_PC_lane0;
  assign execute_ctrl0_down_PC_lane0 = execute_ctrl0_up_PC_lane0;
  assign execute_ctrl0_down_TRAP_lane0 = execute_ctrl0_up_TRAP_lane0;
  assign execute_ctrl0_down_Decode_UOP_ID_lane0 = execute_ctrl0_up_Decode_UOP_ID_lane0;
  assign execute_ctrl0_down_RS1_PHYS_lane0 = execute_ctrl0_up_RS1_PHYS_lane0;
  assign execute_ctrl0_down_RS2_PHYS_lane0 = execute_ctrl0_up_RS2_PHYS_lane0;
  assign execute_ctrl0_down_RD_PHYS_lane0 = execute_ctrl0_up_RD_PHYS_lane0;
  assign execute_ctrl0_down_COMPLETED_lane0 = execute_ctrl0_up_COMPLETED_lane0;
  assign execute_ctrl0_down_lane0_LAYER_SEL_lane0 = execute_ctrl0_up_lane0_LAYER_SEL_lane0;
  assign execute_ctrl1_up_ready = execute_ctrl1_down_isReady;
  assign execute_ctrl1_down_Decode_UOP_lane0 = execute_ctrl1_up_Decode_UOP_lane0;
  assign execute_ctrl1_down_Prediction_ALIGNED_JUMPED_lane0 = execute_ctrl1_up_Prediction_ALIGNED_JUMPED_lane0;
  assign execute_ctrl1_down_Prediction_ALIGNED_JUMPED_PC_lane0 = execute_ctrl1_up_Prediction_ALIGNED_JUMPED_PC_lane0;
  assign execute_ctrl1_down_PC_lane0 = execute_ctrl1_up_PC_lane0;
  assign execute_ctrl1_down_TRAP_lane0 = execute_ctrl1_up_TRAP_lane0;
  assign execute_ctrl1_down_Decode_UOP_ID_lane0 = execute_ctrl1_up_Decode_UOP_ID_lane0;
  assign execute_ctrl1_down_RS1_PHYS_lane0 = execute_ctrl1_up_RS1_PHYS_lane0;
  assign execute_ctrl1_down_RS2_PHYS_lane0 = execute_ctrl1_up_RS2_PHYS_lane0;
  assign execute_ctrl1_down_RD_PHYS_lane0 = execute_ctrl1_up_RD_PHYS_lane0;
  assign execute_ctrl1_down_COMPLETED_lane0 = execute_ctrl1_up_COMPLETED_lane0;
  assign execute_ctrl1_down_lane0_LAYER_SEL_lane0 = execute_ctrl1_up_lane0_LAYER_SEL_lane0;
  assign execute_ctrl1_down_AguPlugin_SIZE_lane0 = execute_ctrl1_up_AguPlugin_SIZE_lane0;
  assign execute_ctrl2_up_ready = execute_ctrl2_down_isReady;
  assign execute_ctrl2_down_Decode_UOP_lane0 = execute_ctrl2_up_Decode_UOP_lane0;
  assign execute_ctrl2_down_Prediction_ALIGNED_JUMPED_lane0 = execute_ctrl2_up_Prediction_ALIGNED_JUMPED_lane0;
  assign execute_ctrl2_down_Prediction_ALIGNED_JUMPED_PC_lane0 = execute_ctrl2_up_Prediction_ALIGNED_JUMPED_PC_lane0;
  assign execute_ctrl2_down_PC_lane0 = execute_ctrl2_up_PC_lane0;
  assign execute_ctrl2_down_Decode_UOP_ID_lane0 = execute_ctrl2_up_Decode_UOP_ID_lane0;
  assign execute_ctrl2_down_RS1_PHYS_lane0 = execute_ctrl2_up_RS1_PHYS_lane0;
  assign execute_ctrl2_down_RS2_PHYS_lane0 = execute_ctrl2_up_RS2_PHYS_lane0;
  assign execute_ctrl2_down_RD_PHYS_lane0 = execute_ctrl2_up_RD_PHYS_lane0;
  assign execute_ctrl2_down_AguPlugin_SIZE_lane0 = execute_ctrl2_up_AguPlugin_SIZE_lane0;
  assign execute_ctrl2_down_early0_SrcPlugin_SRC1_lane0 = execute_ctrl2_up_early0_SrcPlugin_SRC1_lane0;
  assign execute_ctrl2_down_early0_SrcPlugin_SRC2_lane0 = execute_ctrl2_up_early0_SrcPlugin_SRC2_lane0;
  assign execute_ctrl2_down_MAY_FLUSH_PRECISE_3_lane0 = execute_ctrl2_up_MAY_FLUSH_PRECISE_3_lane0;
  assign execute_ctrl2_down_early0_IntAluPlugin_SEL_lane0 = execute_ctrl2_up_early0_IntAluPlugin_SEL_lane0;
  assign execute_ctrl2_down_early0_BarrelShifterPlugin_SEL_lane0 = execute_ctrl2_up_early0_BarrelShifterPlugin_SEL_lane0;
  assign execute_ctrl2_down_early0_BranchPlugin_SEL_lane0 = execute_ctrl2_up_early0_BranchPlugin_SEL_lane0;
  assign execute_ctrl2_down_early0_MulPlugin_SEL_lane0 = execute_ctrl2_up_early0_MulPlugin_SEL_lane0;
  assign execute_ctrl2_down_early0_DivPlugin_SEL_lane0 = execute_ctrl2_up_early0_DivPlugin_SEL_lane0;
  assign execute_ctrl2_down_early0_EnvPlugin_SEL_lane0 = execute_ctrl2_up_early0_EnvPlugin_SEL_lane0;
  assign execute_ctrl2_down_late0_IntAluPlugin_SEL_lane0 = execute_ctrl2_up_late0_IntAluPlugin_SEL_lane0;
  assign execute_ctrl2_down_late0_BarrelShifterPlugin_SEL_lane0 = execute_ctrl2_up_late0_BarrelShifterPlugin_SEL_lane0;
  assign execute_ctrl2_down_late0_BranchPlugin_SEL_lane0 = execute_ctrl2_up_late0_BranchPlugin_SEL_lane0;
  assign execute_ctrl2_down_CsrAccessPlugin_SEL_lane0 = execute_ctrl2_up_CsrAccessPlugin_SEL_lane0;
  assign execute_ctrl2_down_AguPlugin_SEL_lane0 = execute_ctrl2_up_AguPlugin_SEL_lane0;
  assign execute_ctrl2_down_LsuPlugin_logic_FENCE_lane0 = execute_ctrl2_up_LsuPlugin_logic_FENCE_lane0;
  assign execute_ctrl2_down_lane0_integer_WriteBackPlugin_SEL_lane0 = execute_ctrl2_up_lane0_integer_WriteBackPlugin_SEL_lane0;
  assign execute_ctrl2_down_COMPLETION_AT_2_lane0 = execute_ctrl2_up_COMPLETION_AT_2_lane0;
  assign execute_ctrl2_down_COMPLETION_AT_4_lane0 = execute_ctrl2_up_COMPLETION_AT_4_lane0;
  assign execute_ctrl2_down_COMPLETION_AT_3_lane0 = execute_ctrl2_up_COMPLETION_AT_3_lane0;
  assign execute_ctrl2_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0 = execute_ctrl2_up_lane0_logic_completions_onCtrl_0_ENABLE_lane0;
  assign execute_ctrl2_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0 = execute_ctrl2_up_lane0_logic_completions_onCtrl_1_ENABLE_lane0;
  assign execute_ctrl2_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0 = execute_ctrl2_up_lane0_logic_completions_onCtrl_2_ENABLE_lane0;
  assign execute_ctrl2_down_early0_IntAluPlugin_ALU_ADD_SUB_lane0 = execute_ctrl2_up_early0_IntAluPlugin_ALU_ADD_SUB_lane0;
  assign execute_ctrl2_down_early0_IntAluPlugin_ALU_SLTX_lane0 = execute_ctrl2_up_early0_IntAluPlugin_ALU_SLTX_lane0;
  assign execute_ctrl2_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0 = execute_ctrl2_up_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0;
  assign execute_ctrl2_down_SrcStageables_REVERT_lane0 = execute_ctrl2_up_SrcStageables_REVERT_lane0;
  assign execute_ctrl2_down_SrcStageables_ZERO_lane0 = execute_ctrl2_up_SrcStageables_ZERO_lane0;
  assign execute_ctrl2_down_lane0_IntFormatPlugin_logic_SIGNED_lane0 = execute_ctrl2_up_lane0_IntFormatPlugin_logic_SIGNED_lane0;
  assign execute_ctrl2_down_lane0_IntFormatPlugin_logic_WIDTH_ID_lane0 = execute_ctrl2_up_lane0_IntFormatPlugin_logic_WIDTH_ID_lane0;
  assign execute_ctrl2_down_BYPASSED_AT_3_lane0 = execute_ctrl2_up_BYPASSED_AT_3_lane0;
  assign execute_ctrl2_down_SrcStageables_UNSIGNED_lane0 = execute_ctrl2_up_SrcStageables_UNSIGNED_lane0;
  assign execute_ctrl2_down_BarrelShifterPlugin_LEFT_lane0 = execute_ctrl2_up_BarrelShifterPlugin_LEFT_lane0;
  assign execute_ctrl2_down_BarrelShifterPlugin_SIGNED_lane0 = execute_ctrl2_up_BarrelShifterPlugin_SIGNED_lane0;
  assign execute_ctrl2_down_BranchPlugin_BRANCH_CTRL_lane0 = execute_ctrl2_up_BranchPlugin_BRANCH_CTRL_lane0;
  assign execute_ctrl2_down_MulPlugin_HIGH_lane0 = execute_ctrl2_up_MulPlugin_HIGH_lane0;
  assign execute_ctrl2_down_RsUnsignedPlugin_RS1_SIGNED_lane0 = execute_ctrl2_up_RsUnsignedPlugin_RS1_SIGNED_lane0;
  assign execute_ctrl2_down_RsUnsignedPlugin_RS2_SIGNED_lane0 = execute_ctrl2_up_RsUnsignedPlugin_RS2_SIGNED_lane0;
  assign execute_ctrl2_down_DivPlugin_REM_lane0 = execute_ctrl2_up_DivPlugin_REM_lane0;
  assign execute_ctrl2_down_CsrAccessPlugin_CSR_IMM_lane0 = execute_ctrl2_up_CsrAccessPlugin_CSR_IMM_lane0;
  assign execute_ctrl2_down_CsrAccessPlugin_CSR_MASK_lane0 = execute_ctrl2_up_CsrAccessPlugin_CSR_MASK_lane0;
  assign execute_ctrl2_down_CsrAccessPlugin_CSR_CLEAR_lane0 = execute_ctrl2_up_CsrAccessPlugin_CSR_CLEAR_lane0;
  assign execute_ctrl2_down_AguPlugin_LOAD_lane0 = execute_ctrl2_up_AguPlugin_LOAD_lane0;
  assign execute_ctrl2_down_AguPlugin_STORE_lane0 = execute_ctrl2_up_AguPlugin_STORE_lane0;
  assign execute_ctrl2_down_AguPlugin_ATOMIC_lane0 = execute_ctrl2_up_AguPlugin_ATOMIC_lane0;
  assign execute_ctrl2_down_AguPlugin_FLOAT_lane0 = execute_ctrl2_up_AguPlugin_FLOAT_lane0;
  assign execute_ctrl2_down_LsuPlugin_logic_LSU_PREFETCH_lane0 = execute_ctrl2_up_LsuPlugin_logic_LSU_PREFETCH_lane0;
  assign execute_ctrl2_down_early0_EnvPlugin_OP_lane0 = execute_ctrl2_up_early0_EnvPlugin_OP_lane0;
  assign execute_ctrl2_down_late0_IntAluPlugin_ALU_ADD_SUB_lane0 = execute_ctrl2_up_late0_IntAluPlugin_ALU_ADD_SUB_lane0;
  assign execute_ctrl2_down_late0_IntAluPlugin_ALU_SLTX_lane0 = execute_ctrl2_up_late0_IntAluPlugin_ALU_SLTX_lane0;
  assign execute_ctrl2_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0 = execute_ctrl2_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0;
  assign execute_ctrl2_down_late0_SrcPlugin_logic_SRC1_CTRL_lane0 = execute_ctrl2_up_late0_SrcPlugin_logic_SRC1_CTRL_lane0;
  assign execute_ctrl2_down_late0_SrcPlugin_logic_SRC2_CTRL_lane0 = execute_ctrl2_up_late0_SrcPlugin_logic_SRC2_CTRL_lane0;
  assign execute_ctrl3_up_ready = execute_ctrl3_down_isReady;
  assign execute_ctrl3_down_Decode_UOP_lane0 = execute_ctrl3_up_Decode_UOP_lane0;
  assign execute_ctrl3_down_Prediction_ALIGNED_JUMPED_lane0 = execute_ctrl3_up_Prediction_ALIGNED_JUMPED_lane0;
  assign execute_ctrl3_down_Prediction_ALIGNED_JUMPED_PC_lane0 = execute_ctrl3_up_Prediction_ALIGNED_JUMPED_PC_lane0;
  assign execute_ctrl3_down_PC_lane0 = execute_ctrl3_up_PC_lane0;
  assign execute_ctrl3_down_TRAP_lane0 = execute_ctrl3_up_TRAP_lane0;
  assign execute_ctrl3_down_Decode_UOP_ID_lane0 = execute_ctrl3_up_Decode_UOP_ID_lane0;
  assign execute_ctrl3_down_RS1_PHYS_lane0 = execute_ctrl3_up_RS1_PHYS_lane0;
  assign execute_ctrl3_down_RS2_PHYS_lane0 = execute_ctrl3_up_RS2_PHYS_lane0;
  assign execute_ctrl3_down_RD_PHYS_lane0 = execute_ctrl3_up_RD_PHYS_lane0;
  assign execute_ctrl3_down_AguPlugin_SIZE_lane0 = execute_ctrl3_up_AguPlugin_SIZE_lane0;
  assign execute_ctrl3_down_early0_BranchPlugin_SEL_lane0 = execute_ctrl3_up_early0_BranchPlugin_SEL_lane0;
  assign execute_ctrl3_down_early0_MulPlugin_SEL_lane0 = execute_ctrl3_up_early0_MulPlugin_SEL_lane0;
  assign execute_ctrl3_down_early0_DivPlugin_SEL_lane0 = execute_ctrl3_up_early0_DivPlugin_SEL_lane0;
  assign execute_ctrl3_down_late0_IntAluPlugin_SEL_lane0 = execute_ctrl3_up_late0_IntAluPlugin_SEL_lane0;
  assign execute_ctrl3_down_late0_BarrelShifterPlugin_SEL_lane0 = execute_ctrl3_up_late0_BarrelShifterPlugin_SEL_lane0;
  assign execute_ctrl3_down_late0_BranchPlugin_SEL_lane0 = execute_ctrl3_up_late0_BranchPlugin_SEL_lane0;
  assign execute_ctrl3_down_CsrAccessPlugin_SEL_lane0 = execute_ctrl3_up_CsrAccessPlugin_SEL_lane0;
  assign execute_ctrl3_down_AguPlugin_SEL_lane0 = execute_ctrl3_up_AguPlugin_SEL_lane0;
  assign execute_ctrl3_down_LsuPlugin_logic_FENCE_lane0 = execute_ctrl3_up_LsuPlugin_logic_FENCE_lane0;
  assign execute_ctrl3_down_lane0_integer_WriteBackPlugin_SEL_lane0 = execute_ctrl3_up_lane0_integer_WriteBackPlugin_SEL_lane0;
  assign execute_ctrl3_down_COMPLETION_AT_4_lane0 = execute_ctrl3_up_COMPLETION_AT_4_lane0;
  assign execute_ctrl3_down_COMPLETION_AT_3_lane0 = execute_ctrl3_up_COMPLETION_AT_3_lane0;
  assign execute_ctrl3_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0 = execute_ctrl3_up_lane0_logic_completions_onCtrl_1_ENABLE_lane0;
  assign execute_ctrl3_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0 = execute_ctrl3_up_lane0_logic_completions_onCtrl_2_ENABLE_lane0;
  assign execute_ctrl3_down_SrcStageables_REVERT_lane0 = execute_ctrl3_up_SrcStageables_REVERT_lane0;
  assign execute_ctrl3_down_SrcStageables_ZERO_lane0 = execute_ctrl3_up_SrcStageables_ZERO_lane0;
  assign execute_ctrl3_down_lane0_IntFormatPlugin_logic_SIGNED_lane0 = execute_ctrl3_up_lane0_IntFormatPlugin_logic_SIGNED_lane0;
  assign execute_ctrl3_down_lane0_IntFormatPlugin_logic_WIDTH_ID_lane0 = execute_ctrl3_up_lane0_IntFormatPlugin_logic_WIDTH_ID_lane0;
  assign execute_ctrl3_down_SrcStageables_UNSIGNED_lane0 = execute_ctrl3_up_SrcStageables_UNSIGNED_lane0;
  assign execute_ctrl3_down_BarrelShifterPlugin_LEFT_lane0 = execute_ctrl3_up_BarrelShifterPlugin_LEFT_lane0;
  assign execute_ctrl3_down_BarrelShifterPlugin_SIGNED_lane0 = execute_ctrl3_up_BarrelShifterPlugin_SIGNED_lane0;
  assign execute_ctrl3_down_BranchPlugin_BRANCH_CTRL_lane0 = execute_ctrl3_up_BranchPlugin_BRANCH_CTRL_lane0;
  assign execute_ctrl3_down_MulPlugin_HIGH_lane0 = execute_ctrl3_up_MulPlugin_HIGH_lane0;
  assign execute_ctrl3_down_AguPlugin_LOAD_lane0 = execute_ctrl3_up_AguPlugin_LOAD_lane0;
  assign execute_ctrl3_down_AguPlugin_STORE_lane0 = execute_ctrl3_up_AguPlugin_STORE_lane0;
  assign execute_ctrl3_down_AguPlugin_ATOMIC_lane0 = execute_ctrl3_up_AguPlugin_ATOMIC_lane0;
  assign execute_ctrl3_down_AguPlugin_FLOAT_lane0 = execute_ctrl3_up_AguPlugin_FLOAT_lane0;
  assign execute_ctrl3_down_LsuPlugin_logic_LSU_PREFETCH_lane0 = execute_ctrl3_up_LsuPlugin_logic_LSU_PREFETCH_lane0;
  assign execute_ctrl3_down_late0_IntAluPlugin_ALU_ADD_SUB_lane0 = execute_ctrl3_up_late0_IntAluPlugin_ALU_ADD_SUB_lane0;
  assign execute_ctrl3_down_late0_IntAluPlugin_ALU_SLTX_lane0 = execute_ctrl3_up_late0_IntAluPlugin_ALU_SLTX_lane0;
  assign execute_ctrl3_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0 = execute_ctrl3_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0;
  assign execute_ctrl3_down_late0_SrcPlugin_logic_SRC1_CTRL_lane0 = execute_ctrl3_up_late0_SrcPlugin_logic_SRC1_CTRL_lane0;
  assign execute_ctrl3_down_late0_SrcPlugin_logic_SRC2_CTRL_lane0 = execute_ctrl3_up_late0_SrcPlugin_logic_SRC2_CTRL_lane0;
  assign execute_ctrl3_down_COMMIT_lane0 = execute_ctrl3_up_COMMIT_lane0;
  assign execute_ctrl3_down_early0_SrcPlugin_ADD_SUB_lane0 = execute_ctrl3_up_early0_SrcPlugin_ADD_SUB_lane0;
  assign execute_ctrl3_down_LsuL1_MIXED_ADDRESS_lane0 = execute_ctrl3_up_LsuL1_MIXED_ADDRESS_lane0;
  assign execute_ctrl3_down_LsuL1Plugin_logic_BANK_BUSY_lane0 = execute_ctrl3_up_LsuL1Plugin_logic_BANK_BUSY_lane0;
  assign execute_ctrl3_down_LsuL1Plugin_logic_EVENT_WRITE_VALID_lane0 = execute_ctrl3_up_LsuL1Plugin_logic_EVENT_WRITE_VALID_lane0;
  assign execute_ctrl3_down_LsuL1Plugin_logic_EVENT_WRITE_ADDRESS_lane0 = execute_ctrl3_up_LsuL1Plugin_logic_EVENT_WRITE_ADDRESS_lane0;
  assign execute_ctrl3_down_LsuL1Plugin_logic_EVENT_WRITE_MASK_lane0 = execute_ctrl3_up_LsuL1Plugin_logic_EVENT_WRITE_MASK_lane0;
  assign execute_ctrl3_down_LsuL1Plugin_logic_lsu_rt0_SHARED_BYPASS_VALID_lane0 = execute_ctrl3_up_LsuL1Plugin_logic_lsu_rt0_SHARED_BYPASS_VALID_lane0;
  assign execute_ctrl3_down_LsuL1Plugin_logic_lsu_rt0_SHARED_BYPASS_VALUE_lane0_dirty = execute_ctrl3_up_LsuL1Plugin_logic_lsu_rt0_SHARED_BYPASS_VALUE_lane0_dirty;
  assign execute_ctrl3_down_early0_MulPlugin_logic_mul_VALUES_0_lane0 = execute_ctrl3_up_early0_MulPlugin_logic_mul_VALUES_0_lane0;
  assign execute_ctrl3_down_early0_MulPlugin_logic_mul_VALUES_1_lane0 = execute_ctrl3_up_early0_MulPlugin_logic_mul_VALUES_1_lane0;
  assign execute_ctrl3_down_early0_MulPlugin_logic_mul_VALUES_2_lane0 = execute_ctrl3_up_early0_MulPlugin_logic_mul_VALUES_2_lane0;
  assign execute_ctrl3_down_early0_MulPlugin_logic_mul_VALUES_3_lane0 = execute_ctrl3_up_early0_MulPlugin_logic_mul_VALUES_3_lane0;
  assign execute_ctrl3_down_DivPlugin_DIV_RESULT_lane0 = execute_ctrl3_up_DivPlugin_DIV_RESULT_lane0;
  assign execute_ctrl3_down_early0_BranchPlugin_pcCalc_PC_TRUE_lane0 = execute_ctrl3_up_early0_BranchPlugin_pcCalc_PC_TRUE_lane0;
  assign execute_ctrl3_down_early0_BranchPlugin_pcCalc_PC_FALSE_lane0 = execute_ctrl3_up_early0_BranchPlugin_pcCalc_PC_FALSE_lane0;
  assign execute_ctrl3_down_early0_BranchPlugin_pcCalc_PC_LAST_SLICE_lane0 = execute_ctrl3_up_early0_BranchPlugin_pcCalc_PC_LAST_SLICE_lane0;
  assign execute_ctrl3_down_LsuPlugin_logic_FROM_ACCESS_lane0 = execute_ctrl3_up_LsuPlugin_logic_FROM_ACCESS_lane0;
  assign execute_ctrl3_down_LsuL1_MASK_lane0 = execute_ctrl3_up_LsuL1_MASK_lane0;
  assign execute_ctrl3_down_LsuL1_SIZE_lane0 = execute_ctrl3_up_LsuL1_SIZE_lane0;
  assign execute_ctrl3_down_LsuL1_LOAD_lane0 = execute_ctrl3_up_LsuL1_LOAD_lane0;
  assign execute_ctrl3_down_LsuL1_ATOMIC_lane0 = execute_ctrl3_up_LsuL1_ATOMIC_lane0;
  assign execute_ctrl3_down_LsuL1_STORE_lane0 = execute_ctrl3_up_LsuL1_STORE_lane0;
  assign execute_ctrl3_down_LsuL1_CLEAN_lane0 = execute_ctrl3_up_LsuL1_CLEAN_lane0;
  assign execute_ctrl3_down_LsuL1_INVALID_lane0 = execute_ctrl3_up_LsuL1_INVALID_lane0;
  assign execute_ctrl3_down_LsuL1_PREFETCH_lane0 = execute_ctrl3_up_LsuL1_PREFETCH_lane0;
  assign execute_ctrl3_down_LsuL1_FLUSH_lane0 = execute_ctrl3_up_LsuL1_FLUSH_lane0;
  assign execute_ctrl3_down_Decode_STORE_ID_lane0 = execute_ctrl3_up_Decode_STORE_ID_lane0;
  assign execute_ctrl3_down_LsuPlugin_logic_FROM_LSU_lane0 = execute_ctrl3_up_LsuPlugin_logic_FROM_LSU_lane0;
  assign execute_ctrl3_down_LsuPlugin_logic_FROM_PREFETCH_lane0 = execute_ctrl3_up_LsuPlugin_logic_FROM_PREFETCH_lane0;
  assign execute_ctrl4_up_ready = execute_ctrl4_down_isReady;
  assign execute_ctrl4_down_Decode_UOP_lane0 = execute_ctrl4_up_Decode_UOP_lane0;
  assign execute_ctrl4_down_Prediction_ALIGNED_JUMPED_lane0 = execute_ctrl4_up_Prediction_ALIGNED_JUMPED_lane0;
  assign execute_ctrl4_down_Prediction_ALIGNED_JUMPED_PC_lane0 = execute_ctrl4_up_Prediction_ALIGNED_JUMPED_PC_lane0;
  assign execute_ctrl4_down_PC_lane0 = execute_ctrl4_up_PC_lane0;
  assign execute_ctrl4_down_Decode_UOP_ID_lane0 = execute_ctrl4_up_Decode_UOP_ID_lane0;
  assign execute_ctrl4_down_RD_PHYS_lane0 = execute_ctrl4_up_RD_PHYS_lane0;
  assign execute_ctrl4_down_AguPlugin_SIZE_lane0 = execute_ctrl4_up_AguPlugin_SIZE_lane0;
  assign execute_ctrl4_down_early0_BranchPlugin_SEL_lane0 = execute_ctrl4_up_early0_BranchPlugin_SEL_lane0;
  assign execute_ctrl4_down_early0_MulPlugin_SEL_lane0 = execute_ctrl4_up_early0_MulPlugin_SEL_lane0;
  assign execute_ctrl4_down_late0_IntAluPlugin_SEL_lane0 = execute_ctrl4_up_late0_IntAluPlugin_SEL_lane0;
  assign execute_ctrl4_down_late0_BarrelShifterPlugin_SEL_lane0 = execute_ctrl4_up_late0_BarrelShifterPlugin_SEL_lane0;
  assign execute_ctrl4_down_late0_BranchPlugin_SEL_lane0 = execute_ctrl4_up_late0_BranchPlugin_SEL_lane0;
  assign execute_ctrl4_down_AguPlugin_SEL_lane0 = execute_ctrl4_up_AguPlugin_SEL_lane0;
  assign execute_ctrl4_down_LsuPlugin_logic_FENCE_lane0 = execute_ctrl4_up_LsuPlugin_logic_FENCE_lane0;
  assign execute_ctrl4_down_lane0_integer_WriteBackPlugin_SEL_lane0 = execute_ctrl4_up_lane0_integer_WriteBackPlugin_SEL_lane0;
  assign execute_ctrl4_down_COMPLETION_AT_4_lane0 = execute_ctrl4_up_COMPLETION_AT_4_lane0;
  assign execute_ctrl4_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0 = execute_ctrl4_up_lane0_logic_completions_onCtrl_1_ENABLE_lane0;
  assign execute_ctrl4_down_SrcStageables_REVERT_lane0 = execute_ctrl4_up_SrcStageables_REVERT_lane0;
  assign execute_ctrl4_down_SrcStageables_ZERO_lane0 = execute_ctrl4_up_SrcStageables_ZERO_lane0;
  assign execute_ctrl4_down_lane0_IntFormatPlugin_logic_SIGNED_lane0 = execute_ctrl4_up_lane0_IntFormatPlugin_logic_SIGNED_lane0;
  assign execute_ctrl4_down_lane0_IntFormatPlugin_logic_WIDTH_ID_lane0 = execute_ctrl4_up_lane0_IntFormatPlugin_logic_WIDTH_ID_lane0;
  assign execute_ctrl4_down_SrcStageables_UNSIGNED_lane0 = execute_ctrl4_up_SrcStageables_UNSIGNED_lane0;
  assign execute_ctrl4_down_BarrelShifterPlugin_LEFT_lane0 = execute_ctrl4_up_BarrelShifterPlugin_LEFT_lane0;
  assign execute_ctrl4_down_BarrelShifterPlugin_SIGNED_lane0 = execute_ctrl4_up_BarrelShifterPlugin_SIGNED_lane0;
  assign execute_ctrl4_down_BranchPlugin_BRANCH_CTRL_lane0 = execute_ctrl4_up_BranchPlugin_BRANCH_CTRL_lane0;
  assign execute_ctrl4_down_MulPlugin_HIGH_lane0 = execute_ctrl4_up_MulPlugin_HIGH_lane0;
  assign execute_ctrl4_down_AguPlugin_LOAD_lane0 = execute_ctrl4_up_AguPlugin_LOAD_lane0;
  assign execute_ctrl4_down_AguPlugin_STORE_lane0 = execute_ctrl4_up_AguPlugin_STORE_lane0;
  assign execute_ctrl4_down_AguPlugin_ATOMIC_lane0 = execute_ctrl4_up_AguPlugin_ATOMIC_lane0;
  assign execute_ctrl4_down_AguPlugin_FLOAT_lane0 = execute_ctrl4_up_AguPlugin_FLOAT_lane0;
  assign execute_ctrl4_down_LsuPlugin_logic_LSU_PREFETCH_lane0 = execute_ctrl4_up_LsuPlugin_logic_LSU_PREFETCH_lane0;
  assign execute_ctrl4_down_late0_IntAluPlugin_ALU_ADD_SUB_lane0 = execute_ctrl4_up_late0_IntAluPlugin_ALU_ADD_SUB_lane0;
  assign execute_ctrl4_down_late0_IntAluPlugin_ALU_SLTX_lane0 = execute_ctrl4_up_late0_IntAluPlugin_ALU_SLTX_lane0;
  assign execute_ctrl4_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0 = execute_ctrl4_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0;
  assign execute_ctrl4_down_LsuL1_MIXED_ADDRESS_lane0 = execute_ctrl4_up_LsuL1_MIXED_ADDRESS_lane0;
  assign execute_ctrl4_down_early0_MulPlugin_logic_mul_VALUES_0_lane0 = execute_ctrl4_up_early0_MulPlugin_logic_mul_VALUES_0_lane0;
  assign execute_ctrl4_down_early0_MulPlugin_logic_mul_VALUES_1_lane0 = execute_ctrl4_up_early0_MulPlugin_logic_mul_VALUES_1_lane0;
  assign execute_ctrl4_down_early0_MulPlugin_logic_mul_VALUES_2_lane0 = execute_ctrl4_up_early0_MulPlugin_logic_mul_VALUES_2_lane0;
  assign execute_ctrl4_down_early0_MulPlugin_logic_mul_VALUES_3_lane0 = execute_ctrl4_up_early0_MulPlugin_logic_mul_VALUES_3_lane0;
  assign execute_ctrl4_down_early0_BranchPlugin_pcCalc_PC_TRUE_lane0 = execute_ctrl4_up_early0_BranchPlugin_pcCalc_PC_TRUE_lane0;
  assign execute_ctrl4_down_early0_BranchPlugin_pcCalc_PC_FALSE_lane0 = execute_ctrl4_up_early0_BranchPlugin_pcCalc_PC_FALSE_lane0;
  assign execute_ctrl4_down_early0_BranchPlugin_pcCalc_PC_LAST_SLICE_lane0 = execute_ctrl4_up_early0_BranchPlugin_pcCalc_PC_LAST_SLICE_lane0;
  assign execute_ctrl4_down_LsuL1_MASK_lane0 = execute_ctrl4_up_LsuL1_MASK_lane0;
  assign execute_ctrl4_down_LsuL1_SIZE_lane0 = execute_ctrl4_up_LsuL1_SIZE_lane0;
  assign execute_ctrl4_down_LsuL1_LOAD_lane0 = execute_ctrl4_up_LsuL1_LOAD_lane0;
  assign execute_ctrl4_down_LsuL1_ATOMIC_lane0 = execute_ctrl4_up_LsuL1_ATOMIC_lane0;
  assign execute_ctrl4_down_LsuL1_STORE_lane0 = execute_ctrl4_up_LsuL1_STORE_lane0;
  assign execute_ctrl4_down_LsuL1_CLEAN_lane0 = execute_ctrl4_up_LsuL1_CLEAN_lane0;
  assign execute_ctrl4_down_LsuL1_INVALID_lane0 = execute_ctrl4_up_LsuL1_INVALID_lane0;
  assign execute_ctrl4_down_LsuL1_PREFETCH_lane0 = execute_ctrl4_up_LsuL1_PREFETCH_lane0;
  assign execute_ctrl4_down_LsuL1_FLUSH_lane0 = execute_ctrl4_up_LsuL1_FLUSH_lane0;
  assign execute_ctrl4_down_Decode_STORE_ID_lane0 = execute_ctrl4_up_Decode_STORE_ID_lane0;
  assign execute_ctrl4_down_LsuPlugin_logic_FROM_LSU_lane0 = execute_ctrl4_up_LsuPlugin_logic_FROM_LSU_lane0;
  assign execute_ctrl4_down_LsuPlugin_logic_FROM_PREFETCH_lane0 = execute_ctrl4_up_LsuPlugin_logic_FROM_PREFETCH_lane0;
  assign execute_ctrl4_down_LsuL1Plugin_logic_SHARED_lane0_dirty = execute_ctrl4_up_LsuL1Plugin_logic_SHARED_lane0_dirty;
  assign execute_ctrl4_down_LsuL1Plugin_logic_BANK_BUSY_REMAPPED_lane0 = execute_ctrl4_up_LsuL1Plugin_logic_BANK_BUSY_REMAPPED_lane0;
  assign execute_ctrl4_down_LsuL1Plugin_logic_BANKS_MUXES_lane0_0 = execute_ctrl4_up_LsuL1Plugin_logic_BANKS_MUXES_lane0_0;
  assign execute_ctrl4_down_LsuL1Plugin_logic_WRITE_TO_READ_HAZARDS_lane0 = execute_ctrl4_up_LsuL1Plugin_logic_WRITE_TO_READ_HAZARDS_lane0;
  assign execute_ctrl4_down_LsuL1_PHYSICAL_ADDRESS_lane0 = execute_ctrl4_up_LsuL1_PHYSICAL_ADDRESS_lane0;
  assign execute_ctrl4_down_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_loaded = execute_ctrl4_up_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_loaded;
  assign execute_ctrl4_down_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_address = execute_ctrl4_up_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_address;
  assign execute_ctrl4_down_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_fault = execute_ctrl4_up_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_fault;
  assign execute_ctrl4_down_LsuL1Plugin_logic_WAYS_HITS_lane0 = execute_ctrl4_up_LsuL1Plugin_logic_WAYS_HITS_lane0;
  assign execute_ctrl4_down_early0_MulPlugin_logic_steps_0_adders_0_lane0 = execute_ctrl4_up_early0_MulPlugin_logic_steps_0_adders_0_lane0;
  assign execute_ctrl4_down_early0_MulPlugin_logic_steps_0_adders_1_lane0 = execute_ctrl4_up_early0_MulPlugin_logic_steps_0_adders_1_lane0;
  assign execute_ctrl4_down_late0_SrcPlugin_SRC1_lane0 = execute_ctrl4_up_late0_SrcPlugin_SRC1_lane0;
  assign execute_ctrl4_down_late0_SrcPlugin_SRC2_lane0 = execute_ctrl4_up_late0_SrcPlugin_SRC2_lane0;
  assign execute_ctrl4_down_LsuPlugin_logic_onTrigger_HIT_lane0 = execute_ctrl4_up_LsuPlugin_logic_onTrigger_HIT_lane0;
  assign execute_ctrl4_down_MMU_TRANSLATED_lane0 = execute_ctrl4_up_MMU_TRANSLATED_lane0;
  assign execute_ctrl4_down_LsuPlugin_logic_preCtrl_MISS_ALIGNED_lane0 = execute_ctrl4_up_LsuPlugin_logic_preCtrl_MISS_ALIGNED_lane0;
  assign execute_ctrl4_down_LsuPlugin_logic_onPma_CACHED_RSP_lane0_fault = execute_ctrl4_up_LsuPlugin_logic_onPma_CACHED_RSP_lane0_fault;
  assign execute_ctrl4_down_LsuPlugin_logic_onPma_CACHED_RSP_lane0_io = execute_ctrl4_up_LsuPlugin_logic_onPma_CACHED_RSP_lane0_io;
  assign execute_ctrl4_down_LsuPlugin_logic_onPma_IO_RSP_lane0_fault = execute_ctrl4_up_LsuPlugin_logic_onPma_IO_RSP_lane0_fault;
  assign execute_ctrl4_down_LsuPlugin_logic_onPma_IO_RSP_lane0_io = execute_ctrl4_up_LsuPlugin_logic_onPma_IO_RSP_lane0_io;
  assign execute_ctrl4_down_LsuPlugin_logic_onPma_IO_lane0 = execute_ctrl4_up_LsuPlugin_logic_onPma_IO_lane0;
  assign execute_ctrl4_down_LsuPlugin_logic_onPma_FROM_LSU_MSB_FAILED_lane0 = execute_ctrl4_up_LsuPlugin_logic_onPma_FROM_LSU_MSB_FAILED_lane0;
  assign execute_ctrl4_down_LsuPlugin_logic_MMU_PAGE_FAULT_lane0 = execute_ctrl4_up_LsuPlugin_logic_MMU_PAGE_FAULT_lane0;
  assign execute_ctrl4_down_LsuPlugin_logic_MMU_FAILURE_lane0 = execute_ctrl4_up_LsuPlugin_logic_MMU_FAILURE_lane0;
  assign execute_ctrl4_down_MMU_ACCESS_FAULT_lane0 = execute_ctrl4_up_MMU_ACCESS_FAULT_lane0;
  assign execute_ctrl4_down_MMU_REFILL_lane0 = execute_ctrl4_up_MMU_REFILL_lane0;
  assign execute_ctrl4_down_MMU_HAZARD_lane0 = execute_ctrl4_up_MMU_HAZARD_lane0;
  assign execute_ctrl4_down_MMU_BYPASS_TRANSLATION_lane0 = execute_ctrl4_up_MMU_BYPASS_TRANSLATION_lane0;
  assign execute_ctrl5_up_ready = execute_ctrl5_down_isReady;
  assign execute_ctrl5_down_LANE_SEL_lane0 = execute_ctrl5_up_LANE_SEL_lane0;
  assign execute_ctrl5_down_RD_PHYS_lane0 = execute_ctrl5_up_RD_PHYS_lane0;
  assign execute_ctrl5_down_COMMIT_lane0 = execute_ctrl5_up_COMMIT_lane0;
  assign execute_ctrl5_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0 = execute_ctrl5_up_lane0_integer_WriteBackPlugin_logic_DATA_lane0;
  assign fetch_logic_ctrls_0_down_isFiring = (fetch_logic_ctrls_0_down_isValid && fetch_logic_ctrls_0_down_isReady);
  assign fetch_logic_ctrls_0_down_isValid = fetch_logic_ctrls_0_down_valid;
  assign fetch_logic_ctrls_0_down_isReady = fetch_logic_ctrls_0_down_ready;
  assign fetch_logic_ctrls_1_up_isValid = fetch_logic_ctrls_1_up_valid;
  assign fetch_logic_ctrls_1_down_isValid = fetch_logic_ctrls_1_down_valid;
  assign fetch_logic_ctrls_1_down_isReady = fetch_logic_ctrls_1_down_ready;
  assign fetch_logic_ctrls_2_up_isValid = fetch_logic_ctrls_2_up_valid;
  assign fetch_logic_ctrls_2_up_isReady = fetch_logic_ctrls_2_up_ready;
  assign fetch_logic_ctrls_2_up_isCancel = fetch_logic_ctrls_2_up_cancel;
  assign fetch_logic_ctrls_2_up_isCanceling = (fetch_logic_ctrls_2_up_isValid && fetch_logic_ctrls_2_up_isCancel);
  assign fetch_logic_ctrls_0_up_isFiring = (fetch_logic_ctrls_0_up_isValid && fetch_logic_ctrls_0_up_isReady);
  assign fetch_logic_ctrls_0_up_isValid = fetch_logic_ctrls_0_up_valid;
  assign fetch_logic_ctrls_0_up_isReady = fetch_logic_ctrls_0_up_ready;
  assign fetch_logic_ctrls_2_down_isValid = fetch_logic_ctrls_2_down_valid;
  assign fetch_logic_ctrls_2_down_isReady = fetch_logic_ctrls_2_down_ready;
  assign decode_ctrls_0_down_isValid = decode_ctrls_0_down_valid;
  assign decode_ctrls_0_down_isReady = decode_ctrls_0_down_ready;
  assign decode_ctrls_1_up_isMoving = (decode_ctrls_1_up_isValid && decode_ctrls_1_up_isReady);
  assign decode_ctrls_1_up_isValid = decode_ctrls_1_up_valid;
  assign decode_ctrls_1_up_isReady = decode_ctrls_1_up_ready;
  assign decode_ctrls_1_up_isCanceling = 1'b0;
  assign decode_ctrls_0_up_isFiring = (decode_ctrls_0_up_isValid && decode_ctrls_0_up_isReady);
  assign decode_ctrls_0_up_isMoving = (decode_ctrls_0_up_isValid && decode_ctrls_0_up_isReady);
  assign decode_ctrls_0_up_isValid = decode_ctrls_0_up_valid;
  assign decode_ctrls_0_up_isReady = decode_ctrls_0_up_ready;
  assign decode_ctrls_1_down_isReady = decode_ctrls_1_down_ready;
  assign execute_ctrl0_down_isReady = execute_ctrl0_down_ready;
  assign execute_ctrl1_down_isReady = execute_ctrl1_down_ready;
  assign execute_ctrl2_down_isReady = execute_ctrl2_down_ready;
  assign execute_ctrl3_down_isReady = execute_ctrl3_down_ready;
  assign execute_ctrl4_down_isReady = execute_ctrl4_down_ready;
  assign execute_ctrl5_down_isReady = execute_ctrl5_down_ready;
  always @(*) begin
    LsuPlugin_logic_flusher_stateNext = LsuPlugin_logic_flusher_stateReg;
    case(LsuPlugin_logic_flusher_stateReg)
      LsuPlugin_logic_flusher_CMD : begin
        if(when_LsuPlugin_l363) begin
          LsuPlugin_logic_flusher_stateNext = LsuPlugin_logic_flusher_COMPLETION;
        end
      end
      LsuPlugin_logic_flusher_COMPLETION : begin
        if(when_LsuPlugin_l371) begin
          LsuPlugin_logic_flusher_stateNext = LsuPlugin_logic_flusher_IDLE;
        end
      end
      default : begin
        if(LsuPlugin_logic_flusher_arbiter_io_output_valid) begin
          LsuPlugin_logic_flusher_stateNext = LsuPlugin_logic_flusher_CMD;
        end
      end
    endcase
    if(LsuPlugin_logic_flusher_wantKill) begin
      LsuPlugin_logic_flusher_stateNext = LsuPlugin_logic_flusher_IDLE;
    end
  end

  assign when_LsuPlugin_l363 = (LsuPlugin_logic_flusher_cmdCounter[4] && (! LsuPlugin_logic_flusher_inflight));
  assign when_LsuPlugin_l371 = (! (|LsuPlugin_logic_flusher_waiter));
  assign LsuPlugin_logic_flusher_onExit_IDLE = ((LsuPlugin_logic_flusher_stateNext != LsuPlugin_logic_flusher_IDLE) && (LsuPlugin_logic_flusher_stateReg == LsuPlugin_logic_flusher_IDLE));
  assign LsuPlugin_logic_flusher_onExit_CMD = ((LsuPlugin_logic_flusher_stateNext != LsuPlugin_logic_flusher_CMD) && (LsuPlugin_logic_flusher_stateReg == LsuPlugin_logic_flusher_CMD));
  assign LsuPlugin_logic_flusher_onExit_COMPLETION = ((LsuPlugin_logic_flusher_stateNext != LsuPlugin_logic_flusher_COMPLETION) && (LsuPlugin_logic_flusher_stateReg == LsuPlugin_logic_flusher_COMPLETION));
  assign LsuPlugin_logic_flusher_onEntry_IDLE = ((LsuPlugin_logic_flusher_stateNext == LsuPlugin_logic_flusher_IDLE) && (LsuPlugin_logic_flusher_stateReg != LsuPlugin_logic_flusher_IDLE));
  assign LsuPlugin_logic_flusher_onEntry_CMD = ((LsuPlugin_logic_flusher_stateNext == LsuPlugin_logic_flusher_CMD) && (LsuPlugin_logic_flusher_stateReg != LsuPlugin_logic_flusher_CMD));
  assign LsuPlugin_logic_flusher_onEntry_COMPLETION = ((LsuPlugin_logic_flusher_stateNext == LsuPlugin_logic_flusher_COMPLETION) && (LsuPlugin_logic_flusher_stateReg != LsuPlugin_logic_flusher_COMPLETION));
  always @(*) begin
    TrapPlugin_logic_harts_0_trap_fsm_stateNext = TrapPlugin_logic_harts_0_trap_fsm_stateReg;
    case(TrapPlugin_logic_harts_0_trap_fsm_stateReg)
      TrapPlugin_logic_harts_0_trap_fsm_RUNNING : begin
        if(TrapPlugin_logic_harts_0_trap_trigger_valid) begin
          TrapPlugin_logic_harts_0_trap_fsm_stateNext = TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1;
        end
      end
      TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1 : begin
        if(when_TrapPlugin_l409) begin
          TrapPlugin_logic_harts_0_trap_fsm_stateNext = TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL;
        end else begin
          case(TrapPlugin_logic_harts_0_trap_pending_state_code)
            4'b0000 : begin
              TrapPlugin_logic_harts_0_trap_fsm_stateNext = TrapPlugin_logic_harts_0_trap_fsm_RUNNING;
            end
            4'b0001 : begin
              TrapPlugin_logic_harts_0_trap_fsm_stateNext = TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC;
            end
            4'b0010 : begin
              TrapPlugin_logic_harts_0_trap_fsm_stateNext = TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH;
            end
            4'b0100 : begin
              TrapPlugin_logic_harts_0_trap_fsm_stateNext = TrapPlugin_logic_harts_0_trap_fsm_JUMP;
            end
            4'b0101 : begin
              TrapPlugin_logic_harts_0_trap_fsm_stateNext = TrapPlugin_logic_harts_0_trap_fsm_JUMP;
            end
            4'b1000 : begin
              if(TrapPlugin_api_harts_0_askWake) begin
                TrapPlugin_logic_harts_0_trap_fsm_stateNext = TrapPlugin_logic_harts_0_trap_fsm_JUMP;
              end
            end
            4'b0110 : begin
              TrapPlugin_logic_harts_0_trap_fsm_stateNext = TrapPlugin_logic_harts_0_trap_fsm_JUMP;
            end
            default : begin
            end
          endcase
        end
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC : begin
        if(TrapPlugin_logic_harts_0_crsPorts_write_ready) begin
          TrapPlugin_logic_harts_0_trap_fsm_stateNext = TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC;
        end
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL : begin
        if(TrapPlugin_logic_harts_0_crsPorts_write_ready) begin
          TrapPlugin_logic_harts_0_trap_fsm_stateNext = TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC;
        end
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC : begin
        if(TrapPlugin_logic_harts_0_crsPorts_read_ready) begin
          TrapPlugin_logic_harts_0_trap_fsm_stateNext = TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY;
        end
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY : begin
        TrapPlugin_logic_harts_0_trap_fsm_stateNext = TrapPlugin_logic_harts_0_trap_fsm_RUNNING;
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC : begin
        if(TrapPlugin_logic_harts_0_crsPorts_read_ready) begin
          TrapPlugin_logic_harts_0_trap_fsm_stateNext = TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY;
        end
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY : begin
        TrapPlugin_logic_harts_0_trap_fsm_stateNext = TrapPlugin_logic_harts_0_trap_fsm_RUNNING;
      end
      TrapPlugin_logic_harts_0_trap_fsm_JUMP : begin
        TrapPlugin_logic_harts_0_trap_fsm_stateNext = TrapPlugin_logic_harts_0_trap_fsm_RUNNING;
      end
      TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH : begin
        if(TrapPlugin_logic_lsuL1Invalidate_0_cmd_ready) begin
          TrapPlugin_logic_harts_0_trap_fsm_stateNext = TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH;
        end
      end
      TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH : begin
        if(TrapPlugin_logic_fetchL1Invalidate_0_cmd_ready) begin
          TrapPlugin_logic_harts_0_trap_fsm_stateNext = TrapPlugin_logic_harts_0_trap_fsm_JUMP;
        end
      end
      default : begin
        if(when_TrapPlugin_l362) begin
          TrapPlugin_logic_harts_0_trap_fsm_stateNext = TrapPlugin_logic_harts_0_trap_fsm_RUNNING;
        end
      end
    endcase
    if(TrapPlugin_logic_harts_0_trap_fsm_wantKill) begin
      TrapPlugin_logic_harts_0_trap_fsm_stateNext = TrapPlugin_logic_harts_0_trap_fsm_RESET;
    end
  end

  assign when_TrapPlugin_l409 = ((TrapPlugin_logic_harts_0_trap_pending_state_exception || TrapPlugin_logic_harts_0_trap_fsm_triggerEbreak) || TrapPlugin_logic_harts_0_trap_fsm_buffer_trap_interrupt);
  assign when_TrapPlugin_l654 = (TrapPlugin_logic_harts_0_trap_pending_xret_targetPrivilege != 2'b11);
  assign switch_TrapPlugin_l655 = TrapPlugin_logic_harts_0_trap_pending_state_arg[1 : 0];
  assign when_TrapPlugin_l362 = (&TrapPlugin_logic_harts_0_trap_fsm_resetToRunConditions_0);
  assign TrapPlugin_logic_harts_0_trap_fsm_onExit_RESET = ((TrapPlugin_logic_harts_0_trap_fsm_stateNext != TrapPlugin_logic_harts_0_trap_fsm_RESET) && (TrapPlugin_logic_harts_0_trap_fsm_stateReg == TrapPlugin_logic_harts_0_trap_fsm_RESET));
  assign TrapPlugin_logic_harts_0_trap_fsm_onExit_RUNNING = ((TrapPlugin_logic_harts_0_trap_fsm_stateNext != TrapPlugin_logic_harts_0_trap_fsm_RUNNING) && (TrapPlugin_logic_harts_0_trap_fsm_stateReg == TrapPlugin_logic_harts_0_trap_fsm_RUNNING));
  assign TrapPlugin_logic_harts_0_trap_fsm_onExit_PROCESS_1 = ((TrapPlugin_logic_harts_0_trap_fsm_stateNext != TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1) && (TrapPlugin_logic_harts_0_trap_fsm_stateReg == TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1));
  assign TrapPlugin_logic_harts_0_trap_fsm_onExit_TRAP_EPC = ((TrapPlugin_logic_harts_0_trap_fsm_stateNext != TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC) && (TrapPlugin_logic_harts_0_trap_fsm_stateReg == TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC));
  assign TrapPlugin_logic_harts_0_trap_fsm_onExit_TRAP_TVAL = ((TrapPlugin_logic_harts_0_trap_fsm_stateNext != TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL) && (TrapPlugin_logic_harts_0_trap_fsm_stateReg == TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL));
  assign TrapPlugin_logic_harts_0_trap_fsm_onExit_TRAP_TVEC = ((TrapPlugin_logic_harts_0_trap_fsm_stateNext != TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC) && (TrapPlugin_logic_harts_0_trap_fsm_stateReg == TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC));
  assign TrapPlugin_logic_harts_0_trap_fsm_onExit_TRAP_APPLY = ((TrapPlugin_logic_harts_0_trap_fsm_stateNext != TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY) && (TrapPlugin_logic_harts_0_trap_fsm_stateReg == TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY));
  assign TrapPlugin_logic_harts_0_trap_fsm_onExit_XRET_EPC = ((TrapPlugin_logic_harts_0_trap_fsm_stateNext != TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC) && (TrapPlugin_logic_harts_0_trap_fsm_stateReg == TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC));
  assign TrapPlugin_logic_harts_0_trap_fsm_onExit_XRET_APPLY = ((TrapPlugin_logic_harts_0_trap_fsm_stateNext != TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY) && (TrapPlugin_logic_harts_0_trap_fsm_stateReg == TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY));
  assign TrapPlugin_logic_harts_0_trap_fsm_onExit_JUMP = ((TrapPlugin_logic_harts_0_trap_fsm_stateNext != TrapPlugin_logic_harts_0_trap_fsm_JUMP) && (TrapPlugin_logic_harts_0_trap_fsm_stateReg == TrapPlugin_logic_harts_0_trap_fsm_JUMP));
  assign TrapPlugin_logic_harts_0_trap_fsm_onExit_LSU_FLUSH = ((TrapPlugin_logic_harts_0_trap_fsm_stateNext != TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH) && (TrapPlugin_logic_harts_0_trap_fsm_stateReg == TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH));
  assign TrapPlugin_logic_harts_0_trap_fsm_onExit_FETCH_FLUSH = ((TrapPlugin_logic_harts_0_trap_fsm_stateNext != TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH) && (TrapPlugin_logic_harts_0_trap_fsm_stateReg == TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH));
  assign TrapPlugin_logic_harts_0_trap_fsm_onEntry_RESET = ((TrapPlugin_logic_harts_0_trap_fsm_stateNext == TrapPlugin_logic_harts_0_trap_fsm_RESET) && (TrapPlugin_logic_harts_0_trap_fsm_stateReg != TrapPlugin_logic_harts_0_trap_fsm_RESET));
  assign TrapPlugin_logic_harts_0_trap_fsm_onEntry_RUNNING = ((TrapPlugin_logic_harts_0_trap_fsm_stateNext == TrapPlugin_logic_harts_0_trap_fsm_RUNNING) && (TrapPlugin_logic_harts_0_trap_fsm_stateReg != TrapPlugin_logic_harts_0_trap_fsm_RUNNING));
  assign TrapPlugin_logic_harts_0_trap_fsm_onEntry_PROCESS_1 = ((TrapPlugin_logic_harts_0_trap_fsm_stateNext == TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1) && (TrapPlugin_logic_harts_0_trap_fsm_stateReg != TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1));
  assign TrapPlugin_logic_harts_0_trap_fsm_onEntry_TRAP_EPC = ((TrapPlugin_logic_harts_0_trap_fsm_stateNext == TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC) && (TrapPlugin_logic_harts_0_trap_fsm_stateReg != TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC));
  assign TrapPlugin_logic_harts_0_trap_fsm_onEntry_TRAP_TVAL = ((TrapPlugin_logic_harts_0_trap_fsm_stateNext == TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL) && (TrapPlugin_logic_harts_0_trap_fsm_stateReg != TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL));
  assign TrapPlugin_logic_harts_0_trap_fsm_onEntry_TRAP_TVEC = ((TrapPlugin_logic_harts_0_trap_fsm_stateNext == TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC) && (TrapPlugin_logic_harts_0_trap_fsm_stateReg != TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC));
  assign TrapPlugin_logic_harts_0_trap_fsm_onEntry_TRAP_APPLY = ((TrapPlugin_logic_harts_0_trap_fsm_stateNext == TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY) && (TrapPlugin_logic_harts_0_trap_fsm_stateReg != TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY));
  assign TrapPlugin_logic_harts_0_trap_fsm_onEntry_XRET_EPC = ((TrapPlugin_logic_harts_0_trap_fsm_stateNext == TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC) && (TrapPlugin_logic_harts_0_trap_fsm_stateReg != TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC));
  assign TrapPlugin_logic_harts_0_trap_fsm_onEntry_XRET_APPLY = ((TrapPlugin_logic_harts_0_trap_fsm_stateNext == TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY) && (TrapPlugin_logic_harts_0_trap_fsm_stateReg != TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY));
  assign TrapPlugin_logic_harts_0_trap_fsm_onEntry_JUMP = ((TrapPlugin_logic_harts_0_trap_fsm_stateNext == TrapPlugin_logic_harts_0_trap_fsm_JUMP) && (TrapPlugin_logic_harts_0_trap_fsm_stateReg != TrapPlugin_logic_harts_0_trap_fsm_JUMP));
  assign TrapPlugin_logic_harts_0_trap_fsm_onEntry_LSU_FLUSH = ((TrapPlugin_logic_harts_0_trap_fsm_stateNext == TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH) && (TrapPlugin_logic_harts_0_trap_fsm_stateReg != TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH));
  assign TrapPlugin_logic_harts_0_trap_fsm_onEntry_FETCH_FLUSH = ((TrapPlugin_logic_harts_0_trap_fsm_stateNext == TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH) && (TrapPlugin_logic_harts_0_trap_fsm_stateReg != TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH));
  always @(*) begin
    CsrAccessPlugin_logic_fsm_stateNext = CsrAccessPlugin_logic_fsm_stateReg;
    case(CsrAccessPlugin_logic_fsm_stateReg)
      CsrAccessPlugin_logic_fsm_READ : begin
        if(when_CsrAccessPlugin_l296) begin
          CsrAccessPlugin_logic_fsm_stateNext = CsrAccessPlugin_logic_fsm_WRITE;
        end
      end
      CsrAccessPlugin_logic_fsm_WRITE : begin
        if(when_CsrAccessPlugin_l325) begin
          CsrAccessPlugin_logic_fsm_stateNext = CsrAccessPlugin_logic_fsm_COMPLETION;
        end
      end
      CsrAccessPlugin_logic_fsm_COMPLETION : begin
        if(execute_ctrl2_down_isReady) begin
          CsrAccessPlugin_logic_fsm_stateNext = CsrAccessPlugin_logic_fsm_IDLE;
        end
      end
      default : begin
        if(CsrAccessPlugin_logic_fsm_inject_onDecodeDo) begin
          if(when_CsrAccessPlugin_l212) begin
            CsrAccessPlugin_logic_fsm_stateNext = CsrAccessPlugin_logic_fsm_READ;
          end
          if(CsrAccessPlugin_logic_fsm_inject_sampled) begin
            if(!CsrAccessPlugin_logic_fsm_inject_trapReg) begin
              CsrAccessPlugin_logic_fsm_stateNext = CsrAccessPlugin_logic_fsm_READ;
            end
          end
        end
      end
    endcase
    if(CsrAccessPlugin_logic_fsm_wantKill) begin
      CsrAccessPlugin_logic_fsm_stateNext = CsrAccessPlugin_logic_fsm_IDLE;
    end
  end

  assign when_CsrAccessPlugin_l296 = (! CsrAccessPlugin_bus_read_halt);
  assign when_CsrAccessPlugin_l325 = (! CsrAccessPlugin_bus_write_halt);
  assign when_CsrAccessPlugin_l212 = ((! CsrAccessPlugin_logic_fsm_inject_trap) && (! CsrAccessPlugin_bus_decode_trap));
  assign CsrAccessPlugin_logic_fsm_onExit_IDLE = ((CsrAccessPlugin_logic_fsm_stateNext != CsrAccessPlugin_logic_fsm_IDLE) && (CsrAccessPlugin_logic_fsm_stateReg == CsrAccessPlugin_logic_fsm_IDLE));
  assign CsrAccessPlugin_logic_fsm_onExit_READ = ((CsrAccessPlugin_logic_fsm_stateNext != CsrAccessPlugin_logic_fsm_READ) && (CsrAccessPlugin_logic_fsm_stateReg == CsrAccessPlugin_logic_fsm_READ));
  assign CsrAccessPlugin_logic_fsm_onExit_WRITE = ((CsrAccessPlugin_logic_fsm_stateNext != CsrAccessPlugin_logic_fsm_WRITE) && (CsrAccessPlugin_logic_fsm_stateReg == CsrAccessPlugin_logic_fsm_WRITE));
  assign CsrAccessPlugin_logic_fsm_onExit_COMPLETION = ((CsrAccessPlugin_logic_fsm_stateNext != CsrAccessPlugin_logic_fsm_COMPLETION) && (CsrAccessPlugin_logic_fsm_stateReg == CsrAccessPlugin_logic_fsm_COMPLETION));
  assign CsrAccessPlugin_logic_fsm_onEntry_IDLE = ((CsrAccessPlugin_logic_fsm_stateNext == CsrAccessPlugin_logic_fsm_IDLE) && (CsrAccessPlugin_logic_fsm_stateReg != CsrAccessPlugin_logic_fsm_IDLE));
  assign CsrAccessPlugin_logic_fsm_onEntry_READ = ((CsrAccessPlugin_logic_fsm_stateNext == CsrAccessPlugin_logic_fsm_READ) && (CsrAccessPlugin_logic_fsm_stateReg != CsrAccessPlugin_logic_fsm_READ));
  assign CsrAccessPlugin_logic_fsm_onEntry_WRITE = ((CsrAccessPlugin_logic_fsm_stateNext == CsrAccessPlugin_logic_fsm_WRITE) && (CsrAccessPlugin_logic_fsm_stateReg != CsrAccessPlugin_logic_fsm_WRITE));
  assign CsrAccessPlugin_logic_fsm_onEntry_COMPLETION = ((CsrAccessPlugin_logic_fsm_stateNext == CsrAccessPlugin_logic_fsm_COMPLETION) && (CsrAccessPlugin_logic_fsm_stateReg != CsrAccessPlugin_logic_fsm_COMPLETION));
  always @(posedge clk or posedge reset) begin
    if(reset) begin
      LsuL1Plugin_logic_refill_slots_0_valid <= 1'b0;
      LsuL1Plugin_logic_refill_slots_0_loaded <= 1'b1;
      LsuL1Plugin_logic_refill_pushCounter <= 32'h0;
      LsuL1Plugin_logic_refill_read_arbiter_lock <= 1'b0;
      LsuL1Plugin_logic_refill_read_wordIndex <= 4'b0000;
      LsuL1Plugin_logic_refill_read_hadError <= 1'b0;
      LsuL1Plugin_logic_writeback_slots_0_valid <= 1'b0;
      LsuL1Plugin_logic_writeback_slots_0_busy <= 1'b0;
      LsuL1Plugin_logic_writeback_read_arbiter_lock <= 1'b0;
      LsuL1Plugin_logic_writeback_read_wordIndex <= 4'b0000;
      LsuL1Plugin_logic_writeback_read_slotReadLast_valid <= 1'b0;
      LsuL1Plugin_logic_writeback_write_arbiter_lock <= 1'b0;
      LsuL1Plugin_logic_writeback_write_wordIndex <= 4'b0000;
      LsuL1Plugin_logic_writeback_write_bufferRead_rValid <= 1'b0;
      LsuL1Plugin_logic_lsu_rb1_onBanks_0_busyReg <= 1'b0;
      LsuL1Plugin_logic_lsu_ctrl_hazardReg <= 1'b0;
      LsuL1Plugin_logic_lsu_ctrl_flushHazardReg <= 1'b0;
      LsuL1Plugin_logic_initializer_counter <= 5'h0;
      early0_DivPlugin_logic_processing_cmdSent <= 1'b0;
      early0_DivPlugin_logic_processing_unscheduleRequest <= 1'b0;
      PrivilegedPlugin_logic_harts_0_privilege <= 2'b11;
      PrivilegedPlugin_logic_harts_0_m_status_mie <= 1'b0;
      PrivilegedPlugin_logic_harts_0_m_status_mpie <= 1'b0;
      PrivilegedPlugin_logic_harts_0_m_status_mprv <= 1'b0;
      PrivilegedPlugin_logic_harts_0_m_cause_interrupt <= 1'b0;
      PrivilegedPlugin_logic_harts_0_m_cause_code <= 4'b0000;
      PrivilegedPlugin_logic_harts_0_m_ip_meip <= 1'b0;
      PrivilegedPlugin_logic_harts_0_m_ip_mtip <= 1'b0;
      PrivilegedPlugin_logic_harts_0_m_ip_msip <= 1'b0;
      PrivilegedPlugin_logic_harts_0_m_ie_meie <= 1'b0;
      PrivilegedPlugin_logic_harts_0_m_ie_mtie <= 1'b0;
      PrivilegedPlugin_logic_harts_0_m_ie_msie <= 1'b0;
      LsuL1Plugin_logic_bus_toWishbone_arbiter_counter <= 4'b0000;
      LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_rValid <= 1'b0;
      FetchL1Plugin_logic_invalidate_counter <= 5'h0;
      FetchL1Plugin_logic_invalidate_firstEver <= 1'b1;
      FetchL1Plugin_logic_refill_slots_0_valid <= 1'b0;
      FetchL1Plugin_logic_refill_slots_0_cmdSent <= 1'b1;
      FetchL1Plugin_logic_refill_pushCounter <= 32'h0;
      FetchL1Plugin_logic_refill_onCmd_locked <= 1'b0;
      FetchL1Plugin_logic_refill_onRsp_wordIndex <= 4'b0000;
      FetchL1Plugin_logic_refill_onRsp_firstCycle <= 1'b1;
      FetchL1Plugin_logic_ctrl_plruLogic_buffer_regNext_valid <= 1'b0;
      FetchL1Plugin_logic_ctrl_trapSent <= 1'b0;
      FetchL1Plugin_logic_ctrl_firstCycle <= 1'b1;
      decode_ctrls_0_up_LANE_SEL_0_regNext <= 1'b0;
      FetchL1Plugin_logic_bus_toWishbone_counter <= 4'b0000;
      _zz_FetchL1Plugin_logic_bus_rsp_valid <= 1'b0;
      AlignerPlugin_logic_feeder_harts_0_dopId <= 10'h0;
      AlignerPlugin_logic_nobuffer_mask <= 1'b1;
      LsuPlugin_logic_onAddress0_ls_storeId <= 12'h0;
      execute_ctrl3_up_LsuL1_SEL_lane0 <= 1'b0;
      execute_ctrl4_up_LsuL1_SEL_lane0 <= 1'b0;
      LsuPlugin_logic_onCtrl_io_tooEarly <= 1'b0;
      LsuPlugin_logic_onCtrl_io_allowIt <= 1'b0;
      LsuPlugin_logic_onCtrl_io_doItReg <= 1'b0;
      LsuPlugin_logic_onCtrl_io_cmdSent <= 1'b0;
      LsuPlugin_logic_bus_rsp_toStream_rValid <= 1'b0;
      LsuPlugin_logic_onCtrl_hartRegulation_valid <= 1'b0;
      LsuPlugin_logic_bus_cmd_rValid <= 1'b0;
      DecoderPlugin_logic_harts_0_uopId <= 16'h0;
      DecoderPlugin_logic_interrupt_buffered <= 1'b0;
      decode_ctrls_1_up_LANE_SEL_0_regNext <= 1'b0;
      DispatchPlugin_logic_feeds_0_sent <= 1'b0;
      CsrRamPlugin_csrMapper_fired <= 1'b0;
      decode_ctrls_1_up_LANE_SEL_0_regNext_1 <= 1'b0;
      execute_ctrl0_down_LANE_SEL_lane0_regNext <= 1'b0;
      execute_ctrl2_down_LANE_SEL_lane0_regNext <= 1'b0;
      BtbPlugin_logic_applyIt_correctionSent <= 1'b0;
      decode_ctrls_1_up_LANE_SEL_0 <= 1'b0;
      TrapPlugin_logic_harts_0_interrupt_validBuffer <= 1'b0;
      TrapPlugin_logic_harts_0_trap_fsm_trapEnterDebug <= 1'b0;
      PcPlugin_logic_harts_0_self_id <= 10'h0;
      PcPlugin_logic_harts_0_self_increment <= 1'b0;
      PcPlugin_logic_harts_0_self_fault <= 1'b0;
      PcPlugin_logic_harts_0_self_state <= 32'h20200000;
      PcPlugin_logic_harts_0_holdReg <= 1'b1;
      CsrAccessPlugin_logic_fsm_inject_unfreeze <= 1'b0;
      CsrAccessPlugin_logic_fsm_inject_flushReg <= 1'b0;
      CsrAccessPlugin_logic_fsm_inject_sampled <= 1'b0;
      CsrRamPlugin_logic_readLogic_ohReg <= 2'b00;
      CsrRamPlugin_logic_readLogic_busy <= 1'b0;
      CsrRamPlugin_logic_flush_counter <= 3'b000;
      execute_ctrl1_up_LANE_SEL_lane0 <= 1'b0;
      execute_ctrl2_up_LANE_SEL_lane0 <= 1'b0;
      execute_ctrl3_up_LANE_SEL_lane0 <= 1'b0;
      execute_ctrl4_up_LANE_SEL_lane0 <= 1'b0;
      execute_ctrl5_up_LANE_SEL_lane0 <= 1'b0;
      integer_RegFilePlugin_logic_initalizer_counter <= 6'h0;
      _zz_WhiteboxerPlugin_logic_perf_executeFreezedCounter_2 <= 60'h0;
      _zz_WhiteboxerPlugin_logic_perf_dispatchHazardsCounter_2 <= 60'h0;
      _zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_0_2 <= 60'h0;
      _zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_1_2 <= 60'h0;
      _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_0_2 <= 60'h0;
      _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_1_2 <= 60'h0;
      fetch_logic_ctrls_1_up_valid <= 1'b0;
      fetch_logic_ctrls_2_up_valid <= 1'b0;
      decode_ctrls_1_up_valid <= 1'b0;
      LsuPlugin_logic_flusher_stateReg <= LsuPlugin_logic_flusher_IDLE;
      TrapPlugin_logic_harts_0_trap_fsm_stateReg <= TrapPlugin_logic_harts_0_trap_fsm_RESET;
      CsrAccessPlugin_logic_fsm_stateReg <= CsrAccessPlugin_logic_fsm_IDLE;
    end else begin
      if(LsuL1Plugin_logic_refill_slots_0_loadedSet) begin
        LsuL1Plugin_logic_refill_slots_0_loaded <= 1'b1;
      end
      if(LsuL1Plugin_logic_refill_slots_0_fire) begin
        LsuL1Plugin_logic_refill_slots_0_valid <= 1'b0;
      end
      if(LsuL1Plugin_logic_refill_push_valid) begin
        LsuL1Plugin_logic_refill_pushCounter <= (LsuL1Plugin_logic_refill_pushCounter + 32'h00000001);
      end
      if(when_LsuL1Plugin_l377) begin
        LsuL1Plugin_logic_refill_slots_0_valid <= 1'b1;
        LsuL1Plugin_logic_refill_slots_0_loaded <= 1'b0;
      end
      LsuL1Plugin_logic_refill_read_arbiter_lock <= LsuL1Plugin_logic_refill_read_arbiter_oh;
      if(LsuL1Plugin_logic_bus_read_cmd_fire) begin
        LsuL1Plugin_logic_refill_read_arbiter_lock <= 1'b0;
      end
      if(LsuL1Plugin_logic_bus_read_rsp_valid) begin
        `ifndef SYNTHESIS
          `ifdef FORMAL
            assert(LsuL1Plugin_logic_refill_read_writeReservation_win); // LsuL1Plugin.scala:L429
          `else
            if(!LsuL1Plugin_logic_refill_read_writeReservation_win) begin
              $display("FAILURE "); // LsuL1Plugin.scala:L429
              $finish;
            end
          `endif
        `endif
      end
      if(when_LsuL1Plugin_l450) begin
        LsuL1Plugin_logic_refill_read_hadError <= 1'b1;
      end
      if(LsuL1Plugin_logic_bus_read_rsp_valid) begin
        `ifndef SYNTHESIS
          `ifdef FORMAL
            assert(LsuL1Plugin_logic_refill_read_reservation_win); // LsuL1Plugin.scala:L459
          `else
            if(!LsuL1Plugin_logic_refill_read_reservation_win) begin
              $display("FAILURE "); // LsuL1Plugin.scala:L459
              $finish;
            end
          `endif
        `endif
        if(LsuL1Plugin_logic_refill_read_rspWithData) begin
          LsuL1Plugin_logic_refill_read_wordIndex <= (LsuL1Plugin_logic_refill_read_wordIndex + 4'b0001);
        end
        if(when_LsuL1Plugin_l463) begin
          LsuL1Plugin_logic_refill_read_hadError <= 1'b0;
        end
      end
      if(LsuL1Plugin_logic_writeback_slots_0_fire) begin
        LsuL1Plugin_logic_writeback_slots_0_valid <= 1'b0;
      end
      if(LsuL1Plugin_logic_writeback_slots_0_fire) begin
        LsuL1Plugin_logic_writeback_slots_0_busy <= 1'b0;
      end
      if(when_LsuL1Plugin_l530) begin
        LsuL1Plugin_logic_writeback_slots_0_valid <= 1'b0;
      end
      if(when_LsuL1Plugin_l556) begin
        LsuL1Plugin_logic_writeback_slots_0_valid <= 1'b1;
        LsuL1Plugin_logic_writeback_slots_0_busy <= 1'b1;
      end
      LsuL1Plugin_logic_writeback_read_arbiter_lock <= LsuL1Plugin_logic_writeback_read_arbiter_oh;
      LsuL1Plugin_logic_writeback_read_wordIndex <= (LsuL1Plugin_logic_writeback_read_wordIndex + _zz_LsuL1Plugin_logic_writeback_read_wordIndex);
      if(when_LsuL1Plugin_l605) begin
        LsuL1Plugin_logic_writeback_read_arbiter_lock <= 1'b0;
      end
      LsuL1Plugin_logic_writeback_read_slotReadLast_valid <= LsuL1Plugin_logic_writeback_read_slotRead_valid;
      LsuL1Plugin_logic_writeback_write_arbiter_lock <= LsuL1Plugin_logic_writeback_write_arbiter_oh;
      LsuL1Plugin_logic_writeback_write_wordIndex <= (LsuL1Plugin_logic_writeback_write_wordIndex + _zz_LsuL1Plugin_logic_writeback_write_wordIndex);
      if(when_LsuL1Plugin_l676) begin
        LsuL1Plugin_logic_writeback_write_arbiter_lock <= 1'b0;
      end
      if(LsuL1Plugin_logic_writeback_write_bufferRead_ready) begin
        LsuL1Plugin_logic_writeback_write_bufferRead_rValid <= LsuL1Plugin_logic_writeback_write_bufferRead_valid;
      end
      if(LsuL1Plugin_logic_banks_0_usedByWriteback) begin
        LsuL1Plugin_logic_lsu_rb1_onBanks_0_busyReg <= 1'b1;
      end
      if(when_LsuL1Plugin_l735) begin
        LsuL1Plugin_logic_lsu_rb1_onBanks_0_busyReg <= 1'b0;
      end
      LsuL1Plugin_logic_lsu_ctrl_hazardReg <= (execute_ctrl4_down_LsuL1_HAZARD_lane0 && execute_freeze_valid);
      LsuL1Plugin_logic_lsu_ctrl_flushHazardReg <= (execute_ctrl4_down_LsuL1_FLUSH_HAZARD_lane0 && execute_freeze_valid);
      if(execute_ctrl4_down_LsuL1_SEL_lane0) begin
        `ifndef SYNTHESIS
          `ifdef FORMAL
            assert((_zz_22 <= 1'b1)); // LsuL1Plugin.scala:L892
          `else
            if(!(_zz_22 <= 1'b1)) begin
              $display("FAILURE Multiple way hit ???"); // LsuL1Plugin.scala:L892
              $finish;
            end
          `endif
        `endif
      end
      if(when_LsuL1Plugin_l915) begin
        `ifndef SYNTHESIS
          `ifdef FORMAL
            assert((_zz_24 < 2'b10)); // LsuL1Plugin.scala:L916
          `else
            if(!(_zz_24 < 2'b10)) begin
              $display("FAILURE "); // LsuL1Plugin.scala:L916
              $finish;
            end
          `endif
        `endif
      end
      if(when_LsuL1Plugin_l1219) begin
        LsuL1Plugin_logic_initializer_counter <= (LsuL1Plugin_logic_initializer_counter + 5'h01);
      end
      if(io_cmd_fire) begin
        early0_DivPlugin_logic_processing_cmdSent <= 1'b1;
      end
      if(execute_ctrl2_down_isReady) begin
        early0_DivPlugin_logic_processing_cmdSent <= 1'b0;
      end
      early0_DivPlugin_logic_processing_unscheduleRequest <= execute_lane0_ctrls_2_upIsCancel;
      if(execute_ctrl2_down_isReady) begin
        early0_DivPlugin_logic_processing_unscheduleRequest <= 1'b0;
      end
      if(PrivilegedPlugin_logic_harts_0_xretAwayFromMachine) begin
        PrivilegedPlugin_logic_harts_0_m_status_mprv <= 1'b0;
      end
      PrivilegedPlugin_logic_harts_0_m_ip_meip <= PrivilegedPlugin_logic_harts_0_int_m_external;
      PrivilegedPlugin_logic_harts_0_m_ip_mtip <= PrivilegedPlugin_logic_harts_0_int_m_timer;
      PrivilegedPlugin_logic_harts_0_m_ip_msip <= PrivilegedPlugin_logic_harts_0_int_m_software;
      if(LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_fire) begin
        LsuL1Plugin_logic_bus_toWishbone_arbiter_counter <= (LsuL1Plugin_logic_bus_toWishbone_arbiter_counter + 4'b0001);
      end
      if(LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_ready) begin
        LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_rValid <= LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_valid;
      end
      if(FetchL1Plugin_logic_invalidate_done) begin
        FetchL1Plugin_logic_invalidate_firstEver <= 1'b0;
      end
      if(when_FetchL1Plugin_l204) begin
        FetchL1Plugin_logic_invalidate_counter <= FetchL1Plugin_logic_invalidate_counterIncr;
      end
      if(when_FetchL1Plugin_l211) begin
        FetchL1Plugin_logic_invalidate_counter <= 5'h0;
      end
      if(when_FetchL1Plugin_l255) begin
        if(_zz_when_1) begin
          FetchL1Plugin_logic_refill_slots_0_valid <= 1'b1;
          FetchL1Plugin_logic_refill_slots_0_cmdSent <= 1'b0;
        end
        FetchL1Plugin_logic_refill_pushCounter <= (FetchL1Plugin_logic_refill_pushCounter + 32'h00000001);
      end
      if(FetchL1Plugin_logic_bus_cmd_valid) begin
        FetchL1Plugin_logic_refill_onCmd_locked <= 1'b1;
      end
      if(FetchL1Plugin_logic_bus_cmd_ready) begin
        FetchL1Plugin_logic_refill_onCmd_locked <= 1'b0;
      end
      if(FetchL1Plugin_logic_bus_cmd_ready) begin
        if(FetchL1Plugin_logic_refill_onCmd_oh[0]) begin
          FetchL1Plugin_logic_refill_slots_0_cmdSent <= 1'b1;
        end
      end
      if(FetchL1Plugin_logic_bus_rsp_fire) begin
        FetchL1Plugin_logic_refill_onRsp_firstCycle <= 1'b0;
      end
      if(FetchL1Plugin_logic_bus_rsp_valid) begin
        FetchL1Plugin_logic_refill_onRsp_wordIndex <= (FetchL1Plugin_logic_refill_onRsp_wordIndex + 4'b0001);
        if(when_FetchL1Plugin_l330) begin
          FetchL1Plugin_logic_refill_onRsp_firstCycle <= 1'b1;
          FetchL1Plugin_logic_refill_slots_0_valid <= 1'b0;
        end
      end
      FetchL1Plugin_logic_ctrl_plruLogic_buffer_regNext_valid <= FetchL1Plugin_logic_ctrl_plruLogic_buffer_valid;
      if(FetchL1Plugin_logic_trapPort_valid) begin
        FetchL1Plugin_logic_ctrl_trapSent <= 1'b1;
      end
      if(fetch_logic_ctrls_2_up_isCancel) begin
        FetchL1Plugin_logic_ctrl_trapSent <= 1'b0;
      end
      if(fetch_logic_ctrls_2_up_isValid) begin
        FetchL1Plugin_logic_ctrl_firstCycle <= 1'b0;
      end
      if(when_FetchL1Plugin_l541) begin
        FetchL1Plugin_logic_ctrl_firstCycle <= 1'b1;
      end
      `ifndef SYNTHESIS
        `ifdef FORMAL
          assert((! ((|FetchL1Plugin_logic_refill_slots_0_valid) && (! FetchL1Plugin_logic_invalidate_done)))); // FetchL1Plugin.scala:L556
        `else
          if(!(! ((|FetchL1Plugin_logic_refill_slots_0_valid) && (! FetchL1Plugin_logic_invalidate_done)))) begin
            $display("FAILURE "); // FetchL1Plugin.scala:L556
            $finish;
          end
        `endif
      `endif
      decode_ctrls_0_up_LANE_SEL_0_regNext <= decode_ctrls_0_up_LANE_SEL_0;
      if(when_CtrlLaneApi_l50) begin
        decode_ctrls_0_up_LANE_SEL_0_regNext <= 1'b0;
      end
      if(when_FetchL1Bus_l247) begin
        if(when_FetchL1Bus_l250) begin
          FetchL1Plugin_logic_bus_toWishbone_counter <= (FetchL1Plugin_logic_bus_toWishbone_counter + 4'b0001);
        end
      end
      _zz_FetchL1Plugin_logic_bus_rsp_valid <= (FetchL1WishbonePlugin_logic_bus_CYC && (FetchL1WishbonePlugin_logic_bus_ACK || FetchL1WishbonePlugin_logic_bus_ERR));
      if(when_AlignerPlugin_l171) begin
        AlignerPlugin_logic_feeder_harts_0_dopId <= (decode_ctrls_0_down_Decode_DOP_ID_0 + 10'h001);
      end
      if(when_AlignerPlugin_l292) begin
        AlignerPlugin_logic_nobuffer_mask <= AlignerPlugin_logic_nobuffer_remaningMask;
      end
      LsuPlugin_logic_onAddress0_ls_storeId <= (LsuPlugin_logic_onAddress0_ls_storeId + _zz_LsuPlugin_logic_onAddress0_ls_storeId);
      LsuPlugin_logic_onCtrl_io_tooEarly <= 1'b1;
      if(execute_freeze_valid) begin
        LsuPlugin_logic_onCtrl_io_tooEarly <= 1'b0;
      end
      LsuPlugin_logic_onCtrl_io_allowIt <= 1'b0;
      if(when_LsuPlugin_l595) begin
        LsuPlugin_logic_onCtrl_io_allowIt <= 1'b1;
      end
      LsuPlugin_logic_onCtrl_io_doItReg <= LsuPlugin_logic_onCtrl_io_doIt;
      if(LsuPlugin_logic_bus_cmd_fire) begin
        LsuPlugin_logic_onCtrl_io_cmdSent <= 1'b1;
      end
      if(when_LsuPlugin_l599) begin
        LsuPlugin_logic_onCtrl_io_cmdSent <= 1'b0;
      end
      if(LsuPlugin_logic_bus_rsp_toStream_valid) begin
        LsuPlugin_logic_bus_rsp_toStream_rValid <= 1'b1;
      end
      if(LsuPlugin_logic_onCtrl_io_rsp_fire) begin
        LsuPlugin_logic_bus_rsp_toStream_rValid <= 1'b0;
      end
      if(when_LsuPlugin_l259) begin
        LsuPlugin_logic_onCtrl_hartRegulation_valid <= 1'b0;
      end
      if(when_LsuPlugin_l943) begin
        if(when_LsuPlugin_l263) begin
          LsuPlugin_logic_onCtrl_hartRegulation_valid <= 1'b1;
        end
      end
      if(LsuPlugin_logic_bus_cmd_ready) begin
        LsuPlugin_logic_bus_cmd_rValid <= LsuPlugin_logic_bus_cmd_valid;
      end
      if(when_DecoderPlugin_l143) begin
        DecoderPlugin_logic_harts_0_uopId <= (DecoderPlugin_logic_harts_0_uopId + 16'h0001);
      end
      if(when_DecoderPlugin_l151) begin
        DecoderPlugin_logic_interrupt_buffered <= DecoderPlugin_logic_interrupt_async;
      end
      decode_ctrls_1_up_LANE_SEL_0_regNext <= decode_ctrls_1_up_LANE_SEL_0;
      if(when_CtrlLaneApi_l50_1) begin
        decode_ctrls_1_up_LANE_SEL_0_regNext <= 1'b0;
      end
      if(DispatchPlugin_logic_feeds_0_sending) begin
        DispatchPlugin_logic_feeds_0_sent <= 1'b1;
      end
      if(decode_ctrls_1_up_isMoving) begin
        DispatchPlugin_logic_feeds_0_sent <= 1'b0;
      end
      if(when_CsrRamPlugin_l92) begin
        CsrRamPlugin_csrMapper_fired <= 1'b1;
      end
      if(CsrAccessPlugin_bus_write_moving) begin
        CsrRamPlugin_csrMapper_fired <= 1'b0;
      end
      decode_ctrls_1_up_LANE_SEL_0_regNext_1 <= decode_ctrls_1_up_LANE_SEL_0;
      if(when_CtrlLaneApi_l50_2) begin
        decode_ctrls_1_up_LANE_SEL_0_regNext_1 <= 1'b0;
      end
      execute_ctrl0_down_LANE_SEL_lane0_regNext <= execute_ctrl0_down_LANE_SEL_lane0;
      if(when_CtrlLaneApi_l50_3) begin
        execute_ctrl0_down_LANE_SEL_lane0_regNext <= 1'b0;
      end
      execute_ctrl2_down_LANE_SEL_lane0_regNext <= execute_ctrl2_down_LANE_SEL_lane0;
      if(when_CtrlLaneApi_l50_4) begin
        execute_ctrl2_down_LANE_SEL_lane0_regNext <= 1'b0;
      end
      `ifndef SYNTHESIS
        `ifdef FORMAL
          assert((! (fetch_logic_ctrls_1_up_isValid && fetch_logic_ctrls_1_down_BtbPlugin_logic_readCmd_HAZARDS[0]))); // BtbPlugin.scala:L215
        `else
          if(!(! (fetch_logic_ctrls_1_up_isValid && fetch_logic_ctrls_1_down_BtbPlugin_logic_readCmd_HAZARDS[0]))) begin
            $display("FAILURE "); // BtbPlugin.scala:L215
            $finish;
          end
        `endif
      `endif
      if(fetch_logic_ctrls_2_up_isValid) begin
        BtbPlugin_logic_applyIt_correctionSent <= 1'b1;
      end
      if(when_BtbPlugin_l233) begin
        BtbPlugin_logic_applyIt_correctionSent <= 1'b0;
      end
      if(when_AlignerPlugin_l298) begin
        AlignerPlugin_logic_nobuffer_mask <= 1'b1;
      end
      TrapPlugin_logic_harts_0_interrupt_validBuffer <= TrapPlugin_logic_harts_0_interrupt_valid;
      PcPlugin_logic_harts_0_holdReg <= PcPlugin_logic_harts_0_holdComb;
      PcPlugin_logic_harts_0_self_state <= PcPlugin_logic_harts_0_output_payload_pc;
      PcPlugin_logic_harts_0_self_fault <= PcPlugin_logic_harts_0_output_payload_fault;
      PcPlugin_logic_harts_0_self_increment <= 1'b0;
      if(PcPlugin_logic_harts_0_output_fire) begin
        PcPlugin_logic_harts_0_self_increment <= 1'b1;
      end
      if(fetch_logic_ctrls_0_up_isFiring) begin
        PcPlugin_logic_harts_0_self_id <= (PcPlugin_logic_harts_0_self_id + 10'h001);
      end
      `ifndef SYNTHESIS
        `ifdef FORMAL
          assert((! ((execute_ctrl2_up_LANE_SEL_lane0 && execute_ctrl2_down_CsrAccessPlugin_SEL_lane0) && execute_lane0_ctrls_2_upIsCancel))); // CsrAccessPlugin.scala:L136
        `else
          if(!(! ((execute_ctrl2_up_LANE_SEL_lane0 && execute_ctrl2_down_CsrAccessPlugin_SEL_lane0) && execute_lane0_ctrls_2_upIsCancel))) begin
            $display("FAILURE CsrAccessPlugin saw forbidden select && cancel request"); // CsrAccessPlugin.scala:L136
            $finish;
          end
        `endif
      `endif
      CsrAccessPlugin_logic_fsm_inject_unfreeze <= 1'b0;
      if(CsrAccessPlugin_logic_flushPort_valid) begin
        CsrAccessPlugin_logic_fsm_inject_flushReg <= 1'b1;
      end
      if(when_CsrAccessPlugin_l197) begin
        CsrAccessPlugin_logic_fsm_inject_flushReg <= 1'b0;
      end
      CsrAccessPlugin_logic_fsm_inject_sampled <= execute_freeze_valid;
      if(when_CsrAccessPlugin_l346) begin
        PrivilegedPlugin_logic_harts_0_m_status_mpie <= CsrAccessPlugin_bus_write_bits[7];
        PrivilegedPlugin_logic_harts_0_m_status_mie <= CsrAccessPlugin_bus_write_bits[3];
        PrivilegedPlugin_logic_harts_0_m_status_mprv <= CsrAccessPlugin_bus_write_bits[17];
      end
      if(when_CsrAccessPlugin_l346_1) begin
        PrivilegedPlugin_logic_harts_0_m_cause_interrupt <= CsrAccessPlugin_bus_write_bits[31];
        PrivilegedPlugin_logic_harts_0_m_cause_code <= CsrAccessPlugin_bus_write_bits[3 : 0];
      end
      if(when_CsrAccessPlugin_l346_2) begin
        PrivilegedPlugin_logic_harts_0_m_ie_meie <= CsrAccessPlugin_bus_write_bits[11];
        PrivilegedPlugin_logic_harts_0_m_ie_mtie <= CsrAccessPlugin_bus_write_bits[7];
        PrivilegedPlugin_logic_harts_0_m_ie_msie <= CsrAccessPlugin_bus_write_bits[3];
      end
      CsrRamPlugin_logic_readLogic_ohReg <= (CsrRamPlugin_logic_readLogic_port_cmd_valid ? CsrRamPlugin_logic_readLogic_oh : 2'b00);
      CsrRamPlugin_logic_readLogic_busy <= CsrRamPlugin_logic_readLogic_port_cmd_valid;
      CsrRamPlugin_logic_flush_counter <= (CsrRamPlugin_logic_flush_counter + _zz_CsrRamPlugin_logic_flush_counter);
      if(when_RegFilePlugin_l130) begin
        integer_RegFilePlugin_logic_initalizer_counter <= (integer_RegFilePlugin_logic_initalizer_counter + 6'h01);
      end
      _zz_WhiteboxerPlugin_logic_perf_executeFreezedCounter_2 <= _zz_WhiteboxerPlugin_logic_perf_executeFreezedCounter_1;
      _zz_WhiteboxerPlugin_logic_perf_dispatchHazardsCounter_2 <= _zz_WhiteboxerPlugin_logic_perf_dispatchHazardsCounter_1;
      _zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_0_2 <= _zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_0_1;
      _zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_1_2 <= _zz_WhiteboxerPlugin_logic_perf_candidatesCountCounters_1_1;
      _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_0_2 <= _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_0_1;
      _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_1_2 <= _zz_WhiteboxerPlugin_logic_perf_dispatchFeedCounters_1_1;
      if(fetch_logic_ctrls_1_up_forgetOne) begin
        fetch_logic_ctrls_1_up_valid <= 1'b0;
      end
      if(fetch_logic_ctrls_0_down_isReady) begin
        fetch_logic_ctrls_1_up_valid <= fetch_logic_ctrls_0_down_isValid;
      end
      if(fetch_logic_ctrls_2_up_forgetOne) begin
        fetch_logic_ctrls_2_up_valid <= 1'b0;
      end
      if(fetch_logic_ctrls_1_down_isReady) begin
        fetch_logic_ctrls_2_up_valid <= fetch_logic_ctrls_1_down_isValid;
      end
      if(decode_ctrls_0_down_isReady) begin
        decode_ctrls_1_up_valid <= decode_ctrls_0_down_isValid;
      end
      if(decode_ctrls_0_down_isReady) begin
        decode_ctrls_1_up_LANE_SEL_0 <= decode_ctrls_0_down_LANE_SEL_0;
      end
      if(when_DecodePipelinePlugin_l70) begin
        decode_ctrls_1_up_LANE_SEL_0 <= 1'b0;
      end
      if(execute_ctrl0_down_isReady) begin
        execute_ctrl1_up_LANE_SEL_lane0 <= execute_ctrl0_down_LANE_SEL_lane0;
      end
      if(execute_ctrl1_down_isReady) begin
        execute_ctrl2_up_LANE_SEL_lane0 <= execute_ctrl1_down_LANE_SEL_lane0;
      end
      if(execute_ctrl2_down_isReady) begin
        execute_ctrl3_up_LANE_SEL_lane0 <= execute_ctrl2_down_LANE_SEL_lane0;
        execute_ctrl3_up_LsuL1_SEL_lane0 <= execute_ctrl2_down_LsuL1_SEL_lane0;
      end
      if(execute_ctrl3_down_isReady) begin
        execute_ctrl4_up_LANE_SEL_lane0 <= execute_ctrl3_down_LANE_SEL_lane0;
        execute_ctrl4_up_LsuL1_SEL_lane0 <= execute_ctrl3_down_LsuL1_SEL_lane0;
      end
      if(execute_ctrl4_down_isReady) begin
        execute_ctrl5_up_LANE_SEL_lane0 <= execute_ctrl4_down_LANE_SEL_lane0;
      end
      LsuPlugin_logic_flusher_stateReg <= LsuPlugin_logic_flusher_stateNext;
      TrapPlugin_logic_harts_0_trap_fsm_stateReg <= TrapPlugin_logic_harts_0_trap_fsm_stateNext;
      case(TrapPlugin_logic_harts_0_trap_fsm_stateReg)
        TrapPlugin_logic_harts_0_trap_fsm_RUNNING : begin
        end
        TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1 : begin
          TrapPlugin_logic_harts_0_trap_fsm_trapEnterDebug <= 1'b0;
          if(!when_TrapPlugin_l409) begin
            case(TrapPlugin_logic_harts_0_trap_pending_state_code)
              4'b0000 : begin
                `ifndef SYNTHESIS
                  `ifdef FORMAL
                    assert((! TrapPlugin_logic_harts_0_trap_fsm_buffer_i_valid)); // TrapPlugin.scala:L431
                  `else
                    if(!(! TrapPlugin_logic_harts_0_trap_fsm_buffer_i_valid)) begin
                      $display("FAILURE "); // TrapPlugin.scala:L431
                      $finish;
                    end
                  `endif
                `endif
              end
              4'b0001 : begin
              end
              4'b0010 : begin
              end
              4'b0100 : begin
              end
              4'b0101 : begin
              end
              4'b1000 : begin
              end
              4'b0110 : begin
              end
              default : begin
                `ifndef SYNTHESIS
                  `ifdef FORMAL
                    assert(1'b0); // TrapPlugin.scala:L482
                  `else
                    if(!1'b0) begin
                      $display("FAILURE Unexpected trap reason"); // TrapPlugin.scala:L482
                      $finish;
                    end
                  `endif
                `endif
              end
            endcase
          end
        end
        TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC : begin
        end
        TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL : begin
        end
        TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC : begin
        end
        TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY : begin
          PrivilegedPlugin_logic_harts_0_privilege <= TrapPlugin_logic_harts_0_trap_fsm_buffer_trap_targetPrivilege;
          case(TrapPlugin_logic_harts_0_trap_fsm_buffer_trap_targetPrivilege)
            2'b11 : begin
              PrivilegedPlugin_logic_harts_0_m_status_mie <= 1'b0;
              PrivilegedPlugin_logic_harts_0_m_status_mpie <= PrivilegedPlugin_logic_harts_0_m_status_mie;
              PrivilegedPlugin_logic_harts_0_m_cause_code <= TrapPlugin_logic_harts_0_trap_fsm_buffer_trap_code;
              PrivilegedPlugin_logic_harts_0_m_cause_interrupt <= TrapPlugin_logic_harts_0_trap_fsm_buffer_trap_interrupt;
            end
            default : begin
            end
          endcase
        end
        TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC : begin
        end
        TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY : begin
          PrivilegedPlugin_logic_harts_0_privilege <= TrapPlugin_logic_harts_0_trap_pending_xret_targetPrivilege;
          case(switch_TrapPlugin_l655)
            2'b11 : begin
              PrivilegedPlugin_logic_harts_0_m_status_mie <= PrivilegedPlugin_logic_harts_0_m_status_mpie;
              PrivilegedPlugin_logic_harts_0_m_status_mpie <= 1'b1;
            end
            default : begin
            end
          endcase
        end
        TrapPlugin_logic_harts_0_trap_fsm_JUMP : begin
        end
        TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH : begin
        end
        TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH : begin
        end
        default : begin
        end
      endcase
      CsrAccessPlugin_logic_fsm_stateReg <= CsrAccessPlugin_logic_fsm_stateNext;
      case(CsrAccessPlugin_logic_fsm_stateReg)
        CsrAccessPlugin_logic_fsm_READ : begin
        end
        CsrAccessPlugin_logic_fsm_WRITE : begin
        end
        CsrAccessPlugin_logic_fsm_COMPLETION : begin
        end
        default : begin
          if(CsrAccessPlugin_logic_fsm_inject_onDecodeDo) begin
            if(CsrAccessPlugin_logic_fsm_inject_sampled) begin
              if(CsrAccessPlugin_logic_fsm_inject_trapReg) begin
                CsrAccessPlugin_logic_fsm_inject_unfreeze <= execute_freeze_valid;
              end
            end
          end
        end
      endcase
      case(CsrAccessPlugin_logic_fsm_stateNext)
        CsrAccessPlugin_logic_fsm_READ : begin
        end
        CsrAccessPlugin_logic_fsm_WRITE : begin
        end
        CsrAccessPlugin_logic_fsm_COMPLETION : begin
          CsrAccessPlugin_logic_fsm_inject_unfreeze <= 1'b1;
        end
        default : begin
        end
      endcase
    end
  end

  always @(posedge clk) begin
    LsuL1Plugin_logic_refill_slots_0_loadedCounter <= (LsuL1Plugin_logic_refill_slots_0_loadedCounter + ((LsuL1Plugin_logic_refill_slots_0_loaded && (! LsuL1Plugin_logic_refill_slots_0_loadedDone)) && (! execute_freeze_valid)));
    if(when_LsuL1Plugin_l381) begin
      LsuL1Plugin_logic_refill_slots_0_address <= LsuL1Plugin_logic_refill_push_payload_address;
      LsuL1Plugin_logic_refill_slots_0_cmdSent <= 1'b0;
      LsuL1Plugin_logic_refill_slots_0_loadedCounter <= 1'b0;
      LsuL1Plugin_logic_refill_slots_0_victim <= LsuL1Plugin_logic_refill_push_payload_victim;
      LsuL1Plugin_logic_refill_slots_0_dirty <= LsuL1Plugin_logic_refill_push_payload_dirty;
    end
    if(LsuL1Plugin_logic_refill_read_arbiter_oh[0]) begin
      if(LsuL1Plugin_logic_bus_read_cmd_ready) begin
        LsuL1Plugin_logic_refill_slots_0_cmdSent <= 1'b1;
      end
    end
    LsuL1Plugin_logic_writeback_slots_0_timer_counter <= (LsuL1Plugin_logic_writeback_slots_0_timer_counter + ((! LsuL1Plugin_logic_writeback_slots_0_timer_done) && (! execute_freeze_valid)));
    if(when_LsuL1Plugin_l561) begin
      LsuL1Plugin_logic_writeback_slots_0_address <= LsuL1Plugin_logic_writeback_push_payload_address;
      LsuL1Plugin_logic_writeback_slots_0_timer_counter <= 1'b0;
      LsuL1Plugin_logic_writeback_slots_0_writeCmdDone <= 1'b0;
      LsuL1Plugin_logic_writeback_slots_0_readCmdDone <= 1'b0;
      LsuL1Plugin_logic_writeback_slots_0_readRspDone <= 1'b0;
      LsuL1Plugin_logic_writeback_slots_0_victimBufferReady <= 1'b0;
    end
    if(when_LsuL1Plugin_l605) begin
      if(LsuL1Plugin_logic_writeback_read_arbiter_oh[0]) begin
        LsuL1Plugin_logic_writeback_slots_0_readCmdDone <= 1'b1;
      end
    end
    if(LsuL1Plugin_logic_writeback_read_slotRead_valid) begin
      LsuL1Plugin_logic_refill_slots_0_victim[0] <= 1'b0;
    end
    LsuL1Plugin_logic_writeback_read_slotReadLast_payload_last <= LsuL1Plugin_logic_writeback_read_slotRead_payload_last;
    LsuL1Plugin_logic_writeback_read_slotReadLast_payload_wordIndex <= LsuL1Plugin_logic_writeback_read_slotRead_payload_wordIndex;
    if(LsuL1Plugin_logic_writeback_read_slotReadLast_valid) begin
      LsuL1Plugin_logic_writeback_slots_0_victimBufferReady <= 1'b1;
      if(LsuL1Plugin_logic_writeback_read_slotReadLast_payload_last) begin
        LsuL1Plugin_logic_writeback_slots_0_readRspDone <= 1'b1;
      end
    end
    if(when_LsuL1Plugin_l676) begin
      if(LsuL1Plugin_logic_writeback_write_arbiter_oh[0]) begin
        LsuL1Plugin_logic_writeback_slots_0_writeCmdDone <= 1'b1;
      end
    end
    if(LsuL1Plugin_logic_writeback_write_bufferRead_ready) begin
      LsuL1Plugin_logic_writeback_write_bufferRead_rData_address <= LsuL1Plugin_logic_writeback_write_bufferRead_payload_address;
      LsuL1Plugin_logic_writeback_write_bufferRead_rData_last <= LsuL1Plugin_logic_writeback_write_bufferRead_payload_last;
    end
    early0_DivPlugin_logic_processing_divRevertResult <= ((execute_ctrl2_down_RsUnsignedPlugin_RS1_REVERT_lane0 ^ (execute_ctrl2_down_RsUnsignedPlugin_RS2_REVERT_lane0 && (! execute_ctrl2_down_DivPlugin_REM_lane0))) && (! (((execute_ctrl2_down_RsUnsignedPlugin_RS2_FORMATED_lane0 == 32'h0) && execute_ctrl2_down_RsUnsignedPlugin_RS2_SIGNED_lane0) && (! execute_ctrl2_down_DivPlugin_REM_lane0))));
    if(LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_ready) begin
      LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_rData_last <= LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_payload_last;
      LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_rData_fragment_write <= LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_payload_fragment_write;
      LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_rData_fragment_address <= LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_payload_fragment_address;
      LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_rData_fragment_data <= LsuL1Plugin_logic_bus_toWishbone_arbiter_serialized_payload_fragment_data;
    end
    if(when_FetchL1Plugin_l255) begin
      if(_zz_when_1) begin
        FetchL1Plugin_logic_refill_slots_0_address <= FetchL1Plugin_logic_refill_start_address;
        FetchL1Plugin_logic_refill_slots_0_isIo <= FetchL1Plugin_logic_refill_start_isIo;
        FetchL1Plugin_logic_refill_slots_0_priority <= FetchL1Plugin_logic_refill_slots_0_valid;
      end
    end
    if(when_FetchL1Plugin_l276) begin
      FetchL1Plugin_logic_refill_onCmd_lockedOh <= FetchL1Plugin_logic_refill_onCmd_propoedOh;
    end
    FetchL1Plugin_logic_ctrl_plruLogic_buffer_regNext_payload_address <= FetchL1Plugin_logic_ctrl_plruLogic_buffer_payload_address;
    FetchL1WishbonePlugin_logic_bus_DAT_MISO_regNext <= FetchL1WishbonePlugin_logic_bus_DAT_MISO;
    FetchL1WishbonePlugin_logic_bus_ERR_regNext <= FetchL1WishbonePlugin_logic_bus_ERR;
    if(LsuPlugin_logic_onAddress0_flush_port_fire) begin
      LsuPlugin_logic_flusher_cmdCounter <= (LsuPlugin_logic_flusher_cmdCounter + 5'h01);
    end
    if(LsuPlugin_logic_bus_rsp_toStream_ready) begin
      LsuPlugin_logic_bus_rsp_toStream_rData_error <= LsuPlugin_logic_bus_rsp_toStream_payload_error;
      LsuPlugin_logic_bus_rsp_toStream_rData_data <= LsuPlugin_logic_bus_rsp_toStream_payload_data;
    end
    if(when_LsuPlugin_l899) begin
      LsuPlugin_logic_flusher_cmdCounter <= {1'd0, _zz_LsuPlugin_logic_flusher_cmdCounter};
    end
    if(when_LsuPlugin_l943) begin
      if(when_LsuPlugin_l263) begin
        LsuPlugin_logic_onCtrl_hartRegulation_refill <= execute_ctrl4_down_LsuL1_WAIT_REFILL_lane0;
      end
    end
    if(LsuPlugin_logic_bus_cmd_ready) begin
      LsuPlugin_logic_bus_cmd_rData_write <= LsuPlugin_logic_bus_cmd_payload_write;
      LsuPlugin_logic_bus_cmd_rData_address <= LsuPlugin_logic_bus_cmd_payload_address;
      LsuPlugin_logic_bus_cmd_rData_data <= LsuPlugin_logic_bus_cmd_payload_data;
      LsuPlugin_logic_bus_cmd_rData_size <= LsuPlugin_logic_bus_cmd_payload_size;
      LsuPlugin_logic_bus_cmd_rData_mask <= LsuPlugin_logic_bus_cmd_payload_mask;
      LsuPlugin_logic_bus_cmd_rData_io <= LsuPlugin_logic_bus_cmd_payload_io;
      LsuPlugin_logic_bus_cmd_rData_fromHart <= LsuPlugin_logic_bus_cmd_payload_fromHart;
      LsuPlugin_logic_bus_cmd_rData_uopId <= LsuPlugin_logic_bus_cmd_payload_uopId;
    end
    if(TrapPlugin_logic_harts_0_trap_pending_arbiter_down_valid) begin
      TrapPlugin_logic_harts_0_trap_pending_state_exception <= TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_exception;
      TrapPlugin_logic_harts_0_trap_pending_state_tval <= TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_tval;
      TrapPlugin_logic_harts_0_trap_pending_state_code <= TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_code;
      TrapPlugin_logic_harts_0_trap_pending_state_arg <= TrapPlugin_logic_harts_0_trap_pending_arbiter_down_payload_arg;
    end
    if(TrapPlugin_logic_harts_0_trap_trigger_valid) begin
      TrapPlugin_logic_harts_0_trap_pending_pc <= execute_ctrl4_down_PC_lane0;
      TrapPlugin_logic_harts_0_trap_pending_slices <= (1'b0 + 1'b1);
    end
    if(TrapPlugin_logic_harts_0_trap_fsm_buffer_sampleIt) begin
      TrapPlugin_logic_harts_0_trap_fsm_buffer_i_valid <= TrapPlugin_logic_harts_0_interrupt_valid;
    end
    if(TrapPlugin_logic_harts_0_trap_fsm_buffer_sampleIt) begin
      TrapPlugin_logic_harts_0_trap_fsm_buffer_i_code <= TrapPlugin_logic_harts_0_interrupt_code;
    end
    if(TrapPlugin_logic_harts_0_trap_fsm_buffer_sampleIt) begin
      TrapPlugin_logic_harts_0_trap_fsm_buffer_i_targetPrivilege <= TrapPlugin_logic_harts_0_interrupt_targetPrivilege;
    end
    TrapPlugin_logic_harts_0_trap_fsm_jumpTarget <= (TrapPlugin_logic_harts_0_trap_pending_pc + _zz_TrapPlugin_logic_harts_0_trap_fsm_jumpTarget);
    if(when_TrapPlugin_l556) begin
      TrapPlugin_logic_harts_0_trap_fsm_readed <= TrapPlugin_logic_harts_0_crsPorts_read_data;
    end
    CsrAccessPlugin_logic_fsm_interface_read <= ((execute_ctrl2_down_CsrAccessPlugin_SEL_lane0 && (! CsrAccessPlugin_logic_fsm_inject_trap)) && CsrAccessPlugin_logic_fsm_inject_csrRead);
    CsrAccessPlugin_logic_fsm_interface_write <= ((execute_ctrl2_down_CsrAccessPlugin_SEL_lane0 && (! CsrAccessPlugin_logic_fsm_inject_trap)) && CsrAccessPlugin_logic_fsm_inject_csrWrite);
    CsrAccessPlugin_logic_fsm_inject_trapReg <= CsrAccessPlugin_logic_fsm_inject_trap;
    CsrAccessPlugin_logic_fsm_inject_busTrapReg <= CsrAccessPlugin_bus_decode_trap;
    CsrAccessPlugin_logic_fsm_inject_busTrapCodeReg <= CsrAccessPlugin_bus_decode_trapCode;
    CsrAccessPlugin_logic_fsm_interface_onWriteBits <= CsrAccessPlugin_logic_fsm_writeLogic_alu_result;
    if(fetch_logic_ctrls_0_down_isReady) begin
      fetch_logic_ctrls_1_up_Fetch_WORD_PC <= fetch_logic_ctrls_0_down_Fetch_WORD_PC;
      fetch_logic_ctrls_1_up_Fetch_PC_FAULT <= fetch_logic_ctrls_0_down_Fetch_PC_FAULT;
      fetch_logic_ctrls_1_up_Fetch_ID <= fetch_logic_ctrls_0_down_Fetch_ID;
      fetch_logic_ctrls_1_up_FetchL1Plugin_logic_cmd_PLRU_BYPASS_VALID <= fetch_logic_ctrls_0_down_FetchL1Plugin_logic_cmd_PLRU_BYPASS_VALID;
      fetch_logic_ctrls_1_up_FetchL1Plugin_logic_cmd_TAGS_UPDATE <= fetch_logic_ctrls_0_down_FetchL1Plugin_logic_cmd_TAGS_UPDATE;
      fetch_logic_ctrls_1_up_FetchL1Plugin_logic_cmd_TAGS_UPDATE_ADDRESS <= fetch_logic_ctrls_0_down_FetchL1Plugin_logic_cmd_TAGS_UPDATE_ADDRESS;
      fetch_logic_ctrls_1_up_BtbPlugin_logic_readCmd_HAZARDS <= fetch_logic_ctrls_0_down_BtbPlugin_logic_readCmd_HAZARDS;
    end
    if(fetch_logic_ctrls_1_down_isReady) begin
      fetch_logic_ctrls_2_up_Fetch_WORD_PC <= fetch_logic_ctrls_1_down_Fetch_WORD_PC;
      fetch_logic_ctrls_2_up_Fetch_PC_FAULT <= fetch_logic_ctrls_1_down_Fetch_PC_FAULT;
      fetch_logic_ctrls_2_up_Fetch_ID <= fetch_logic_ctrls_1_down_Fetch_ID;
      fetch_logic_ctrls_2_up_FetchL1Plugin_logic_WAYS_TAGS_0_loaded <= fetch_logic_ctrls_1_down_FetchL1Plugin_logic_WAYS_TAGS_0_loaded;
      fetch_logic_ctrls_2_up_FetchL1Plugin_logic_WAYS_TAGS_0_error <= fetch_logic_ctrls_1_down_FetchL1Plugin_logic_WAYS_TAGS_0_error;
      fetch_logic_ctrls_2_up_FetchL1Plugin_logic_WAYS_TAGS_0_address <= fetch_logic_ctrls_1_down_FetchL1Plugin_logic_WAYS_TAGS_0_address;
      fetch_logic_ctrls_2_up_FetchL1Plugin_logic_BANKS_MUXES_0 <= fetch_logic_ctrls_1_down_FetchL1Plugin_logic_BANKS_MUXES_0;
      fetch_logic_ctrls_2_up_FetchL1Plugin_logic_HAZARD <= fetch_logic_ctrls_1_down_FetchL1Plugin_logic_HAZARD;
      fetch_logic_ctrls_2_up_FetchL1Plugin_logic_WAYS_HITS_0 <= fetch_logic_ctrls_1_down_FetchL1Plugin_logic_WAYS_HITS_0;
      fetch_logic_ctrls_2_up_MMU_TRANSLATED <= fetch_logic_ctrls_1_down_MMU_TRANSLATED;
      fetch_logic_ctrls_2_up_FetchL1Plugin_logic_WAYS_HIT <= fetch_logic_ctrls_1_down_FetchL1Plugin_logic_WAYS_HIT;
      fetch_logic_ctrls_2_up_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_hash <= fetch_logic_ctrls_1_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_hash;
      fetch_logic_ctrls_2_up_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_pcTarget <= fetch_logic_ctrls_1_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_pcTarget;
      fetch_logic_ctrls_2_up_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isBranch <= fetch_logic_ctrls_1_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isBranch;
      fetch_logic_ctrls_2_up_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isPush <= fetch_logic_ctrls_1_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isPush;
      fetch_logic_ctrls_2_up_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isPop <= fetch_logic_ctrls_1_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_isPop;
      fetch_logic_ctrls_2_up_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_taken <= fetch_logic_ctrls_1_down_BtbPlugin_logic_chunksLogic_0_readRsp_ENTRY_taken;
      fetch_logic_ctrls_2_up_BtbPlugin_logic_chunksLogic_0_hitCalc_HIT <= fetch_logic_ctrls_1_down_BtbPlugin_logic_chunksLogic_0_hitCalc_HIT;
      fetch_logic_ctrls_2_up_MMU_REFILL <= fetch_logic_ctrls_1_down_MMU_REFILL;
      fetch_logic_ctrls_2_up_MMU_HAZARD <= fetch_logic_ctrls_1_down_MMU_HAZARD;
      fetch_logic_ctrls_2_up_MMU_ALLOW_EXECUTE <= fetch_logic_ctrls_1_down_MMU_ALLOW_EXECUTE;
      fetch_logic_ctrls_2_up_MMU_PAGE_FAULT <= fetch_logic_ctrls_1_down_MMU_PAGE_FAULT;
      fetch_logic_ctrls_2_up_MMU_ACCESS_FAULT <= fetch_logic_ctrls_1_down_MMU_ACCESS_FAULT;
      fetch_logic_ctrls_2_up_MMU_BYPASS_TRANSLATION <= fetch_logic_ctrls_1_down_MMU_BYPASS_TRANSLATION;
    end
    if(decode_ctrls_0_down_isReady) begin
      decode_ctrls_1_up_Decode_INSTRUCTION_0 <= decode_ctrls_0_down_Decode_INSTRUCTION_0;
      decode_ctrls_1_up_Decode_DECOMPRESSION_FAULT_0 <= decode_ctrls_0_down_Decode_DECOMPRESSION_FAULT_0;
      decode_ctrls_1_up_Decode_INSTRUCTION_RAW_0 <= decode_ctrls_0_down_Decode_INSTRUCTION_RAW_0;
      decode_ctrls_1_up_PC_0 <= decode_ctrls_0_down_PC_0;
      decode_ctrls_1_up_Decode_DOP_ID_0 <= decode_ctrls_0_down_Decode_DOP_ID_0;
      decode_ctrls_1_up_TRAP_0 <= decode_ctrls_0_down_TRAP_0;
      decode_ctrls_1_up_Prediction_ALIGNED_JUMPED_0 <= decode_ctrls_0_down_Prediction_ALIGNED_JUMPED_0;
      decode_ctrls_1_up_Prediction_ALIGNED_JUMPED_PC_0 <= decode_ctrls_0_down_Prediction_ALIGNED_JUMPED_PC_0;
      decode_ctrls_1_up_Prediction_ALIGNED_SLICES_BRANCH_0 <= decode_ctrls_0_down_Prediction_ALIGNED_SLICES_BRANCH_0;
      decode_ctrls_1_up_Prediction_ALIGNED_SLICES_TAKEN_0 <= decode_ctrls_0_down_Prediction_ALIGNED_SLICES_TAKEN_0;
      decode_ctrls_1_up_Prediction_ALIGN_REDO_0 <= decode_ctrls_0_down_Prediction_ALIGN_REDO_0;
    end
    if(execute_ctrl0_down_isReady) begin
      execute_ctrl1_up_Decode_UOP_lane0 <= execute_ctrl0_down_Decode_UOP_lane0;
      execute_ctrl1_up_Prediction_ALIGNED_JUMPED_lane0 <= execute_ctrl0_down_Prediction_ALIGNED_JUMPED_lane0;
      execute_ctrl1_up_Prediction_ALIGNED_JUMPED_PC_lane0 <= execute_ctrl0_down_Prediction_ALIGNED_JUMPED_PC_lane0;
      execute_ctrl1_up_PC_lane0 <= execute_ctrl0_down_PC_lane0;
      execute_ctrl1_up_TRAP_lane0 <= execute_ctrl0_down_TRAP_lane0;
      execute_ctrl1_up_Decode_UOP_ID_lane0 <= execute_ctrl0_down_Decode_UOP_ID_lane0;
      execute_ctrl1_up_RS1_PHYS_lane0 <= execute_ctrl0_down_RS1_PHYS_lane0;
      execute_ctrl1_up_RS2_PHYS_lane0 <= execute_ctrl0_down_RS2_PHYS_lane0;
      execute_ctrl1_up_RD_ENABLE_lane0 <= execute_ctrl0_down_RD_ENABLE_lane0;
      execute_ctrl1_up_RD_PHYS_lane0 <= execute_ctrl0_down_RD_PHYS_lane0;
      execute_ctrl1_up_COMPLETED_lane0 <= execute_ctrl0_down_COMPLETED_lane0;
      execute_ctrl1_up_lane0_LAYER_SEL_lane0 <= execute_ctrl0_down_lane0_LAYER_SEL_lane0;
      execute_ctrl1_up_AguPlugin_SIZE_lane0 <= execute_ctrl0_down_AguPlugin_SIZE_lane0;
    end
    if(execute_ctrl1_down_isReady) begin
      execute_ctrl2_up_Decode_UOP_lane0 <= execute_ctrl1_down_Decode_UOP_lane0;
      execute_ctrl2_up_Prediction_ALIGNED_JUMPED_lane0 <= execute_ctrl1_down_Prediction_ALIGNED_JUMPED_lane0;
      execute_ctrl2_up_Prediction_ALIGNED_JUMPED_PC_lane0 <= execute_ctrl1_down_Prediction_ALIGNED_JUMPED_PC_lane0;
      execute_ctrl2_up_PC_lane0 <= execute_ctrl1_down_PC_lane0;
      execute_ctrl2_up_TRAP_lane0 <= execute_ctrl1_down_TRAP_lane0;
      execute_ctrl2_up_Decode_UOP_ID_lane0 <= execute_ctrl1_down_Decode_UOP_ID_lane0;
      execute_ctrl2_up_RS1_PHYS_lane0 <= execute_ctrl1_down_RS1_PHYS_lane0;
      execute_ctrl2_up_RS2_PHYS_lane0 <= execute_ctrl1_down_RS2_PHYS_lane0;
      execute_ctrl2_up_RD_ENABLE_lane0 <= execute_ctrl1_down_RD_ENABLE_lane0;
      execute_ctrl2_up_RD_PHYS_lane0 <= execute_ctrl1_down_RD_PHYS_lane0;
      execute_ctrl2_up_COMPLETED_lane0 <= execute_ctrl1_down_COMPLETED_lane0;
      execute_ctrl2_up_AguPlugin_SIZE_lane0 <= execute_ctrl1_down_AguPlugin_SIZE_lane0;
      execute_ctrl2_up_early0_SrcPlugin_SRC1_lane0 <= execute_ctrl1_down_early0_SrcPlugin_SRC1_lane0;
      execute_ctrl2_up_integer_RS1_lane0 <= execute_ctrl1_down_integer_RS1_lane0;
      execute_ctrl2_up_early0_SrcPlugin_SRC2_lane0 <= execute_ctrl1_down_early0_SrcPlugin_SRC2_lane0;
      execute_ctrl2_up_integer_RS2_lane0 <= execute_ctrl1_down_integer_RS2_lane0;
      execute_ctrl2_up_MAY_FLUSH_PRECISE_3_lane0 <= execute_ctrl1_down_MAY_FLUSH_PRECISE_3_lane0;
      execute_ctrl2_up_early0_IntAluPlugin_SEL_lane0 <= execute_ctrl1_down_early0_IntAluPlugin_SEL_lane0;
      execute_ctrl2_up_early0_BarrelShifterPlugin_SEL_lane0 <= execute_ctrl1_down_early0_BarrelShifterPlugin_SEL_lane0;
      execute_ctrl2_up_early0_BranchPlugin_SEL_lane0 <= execute_ctrl1_down_early0_BranchPlugin_SEL_lane0;
      execute_ctrl2_up_early0_MulPlugin_SEL_lane0 <= execute_ctrl1_down_early0_MulPlugin_SEL_lane0;
      execute_ctrl2_up_early0_DivPlugin_SEL_lane0 <= execute_ctrl1_down_early0_DivPlugin_SEL_lane0;
      execute_ctrl2_up_early0_EnvPlugin_SEL_lane0 <= execute_ctrl1_down_early0_EnvPlugin_SEL_lane0;
      execute_ctrl2_up_late0_IntAluPlugin_SEL_lane0 <= execute_ctrl1_down_late0_IntAluPlugin_SEL_lane0;
      execute_ctrl2_up_late0_BarrelShifterPlugin_SEL_lane0 <= execute_ctrl1_down_late0_BarrelShifterPlugin_SEL_lane0;
      execute_ctrl2_up_late0_BranchPlugin_SEL_lane0 <= execute_ctrl1_down_late0_BranchPlugin_SEL_lane0;
      execute_ctrl2_up_CsrAccessPlugin_SEL_lane0 <= execute_ctrl1_down_CsrAccessPlugin_SEL_lane0;
      execute_ctrl2_up_AguPlugin_SEL_lane0 <= execute_ctrl1_down_AguPlugin_SEL_lane0;
      execute_ctrl2_up_LsuPlugin_logic_FENCE_lane0 <= execute_ctrl1_down_LsuPlugin_logic_FENCE_lane0;
      execute_ctrl2_up_lane0_integer_WriteBackPlugin_SEL_lane0 <= execute_ctrl1_down_lane0_integer_WriteBackPlugin_SEL_lane0;
      execute_ctrl2_up_COMPLETION_AT_2_lane0 <= execute_ctrl1_down_COMPLETION_AT_2_lane0;
      execute_ctrl2_up_COMPLETION_AT_4_lane0 <= execute_ctrl1_down_COMPLETION_AT_4_lane0;
      execute_ctrl2_up_COMPLETION_AT_3_lane0 <= execute_ctrl1_down_COMPLETION_AT_3_lane0;
      execute_ctrl2_up_lane0_logic_completions_onCtrl_0_ENABLE_lane0 <= execute_ctrl1_down_lane0_logic_completions_onCtrl_0_ENABLE_lane0;
      execute_ctrl2_up_lane0_logic_completions_onCtrl_1_ENABLE_lane0 <= execute_ctrl1_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0;
      execute_ctrl2_up_lane0_logic_completions_onCtrl_2_ENABLE_lane0 <= execute_ctrl1_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0;
      execute_ctrl2_up_early0_IntAluPlugin_ALU_ADD_SUB_lane0 <= execute_ctrl1_down_early0_IntAluPlugin_ALU_ADD_SUB_lane0;
      execute_ctrl2_up_early0_IntAluPlugin_ALU_SLTX_lane0 <= execute_ctrl1_down_early0_IntAluPlugin_ALU_SLTX_lane0;
      execute_ctrl2_up_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0 <= execute_ctrl1_down_early0_IntAluPlugin_ALU_BITWISE_CTRL_lane0;
      execute_ctrl2_up_SrcStageables_REVERT_lane0 <= execute_ctrl1_down_SrcStageables_REVERT_lane0;
      execute_ctrl2_up_SrcStageables_ZERO_lane0 <= execute_ctrl1_down_SrcStageables_ZERO_lane0;
      execute_ctrl2_up_lane0_IntFormatPlugin_logic_SIGNED_lane0 <= execute_ctrl1_down_lane0_IntFormatPlugin_logic_SIGNED_lane0;
      execute_ctrl2_up_lane0_IntFormatPlugin_logic_WIDTH_ID_lane0 <= execute_ctrl1_down_lane0_IntFormatPlugin_logic_WIDTH_ID_lane0;
      execute_ctrl2_up_BYPASSED_AT_3_lane0 <= execute_ctrl1_down_BYPASSED_AT_3_lane0;
      execute_ctrl2_up_SrcStageables_UNSIGNED_lane0 <= execute_ctrl1_down_SrcStageables_UNSIGNED_lane0;
      execute_ctrl2_up_BarrelShifterPlugin_LEFT_lane0 <= execute_ctrl1_down_BarrelShifterPlugin_LEFT_lane0;
      execute_ctrl2_up_BarrelShifterPlugin_SIGNED_lane0 <= execute_ctrl1_down_BarrelShifterPlugin_SIGNED_lane0;
      execute_ctrl2_up_BranchPlugin_BRANCH_CTRL_lane0 <= execute_ctrl1_down_BranchPlugin_BRANCH_CTRL_lane0;
      execute_ctrl2_up_MulPlugin_HIGH_lane0 <= execute_ctrl1_down_MulPlugin_HIGH_lane0;
      execute_ctrl2_up_RsUnsignedPlugin_RS1_SIGNED_lane0 <= execute_ctrl1_down_RsUnsignedPlugin_RS1_SIGNED_lane0;
      execute_ctrl2_up_RsUnsignedPlugin_RS2_SIGNED_lane0 <= execute_ctrl1_down_RsUnsignedPlugin_RS2_SIGNED_lane0;
      execute_ctrl2_up_DivPlugin_REM_lane0 <= execute_ctrl1_down_DivPlugin_REM_lane0;
      execute_ctrl2_up_CsrAccessPlugin_CSR_IMM_lane0 <= execute_ctrl1_down_CsrAccessPlugin_CSR_IMM_lane0;
      execute_ctrl2_up_CsrAccessPlugin_CSR_MASK_lane0 <= execute_ctrl1_down_CsrAccessPlugin_CSR_MASK_lane0;
      execute_ctrl2_up_CsrAccessPlugin_CSR_CLEAR_lane0 <= execute_ctrl1_down_CsrAccessPlugin_CSR_CLEAR_lane0;
      execute_ctrl2_up_AguPlugin_LOAD_lane0 <= execute_ctrl1_down_AguPlugin_LOAD_lane0;
      execute_ctrl2_up_AguPlugin_STORE_lane0 <= execute_ctrl1_down_AguPlugin_STORE_lane0;
      execute_ctrl2_up_AguPlugin_ATOMIC_lane0 <= execute_ctrl1_down_AguPlugin_ATOMIC_lane0;
      execute_ctrl2_up_AguPlugin_FLOAT_lane0 <= execute_ctrl1_down_AguPlugin_FLOAT_lane0;
      execute_ctrl2_up_LsuPlugin_logic_LSU_PREFETCH_lane0 <= execute_ctrl1_down_LsuPlugin_logic_LSU_PREFETCH_lane0;
      execute_ctrl2_up_early0_EnvPlugin_OP_lane0 <= execute_ctrl1_down_early0_EnvPlugin_OP_lane0;
      execute_ctrl2_up_late0_IntAluPlugin_ALU_ADD_SUB_lane0 <= execute_ctrl1_down_late0_IntAluPlugin_ALU_ADD_SUB_lane0;
      execute_ctrl2_up_late0_IntAluPlugin_ALU_SLTX_lane0 <= execute_ctrl1_down_late0_IntAluPlugin_ALU_SLTX_lane0;
      execute_ctrl2_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0 <= execute_ctrl1_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0;
      execute_ctrl2_up_late0_SrcPlugin_logic_SRC1_CTRL_lane0 <= execute_ctrl1_down_late0_SrcPlugin_logic_SRC1_CTRL_lane0;
      execute_ctrl2_up_late0_SrcPlugin_logic_SRC2_CTRL_lane0 <= execute_ctrl1_down_late0_SrcPlugin_logic_SRC2_CTRL_lane0;
    end
    if(execute_ctrl2_down_isReady) begin
      execute_ctrl3_up_Decode_UOP_lane0 <= execute_ctrl2_down_Decode_UOP_lane0;
      execute_ctrl3_up_Prediction_ALIGNED_JUMPED_lane0 <= execute_ctrl2_down_Prediction_ALIGNED_JUMPED_lane0;
      execute_ctrl3_up_Prediction_ALIGNED_JUMPED_PC_lane0 <= execute_ctrl2_down_Prediction_ALIGNED_JUMPED_PC_lane0;
      execute_ctrl3_up_PC_lane0 <= execute_ctrl2_down_PC_lane0;
      execute_ctrl3_up_TRAP_lane0 <= execute_ctrl2_down_TRAP_lane0;
      execute_ctrl3_up_Decode_UOP_ID_lane0 <= execute_ctrl2_down_Decode_UOP_ID_lane0;
      execute_ctrl3_up_RS1_PHYS_lane0 <= execute_ctrl2_down_RS1_PHYS_lane0;
      execute_ctrl3_up_RS2_PHYS_lane0 <= execute_ctrl2_down_RS2_PHYS_lane0;
      execute_ctrl3_up_RD_ENABLE_lane0 <= execute_ctrl2_down_RD_ENABLE_lane0;
      execute_ctrl3_up_RD_PHYS_lane0 <= execute_ctrl2_down_RD_PHYS_lane0;
      execute_ctrl3_up_COMPLETED_lane0 <= execute_ctrl2_down_COMPLETED_lane0;
      execute_ctrl3_up_AguPlugin_SIZE_lane0 <= execute_ctrl2_down_AguPlugin_SIZE_lane0;
      execute_ctrl3_up_integer_RS1_lane0 <= execute_ctrl2_down_integer_RS1_lane0;
      execute_ctrl3_up_integer_RS2_lane0 <= execute_ctrl2_down_integer_RS2_lane0;
      execute_ctrl3_up_early0_BranchPlugin_SEL_lane0 <= execute_ctrl2_down_early0_BranchPlugin_SEL_lane0;
      execute_ctrl3_up_early0_MulPlugin_SEL_lane0 <= execute_ctrl2_down_early0_MulPlugin_SEL_lane0;
      execute_ctrl3_up_early0_DivPlugin_SEL_lane0 <= execute_ctrl2_down_early0_DivPlugin_SEL_lane0;
      execute_ctrl3_up_late0_IntAluPlugin_SEL_lane0 <= execute_ctrl2_down_late0_IntAluPlugin_SEL_lane0;
      execute_ctrl3_up_late0_BarrelShifterPlugin_SEL_lane0 <= execute_ctrl2_down_late0_BarrelShifterPlugin_SEL_lane0;
      execute_ctrl3_up_late0_BranchPlugin_SEL_lane0 <= execute_ctrl2_down_late0_BranchPlugin_SEL_lane0;
      execute_ctrl3_up_CsrAccessPlugin_SEL_lane0 <= execute_ctrl2_down_CsrAccessPlugin_SEL_lane0;
      execute_ctrl3_up_AguPlugin_SEL_lane0 <= execute_ctrl2_down_AguPlugin_SEL_lane0;
      execute_ctrl3_up_LsuPlugin_logic_FENCE_lane0 <= execute_ctrl2_down_LsuPlugin_logic_FENCE_lane0;
      execute_ctrl3_up_lane0_integer_WriteBackPlugin_SEL_lane0 <= execute_ctrl2_down_lane0_integer_WriteBackPlugin_SEL_lane0;
      execute_ctrl3_up_COMPLETION_AT_4_lane0 <= execute_ctrl2_down_COMPLETION_AT_4_lane0;
      execute_ctrl3_up_COMPLETION_AT_3_lane0 <= execute_ctrl2_down_COMPLETION_AT_3_lane0;
      execute_ctrl3_up_lane0_logic_completions_onCtrl_1_ENABLE_lane0 <= execute_ctrl2_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0;
      execute_ctrl3_up_lane0_logic_completions_onCtrl_2_ENABLE_lane0 <= execute_ctrl2_down_lane0_logic_completions_onCtrl_2_ENABLE_lane0;
      execute_ctrl3_up_SrcStageables_REVERT_lane0 <= execute_ctrl2_down_SrcStageables_REVERT_lane0;
      execute_ctrl3_up_SrcStageables_ZERO_lane0 <= execute_ctrl2_down_SrcStageables_ZERO_lane0;
      execute_ctrl3_up_lane0_IntFormatPlugin_logic_SIGNED_lane0 <= execute_ctrl2_down_lane0_IntFormatPlugin_logic_SIGNED_lane0;
      execute_ctrl3_up_lane0_IntFormatPlugin_logic_WIDTH_ID_lane0 <= execute_ctrl2_down_lane0_IntFormatPlugin_logic_WIDTH_ID_lane0;
      execute_ctrl3_up_SrcStageables_UNSIGNED_lane0 <= execute_ctrl2_down_SrcStageables_UNSIGNED_lane0;
      execute_ctrl3_up_BarrelShifterPlugin_LEFT_lane0 <= execute_ctrl2_down_BarrelShifterPlugin_LEFT_lane0;
      execute_ctrl3_up_BarrelShifterPlugin_SIGNED_lane0 <= execute_ctrl2_down_BarrelShifterPlugin_SIGNED_lane0;
      execute_ctrl3_up_BranchPlugin_BRANCH_CTRL_lane0 <= execute_ctrl2_down_BranchPlugin_BRANCH_CTRL_lane0;
      execute_ctrl3_up_MulPlugin_HIGH_lane0 <= execute_ctrl2_down_MulPlugin_HIGH_lane0;
      execute_ctrl3_up_AguPlugin_LOAD_lane0 <= execute_ctrl2_down_AguPlugin_LOAD_lane0;
      execute_ctrl3_up_AguPlugin_STORE_lane0 <= execute_ctrl2_down_AguPlugin_STORE_lane0;
      execute_ctrl3_up_AguPlugin_ATOMIC_lane0 <= execute_ctrl2_down_AguPlugin_ATOMIC_lane0;
      execute_ctrl3_up_AguPlugin_FLOAT_lane0 <= execute_ctrl2_down_AguPlugin_FLOAT_lane0;
      execute_ctrl3_up_LsuPlugin_logic_LSU_PREFETCH_lane0 <= execute_ctrl2_down_LsuPlugin_logic_LSU_PREFETCH_lane0;
      execute_ctrl3_up_late0_IntAluPlugin_ALU_ADD_SUB_lane0 <= execute_ctrl2_down_late0_IntAluPlugin_ALU_ADD_SUB_lane0;
      execute_ctrl3_up_late0_IntAluPlugin_ALU_SLTX_lane0 <= execute_ctrl2_down_late0_IntAluPlugin_ALU_SLTX_lane0;
      execute_ctrl3_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0 <= execute_ctrl2_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0;
      execute_ctrl3_up_late0_SrcPlugin_logic_SRC1_CTRL_lane0 <= execute_ctrl2_down_late0_SrcPlugin_logic_SRC1_CTRL_lane0;
      execute_ctrl3_up_late0_SrcPlugin_logic_SRC2_CTRL_lane0 <= execute_ctrl2_down_late0_SrcPlugin_logic_SRC2_CTRL_lane0;
      execute_ctrl3_up_COMMIT_lane0 <= execute_ctrl2_down_COMMIT_lane0;
      execute_ctrl3_up_early0_SrcPlugin_ADD_SUB_lane0 <= execute_ctrl2_down_early0_SrcPlugin_ADD_SUB_lane0;
      execute_ctrl3_up_LsuL1_MIXED_ADDRESS_lane0 <= execute_ctrl2_down_LsuL1_MIXED_ADDRESS_lane0;
      execute_ctrl3_up_LsuL1Plugin_logic_BANK_BUSY_lane0 <= execute_ctrl2_down_LsuL1Plugin_logic_BANK_BUSY_lane0;
      execute_ctrl3_up_LsuL1Plugin_logic_EVENT_WRITE_VALID_lane0 <= execute_ctrl2_down_LsuL1Plugin_logic_EVENT_WRITE_VALID_lane0;
      execute_ctrl3_up_LsuL1Plugin_logic_EVENT_WRITE_ADDRESS_lane0 <= execute_ctrl2_down_LsuL1Plugin_logic_EVENT_WRITE_ADDRESS_lane0;
      execute_ctrl3_up_LsuL1Plugin_logic_EVENT_WRITE_MASK_lane0 <= execute_ctrl2_down_LsuL1Plugin_logic_EVENT_WRITE_MASK_lane0;
      execute_ctrl3_up_LsuL1Plugin_logic_lsu_rt0_SHARED_BYPASS_VALID_lane0 <= execute_ctrl2_down_LsuL1Plugin_logic_lsu_rt0_SHARED_BYPASS_VALID_lane0;
      execute_ctrl3_up_LsuL1Plugin_logic_lsu_rt0_SHARED_BYPASS_VALUE_lane0_dirty <= execute_ctrl2_down_LsuL1Plugin_logic_lsu_rt0_SHARED_BYPASS_VALUE_lane0_dirty;
      execute_ctrl3_up_early0_MulPlugin_logic_mul_VALUES_0_lane0 <= execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_0_lane0;
      execute_ctrl3_up_early0_MulPlugin_logic_mul_VALUES_1_lane0 <= execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_1_lane0;
      execute_ctrl3_up_early0_MulPlugin_logic_mul_VALUES_2_lane0 <= execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_2_lane0;
      execute_ctrl3_up_early0_MulPlugin_logic_mul_VALUES_3_lane0 <= execute_ctrl2_down_early0_MulPlugin_logic_mul_VALUES_3_lane0;
      execute_ctrl3_up_DivPlugin_DIV_RESULT_lane0 <= execute_ctrl2_down_DivPlugin_DIV_RESULT_lane0;
      execute_ctrl3_up_early0_BranchPlugin_pcCalc_PC_TRUE_lane0 <= execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_TRUE_lane0;
      execute_ctrl3_up_early0_BranchPlugin_pcCalc_PC_FALSE_lane0 <= execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_FALSE_lane0;
      execute_ctrl3_up_early0_BranchPlugin_pcCalc_PC_LAST_SLICE_lane0 <= execute_ctrl2_down_early0_BranchPlugin_pcCalc_PC_LAST_SLICE_lane0;
      execute_ctrl3_up_LsuPlugin_logic_FROM_ACCESS_lane0 <= execute_ctrl2_down_LsuPlugin_logic_FROM_ACCESS_lane0;
      execute_ctrl3_up_LsuL1_MASK_lane0 <= execute_ctrl2_down_LsuL1_MASK_lane0;
      execute_ctrl3_up_LsuL1_SIZE_lane0 <= execute_ctrl2_down_LsuL1_SIZE_lane0;
      execute_ctrl3_up_LsuL1_LOAD_lane0 <= execute_ctrl2_down_LsuL1_LOAD_lane0;
      execute_ctrl3_up_LsuL1_ATOMIC_lane0 <= execute_ctrl2_down_LsuL1_ATOMIC_lane0;
      execute_ctrl3_up_LsuL1_STORE_lane0 <= execute_ctrl2_down_LsuL1_STORE_lane0;
      execute_ctrl3_up_LsuL1_CLEAN_lane0 <= execute_ctrl2_down_LsuL1_CLEAN_lane0;
      execute_ctrl3_up_LsuL1_INVALID_lane0 <= execute_ctrl2_down_LsuL1_INVALID_lane0;
      execute_ctrl3_up_LsuL1_PREFETCH_lane0 <= execute_ctrl2_down_LsuL1_PREFETCH_lane0;
      execute_ctrl3_up_LsuL1_FLUSH_lane0 <= execute_ctrl2_down_LsuL1_FLUSH_lane0;
      execute_ctrl3_up_Decode_STORE_ID_lane0 <= execute_ctrl2_down_Decode_STORE_ID_lane0;
      execute_ctrl3_up_LsuPlugin_logic_FROM_LSU_lane0 <= execute_ctrl2_down_LsuPlugin_logic_FROM_LSU_lane0;
      execute_ctrl3_up_LsuPlugin_logic_FROM_PREFETCH_lane0 <= execute_ctrl2_down_LsuPlugin_logic_FROM_PREFETCH_lane0;
      execute_ctrl3_up_lane0_integer_WriteBackPlugin_logic_DATA_lane0 <= execute_ctrl2_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0;
    end
    if(execute_ctrl3_down_isReady) begin
      execute_ctrl4_up_Decode_UOP_lane0 <= execute_ctrl3_down_Decode_UOP_lane0;
      execute_ctrl4_up_Prediction_ALIGNED_JUMPED_lane0 <= execute_ctrl3_down_Prediction_ALIGNED_JUMPED_lane0;
      execute_ctrl4_up_Prediction_ALIGNED_JUMPED_PC_lane0 <= execute_ctrl3_down_Prediction_ALIGNED_JUMPED_PC_lane0;
      execute_ctrl4_up_PC_lane0 <= execute_ctrl3_down_PC_lane0;
      execute_ctrl4_up_TRAP_lane0 <= execute_ctrl3_down_TRAP_lane0;
      execute_ctrl4_up_Decode_UOP_ID_lane0 <= execute_ctrl3_down_Decode_UOP_ID_lane0;
      execute_ctrl4_up_RD_ENABLE_lane0 <= execute_ctrl3_down_RD_ENABLE_lane0;
      execute_ctrl4_up_RD_PHYS_lane0 <= execute_ctrl3_down_RD_PHYS_lane0;
      execute_ctrl4_up_COMPLETED_lane0 <= execute_ctrl3_down_COMPLETED_lane0;
      execute_ctrl4_up_AguPlugin_SIZE_lane0 <= execute_ctrl3_down_AguPlugin_SIZE_lane0;
      execute_ctrl4_up_integer_RS2_lane0 <= execute_ctrl3_down_integer_RS2_lane0;
      execute_ctrl4_up_early0_BranchPlugin_SEL_lane0 <= execute_ctrl3_down_early0_BranchPlugin_SEL_lane0;
      execute_ctrl4_up_early0_MulPlugin_SEL_lane0 <= execute_ctrl3_down_early0_MulPlugin_SEL_lane0;
      execute_ctrl4_up_late0_IntAluPlugin_SEL_lane0 <= execute_ctrl3_down_late0_IntAluPlugin_SEL_lane0;
      execute_ctrl4_up_late0_BarrelShifterPlugin_SEL_lane0 <= execute_ctrl3_down_late0_BarrelShifterPlugin_SEL_lane0;
      execute_ctrl4_up_late0_BranchPlugin_SEL_lane0 <= execute_ctrl3_down_late0_BranchPlugin_SEL_lane0;
      execute_ctrl4_up_AguPlugin_SEL_lane0 <= execute_ctrl3_down_AguPlugin_SEL_lane0;
      execute_ctrl4_up_LsuPlugin_logic_FENCE_lane0 <= execute_ctrl3_down_LsuPlugin_logic_FENCE_lane0;
      execute_ctrl4_up_lane0_integer_WriteBackPlugin_SEL_lane0 <= execute_ctrl3_down_lane0_integer_WriteBackPlugin_SEL_lane0;
      execute_ctrl4_up_COMPLETION_AT_4_lane0 <= execute_ctrl3_down_COMPLETION_AT_4_lane0;
      execute_ctrl4_up_lane0_logic_completions_onCtrl_1_ENABLE_lane0 <= execute_ctrl3_down_lane0_logic_completions_onCtrl_1_ENABLE_lane0;
      execute_ctrl4_up_SrcStageables_REVERT_lane0 <= execute_ctrl3_down_SrcStageables_REVERT_lane0;
      execute_ctrl4_up_SrcStageables_ZERO_lane0 <= execute_ctrl3_down_SrcStageables_ZERO_lane0;
      execute_ctrl4_up_lane0_IntFormatPlugin_logic_SIGNED_lane0 <= execute_ctrl3_down_lane0_IntFormatPlugin_logic_SIGNED_lane0;
      execute_ctrl4_up_lane0_IntFormatPlugin_logic_WIDTH_ID_lane0 <= execute_ctrl3_down_lane0_IntFormatPlugin_logic_WIDTH_ID_lane0;
      execute_ctrl4_up_SrcStageables_UNSIGNED_lane0 <= execute_ctrl3_down_SrcStageables_UNSIGNED_lane0;
      execute_ctrl4_up_BarrelShifterPlugin_LEFT_lane0 <= execute_ctrl3_down_BarrelShifterPlugin_LEFT_lane0;
      execute_ctrl4_up_BarrelShifterPlugin_SIGNED_lane0 <= execute_ctrl3_down_BarrelShifterPlugin_SIGNED_lane0;
      execute_ctrl4_up_BranchPlugin_BRANCH_CTRL_lane0 <= execute_ctrl3_down_BranchPlugin_BRANCH_CTRL_lane0;
      execute_ctrl4_up_MulPlugin_HIGH_lane0 <= execute_ctrl3_down_MulPlugin_HIGH_lane0;
      execute_ctrl4_up_AguPlugin_LOAD_lane0 <= execute_ctrl3_down_AguPlugin_LOAD_lane0;
      execute_ctrl4_up_AguPlugin_STORE_lane0 <= execute_ctrl3_down_AguPlugin_STORE_lane0;
      execute_ctrl4_up_AguPlugin_ATOMIC_lane0 <= execute_ctrl3_down_AguPlugin_ATOMIC_lane0;
      execute_ctrl4_up_AguPlugin_FLOAT_lane0 <= execute_ctrl3_down_AguPlugin_FLOAT_lane0;
      execute_ctrl4_up_LsuPlugin_logic_LSU_PREFETCH_lane0 <= execute_ctrl3_down_LsuPlugin_logic_LSU_PREFETCH_lane0;
      execute_ctrl4_up_late0_IntAluPlugin_ALU_ADD_SUB_lane0 <= execute_ctrl3_down_late0_IntAluPlugin_ALU_ADD_SUB_lane0;
      execute_ctrl4_up_late0_IntAluPlugin_ALU_SLTX_lane0 <= execute_ctrl3_down_late0_IntAluPlugin_ALU_SLTX_lane0;
      execute_ctrl4_up_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0 <= execute_ctrl3_down_late0_IntAluPlugin_ALU_BITWISE_CTRL_lane0;
      execute_ctrl4_up_COMMIT_lane0 <= execute_ctrl3_down_COMMIT_lane0;
      execute_ctrl4_up_LsuL1_MIXED_ADDRESS_lane0 <= execute_ctrl3_down_LsuL1_MIXED_ADDRESS_lane0;
      execute_ctrl4_up_early0_MulPlugin_logic_mul_VALUES_0_lane0 <= execute_ctrl3_down_early0_MulPlugin_logic_mul_VALUES_0_lane0;
      execute_ctrl4_up_early0_MulPlugin_logic_mul_VALUES_1_lane0 <= execute_ctrl3_down_early0_MulPlugin_logic_mul_VALUES_1_lane0;
      execute_ctrl4_up_early0_MulPlugin_logic_mul_VALUES_2_lane0 <= execute_ctrl3_down_early0_MulPlugin_logic_mul_VALUES_2_lane0;
      execute_ctrl4_up_early0_MulPlugin_logic_mul_VALUES_3_lane0 <= execute_ctrl3_down_early0_MulPlugin_logic_mul_VALUES_3_lane0;
      execute_ctrl4_up_early0_BranchPlugin_pcCalc_PC_TRUE_lane0 <= execute_ctrl3_down_early0_BranchPlugin_pcCalc_PC_TRUE_lane0;
      execute_ctrl4_up_early0_BranchPlugin_pcCalc_PC_FALSE_lane0 <= execute_ctrl3_down_early0_BranchPlugin_pcCalc_PC_FALSE_lane0;
      execute_ctrl4_up_early0_BranchPlugin_pcCalc_PC_LAST_SLICE_lane0 <= execute_ctrl3_down_early0_BranchPlugin_pcCalc_PC_LAST_SLICE_lane0;
      execute_ctrl4_up_LsuL1_MASK_lane0 <= execute_ctrl3_down_LsuL1_MASK_lane0;
      execute_ctrl4_up_LsuL1_SIZE_lane0 <= execute_ctrl3_down_LsuL1_SIZE_lane0;
      execute_ctrl4_up_LsuL1_LOAD_lane0 <= execute_ctrl3_down_LsuL1_LOAD_lane0;
      execute_ctrl4_up_LsuL1_ATOMIC_lane0 <= execute_ctrl3_down_LsuL1_ATOMIC_lane0;
      execute_ctrl4_up_LsuL1_STORE_lane0 <= execute_ctrl3_down_LsuL1_STORE_lane0;
      execute_ctrl4_up_LsuL1_CLEAN_lane0 <= execute_ctrl3_down_LsuL1_CLEAN_lane0;
      execute_ctrl4_up_LsuL1_INVALID_lane0 <= execute_ctrl3_down_LsuL1_INVALID_lane0;
      execute_ctrl4_up_LsuL1_PREFETCH_lane0 <= execute_ctrl3_down_LsuL1_PREFETCH_lane0;
      execute_ctrl4_up_LsuL1_FLUSH_lane0 <= execute_ctrl3_down_LsuL1_FLUSH_lane0;
      execute_ctrl4_up_Decode_STORE_ID_lane0 <= execute_ctrl3_down_Decode_STORE_ID_lane0;
      execute_ctrl4_up_LsuPlugin_logic_FROM_LSU_lane0 <= execute_ctrl3_down_LsuPlugin_logic_FROM_LSU_lane0;
      execute_ctrl4_up_LsuPlugin_logic_FROM_PREFETCH_lane0 <= execute_ctrl3_down_LsuPlugin_logic_FROM_PREFETCH_lane0;
      execute_ctrl4_up_lane0_integer_WriteBackPlugin_logic_DATA_lane0 <= execute_ctrl3_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0;
      execute_ctrl4_up_LsuL1Plugin_logic_SHARED_lane0_dirty <= execute_ctrl3_down_LsuL1Plugin_logic_SHARED_lane0_dirty;
      execute_ctrl4_up_LsuL1Plugin_logic_BANK_BUSY_REMAPPED_lane0 <= execute_ctrl3_down_LsuL1Plugin_logic_BANK_BUSY_REMAPPED_lane0;
      execute_ctrl4_up_LsuL1Plugin_logic_BANKS_MUXES_lane0_0 <= execute_ctrl3_down_LsuL1Plugin_logic_BANKS_MUXES_lane0_0;
      execute_ctrl4_up_LsuL1Plugin_logic_WRITE_TO_READ_HAZARDS_lane0 <= execute_ctrl3_down_LsuL1Plugin_logic_WRITE_TO_READ_HAZARDS_lane0;
      execute_ctrl4_up_LsuL1_PHYSICAL_ADDRESS_lane0 <= execute_ctrl3_down_LsuL1_PHYSICAL_ADDRESS_lane0;
      execute_ctrl4_up_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_loaded <= execute_ctrl3_down_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_loaded;
      execute_ctrl4_up_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_address <= execute_ctrl3_down_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_address;
      execute_ctrl4_up_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_fault <= execute_ctrl3_down_LsuL1Plugin_logic_WAYS_TAGS_lane0_0_fault;
      execute_ctrl4_up_LsuL1Plugin_logic_WAYS_HITS_lane0 <= execute_ctrl3_down_LsuL1Plugin_logic_WAYS_HITS_lane0;
      execute_ctrl4_up_early0_MulPlugin_logic_steps_0_adders_0_lane0 <= execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_0_lane0;
      execute_ctrl4_up_early0_MulPlugin_logic_steps_0_adders_1_lane0 <= execute_ctrl3_down_early0_MulPlugin_logic_steps_0_adders_1_lane0;
      execute_ctrl4_up_late0_SrcPlugin_SRC1_lane0 <= execute_ctrl3_down_late0_SrcPlugin_SRC1_lane0;
      execute_ctrl4_up_late0_SrcPlugin_SRC2_lane0 <= execute_ctrl3_down_late0_SrcPlugin_SRC2_lane0;
      execute_ctrl4_up_LsuPlugin_logic_onTrigger_HIT_lane0 <= execute_ctrl3_down_LsuPlugin_logic_onTrigger_HIT_lane0;
      execute_ctrl4_up_MMU_TRANSLATED_lane0 <= execute_ctrl3_down_MMU_TRANSLATED_lane0;
      execute_ctrl4_up_LsuPlugin_logic_preCtrl_MISS_ALIGNED_lane0 <= execute_ctrl3_down_LsuPlugin_logic_preCtrl_MISS_ALIGNED_lane0;
      execute_ctrl4_up_LsuPlugin_logic_onPma_CACHED_RSP_lane0_fault <= execute_ctrl3_down_LsuPlugin_logic_onPma_CACHED_RSP_lane0_fault;
      execute_ctrl4_up_LsuPlugin_logic_onPma_CACHED_RSP_lane0_io <= execute_ctrl3_down_LsuPlugin_logic_onPma_CACHED_RSP_lane0_io;
      execute_ctrl4_up_LsuPlugin_logic_onPma_IO_RSP_lane0_fault <= execute_ctrl3_down_LsuPlugin_logic_onPma_IO_RSP_lane0_fault;
      execute_ctrl4_up_LsuPlugin_logic_onPma_IO_RSP_lane0_io <= execute_ctrl3_down_LsuPlugin_logic_onPma_IO_RSP_lane0_io;
      execute_ctrl4_up_LsuPlugin_logic_onPma_IO_lane0 <= execute_ctrl3_down_LsuPlugin_logic_onPma_IO_lane0;
      execute_ctrl4_up_LsuPlugin_logic_onPma_FROM_LSU_MSB_FAILED_lane0 <= execute_ctrl3_down_LsuPlugin_logic_onPma_FROM_LSU_MSB_FAILED_lane0;
      execute_ctrl4_up_LsuPlugin_logic_MMU_PAGE_FAULT_lane0 <= execute_ctrl3_down_LsuPlugin_logic_MMU_PAGE_FAULT_lane0;
      execute_ctrl4_up_LsuPlugin_logic_MMU_FAILURE_lane0 <= execute_ctrl3_down_LsuPlugin_logic_MMU_FAILURE_lane0;
      execute_ctrl4_up_MMU_ACCESS_FAULT_lane0 <= execute_ctrl3_down_MMU_ACCESS_FAULT_lane0;
      execute_ctrl4_up_MMU_REFILL_lane0 <= execute_ctrl3_down_MMU_REFILL_lane0;
      execute_ctrl4_up_MMU_HAZARD_lane0 <= execute_ctrl3_down_MMU_HAZARD_lane0;
      execute_ctrl4_up_MMU_BYPASS_TRANSLATION_lane0 <= execute_ctrl3_down_MMU_BYPASS_TRANSLATION_lane0;
    end
    if(execute_ctrl4_down_isReady) begin
      execute_ctrl5_up_RD_ENABLE_lane0 <= execute_ctrl4_down_RD_ENABLE_lane0;
      execute_ctrl5_up_RD_PHYS_lane0 <= execute_ctrl4_down_RD_PHYS_lane0;
      execute_ctrl5_up_COMMIT_lane0 <= execute_ctrl4_down_COMMIT_lane0;
      execute_ctrl5_up_lane0_integer_WriteBackPlugin_logic_DATA_lane0 <= execute_ctrl4_down_lane0_integer_WriteBackPlugin_logic_DATA_lane0;
    end
    case(LsuPlugin_logic_flusher_stateReg)
      LsuPlugin_logic_flusher_CMD : begin
        if(when_LsuPlugin_l363) begin
          LsuPlugin_logic_flusher_waiter <= LsuL1_WRITEBACK_BUSY;
        end
      end
      LsuPlugin_logic_flusher_COMPLETION : begin
        LsuPlugin_logic_flusher_waiter <= (LsuPlugin_logic_flusher_waiter & LsuL1_WRITEBACK_BUSY);
      end
      default : begin
        LsuPlugin_logic_flusher_cmdCounter <= 5'h0;
      end
    endcase
    case(TrapPlugin_logic_harts_0_trap_fsm_stateReg)
      TrapPlugin_logic_harts_0_trap_fsm_RUNNING : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_PROCESS_1 : begin
        TrapPlugin_logic_harts_0_trap_fsm_triggerEbreakReg <= TrapPlugin_logic_harts_0_trap_fsm_triggerEbreak;
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVAL : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_TVEC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_TRAP_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_EPC : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_XRET_APPLY : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_JUMP : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_LSU_FLUSH : begin
      end
      TrapPlugin_logic_harts_0_trap_fsm_FETCH_FLUSH : begin
      end
      default : begin
      end
    endcase
    case(CsrAccessPlugin_logic_fsm_stateReg)
      CsrAccessPlugin_logic_fsm_READ : begin
        CsrAccessPlugin_logic_fsm_interface_aluInput <= CsrAccessPlugin_bus_read_toWriteBits;
        CsrAccessPlugin_logic_fsm_interface_csrValue <= CsrAccessPlugin_logic_fsm_readLogic_csrValue;
      end
      CsrAccessPlugin_logic_fsm_WRITE : begin
      end
      CsrAccessPlugin_logic_fsm_COMPLETION : begin
      end
      default : begin
        REG_CSR_1952 <= COMB_CSR_1952;
        REG_CSR_1953 <= COMB_CSR_1953;
        REG_CSR_1954 <= COMB_CSR_1954;
        REG_CSR_3857 <= COMB_CSR_3857;
        REG_CSR_3858 <= COMB_CSR_3858;
        REG_CSR_3859 <= COMB_CSR_3859;
        REG_CSR_3860 <= COMB_CSR_3860;
        REG_CSR_769 <= COMB_CSR_769;
        REG_CSR_768 <= COMB_CSR_768;
        REG_CSR_834 <= COMB_CSR_834;
        REG_CSR_836 <= COMB_CSR_836;
        REG_CSR_772 <= COMB_CSR_772;
        REG_CSR_PrivilegedPlugin_logic_readAnyWriteLegal_tvecFilter <= COMB_CSR_PrivilegedPlugin_logic_readAnyWriteLegal_tvecFilter;
        REG_CSR_PrivilegedPlugin_logic_readAnyWriteLegal_epcFilter <= COMB_CSR_PrivilegedPlugin_logic_readAnyWriteLegal_epcFilter;
        REG_CSR_CsrRamPlugin_csrMapper_selFilter <= COMB_CSR_CsrRamPlugin_csrMapper_selFilter;
        REG_CSR_CsrAccessPlugin_logic_trapNextOnWriteFilter <= COMB_CSR_CsrAccessPlugin_logic_trapNextOnWriteFilter;
      end
    endcase
  end


endmodule

module RegFileMem (
  input  wire          io_writes_0_valid,
  input  wire [4:0]    io_writes_0_address,
  input  wire [31:0]   io_writes_0_data,
  input  wire [15:0]   io_writes_0_uopId,
  input  wire          io_reads_0_valid,
  input  wire [4:0]    io_reads_0_address,
  output wire [31:0]   io_reads_0_data,
  input  wire          io_reads_1_valid,
  input  wire [4:0]    io_reads_1_address,
  output wire [31:0]   io_reads_1_data,
  input  wire          clk,
  input  wire          reset
);

  reg        [31:0]   asMem_ram_spinal_port1;
  reg        [31:0]   asMem_ram_spinal_port2;
  reg                 _zz_1;
  wire                conv_writes_0_valid;
  wire       [4:0]    conv_writes_0_payload_address;
  wire       [31:0]   conv_writes_0_payload_data;
  wire                conv_read_0_cmd_valid;
  wire       [4:0]    conv_read_0_cmd_payload;
  wire       [31:0]   conv_read_0_rsp;
  wire                conv_read_1_cmd_valid;
  wire       [4:0]    conv_read_1_cmd_payload;
  wire       [31:0]   conv_read_1_rsp;
  wire                asMem_writes_0_port_valid;
  wire       [4:0]    asMem_writes_0_port_payload_address;
  wire       [31:0]   asMem_writes_0_port_payload_data;
  wire                asMem_reads_0_sync_port_cmd_valid;
  wire       [4:0]    asMem_reads_0_sync_port_cmd_payload;
  wire       [31:0]   asMem_reads_0_sync_port_rsp;
  wire                asMem_reads_1_sync_port_cmd_valid;
  wire       [4:0]    asMem_reads_1_sync_port_cmd_payload;
  wire       [31:0]   asMem_reads_1_sync_port_rsp;
  reg [31:0] asMem_ram [0:31] /* verilator public */ ;

  always @(posedge clk) begin
    if(_zz_1) begin
      asMem_ram[asMem_writes_0_port_payload_address] <= asMem_writes_0_port_payload_data;
    end
  end

  always @(posedge clk) begin
    if(asMem_reads_0_sync_port_cmd_valid) begin
      asMem_ram_spinal_port1 <= asMem_ram[asMem_reads_0_sync_port_cmd_payload];
    end
  end

  always @(posedge clk) begin
    if(asMem_reads_1_sync_port_cmd_valid) begin
      asMem_ram_spinal_port2 <= asMem_ram[asMem_reads_1_sync_port_cmd_payload];
    end
  end

  always @(*) begin
    _zz_1 = 1'b0;
    if(asMem_writes_0_port_valid) begin
      _zz_1 = 1'b1;
    end
  end

  assign conv_writes_0_valid = io_writes_0_valid;
  assign conv_writes_0_payload_address = io_writes_0_address;
  assign conv_writes_0_payload_data = io_writes_0_data;
  assign conv_read_0_cmd_valid = io_reads_0_valid;
  assign conv_read_0_cmd_payload = io_reads_0_address;
  assign io_reads_0_data = conv_read_0_rsp;
  assign conv_read_1_cmd_valid = io_reads_1_valid;
  assign conv_read_1_cmd_payload = io_reads_1_address;
  assign io_reads_1_data = conv_read_1_rsp;
  assign asMem_writes_0_port_valid = conv_writes_0_valid;
  assign asMem_writes_0_port_payload_address = conv_writes_0_payload_address;
  assign asMem_writes_0_port_payload_data = conv_writes_0_payload_data;
  assign asMem_reads_0_sync_port_rsp = asMem_ram_spinal_port1;
  assign asMem_reads_0_sync_port_cmd_valid = conv_read_0_cmd_valid;
  assign asMem_reads_0_sync_port_cmd_payload = conv_read_0_cmd_payload;
  assign conv_read_0_rsp = asMem_reads_0_sync_port_rsp;
  assign asMem_reads_1_sync_port_rsp = asMem_ram_spinal_port2;
  assign asMem_reads_1_sync_port_cmd_valid = conv_read_1_cmd_valid;
  assign asMem_reads_1_sync_port_cmd_payload = conv_read_1_cmd_payload;
  assign conv_read_1_rsp = asMem_reads_1_sync_port_rsp;

endmodule

module StreamArbiter_3 (
  input  wire          io_inputs_0_valid,
  output wire          io_inputs_0_ready,
  input  wire [31:0]   io_inputs_0_payload_pcOnLastSlice,
  input  wire [31:0]   io_inputs_0_payload_pcTarget,
  input  wire          io_inputs_0_payload_taken,
  input  wire          io_inputs_0_payload_isBranch,
  input  wire          io_inputs_0_payload_isPush,
  input  wire          io_inputs_0_payload_isPop,
  input  wire          io_inputs_0_payload_wasWrong,
  input  wire          io_inputs_0_payload_badPredictedTarget,
  input  wire [15:0]   io_inputs_0_payload_uopId,
  output wire          io_output_valid,
  input  wire          io_output_ready,
  output wire [31:0]   io_output_payload_pcOnLastSlice,
  output wire [31:0]   io_output_payload_pcTarget,
  output wire          io_output_payload_taken,
  output wire          io_output_payload_isBranch,
  output wire          io_output_payload_isPush,
  output wire          io_output_payload_isPop,
  output wire          io_output_payload_wasWrong,
  output wire          io_output_payload_badPredictedTarget,
  output wire [15:0]   io_output_payload_uopId,
  output wire [0:0]    io_chosenOH,
  input  wire          clk,
  input  wire          reset
);

  wire       [1:0]    _zz__zz_maskProposal_0_2;
  wire       [1:0]    _zz__zz_maskProposal_0_2_1;
  wire       [0:0]    _zz__zz_maskProposal_0_2_2;
  wire       [0:0]    _zz_maskProposal_0_3;
  wire                locked;
  wire                maskProposal_0;
  reg                 maskLocked_0;
  wire                maskRouted_0;
  wire       [0:0]    _zz_maskProposal_0;
  wire       [1:0]    _zz_maskProposal_0_1;
  wire       [1:0]    _zz_maskProposal_0_2;

  assign _zz__zz_maskProposal_0_2 = (_zz_maskProposal_0_1 - _zz__zz_maskProposal_0_2_1);
  assign _zz__zz_maskProposal_0_2_2 = maskLocked_0;
  assign _zz__zz_maskProposal_0_2_1 = {1'd0, _zz__zz_maskProposal_0_2_2};
  assign _zz_maskProposal_0_3 = (_zz_maskProposal_0_2[1 : 1] | _zz_maskProposal_0_2[0 : 0]);
  assign locked = 1'b0;
  assign maskRouted_0 = (locked ? maskLocked_0 : maskProposal_0);
  assign _zz_maskProposal_0 = io_inputs_0_valid;
  assign _zz_maskProposal_0_1 = {_zz_maskProposal_0,_zz_maskProposal_0};
  assign _zz_maskProposal_0_2 = (_zz_maskProposal_0_1 & (~ _zz__zz_maskProposal_0_2));
  assign maskProposal_0 = _zz_maskProposal_0_3[0];
  assign io_output_valid = (io_inputs_0_valid && maskRouted_0);
  assign io_output_payload_pcOnLastSlice = io_inputs_0_payload_pcOnLastSlice;
  assign io_output_payload_pcTarget = io_inputs_0_payload_pcTarget;
  assign io_output_payload_taken = io_inputs_0_payload_taken;
  assign io_output_payload_isBranch = io_inputs_0_payload_isBranch;
  assign io_output_payload_isPush = io_inputs_0_payload_isPush;
  assign io_output_payload_isPop = io_inputs_0_payload_isPop;
  assign io_output_payload_wasWrong = io_inputs_0_payload_wasWrong;
  assign io_output_payload_badPredictedTarget = io_inputs_0_payload_badPredictedTarget;
  assign io_output_payload_uopId = io_inputs_0_payload_uopId;
  assign io_inputs_0_ready = (maskRouted_0 && io_output_ready);
  assign io_chosenOH = maskRouted_0;
  always @(posedge clk or posedge reset) begin
    if(reset) begin
      maskLocked_0 <= 1'b1;
    end else begin
      if(io_output_valid) begin
        maskLocked_0 <= maskRouted_0;
      end
    end
  end


endmodule

module StreamArbiter_2 (
  input  wire          io_inputs_0_valid,
  output wire          io_inputs_0_ready,
  input  wire [2:0]    io_inputs_0_payload_op,
  input  wire [31:0]   io_inputs_0_payload_address,
  input  wire [1:0]    io_inputs_0_payload_size,
  input  wire          io_inputs_0_payload_load,
  input  wire          io_inputs_0_payload_store,
  input  wire          io_inputs_0_payload_atomic,
  input  wire          io_inputs_0_payload_clean,
  input  wire          io_inputs_0_payload_invalidate,
  input  wire [11:0]   io_inputs_0_payload_storeId,
  input  wire          io_inputs_1_valid,
  output wire          io_inputs_1_ready,
  input  wire [2:0]    io_inputs_1_payload_op,
  input  wire [31:0]   io_inputs_1_payload_address,
  input  wire [1:0]    io_inputs_1_payload_size,
  input  wire          io_inputs_1_payload_load,
  input  wire          io_inputs_1_payload_store,
  input  wire          io_inputs_1_payload_atomic,
  input  wire          io_inputs_1_payload_clean,
  input  wire          io_inputs_1_payload_invalidate,
  input  wire [11:0]   io_inputs_1_payload_storeId,
  output wire          io_output_valid,
  input  wire          io_output_ready,
  output wire [2:0]    io_output_payload_op,
  output wire [31:0]   io_output_payload_address,
  output wire [1:0]    io_output_payload_size,
  output wire          io_output_payload_load,
  output wire          io_output_payload_store,
  output wire          io_output_payload_atomic,
  output wire          io_output_payload_clean,
  output wire          io_output_payload_invalidate,
  output wire [11:0]   io_output_payload_storeId,
  output wire [0:0]    io_chosen,
  output wire [1:0]    io_chosenOH,
  input  wire          clk,
  input  wire          reset
);
  localparam LsuL1CmdOpcode_LSU = 3'd0;
  localparam LsuL1CmdOpcode_ACCESS_1 = 3'd1;
  localparam LsuL1CmdOpcode_STORE_BUFFER = 3'd2;
  localparam LsuL1CmdOpcode_FLUSH = 3'd3;
  localparam LsuL1CmdOpcode_PREFETCH = 3'd4;

  wire       [1:0]    _zz_maskProposal_1_1;
  wire       [1:0]    _zz_maskProposal_1_2;
  wire                locked;
  wire                maskProposal_0;
  wire                maskProposal_1;
  reg                 maskLocked_0;
  reg                 maskLocked_1;
  wire                maskRouted_0;
  wire                maskRouted_1;
  wire       [1:0]    _zz_maskProposal_1;
  wire       [2:0]    _zz_io_output_payload_op;
  wire                _zz_io_chosen;
  `ifndef SYNTHESIS
  reg [95:0] io_inputs_0_payload_op_string;
  reg [95:0] io_inputs_1_payload_op_string;
  reg [95:0] io_output_payload_op_string;
  reg [95:0] _zz_io_output_payload_op_string;
  `endif


  assign _zz_maskProposal_1_1 = (_zz_maskProposal_1 & (~ _zz_maskProposal_1_2));
  assign _zz_maskProposal_1_2 = (_zz_maskProposal_1 - 2'b01);
  `ifndef SYNTHESIS
  always @(*) begin
    case(io_inputs_0_payload_op)
      LsuL1CmdOpcode_LSU : io_inputs_0_payload_op_string = "LSU         ";
      LsuL1CmdOpcode_ACCESS_1 : io_inputs_0_payload_op_string = "ACCESS_1    ";
      LsuL1CmdOpcode_STORE_BUFFER : io_inputs_0_payload_op_string = "STORE_BUFFER";
      LsuL1CmdOpcode_FLUSH : io_inputs_0_payload_op_string = "FLUSH       ";
      LsuL1CmdOpcode_PREFETCH : io_inputs_0_payload_op_string = "PREFETCH    ";
      default : io_inputs_0_payload_op_string = "????????????";
    endcase
  end
  always @(*) begin
    case(io_inputs_1_payload_op)
      LsuL1CmdOpcode_LSU : io_inputs_1_payload_op_string = "LSU         ";
      LsuL1CmdOpcode_ACCESS_1 : io_inputs_1_payload_op_string = "ACCESS_1    ";
      LsuL1CmdOpcode_STORE_BUFFER : io_inputs_1_payload_op_string = "STORE_BUFFER";
      LsuL1CmdOpcode_FLUSH : io_inputs_1_payload_op_string = "FLUSH       ";
      LsuL1CmdOpcode_PREFETCH : io_inputs_1_payload_op_string = "PREFETCH    ";
      default : io_inputs_1_payload_op_string = "????????????";
    endcase
  end
  always @(*) begin
    case(io_output_payload_op)
      LsuL1CmdOpcode_LSU : io_output_payload_op_string = "LSU         ";
      LsuL1CmdOpcode_ACCESS_1 : io_output_payload_op_string = "ACCESS_1    ";
      LsuL1CmdOpcode_STORE_BUFFER : io_output_payload_op_string = "STORE_BUFFER";
      LsuL1CmdOpcode_FLUSH : io_output_payload_op_string = "FLUSH       ";
      LsuL1CmdOpcode_PREFETCH : io_output_payload_op_string = "PREFETCH    ";
      default : io_output_payload_op_string = "????????????";
    endcase
  end
  always @(*) begin
    case(_zz_io_output_payload_op)
      LsuL1CmdOpcode_LSU : _zz_io_output_payload_op_string = "LSU         ";
      LsuL1CmdOpcode_ACCESS_1 : _zz_io_output_payload_op_string = "ACCESS_1    ";
      LsuL1CmdOpcode_STORE_BUFFER : _zz_io_output_payload_op_string = "STORE_BUFFER";
      LsuL1CmdOpcode_FLUSH : _zz_io_output_payload_op_string = "FLUSH       ";
      LsuL1CmdOpcode_PREFETCH : _zz_io_output_payload_op_string = "PREFETCH    ";
      default : _zz_io_output_payload_op_string = "????????????";
    endcase
  end
  `endif

  assign locked = 1'b0;
  assign maskRouted_0 = (locked ? maskLocked_0 : maskProposal_0);
  assign maskRouted_1 = (locked ? maskLocked_1 : maskProposal_1);
  assign _zz_maskProposal_1 = {io_inputs_1_valid,io_inputs_0_valid};
  assign maskProposal_0 = io_inputs_0_valid;
  assign maskProposal_1 = _zz_maskProposal_1_1[1];
  assign io_output_valid = ((io_inputs_0_valid && maskRouted_0) || (io_inputs_1_valid && maskRouted_1));
  assign _zz_io_output_payload_op = (maskRouted_0 ? io_inputs_0_payload_op : io_inputs_1_payload_op);
  assign io_output_payload_op = _zz_io_output_payload_op;
  assign io_output_payload_address = (maskRouted_0 ? io_inputs_0_payload_address : io_inputs_1_payload_address);
  assign io_output_payload_size = (maskRouted_0 ? io_inputs_0_payload_size : io_inputs_1_payload_size);
  assign io_output_payload_load = (maskRouted_0 ? io_inputs_0_payload_load : io_inputs_1_payload_load);
  assign io_output_payload_store = (maskRouted_0 ? io_inputs_0_payload_store : io_inputs_1_payload_store);
  assign io_output_payload_atomic = (maskRouted_0 ? io_inputs_0_payload_atomic : io_inputs_1_payload_atomic);
  assign io_output_payload_clean = (maskRouted_0 ? io_inputs_0_payload_clean : io_inputs_1_payload_clean);
  assign io_output_payload_invalidate = (maskRouted_0 ? io_inputs_0_payload_invalidate : io_inputs_1_payload_invalidate);
  assign io_output_payload_storeId = (maskRouted_0 ? io_inputs_0_payload_storeId : io_inputs_1_payload_storeId);
  assign io_inputs_0_ready = (maskRouted_0 && io_output_ready);
  assign io_inputs_1_ready = (maskRouted_1 && io_output_ready);
  assign io_chosenOH = {maskRouted_1,maskRouted_0};
  assign _zz_io_chosen = io_chosenOH[1];
  assign io_chosen = _zz_io_chosen;
  always @(posedge clk) begin
    if(io_output_valid) begin
      maskLocked_0 <= maskRouted_0;
      maskLocked_1 <= maskRouted_1;
    end
  end


endmodule

module StreamArbiter_1 (
  input  wire          io_inputs_0_valid,
  output wire          io_inputs_0_ready,
  output wire          io_output_valid,
  input  wire          io_output_ready,
  output wire [0:0]    io_chosenOH,
  input  wire          clk,
  input  wire          reset
);

  reg                 locked;
  wire                maskProposal_0;
  reg                 maskLocked_0;
  wire                maskRouted_0;
  wire                io_output_fire;

  assign maskRouted_0 = (locked ? maskLocked_0 : maskProposal_0);
  assign maskProposal_0 = io_inputs_0_valid;
  assign io_output_fire = (io_output_valid && io_output_ready);
  assign io_output_valid = (io_inputs_0_valid && maskRouted_0);
  assign io_inputs_0_ready = (maskRouted_0 && io_output_ready);
  assign io_chosenOH = maskRouted_0;
  always @(posedge clk or posedge reset) begin
    if(reset) begin
      locked <= 1'b0;
    end else begin
      if(io_output_valid) begin
        locked <= 1'b1;
      end
      if(io_output_fire) begin
        locked <= 1'b0;
      end
    end
  end

  always @(posedge clk) begin
    if(io_output_valid) begin
      maskLocked_0 <= maskRouted_0;
    end
  end


endmodule

module StreamArbiter (
  input  wire          io_inputs_0_valid,
  output wire          io_inputs_0_ready,
  input  wire          io_inputs_0_payload_last,
  input  wire          io_inputs_0_payload_fragment_write,
  input  wire [31:0]   io_inputs_0_payload_fragment_address,
  input  wire          io_inputs_1_valid,
  output wire          io_inputs_1_ready,
  input  wire          io_inputs_1_payload_last,
  input  wire          io_inputs_1_payload_fragment_write,
  input  wire [31:0]   io_inputs_1_payload_fragment_address,
  output wire          io_output_valid,
  input  wire          io_output_ready,
  output wire          io_output_payload_last,
  output wire          io_output_payload_fragment_write,
  output wire [31:0]   io_output_payload_fragment_address,
  output wire [0:0]    io_chosen,
  output wire [1:0]    io_chosenOH,
  input  wire          clk,
  input  wire          reset
);

  wire       [1:0]    _zz_maskProposal_1_1;
  wire       [1:0]    _zz_maskProposal_1_2;
  reg                 locked;
  wire                maskProposal_0;
  wire                maskProposal_1;
  reg                 maskLocked_0;
  reg                 maskLocked_1;
  wire                maskRouted_0;
  wire                maskRouted_1;
  wire       [1:0]    _zz_maskProposal_1;
  wire                io_output_fire;
  wire                when_Stream_l710;
  wire                _zz_io_chosen;

  assign _zz_maskProposal_1_1 = (_zz_maskProposal_1 & (~ _zz_maskProposal_1_2));
  assign _zz_maskProposal_1_2 = (_zz_maskProposal_1 - 2'b01);
  assign maskRouted_0 = (locked ? maskLocked_0 : maskProposal_0);
  assign maskRouted_1 = (locked ? maskLocked_1 : maskProposal_1);
  assign _zz_maskProposal_1 = {io_inputs_1_valid,io_inputs_0_valid};
  assign maskProposal_0 = io_inputs_0_valid;
  assign maskProposal_1 = _zz_maskProposal_1_1[1];
  assign io_output_fire = (io_output_valid && io_output_ready);
  assign when_Stream_l710 = (io_output_fire && io_output_payload_last);
  assign io_output_valid = ((io_inputs_0_valid && maskRouted_0) || (io_inputs_1_valid && maskRouted_1));
  assign io_output_payload_last = (maskRouted_0 ? io_inputs_0_payload_last : io_inputs_1_payload_last);
  assign io_output_payload_fragment_write = (maskRouted_0 ? io_inputs_0_payload_fragment_write : io_inputs_1_payload_fragment_write);
  assign io_output_payload_fragment_address = (maskRouted_0 ? io_inputs_0_payload_fragment_address : io_inputs_1_payload_fragment_address);
  assign io_inputs_0_ready = (maskRouted_0 && io_output_ready);
  assign io_inputs_1_ready = (maskRouted_1 && io_output_ready);
  assign io_chosenOH = {maskRouted_1,maskRouted_0};
  assign _zz_io_chosen = io_chosenOH[1];
  assign io_chosen = _zz_io_chosen;
  always @(posedge clk or posedge reset) begin
    if(reset) begin
      locked <= 1'b0;
    end else begin
      if(io_output_valid) begin
        locked <= 1'b1;
      end
      if(when_Stream_l710) begin
        locked <= 1'b0;
      end
    end
  end

  always @(posedge clk) begin
    if(io_output_valid) begin
      maskLocked_0 <= maskRouted_0;
      maskLocked_1 <= maskRouted_1;
    end
  end


endmodule

module DivRadix (
  input  wire          io_flush,
  input  wire          io_cmd_valid,
  output wire          io_cmd_ready,
  input  wire [31:0]   io_cmd_payload_a,
  input  wire [31:0]   io_cmd_payload_b,
  input  wire          io_cmd_payload_normalized,
  input  wire [4:0]    io_cmd_payload_iterations,
  output wire          io_rsp_valid,
  input  wire          io_rsp_ready,
  output wire [31:0]   io_rsp_payload_result,
  output wire [31:0]   io_rsp_payload_remain,
  input  wire          clk,
  input  wire          reset
);

  wire       [7:0]    _zz_shifter_1;
  wire       [15:0]   _zz_shifter_2;
  wire       [23:0]   _zz_shifter_3;
  wire       [30:0]   _zz_shifter_4;
  reg        [4:0]    counter;
  reg                 busy;
  wire                io_rsp_fire;
  reg                 done;
  wire                when_DivRadix_l45;
  reg        [31:0]   shifter;
  reg        [31:0]   numerator;
  reg        [31:0]   result;
  reg        [32:0]   div1;
  reg        [32:0]   div3;
  wire       [32:0]   div2;
  wire       [32:0]   shifted;
  wire       [33:0]   sub1;
  wire                when_DivRadix_l64;
  reg        [32:0]   _zz_shifter;
  wire                when_DivRadix_l68;
  wire                slicesZero_0;
  wire                slicesZero_1;
  wire                slicesZero_2;
  wire       [2:0]    shiftSel;
  wire       [3:0]    _zz_sel;
  wire                _zz_sel_1;
  wire                _zz_sel_2;
  wire                _zz_sel_3;
  reg        [3:0]    _zz_sel_4;
  wire       [3:0]    _zz_sel_5;
  wire                _zz_sel_6;
  wire                _zz_sel_7;
  wire                _zz_sel_8;
  wire       [1:0]    sel;
  reg                 wasBusy;
  wire                when_DivRadix_l93;

  assign _zz_shifter_1 = io_cmd_payload_a[31 : 24];
  assign _zz_shifter_2 = io_cmd_payload_a[31 : 16];
  assign _zz_shifter_3 = io_cmd_payload_a[31 : 8];
  assign _zz_shifter_4 = io_cmd_payload_a[31 : 1];
  assign io_rsp_fire = (io_rsp_valid && io_rsp_ready);
  assign when_DivRadix_l45 = (busy && (counter == 5'h1f));
  assign div2 = (div1 <<< 1);
  assign shifted = {shifter,numerator[31 : 31]};
  assign sub1 = ({1'b0,shifted} - {1'b0,div1});
  assign io_rsp_valid = done;
  assign io_rsp_payload_result = result;
  assign io_rsp_payload_remain = shifter;
  assign io_cmd_ready = (! busy);
  assign when_DivRadix_l64 = (! done);
  always @(*) begin
    _zz_shifter = shifted;
    if(when_DivRadix_l68) begin
      _zz_shifter = sub1[32:0];
    end
  end

  assign when_DivRadix_l68 = (! sub1[33]);
  assign slicesZero_0 = (io_cmd_payload_a[15 : 8] == 8'h0);
  assign slicesZero_1 = (io_cmd_payload_a[23 : 16] == 8'h0);
  assign slicesZero_2 = (io_cmd_payload_a[31 : 24] == 8'h0);
  assign shiftSel = {(&slicesZero_2),{(&{slicesZero_2,slicesZero_1}),(&{slicesZero_2,{slicesZero_1,slicesZero_0}})}};
  assign _zz_sel = {1'b1,shiftSel};
  assign _zz_sel_1 = _zz_sel[0];
  assign _zz_sel_2 = _zz_sel[1];
  assign _zz_sel_3 = _zz_sel[2];
  always @(*) begin
    _zz_sel_4[0] = (_zz_sel_1 && (! 1'b0));
    _zz_sel_4[1] = (_zz_sel_2 && (! _zz_sel_1));
    _zz_sel_4[2] = (_zz_sel_3 && (! (|{_zz_sel_2,_zz_sel_1})));
    _zz_sel_4[3] = (_zz_sel[3] && (! (|{_zz_sel_3,{_zz_sel_2,_zz_sel_1}})));
  end

  assign _zz_sel_5 = _zz_sel_4;
  assign _zz_sel_6 = _zz_sel_5[3];
  assign _zz_sel_7 = (_zz_sel_5[1] || _zz_sel_6);
  assign _zz_sel_8 = (_zz_sel_5[2] || _zz_sel_6);
  assign sel = {_zz_sel_8,_zz_sel_7};
  assign when_DivRadix_l93 = (! busy);
  always @(posedge clk or posedge reset) begin
    if(reset) begin
      busy <= 1'b0;
      done <= 1'b0;
      wasBusy <= 1'b0;
    end else begin
      if(io_rsp_fire) begin
        busy <= 1'b0;
      end
      if(when_DivRadix_l45) begin
        done <= 1'b1;
      end
      if(io_rsp_fire) begin
        done <= 1'b0;
      end
      wasBusy <= busy;
      if(when_DivRadix_l93) begin
        busy <= io_cmd_valid;
      end
      if(io_flush) begin
        done <= 1'b0;
        busy <= 1'b0;
      end
    end
  end

  always @(posedge clk) begin
    if(when_DivRadix_l64) begin
      counter <= (counter + 5'h01);
      result <= (result <<< 1);
      if(when_DivRadix_l68) begin
        result[0 : 0] <= 1'b1;
      end
      shifter <= _zz_shifter[31:0];
      numerator <= (numerator <<< 1);
    end
    if(when_DivRadix_l93) begin
      div1 <= {1'd0, io_cmd_payload_b};
      result <= ((io_cmd_payload_b == 32'h0) ? 32'hffffffff : 32'h0);
      case(sel)
        2'b11 : begin
          counter <= 5'h0;
          shifter <= 32'h0;
          numerator <= (io_cmd_payload_a <<< 0);
        end
        2'b10 : begin
          counter <= 5'h08;
          shifter <= {24'd0, _zz_shifter_1};
          numerator <= (io_cmd_payload_a <<< 8);
        end
        2'b01 : begin
          counter <= 5'h10;
          shifter <= {16'd0, _zz_shifter_2};
          numerator <= (io_cmd_payload_a <<< 16);
        end
        default : begin
          counter <= 5'h18;
          shifter <= {8'd0, _zz_shifter_3};
          numerator <= (io_cmd_payload_a <<< 24);
        end
      endcase
      if(io_cmd_payload_normalized) begin
        counter <= (5'h1f - io_cmd_payload_iterations);
        shifter <= {1'd0, _zz_shifter_4};
        numerator <= (io_cmd_payload_a <<< 31);
      end
    end
  end


endmodule
