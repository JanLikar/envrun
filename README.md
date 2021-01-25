<img src="https://img.shields.io/pypi/v/envrun"/>

`envrun` is a CLI tool that runs a command with dynamically-sourced env variables.

A variable can be sourced from a file, output of an arbitrary coommand, from the environment, or from any [compatible backend](#backends)

[PyPi](https://pypi.org/project/envrun/)

This tool is still under heavy development and its API might change at any time. Use with caution.


## Installation
To install using pip, run:

    pip install envrun

Other installation options are not yet available.


## Usage

    Usage: envrun [OPTIONS] COMMAND...

    Execute COMMAND with env variables from .envrun

    If COMMAND uses flags, prepend it with " -- ".

    Options:
    --non-interactive  Don't prompt for missing variable values.
    --isolated         Don't pass the variables from the outer environment.
    --help             Show this message and exit.


For debugging, invoke the `env` command, which should be available on most Unix-like systems:

    envrun env

If invoking a COMMAND which uses flags, prepend it with " -- ":

    envrun -- ls -al

If wanting to execute multiple commands within the same environment, COMMAND can be passed as a quoted string:

    envrun "ls -a | sort"


### envrun.toml file

Envrun starts searching for a envrun.toml file in the current working directory, checking parent directories
if no envrun.toml file is found.

Variables are namespaced using the following convention:

    vars.<backend>.<var_name> = <var>

The following lines are equivalent:

    vars.<backend>.<var_name> = { key="x }
    vars.<backend>.<var_name> = "x"

The "key" has a backend-specific meaning. Generally, it represents
the most commonly-used setting for a particular backend.

 See https://toml.io/ for file format specifics.


#### Example

    # Variable PWD will be set to the output of `ls -al`
    vars.shell.PWD = "ls -al"

    # MY_PATH will be set to the value of $PATH.
    vars.env.MY_PATH = "PATH"

    [vars.const]
        # Hardcoded vars can be placed here.
        ENV = "development"
        TWO = "2"

    [vars.file.SSH_PUBKEY]
        # SSH_PUBKEY will be set to the contents of id_rsa.pub.
        key = "~/.ssh/id_rsa.pub"


## Backends

  - const (builtin)
  - file (builtin)
  - env (builtin)
  - shell (builtin)
  - [envrun-vault](https://github.com/janlikar/envrun-vault)


## Use cases
### 12-Factor apps
According to the [Twelve-Factor App](https://12factor.net/) methodology, app secrets should be configured from the environment.
`envrun` can neatly support this workflow by keeping the `.envrun.toml` config files in version control and sourcing the config values
from storage backends.

### Infrastructure as code
When running configuration managament and Infrastructure as Code tools, there is often a need to inject secrets into the tool.
Different tools have different ways of handling configuration and secret managament, and they can rarely work together.

Environment variables provide a common ground, as they are supported by the majority of popular tools.

This is where `envrun` comes into play - it provides a concise and extensible way of defining and passing the variables to tools like `terraform` and `ansible`.

### Generating config files
Combined with the excelent [envsubst](https://linux.die.net/man/1/envsubst), `envrun` can be used as a rudimentary templating engine.

    envrun envsubst < nginx.conf.tmpl > nginx.conf

This will generate `nginx.conf` from `nginx.conf.tmpl` and replace all strings like `$VAR` or `${VAR}` with their values - as provided by `envrun`.

## Contributing
Create a virtualenv

    python3 -m venv venv
    . venv/bin/activate

Install the package:

    pip install -e ".[dev]"

Make your changes.

Run code formatter:

    black envrun

And finally: create a pull request.
