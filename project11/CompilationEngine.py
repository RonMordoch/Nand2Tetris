from VMWriter import VMWriter
from SymbolTable import SymbolTable


class CompilationEngine:
    """
    A CompilationEngine for the Jack language.
    """

    BINARY_OPS = {'+': 'add', '-': 'sub', '=': 'eq', '>': 'gt', '<': 'lt', '&': 'and', '|': 'or',
                  '*': "call Math.multiply 2", '/': "call Math.divide 2"}
    STATEMENTS_KEYWORDS = {'if', 'while', 'let', 'do', 'return'}

    def __init__(self, tokenizer, output_file):
        """
        Initializes a CompilationEngine object.
        :param tokenizer: the input file stream
        :param output_file: output file stream to write into.
        """
        self.__tokenizer = tokenizer  # input file stream
        self.__out_file = output_file  # output file stream
        self.__curr_token = ""  # curr token being processed
        self.__curr_token_type = ""  # curr token type
        self.__advance_tokenizer()  # advances the tokenizer
        self.__symbol_table = SymbolTable()
        self.__vm_writer = VMWriter(output_file)
        self.__class_name = ""
        self.__curr_subroutine_name = ""
        self.__curr_label_counter = 0

    def compile_class(self):
        """
        Compiles the entire class file.
        """
        self.__advance_tokenizer()
        self.__class_name = self.__curr_token
        self.__advance_tokenizer()  # '{'
        self.__advance_tokenizer()
        # compiles class static members or fields
        while self.__curr_token == "static" or self.__curr_token == "field":
            self.compile_class_var_dec()
            self.__advance_tokenizer()
        # compiles all the functions in the class
        while self.__curr_token == "constructor" or self.__curr_token == "function" or self.__curr_token == "method":
            self.compile_subroutine_dec()
            self.__advance_tokenizer()

    def compile_class_var_dec(self):
        """
        Compiles class' variables declarations.
        """
        kind = self.__curr_token  # static or field
        self.__advance_tokenizer()
        type = self.__curr_token  # type
        self.__advance_tokenizer()
        var_name = self.__curr_token  # variable name
        self.__symbol_table.define(var_name, type, kind)
        self.__advance_tokenizer()
        while self.__curr_token == ",":
            self.__advance_tokenizer()
            var_name = self.__curr_token
            self.__symbol_table.define(var_name, type, kind)
            self.__advance_tokenizer()

    def compile_subroutine_dec(self):
        """
        Compiles all the subroutines located in the class - constructor, methods and functions.
        """
        self.__symbol_table.start_subroutine()
        subroutine_type = self.__curr_token  # constructor / function / method
        self.__advance_tokenizer()
        # return_type = self.__curr_token # return type
        self.__advance_tokenizer()
        self.__curr_subroutine_name = self.__class_name + "." + self.__curr_token  # subroutine name
        self.__advance_tokenizer()  # '('
        # 'this' is always the first in a method's symbol table
        if subroutine_type == 'method':
            self.__symbol_table.define('this', self.__class_name, 'argument')
        self.__advance_tokenizer()
        self.compile_parameter_list()  # parameter list
        self.__advance_tokenizer()  # get next after ')'

        self.__advance_tokenizer()
        while self.__curr_token == "var":
            self.compile_var_dec()
            self.__advance_tokenizer()  # get next after ';'

        self.__vm_writer.write_function(self.__curr_subroutine_name, self.__symbol_table.var_count('var'))
        if subroutine_type == 'constructor':
            self.__vm_writer.write_push('constant', self.__symbol_table.var_count('field'))
            self.__vm_writer.write_call("Memory.alloc", 1)
            self.__vm_writer.write_pop('pointer', 0)
        if subroutine_type == 'method':
            self.__vm_writer.write_push('argument', 0)
            self.__vm_writer.write_pop('pointer', 0)
        self.compile_subroutine_body()

    def compile_parameter_list(self):
        """
        Compiles the parameters list for the subroutine.
        """
        while self.__curr_token != ")":
            type = self.__curr_token
            self.__advance_tokenizer()
            name = self.__curr_token
            self.__symbol_table.define(name, type, "argument")
            self.__advance_tokenizer()
            if self.__curr_token == ",":
                self.__advance_tokenizer()

        # once the loop is finished, curr_token == ")"

    def compile_subroutine_body(self):
        """
        Compiles the main body of the subroutine.
        """
        self.compile_statements()

    def compile_var_dec(self):
        """
        Compiles the subroutine variable declarations.
        """
        kind = self.__curr_token  # 'var'
        self.__advance_tokenizer()
        type = self.__curr_token  # type
        self.__advance_tokenizer()
        name = self.__curr_token  # var name
        self.__symbol_table.define(name, type, kind)
        self.__advance_tokenizer()
        while self.__curr_token == ",":
            self.__advance_tokenizer()  # get next after ','
            name = self.__curr_token  # another var name
            self.__symbol_table.define(name, type, kind)
            self.__advance_tokenizer()
        # ';' - do not advance here

    def compile_statements(self):
        """
        Compiles the statements.
        """
        # no need to advance
        while self.__curr_token in self.STATEMENTS_KEYWORDS:
            if self.__curr_token == "let":
                self.compile_let()
            elif self.__curr_token == "if":
                self.compile_if()
            elif self.__curr_token == "while":
                self.compile_while()
            elif self.__curr_token == "do":
                self.compile_do()
            else:  # return
                self.compile_return()

    def compile_let(self):
        """
        Compiles a let statement.
        """
        self.__advance_tokenizer()  # get next after 'let'
        name = self.__curr_token  # var name
        self.__advance_tokenizer()

        is_array = False
        if self.__curr_token == "[":
            is_array = True
            self.__advance_tokenizer()
            self.compile_expression()  # expression, advance there
            self.__vm_writer.write_push(self.__symbol_table.kind_of(name), self.__symbol_table.index_of(name))
            self.__advance_tokenizer()
            self.__vm_writer.write_arithmetic('add')
        self.__advance_tokenizer()  # get expression after '='
        self.compile_expression()  # expression, advance there
        if is_array:
            self.__vm_writer.write_pop('temp', 0)
            self.__vm_writer.write_pop('pointer', 1)
            self.__vm_writer.write_push('temp', 0)
            self.__vm_writer.write_pop('that', 0)
        else:
            self.__vm_writer.write_pop(self.__symbol_table.kind_of(name), self.__symbol_table.index_of(name))
        self.__advance_tokenizer()

    def compile_if(self):
        """
        Compiles an if statement.
        """
        self.__advance_tokenizer()  # get next after 'if'
        self.__advance_tokenizer()  # get next after '('
        self.compile_expression()  # expression, advance there

        if_true_label = "IF_TRUE" + str(self.__curr_label_counter)
        if_false_label = "IF_FALSE" + str(self.__curr_label_counter)
        end_label = "IF_END" + str(self.__curr_label_counter)
        self.__curr_label_counter += 1

        self.__vm_writer.write_if_go_to(if_true_label)
        self.__vm_writer.write_go_to(if_false_label)
        self.__vm_writer.write_label(if_true_label)
        self.__advance_tokenizer()  # ')'
        self.__advance_tokenizer()  # '{'
        self.compile_statements()  # statements
        self.__advance_tokenizer()
        if self.__curr_token == "else":
            self.__vm_writer.write_go_to(end_label)
            self.__vm_writer.write_label(if_false_label)
            self.__advance_tokenizer()  # 'else'
            self.__advance_tokenizer()  # '{'
            self.compile_statements()  # statements inside else clause
            self.__advance_tokenizer()  # '}'
            self.__vm_writer.write_label(end_label)
        else:
            self.__vm_writer.write_label(if_false_label)

    def compile_while(self):
        """
        Compiles a while statement.
        """
        exp_label = "WHILE_EXP" + str(self.__curr_label_counter)
        end_label = "WHILE_END" + str(self.__curr_label_counter)
        self.__curr_label_counter += 1

        self.__advance_tokenizer()  # while
        self.__vm_writer.write_label(exp_label)
        self.__advance_tokenizer()  # '('
        self.compile_expression()  # expression, advance there
        self.__vm_writer.write_arithmetic("not")
        self.__vm_writer.write_if_go_to(end_label)
        self.__advance_tokenizer()  # ')'
        self.__advance_tokenizer()  # '{'
        self.compile_statements()  # statements
        self.__vm_writer.write_go_to(exp_label)
        self.__vm_writer.write_label(end_label)
        self.__advance_tokenizer()  # '}'

    def compile_do(self):
        """
        Compiles a do statement.
        """
        self.__advance_tokenizer()  # get next after do

        # subroutineCall
        token = self.__curr_token  # subroutineName
        n_args = 0
        self.__advance_tokenizer()
        if self.__curr_token == '.':
            self.__advance_tokenizer()
            # subroutineName
            if self.__symbol_table.type_of(token) is not None:  # a variable
                subroutine_name = self.__symbol_table.type_of(token) + '.' + self.__curr_token
                # self.__symbol_table.define('this', self.__symbol_table.type_of(token), 'argument')
                n_args += 1  # 'this' is an argument
                self.__vm_writer.write_push(self.__symbol_table.kind_of(token), self.__symbol_table.index_of(token))
                # self.__vm_writer.write_pop('pointer', 0)
            else:
                subroutine_name = token + "." + self.__curr_token
            self.__advance_tokenizer()
        else:
            self.__vm_writer.write_push('pointer', 0)
            self.__symbol_table.define('this', self.__class_name, 'argument')
            n_args += 1
            subroutine_name = self.__class_name + '.' + token

        self.__advance_tokenizer()
        n_args += self.compile_expression_list()  # curr_token is ')'
        self.__advance_tokenizer()  # ';'
        self.__advance_tokenizer()
        self.__vm_writer.write_call(subroutine_name, n_args)
        self.__vm_writer.write_pop("temp", 0)

    def compile_return(self):
        """
        Compiles a return statement.
        :return: haha
        """
        self.__advance_tokenizer()  # 'return'
        if self.__curr_token != ';':
            self.compile_expression()  # expression, advance there
        else:  # else, a void method/function, return 0 by default
            self.__vm_writer.write_push("constant", 0)
        self.__vm_writer.write_return()
        self.__advance_tokenizer()

    def compile_expression(self):
        """
        Compiles a single expression.
        """
        # is_array = [False]
        self.compile_term()  # term
        self.__advance_tokenizer()  # check if we have an op afterwards
        while self.__curr_token in self.BINARY_OPS:
            op = self.BINARY_OPS[self.__curr_token]
            self.__advance_tokenizer()
            self.compile_term()
            self.__vm_writer.write_arithmetic(op)
            self.__advance_tokenizer()

    def compile_term(self):
        """
        Compile a term.
        """
        # Integer constant
        if self.__curr_token_type == "integerConstant":
            int_const = self.__curr_token
            self.__vm_writer.write_push("constant", int_const)

        # String constant
        elif self.__curr_token_type == "stringConstant":
            self.__vm_writer.write_push('constant', len(self.__curr_token))
            self.__vm_writer.write_call("String.new", 1)
            for char in self.__curr_token:
                self.__vm_writer.write_push('constant', ord(char))
                self.__vm_writer.write_call('String.appendChar', 2)

        # Keywords
        elif self.__curr_token == 'this':
            self.__vm_writer.write_push('pointer', 0)
        elif self.__curr_token in {'true', 'false', 'null'}:
            self.__vm_writer.write_push('constant', 0)
            if self.__curr_token == 'true':
                self.__vm_writer.write_arithmetic('not')

        # Unary op : |op term| format
        elif self.__curr_token in {'~', '-'}:
            op = 'not' if self.__curr_token == '~' else 'neg'
            self.__advance_tokenizer()
            self.compile_term()
            self.__vm_writer.write_arithmetic(op)

        # Expression
        elif self.__curr_token == '(':
            self.__advance_tokenizer()
            self.compile_expression()
            # ')"

        else:  # either varName, varName followed by [expression], or subroutine call
            token = self.__curr_token
            n_args = 0
            next_token = self.__tokenizer.peek_token()
            if next_token == '(':
                self.__advance_tokenizer()
                self.__vm_writer.write_push('pointer', 0)
                self.__symbol_table.define('this', self.__class_name, 'argument')
                n_args += 1
                subroutine_name = self.__class_name + '.' + token
                self.__advance_tokenizer()
                n_args += self.compile_expression_list()  # advance there through self.compile_expression
                self.__vm_writer.write_call(subroutine_name, n_args)

            elif next_token == '.':
                self.__advance_tokenizer()  # curr_token = '.'
                self.__advance_tokenizer()
                if self.__symbol_table.type_of(token) is not None:  # token is a variable
                    subroutine_name = self.__symbol_table.type_of(token) + '.' + self.__curr_token
                    n_args += 1  # 'this' is an argument
                    self.__vm_writer.write_push(self.__symbol_table.kind_of(token), self.__symbol_table.index_of(token))
                else:
                    subroutine_name = token + "." + self.__curr_token
                self.__advance_tokenizer()
                self.__advance_tokenizer()
                n_args += self.compile_expression_list()
                self.__vm_writer.write_call(subroutine_name, n_args)

            elif next_token == '[':
                self.__advance_tokenizer()  # ']'
                self.__advance_tokenizer()  # expression
                self.compile_expression()
                self.__vm_writer.write_push(self.__symbol_table.kind_of(token),
                                            self.__symbol_table.index_of(token))  # token = arr
                self.__vm_writer.write_arithmetic('add')  # add arr + expression
                self.__vm_writer.write_pop('pointer', 1)
                self.__vm_writer.write_push('that', 0)
            else:
                self.__vm_writer.write_push(self.__symbol_table.kind_of(token), self.__symbol_table.index_of(token))

    def compile_expression_list(self):
        """
        Compile an expression list.
        """
        n_args = 0
        if self.__curr_token == ')':
            return n_args
        # write first expression, advance there
        self.compile_expression()
        n_args += 1
        while self.__curr_token == ',':
            self.__advance_tokenizer()
            self.compile_expression()
            n_args += 1
        return n_args

    def __advance_tokenizer(self):
        """
        Advances the tokenizer to get the next token and token type.
        """
        self.__tokenizer.advance()
        self.__curr_token_type, self.__curr_token = self.__tokenizer.token_type()
