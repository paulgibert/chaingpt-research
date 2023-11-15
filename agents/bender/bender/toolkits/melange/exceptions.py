class MissingMelangeHeader(Exception):
    """
    Raised if a melange operation is executed before
    a header has been initialized.
    """
    pass