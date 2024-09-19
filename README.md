# MSNoise-DB CLI Tool

This is a Python-based command-line interface (CLI) tool for managing a portable MariaDB server for MSNoise.
The tool allows you to download, extract, install, start, stop, create, and drop databases using MariaDB.

## Features

- Download and extract MariaDB portable version from a URL.
- Install/Setup MariaDB.
- Start MariaDB server in the background.
- Stop MariaDB server.
- Create a new database.
- Drop an existing database.
- Supports custom configurations for port, maximum connections, and large queries.

## Prerequisites

- Python 3.6 or above.
- `click` package: Install using `pip install click`.
- `requests` package: Install using `pip install requests`.
- `psutil` package: Install using `pip install psutil`.
- `configobj` package: Install using `pip install configobj`.

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/ROBelgium/msnoise-db.git
    cd msnoise-db
    ```

2. Install the required Python packages:

    ```sh
    pip install click requests psutil configobj pooch
    ```

4. Install this package:

    ```sh
    pip install -e .
    ```


## Usage

### 1. Download and Extract MariaDB

Download and extract MariaDB portable version from a given URL.

```sh
msnoisedb download_and_extract C:/path/to/extract/to
```

### 2. Install MariaDB

Install MariaDB by specifying the port (default is 3307).

```sh
msnoisedb install_db
```

### 3. Start MariaDB Server

Start the MariaDB server in the background.

```sh
msnoisedb start_server
```

### 4. Stop MariaDB Server

Stop the running MariaDB server.

```sh
msnoisedb stop_server
```

### 5. Create a New Database

Create a new database.

```sh
msnoisedb create_database DATABASE_NAME
```

### 6. Drop an Existing Database

Drop an existing database.

```sh
msnoisedb drop_database DATABASE_NAME
```

## Environment Variable

You should set the `MARIADB_DIR` environment variable to the path where MariaDB is extracted.
This avoids passing the directory path as an argument to each command.

Similarly, if you plan to use another port than the default (3307), you can set the `MARIADB_PORT` environment variable.

### On Windows:

```cmd
set MARIADB_DIR=C:\path\to\extracted\mariadb
set MARIADB_PORT=9307
```

### On Linux/macOS:

```sh
export MARIADB_DIR=/path/to/extracted/mariadb
export MARIADB_PORT=9307
```

## Configuration

The tool makes use of a custom configuration file named `my_custom.cnf` to manage the MariaDB server settings.
The configuration file includes settings such as:

- Port number
- `skip-grant-tables` to allow any user to connect without a password.
- `max_connections` to allow more than the default 10 connections.
- `max_allowed_packet` to allow large query sizes.

## Example Configuration (`my_custom.cnf`)

```ini
[mysqld]
port=3307
skip-grant-tables
max_connections=100
max_allowed_packet=64M
```

## Notes

- **Security Warning**: The `skip-grant-tables` option is included for development and debugging purposes, allowing any user to connect without authentication. This should not be used in a production environment.
- **Supported Platforms**: The tool is designed to work on both Windows and Linux platforms.

## License

This project is licensed under the EUPL License. See the [LICENSE](LICENSE.TXT) file for more details.

## Acknowledgements

- [Click](https://palletsprojects.com/p/click/) for creating powerful command-line interfaces.
- [Requests](https://docs.python-requests.org/en/latest/) for handling HTTP requests.
- [Psutil](https://psutil.readthedocs.io/en/latest/) for process management.
- [ConfigObj](https://configobj.readthedocs.io/en/latest/) for reading and writing configuration files.
- [Pooch](https://www.fatiando.org/pooch/latest/) for downloading the portable zip/tarball.
