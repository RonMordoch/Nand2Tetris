class CompilationEngine:
    """
    A CompilationEngine for the Jack language.
    """

    def __init__(self, tokenizer, output_file):
        """
        Initiliazes a CompilationEngine object.
        :param tokenizer: the input file stream
        :param output_file: output file stream to write into.
        """
        self.__tokenizer = tokenizer  # input file stream
        self.__out_file = output_file  # output file stream
        self.__indentation = 2  # current indentation
        self.__curr_token = ""  # curr token being processed
        self.__curr_token_type = ""  # curr token type
        self.__advance_tokenizer()  # advances the tokenizer

    def compile_class(self):
        """
        Compiles the entire class file.
        """
        self.__out_file.write("<class>\n")

        self.__print_line()
        self.__advance_tokenizer()
        self.__print_line()
        self.__advance_tokenizer()
        self.__print_line()
        self.__advance_tokenizer()
        # compiles class static members or fields
        while self.__curr_token == "static" or self.__curr_token == "field":
            self.compile_class_var_dec()
            self.__advance_tokenizer()
        # compiles all the functions in the class
        while self.__curr_token == "constructor" or self.__curr_token == "function" or self.__curr_token == "method":
            self.compile_subroutine_dec()
            self.__advance_tokenizer()
        self.__print_line()
        self.__out_file.write("</class>\n")

    def compile_class_var_dec(self):
        """
        Compiles class' variables declarations.
        """
        self.__open_section("<classVarDec>")
        # static or field
        self.__print_line()
        self.__advance_tokenizer()
        # type
        self.__print_line()
        self.__advance_tokenizer()
        # variable name
        self.__print_line()
        # get next token
        self.__advance_tokenizer()
        while self.__curr_token == ",":
            self.__print_line()
            self.__advance_tokenizer()
            self.__print_line()
            self.__advance_tokenizer()
        # ';'
        self.__print_line()

        self.__close_section("</classVarDec>")

    def compile_subroutine_dec(self):
        """
        Compiles all the subroutines located in the class - constructor, methods and functions.
        """
        self.__open_section("<subroutineDec>")

        # constructor / function / method
        self.__print_line()
        self.__advance_tokenizer()
        # return type
        self.__print_line()
        self.__advance_tokenizer()
        # subroutine name
        self.__print_line()
        self.__advance_tokenizer()
        # '('
        self.__print_line()
        self.__advance_tokenizer()
        # parameter list
        self.compile_parameter_list()
        # ')'
        self.__print_line()
        self.__advance_tokenizer()
        # subroutine body
        self.compile_subroutine_body()

        self.__close_section("</subroutineDec>")

    def compile_parameter_list(self):
        """
        Compiles the parameters list for the subroutine.
        """
        self.__open_section("<parameterList>")

        while self.__curr_token != ")":
            self.__print_line()
            self.__advance_tokenizer()
        # once the loop is finished, curr_token == ")"
        self.__close_section("</parameterList>")

    def compile_subroutine_body(self):
        """
        Compiles the main body of the subroutine.
        """
        self.__open_section("<subroutineBody>")

        # '{'
        self.__print_line()
        self.__advance_tokenizer()
        #
        while self.__curr_token == "var":
            self.compile_var_dec()
            self.__advance_tokenizer()
        self.compile_statements()
        # '}'
        self.__print_line()

        self.__close_section("</subroutineBody>")

    def compile_var_dec(self):
        """
        Compiles the subroutine variable declarations.
        """
        self.__open_section("<varDec>")
        # 'var'
        self.__print_line()
        self.__advance_tokenizer()
        # type
        self.__print_line()
        self.__advance_tokenizer()
        # var name
        self.__print_line()
        self.__advance_tokenizer()

        while self.__curr_token == ",":
            # ','
            self.__print_line()
            self.__advance_tokenizer()
            # another var name
            self.__print_line()
            self.__advance_tokenizer()
        # ';'
        self.__print_line()
        # do not advance
        self.__close_section("</varDec>")

    def compile_statements(self):
        """
        Compiles the statements.
        """
        self.__open_section("<statements>")

        # no need to advance do not change!
        while self.__curr_token == "if" or self.__curr_token == "while" or self.__curr_token == "let" or \
                self.__curr_token == "do" or self.__curr_token == "return":
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
            # self.__advance_tokenizer()

        self.__close_section("</statements>")

    def compile_let(self):
        """
        Compiles a let statement.
        """
        self.__open_section("<letStatement>")

        # 'let'
        self.__print_line()
        self.__advance_tokenizer()
        # var name
        self.__print_line()
        self.__advance_tokenizer()
        if self.__curr_token == "[":
            self.__print_line()  # print '['
            self.__advance_tokenizer()
            self.compile_expression()  # expression, advance there

            self.__print_line()  # ']'
            self.__advance_tokenizer()
        self.__print_line()  # '='
        self.__advance_tokenizer()
        self.compile_expression()  # expression, advance there

        self.__print_line()  # ';'
        self.__advance_tokenizer()

        self.__close_section("</letStatement>")

    def compile_if(self):
        """
        Compiles an if statement.
        """
        self.__open_section("<ifStatement>")

        # 'if'
        self.__print_line()
        self.__advance_tokenizer()
        # '('
        self.__print_line()
        self.__advance_tokenizer()
        # expression, advance there
        self.compile_expression()

        # ')'
        self.__print_line()
        self.__advance_tokenizer()
        # '{'
        self.__print_line()
        self.__advance_tokenizer()
        # statements
        self.compile_statements()
        # dont advance, print '}'
        self.__print_line()
        self.__advance_tokenizer()
        if self.__curr_token == "else":
            self.__print_line()  # 'else'
            self.__advance_tokenizer()
            self.__print_line()  # '{'
            self.__advance_tokenizer()
            self.compile_statements()  # statements inside else clause
            self.__print_line()  # do not advance, print '}'
            self.__advance_tokenizer()

        self.__close_section("</ifStatement>")

    def compile_while(self):
        """
        Compiles a while statement.
        """
        self.__open_section("<whileStatement>")

        # while
        self.__print_line()
        self.__advance_tokenizer()
        # '('
        self.__print_line()
        self.__advance_tokenizer()
        # expression, advance there
        self.compile_expression()

        # ')'
        self.__print_line()
        self.__advance_tokenizer()
        # '{'
        self.__print_line()
        self.__advance_tokenizer()
        # statements
        self.compile_statements()
        # dont advance, print '}'
        self.__print_line()
        self.__advance_tokenizer()

        self.__close_section("</whileStatement>")

    def compile_do(self):
        """
        Compiles a do statement.
        """
        self.__open_section("<doStatement>")
        # do
        self.__print_line()
        self.__advance_tokenizer()
        # subroutineCall

        # subroutineName
        self.__print_line()
        self.__advance_tokenizer()
        if self.__curr_token == '.':
            # '.'
            self.__print_line()
            self.__advance_tokenizer()
            # subroutineName
            self.__print_line()
            self.__advance_tokenizer()
        # '('
        self.__print_line()
        self.__advance_tokenizer()
        self.compile_expression_list()
        # curr_token is ')'
        self.__print_line()  # ')'
        self.__advance_tokenizer()
        self.__print_line()  # ';'
        self.__advance_tokenizer()

        self.__close_section("</doStatement>")

    def compile_return(self):
        """
        Compiles a return statement.
        :return: haha
        """
        self.__open_section("<returnStatement>")

        # 'return'
        self.__print_line()
        self.__advance_tokenizer()

        if self.__curr_token != ';':
            # expression, advance there
            self.compile_expression()
        # ';'
        self.__print_line()
        self.__advance_tokenizer()

        self.__close_section("</returnStatement>")

    def compile_expression(self):
        """
        Compiles a single expression.
        """
        self.__open_section("<expression>")

        # term
        self.compile_term()
        # advance here not in compile term
        self.__advance_tokenizer()
        while self.__curr_token in {'+', '-', '*', '/', '&amp;', '|', '&lt;', '&gt;', '='}:
            self.__print_line()
            self.__advance_tokenizer()
            self.compile_term()
            self.__advance_tokenizer()

        self.__close_section("</expression>")

    def compile_term(self):
        """
        Compile a term.
        """
        self.__open_section("<term>")

        # self.__print_line()
        if self.__curr_token_type == "integerConstant" or self.__curr_token_type == "stringConstant" or\
                self.__curr_token in {'true', 'false', 'null', 'this'}:
            self.__print_line()
        elif self.__curr_token in {'~', '-'}:
            self.__print_line()
            self.__advance_tokenizer()
            self.compile_term()
        elif self.__curr_token == '(':  # expression
            self.__print_line()
            self.__advance_tokenizer()
            self.compile_expression()
            self.__print_line()  # ')"
        else:
            self.__print_line()  # print either varName, varName followed by [expression], or subroutine call
            next_token = self.__tokenizer.peek_token()
            if next_token == '(':
                self.__advance_tokenizer()
                self.__print_line()  # print '('
                self.__advance_tokenizer()
                self.compile_expression_list()  # advance there through self.compile_expression
                self.__print_line()  # print ')'
            elif next_token == '.':
                self.__advance_tokenizer()
                self.__print_line()  # print '.'
                self.__advance_tokenizer()
                self.__print_line()  # print subroutineName
                self.__advance_tokenizer()
                self.__print_line()  # print '('
                self.__advance_tokenizer()
                self.compile_expression_list()
                self.__print_line()  # print ')'
            elif next_token == '[':
                self.__advance_tokenizer()
                self.__print_line()
                self.__advance_tokenizer()
                self.compile_expression()
                self.__print_line()  # print ']'
            # else only varName

        self.__close_section("</term>")

    def compile_expression_list(self):
        """
        Compile an expression list.
        """
        self.__open_section("<expressionList>")

        if self.__curr_token == ')':
            self.__indentation -= 2
            self.__out_file.write(self.__indentation * " " + "</expressionList>\n")
            return

        # write first expression, advance there
        self.compile_expression()
        while self.__curr_token == ',':
            self.__print_line()
            self.__advance_tokenizer()
            self.compile_expression()

        self.__close_section("</expressionList>")

    def __open_section(self, section_opening):
        """
        Writes the section opening markup.
        :param section_opening: markup of section opening
        """
        self.__out_file.write(self.__indentation * " " + section_opening + "\n")
        self.__indentation += 2

    def __close_section(self, section_closing):
        """
        Writes the section closing markup.
        :param section_closing: markup of section closing
        """
        self.__indentation -= 2
        self.__out_file.write(self.__indentation * " " + section_closing + "\n")

    def __advance_tokenizer(self):
        """
        Advances the tokenizer to get the next token and token type.
        """
        self.__tokenizer.advance()
        self.__curr_token_type, self.__curr_token = self.__tokenizer.token_type()

    def __print_line(self):
        """
        Prints the format of the line with the current indentation, token type and token.
        """
        self.__out_file.write(self.__indentation * " " + "<" + self.__curr_token_type + "> " + str(
            self.__curr_token) + " </" + self.__curr_token_type + ">" + "\n")
