from dataclasses import dataclass, field
from datatype import DataType

@dataclass
class CallRegister:
    name : str
    num_args : int = field(default=0)
    args : list[str] = field(default_factory=lambda : [])

@dataclass
class FunctionRegister:
    name : str
    num_args : int = field(default=0)
    args : list[str] = field(default_factory=lambda : [])
    ret_type : DataType = field(default=DataType.Void)

@dataclass
class SymbolTableEntry:
    name : str
    datatype : DataType = field(default=DataType.Void)
    is_param : bool = field(default=False)
    pos_param : int = field(default=-1)
    call_ref : FunctionRegister | None = field(default=None)

class SymbolTable:
    def __init__(self):
        self.entries : dict[str, SymbolTableEntry] = dict()

    def has_entry(self, key):
        return key in self.entries

    def get_entry(self, key):
        if not key in self.entries:
            self.entries[key] = SymbolTableEntry(key)
        return self.entries[key]

    def __iter__(self):
        for item in self.entries.items():
            yield item

