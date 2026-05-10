#!/usr/bin/env python3

#SCRIPT DE PYTHON QUE COMPRUEBA LOS MANIFIESTOS DE KUBERNETES ANTES DE HACER EL MERGE DE LA PULL REQUEST.

import argparse
import sys
from pathlib import Path
import yaml

#FUNCION QUE PARSEA ARGUMENTOS RECIBIDOS POR LA LINEA DE COMANDOS CUANDO SE EJECUTA EL SCRIPT. EN ESTE CASO, SE ESPERA RECIBIR UN ARGUMENTO LLAMADO '--file' QUE ES LA RUTA AL MANIFIESTO DE KUBERNETES QUE QUEREMOS VALIDAR.
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Valida los manifiestos de Kubernetes en la carpeta 'k8s' antes de hacer el merge de la pull request."
    )
    
    parser.add_argument(
        "--file",
        required="True",
        help="PATH to Kubernetes YAML manifest"
    )
    
    return parser.parse_args()

"""
CREAMOS 'parser' PARA PARSEAR LOS ARGUMENTOS DE LA LINEA DE COMANDOS. ESTE OBEJTO ES DE LA CLASE 'ArgumentParser' DE LA LIBRERIA 'argparse'. LE PASAMOS UNA DESCRIPCION DEL SCRIPT.
AÑADIMOS UN ARGUMENTO REQUERIDO LLAMADO '--file' QUE ES LA RUTA AL MANIFIESTO DE KUBERNETES QUE QUEREMOS VALIDAR. ESTE ARGUMENTO SE ALMACENA EN 'args.file'.
DEVUELVE LOS ARGUMENTOS PARSEADOS EN UN OBJETO 'args'.
"""

#FUNCION QUE CARGA UN ARCHIVO YAML.
def load_yaml_file(file_path):
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")
    
    if not path.is_file():
        raise ValueError(f"La ruta no es un archivo: {path}")

    with path.open("r", endcoding="utf-8") as file: #"r" - read
        return yaml.safe_load(file)

"""
CREO UN OBJETO 'path' DE LA CLASE 'Path' DE LA LIBRERIA 'pathlib' PASANDOLE LA RUTA DEL ARCHIVO QUE QUEREMOS CARGAR.
COMPRUEBO SI EL ARCHIVO EXISTE. SI NO EXISTE, LANZO UNA EXCEPCION 'FileNotFoundError' CON UN MENSAJE DE ERROR.
COMPRUEBO SI LA RUTA ES UN ARCHIVO. SI NO ES UN ARCHIVO, LANZO UNA EXCEPCION 'ValueError' CON UN MENSAJE DE ERROR.
ABRO EL ARCHIVO EN MODO LECTURA Y CON CODIFICACION UTF-8. UTILIZO 'yaml.safe_load' PARA CARGAR EL CONTENIDO DEL ARCHIVO YAML Y DEVUELVO EL RESULTADO.
"""

#FUNCION QUE VALIDA LOS CAMPOS MINIMOS REQUERIDOS EN UN MANIFIESTO DE KUBERNETES.
def validate_common_fields(manifest):
    errors = []

    if not isinstance(manifest, dict):
        errors.append("Manifest must be a YAML object")
        return errors

    if not manifest.get("apiVersion"):
        errors.append("Missing required field: apiVersion")

    if not manifest.get("kind"):
        errors.append("Missing required field: kind")

    metadata = manifest.get("metadata")

    if not isinstance(metadata, dict):
        errors.append("Missing or invalid required field: metadata")
    elif not metadata.get("name"):
        errors.append("Missing required field: metadata.name")

    return errors

"""
CREO UNA LISTA VACIA PARA ALMACENAR LOS ERRORES DE VALIDACION.
COMPRUEBO SI EL MANIFIESTO ES UN DICCIONARIO. SI NO ES UN DICCIONARIO, SIGNIFICA QUE EL MANIFIESTO NO ES UN OBJETO YAML VALIDO, POR LO QUE AÑADO UN MENSAJE DE ERROR A LA LISTA DE ERRORES.
COMPRUEBO SI EL MANIFIESTO TIENE EL CAMPO 'apiVersion'. SI NO LO TIENE, AÑADO UN MENSAJE DE ERROR A LA LISTA DE ERRORES.
COMPRUEBO SI EL MANIFIESTO TIENE EL CAMPO 'kind'. SI NO LO TIENE, AÑADO UN MENSAJE DE ERROR A LA LISTA DE ERRORES.
COMPRUEBO SI EL MANIFIESTO TIENE EL CAMPO 'metadata' Y SI ES UN DICCIONARIO. SI NO LO TIENE O NO ES UN DICCIONARIO, AÑADO UN MENSAJE DE ERROR A LA LISTA DE ERRORES.
SI EL CAMPO 'metadata' ES UN DICCIONARIO, COMPRUEBO SI TIENE EL CAMPO 'name'. SI NO LO TIENE, AÑADO UN MENSAJE DE ERROR A LA LISTA DE ERRORES.
DEVUELVO LA LISTA DE ERRORES.
"""

