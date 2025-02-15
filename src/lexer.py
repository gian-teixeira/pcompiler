from enum import Enum
from tokens import Token, TokenType

LexerState = Enum('State', [
    'Base',
    'Name',
    'DoubleOperator',
    'Integer',
    'Float',
    'IntConst',
    'FloatConst',
    'CharConst',
    'FormatString'
])

class Lexer:
    @classmethod
    def parse(cls, source : str):
        tokens = []
        for nline, line in enumerate(source.splitlines()):
            tokens += cls.parse_line(line, nline)
        return tokens

    @staticmethod
    def parse_line(line : str, nline : int):
        line += '$'
        tokens = []
        state = LexerState.Base
        buffer = ""
        i = 0
        while True:
            match state:
                case LexerState.Base:
                    if line[i] == '$':
                        new_token = Token.new(buffer, TokenType.Infer, nline)
                        break
                    elif line[i].isspace():
                        new_token = Token.new(buffer, TokenType.Infer, nline)
                        if new_token is not None:
                            tokens.append(new_token)
                        buffer = ""
                    elif line[i] in "()[]{}+*/,;:":
                        before = Token.new(buffer, TokenType.Infer, nline)
                        if before is not None:
                            tokens.append(before)
                        buffer = ""
                        sign = Token.new(line[i], TokenType.Infer, nline)
                        tokens.append(sign)
                    else:
                        if line[i] in "!-=><": state = LexerState.DoubleOperator
                        elif line[i].isalpha(): state = LexerState.Name
                        elif line[i].isnumeric(): state = LexerState.IntConst
                        elif line[i] == '\'': state = LexerState.CharConst
                        elif line[i] == '\"': state = LexerState.FormatString
                        buffer += line[i]
                    i += 1
                case LexerState.DoubleOperator:
                    double_operator = Token.new(buffer+line[i], TokenType.Infer, nline)
                    if double_operator is not None:
                        tokens.append(double_operator)
                        buffer = ""
                        state = LexerState.Base
                        i += 1
                    else:
                        single_operator = Token.new(buffer, TokenType.Infer, nline)
                        tokens.append(single_operator)
                        buffer = ""
                        state = LexerState.Base
                case LexerState.Name:
                    if not line[i].isalnum() and line[i] != '_':
                        name = Token.new(buffer, TokenType.Infer, nline)
                        tokens.append(name)
                        buffer = ""
                        state = LexerState.Base
                    else:
                        buffer += line[i]
                        i += 1
                case LexerState.IntConst:
                    if line[i] == '.':
                        state = LexerState.FloatConst
                        buffer += line[i]
                        i += 1
                    elif not line[i].isnumeric():
                        int_const = Token.new(buffer, TokenType.IntConst, nline)
                        tokens.append(int_const)
                        state = LexerState.Base
                        buffer = ""
                    else:
                        buffer += line[i]
                        i += 1
                case LexerState.FloatConst:
                    if not line[i].isnumeric():
                        float_const = Token.new(buffer, TokenType.FloatConst, nline)
                        tokens.append(float_const)
                        state = LexerState.Base
                        buffer = ""
                    else:
                        buffer += line[i]
                        i += 1
                case LexerState.CharConst:
                    if line[i+1] != '\'':
                        pass # ERROR
                    buffer += line[i:i+2]
                    char_const = Token.new(buffer, TokenType.CharConst, nline)
                    tokens.append(char_const)
                    buffer = ""
                    i += 2
                    state = LexerState.Base
                case LexerState.FormatString:
                    buffer += line[i]
                    if line[i] == '\"':
                        format_string = Token.new(buffer, TokenType.FormatString, nline)
                        tokens.append(format_string)
                        state = LexerState.Base
                    i += 1
        return tokens


