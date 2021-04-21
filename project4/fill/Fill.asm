// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.


(MAIN)
	@SCREEN
	D = A // D = address of screen
	@addr
	M = D //addr = address of screen
	@8191
	D = A // D = 8191
	@n 
	M = D // n = 8191
	@i
	M = 0 // i = 0

	@KBD
	D = M // address of keyboard

	@FILL
	D; JNE // if KBD != 0, goto FILL code 
	//else
	@BLANK // if KBD == 0, goto BLANK code
	D; JEQ

	@MAIN //back to main loop
	0;JMP
//to fill screen
(FILL)
	@i
	D = M
	@n
	D = D - M
	@MAIN
	D; JGT //if i - n > 0 goto main loop
	
	@addr
	A = M
	M = -1 //change screen bit to -1
	
	@i
	M = M + 1 // i ++
	@addr
	M = M + 1 //addr ++
	@FILL
	0;JMP //go to FILL loop

(BLANK)
	@i
	D = M
	@n
	D = D - M
	@MAIN
	D; JGT //if i - n > 0 goto MAIN loop
	
	@addr
	A = M
	M = 0 //change screen bit to 0 (white)
	
	@i
	M = M + 1 //i++
	@addr
	M = M + 1 //addr ++
	@BLANK
	0;JMP //continue the BLANK loop




