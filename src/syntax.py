from copy import deepcopy
import json
from pprint import pprint

from tokens import TokenType, Token
from table import SymbolTable, SymbolTableEntry, FunctionRegister, CallRegister
from tree import AbstractSyntaxTree, Node
from datatype import DataType
from util import DefaultDict
from log import Logger
from error import SyntaticError, SemanticError, CompilerError

def tree_method(func):
    def wrapper(analyzer, *args, **kwargs):
        Logger.log(f"Starting {func.__name__} {analyzer.token.type}")
        node = func(analyzer, *args, **kwargs)
        Logger.log(f"Ending {func.__name__} {node}")
        return node
    return wrapper

class SyntaxAnalyzer:
    def __init__(self, tokens):
        self.tokens = list(reversed(deepcopy(tokens)))
        self.tokens = [Token("$", TokenType.EOF, -1)] + self.tokens

        self.symbol_tables = DefaultDict(lambda key: SymbolTable())
        self.ASTs = DefaultDict(lambda key: AbstractSyntaxTree(key))
        self.function_registers = DefaultDict(lambda key: FunctionRegister(key))

        self.symbol_table_stack = []
        self.AST_stack = []
        self.function_register_stack = []

        self.__program()

    @property
    def token(self):
        if False and self.tokens[-1].type == TokenType.EOF:
            error = (f"found EOF")
            Logger.syntatic_error(error)
            raise SyntaticError(error)
        return self.tokens[-1]

    @property
    def symbol_table(self):
        return self.symbol_table_stack[-1]

    @property
    def AST(self):
        return self.AST_stack[-1]

    @property
    def function_register(self):
        return self.function_register_stack[-1]

    def match(self, expected_type : TokenType):
        if self.token.type != expected_type:
            error_message = f"expected token {expected_type} " \
                    f"but found {self.token.type} on line {self.token.line}"
            Logger.syntatic_error(error_message)
            raise SyntaticError(error_message)
        return self.tokens.pop()

    def search_match(self, expected_type : TokenType):
        while True:
            if len(self.tokens) == 0:
                error_message = f"expected token {expected_type} " \
                        f"but source ended"
                Logger.syntatic_error(error_message)
                raise SyntaticError(error_message)
            if self.token.type == expected_type:
                return self.tokens.pop()
            self.tokens.pop()

    def push_scope(self, function_name : str):
        symbol_table = self.symbol_tables[function_name]
        AST = self.ASTs[function_name]
        function_register = self.function_registers[function_name]

        self.AST_stack.append(AST)
        self.symbol_table_stack.append(symbol_table)
        self.function_register_stack.append(function_register)

    def pop_scope(self):
        self.function_register_stack.pop()
        self.symbol_table_stack.pop()
        self.AST_stack.pop()

    def __program(self):
        self.__function()
        self.__function_sequence()

        logger = Logger.get_instance()
        for function in self.symbol_tables:
            logger.function_info(function, self.symbol_tables[function], self.ASTs[function])

    @tree_method
    def __function(self):
        self.match(TokenType.Function)
        function_name = self.__function_name()
        function_node = Node.Function(function_name.lexeme)
        self.push_scope(function_name.lexeme)
        self.match(TokenType.LBracket)
        self.__parameter_list(function_node)
        self.match(TokenType.RBracket)
        self.__function_return_type()
        function_node.block = self.__block()
        self.pop_scope()
        self.ASTs[function_name.lexeme] = function_node
        return function_node

        #for entry in self.symbol_table:
        #    print(entry)

        AST_dict = function_node.asdict()
        #pprint(AST_dict)
        print(json.dumps(AST_dict, indent=2))

        for entry in self.symbol_table:
            print(entry)

        self.pop_scope()
        return function_node

    @tree_method
    def __function_sequence(self):
        match self.token.type:
            case TokenType.Function:
                function_node = self.__function()
                self.__function_sequence()


    @tree_method
    def __function_name(self):
        match self.token.type:
            case TokenType.Id: return self.match(TokenType.Id)
            case TokenType.Main: return self.match(TokenType.Main)
        self.match(TokenType.Id)

    @tree_method
    def __parameter_list(self, function_node : Node.Function):
        match self.token.type:
            case TokenType.Id:
                arg = self.match(TokenType.Id)
                self.match(TokenType.Colon)
                datatype = self.__type()

                table_entry = self.symbol_table.get_entry(arg.lexeme)
                table_entry.datatype = datatype
                table_entry.is_param = True
                table_entry.pos_param = self.function_register.num_args
                table_entry.call_ref = None
                self.function_register.args.append(arg.lexeme)
                self.function_register.num_args += 1

                id_node = Node.Id(arg.lexeme, datatype)
                function_node.parameters.append(id_node)

                self.__parameter_list_opt(function_node)

    @tree_method
    def __parameter_list_opt(self, function_node : Node.Function):
        match self.token.type:
            case TokenType.Comma:
                self.match(TokenType.Comma)
                arg = self.match(TokenType.Id)
                self.match(TokenType.Colon)
                datatype = self.__type()

                table_entry = self.symbol_table.get_entry(arg.lexeme)
                table_entry.datatype = datatype
                table_entry.is_param = True
                table_entry.pos_param = self.function_register.num_args
                table_entry.call_ref = None
                self.function_register.args.append(arg.lexeme)
                self.function_register.num_args += 1

                id_node = Node.Id(arg.lexeme, datatype)
                function_node.parameters.append(id_node)

                self.__parameter_list_opt(function_node)

    @tree_method
    def __function_return_type(self):
        ret_type = DataType.Void
        match self.token.type:
            case TokenType.Arrow:
                self.match(TokenType.Arrow)
                ret_type = self.__type()
        self.function_register.ret_type = ret_type

    @tree_method
    def __type(self):
        match self.token.type:
            case TokenType.Int:
                self.match(TokenType.Int)
                return DataType.Int
            case TokenType.Float:
                self.match(TokenType.Float)
                return DataType.Float
            case TokenType.Char:
                self.match(TokenType.Char)
                return DataType.Char
        return DataType.Void

    @tree_method
    def __block(self):
        block_node = Node.Block()
        begin = self.match(TokenType.LBrace)
        try:
            self.__sequence(block_node)
        except CompilerError as e:
            Logger.syntatic_error("Ignoring block's content on line {begin.line}")
            self.search_match(TokenType.RBrace)
            return block_node
        self.match(TokenType.RBrace)
        return block_node

    @tree_method
    def __sequence(self, block_node : Node.Block):
        match self.token.type:
            case TokenType.Let:
                self.__declaration()
                self.__sequence(block_node)
            case TokenType.Id | TokenType.If | TokenType.While | TokenType.Println | TokenType.Return:
                command_node = self.__command()
                block_node.expressions.append(command_node)
                self.__sequence(block_node)

    @tree_method
    def __declaration(self):
        self.match(TokenType.Let)
        var_list = self.__var_list()
        self.match(TokenType.Colon)
        datatype : DataType = self.__type();
        self.match(TokenType.PComma)
        for var in var_list:
            if self.symbol_table.has_entry(var.lexeme):
                Logger.semantic_error(f"variable {var.lexeme} "
                        f"already declared on line {var.line}")
            table_entry = self.symbol_table.get_entry(var.lexeme)
            table_entry.datatype = datatype

    @tree_method
    def __var_list(self):
        id = self.match(TokenType.Id)
        return [id] + self.__var_list_opt()

    @tree_method
    def __var_list_opt(self):
        match self.token.type:
            case TokenType.Comma:
                self.match(TokenType.Comma)
                id = self.match(TokenType.Id)
                return [id] + self.__var_list_opt()
        return []

    @tree_method
    def __command(self):
        match self.token.type:
            case TokenType.Id:
                id = self.match(TokenType.Id);
                datatype = DataType.Void
                if not self.symbol_table.has_entry(id.lexeme):
                    Logger.semantic_error(f"name {id.lexeme} "
                            f"not declared in this scope, line {var.line}")
                else:
                    datatype = self.symbol_table.get_entry(id.lexeme).datatype
                id_node = Node.Id(id.lexeme, datatype)
                command_node = self.__attr_or_call(id_node)
                return command_node
            case TokenType.If | TokenType.LBrace: return self.__if()
            case TokenType.While: return self.__while()
            case TokenType.Println: return self.__println()
            case TokenType.Return: return self.__return()

    @tree_method
    def __if(self):
        match self.token.type:
            case TokenType.If:
                self.match(TokenType.If)
                expr_node = self.__expr()
                block_node = self.__block()
                else_node = self.__else()
                return Node.If(expr_node, block_node, else_node)
            case TokenType.LBrace:
                return self.__block()

    @tree_method
    def __else(self):
        match self.token.type:
            case TokenType.Else:
                self.match(TokenType.Else)
                return self.__if()

    @tree_method
    def __while(self):
        self.match(TokenType.While)
        expr_node = self.__expr()
        block_node = self.__block()
        return Node.While(expr_node, block_node)

    @tree_method
    def __println(self):
        self.match(TokenType.Println)
        self.match(TokenType.LBracket)
        format_str = self.mtach(TokenType.FormatString)
        self.match(TokenType.Comma)
        print_node = Node.Print(format_str.lexeme)
        self.__arg_list(print_node, CallRegister("tmp"))
        self.match(TokenType.RBracket)
        self.match(TokenType.PComma)
        return print_node

    @tree_method
    def __return(self):
        self.match(TokenType.Return)
        expr_node = self.__expr()
        self.match(TokenType.PComma)
        return Node.Return(expr_node)

    @tree_method
    def __attr_or_call(self, id_node : Node.Id):
        match self.token.type:
            case TokenType.Attr:
                self.match(TokenType.Attr)
                expr_node = self.__expr()
                assign_node = Node.Assign(id_node, expr_node)
                self.match(TokenType.PComma)
                return assign_node
            case TokenType.LBracket:
                self.match(TokenType.LBracket)
                try:
                    call_node = Node.Call(id_node.name)
                    call_register = CallRegister(id_node.name)
                    call_node = self.__arg_list(call_node, call_register)
                    self.match(TokenType.RBracket)
                    call_entry = self.symbol_table.get_entry(f"{id_node.name}")
                    call_entry.name = id_node.name
                    call_entry.datatype = self.function_register.ret_type
                    call_entry.call_ref = call_register
                    return call_node
                except CompilerError as e:
                    Logger.syntatic_error("Ignoring parenthesis content on line {begin.line}")
                    self.search_match(TokenType.RBracket)
                    return Node.Error()

    @tree_method
    def __expr(self):
        expr_node = self.__rel()
        return self.__expr_opt(expr_node)

    @tree_method
    def __expr_opt(self, expr_node : any):
        match self.token.type:
            case TokenType.EQ | TokenType.NEQ:
                relop_node = self.__op_equal(expr_node)
                relop_node.right = self.__rel()
                return self.__expr_opt(relop_node)
        return expr_node

    @tree_method
    def __op_equal(self, expr_node : any):
        match self.token.type:
            case TokenType.EQ:
                self.match(TokenType.EQ)
                relop_node = Node.RelOp('==', expr_node, None, DataType.Int)
                return relop_node
            case TokenType.NEQ:
                self.match(TokenType.NEQ)
                relop_node = Node.RelOp('!=', expr_node, None, DataType.Int)
                return relop_node

    @tree_method
    def __rel(self):
        add_node = self.__add()
        return self.__rel_opt(add_node)

    @tree_method
    def __rel_opt(self, add_node):
        match self.token.type:
            case TokenType.LT | TokenType.LE | TokenType. GT | TokenType.GE:
                relop_node = self.__op_rel(add_node)
                relop_node.right = self.__add()
                return self.__rel_opt(relop_node)
        return add_node

    @tree_method
    def __op_rel(self, add_node):
        match self.token.type:
            case TokenType.LT:
                self.match(TokenType.LT)
                relop_node = Node.RelOp('<', add_node, None, DataType.Int)
                return relop_node
            case TokenType.LE:
                self.match(TokenType.LE)
                relop_node = Node.RelOp('<=', add_node, None, DataType.Int)
                return relop_node
            case TokenType.GT:
                self.match(TokenType.GT)
                relop_node = Node.RelOp('>', add_node, None, DataType.Int)
                return relop_node
            case TokenType.GE:
                self.match(TokenType.GE)
                relop_node = Node.RelOp('>=', add_node, None, DataType.Int)
                return relop_node

    @tree_method
    def __add(self):
        add_node = self.__term()
        return self.__add_opt(add_node)

    @tree_method
    def __add_opt(self, left_node):
        match self.token.type:
            case TokenType.Plus | TokenType.Minus:
                add_node = self.__op_add(left_node)
                add_node.right = self.__term()
                return self.__add_opt(add_node)
        return left_node

    @tree_method
    def __op_add(self, left_node):
        match self.token.type:
            case TokenType.Plus:
                self.match(TokenType.Plus)
                add_node = Node.AritOp('+', left_node, None, left_node.datatype)
                return add_node
            case TokenType.Minus:
                self.match(TokenType.Minus)
                add_node = Node.AritOp('-', left_node, None, left_node.datatype)
                return add_node

    @tree_method
    def __term(self):
        term_node = self.__factor()
        return self.__term_opt(term_node)

    @tree_method
    def __term_opt(self, left_node):
        match self.token.type:
            case TokenType.Mult | TokenType.Div:
                term_node = self.__op_mult(left_node)
                term_node.right = self.__factor()
                return self.__term_opt(term_node)
        return left_node

    @tree_method
    def __op_mult(self, left_node):
        match self.token.type:
            case TokenType.Mult:
                self.match(TokenType.Mult)
                mult_node = Node.AritOp('*', left_node, None)
                return mult_node
            case TokenType.Div:
                self.match(TokenType.Minus)
                mult_node = Node.AritOp('/', left_node, None)
                return mult_node

    @tree_method
    def __factor(self):
        match self.token.type:
            case TokenType.Id:
                id = self.match(TokenType.Id)
                if not self.symbol_table.has_entry(id.lexeme):
                    Logger.semantic_error(f"name {id.lexeme} "
                            f"not declared in this scope, line {var.line}")
                    datatype = DataType.Void
                else:
                    datatype = self.symbol_table.get_entry(id.lexeme).datatype
                id_node = Node.Id(id.lexeme, datatype)
                return self.__function_call(id_node)
            case TokenType.IntConst:
                int_const = self.match(TokenType.IntConst)
                return Node.IntConst(int(int_const.lexeme))
            case TokenType.FloatConst:
                float_const = self.match(TokenType.FloatConst)
                return Node.floatConst(float(float_const.lexeme))
            case TokenType.CharConst:
                char_const = self.match(TokenType.CharConst)
                return Node.CharConst(char_const.lexeme)
            case TokenType.LBracket:
                self.match(TokenType.LBracket)
                try:
                    expr_node = self.__expr()
                    self.match(TokenType.RBracket)
                    return expr_node
                except CompilerError as e:
                    Logger.syntatic_error("Ignoring parenthesis content on line {begin.line}")
                    self.search_match(TokenType.RBracket)
                    return Node.Error()

    @tree_method
    def __function_call(self, id_node):
        match self.token.type:
            case TokenType.LBracket:
                self.match(TokenType.LBracket)
                try:
                    call_node = Node.Call(id_node.name)
                    call_register = CallRegister(id_node.name)
                    call_node = self.__arg_list(call_node, call_register)
                    self.match(TokenType.RBracket)
                    call_entry = self.symbol_table.get_entry(f"{id_node.name}")
                    call_entry.name = id_node.name
                    call_entry.datatype = self.function_register.ret_type
                    call_entry.call_ref = call_register
                    return call_node
                except CompilerError as e:
                    Logger.syntatic_error("Ignoring parenthesis content on line {begin.line}")
                    self.search_match(TokenType.RBracket)
                    return Node.Error()
        return id_node

    @tree_method
    def __arg_list(self, call_node, call_register):
        match self.token.type:
            case TokenType.Id | TokenType.IntConst | TokenType.FloatConst | TokenType.CharConst:
                arg_node = self.__arg(call_node, call_register)
                return self.__arg_list_opt(call_node, call_register)
        return call_node

    @tree_method
    def __arg_list_opt(self, call_node, call_register):
        match self.token.type:
            case TokenType.Comma:
                self.match(TokenType.Comma)
                arg_node = self.__arg(call_node, call_register)
                return self.__arg_list_opt(call_node, call_register)
        return call_node

    @tree_method
    def __arg(self, call_node, call_register):
        arg_node = None
        arg = None
        match self.token.type:
            case TokenType.Id:
                id = self.match(TokenType.Id)

                if not self.symbol_table.has_entry(id.lexeme):
                    Logger.semantic_error(f"function {id.lexeme} "
                            f"not declared in this scope, line {var.line}")

                call_node = Node.Call(id.lexeme)
                call_register = CallRegister(id.lexeme)
                call_node = self.__function_call(call_node, call_register)

                call_entry = self.symbol_table.get_entry(f"{id.lexeme}:{id.line}")
                call_entry.name = id.lexeme
                call_entry.datatype = self.function_register.ret_type
                call_entry.call_ref = call_register

                return call_node

                id = self.match(TokenType.Id)
                if not self.symbol_table.has_entry(id.lexeme):
                    Logger.semantic_error(f"name {id.lexeme} "
                            f"not declared in this scope, line {var.line}")
                    datatype = DataType.Void
                else:
                    datatype = self.symbol_table.get_entry(id.lexeme).datatype
                arg_node = Node.Id(id.lexeme, datatype)
                arg = id.lexeme
            case TokenType.IntConst:
                int_const = self.match(TokenType.IntConst)
                arg_node = Node.IntConst(int(int_const.lexeme))
                arg = int_const.lexeme
            case TokenType.FloatConst:
                float_const = self.match(TokenType.FloatConst)
                arg_node = Node.floatConst(float(float_const.lexeme))
                arg = float_const.lexeme
            case TokenType.CharConst:
                char_const = self.match(TokenType.CharConst)
                arg_node = Node.CharConst(char_const.lexeme)
                arg = char_const.lexeme
        call_node.args.append(arg_node)
        return call_node


