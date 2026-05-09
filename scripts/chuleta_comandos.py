#!/usr/bin/env python3
"""
chuleta_comandos.py

Chuleta practica de Python para scripting DevOps.

Objetivo:
- Tener en un unico archivo los conceptos base de Python.
- Entender quq problema resuelve cada cosa.
- Usar ejemplos 'reales' o practicos para automatizacion, Linux, CI/CD, Kubernetes, GitHub Actions, etc.
"""

# =============================================================================
# 1. COMENTARIOS
# =============================================================================

# Esto es un comentario de una linea.

"""
Esto parece un comentario multilinea.
Tecnicamente es un string multilinea.
Se usa mucho para documentar modulos, clases y funciones.
"""

# =============================================================================
# 2. VARIABLES
# =============================================================================

# En Python no declaras el tipo explicitamente.
# Python detecta el tipo segun el valor asignado.

nombre = "Sergio" # str: texto
edad = 30 # int: numero entero
altura = 1.78 # float: numero decimal
activo = True # bool: verdadero/falso
valor_nulo = None # None: ausencia de valor

# Buenas practicas:
# - Usa nombres descriptivos.
# - Usa snake_case en lugar de CamelCase.
# - Evita nombres como x, y, z salvo ejemplos muy pequeños.

docker_running = True
runner_name = "local-runner"
max_retries = 5

# Constantes:
# Python no tiene constantes reales, pero por convencion se escriben en mayusculas.

API_VERSION = "2022-11-28"
DEFAULT_TIMEOUT = 30

# =============================================================================
# 3. TIPOS DE DATOS BASICOS
# =============================================================================

# str: cadenas de texto
texto = "Hola mundo"

# int: enteros
numero_pods = 3

# float: decimales
cpu_limit = 0.5

# bool: booleanos
is_ready = False

# None: sin valor
resultado = None

# type() es una funcion que permite saber el tipo de una variable.
print(type(texto)) # <class 'str'>
print(type(numero_pods)) # <class 'int'>

# =============================================================================
# 4. CONVERSION DE TIPOS
# =============================================================================

numero_como_texto = "123"

numero = int(numero_como_texto) # str -> int
decimal = float("3.14") # str -> float
texto_numero = str(123) # int -> str
booleano = bool(1) # int -> bool

# =============================================================================
# 5. STRINGS / TEXTO
# =============================================================================

servicio = "api"
entorno = "dev"

# f-string: forma recomendada para insertar variables en texto.
mensaje = f"Desplegando servicio {servicio} en entorno {entorno}"
print(mensaje) # Desplegando servicio api en entorno dev

# Metodos utiles de strings:
texto = "  Kubernetes DevOps  "

print(texto.strip()) # Quita espacios al principio y al final
print(texto.lower()) # minusculas
print(texto.upper()) # mayusculas
print(texto.replace("DevOps", "GitOps")) # Reemplaza texto - Kubernetes GitOps
print(texto.startswith("  Ku")) # Comprueba si empieza por un texto - True
print(texto.endswith("  ")) # Comprueba si termina por un texto - True
print("DevOps" in texto) # Comprueba si contiene una palabra

# Dividir texto:
csv_line = "api,dev,3"
partes = csv_line.split(",")
print(partes) # ['api', 'dev', '3']

# Unir texto:
items = ["pod1", "pod2", "pod3"]
print(",".join(items)) # pod1,pod2,pod3

# =============================================================================
# 6. OPERADORES ARITMETICOS
# =============================================================================

a = 10
b = 3

