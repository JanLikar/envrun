# envrun

`envrun` is a CLI tool that runs a command with env variables dynamically sourced from specified sources.

Currently, only a `keyring` backend is implemented, which uses libsecret-compatible secrets service, like Gnome keyring.


## Installation
To install using pip, run:

    pip install envrun

Other installation options are not yet available.


## Usage

    envrun [OPTIONS] COMMAND...

To pass options to the called command, prepend it with `--`

    envrun -- ls -hal


Passing the `-i / --interactive` flag will prompt for missing variable values. 

    envrun -i ls

If supported by the storage backend, the provided values will automatically get stored.


For debugging, invoke the `env` command, which should be available on most Unix-like systems:

    envrun env


### Example .envrun file

    [vars]
    ; Statically set environment variables
    ENV=dev

    [vars.PASSWORD]
    ; Sourced from the system keyring (Gnome keyring)
    type = keyring

    [vars.PATH]
    ; Passed from environment
    type = env


## Usecases

### 12-Factor apps
According to the (Twelve-Factor App)[https://12factor.net/] methodology, app secrets should be configured from the environment.
`envrun` can neatly support this workflow by keeping the `.envrun` config files in version control and sourcing the config values
from storage backends.

### Local development


### Generating config files
Combined with the excelent (envsubst)[https://linux.die.net/man/1/envsubst], `envrun` can be used as a rudimentary templating engine.

    envrun envsubst < nginx.conf.tmpl > nginx.conf

This will generate `nginx.conf` from `nginx.conf.tmpl` and replace all strings like `$VAR` or `${VAR}` with their values - as provided by `envrun`.

## Contributing
Create a virtualenv

    python3 -m venv venv
    . venv/bin/activate

Install the package

    pip install -e ".[dev]"

Make your changes.


### Updating dependencies
Update `dev_require` in `setup.py` and run

    pip-compile
