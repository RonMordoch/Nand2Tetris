import os
import sys

STACK_UPDATE = "@SP" + "\n" + "A = M" + "\n" + "M = D" + "\n" + "@SP" + "\n" + "M = M + 1" + "\n"

ARITHMETIC_OPS = {"add": "+", "sub": "-", "neg": "-", "and": "&", "or": "|", "not": "!"}
COMPARISON_OPS = ["gt", "lt", "eq"]

MEM_SEGMENTS = {"argument": "ARG", "local": "LCL", "this": "THIS", "that": "THAT", "temp": "5", "pointer": "3"}

SET_STACK_TRUE = "@SP" + "\n" + "A = M" + "\n" + "M = -1" + "\n" + "@SP" + "\n" + "M = M + 1" + "\n"
SET_STACK_FALSE = "@SP" + "\n" + "A = M" + "\n" + "M = 0" + "\n" + "@SP" + "\n" + "M = M + 1" + "\n"


def parse_file(file_path):
    """
    Parses the file/files given in the file path.
    :param file_path: file path of a vm file or a folder containing vm file
    :return: none
    """
    if os.path.isdir(file_path):
        asm_files = [file_path + '/' + filename for filename in os.listdir(file_path) if filename.endswith(".vm")]
        output_file_path = file_path + "/" + os.path.basename(file_path) + ".asm"
    else:
        asm_files = [file_path]
        output_file_path = file_path.replace(".vm", ".asm")
    with open(output_file_path, "w+") as output_file:
        for file in asm_files:
            with open(file) as f:
                MEM_SEGMENTS["static"] = f.name.split("/")[-1].replace(".vm", "")
                comparison_counter = [0]
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("//") or line.startswith("("):  # empty line or comment line
                        continue
                    line = line.split('//')[0]
                    line_arr = line.split()
                    handle_line(output_file, line_arr, comparison_counter)


def handle_line(output_file, line_arr, comparison_counter):
    """
    This function handles a single line of vm input
    :param output_file: output file that it writes assembly code into
    :param line_arr: array containing line
    :param comparison_counter: counter for comparison operations
    :return: none
    """
    if line_arr[0] in ARITHMETIC_OPS or line_arr[0] in COMPARISON_OPS:
        write_arithmetic(output_file, line_arr[0], comparison_counter)
    elif line_arr[0] == "push":
        write_push(output_file, line_arr)
    elif line_arr[0] == "pop":
        write_pop(output_file, line_arr)


def write_arithmetic(output_file, op, comparison_counter):
    """
    This function writes the arithmetic operations into assembly code
    :param output_file: output file to be written into
    :param op: operation of
    :return: nothing
    """
    if op == "eq":
        write_equals(output_file, comparison_counter)
        comparison_counter[0] += 1
    elif op == "gt" or op == "lt":
        write_gl_lt(output_file, comparison_counter, op)
        comparison_counter[0] += 1
    elif op == "neg" or op == "not":
        output_file.write("@SP" + "\n" +
                          "AM = M - 1" + "\n" +
                          "D = " + ARITHMETIC_OPS[op] + "M" + "\n" + STACK_UPDATE
                          )
    else:
        output_file.write("@SP" + "\n" +
                          "AM = M - 1" + "\n" +
                          "D = M" + "\n" +
                          "@SP" + "\n" +
                          "AM = M - 1" + "\n" +
                          "D = M" + ARITHMETIC_OPS[op] + "D" + "\n" + STACK_UPDATE
                          )


def write_push(output_file, line_arr):
    """
    Writes push operations into assembler code
    :param output_file: output file to be written into
    :param line_arr: array of the words in a line
    :return: none
    """
    if line_arr[1] == "constant":
        write_push_constant(output_file, line_arr)
    elif line_arr[1] in MEM_SEGMENTS:
        write_push_segment(output_file, line_arr)


def write_push_constant(output_file, line_arr):
    """
    Writes the push operations for the constants
    :param output_file: output file to be written into
    :param line_arr: array of words in line
    :return: none
    """
    output_file.write("@" + line_arr[2] + "\n" +
                      "D = A" + "\n" +
                      STACK_UPDATE)


def write_push_segment(output_file, line_arr):
    """
    Writes the push operations for the memory segments
    :param output_file: output file to be written into
    :param line_arr: array of words in line
    :return: none
    """
    a_or_m = "M"
    if line_arr[1] == "static":
        output_file.write("@" + MEM_SEGMENTS[line_arr[1]] + "." + line_arr[2] + "\n" +
                          "D =" + a_or_m + "\n" +
                          STACK_UPDATE)
    else:
        if line_arr[1] == "temp" or line_arr[1] == "pointer":
            a_or_m = "A"
        output_file.write("@" + MEM_SEGMENTS[line_arr[1]] + "\n" +
                          "D =" + a_or_m + "\n" +
                          "@" + line_arr[2] + "\n" +
                          "D = D + A" + "\n" +
                          "A = D" + "\n" +
                          "D = M" + "\n" +
                          STACK_UPDATE)


