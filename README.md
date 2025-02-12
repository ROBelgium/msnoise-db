# MSNoise-DB CLI Tool

This is a Python-based command-line interface (CLI) tool for managing a portable postgresql server for MSNoise.

The tool allows you to install, start, stop, create, and drop databases.

[![Github Action Status](https://github.com/ROBelgium/msnoise-db/actions/workflows/test_linux.yml/badge.svg)](https://github.com/ROBelgium/msnoise-db/actions)


## Features

- Setup PostgreSQL.
- Start PostgreSQL server in the background (custom port by default 8099, configurable)
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
    pip install git+https://github.com/ROBelgium/msnoise-db
    ```

    if your console doesn't have git, you can access the zip directly:

    ```sh
    pip install https://github.com/ROBelgium/msnoise-db/archive.master.zip
    ```
   

3. Create a new folder to store the database data


## Usage

### Start a PostgreSQL Server (and set up if not existing)

Start the PostgreSQL server in the background.

```sh
msnoisedb start
```

### Stop PostgreSQL Server

Stop the running PostgreSQL server.

```sh
msnoisedb stop
```

### Create a New Database

Create a new database.

```sh
msnoisedb create-db DATABASE_NAME
```

### Drop an Existing Database

Drop an existing database.

```sh
msnoisedb drop-db DATABASE_NAME
```

### List databases

Drop an existing database.

```sh
msnoisedb list-db
```

## Configuring an MSNoise project

Create a new project database

```sh
msnoisedb create-db test_database
```

Initialise the db in msnoise:

```sh
msnoise db init
```

```sh
Launching the init
Welcome to MSNoise

What database technology do you want to use?
 [1] sqlite
 [2] mysql
 [3] postgresql
Choice: 3
Server: [localhost]: localhost:5099
Database: [msnoise]: test_database
Username: [msnoise]: msnoise
Password (not shown as you type): msnoise
Table prefix: []:
Installation Done! - Go to Configuration Step!
```


## Notes

- **Supported Platforms**: The tool is designed to work on Windows, Linux and MacOS platforms.

## License

This project is licensed under the EUPL License. See the [LICENSE](LICENSE.TXT) file for more details.

## Acknowledgements

- [Click](https://palletsprojects.com/p/click/) for creating powerful command-line interfaces.
