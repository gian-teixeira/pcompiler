class Logger:
    instance = None

    def __init__(self):
        self.syntatic_errors = []
        self.semantic_errors = []

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance

    @classmethod
    def syntatic_error(cls, desc : str):
        logger = cls.get_instance()
        logger.syntatic_errors.append(desc)

    @classmethod
    def semantic_error(cls, desc : str):
        logger = cls.get_instance()
        logger.semantic_errors.append(desc)