print(a + b) # suma
print(a - b) # resta
print(a * b) # multiplicacion
print(a / b) # division normal, devuelve float
print(a // b) # division entera
print(a % b) # modulo/resto
print(a ** b) # potencia

# Uso tipico DevOps:
# - Calcular reintentos.
# - Calcular tiempos.
# - Comprobar si un numero es par/impar con %.
# - Calcular porcentajes de uso.

# =============================================================================
# 7. OPERADORES DE COMPARACION
# =============================================================================

print(a == b) # igual
print(a != b) # distinto
print(a > b) # mayor que
print(a < b) # menor que
print(a >= b) # mayor o igual
print(a <= b) # menor o igual

# Uso tipico:
# - Comprobar codigos de salida.
# - Comprobar numero de pods.
# - Comprobar si se supero un limite.

exit_code = 0

if exit_code == 0:
    print("Comando ejecutado correctamente")

# =============================================================================
# 8. OPERADORES LOGICOS
# =============================================================================

docker_ok = True
network_ok = False

print(docker_ok and network_ok) # True solo si ambas son True
print(docker_ok or network_ok) # True si al menos una es True
print(not docker_ok) # Invierte el valor

# Uso tipico:
# - Validar varias condiciones antes de continuar.
# - Hacer fallback si una opcion falla.

if docker_ok and network_ok:
    print("El entorno esta listo")
else:
    print("Falta algo por preparar")

# =============================================================================
# 9. OPERADORES DE ASIGNACION
# =============================================================================

contador = 0

contador += 1 # contador = contador + 1
contador -= 1 # contador = contador - 1
contador *= 2 # contador = contador * 2
contador /= 2 # contador = contador / 2

# Uso tipico:
# - Contar intentos.
# - Acumular resultados.
# - Incrementar indices.

# =============================================================================
# 10. LISTAS
# =============================================================================

# Una lista guarda varios valores ordenados.
# Es mutable: se puede modificar.

pods = ["api-1", "api-2", "api-3"]

print(pods[0]) # primer elemento
print(pods[-1]) # ultimo elemento

pods.append("api-4") # añade elemento
pods.remove("api-2") # elimina elemento por valor

print(len(pods)) # numero de elementos

# Recorrer lista:
for pod in pods:
    print(f"Pod encontrado: {pod}")

# Uso tipico:
# - Lista de ficheros.
# - Lista de namespaces.
# - Lista de servicios.
# - Lista de comandos a ejecutar.

# =============================================================================
# 11. TUPLAS
# =============================================================================

# Una tupla es parecida a una lista, pero inmutable.
# util cuando no quieres que los datos cambien.

coordenadas = (10, 20)

# Uso tipico:
# - Devolver varios valores desde una funcion.
# - Guardar datos fijos.

# =============================================================================
# 12. DICCIONARIOS
# =============================================================================

# Un diccionario guarda pares clave/valor.
# Es uno de los tipos mas importantes para DevOps cuando trabajamos con ficheros de JSON o YAML.

deployment = {
    "name": "python-api",
    "namespace": "dev",
    "replicas": 2,
    "image": "ghcr.io/user/python-api:1.0.0",
}

print(deployment["name"])
print(deployment.get("namespace"))

# Diferencia:
# deployment["clave"] falla si la clave no existe.
# deployment.get("clave") devuelve None si no existe.

deployment["replicas"] = 3 # modificar valor
deployment["port"] = 8000 # añadir valor

for key, value in deployment.items():
    print(f"{key}: {value}")

"""
Resultado del bucle for:
name: python-api
namespace: dev
replicas: 3
image: ghcr.io/user/python-api:1.0.0
port: 8000
"""


# Uso tipico:
# - Leer JSON.
# - Leer YAML.
# - Preparar payloads de APIs.
# - Representar configuracion.

# =============================================================================
# 13. SETS
# =============================================================================

# Un set es una coleccion sin duplicados.

namespaces = {"dev", "prod", "dev", "monitoring"}
print(namespaces) # "dev" aparece una sola vez

# Uso tipico:
# - Eliminar duplicados.
# - Comprobar pertenencia rapidamente.

if "prod" in namespaces:
    print("Existe namespace prod")

# =============================================================================
# 14. CONDICIONES BASICAS
# =============================================================================

status = "Running"

if status == "Running":
    print("El pod esta corriendo")
elif status == "Pending":
    print("El pod esta pendiente")
elif status == "Failed":
    print("El pod ha fallado")
else:
    print("Estado desconocido")

# =============================================================================
# 15. CONDICIONES ALGO MAS COMPLEJAS
# =============================================================================

pod_status = "Running"
restarts = 0
ready = True

if pod_status == "Running" and ready and restarts == 0:
    print("Pod correcto")
elif pod_status == "Running" and restarts > 0:
    print("Pod correcto pero con reinicios")
elif pod_status in ["Pending", "ContainerCreating"]:
    print("Pod todavia arrancando")
else:
    print("Revisar pod")

# Uso de "in":
environment = "dev"

if environment in ["dev", "staging", "prod"]:
    print("Entorno valido")

# Uso de "is None":
config_path = None

if config_path is None:
    print("No tiene ruta de configuracion")

# =============================================================================
# 16. BUCLES FOR
# =============================================================================

# for se usa cuando quieres recorrer una coleccion.

services = ["api", "worker", "frontend"]

for service in services:
    print(f"Validando servicio: {service}")

# range(): Ejecuta un bucle un numero determinado de veces.
for i in range(5):
    print(f"Intento {i}")

# range con inicio y fin:
for i in range(1, 6):
    print(f"Intento {i}")

# enumerate: recorre una lista y da el indice de cada elemento.
for index, service in enumerate(services, start=1):
    print(f"{index}. {service}")

"""
Resultado del bucle for con enumerate:
1. api
2. worker
3. frontend
"""


# =============================================================================
# 17. BUCLES WHILE
# =============================================================================

# while se usa cuando no sabes cuantas veces vas a repetir.
# Muy comun para esperar a que algo este listo.

attempt = 0
max_attempts = 3

while attempt < max_attempts:
    print(f"Comprobacion {attempt + 1}/{max_attempts}")
    attempt += 1
    
"""
Resultado del bucle while:
Comprobacion 1/3
Comprobacion 2/3
Comprobacion 3/3
"""

# =============================================================================
# 18. BREAK Y CONTINUE
# =============================================================================

"""
Contenido para el bucle:
services = ["api", "worker", "frontend"]
"""

for service in services:
    if service == "worker":
        continue # salta esta iteracion
    if service == "frontend":
        break # termina el bucle
    print(service)
    
"""
Resultado del bucle con break y continue:
api
worker (se salta por continue), no se muestra
frontend (se encuentra, se ejecuta break, el bucle termina)

continue: Salta al siguiente elemento.
break: Corta el bucle por completo.
"""

# =============================================================================
# 19. FUNCIONES BASICAS
# =============================================================================

def saludar():
    print("Hola desde una funcion")

saludar()

# Una funcion permite:
# - Reutilizar codigo.
# - Dividir problemas grandes en pasos pequeños.
# - Dar nombres humanos a acciones tecnicas.

# =============================================================================
# 20. FUNCIONES CON ARGUMENTOS
# =============================================================================

def saludar_usuario(nombre):
    print(f"Hola {nombre}")

saludar_usuario("Sergio")

def crear_nombre_imagen(registry, image_name, tag):
    return f"{registry}/{image_name}:{tag}"

image = crear_nombre_imagen("ghcr.io/sergio", "python-api", "1.0.0")
print(image) # ghcr.io/sergio/python-api:1.0.0

# =============================================================================
# 21. ARGUMENTOS CON VALORES POR DEFECTO
# =============================================================================

def check_service(name, namespace="default"):
    print(f"Comprobando servicio {name} en namespace {namespace}")

check_service("api") # Comprueba servicio api en namespace default
check_service("api", namespace="dev") # Comprueba servicio api en namespace dev

# =============================================================================
# 22. FUNCIONES QUE DEVUELVEN VARIOS VALORES
# =============================================================================

def get_runner_info():
    name = "local-runner"
    labels = ["self-hosted", "linux", "podman"]
    return name, labels

runner_name, runner_labels = get_runner_info()
print(runner_name) # local-runner
print(runner_labels) # ['self-hosted', 'linux', 'podman']

# =============================================================================
# 23. SCOPE / ALCANCE DE VARIABLES
# =============================================================================

global_var = "Soy global"

def ejemplo_scope():
    local_var = "Soy local"
    print(global_var) # Las funciones pueden acceder a variables globales.
    print(local_var) # local_var solo existe dentro de esta funcion.

ejemplo_scope()

# print(local_var) fallaria porque local_var solo existe dentro de la funcion.

# =============================================================================
# 24. IMPORTS
# =============================================================================

# Python trae modulos estandar muy utiles para scripting.

import os # manejo de sistema operativo, variables de entorno, rutas, etc.
import sys # manejo de argumentos, salida del programa, etc.
import subprocess # ejecutar comandos del sistema
import json # leer y escribir JSON
import time # funciones relacionadas con el tiempo, como sleep() o time()
from pathlib import Path # manejo moderno de rutas de ficheros


# =============================================================================
# 25. VARIABLES DE ENTORNO
# =============================================================================

# Leer variable de entorno.
github_token = os.environ.get("GITHUB_TOKEN") # devuelve None si no existe

if github_token is None:
    print("GITHUB_TOKEN no esta definido")
else:
    print("GITHUB_TOKEN existe")

# Tambien puedes poner valor por defecto:
environment = os.environ.get("ENVIRONMENT", "dev")

# Uso tipico:
# - Tokens
# - URLs
# - Nombres de entorno
# - Configuracion en GitHub Actions

# =============================================================================
# 26. ARGUMENTOS DE LINEA DE COMANDOS CON SYS
# =============================================================================

# sys.argv contiene los argumentos con los que se llama el script.
# Ejemplo:
#   python script.py dev
#
# sys.argv[0] -> script.py
# sys.argv[1] -> dev

print(sys.argv)

# Para scripts reales, normalmente es mejor argparse.

# =============================================================================
# 27. ARGPARSE
# =============================================================================

# argparse permite crear scripts con argumentos profesionales.
# Ejemplo de uso real:
#
#   python check_env.py --env dev --verbose

import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="Ejemplo de script Python con argumentos"
    )

    parser.add_argument(
        "--env",
        default="dev",
        choices=["dev", "staging", "prod"],
        help="Entorno a validar"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Muestra mas informacion"
    )

    return parser.parse_args()

