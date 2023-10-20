
import re

#token values
tok_type_iden="Identifier"
tok_type_op="Operator"
tok_type_const="Constant"
tok_type_key="Keyword"
tok_type_ss="Special Symbols"
tok_type_pun="Punctuations"
tok_type_str = "String"
keywords = ['False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class',
           'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global',
           'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
           'try', 'while', 'with', 'yield','print','true','false']
#error handling

class Error:
    def __init__(self,err_name,details):
        self.err_name = err_name
        self.details = details
    def as_string(self):
        result = f'{self.err_name}:{self.details}'
        return result
class IllegalCharacterError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__('Illegal Character', details)
        self.pos_start = pos_start
        self.pos_end = pos_end

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def jump(self, current_char):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

#token classs
class Tok:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value:
            return f"{self.type}:{self.value}"
        return f"{self.type}"

class Lex:
    def __init__(self,fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1,0,-1,fn,text)
        self.cur_char = None
        self.jump()

    def jump(self):
        self.pos.jump(self.cur_char)
        self.cur_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_string(self):
        string = ''
        pos_start = self.pos.copy()
        escape_character = False
        self.jump()

        escape_characters = {
            'n': '\n',
            't': '\t',
        }

        while self.cur_char is not None and (self.cur_char != '"' or escape_character):
            if escape_character:
                if self.cur_char in escape_characters:
                    string += escape_characters[self.cur_char]
                else:
                    string += self.cur_char
                escape_character = False
            else:
                if self.cur_char == '\\':
                    escape_character = True
                else:
                    string += self.cur_char
            self.jump()

        if self.cur_char == '"':
            self.jump()

        return Tok(tok_type_str, string)
    
    def skip_comment(self):
                while self.cur_char is not None and self.cur_char != '\n':
                 self.jump()

    def create_tok(self):
        tokens = []
        while self.cur_char is not None:
            if self.cur_char in ' \t':
                self.jump()
            elif self.cur_char == '"':
                tokens.append(self.make_string())
            elif self.cur_char == '#':
                 tokens.append(self.skip_comment())
                 
            elif re.match(r'^[^\d\W]\w*\Z', self.cur_char):
                identifier_value = self.cur_char
                self.jump()
                while self.cur_char and self.cur_char.isalnum():
                    identifier_value += self.cur_char
                    self.jump()
                if identifier_value in keywords:
                    tokens.append(Tok(tok_type_key, identifier_value))
                else:
                    tokens.append(Tok(tok_type_iden, identifier_value)) 
            elif re.match(r'^[+\-/=*%]', self.cur_char):
                tokens.append(Tok(tok_type_op, self.cur_char))
                self.jump()
            
            elif re.match(r'^[+-]?\d+(\.\d+)?', self.cur_char):
                tokens.append(Tok(tok_type_const, self.cur_char))
                self.jump()
            elif re.match(r'[!@#$%^&]', self.cur_char):
                tokens.append(Tok(tok_type_ss, self.cur_char))
                self.jump()
            elif re.match(r'[*()_+=\-[\]{}|;:\'",.<>/?]', self.cur_char):
                tokens.append(Tok(tok_type_pun, self.cur_char))
                self.jump()
            elif self.cur_char == '"':
                tokens.append(self.create_string())
            else:
                pos_start = self.pos.copy()
                char = self.cur_char
                self.jump()
                return [], IllegalCharacterError(pos_start, self.pos, "'" + char + "'")

        return tokens, None
def run(fn, text):
    lexer = Lex(fn, text)
    tokens, error = lexer.create_tok()
    return tokens, error   
