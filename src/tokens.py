from dataclasses import dataclass
from enum import Enum
import re

from log import Logger

TokenType = Enum('TokenType', [
    'Infer',
    'Ignore',
    'EOF',
    'Id',
    'Int',
    'Float',
    'Char',
    'IntConst',
    'FloatConst',
    'CharConst',
    'LBracket',
    'RBracket',
    'LBrace',
    'RBrace',
    'LCol',
    'RCol',
    'Colon',
    'Comma',
    'PComma',
    'Attr',
    'Not',
    'Plus',
    'Minus',
    'Mult',
    'Div',
    'EQ',
    'NEQ',
    'LT',
    'LE',
    'GT',
    'GE',
    'If',
    'Else',
    'While',
    'Function',
    'Return',
    'Main',
    'Println',
    'Let',
    'FormatString',
    'Arrow'
])

@dataclass
class Token:
    lexeme : str
    type : TokenType
    line : int

    def new(lexeme : str, token_type : TokenType, line : int):
        if token_type == TokenType.Infer:
            match lexeme:
                case ")": token_type = TokenType.RBracket
                case "(": token_type = TokenType.LBracket
                case "}": token_type = TokenType.RBrace
                case "{": token_type = TokenType.LBrace
                case "]": token_type = TokenType.RCol
                case "[": token_type = TokenType.LCol
                case "+": token_type = TokenType.Plus
                case "-": token_type = TokenType.Minus
                case "*": token_type = TokenType.Mult
                case "/": token_type = TokenType.Div
                case ":": token_type = TokenType.Colon
                case ";": token_type = TokenType.PComma
                case ",": token_type = TokenType.Comma
                case "=": token_type = TokenType.Attr
                case ">": token_type = TokenType.GT
                case "<": token_type = TokenType.LT
                case "!=": token_type = TokenType.NEQ
                case "==": token_type = TokenType.EQ
                case ">=": token_type = TokenType.GE
                case "<=": token_type = TokenType.LE
                case "->": token_type = TokenType.Arrow
                case "int": token_type = TokenType.Int
                case "float": token_type = TokenType.Float
                case "char": token_type = TokenType.Char
                case "if": token_type = TokenType.If
                case "else": token_type = TokenType.Else
                case "while": token_type = TokenType.While
                case "fn": token_type = TokenType.Function
                case "return": token_type = TokenType.Return
                case "main": token_type = TokenType.Main
                case "println": token_type = TokenType.Println
                case "let": token_type = TokenType.Let
                case _:
                    if re.match(r"[a-zA-Z0-9_]", lexeme) is not None:
                        token_type = TokenType.Id
                    else:
                        return None
                        Logger.sintatic_error(
                            "Unexpected token "
                            f"`{lexeme}` on line {line}")
        return Token(lexeme, token_type, line)
