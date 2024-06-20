# Tryton\src\docker_operations.py
import subprocess
from .logs.config_logger import configurar_logging
from .utils.command_utils import countdown

# Configurar el logger
logger = configurar_logging()

def run_docker_command(docker_command, success_message, error_message):
    try:
        result = subprocess.run(docker_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info(success_message)
        return result.stdout.decode()
    except subprocess.CalledProcessError as e:
        logger.error(f"{error_message}: {e.stderr.decode().strip()}")
        raise

def check_if_container_exists(container_name):
    """Verifica si un contenedor Docker está en ejecución."""
    try:
        result = subprocess.run(['docker', 'ps', '--filter', f'name={container_name}', '--filter', 'status=running', '--format', '{{.Names}}'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        running_containers = result.stdout.decode().splitlines()
        return container_name in running_containers
    except subprocess.CalledProcessError:
        return False

def create_and_start_container(container_name):
    """Crea e inicia los contenedores Docker necesarios para Tryton."""
    docker_commands = {
        "tryton-postgres": [
            'docker', 'run', '--name', 'tryton-postgres', '-e', 'POSTGRES_PASSWORD=mysecretpassword', '-e', 'POSTGRES_DB=tryton', '-d', 'postgres'
        ],
        "tryton": [
            'docker', 'run', '--name', 'tryton', '-p', '8000:8000', '--link', 'tryton-postgres:postgres', '-e', 'DB_PASSWORD=mysecretpassword', '-d', 'tryton/tryton'
        ]
    }

    while True:
        try:
            subprocess.run(docker_commands[container_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info(f"Contenedor {container_name} creado e iniciado exitosamente.")
            break
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.decode().strip()
            logger.error(f"Fallo al crear e iniciar el contenedor {container_name}: {error_message}")
            countdown(10, "Reintentando creación y inicio del contenedor")

def setup_tryton_database():
    """Configura la base de datos para Tryton."""
    while True:
        try:
            subprocess.run(['docker', 'run', '--link', 'tryton-postgres:postgres', '-e', 'DB_PASSWORD=mysecretpassword', '-it', 'tryton/tryton', 'trytond-admin', '-d', 'tryton', '--all'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info("Base de datos de Tryton configurada exitosamente.")
            break
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.decode().strip()
            logger.error(f"Fallo al configurar la base de datos de Tryton: {error_message}")
            countdown(10, "Reintentando configuración de la base de datos de Tryton")
