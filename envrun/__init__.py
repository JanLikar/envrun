from typing import Optional

import click
import toml

import configparser
import os
import shlex
import subprocess
import sys
import typing


@click.command()
@click.option(
    "--config",
    "-c",
    "config_file",
    type=click.Path(),
    default=".envrun.toml",
    show_default=True,
)
@click.option(
    "-p",
    "--prefix",
    help="Set a prefix to allow multiple independent sets of variables.",
    default="",
)
@click.option("--interactive/--non-interactive", "-i/", default=False)
@click.argument("command", required=True, nargs=-1)
def main(config_file, prefix, interactive,  command):
    """Execute COMMAND with env variables from .envrun

    If COMMAND uses flags, prepend it with " -- ".
    """
    config = toml.load(config_file )

    env = get_vars(config, prefix, interactive, environ=os.environ)

    try:
        r = subprocess.run(command, env=env)
        sys.exit(r.returncode)
    except FileNotFoundError:
        bail(f"Command not found: {command[0]}")


def get_vars(config, prefix: str, interactive: bool, environ):
    var_definitions = config["vars"]

    output_vars = {}

    for (var_name, var) in var_definitions.items():
        if isinstance(var, str):
            output_vars[var_name] = var

        else:
            var_key = var.get("key", var_name)
            var_type = var["type"]

            if var_type == "keyring":
                secret = get_gnome_keyring(prefix, var_key, interactive)

                if secret is None:
                    secret = handle_missing(var_key, interactive)
                    set_gnome_keyring(prefix, var_key, secret, interactive)

            elif var_type == "env":
                secret = environ.get(var_key)

                if secret is None:
                    secret = handle_missing(var_key, interactive)
            elif var_type == "shell":
                command = var["command"]

                secret = get_from_command(command)
            elif var_type == "file":
                # Tilde expansion
                filename = os.path.expanduser(var["file"])

                with open(filename) as f:
                    secret = f.read()

            else:
                bail(f"Unsupported var type: {var_type} for {var_name}")

            output_vars[var_key] = secret

    return output_vars


def handle_missing(key: str, interactive: bool) -> str:
    if interactive:
        return input(f"Value for {key}> ")
    else:
        bail(f"Key {key} not set. Use -i")


def get_from_command(command: str) -> str:
    r = subprocess.run(
        shlex.split(command), capture_output=True, check=True, shell=True, text=True
    )

    return r.stdout


def get_gnome_keyring(prefix: str, key: str, interactive: bool) -> typing.Optional[str]:
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
        secret.encode("utf-8"),
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
