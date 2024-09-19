import os
import sys
import subprocess
import click
import platform
import psutil
import pooch

PID_FILE = 'mariadb_server.pid'
CONFIG_FILE = 'my_custom.cnf'  # Configuration file for non-default port
MARIADB_DIR_ENV_VAR = 'MARIADB_DIR'  # Name of the environment variable


def get_mariadb_dir():
    mariadb_dir = os.getenv(MARIADB_DIR_ENV_VAR)
    if not mariadb_dir:
        raise click.UsageError(f"Environment variable {MARIADB_DIR_ENV_VAR} is not set.")
    return mariadb_dir


@click.group()
def cli():
    pass


@cli.command()
@click.argument('extract_to', type=click.Path())
def download_and_extract(extract_to):
    """Download and extract MariaDB portable version."""
    system = platform.system()
    if system == 'Windows':
        url = "https://archive.mariadb.org/mariadb-11.5.2/winx64-packages/mariadb-11.5.2-winx64.zip"
        hash = "e800794421dfb82699af24b47ecf9efe4add7439b5e5eec33bffa569615c3f3f"
    else:
        url = "https://archive.mariadb.org/mariadb-11.5.2/bintar-linux-systemd-x86_64/mariadb-11.5.2-linux-systemd-x86_64.tar.gz"
        hash = "6fffce126dda54ecaaa3659e03caa47bf5ff6828936001176f84b6bed9637f5c"
    zip_file = pooch.retrieve(
        # URL to one of Pooch's test files
        url=url,
        known_hash=hash,
    )

    click.echo("Unzipping the file...")
    if zip_file.endswith(".zip"):
        subprocess.run(["unzip", zip_file, "-d", extract_to])
    elif zip_file.endswith((".tar.gz", ".tgz")):
        subprocess.run(["tar", "-xzf", zip_file, "-C", extract_to])
    else:
        raise click.BadParameter("Unsupported file format. Only .zip and .tar.gz are supported.")
    click.echo(f"Extracted to: {extract_to}")


@cli.command()
@click.option('--port', default=os.environ.get("MARIADB_PORT", 3307), help="Specify the port to use for MariaDB server.")
def install_db(port):
    """Install the MariaDB database."""
    mariadb_dir = get_mariadb_dir()
    system = platform.system()
    if system == 'Windows':
        bin_dir = os.path.join(mariadb_dir, 'bin')
        install_cmd = os.path.join(bin_dir, 'mariadb-install-db.exe')
    else:
        script_dir = os.path.join(mariadb_dir, 'scripts')
        install_cmd = os.path.join(script_dir, 'mariadb-install-db')

    click.echo("Installing MariaDB database...")
    subprocess.run([install_cmd])

    # Create a custom config file for the specified port
    with open(CONFIG_FILE, 'w') as f:
        f.write("[mysqld]\n")
        f.write(f"port={port}\n")
        f.write("skip-grant-tables\n")
        f.write("max_connections=100\n")       # Allow up to 100 connections
        f.write("max_allowed_packet=64M\n")    # Allow large queries up to 64MB

    click.echo(f"Installation complete. MariaDB will use port {port}.")


@cli.command()
def start_server():
    """Start the MariaDB server in the background."""
    mariadb_dir = get_mariadb_dir()
    system = platform.system()
    if system == 'Windows':
        bin_dir = os.path.join(mariadb_dir, 'bin')
    else:
        bin_dir = os.path.join(mariadb_dir, 'scripts')

    mysqld_cmd = os.path.join(bin_dir, 'mysqld')
    click.echo("Starting MariaDB server in the background...")
    process = subprocess.Popen([mysqld_cmd, '--defaults-file=' + CONFIG_FILE], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    with open(PID_FILE, 'w') as f:
        f.write(str(process.pid))

    click.echo(f"MariaDB server started with PID: {process.pid} with this config file: {CONFIG_FILE}")


@cli.command()
def stop_server():
    """Stop the MariaDB server."""
    if not os.path.exists(PID_FILE):
        click.echo("MariaDB server PID file not found.")
        return

    with open(PID_FILE, 'r') as f:
        pid = int(f.read())

    try:
        p = psutil.Process(pid)
        p.terminate()
        p.wait(timeout=5)
        click.echo("MariaDB server stopped.")
    except (psutil.NoSuchProcess, psutil.TimeoutExpired) as e:
        click.echo(f"Error stopping MariaDB server: {str(e)}")
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)


