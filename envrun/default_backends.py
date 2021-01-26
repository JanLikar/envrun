import subprocess
from typing import List, Optional

import os


from .interfaces import Backend
from .utils import bail


def get_available() -> List[Backend]:
    return {
        "env": Env,
        "file": File,
        "const": Const,
        "shell": Shell,
        "keyring": Keyring,
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
        r = subprocess.run(
            key, capture_output=True, check=True, shell=True, text=True
        )

        return r.stdout


class Keyring(Backend):
    def __getitem__(self, key: str) -> Optional[str]:
        import secretstorage

        connection = secretstorage.dbus_init()
        collection = secretstorage.get_default_collection(connection)

        self._ensure_unlocked(collection, self.interactive)

        try:
            secret = next(
                collection.search_items(
                    {"application": "envrun", "key": str(key)}
                )
            )
        except StopIteration:
            raise KeyError()

        return secret.get_secret()

    def __setitem__(self, key: str, secret: str):
        import secretstorage

        connection = secretstorage.dbus_init()
        collection = secretstorage.get_default_collection(connection)

        self._ensure_unlocked(collection, self.interactive)

        item = collection.create_item(
            f"envrun-{key}",
            {"application": "envrun", "key": key},
            secret.encode("utf-8"),
        )

    def _ensure_unlocked(self, collection, interactive: bool):
        if not collection.is_locked():
            return

        if interactive:
            collection.unlock()
            return

        bail("Secret storage locked. Unlock it or run with -i flag.")
