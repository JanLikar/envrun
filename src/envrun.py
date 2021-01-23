from typing import Optional
import click

import configparser
import os
import subprocess
import sys
import typing


@click.command()
@click.option(
    "--config",
    "-c",
    "config_file",
    type=click.Path(),
    default=".envrun",
    show_default=True,
)
@click.option("-p", "--prefix", default="")
@click.option("--interactive/--non-interactive", "-i/", default=False)
@click.argument("command", required=True, nargs=-1)
def main(config_file, prefix, interactive, command):
    config = configparser.ConfigParser()

    # Make config file case-sensitive
    config.optionxform = lambda o: o

    config.read(config_file)

    env = get_vars(config, prefix, interactive, environ=os.environ)

    try:
        r = subprocess.run(command, env=env)
        sys.exit(r.returncode)
    except FileNotFoundError:
        bail(f"Command not found: {command[0]}")


def get_vars(config, prefix: str, interactive: bool, environ):
    vars = {}

    for k in config:
        if k == "DEFAULT":
            continue

        if k == "vars":
            vars = {**vars, **config[k]}

        elif k.startswith("vars."):
            key = k[5:]
            var_type = config[k]["type"]

            if var_type == "keyring":
                secret = get_gnome_keyring(prefix, key, interactive)

                if secret is None:
                    secret = handle_missing(key, interactive)
                    set_gnome_keyring(prefix, key, secret)

            elif var_type == "env":
                secret = environ.get(key)

                if secret is None:
                    secret = handle_missing(key, interactive)

            else:
                bail(f"Unsupported var type: {var_type} in {k}")

            vars[key] = secret


def handle_missing(key: str, interactive: bool):
    if interactive:
        val = input(f"Value for {key}")
    else:
        bail(f"Key {key} not set. Use -i")


def get_gnome_keyring(prefix:str, key:str, interactive: bool) -> typing.Optional[str]:
    import secretstorage

    connection = secretstorage.dbus_init()
    collection = secretstorage.get_default_collection(connection)

    ensure_unlocked(collection, interactive)

    secret = next(
        collection.search_items(
            {"application": "envrun", "prefix": str(prefix), "key": str(key)}
        ),
        None,
    )

    if not secret:
        return None

    return secret.get_secret()


def set_gnome_keyring(prefix: str, key: str, secret: str, interactive: bool):
    import secretstorage

    connection = secretstorage.dbus_init()
    collection = secretstorage.get_default_collection(connection)

    ensure_unlocked(collection, interactive)

    item = collection.create_item(
        f"MyApp: {key}",
        {"application": "envrun", "prefix": str(prefix), "key": key},
        secret,
    )


def ensure_unlocked(collection, interactive: bool):
    if not collection.is_locked():
        return

    if interactive:
        collection.unlock()
        return

    bail("Secret storage locked. Unlock it or run with -i flag.")


def eprint(*args, **kwargs):
    """Print to stderr."""
    print(*args, file=sys.stderr, **kwargs)


def bail(error: str):
    """Print message to stderr and exit with an error code."""
    eprint(error)
    sys.exit(1)
