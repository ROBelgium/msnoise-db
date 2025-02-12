# MSNoise-DB CLI Tool

This is a Python-based command-line interface (CLI) tool for managing a portable postgresql server for MSNoise.

The tool allows you to download, extract, install, start, stop, create, and drop databases using MariaDB.

[![Github Action Status](https://github.com/ROBelgium/msnoise-db/actions/workflows/test_linux.yml/badge.svg)](https://github.com/ROBelgium/msnoise-db/actions)


## Features

- Setup PostgreSQL.
- Start PostgreSQL server in the background (custom port by default 15432, configurable)
- Stop PostgreSQL server.
- Create a new database.
- Drop an existing database.

## Prerequisites

- Python 3.11 or above.
- `click` package: Install using `conda install -c conda-forge click`.
- `postgresql` package: Install using `conda install -c conda-forge postgresql`.

## Installation

1. Install the code

    ```sh
    pip install pip@git+https://github.com/ROBelgium/msnoise-db

    ```

2. Create a new folder to store the database data


## Usage

### 1. Start a PostgreSQL Server (and set up if not existing)

Start the PostgreSQL server in the background.

```sh
msnoisedb start
```

### 4. Stop PostgreSQL Server

Stop the running PostgreSQL server.

```sh
msnoisedb stop
```

### 5. Create a New Database

Create a new database.

```sh
msnoisedb create-db DATABASE_NAME
```

### 6. Drop an Existing Database

Drop an existing database.

```sh
msnoisedb drop-db DATABASE_NAME
```

## Notes

- **Supported Platforms**: The tool is designed to work on Windows, Linux and MacOS platforms.

## License

This project is licensed under the EUPL License. See the [LICENSE](LICENSE.TXT) file for more details.

## Acknowledgements

- [Click](https://palletsprojects.com/p/click/) for creating powerful command-line interfaces.
