class VMWriter:
    """
    A module to write VM code.
    """

    def __init__(self, output_file):
        """
        Receives an output file to write VM code into.
        :param output_file: target file
        """
        self.__file = output_file

    def write_push(self, segment, index):
        """
        Writes the push command.
        :param segment: memory segment to push into
        :param index: index
        """
        self.__file.write("push " + segment + " " + str(index) + "\n")

    def write_pop(self, segment, index):
        """
        Writes the pop command.
        :param segment: memory segment to pop into
        :param index: index
        """
        self.__file.write("pop " + segment + " " + str(index) + "\n")

    def write_arithmetic(self, command):
        """
        Writes an arithmetic command.
        :param command: arithmetic command
        """
        self.__file.write(command + "\n")

    def write_label(self, label):
        """
        Writes the given label.
        :param label: label
        """
        self.__file.write("label " + label + "\n")

    def write_go_to(self, label):
        """
        Writes goto command.
        :param label: label to go to
        """
        self.__file.write("goto " + label + "\n")

    def write_if_go_to(self, label):
        """
        Writes if-goto command.
        :param label: label to go to
        """
        self.__file.write("if-goto " + label + "\n")

    def write_call(self, name, n_args):
        """
        Writes a function call.
        :param name: function name
        :param n_args: number of arguments
        """
        self.__file.write("call " + name + " " + str(n_args) + "\n")

    def write_function(self, name, n_locals):
        """
        Writes a function declaration.
        :param name: function name
        :param n_locals: number of local variables
        """
        self.__file.write("function " + name + " " + str(n_locals) + "\n")

    def write_return(self):
        """
        Writes a return command.
        """
        self.__file.write("return\n")
