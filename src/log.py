import json
from pprint import pprint
import os

class Logger:
    instance = None

    def __init__(self):
        os.makedirs("log", exist_ok=True)
        self.semantic_errors_file = open(f"log/semantic_errors.txt", "w+")
        self.syntatic_errors_file = open(f"log/syntatic_errors.txt", "w+")
        self.general_file = open(f"log/log.txt", "w+")

    @classmethod
    def init(cls):
        cls.instance = cls()

    @classmethod
    def close(cls):
        logger = cls.get_instance()
        logger.semantic_errors_file.close()
        logger.syntatic_errors_file.close()
        logger.general_file.close()

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance

    @classmethod
    def syntatic_error(cls, desc : str):
        logger = cls.get_instance()
        logger.syntatic_errors_file.write(f"{desc}\n")

    @classmethod
    def semantic_error(cls, desc : str):
        logger = cls.get_instance()
        logger.semantic_errors_file.write(f"{desc}\n")

    @classmethod
    def log(cls, message : str):
        logger = cls.get_instance()
        logger.general_file.write(f"{message}\n")

    @classmethod
    def function_info(cls, function_name, symbol_table, root_node):
        with open(f"log/function_{function_name}_AST.txt", "w+") as file:
            file.write(json.dumps(root_node.asdict(), indent=1))
        with open(f"log/function_{function_name}_ST.txt", "w+") as file:
            for entry in symbol_table:
                file.write(str(entry)+'\n')

    @classmethod
    def token_list(cls, tokens):
        with open(f"log/tokens.txt", "w+") as file:
            for token in tokens:
                file.write(f"{str(token)}\n")

