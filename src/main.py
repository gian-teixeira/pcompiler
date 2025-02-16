from lexer import Lexer
from syntax import SyntaxAnalyzer
from log import Logger
from sys import argv

if __name__ == '__main__':
    with open(argv[1]) as source_file:
        source = source_file.read()

    Logger.init()

    tokens = Lexer.parse(source)
    syntax_analyzer = SyntaxAnalyzer(tokens)

    for function in syntax_analyzer.ASTs:
        node = syntax_analyzer.ASTs[function]
        node.type_check()

    Logger.close()