# =============================================================================
# 28. PATHLIB / MANEJO DE RUTAS
# =============================================================================

# pathlib es la forma moderna de trabajar con rutas.

current_file = Path(__file__)
current_dir = current_file.parent
project_root = current_dir

print(current_file) # ruta completa del script
print(current_dir) # ruta del directorio donde esta el script

logs_dir = project_root / "logs" # Crea una ruta combinando project_root y "logs"
log_file = logs_dir / "app.log" # Crea una ruta para el fichero de log dentro del directorio logs

# Crear directorio si no existe:
logs_dir.mkdir(parents=True, exist_ok=True) # crea logs/ si no existe, no da error si ya existe

# Comprobar si existe:
if log_file.exists():
    print("El fichero de log existe")
else:
    print("El fichero de log no existe")

# Uso tipico:
# - Crear rutas portables.
# - Evitar concatenar strings manualmente.

# =============================================================================
# 29. LEER FICHEROS
# =============================================================================

example_file = project_root / "example.txt"

# Crear un fichero de ejemplo:
example_file.write_text("linea1\nlinea2\nlinea3\n", encoding="utf-8") # escribe texto en el fichero, creando el fichero si no existe

# Leer todo el fichero:
contenido = example_file.read_text(encoding="utf-8")
print(contenido)

