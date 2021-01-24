import click
import toml

import pkg_resources
import subprocess
import sys
import typing

from . import default_backends


@click.command()
@click.option(
    "--config",
    "-c",
    "config_file",
    type=click.Path(),
    default=".envrun.toml",
    show_default=True,
)
@click.option("--interactive/--non-interactive", "-i/", default=False)
@click.argument("command", required=True, nargs=-1)
def main(config_file, interactive,  command):
    """Execute COMMAND with env variables from .envrun

    If COMMAND uses flags, prepend it with " -- ".
    """
    config = toml.load(config_file )

    env = get_vars(config, interactive)

    try:
        r = subprocess.run(command, env=env)
        sys.exit(r.returncode)
    except FileNotFoundError:
        bail(f"Command not found: {command[0]}")


def get_vars(config, interactive: bool):
    output_vars = {}

    backends = register_backends(config)

    for backend_name, vars in config["vars"].items():
        print(backend_name)
        if backend_name not in backends:
            bail(f"'{backend_name}' backend not found.")

        backend = backends[backend_name]

        for name, conf in vars.items():
            output_vars[name] = get_var(backend, name, conf, interactive)

    return output_vars


def get_var(
    backend: default_backends.Backend,
    name: str,
    conf: typing.Union[str, dict, list],
    interactive: bool
) -> str:
    if not isinstance(conf, (str, dict)):
        bail(f"{name} must be either a string or a mapping.")

    key = _var_key(name, conf)

    try:
        return backend[key]
    except KeyError:
        secret = handle_missing(backend, key, interactive)

        try:
            backend[key] = secret
        except NotImplementedError:
            pass

        return secret


def _var_key(var_name: str, var_conf: typing.Union[str, dict]):
    if isinstance(var_conf, str):
        return var_conf
    elif var_conf.get("key", None) is not None:
        return var_conf["key"]
    else:
        return var_name


def register_backends(config):
    available_backends = default_backends.get_available()
    registered_backends = {}

    for name, backend in available_backends.items():
        registered_backends[name] = backend(name=name, backend_config={})

    available_backends.update(extra_backends())

    for name, backend in config.get("backends", {}).items():
        backend_type = backend["type"]

        if backend_type in available_backends:
            registered_backends[name] = available_backends[backend_type](name=name, backend_config=backend)
        else:
            bail(f"Unsupported backend type: {backend_type}")

    return registered_backends


def extra_backends() -> dict:
    return {
        entry_point.name: entry_point.load()
        for entry_point
        in pkg_resources.iter_entry_points('envrun.backends')
    }


def handle_missing(backend: default_backends.Backend, key: str, interactive: bool) -> str:
    if not interactive:
        bail(f"Key '{backend.name}.{key}' not set. Set it manually or use -i for a prompt.")

    return input(f"Value for {backend.name}.{key}> ")


def eprint(*args, **kwargs):
    """Print to stderr."""
    print(*args, file=sys.stderr, **kwargs)


def bail(error: str):
    """Print message to stderr and exit with an error code."""
    eprint(error)
    sys.exit(1)
