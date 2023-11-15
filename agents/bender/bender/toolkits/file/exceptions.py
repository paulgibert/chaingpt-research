class FileTooBigError(Exception):
    """
    Raised if a file's size is too large for the context
    """
    pass

class UnsupportedLanguage(Exception):
    """
    Raised if a language type is not supported for a file split operation
    """
    pass