@cli.command()
@click.argument('database_name')
@click.option('--port', default=os.environ.get("MARIADB_PORT", 3307), help="Port used by the MariaDB server.")
def create_database(database_name, port):
    """Create a new database in MariaDB."""
    mariadb_dir = get_mariadb_dir()
    system = platform.system()
    if system == 'Windows':
        bin_dir = os.path.join(mariadb_dir, 'bin')
    else:
        bin_dir = os.path.join(mariadb_dir, 'scripts')

    mysql_cmd = os.path.join(bin_dir, 'mysql')

    # Test connection
    click.echo("Testing connection...")
    subprocess.run([mysql_cmd, '-u', 'root', f'--port={port}', '--ssl=FALSE', '-e', 'SHOW DATABASES;'])

    # Create database
    create_db_command = f'CREATE DATABASE {database_name};'

    click.echo("Creating database 'msnoise'...")
    result = subprocess.run([mysql_cmd, '-u', 'root', f'--port={port}', '--ssl=FALSE', '-e', create_db_command],
                            capture_output=True, text=True)
    if result.returncode == 0:
        click.echo(f"Database '{database_name}' has been created.")
    else:
        click.echo(f"Failed to drop database '{database_name}'!\nError message:\n{result.stderr}")
        sys.exit(1)

    # List databases
    click.echo("Listing databases...")
    subprocess.run([mysql_cmd, '-u', 'root', f'--port={port}', '--ssl=FALSE', '-e', 'SHOW DATABASES;'])

    click.echo("Database setup completed.")


@cli.command()
@click.argument('database_name')
@click.option('--port', default=os.environ.get("MARIADB_PORT", 3307), help="Port used by the MariaDB server.")
def drop_database(database_name, port):
    """Drop a database in MariaDB."""
    mariadb_dir = get_mariadb_dir()
    system = platform.system()
    if system == 'Windows':
        bin_dir = os.path.join(mariadb_dir, 'bin')
    else:
        bin_dir = os.path.join(mariadb_dir, 'scripts')

    mysql_cmd = os.path.join(bin_dir, 'mysql')
    if database_name in ["information_schema", "mysql", "performance_schema", "sys"]:
        click.echo("You can't drop that database!")
        sys.exit(1)

    # Drop database
    drop_db_command = f'DROP DATABASE {database_name};'

    click.echo(f"Dropping database '{database_name}'...")
    result = subprocess.run([mysql_cmd, '-u', 'root', f'--port={port}', '--ssl=FALSE', '-e', drop_db_command],
                            capture_output=True, text=True)
    if result.returncode == 0:
        click.echo(f"Database '{database_name}' has been dropped.")
    else:
        click.echo(f"Failed to drop database '{database_name}'!\nError message:\n{result.stderr}")


@cli.command()
@click.option('--port', default=os.environ.get("MARIADB_PORT", 3307), help="Port used by the MariaDB server.")
def show_databases(port):
    """Create a new database in MariaDB."""
    mariadb_dir = get_mariadb_dir()
    system = platform.system()
    if system == 'Windows':
        bin_dir = os.path.join(mariadb_dir, 'bin')
    else:
        bin_dir = os.path.join(mariadb_dir, 'scripts')

    mysql_cmd = os.path.join(bin_dir, 'mysql')

    # List databases
    click.echo("Listing databases...")
    subprocess.run([mysql_cmd, '-u', 'root', f'--port={port}', '--ssl=FALSE', '-e', 'SHOW DATABASES;'])

def run():
    cli(obj={})


if __name__ == '__main__':
    cli()