"""
Resultado de leer el fichero:
linea1
linea2
linea3
"""


# Leer linea a linea:
with example_file.open("r", encoding="utf-8") as file: # abre el fichero en modo lectura, "r" es opcional porque es el modo por defecto y hace que el fichero se cierre automaticamente al terminar el bloque
    for line in file:
        print(line.strip())

"""
Resultado de leer el fichero linea a linea:
linea1
linea2
linea3
"""

# with:
# - Abre el fichero.
# - Lo cierra automaticamente.
# - Evita fugas de recursos.

# =============================================================================
# 30. ESCRIBIR FICHEROS
# =============================================================================

output_file = project_root / "output.txt"

# Sobrescribe el fichero completo.
output_file.write_text("Nuevo contenido\n", encoding="utf-8")

# Añadir contenido sin borrar lo anterior:
with output_file.open("a", encoding="utf-8") as file:
    file.write("Linea añadida\n")

# Modos comunes:
# "r"  leer
# "w"  escribir sobrescribiendo
# "a"  añadir al final
# "rb" leer binario
# "wb" escribir binario

# =============================================================================
# 31. LIMPIAR / VACIAR FICHEROS
# =============================================================================

# Opcion 1: sobrescribir con texto vacio.
output_file.write_text("", encoding="utf-8")

