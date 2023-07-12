//
// Project: CYBORG65R2
// Block:   CYBORG65R2_DIGITAL_TOP
// $Author: anthony.wall $
// $Date: 2023/01/29 20:47:22 GMT $
// $Revision: 9 $
// 
// 
//


`timescale 1ns/1ps

module cyborg65r2_digital_top (
		clk_rs,
		clk_8rs,
		resetb,
		pulse_in,
		count_enc,
		scl,
		sda_in,
                sda_out,
		d_out,
		clk_out,
		clk_rs_div,
		aux_pin_out,
		output_drive_strength,
		i2c_pullup_enable,
		cco_enable,
		afe_enable,
                afe_bias_fvf_current,
		afe_bias_gb_current
		);



// ------------------
// Inputs and Outputs
// ------------------


  input		clk_rs;			// clk running at 1x the resampling rate
  input		clk_8rs;		// clk running at 8x the sampling rate
  input		resetb;			// global asynchronous reset
  input		pulse_in;		// nonunirom clock
  input	 [11:0]	count_enc;		// input data [11:0] from encoder block
  input 	scl;			// I2C Clock
  input		sda_in;			// I2C Data In
  output	sda_out;		// I2C Data Out

  output [18:0] d_out;			// Main DSP output data
  output	clk_out;		// output clk DSP data is sampled on

  output  [7:0]	clk_rs_div;		// CLK_RS Divider (i2c register map address 0)
  output [11:0]	aux_pin_out;		// Debug
  output   	output_drive_strength;	// Debug control
  output   	i2c_pullup_enable;	// Debug control
//  output   	tq_enable;		// Power control
  output   	cco_enable;		// Power control
  output   	afe_enable;		// Power control
  //output  [4:0]	afe_bias_current_cntl;	// AFE control
  output	afe_bias_fvf_current;	//Power control
  output	afe_bias_gb_current;	//Power control




// ---------------------
// Variable Declarations
// ---------------------

  wire   [98:0] data_out_lumped;	// 8 samples (8*12-bit) + nsamp (3-bit)

  wire   [18:0] d_out;			// filtered and resampled output, posedge sampled
  wire		clk_out;		// clk to which d_out is synchronised

  wire		sram_zm3_en;
  wire		sram_zm2_en;
  wire		sram_zm1_en;
  wire		sram_zm0_en;
  wire	  [1:0]	sram_sel;
  wire		sram_write_en;
  wire		sram_read_en;
  wire	 [11:0]	sram_addr;
  wire	 [15:0]	sram_wdata;
  wire	 [15:0]	sram_rdata;
  wire		start_ram_wr;
  wire		start_ram_rd;
  wire		ram_rd_done;
  wire		ram_wr_done;
  wire	 [11:0]	config_t_rs_lsb;

  wire    [7:0]	lsb_corr;		// Nonlinearity Correction
  wire    [2:0]	aux_pin_out_control;	// Nonlinearity Correction

  wire    [7:0] reg_24_r;
  wire    [7:0] reg_25_r;
  wire    [7:0] reg_26_r;
  wire    [7:0] reg_27_r;
  wire    [7:0] reg_28_r;
  wire    [7:0] reg_29_r;
  wire    [7:0] reg_30_r;
  wire    [7:0] reg_31_r;
  wire    [7:0] reg_00_w;
  wire    [7:0] reg_01_w;
  wire    [7:0] reg_02_w;
  wire    [7:0] reg_03_w;
  wire    [7:0] reg_04_w;
  wire    [7:0] reg_05_w;
  wire    [7:0] reg_06_w;
  wire    [7:0] reg_07_w;
  wire    [7:0] reg_08_w;
  wire    [7:0] reg_09_w;
  wire    [7:0] reg_10_w;
  wire    [7:0] reg_11_w;
  wire    [7:0] reg_12_w;
  wire    [7:0] reg_13_w;
  wire    [7:0] reg_14_w;
  wire    [7:0] reg_15_w;
  wire    [7:0] reg_16_w;
  wire    [7:0] reg_17_w;
  wire    [7:0] reg_18_w;
  wire    [7:0] reg_19_w;
  wire    [7:0] reg_20_w;
  wire    [7:0] reg_21_w;
  wire    [7:0] reg_22_w;
  wire    [7:0] reg_23_w;
  wire		reg_00_write;
  wire		reg_01_write;
  wire		reg_02_write;
  wire		reg_03_write;
  wire		reg_04_write;
  wire		reg_05_write;
  wire		reg_06_write;
  wire		reg_07_write;
  wire		reg_08_write;
  wire		reg_09_write;
  wire		reg_10_write;
  wire		reg_11_write;
  wire		reg_12_write;
  wire		reg_13_write;
  wire		reg_14_write;
  wire		reg_15_write;
  wire		reg_16_write;
  wire		reg_17_write;
  wire		reg_18_write;
  wire		reg_19_write;
  wire		reg_20_write;
  wire		reg_21_write;
  wire		reg_22_write;
  wire		reg_23_write;


  wire    [7:0]	status_reg_0;		// read-only register 0  (i2c register map address 24)
  wire    [7:0]	status_reg_1;		// read-only register 1  (i2c register map address 25)
  wire    [7:0]	status_reg_2;		// read-only register 2  (i2c register map address 26)
  wire    [7:0]	status_reg_3;		// read-only register 3  (i2c register map address 27)
  wire    [7:0]	status_reg_4;		// read-only register 4  (i2c register map address 28)
  wire    [7:0]	status_reg_5;		// read-only register 5  (i2c register map address 29)
  wire    [7:0]	status_reg_6;		// read-only register 6  (i2c register map address 30)
  wire    [7:0]	status_reg_7;		// read-only register 7  (i2c register map address 31)

  wire    [7:0]	config_reg_0;		// read-write register 0  (i2c register map address 0)
  wire    [7:0]	config_reg_1;		// read-write register 1  (i2c register map address 1)
  wire    [7:0]	config_reg_2;		// read-write register 2  (i2c register map address 2)
  wire    [7:0]	config_reg_3;		// read-write register 3  (i2c register map address 3)
  wire    [7:0]	config_reg_4;		// read-write register 4  (i2c register map address 4)
  wire    [7:0]	config_reg_5;		// read-write register 5  (i2c register map address 5)
  wire    [7:0]	config_reg_6;		// read-write register 6  (i2c register map address 6)
  wire    [7:0]	config_reg_7;		// read-write register 7  (i2c register map address 7)
  wire    [7:0]	config_reg_8;		// read-write register 8  (i2c register map address 8)
  wire    [7:0]	config_reg_9;		// read-write register 9  (i2c register map address 9)
  wire    [7:0]	config_reg_10;		// read-write register 10 (i2c register map address 10)
  wire    [7:0]	config_reg_11;		// read-write register 11 (i2c register map address 11)
  wire    [7:0]	config_reg_12;		// read-write register 12 (i2c register map address 12)
  wire    [7:0]	config_reg_13;		// read-write register 13 (i2c register map address 13)
  wire    [7:0]	config_reg_14;		// read-write register 14 (i2c register map address 14)
  wire    [7:0]	config_reg_15;		// read-write register 15 (i2c register map address 15)
  wire    [7:0]	config_reg_16;		// read-write register 16 (i2c register map address 16)
  wire    [7:0]	config_reg_17;		// read-write register 17 (i2c register map address 17)
  wire    [7:0]	config_reg_18;		// read-write register 18 (i2c register map address 18)
  wire    [7:0]	config_reg_19;		// read-write register 19 (i2c register map address 19)
  wire    [7:0]	config_reg_20;		// read-write register 20 (i2c register map address 20)
  wire    [7:0]	config_reg_21;		// read-write register 21 (i2c register map address 21)
  wire    [7:0]	config_reg_22;		// read-write register 22 (i2c register map address 22)
  wire    [7:0]	config_reg_23;		// read-write register 23 (i2c register map address 23)

  wire	 [11:0]	times_in_array [0:7];	// Accepting up to 8 12-bit time words, arranged in ascending order according to when they occured, previously negedge sampled

  wire		reg_06_read;

  wire	 [11:0]	nusdsp_sram_addr;
  wire	 [15:0]	nusdsp_sram_data_zm0;
  wire	 [15:0]	nusdsp_sram_data_zm1;
  wire	 [15:0]	nusdsp_sram_data_zm2;
  wire	 [15:0]	nusdsp_sram_data_zm3;



// probably also need these signals....
//    .ram_rd_done	(ram_rd_done),
//    .ram_wr_done	(ram_wr_done)



// ----------------
// Wire Assignments
// ----------------

  assign sram_zm3_en		= config_reg_7[7];
  assign sram_zm2_en		= config_reg_7[6];
  assign sram_zm1_en		= config_reg_7[5];
  assign sram_zm0_en		= config_reg_7[4];
  assign sram_sel		= config_reg_7[3:2];
  assign sram_write_en		= config_reg_7[1];
  assign sram_read_en		= config_reg_7[0];

  assign sram_addr[11:8]	= config_reg_8[3:0];
  assign sram_addr[7:0]		= config_reg_9;
  assign sram_wdata[15:8]	= config_reg_10;
  assign sram_wdata[7:0]	= config_reg_11;

  assign config_t_rs_lsb[11:8]	= config_reg_14[3:0];
  assign config_t_rs_lsb[7:0]	= config_reg_15;

  assign status_reg_0		= sram_rdata[15:8];		//**** need to move these to addresses 12+13????
  assign status_reg_1		= sram_rdata[7:0];



  assign times_in_array[7]	= data_out_lumped[98:87];
  assign times_in_array[6]	= data_out_lumped[86:75];
  assign times_in_array[5]	= data_out_lumped[74:63];
  assign times_in_array[4]	= data_out_lumped[62:51];
  assign times_in_array[3]	= data_out_lumped[50:39];
  assign times_in_array[2]	= data_out_lumped[38:27];
  assign times_in_array[1]	= data_out_lumped[26:15];
  assign times_in_array[0]	= data_out_lumped[14:3];



					//**** need to add stuff for ram read data registers 12+13....and make them read-only






// ------------------
// Output Assignments
// ------------------

  assign clk_rs_div 		= config_reg_0;
  assign lsb_corr		= config_reg_1;
  assign aux_pin_out_control	= config_reg_2[7:5];
  assign output_drive_strength	= config_reg_2[4];
  assign i2c_pullup_enable	= config_reg_2[3];
//  assign cco_pulse_out_en	= config_reg_2[2];
//  assign nusdsp_enable	= config_reg_3[7];
//  assign fifo_enable		= config_reg_3[6];
//  assign encoder_enable	= config_reg_3[5];
//  assign enc_coarse_enable	= config_reg_3[4];
//  assign tq_enable		= config_reg_3[3];
//  assign saff_enable		= config_reg_3[2];
  assign cco_enable		= config_reg_3[1];
  assign afe_enable		= config_reg_3[0];
 // assign afe_bias_current_cntl	= config_reg_4[4:0];
  assign afe_bias_fvf_current	= config_reg_4[0];
  assign afe_bias_gb_current	= config_reg_4[1];
  //  assign cco_cl_cntl		= config_reg_4[2:0];
//  assign chan_sel		= config_reg_5[7:3];

					//**** need to add stuff for status register 6....and make it read-only

  //assign aux_pin_out		= count_enc;
assign aux_pin_out = (aux_pin_out_control[0] == 1'b1)? count_enc : 12'b0;



// ------------------------
// Component Instantiations
// ------------------------

  // FIFO
  asyncfifo #(.fifo_depth(8), .bit_cnt(3), .word_size(12), .output_width(99)) i_asyncfifo(
    .pulse_in		(pulse_in),
    .data_in		(count_enc),
    .clk_in		(clk_rs),
    .resetb		(resetb),
    .data_out_lumped	(data_out_lumped)
    );


  // NUSDSP
  cyborg65r2_nusdsp i_cyborg65r2_nusdsp(
    .clk_rs		(clk_rs),
    .clk_8rs		(clk_8rs),
    .resetb		(resetb),
    .config_t_rs_lsb	(config_t_rs_lsb),
    .config_lsb_corr	(lsb_corr),
//    .times_in		(data_out_lumped[98:3]),
    .times_in		(times_in_array[0:7]),
    .n_nus		(data_out_lumped[2:0]),
    .sram_addr		(nusdsp_sram_addr),
    .sram_data_zm0	(nusdsp_sram_data_zm0),
    .sram_data_zm1	(nusdsp_sram_data_zm1),
    .sram_data_zm2	(nusdsp_sram_data_zm2),
    .sram_data_zm3	(nusdsp_sram_data_zm3),
    .d_out		(d_out),
    .clk_out		(clk_out)
    );



  // Memory
  cyborg65r2_memory i_cyborg65r2_memory(
    .clk_8rs			(clk_8rs),
    .resetb			(resetb),

    .sram_zm3_en		(sram_zm3_en),
    .sram_zm2_en		(sram_zm2_en),
    .sram_zm1_en		(sram_zm1_en),
    .sram_zm0_en		(sram_zm0_en),
    .sram_sel			(sram_sel),
    .sram_write_en		(sram_write_en),
    .sram_read_en		(sram_read_en),
    .sram_addr			(sram_addr),
    .sram_wdata			(sram_wdata),
    .sram_rdata			(sram_rdata),

    .nusdsp_sram_addr		(nusdsp_sram_addr),
    .nusdsp_sram_data_zm0	(nusdsp_sram_data_zm0),
    .nusdsp_sram_data_zm1	(nusdsp_sram_data_zm1),
    .nusdsp_sram_data_zm2	(nusdsp_sram_data_zm2),
    .nusdsp_sram_data_zm3	(nusdsp_sram_data_zm3),

    .start_ram_wr		(start_ram_wr),
    .start_ram_rd		(start_ram_rd),
    .ram_rd_done		(ram_rd_done),
    .ram_wr_done		(ram_wr_done)
    );




  // i2c_slave
  digital_i2c_32_slave i_digital_i2c_32_slave(
    .SDA_IN		(sda_in),
    .SDA_OUT		(sda_out),
    .RSTB		(resetb),
    .SCL		(scl),
    .REG_24_R		(reg_24_r),
    .REG_25_R		(reg_25_r),
    .REG_26_R		(reg_26_r),
    .REG_27_R		(reg_27_r),
    .REG_28_R		(reg_28_r),
    .REG_29_R		(reg_29_r),
    .REG_30_R		(reg_30_r),
    .REG_31_R		(reg_31_r),
    .REG_00_W		(reg_00_w),
    .REG_01_W		(reg_01_w),
    .REG_02_W		(reg_02_w),
    .REG_03_W		(reg_03_w),
    .REG_04_W		(reg_04_w),
    .REG_05_W		(reg_05_w),
    .REG_06_W		(reg_06_w),
    .REG_07_W		(reg_07_w),
    .REG_08_W		(reg_08_w),
    .REG_09_W		(reg_09_w),
    .REG_10_W		(reg_10_w),
    .REG_11_W		(reg_11_w),
    .REG_12_W		(reg_12_w),
    .REG_13_W		(reg_13_w),
    .REG_14_W		(reg_14_w),
    .REG_15_W		(reg_15_w),
    .REG_16_W		(reg_16_w),
    .REG_17_W		(reg_17_w),
    .REG_18_W		(reg_18_w),
    .REG_19_W		(reg_19_w),
    .REG_20_W		(reg_20_w),
    .REG_21_W		(reg_21_w),
    .REG_22_W		(reg_22_w),
    .REG_23_W		(reg_23_w),
    .reg_00_write	(reg_00_write),
    .reg_01_write	(reg_01_write),
    .reg_02_write	(reg_02_write),
    .reg_03_write	(reg_03_write),
    .reg_04_write	(reg_04_write),
    .reg_05_write	(reg_05_write),
    .reg_06_write	(reg_06_write),
    .reg_07_write	(reg_07_write),
    .reg_08_write	(reg_08_write),
    .reg_09_write	(reg_09_write),
    .reg_10_write	(reg_10_write),
    .reg_11_write	(reg_11_write),
    .reg_12_write	(reg_12_write),
    .reg_13_write	(reg_13_write),
    .reg_14_write	(reg_14_write),
    .reg_15_write	(reg_15_write),
    .reg_16_write	(reg_16_write),
    .reg_17_write	(reg_17_write),
    .reg_18_write	(reg_18_write),
    .reg_19_write	(reg_19_write),
    .reg_20_write	(reg_20_write),
    .reg_21_write	(reg_21_write),
    .reg_22_write	(reg_22_write),
    .reg_23_write	(reg_23_write),
    .reg_06_read	(reg_06_read)
    );




  // i2c_control
  digital_i2c_32_control i_digital_i2c_32_control(
    .clk			(clk_8rs),
    .resetb			(resetb),
    .reg_24			(status_reg_0),
    .reg_25			(status_reg_1),
    .reg_26			(status_reg_2),
    .reg_27			(status_reg_3),
    .reg_28			(status_reg_4),
    .reg_29			(status_reg_5),
    .reg_30			(status_reg_6),
    .reg_31			(status_reg_7),
    .reg_00			(config_reg_0),
    .reg_01			(config_reg_1),
    .reg_02			(config_reg_2),
    .reg_03			(config_reg_3),
    .reg_04			(config_reg_4),
    .reg_05			(config_reg_5),
    .reg_06			(config_reg_6),
    .reg_07			(config_reg_7),
    .reg_08			(config_reg_8),
    .reg_09			(config_reg_9),
    .reg_10			(config_reg_10),
    .reg_11			(config_reg_11),
    .reg_12			(config_reg_12),
    .reg_13			(config_reg_13),
    .reg_14			(config_reg_14),
    .reg_15			(config_reg_15),
    .reg_16			(config_reg_16),
    .reg_17			(config_reg_17),
    .reg_18			(config_reg_18),
    .reg_19			(config_reg_19),
    .reg_20			(config_reg_20),
    .reg_21			(config_reg_21),
    .reg_22			(config_reg_22),
    .reg_23			(config_reg_23),
    .ram_rd_done		(ram_rd_done),
    .ram_wr_done		(ram_wr_done),
    .start_ram_wr		(start_ram_wr),
    .start_ram_rd		(start_ram_rd),
    .scl			(scl),
    .REG_24_R			(reg_24_r),
    .REG_25_R			(reg_25_r),
    .REG_26_R			(reg_26_r),
    .REG_27_R			(reg_27_r),
    .REG_28_R			(reg_28_r),
    .REG_29_R			(reg_29_r),
    .REG_30_R			(reg_30_r),
    .REG_31_R			(reg_31_r),
    .REG_00_W			(reg_00_w),
    .REG_01_W			(reg_01_w),
    .REG_02_W			(reg_02_w),
    .REG_03_W			(reg_03_w),
    .REG_04_W			(reg_04_w),
    .REG_05_W			(reg_05_w),
    .REG_06_W			(reg_06_w),
    .REG_07_W			(reg_07_w),
    .REG_08_W			(reg_08_w),
    .REG_09_W			(reg_09_w),
    .REG_10_W			(reg_10_w),
    .REG_11_W			(reg_11_w),
    .REG_12_W			(reg_12_w),
    .REG_13_W			(reg_13_w),
    .REG_14_W			(reg_14_w),
    .REG_15_W			(reg_15_w),
    .REG_16_W			(reg_16_w),
    .REG_17_W			(reg_17_w),
    .REG_18_W			(reg_18_w),
    .REG_19_W			(reg_19_w),
    .REG_20_W			(reg_20_w),
    .REG_21_W			(reg_21_w),
    .REG_22_W			(reg_22_w),
    .REG_23_W			(reg_23_w),
    .reg_00_write		(reg_00_write),
    .reg_01_write		(reg_01_write),
    .reg_02_write		(reg_02_write),
    .reg_03_write		(reg_03_write),
    .reg_04_write		(reg_04_write),
    .reg_05_write		(reg_05_write),
    .reg_06_write		(reg_06_write),
    .reg_07_write		(reg_07_write),
    .reg_08_write		(reg_08_write),
    .reg_09_write		(reg_09_write),
    .reg_10_write		(reg_10_write),
    .reg_11_write		(reg_11_write),
    .reg_12_write		(reg_12_write),
    .reg_13_write		(reg_13_write),
    .reg_14_write		(reg_14_write),
    .reg_15_write		(reg_15_write),
    .reg_16_write		(reg_16_write),
    .reg_17_write		(reg_17_write),
    .reg_18_write		(reg_18_write),
    .reg_19_write		(reg_19_write),
    .reg_20_write		(reg_20_write),
    .reg_21_write		(reg_21_write),
    .reg_22_write		(reg_22_write),
    .reg_23_write		(reg_23_write),
    .reg_06_read		(reg_06_read)
    );






endmodule
