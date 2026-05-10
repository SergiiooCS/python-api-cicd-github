#!/usr/bin/env python3

#SCRIPT DE PYTHON ENCARGADO DE COMPROBAR QUE LAS HERRAMIENTAS REQUERIDAS PARA CONSTRUIR LA APLICACION ESTEN INSTALADAS EN EL SISTEMA.
import shutil

REQUIRED_TOOLS = ["bash", "curl", "git", "jq", "yq", "tar", "gzip", "unzip", "docker", "python3", "pip"]

#FUNCION QUE COMPRUEBA SI UNA HERRAMIENTA EXISTE EN EL PATH DEL SISTEMA.
def tool_exists(tool_name):
    tool_path = shutil.which(tool_name)
    
    if tool_path is None:
        return False, None

    return True, tool_path

"""
LE PASO EL NOMBRE DE LA HERRAMIENTA A COMPROBAR.
CREO 'tool_path' PARA ALMACENAR LA RUTA DE LA HERRAMIENTA EN EL SISTEMA.
SI 'tool_path' ES NULO, SIGNIFICA QUE LA HERRAMIENTA NO SE ENCUENTRA EN EL PATH, POR LO QUE DEVUELVO FALSO Y NULO.
SI 'tool_path' NO ES NULO, SIGNIFICA QUE LA HERRAMIENTA SE ENCUENTRA EN EL PATH, POR LO QUE DEVUELVO VERDADERO Y LA RUTA DE LA HERRAMIENTA.
"""

#FUNCION QUE COMPRUEBA SI LAS HERRAMIENTAS REQUERIDAS ESTAN INSTALADAS EN EL SISTEMA.
def check_required_tools():
    missing_tools = []
    print(f"=== COMPROBANDO HERRAMIENTAS REQUERIDAS ===")
    
    for tool in REQUIRED_TOOLS:
        exists, tool_path = tool_exists(tool)
        
        if exists:
            print(f"OK: {tool} encontrado en: {tool_path}")
        else:
            print(f"ERROR: {tool} NO encontrado en el sistema.")
            missing_tools.append(tool)
    return missing_tools
"""
CREO UNA LISTA VACIA PARA ALMACENAR AQUELLAS HERRAMIENTAS QUE NO SE ENCUENTREN EN EL SISTEMA.
RECORRO LA LISTA DE LAS HERRAMIENTAS REQUERIDAS.
LLAMO A LA FUNCION 'tool_exists' PASANDOLE EL NOMBRE DE LA HERRAMIENTA. ESTA FUNCION DEVUELVE DOS VALORES DEPENDENDIENDO DEL RESULTADO. EL PRIMER VALOR QUE DEVUELVE ES 'True' o 'False' Y ESTE VALOR SE ALMACENA EN 'exists'. EL SEGUNDO VALOR QUE DEVUELVE ES LA RUTA DE LA HERRAMIENTA EN EL SISTEMA O 'None' Y SE ALMACENA EN LA VARIABLE 'tool_path'.
SI 'exists' ES VERDADERO, SIGNIFICA QUE LA HERRAMIENTA SE ENCUENTRA EN EL PATH. DEVOLVERIA LA LISTA DE 'missing_tools' VACIA.
SI 'exists' ES FALSO, SIGNIFICA QUE LA HERRAMIENTA NO SE ENCUENTRA EN EL PATH. ESTA HERRAMIENTA SE AÑADE A LA LISTA DE 'missing_tools'.
"""

def main():
    missing_tools = check_required_tools()
    
    print("=== FINALIZA LA COMPROBACION DE HERRAMIENTAS REQUERIDAS ===")
    
    if missing_tools:
        print(f"ERROR: El runner NO tiene todas las herramientas que necesita")
        print(f"Herramientas faltantes:")
        
        for tool in missing_tools:
            print(f"- {tool}")
        return 1
    
    print(f"OK: El runner tiene todas las herramientas requeridas y esta listo")
    return 0

"""
LA RESPUESTA DE LA FUNCION 'check_required_tools' SE ALMACENA EN LA VARIABLE 'missing_tools'.
SI 'missing_tools' NO ESTA VACIA, RECORREMOS LA LISTA DE LAS HERRAMIENTAS QUE FALTAN Y MOSTRAMOS POR CONSOLA EL NOMBRE DE LAS HERRAMIENTAS NO ENCONTRADAS.
SI 'missing_tools' ESTA VACIA, MOSTRAMOS POR CONSOLA UN MENSAJE INDICANDO QUE EL RUNNER TIENE TODAS LAS HERRAMIENTAS REQUERIDAS Y ESTA LISTO.
"""
   
if __name__ == "__main__":
    exit(main())
