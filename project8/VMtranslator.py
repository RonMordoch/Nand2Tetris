import os
import sys

# code for pushing into stack
STACK_UPDATE = "@SP" + "\n" + "A = M" + "\n" + "M = D" + "\n" + "@SP" + "\n" + "M = M + 1" + "\n"
# all arithmetic ops
ARITHMETIC_OPS = {"add": "+", "sub": "-", "neg": "-", "and": "&", "or": "|", "not": "!"}
# all comparison ops
COMPARISON_OPS = ["gt", "lt", "eq"]
# memory segments
MEM_SEGMENTS = {"argument": "ARG", "local": "LCL", "this": "THIS", "that": "THAT", "temp": "5", "pointer": "3"}
# code for setting the stack's top-most value to be true or false
SET_STACK_TRUE = "@SP" + "\n" + "A = M" + "\n" + "M = -1" + "\n" + "@SP" + "\n" + "M = M + 1" + "\n"
SET_STACK_FALSE = "@SP" + "\n" + "A = M" + "\n" + "M = 0" + "\n" + "@SP" + "\n" + "M = M + 1" + "\n"
# array of memory segments used in the caller-callee procedure
MEM_SEGMENT_ARR = ["THAT", "THIS", "ARG", "LCL"]
#  code for calculating (FRAME - 1) for the return procedure
FRAME_MINUS_ONE = "@R14" + "\n" + "AM = M - 1" + "\n" + "D = M" + "\n"


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
        curr_function = ["Sys.init", 0]
        # write bootstrap once in the beginning of output file
        write_bootstrap(output_file, curr_function)
        comparison_counter = [0]
        for file in asm_files:
            with open(file) as f:
                MEM_SEGMENTS["static"] = f.name.split("/")[-1].replace(".vm", "")
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("//") or line.startswith("("):  # empty line or comment line
                        continue
                    line = line.split('//')[0]
                    line_arr = line.split()
                    handle_line(output_file, line_arr, comparison_counter, curr_function)


def write_bootstrap(output_file, curr_function):
    """
    Writes the bootstrap code in the beginning of asm file.
    :param output_file: output file that it writes assembly code into
    :param curr_function: the current function being processed, in this case, always Sys.init
    :return: none
    """
    # initialize stack
    output_file.write("@256" + "\n" +
                      "D = A" + "\n" +
                      "@SP" + "\n" +
                      "M = D" + "\n"
                      )
    # call the Sys.init function
    write_call(output_file, "Sys.init", "0", curr_function)


def handle_line(output_file, line_arr, comparison_counter, curr_function):
    """
    This function handles a single line of vm input
    :param output_file: output file that it writes assembly code into
    :param line_arr: array containing line
    :param comparison_counter
    :param curr_function
    :return: none
    """
    if line_arr[0] in ARITHMETIC_OPS or line_arr[0] in COMPARISON_OPS:
        write_arithmetic(output_file, line_arr[0], comparison_counter)
    elif line_arr[0] == "push":
        write_push(output_file, line_arr)
    elif line_arr[0] == "pop":
        write_pop(output_file, line_arr[1], line_arr[2])
    elif line_arr[0] == "label":
        write_label(output_file, line_arr[1], curr_function)
    elif line_arr[0].endswith("goto"):
        write_goto(output_file, line_arr[0], line_arr[1], curr_function)
    elif line_arr[0] == "function":
        write_function(output_file, line_arr[1], line_arr[2], curr_function)
    elif line_arr[0] == "return":
        write_return(output_file)
    elif line_arr[0] == "call":
        write_call(output_file, line_arr[1], line_arr[2], curr_function)


def write_arithmetic(output_file, op, comparison_counter):
    """
    This function writes the arithmetic operations into assembly code
    :param comparison_counter: counter of comparison operations used in order to differentiate different comparison
    calls in the same file
    :param output_file: output file to be written into
    :param op: operation of
    :return: none
    """
    if op == "eq":
        write_equals(output_file, comparison_counter)
        comparison_counter[0] += 1
    elif op == "gt" or op == "lt":
        write_gl_lt(output_file, comparison_counter, op)
        comparison_counter[0] += 1
    # unary operations
    elif op == "neg" or op == "not":
        output_file.write("@SP" + "\n" +
                          "AM = M - 1" + "\n" +
                          "D = " + ARITHMETIC_OPS[op] + "M" + "\n" + STACK_UPDATE
                          )
    else:
        # binary operations
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
        write_push_constant(output_file, line_arr[2])
    elif line_arr[1] in MEM_SEGMENTS:
        write_push_segment(output_file, line_arr)


def write_push_constant(output_file, constant):
    """
    Writes the push operations for the constants
    :param output_file: output file to be written into
    :param constant: string of constant integer to push into stack
    :return: none
    """
    output_file.write("@" + constant + "\n" +
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
                          "D = " + a_or_m + "\n" +
                          STACK_UPDATE)
    else:
        if line_arr[1] == "temp" or line_arr[1] == "pointer":
            a_or_m = "A"
        output_file.write("@" + MEM_SEGMENTS[line_arr[1]] + "\n" +
                          "D = " + a_or_m + "\n" +
                          "@" + line_arr[2] + "\n" +
                          "D = D + A" + "\n" +
                          "A = D" + "\n" +
                          "D = M" + "\n" +
                          STACK_UPDATE)


