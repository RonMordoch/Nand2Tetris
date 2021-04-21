import re


class JackTokenizer:
    """
    A tokenizer class for the Jack language.
    """
    # Jack language keyword
    KEYWORDS = {"class", "constructor", "function", "method", "field",
                "static", "var", "int", "char", "boolean",
                "void", "true", "false", "null", "this", "let", "do", "if",
                "else", "while", "return"}
    # Jack language symbols
    SYMBOLS = {"{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/",
               "&", "|", "<", ">", "=", "~"}
    # Maximum and minimum integer values supported
    MAX_INT = 32767
    MIN_INT = 0

    def __init__(self, input_file):
        """
        Initializes a tokenizer from an input jack file.
        :param input_file: input jack file
        """
        self.__file = input_file
        # keyword/identifier, symbol, string, int
        self.keyword_identifier_regex = r"\b[a-zA-Z\_]{1}[\w]*\b"
        self.symbol_regex = "[%s]" % re.escape(
            "|".join(self.SYMBOLS))  # re.escape takes care of backslashing all non alphanumeric types
        self.string_regex = r"\"[^\n\"]*\""
        self.int_regex = r"\b(?<!\")[\d]+\b"
        # all patterns into a single string
        self.all_patterns = "|".join([self.symbol_regex,
                                      self.keyword_identifier_regex,
                                      self.string_regex,
                                      self.int_regex])
        # compile into a matcher object
        self.matcher = re.compile(self.all_patterns)

        self.__curr_token = ""
        self.__load_line_tokens()

    def __get_valid_line(self):
        """
        Gets the next valid line to process.
        """
        curr = self.__file.readline()
        while (curr.strip()).startswith("//") or curr == "\n" or (
                curr.replace("\t", "").replace(" ", "")) == "\n" or "/*" in curr:
            start_enclose = curr.find("/*")
            # checks for beginning of multi-line comment
            if start_enclose != -1:
                end_enclose = curr.find("*/")
                if end_enclose != -1:
                    curr = curr[:start_enclose] + curr[end_enclose + 2:]
                else:
                    # checks for /* in string
                    if "\"" in curr:
                        start = curr.find("\"")
                        finish = curr.find("\"", start+1)
                        if start < start_enclose < finish:
                            self.__curr_line = curr
                            return
                    line_start = curr[:start_enclose]
                    # finds end of multi-line comment
                    while end_enclose == -1:
                        curr = self.__file.readline()
                        end_enclose = curr.find("*/")
                    line_end = curr[end_enclose + 2:]
                    curr = line_start + " " + line_end
            else:
                curr = self.__file.readline()
        # checks for comments
        if "//" in curr:
            if "\"" in curr:
                # checks for annoying case of comment in a string (very very very annoying case)
                start = curr.find("\"")
                finish = curr.find("\"", start+1)
                if start < curr.find("//") < finish:
                    self.__curr_line = curr
                    return
            curr = curr[:curr.find("//")]
        self.__curr_line = curr
        return


    def __load_line_tokens(self):
        """
        Loads the current line and splits its token into an array.
        """
        self.__get_valid_line()
        self.__curr_line_tokens = self.matcher.findall(self.__curr_line)

    def has_more_tokens(self):
        """
        Check if there are more tokens.
        :return: true if there are more tokens to process; false otherwise
        """
        if self.__curr_line_tokens:
            return True
        return False  # EOF

    def advance(self):
        """
        Advances the tokenizer if there are more lines.
        """
        if self.has_more_tokens():  # not an empty array, we have tokens inside
            self.__curr_token = self.__curr_line_tokens.pop(0)
            if not self.has_more_tokens():  # finished tokens for current line
                self.__load_line_tokens()

    def token_type(self):
        """
        :return: tuple containing (token_type, token)
        """
        try:
            if self.__curr_token in self.KEYWORDS:
                return "keyword", self.key_word()
            elif self.__curr_token in self.SYMBOLS:
                return "symbol", self.symbol()
            elif self.__curr_token.startswith(
                    "\"") and self.__curr_token.endswith("\""):
                return "stringConstant", self.string_val()
            elif self.MIN_INT <= int(self.__curr_token) <= self.MAX_INT:
                return "integerConstant", self.int_val()
        except ValueError:
            return "identifier", self.identifier()

    def key_word(self):
        """
        :return: token in string format
        """
        return self.__curr_token

    def symbol(self):
        """
        :return: token in string format
        """
        # self.__convert_symbol()
        return self.__curr_token

    def identifier(self):
        """
        :return: token in string format
        """
        return self.__curr_token

    def int_val(self):
        """
        :return: token as in int
        """
        return int(self.__curr_token)

    def string_val(self):
        """
        :return: the string token without the quote marks
        """
        return self.__curr_token[1:-1]

    # def __convert_symbol(self):
    #     """
    #     :return: the correct xml markup of the symbol as described in page 220 in book
    #     """
    #     self.__curr_token = "&lt;" if self.__curr_token == "<" else self.__curr_token
    #     self.__curr_token = "&gt;" if self.__curr_token == ">" else self.__curr_token
    #     self.__curr_token = "&quot;" if self.__curr_token == "\"" else self.__curr_token
    #     self.__curr_token = "&amp;" if self.__curr_token == "&" else self.__curr_token

    def peek_token(self):
        """
        A genius way to deal with looking ahead to get the next token without losing the current one.
        :return: the next token to be processed
        """
        if self.has_more_tokens():
            return self.__curr_line_tokens[0]
