import sys


def eprint(*args, **kwargs):
    """Print to stderr."""
    print(*args, file=sys.stderr, **kwargs)


def bail(error: str):
    """Print message to stderr and exit with an error code."""
    eprint(error)
    sys.exit(1)
