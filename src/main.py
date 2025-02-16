from lexer import Lexer
from syntax import SyntaxAnalyzer
from log import Logger

if __name__ == '__main__':
    source = """
    fn min(x : int, y : int) {
        let x : int;
        while(x < y) {
            x = x+1;
        }
        return y;
    }
    """

    tokens = Lexer.parse(source)

    for token in tokens:
        print(token)

    syntax_analyzer = SyntaxAnalyzer(tokens)

    syntax_analyzer.program()

