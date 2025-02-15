from lexer import Lexer
from syntax import SyntaxAnalyzer
from log import Logger

if __name__ == '__main__':
    source = """
    fn tmp(x : int, y : int) {
        let a, b : int;
        a = min(x, y);
    }
    """

    tokens = Lexer.parse(source)

    for token in tokens:
        print(token)

    syntax_analyzer = SyntaxAnalyzer(tokens)

    syntax_analyzer.program()

    logger = Logger.get_instance()
    for error in Logger.instance.syntatic_errors:
        print(error)
    for error in Logger.instance.semantic_errors:
        print(error)