# Opcion 2: abrir en modo write y no escribir nada.
with output_file.open("w", encoding="utf-8"):
    pass

# Uso tipico:
# - Limpiar logs temporales.
# - Vaciar ficheros generados.
# - Preparar salida limpia para un script.

# =============================================================================
# 32. BORRAR FICHEROS Y DIRECTORIOS
# =============================================================================

temp_file = project_root / "temp.txt"
temp_file.write_text("temporal", encoding="utf-8")

if temp_file.exists():
    temp_file.unlink()  # borra fichero

# Para borrar directorios con contenido se usa shutil.rmtree.
import shutil

temp_dir = project_root / "temp_dir"
temp_dir.mkdir(exist_ok=True)
(temp_dir / "file.txt").write_text("hola", encoding="utf-8")

if temp_dir.exists():
    shutil.rmtree(temp_dir)

# =============================================================================
# 33. JSON
# =============================================================================

# JSON es clave en DevOps:
# - APIs
# - GitHub
# - Kubernetes
# - Docker
# - Terraform output
# - Configuracion

data = {
    "name": "python-api",
    "version": "1.0.0",
    "replicas": 2,
}

json_file = project_root / "app.json"

# Escribir JSON:
json_file.write_text(
    json.dumps(data, indent=2),
    encoding="utf-8"
)

# Leer JSON:
loaded_data = json.loads(json_file.read_text(encoding="utf-8"))
print(loaded_data["name"])

# =============================================================================
# 34. YAML
# =============================================================================

# YAML se usa muchisimo en Kubernetes, GitHub Actions, FluxCD, Helm, etc.
# Python no trae YAML en la libreria estandar.
# Normalmente se instala PyYAML:
#
#   pip install pyyaml

try:
    import yaml

    yaml_data = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": "python-api"
        }
    }

    yaml_file = project_root / "deployment-example.yaml"

    yaml_file.write_text(
        yaml.safe_dump(yaml_data, sort_keys=False),
        encoding="utf-8"
    )

    loaded_yaml = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
    print(loaded_yaml["kind"])

except ImportError:
    print("PyYAML no esta instalado. Instala con: pip install pyyaml")

# =============================================================================
# 35. EJECUTAR COMANDOS DEL SISTEMA
# =============================================================================

# subprocess permite ejecutar comandos externos.
# Es una de las herramientas mas importantes para scripting DevOps.

result = subprocess.run(
    ["echo", "Hola desde subprocess"],
    capture_output=True,
    text=True
)

print(result.stdout)
print(result.returncode)

# Importante:
# - capture_output=True captura stdout/stderr.
# - text=True devuelve texto en vez de bytes.
# - returncode indica si el comando fue bien.
#
# returncode 0     -> OK
# returncode != 0  -> error

# =============================================================================
# 36. COMPROBAR ERRORES EN COMANDOS
# =============================================================================