def write_pop(output_file, line_arr):
    """
    Writes the stack pop operation.
    :param output_file: the output file to write the assembly code to
    :param line_arr: the array of elements of current line that is being parsed
    :return:  none
    """
    if line_arr[1] == "static":
        output_file.write("@SP" + "\n" +
                          "AM = M - 1" + "\n" +
                          "D = M" + "\n" +
                          "@" + MEM_SEGMENTS[line_arr[1]] + "." + line_arr[2] + "\n" +
                          "M = D" + "\n"
                          )
    else:
        a_or_m = "M"
        if line_arr[1] == "temp" or line_arr[1] == "pointer":
            a_or_m = "A"
        output_file.write("@" + MEM_SEGMENTS[line_arr[1]] + "\n" +
                          "D =" + a_or_m + "\n" +
                          "@" + line_arr[2] + "\n" +
                          "D = A + D" + "\n" +
                          "@13" + "\n" +
                          "M = D" + "\n" +
                          "@SP" + "\n" +
                          "AM = M - 1" + "\n" +
                          "D = M" + "\n" +
                          "@13" + "\n" +
                          "A = M" + "\n" +
                          "M = D" + "\n"
                          )


def write_equals(output_file, eq_counter):
    """
    Writes the equals (==) comparison operation.
    :param output_file: the output file to write the assembly code to
    :param eq_counter: the counter of the number of equal comparison ops written, used in order to distinguish the
    jumps between different equal comparisons
    :return:  none
    """
    output_file.write("@SP" + "\n" +
                      "AM = M - 1" + "\n" +
                      "D = M" + "\n" +
                      "@SP" + "\n" +
                      "AM = M - 1" + "\n" +
                      "D = D - M" + "\n" +
                      "@TRUE" + str(eq_counter[0]) + "\n" +
                      "D;JEQ" + "\n" +
                      SET_STACK_FALSE+
                      "@CONTINUE" + str(eq_counter[0]) + "\n" +
                      "0; JMP" + "\n" +
                      "(TRUE" + str(eq_counter[0]) + ")" + "\n" +
                      SET_STACK_TRUE +
                      "(CONTINUE" + str(eq_counter[0]) + ")" + "\n"
                      )


def write_gl_lt(output_file, comparison_counter, op):
    """
    Writes the greater than (>=) or lesser than (<= comparison operations.
    :param output_file: the output file to write the assembly code to
    :param comparison_counter: the counter of the number of comparison ops written, used in order to distinguish the
    jumps between different comparisons
    :param op: the operation that being written
    :return:  none
    """
    op_bool = ["TRUE", "FALSE"]  # comparison conditions for greater than
    if op == "lt":
        op_bool = op_bool[::-1]  # reverse for lesser than
    output_file.write("@SP" + "\n" +
                      "AM = M - 1" + "\n" +
                      "D = M" + "\n" +
                      "@13" + "\n" +
                      "M = D" + "\n" +
                      "@SP" + "\n" +
                      "AM = M - 1" + "\n" +
                      "D = M" + "\n" +
                      "@14" + "\n" +
                      "M = D" + "\n" +
                      "@PositiveX" + str(comparison_counter[0]) + "\n" +
                      "D; JGT" + "\n" +

                      "(NegativeX" + str(comparison_counter[0]) + ")" + "\n" +
                      "@13" + "\n" +
                      "D = M" + "\n" +
                      "@" + op_bool[1] + str(comparison_counter[0]) + "\n" +
                      "D;JGE" + "\n" +
                      "@SAMESIGN" + str(comparison_counter[0]) + "\n" +
                      "D; JLT" + "\n" +

                      "(PositiveX" + str(comparison_counter[0]) + ")" + "\n" +
                      "@13" + "\n" +
                      "D = M" + "\n" +
                      "@" + op_bool[0] + str(comparison_counter[0]) + "\n" +
                      "D; JLE" + "\n" +

                      "(SAMESIGN" + str(comparison_counter[0]) + ")" + "\n" +
                      "@13" + "\n" +
                      "D = M " + "\n" +
                      "@14" + "\n" +
                      "D = M - D" + "\n" +
                      "@" + op_bool[0] + str(comparison_counter[0]) + "\n" +
                      "D; JGT" + "\n" +
                      "@" + op_bool[1] + str(comparison_counter[0]) + "\n" +
                      "D; JLT" + "\n" +

                      "(FALSE" + str(comparison_counter[0]) + ")" + "\n" +
                      SET_STACK_FALSE +
                      "@CONTINUE" + str(comparison_counter[0]) + "\n" +
                      "0;JMP" + "\n" +

                      "(TRUE" + str(comparison_counter[0]) + ")" + "\n" +
                      SET_STACK_TRUE +

                      "(CONTINUE" + str(comparison_counter[0]) + ")" + "\n"
                      )


def main():
    """
    Main function, parses the argument received in CLI.
    :return: none
    """
    parse_file(sys.argv[1])


if __name__ == '__main__':
    main()