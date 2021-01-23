# envrun

`envrun` is a CLI tool that runs a command with dynamically-sourced env variables.

Currently, only the `keyring` backend is implemented, which uses a libsecret-compatible service, eg. Gnome keyring.

Alternatively, a variable can be sourced from a file, output of an arbitrary coommand, of from the environment.

[PyPi](https://pypi.org/project/envrun/)

This tool is still under heavy development and its API might change at any time. Use with caution.


## Installation
To install using pip, run:

    pip install envrun

Other installation options are not yet available.


## Usage

    envrun [OPTIONS] COMMAND...


To pass options to the invoked command, prepend the command with `--`

    envrun -- ls -hal


Passing a `-i / --interactive` flag will prompt for missing variable values.

    envrun -i ls

If supported by the storage backend, values provided will get stored automatically.


For debugging, invoke the `env` command, which should be available on most Unix-like systems:

    envrun env


### Example .envrun file

    [vars]
    ; Variables can be hardcoded here
    ENV=dev

    [vars.SECRET]
    ; This will set SECRET from Gnome keyring.
    type = keyring

    [vars.MY_PATH]
    ; MY_PATH will be set to the value of the $PATH env variable
    type = env
    key = PATH

    [vars.PWD]
    ; PWD will be set to captured stdout of the pwd command
    type = shell
    command = pwd

    [vars.SSH_PUBKEY]
    ; SSH_PUBKEY will be set to the contents of id_rsa.pub
    type = file
    file = ~/.ssh/id_rsa.pub


## Use cases
### 12-Factor apps
According to the [Twelve-Factor App](https://12factor.net/) methodology, app secrets should be configured from the environment.
`envrun` can neatly support this workflow by keeping the `.envrun` config files in version control and sourcing the config values
from storage backends.

### Infrastructure as code
When running configuration managament and Infrastructure as Code tools, there is often a need to inject secrets into the tool.

`envrun` provides a concise way of defining and passing the variables to tools like `terraform` and `ansible`.

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

    black src

And finally: create a pull request.
