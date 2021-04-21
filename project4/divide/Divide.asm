// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Sort.asm

// Calculates R13/R14, and stores the result at R15.
	
	@R14
	D = M
	@de
	M = D // de = RAM[14] 

	@R13
	D = M
	@nu
	M = D // nu = RAM[13]

	@temp
	M = 1 //temp = 1

	@R15
	M = 0 //quotient = 0

(EDGECASE)
	@de
	D = M
	@nu
	D = M - D // if nu - de < 0, stop the division
	@STOP
	D; JLT

(LOOP1)
	@de
	D = M
	@nu
	D = D - M // if de - nu > 0 goto next loop
	@LOOP2
	D;JGT

	@de
	D = M
	D = D<< // check if D < 0
	@LOOP2
	D; JLT
	@de
	M = M<< //de <<= 1
	D = M
	@nu
	D = D - M  // D = de - nu
	@LOOP1 // check if de - nu > 0
	D; JGT

(CONT)
	@de
	D = M
	@oldde
	M = D // old de
	@temp
	M = M<< // temp <<= 1
	@LOOP1
	0;JMP

(LOOP2)
	@temp
	D = M
	@R15
	M = M + D // res = temp
	@temp
	M = 1 // reset temp back to 1
	@oldde
	D = M // d = old denominator
	@nu
	M = M - D // nu = nu - old denominator
	D = M
	@STOP
	D; JLE
	@R14
	D = M // D = de
	@de
	M = D // reset de back to original value
	@EDGECASE
	0;JMP

(STOP)

	
	

