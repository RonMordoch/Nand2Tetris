// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Sort.asm

// Sorts an array of integers in a descending order.

	@i
	M = 0

(OUTER)
	@i
	D = M // D = i
	@R15 // arr length
	D = M - D // D = n - i
	@i
	M = M + 1 // i = i + 1
	@END
	D; JLE // if i >= n  end inner loop 
	// else
	@j 
	M = 0
	@INNER
	0; JMP

(INNER)
	@j
	D = M // D = j
	D = D + 1 // D = j + 1
	@R15 // arr length
	D = M - D // D = n - ( j + 1 )
	@OUTER
	D; JLE // if j >= n - 1 go to outer loop 
	// else
	@CONDITION
	0; JMP

(CONDITION)

	@R14
	D = M // D = arr
	@j
	D = D + M // D = arr + j
	@R0
	M = D // R0 = arr + j , index of current position
	@R1
	M = D + 1 // R1 = arr + j + 1, index of next position

	@R14
	D = M // D = arr
	@j
	A = D + M // A = arr + j
	D = M // D = RAM[arr + j]
	A = A + 1
	D = D - M // D = RAM[arr+j] - RAM[arr+j+1]
	
	@SWAP
	D; JLT
	// else, we did not swap
	@j
	M = M + 1
	@INNER
	0;JMP

(SWAP)
	@R0
	A = M // A = R0
	D = M // D = RAM[R0] = RAM[arr + j]
	@temp
	M = D // temp = RAM[arr + j]
	@R1
	A = M // A = R1
	D = M // D = RAM[R1] = RAM[arr + j + 1]
	@R0
	A = M
	M = D // RAM[arr + j] = RAM[arr+j+1]
	@temp
	D = M // D = RAM[arr +j]
	@R1
	A = M // A = R1
	M = D // R1 = RAM[arr + j]
	
	@j
	M = M + 1
	@INNER
	0; JMP
	
(END)







	
