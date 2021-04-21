import os
import sys
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine


def main():
    """
    Initializes  compilation engine for each file and outputs VM code.
    """
    file_path = sys.argv[1]
    if os.path.isdir(file_path):
        asm_files = [file_path + '/' + filename for filename in os.listdir(file_path) if filename.endswith(".jack")]
    else:
        asm_files = [file_path]
    for file in asm_files:
        with open(file) as f:
            tokenizer = JackTokenizer(f)
            output_file_path = file.replace(".jack", ".vm")
            with open(output_file_path, "w+") as output_file:
                c = CompilationEngine(tokenizer, output_file)
                c.compile_class()


if __name__ == '__main__':
    main()

