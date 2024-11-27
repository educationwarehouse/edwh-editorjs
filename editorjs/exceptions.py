class TODO(NotImplementedError):
    def __init__(self, msg: str = "todo"):
        super().__init__(msg)


class Unreachable(NotImplementedError):
    def __init__(self, msg: str = "unimplemented"):
        super().__init__(msg)
