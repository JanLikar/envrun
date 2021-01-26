class Backend:
    def __init__(self, name, interactive, backend_config) -> None:
        self.name = name
        self.interactive = interactive
        self.config = backend_config

    def __setitem__(self, key: str, value: str):
        raise NotImplementedError()

    def __getitem__(self, key: str) -> str:
        """

        Raise a KeyError if the key cannot be found.
        """
        raise NotImplementedError()