result = subprocess.run(
    ["python", "--version"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print(f"Python encontrado: {result.stdout.strip()}")
else:
    print(f"Error: {result.stderr.strip()}")

# check=True lanza una excepcion si el comando falla.

try:
    subprocess.run(
        ["python", "--version"],
        capture_output=True,
        text=True,
        check=True
    )
except subprocess.CalledProcessError as error:
    print("El comando fallo")
    print(error.stderr)

# =============================================================================
# 37. EJECUTAR COMANDOS CON SHELL
# =============================================================================

# Evita shell=True salvo que sea necesario.
# shell=True puede ser peligroso si mezclas input de usuario.

# Mejor:
subprocess.run(["ls", "-la"], capture_output=True, text=True)

# Menos seguro:
# subprocess.run("ls -la", shell=True)

# Regla practica:
# - Usa listas: ["kubectl", "get", "pods"]
# - Evita strings con shell=True

# =============================================================================
# 38. MANEJO DE ERRORES / EXCEPCIONES
# =============================================================================

try:
    number = int("123")
    print(number)
except ValueError:
    print("No se pudo convertir a numero")

# Estructura completa:

try:
    number = int("abc")
except ValueError as error:
    print(f"Error de conversion: {error}")
else:
    print("Esto se ejecuta si no hubo error")
finally:
    print("Esto se ejecuta siempre")

# Uso tipico:
# - Capturar errores controlados.
# - Mostrar mensajes claros.
# - Evitar que un script muera sin explicacion.
# - Hacer cleanup.

# =============================================================================
# 39. LANZAR TUS PROPIOS ERRORES
# =============================================================================

def validate_environment(env):
    valid_envs = ["dev", "staging", "prod"]

    if env not in valid_envs:
        raise ValueError(f"Entorno invalido: {env}")

    return True


try:
    validate_environment("dev")
except ValueError as error:
    print(error)

# =============================================================================
# 40. LOGGING
# =============================================================================

# logging es mejor que print para scripts reales.

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logging.info("Mensaje informativo")
logging.warning("Aviso")
logging.error("Error")

# Niveles comunes:
# DEBUG   -> detalle tecnico
# INFO    -> informacion normal
# WARNING -> algo raro pero no fatal
# ERROR   -> error
# CRITICAL -> error grave

# =============================================================================
# 41. CODIGOS DE SALIDA
# =============================================================================

# En scripting es importante devolver codigos de salida.
#
# 0 -> exito
# distinto de 0 -> error

def exit_success():
    sys.exit(0)


def exit_error():
    sys.exit(1)


# No llamamos estas funciones en la chuleta para no terminar el script.

# =============================================================================
# 42. MAIN
# =============================================================================

# Patron recomendado para scripts Python.

def main():
    print("Ejecutando main()")
    print("Aqui empezaria la logica principal del script")


if __name__ == "__main__":
    main()

# ¿Por que existe esto?
#
# Si ejecutas:
#   python chuleta_comandos.py
#
# entonces __name__ == "__main__" y se ejecuta main().
#
# Si importas este archivo desde otro:
#   import chuleta_comandos
#
# entonces main() no se ejecuta automaticamente.
#
# Esto permite reutilizar funciones sin ejecutar todo el script.

# =============================================================================
# 43. REQUESTS / PETICIONES HTTP
# =============================================================================

# requests no viene instalado por defecto.
# Se instala con:
#
#   pip install requests
#
# Uso tipico:
# - Llamar APIs.
# - GitHub API.
# - Comprobar endpoints.
# - Obtener tokens.

try:
    import requests

    # Ejemplo comentado para evitar depender de internet:
    #
    # response = requests.get("https://api.github.com", timeout=10)
    #
    # if response.status_code == 200:
    #     print(response.json())
    # else:
    #     print(f"Error HTTP: {response.status_code}")

except ImportError:
    print("requests no esta instalado. Instala con: pip install requests")

# =============================================================================
# 44. FUNCIONES DEVOPS UTILES
# =============================================================================

def run_command(command, check=False):
    """
    Ejecuta un comando del sistema.

    command:
        Lista con el comando.
        Ejemplo: ["kubectl", "get", "pods"]

    check:
        Si True, lanza excepcion cuando el comando falla.

    return:
        Objeto CompletedProcess con stdout, stderr y returncode.
    """

    logging.info("Ejecutando comando: %s", " ".join(command))

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if check and result.returncode != 0:
        raise RuntimeError(
            f"Comando fallido: {' '.join(command)}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )

    return result


def command_exists(command):
    """
    Comprueba si un comando existe en el PATH.
    Similar a usar 'which' en Linux.
    """

    return shutil.which(command) is not None


def require_env_var(name):
    """
    Lee una variable de entorno obligatoria.
    Si no existe, lanza error claro.
    """

    value = os.environ.get(name)

    if not value:
        raise EnvironmentError(f"Variable de entorno obligatoria no definida: {name}")

    return value


def ensure_directory(path):
    """
    Crea un directorio si no existe.
    """

    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


# =============================================================================
# 45. EJEMPLO REAL: CHECK BASICO DE ENTORNO
# =============================================================================

def check_basic_environment():
    """
    Ejemplo de script DevOps:
    Comprueba si existen comandos basicos.
    """

    required_commands = ["python", "git"]

    missing = []

    for command in required_commands:
        if command_exists(command):
            logging.info("OK: comando encontrado: %s", command)
        else:
            logging.error("ERROR: comando no encontrado: %s", command)
            missing.append(command)

    if missing:
        logging.error("Faltan comandos: %s", ", ".join(missing))
        return False

    return True


# =============================================================================
# 46. EJEMPLO REAL: LEER Y MODIFICAR UN MANIFEST YAML
# =============================================================================

def update_image_in_kubernetes_manifest(manifest_path, new_image):
    """
    Ejemplo orientado a GitOps:
    Lee un deployment.yaml y modifica la imagen del primer container.

    Requiere:
        pip install pyyaml
    """

    try:
        import yaml
    except ImportError:
        raise RuntimeError("PyYAML no esta instalado. Ejecuta: pip install pyyaml")

    manifest_path = Path(manifest_path)

    if not manifest_path.exists():
        raise FileNotFoundError(f"No existe el fichero: {manifest_path}")

    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

    manifest["spec"]["template"]["spec"]["containers"][0]["image"] = new_image

    manifest_path.write_text(
        yaml.safe_dump(manifest, sort_keys=False),
        encoding="utf-8"
    )

    logging.info("Imagen actualizada a: %s", new_image)


# =============================================================================
# 47. PYTEST / TESTS BASICOS
# =============================================================================

# pytest permite probar funciones.
#
# Instalacion:
#   pip install pytest
#
# Ejemplo de fichero:
#
# tests/test_utils.py
#
# def test_crear_nombre_imagen():
#     result = crear_nombre_imagen("ghcr.io/user", "api", "1.0.0")
#     assert result == "ghcr.io/user/api:1.0.0"
#
# Ejecutar:
#   python -m pytest -v

# =============================================================================
# 48. REGLAS MENTALES PARA SCRIPTING DEVOPS CON PYTHON
# =============================================================================

"""
1. Divide el problema en pasos pequeños.
   Ejemplo:
   - leer argumentos
   - validar entorno
   - leer fichero
   - modificar dato
   - guardar fichero
   - mostrar resultado

2. Evita hardcodear secretos.
   Mal:
       token = "ghp_xxxxx"
   Bien:
       token = os.environ.get("GITHUB_TOKEN")

3. Los errores deben ser claros.
   Mal:
       Error
   Bien:
       No se encontro deployment.yaml en ruta X

4. Usa logging en scripts reales.

5. Usa pathlib para rutas.

6. Usa subprocess con listas, no shell=True.

7. Usa argparse para scripts que se ejecutan desde terminal.
"""