#FUNCION QUE VALIDA LOS CAMPOS ESPECIFICOS DE UN MANIFIESTO DE KUBERNETES DE TIPO 'Deployment'.
def validate_deployment(manifest):
    errors = []

    spec = manifest.get("spec")
    if not isinstance(spec, dict):
        errors.append("Deployment missing or invalid field: spec")
        return errors

    template = spec.get("template")
    if not isinstance(template, dict):
        errors.append("Deployment missing or invalid field: spec.template")
        return errors

    template_spec = template.get("spec")
    if not isinstance(template_spec, dict):
        errors.append("Deployment missing or invalid field: spec.template.spec")
        return errors

    containers = template_spec.get("containers")
    if not isinstance(containers, list) or len(containers) == 0:
        errors.append("Deployment must define at least one container")
        return errors

    for index, container in enumerate(containers):
        if not isinstance(container, dict):
            errors.append(f"Container at index {index} must be an object")
            continue

        if not container.get("name"):
            errors.append(f"Container at index {index} missing field: name")

        if not container.get("image"):
            errors.append(f"Container at index {index} missing field: image")

        image = container.get("image")
        if image == "latest" or str(image).endswith(":latest"):
            errors.append(
                f"Container {container.get('name', index)} uses forbidden image tag: latest"
            )

    return errors

"""
CREO UNA LISTA VACIA PARA ALMACENAR LOS ERRORES DE VALIDACION.
COMPRUEBO SI EL MANIFIESTO TIENE EL CAMPO 'spec' Y SI ES UN DICCIONARIO. SI NO LO TIENE O NO ES UN DICCIONARIO, AÑADO UN MENSAJE DE ERROR A LA LISTA DE ERRORES.
COMPRUEBO SI EL CAMPO 'spec' TIENE EL CAMPO 'template' Y SI ES UN DICCIONARIO. SI NO LO TIENE O NO ES UN DICCIONARIO, AÑADO UN MENSAJE DE ERROR A LA LISTA DE ERRORES.
COMPRUEBO SI EL CAMPO 'template' TIENE EL CAMPO 'spec' Y SI ES UN DICCIONARIO. SI NO LO TIENE O NO ES UN DICCIONARIO, AÑADO UN MENSAJE DE ERROR A LA LISTA DE ERRORES.
COMPRUEBO SI EL CAMPO 'template.spec' TIENE EL CAMPO 'containers' Y SI ES UNA LISTA NO VACIA. SI NO LO TIENE O NO ES UNA LISTA O ES UNA LISTA VACIA, AÑADO UN MENSAJE DE ERROR A LA LISTA DE ERRORES.
RECORRO LA LISTA DE CONTENEDORES Y COMPRUEBO SI CADA CONTENEDOR ES UN DICCIONARIO. SI NO ES UN DICCIONARIO, AÑADO UN MENSAJE DE ERROR A LA LISTA DE ERRORES.
COMPRUEBO SI CADA CONTENEDOR TIENE EL CAMPO 'name'. SI NO LO TIENE, AÑADO UN MENSAJE DE ERROR A LA LISTA DE ERRORES.
COMPRUEBO SI CADA CONTENEDOR TIENE EL CAMPO 'image'. SI NO LO TIENE, AÑADO UN MENSAJE DE ERROR A LA LISTA DE ERRORES.
COMPRUEBO SI EL CAMPO 'image' DE CADA CONTENEDOR ES 'latest' O TERMINA CON ':latest'. SI ES ASI, AÑADO UN MENSAJE DE ERROR A LA LISTA DE ERRORES INDICANDO QUE EL USO DE LA ETIQUETA 'latest' ESTA PROHIBIDO.
DEVUELVO LA LISTA DE ERRORES.
"""

#FUNCION PRINCIPAL QUE EJECUTA LA VALIDACION DEL MANIFIESTO DE KUBERNETES.
def validate_manifest(manifest):
    errors = []

    errors.extend(validate_common_fields(manifest))

    if errors:
        return errors

    kind = manifest.get("kind")

    if kind == "Deployment":
        errors.extend(validate_deployment(manifest))

    return errors

