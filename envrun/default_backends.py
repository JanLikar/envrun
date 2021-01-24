import subprocess
from typing import List

import os


from .interfaces import Backend


def get_available() -> List[Backend]:
    return {
        "env": Env,
        "file": File,
        "const": Const,
        "shell": Shell,
    }


class Env(Backend):
    def __getitem__(self, key):
        return os.environ[key]


class File(Backend):
    def __getitem__(self, key: str) -> str:
        # Tilde expansion
        filename = os.path.expanduser(key)

        with open(filename) as f:
            return f.read()


class Const(Backend):
    def __getitem__(self, key: str) -> str:
        return key


class Shell(Backend):
    def __getitem__(self, key: str) -> str:
        print(key)
        r = subprocess.run(
            key, capture_output=True, check=True, shell=True, text=True
        )

        return r.stdout
