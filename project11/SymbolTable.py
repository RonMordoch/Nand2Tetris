class SymbolTable:
    """
    A symbol table for each jack file.
    """

    def __init__(self):
        """
        Constructs an empty symbol table.
        """
        self.__class_scope = {}
        self.__subroutine_scope = {}
        # class scope counters, do not reset
        self.__static_counter = 0
        self.__field_counter = 0
        # subroutine scope counters, reset every time a new subroutine scope is started
        self.__arg_counter = 0
        self.__var_counter = 0

    def start_subroutine(self):
        """
        Starts a new table for the current subroutine.
        """
        self.__subroutine_scope = {}
        self.__arg_counter = 0
        self.__var_counter = 0

    def define(self, name, type, kind):
        """
        Adds a variable to the symbol table.
        :param name: name of variable
        :param type:  type of variable
        :param kind: kind of variable
        """
        if kind == "static":
            self.__class_scope[name] = (type, kind, self.__static_counter)
            self.__static_counter += 1
        elif kind == "field":
            self.__class_scope[name] = (type, "this", self.__field_counter)
            self.__field_counter += 1
        elif kind == "argument":
            self.__subroutine_scope[name] = (type, kind, self.__arg_counter)
            self.__arg_counter += 1
        elif kind == "var":
            self.__subroutine_scope[name] = (type, "local", self.__var_counter)
            self.__var_counter += 1

    def var_count(self, kind):
        """
        Returns the number of variables from given kind.
        :param kind: kind of variables
        """
        if kind == "static":
            return self.__static_counter
        elif kind == "field":
            return self.__field_counter
        elif kind == "argument":
            return self.__arg_counter
        elif kind == "var":
            return self.__var_counter

    def kind_of(self, name):
        """
        Returns the kind of a variable.
        :param name: variable name
        """
        if name in self.__subroutine_scope:
            return self.__subroutine_scope[name][1]
        elif name in self.__class_scope:
            return self.__class_scope[name][1]
        return None

    def type_of(self, name):
        """
        Returns the type of a variable.
        :param name: variable name
        """
        if name in self.__subroutine_scope:
            return self.__subroutine_scope[name][0]
        elif name in self.__class_scope:
            return self.__class_scope[name][0]
        return None

    def index_of(self, name):
        """
        Returns the index of a variable.
        :param name: variable name
        """
        if name in self.__subroutine_scope:
            return self.__subroutine_scope[name][2]
        elif name in self.__class_scope:
            return self.__class_scope[name][2]
        return None
