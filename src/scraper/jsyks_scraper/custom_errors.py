# Custom errors and exceptions for the JSYKS scraper module.

class JSYKSConnectionError(ConnectionError):
    """
    Custom error for connection errors to the JSYKS website.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class JSYKSContentRetrievalError(ConnectionError):
    """
    Custom error for when the content of a question cannot be retrieved
    because the jsyks website is formatted differently than expected.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class ConfigError(LookupError):
    """
    Custom error for a missing or incorrectly formatted configuration file.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