def write_pop(output_file, mem_segment, dest_index):
    """
    Writes the stack pop operation.
    :param output_file: the output file to write the assembly code to
    :param mem_segment: line_arr[1] - the memory segment to pop into
    :param dest_index: line_arr[2] -index of the memory segment to pop into
     ( i.e. final destination is base adrr + dest_index)
    :return: none
    """
    if mem_segment == "static":
        output_file.write("@SP" + "\n" +
                          "AM = M - 1" + "\n" +
                          "D = M" + "\n" +
                          "@" + MEM_SEGMENTS[mem_segment] + "." + dest_index + "\n" +
                          "M = D" + "\n"
                          )
    else:
        a_or_m = "M"
        if mem_segment == "temp" or mem_segment == "pointer":
            a_or_m = "A"
        output_file.write("@" + MEM_SEGMENTS[mem_segment] + "\n" +
                          "D = " + a_or_m + "\n" +
                          "@" + dest_index + "\n" +
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
                      SET_STACK_FALSE +
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


def write_goto(output_file, command, label, curr_function):
    """
    Writes the goto and if-goto conditions.
    :param output_file: output file that it writes assembly code into
    :param command: line_arr[0] - goto or if-goto
    :param label: the line_arr[1] - the destination for the jump
    :param curr_function: current function being called
    :return: none
    """
    if command == "if-goto":
        output_file.write("@SP" + "\n" +
                          "AM = M - 1" + "\n" +
                          "D = M" + "\n" +
                          "@" + curr_function[0] + "$" + label + "\n" +
                          "D; JNE" + "\n")
    else:
        output_file.write("@" + curr_function[0] + "$" + label + "\n" +
                          "0; JMP" + "\n")


def write_label(output_file, label, curr_function):
    """
    Writes the label for the current function.
    :param output_file: output file that it writes assembly code into
    :param label: line_arr[1] - label name as written in the VM code, written in the format specified by the book
    :param curr_function: current function being processed
    :return: none
    """
    output_file.write("(" + curr_function[0] + "$" + label + ")" + "\n")


def write_function(output_file, function_name, n_vars, curr_function):
    """
    Writes the function and the code to push the n zero arguments into the stack.
    :param output_file: output file that it writes assembly code into
    :param function_name: line_arr[1], name of function
    :param n_vars: line_arr[2], number of local variables
    :param curr_function: current function being processed
    :return: none
    """
    curr_function[0] = function_name
    output_file.write("(" + function_name + ")" + "\n")
    for i in range(int(n_vars)):
        write_push_constant(output_file, "0")


def write_call(output_file, function_name, n_args, curr_function):
    """
    Writes the call-function code, as specified in the book.
    :param output_file: output file that it writes assembly code into
    :param function_name: line_arr[1] , name of function being called
    :param n_args: line_arr[2], number of arguments
    :param curr_function: current function being processed
    :return: none
    """
    curr_function[1] += 1
    # create return address
    output_file.write("@" + curr_function[0] + "$RET" + str(curr_function[1]) + "\n" +
                      "D = A" + "\n" +
                      STACK_UPDATE + "\n")
    # push memory segments of calling function
    for mem_segment in reversed(MEM_SEGMENT_ARR):
        output_file.write("@" + mem_segment + "\n" +
                          "D = M" + "\n" +
                          STACK_UPDATE)
    output_file.write("@5" + "\n"
                             "D = A" + "\n"
                                       "@SP" + "\n" +
                      "D = M - D" + "\n" +
                      "@" + n_args + "\n" +
                      "D = D - A" + "\n" +
                      "@ARG" + "\n" +
                      "M = D" + "\n" +
                      "@SP" + "\n" +
                      "D = M" + "\n" +
                      "@LCL" + "\n" +
                      "M = D" + "\n" +
                      "@" + function_name + "\n" +
                      "0; JMP" + "\n" +
                      "(" + curr_function[0] + "$RET" + str(curr_function[1]) + ")"
                      + "\n"
                      )


def write_return(output_file):
    """
    Writes the procedure for the return command, as specified in the book.
    :param output_file: output file that it writes assembly code into
    :return: none, ironically
    """
    # temp variables: R14 is FRAME; R15 is RET.
    output_file.write("@LCL" + "\n" +
                      "D = M" + "\n" +
                      "@R14" + "\n" +
                      "M = D " + "\n" +
                      "@5" + "\n" +
                      "D = D - A" + "\n" +
                      "A = D" + "\n" +
                      "D = M" + "\n" +
                      "@R15" + "\n" +
                      "M = D" + "\n"
                      )
    write_pop(output_file, "argument", "0")
    output_file.write("@ARG" + "\n" +
                      "D = M +1 " + "\n" +
                      "@SP" + "\n" +
                      "M = D" + "\n")
    for mem_segment in MEM_SEGMENT_ARR:
        output_file.write(FRAME_MINUS_ONE + "@" + mem_segment + "\n" + "M = D" + "\n")
    output_file.write("@R15" + "\n" +
                      "A = M" + "\n"
                                "0; JMP" + "\n")


def main():
    """
    Main function, parses the argument received in CLI.
    :return: none
    """
    parse_file(sys.argv[1])


if __name__ == '__main__':
    main()
