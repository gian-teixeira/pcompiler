from dataclasses import dataclass, field, InitVar
from typing import Any
from enum import Enum

from datatype import DataType

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

    @dataclass
    class Block:
        expressions : list[Any] = field(default_factory=lambda : [])

        def asdict(self):
            return {
                "Block": {
                    "expressions": [expr.asdict() for expr in self.expressions]
                }
            }

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
                    "else": self.else_.asdict()
                }
            }

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

    @dataclass
    class Print:
        format_string : str
        args : list[Any] = field(default_factory=lambda : [])

        def asdict(self):
            return {
                "Print": {
                    "format_string": self.format_string.asdict(),
                    "args": [arg.asdict() for arg in args]
                }
            }

    @dataclass
    class Return:
        expression : Any

        def asdict(self):
            return {
                "Return": {
                    "expression": self.expression.asdict(),
                }
            }

    @dataclass
    class Call:
        function : str
        args : list[Any] = field(default_factory=lambda : [])

        def asdict(self):
            return {
                "Call": {
                    "function": self.function,
                    "args": [arg.asdict() for arg in self.args]
                }
            }

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

class AbstractSyntaxTree:
    def __init__(self, function_name):
        self.root = Node.Function(function_name)

