#!/usr/bin/env python3
import click
import os
import subprocess
import sys
import time
from pathlib import Path


class PostgresManager:
    def __init__(self, data_dir=None, port=5099, host='localhost'):
        self.data_dir = data_dir and Path(data_dir) or Path.cwd() / 'postgres_data'
        self.port = port
        self.host = host
        self.data_dir.parent.mkdir(parents=True, exist_ok=True)

    def init_db(self):
        """Initialize PostgreSQL data directory if it doesn't exist."""
        if not (self.data_dir / 'PG_VERSION').exists():
            click.echo(f"Initializing PostgreSQL data directory at {self.data_dir}")
            subprocess.run(['initdb', '-D', str(self.data_dir)], check=True)

            # Modify pg_hba.conf to allow password authentication
            hba_path = self.data_dir / 'pg_hba.conf'
            with open(hba_path, 'a') as f:
                f.write("\n# MSNoise user authentication\n")
                f.write("host    all             msnoise         127.0.0.1/32            md5\n")
                f.write("host    all             msnoise         ::1/128                 md5\n")
                f.write("host    all             msnoise         localhost               md5\n")
            # Configure postgresql.conf for high number of connections
            conf_path = self.data_dir / 'postgresql.conf'
            click.echo("Configuring postgresql.conf for 1000 connections")
            with open(conf_path, 'a') as f:
                f.write("\n# MSNoise custom settings\n")
                f.write("max_connections = 1000\n")
                f.write("shared_buffers = 256MB\n")  # Increased for many connections
                f.write("listen_addresses = '*'\n")  # Listen on all interfaces

    def create_msnoise_user(self):
        """Create msnoise user with password if it doesn't exist."""
        try:
            create_user_sql = """
            DO
            $do$
            BEGIN
               IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'msnoise') THEN
                  CREATE USER msnoise WITH PASSWORD 'msnoise';
               END IF;
            END
            $do$;
            ALTER USER msnoise CREATEDB;
            """

            # Use subprocess.run instead of Popen for simpler handling
            result = subprocess.run(
                ['psql',
                 '-p', str(self.port),
                 '-h', self.host,
                 '-d', 'postgres',
                 '-U', 'postgres',  # Connect as postgres user initially
                 '-c', create_user_sql
                 ],
                capture_output=True,
                text=True,
                env={
                    **os.environ,
                    'PGPASSWORD': 'postgres'  # Default superuser password on CI
                }
            )

            if result.returncode == 0:
                click.echo("MSNoise user created/verified successfully")
            else:
                click.echo("Failed to create MSNoise user", err=True)
                if result.stderr:
                    click.echo(result.stderr, err=True)
                if result.stdout:
                    click.echo(result.stdout)
                sys.exit(1)

        except subprocess.CalledProcessError as e:
            click.echo(f"Failed to create MSNoise user: {e}", err=True)
            if e.stderr:
                click.echo(e.stderr, err=True)
            sys.exit(1)
        except Exception as e:
            click.echo(f"Unexpected error creating MSNoise user: {e}", err=True)
            sys.exit(1)

    def start_server(self):
        """Start PostgreSQL server."""
        if self.is_server_running():
            click.echo(f"PostgreSQL server is already running on port {self.port}")
            return

        self.init_db()

        cmd = [
            'pg_ctl', 'start',
            '-D', str(self.data_dir),
            '-o', f'-p {self.port} -h {self.host}',
            '-l', str(self.data_dir / 'postgres.log')
        ]

        try:
            subprocess.run(cmd, check=True)
            time.sleep(2)  # Wait for server to start
            click.echo(f"PostgreSQL server started on {self.host}:{self.port}")

            # Create msnoise user after server starts
            self.create_msnoise_user()

        except subprocess.CalledProcessError as e:
            click.echo(f"Failed to start PostgreSQL server: {e}", err=True)
            sys.exit(1)

    def stop_server(self):
        """Stop PostgreSQL server."""
        if not self.is_server_running():
            click.echo("PostgreSQL server is not running")
            return

        cmd = ['pg_ctl', 'stop', '-D', str(self.data_dir)]
        try:
            subprocess.run(cmd, check=True)
            click.echo("PostgreSQL server stopped")
        except subprocess.CalledProcessError as e:
            click.echo(f"Failed to stop PostgreSQL server: {e}", err=True)
            sys.exit(1)

    def create_database(self, db_name):
        """Create a new database."""
        if not self.is_server_running():
            click.echo("PostgreSQL server is not running. Please start it first.", err=True)
            return

        try:
            # Create database owned by msnoise user
            subprocess.run([
                'createdb',
                '-p', str(self.port),
                '-h', self.host,
                '-O', 'msnoise',
                db_name
            ], check=True)
            click.echo(f"Database '{db_name}' created successfully (owned by msnoise)")
        except subprocess.CalledProcessError as e:
            click.echo(f"Failed to create database: {e}", err=True)
            sys.exit(1)

    def drop_database(self, db_name):
        """Drop an existing database."""
        if not self.is_server_running():
            click.echo("PostgreSQL server is not running. Please start it first.", err=True)
            return

        try:
            subprocess.run([
                'dropdb',
                '-p', str(self.port),
                '-h', self.host,
                db_name
            ], check=True)
            click.echo(f"Database '{db_name}' dropped successfully")
        except subprocess.CalledProcessError as e:
            click.echo(f"Failed to drop database: {e}", err=True)
            sys.exit(1)

    def list_databases(self):
        """List all databases."""
        if not self.is_server_running():
            click.echo("PostgreSQL server is not running. Please start it first.", err=True)
            return

        try:
            result = subprocess.run(
                ['psql', '-p', str(self.port), '-h', self.host,
                 '-U', 'msnoise', '-l', ],
                check=True,
                capture_output=True,
                text=True,
                env={**os.environ, 'PGPASSWORD': 'msnoise'}
            )
            click.echo("Available databases:")
            click.echo(result.stdout)
        except subprocess.CalledProcessError as e:
            click.echo(f"Failed to list databases: {e}", err=True)
            if e.stderr:
                click.echo(e.stderr, err=True)
            sys.exit(1)

    def is_server_running(self):
        """Check if PostgreSQL server is running."""
        try:
            subprocess.run(
                ['pg_ctl', 'status', '-D', str(self.data_dir)],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False


# Shared options for all commands
def common_options(f):
    f = click.option('--port', default=5099, help='Port number (default: 5099)')(f)
    f = click.option('--host', default='localhost', help='Listen address (default: localhost)')(f)
    f = click.option('--data-dir', type=click.Path(), help='Custom data directory path')(f)
    return f


@click.group()
def cli():
    """PostgreSQL Server Management CLI for MSNoise

    This CLI tool manages a PostgreSQL server instance configured for MSNoise,
    with automatic user creation (msnoise:msnoise) and appropriate permissions.
    """
    pass


@cli.command()
@common_options
def start(port, host, data_dir):
    """Start PostgreSQL server with MSNoise user configuration"""
    pg_manager = PostgresManager(
        data_dir=data_dir and Path(data_dir),
        port=port,
        host=host
    )
    pg_manager.start_server()


@cli.command()
@common_options
def stop(port, host, data_dir):
    """Stop PostgreSQL server"""
    pg_manager = PostgresManager(
        data_dir=data_dir and Path(data_dir),
        port=port,
        host=host
    )
    pg_manager.stop_server()


@cli.command()
@click.argument('db_name')
@common_options
def create_db(db_name, port, host, data_dir):
    """Create a new database owned by msnoise user"""
    pg_manager = PostgresManager(
        data_dir=data_dir and Path(data_dir),
        port=port,
        host=host
    )
    pg_manager.create_database(db_name)


@cli.command()
@common_options
def list_db(port, host, data_dir):
    """List all databases"""
    pg_manager = PostgresManager(
        data_dir=data_dir and Path(data_dir),
        port=port,
        host=host
    )
    pg_manager.list_databases()


@cli.command()
@click.argument('db_name')
@common_options
def drop_db(db_name, port, host, data_dir):
    """Drop an existing database"""
    pg_manager = PostgresManager(
        data_dir=data_dir and Path(data_dir),
        port=port,
        host=host
    )
    pg_manager.drop_database(db_name)



def run():
    cli(obj={})


if __name__ == '__main__':
    run()