"""
CREO UNA LISTA VACIA PARA ALMACENAR LOS ERRORES DE VALIDACION.
LLAMO A LA FUNCION 'validate_common_fields' PASANDOLE EL MANIFIESTO Y AÑADO LOS ERRORES DEVUELTOS A LA LISTA DE ERRORES.
SI HAY ERRORES DE VALIDACION COMUNES, DEVUELVO LA LISTA DE ERRORES SIN CONTINUAR CON LAS VALIDACIONES ESPECIFICAS.
OBTENGO EL VALOR DEL CAMPO 'kind' DEL MANIFIESTO PARA DETERMINAR EL TIPO DE RECURSO DE KUBERNETES QUE ESTAMOS VALIDANDO.
SI EL CAMPO 'kind' ES 'Deployment', LLAMO A LA FUNCION 'validate_deployment' PASANDOLE EL MANIFIESTO Y AÑADO LOS ERRORES DEVUELTOS A LA LISTA DE ERRORES.
DEVUELVO LA LISTA DE ERRORES DE VALIDACION. SI LA LISTA ESTA VACIA, SIGNIFICA QUE EL MANIFIESTO ES VALIDO. SI LA LISTA NO ESTA VACIA, SIGNIFICA QUE HAY ERRORES DE VALIDACION EN EL MANIFIESTO.
"""

#FUNCION PRINCIPAL QUE EJECUTA EL SCRIPT.
def main():
    args = parse_arguments()

    try:
        manifest = load_yaml_file(args.file)
        errors = validate_manifest(manifest)

        if errors:
            print("Kubernetes manifest validation failed:")
            for error in errors:
                print(f"- {error}")
            return 1

        print(f"Kubernetes manifest is valid: {args.file}")
        return 0

    except yaml.YAMLError as error:
        print(f"Invalid YAML syntax: {error}")
        return 1

    except Exception as error:
        print(f"Validation error: {error}")
        return 1

"""
CREO 'args' PARA ALMACENAR LOS ARGUMENTOS PARSEADOS POR LA FUNCION 'parse_args'.
INTENTO CARGAR EL MANIFIESTO DE KUBERNETES UTILIZANDO LA FUNCION 'load_yaml_file' PASANDOLE LA RUTA DEL ARCHIVO QUE OBTENGO DE 'args.file'. SI HAY UN ERROR DE SINTAXIS EN EL ARCHIVO YAML, SE LANZARA UNA EXCEPCION 'yaml.YAMLError' QUE SERÁ CAPTURADA EN EL BLOQUE 'except' CORRESPONDIENTE, MOSTRANDO UN MENSAJE DE ERROR Y DEVOLVIENDO '1'.
SI EL MANIFIESTO SE CARGA CORRECTAMENTE, LLAMO A LA FUNCION 'validate_manifest' PASANDOLE EL MANIFIESTO CARGADO Y ALMACENO LOS ERRORES DE VALIDACION EN LA VARIABLE 'errors'.
SI HAY ERRORES DE VALIDACION, MOSTRAMOS POR CONSOLA UN MENSAJE INDICANDO QUE LA VALIDACION DEL MANIFIESTO DE KUBERNETES HA FALLADO Y RECORREMOS LA LISTA DE ERRORES MOSTRANDO CADA ERROR POR CONSOLA. DEVOLVEMOS '1' PARA INDICAR QUE EL SCRIPT HA FALLADO.
SI NO HAY ERRORES DE VALIDACION, MOSTRAMOS POR CONSOLA UN MENSAJE INDICANDO QUE EL MANIFIESTO DE KUBERNETES ES VALIDO Y DEVOLVEMOS '0' PARA INDICAR QUE EL SCRIPT HA SIDO EXITOSO.
SI HAY CUALQUIER OTRA EXCEPCION DURANTE EL PROCESO DE VALIDACION, SE CAPTURA EN EL BLOQUE 'except' CORRESPONDIENTE, MOSTRANDO UN MENSAJE DE ERROR Y DEVOLVIENDO '1' PARA INDICAR QUE EL SCRIPT HA FALLADO.
"""



if __name__ == "__main__":
    sys.exit(main())
    
"""
EN PYTHON CUALQUIER ARCHIVO SE LE DENOMINA 'MODULO'.
CUANDO SE INTERPRETA ESTE 'MODULO' AUTOMATICAMENTE SE CREA LA VARIABLE '__name__' QUE CONTIENE EL NOMBRE DEL MODULO.
LA CONDICION ES: SI EL NOMBRE DEL MODULO ES IGUAL A '__main__', SIGNIFICA QUE ESTE MODULO SE ESTA EJECUTANDO DIRECTAMENTE.
'__main__' ES EL NOMBRE QUE PYTHON ASIGNA AL MODULO PRINCIPAL QUE SE EJECUTA.
"""
