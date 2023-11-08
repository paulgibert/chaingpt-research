class PathNotFoundError(Exception):
    def __init__(self):
        super().__init__("The provided path is invalid")


class RepositoryNotFoundError(Exception):
    def __init__(self):
        super().__init__("The provided repository does not exist")


class GenericCloneError(Exception):
    def __init__(self):
        super().__init__("An error occured when attempting to clone the provided repository")