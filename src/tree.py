from dataclasses import dataclass, field, InitVar
from typing import Any
from enum import Enum
import json

from datatype import DataType
from log import Logger

class Node:
    @dataclass
    class Error:
        def asdict(self):
            return { "Error" : "!"}

    @dataclass
    class RelOp:
        signal : str = field(default='')
        left : Any = field(default=None)
        right : Any = field(default=None)
        datatype : DataType = field(default=None)

        def asdict(self):
            return {
                "RelOp": {
                    "signal": self.signal,
                    "datatype": self.datatype.value,
                    "left": self.left.asdict(),
                    "right": self.right.asdict(),
                }
            }

        def type_check(self):
            if self.right.datatype != self.left.datatype:
                Logger.semantic_error(f"RelOp : operator `{self.signal}` "
                        f"incompatible with types `{self.left.datatype.value}` "
                        f"and `{self.right.datatype.value}`")
            self.left.type_check()
            self.right.type_check()

    @dataclass
    class AritOp:
        signal : str = field(default='')
        left : Any = field(default=None)
        right : Any = field(default=None)
        datatype : DataType = field(default=None)

        def asdict(self):
            return {
                "AritOp": {
                    "signal": self.signal,
                    "datatype": self.datatype.value,
                    "left": self.left.asdict(),
                    "right": self.right.asdict(),
                }
            }

        def type_check(self):
            if self.right.datatype != self.left.datatype:
                Logger.semantic_error(f"AritOp : operator `{self.signal}` "
                        f"incompatible with types `{self.left.datatype.value}` "
                        f"and `{self.right.datatype.value}`")
            self.left.type_check()
            self.right.type_check()

    @dataclass
    class Assign:
        left : Any = field(default=None)
        right : Any = field(default=None)

        def asdict(self):
            return {
                "Assign": {
                    "left": self.left.asdict(),
                    "right": self.right.asdict(),
                }
            }

        def type_check(self):
            if self.right.datatype != self.left.datatype:
                Logger.semantic_error(f"Assign : variable `{self.left.name}` "
                        f"incompatible with type `{self.right.datatype.value}`")
            self.left.type_check()
            self.right.type_check()

    @dataclass
    class Block:
        expressions : list[Any] = field(default_factory=lambda : [])

        def asdict(self):
            return {
                "Block": {
                    "expressions": [expr.asdict() for expr in self.expressions]
                }
            }

        def type_check(self):
            for expr in self.expressions:
                expr.type_check()

    @dataclass
    class If:
        condition : Any
        block : Any
        else_ : Any

        def asdict(self):
            return {
                "If": {
                    "condition": self.condition.asdict(),
                    "block": self.block.asdict(),
                    "else": self.else_.asdict() if self.else_ is not None else {}
                }
            }

        def type_check(self):
            self.condition.type_check()
            self.block.type_check()
            if self.else_ is not None:
                self.else_.type_check()

    @dataclass
    class While:
        condition : Any
        block : Any

        def asdict(self):
            return {
                "While": {
                    "condition": self.condition.asdict(),
                    "block": self.block.asdict()
                }
            }

        def type_check(self):
            self.condition.type_check()
            self.block.type_check()

    @dataclass
    class Print:
        format_string : str
        args : list[Any] = field(default_factory=lambda : [])

        def asdict(self):
            return {
                "Print": {
                    "format_string": self.format_string,
                    "args": [arg.asdict() for arg in self.args]
                }
            }

        def type_check(self):
            for arg in self.args:
                arg.type_check()

    @dataclass
    class Return:
        expression : Any

        def asdict(self):
            return {
                "Return": {
                    "expression": self.expression.asdict(),
                }
            }

        def type_check(self):
            self.expression.type_check()

    @dataclass
    class Call:
        function : str
        datatype : DataType
        args : list[Any] = field(default_factory=lambda : [])

        def asdict(self):
            return {
                "Call": {
                    "function": self.function,
                    "args": [arg.asdict() for arg in self.args]
                }
            }

        def type_check(self):
            for arg in self.args:
                arg.type_check()

    @dataclass
    class Id:
        name : str
        datatype : DataType

        def asdict(self):
            return {
                "Id": {
                    "name": self.name,
                    "datatype": self.datatype.value
                }
            }

        def type_check(self):
            pass

    @dataclass
    class IntConst:
        value : int
        datatype : InitVar[DataType] = DataType.Int

        def asdict(self):
            return {
                "IntConst": {
                    "value": self.value,
                    "datatype": self.datatype.value
                }
            }

        def type_check(self):
            pass

    @dataclass
    class FloatConst:
        value : float
        datatype : InitVar[DataType] = DataType.Float

        def asdict(self):
            return {
                "FloatConst": {
                    "value": self.value,
                    "datatype": self.datatype.value
                }
            }

        def type_check(self):
            pass

    @dataclass
    class CharConst:
        value : str
        datatype : InitVar[DataType] = DataType.Char

        def asdict(self):
            return {
                "CharConst": {
                    "value": self.value,
                    "datatype": self.datatype.value
                }
            }

        def type_check(self):
            pass

    @dataclass
    class Function:
        name : str
        block : Any = None
        parameters : list[Any] = field(default_factory=lambda : [])

        def asdict(self):
            return {
                "Function": {
                    "name": self.name,
                    "parameters": [param.asdict() for param in self.parameters],
                    "block": self.block.asdict()
                }
            }

        def type_check(self):
            self.block.type_check()
            for param in self.parameters:
                param.type_check()

class AbstractSyntaxTree:
    def __init__(self, function_name):
        self.root = Node.Function(function_name)

