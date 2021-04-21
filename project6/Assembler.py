#!usr/bin/env python3

import numpy as np
import os
import sys

# dictionaries

# destination
DEST_DICT = {"": "000", "M": "001", "D": "010", "MD": "011", "A": "100", "AM": "101", "AD": "110", "AMD": "111"}

# jump
JUMP_DCT = {"": "000", "JGT": "001", "JEQ": "010", "JGE": "011", "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"}

# comp dictionaries
COMP_DICT = {"0": "0101010", "1": "0111111", "-1": "0111010", "D": "0001100", "A": "0110000", "M": "1110000",
             "!D": "0001101", "!A": "0110001", "!M": "1110001", "-D": "0001111", "-A": "0110011", "-M": "1110011",
             "D+1": "0011111", "A+1": "0110111", "M+1": "1110111", "D-1": "0001110", "A-1": "0110010", "M-1": "1110010",
             "D+A": "0000010", "D+M": "1000010", "A+D": "0000010", "M+D": "1000010", "D-A": "0010011", "D-M": "1010011",
             "A-D": "0000111", "M-D": "1000111", "D&A": "0000000", "D&M": "1000000", "D|A": "0010101", "D|M": "1010101",
             "A&D": "0000000", "M&D": "1000000", "A|D": "0010101", "M|D": "1010101"}

# symbols dict
SYMBOLS_DICT = {"SP": "0", "LCL": "1", "ARG": "2", "THIS": "3", "THAT": "4", "R0": "0", "R1": "1", "R2": "2", "R3": "3",
                "R4": "4", "R5": "5", "R6": "6", "R7": "8", "R9": "9", "R10": "10", "R11": "11", "R12": "12",
                "R13": "13", "R14": "14", "R15": "15", "SCREEN": "16384", "KBD": "24576"}

# shift comparison
COMP_SHIFT_DICT = {"D<<": "0110000", "A<<": "0100000", "M<<": "1100000", "D>>": "0010000", "A>>": "0000000",
                   "M>>": "1000000"}


def is_string_int(string):
    """
    :param string: string possibly representing an integer
    :return: True if the string is a valid integer; False otherwise
    """
    try:
        int(string)
        return True
    except ValueError:
        return False


def string_num_to_binary(string):
    """
    :param string: string representing an integer
    :return: string containing binary representation of the integer
    """
    return np.binary_repr(int(string), width=15)


def a_instruction_to_binary(string, dictionary, counter):
    """
    Converts an A-instruction to binary code.
    :param string: string in assembly code
    :param dictionary: dictionary with variables of  assembly code file
    :param counter: line counter to find the the address in memory for variables
    :return: counter, the A-instruction in binary code
    """
    if is_string_int(string):
        return counter, "0" + string_num_to_binary(string)
    if string in dictionary:
        return counter, "0" + string_num_to_binary(dictionary[string])
    dictionary[string] = counter
    counter += 1
    return counter, "0" + string_num_to_binary(dictionary[string])


def split_c_instruction(string):
    """
    Splits a C-instruction into its components.
    :param string: C-instruction
    :return: dest, comp and jmp values of C-instruction (if exists, empty string otherwise)
    """
    string = string.replace(" ", "")
    if "=" in string:
        instruction_line = string.split('=')
        dest = instruction_line[0]
        if len(instruction_line[1].split(';')) == 2:
            comp, jmp = instruction_line[1].split(';')[0], instruction_line[1].split(';')[1]
        else:
            comp, jmp = instruction_line[1].split(';')[0], ""
    else:
        dest = ""
        comp, jmp = string.split(';')[0], string.split(';')[1]

    return dest, comp, jmp


def c_instruction_to_binary(dest, comp, jmp):
    """
    Converts a C-instruction to binary code.
    :param dest: destination of the instruction
    :param comp: the computational operation to perform
    :param jmp: the jump condition
    :return: the C instruction in binary code.
    """
    if comp in COMP_DICT:
        return "111" + COMP_DICT[comp] + DEST_DICT[dest] + JUMP_DCT[jmp]
    return "101"+COMP_SHIFT_DICT[comp]+DEST_DICT[dest]+JUMP_DCT[jmp]


def first_pass(file):
    """
    Adds all the symbols in the file to a copy of the symbols dictionary.
    :param file: the asm file
    :return: dictionary with all the symbols in file
    """
    line_counter = 0
    curr_file_symbols = SYMBOLS_DICT.copy()
    for line in file:
        line = line.strip()
        if not line or line.startswith("//"):
            continue
        line = line.split('//')[0]
        if line.startswith("("):
            curr_file_symbols[line[1:len(line)-1]] = str(line_counter)
        else:
            line_counter += 1
    return curr_file_symbols


def parse_file(file_path):
    """
    Parses a file path containing one or more asm files .
    :param file_path: directory of folder of asm files or an asm file
    :return: none, performs writing to the output file
    """
    if os.path.isdir(file_path):
        asm_files = [file_path+'/'+filename for filename in os.listdir(file_path) if filename.endswith(".asm")]
    else:
        asm_files = [file_path]
    for file in asm_files:
        with open(file) as f:
            output_file_path = file.replace(".asm", ".hack")
            current_symbols_dict = first_pass(f)
            f.seek(0)
            with open(output_file_path, "w+") as output_file:
                curr_address = 16
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("//") or line.startswith("("):  # empty line or comment line
                        continue
                    line = line.split('//')[0]
                    if line.startswith("@"):
                        curr_address, instruction = a_instruction_to_binary(line[1:], current_symbols_dict, curr_address)
                        output_file.write(instruction + "\n")
                    else:  # c instruction
                        dest, comp, jmp = split_c_instruction(line) #TODO change function call to tuple
                        output_file.write(c_instruction_to_binary(dest, comp, jmp) + "\n")


def main():
    """
    Main function, parses the argument received in CLI.
    :return: none
    """
    parse_file(sys.argv[1])


if __name__ == '__main__':
    main()