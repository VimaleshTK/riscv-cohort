module alu (
  input  logic [31:0] a,
  input  logic [31:0] b,
  input  logic [3:0]  op,
  output logic [31:0] y
);

  always_comb begin
    case (op)
      4'b0001: y = a + b; // ADD
      4'b0010: y = a - b; // SUB
      default: y = 32'hdeadbeef;
    endcase
  end

endmodule
