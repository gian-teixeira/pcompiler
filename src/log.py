import json
from pprint import pprint
import os

class Logger:
    log_folder = "log"
    semantic_errors_filename = "semantic_errors"
    syntatic_errors_filename = "syntatic_errors"
    function_info_filename_prefix = "function_"
    instance = None

    def __init__(self):
        os.makedirs("log", exist_ok=True)
        self.semantic_errors_file = open(f"{self.log_folder}/{self.semantic_errors_filename}.txt", "w+")
        self.syntatic_errors_file = open(f"{self.log_folder}/{self.syntatic_errors_filename}.txt", "w+")

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
    def function_info(cls, function_name, symbol_table, root_node):
        with open(f"{cls.log_folder}/{cls.function_info_filename_prefix}"
                  f"{function_name}_AST_AST.txt", "w+") as file:
            file.write(json.dumps(root_node.asdict(), indent=1))
