class DefaultException(Exception):
    message: str = "Произошла ошибка"

    def __init__(self, message: str | None = None):
        super().__init__(message or self.message)
