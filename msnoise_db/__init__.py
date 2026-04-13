from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("msnoise-db")
except PackageNotFoundError:
    # Package not installed (e.g. running from source without pip install -e .)
    __version__ = "unknown"
