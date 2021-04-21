// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

	@res 
	M = 0 // res = 0

	@R0
	D = M // D = R0
	@t
	M = D // t = R0

	@R1
	D = M // D = R1
	@n
	M = D // n = R1
	
(LOOP)
	@n
	D = M // D = n
	@STOP
	D;JLE

	@t
	D = M // D = t
	@res
	M = M + D // res = res + t

	@n
	M = M - 1 // n = n - 1
	@LOOP
	0;JMP

(STOP)
	@res
	D = M // D = res
	@R2
	M = D // R2 = res
	
