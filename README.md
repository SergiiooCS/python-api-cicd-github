# python-api-cicd-github

Repositorio de laboratorio para construir un entorno local de CI/CD y GitOps utilizando GitHub Actions, un runner self-hosted en Podman, GHCR, Minikube y FluxCD.

## Objetivo del proyecto

El objetivo es simular un flujo DevOps similar al de una empresa:

1. Desarrollar una aplicación Python.
2. Ejecutar CI con lint, tests y build del paquete `.whl`.
3. Construir una imagen de contenedor.
4. Publicar la imagen en GHCR.
5. Crear una PR automática actualizando el tag de imagen en `deployment.yaml`.
6. Revisar y aceptar manualmente la PR.
7. Dejar que FluxCD reconcilie el cambio en Minikube.

## Arquitectura general

```text
Push / Pull Request
        │
        ▼
GitHub Actions CI
        │
        ├── Lint
        ├── Tests
        ├── Build Python package
        └── Upload artifact .whl
        │
        ▼
Publish workflow
        │
        ├── Download artifact
        ├── Build Docker image
        ├── Push image to GHCR
        └── Create PR updating deployment.yaml
        │
        ▼
Manual PR review
        │
        ▼
Merge to main
        │
        ▼
FluxCD reconcile
        │
        ▼
Minikube deployment
```

---

## Workflow: Build, Test and Prepare Python App

Este workflow se encarga de validar, comprobar y preparar la aplicacion Python antes de continuar con el proceso de publicacion de imagen.

El objetivo principal es aplicar varios checks previos dentro del proceso de CI para detectar errores antes de construir el paquete Python o generar una nueva imagen de contenedor.

### Pasos principales

1. Checkout del codigo.
2. Configuracion de Python `3.12`.
3. Instalacion de dependencias desde `requirements.txt`.
4. Ejecucion del script `check_env.py`.
5. Ejecucion del script `check_required_tools.py`.
6. Ejecucion del script `validate_k8s_manifest.py`.
7. Instalacion de `flake8` para linting.
8. Ejecucion de lint sobre el codigo Python.
9. Ejecucion de tests unitarios con `pytest`.
10. Instalacion de la herramienta `build`.
11. Construccion del paquete Python `.whl`.
12. Publicacion del `.whl` como artifact de GitHub Actions.

### Scripts Python utilizados en CI

Dentro del workflow de Build se ejecutan varios scripts Python personalizados para validar el entorno y aplicar checks previos antes del build.

#### `check_env.py`

Este script comprueba variables de entorno disponibles dentro del runner self-hosted.

Su objetivo es entender y validar el contexto de ejecucion del pipeline, incluyendo variables propias de GitHub Actions, del sistema y del runner.

Ejemplos de validaciones:

- Variables de entorno existentes.
- Variables vacias o no definidas.
- Variables sensibles enmascaradas en la salida.
- Informacion general del entorno de ejecucion.

#### `check_required_tools.py`

Este script valida que el runner self-hosted tenga disponibles las herramientas necesarias para ejecutar correctamente el CI.

Comprueba comandos instalados en el sistema mediante el `PATH`.

Herramientas comprobadas:

- `bash`
- `curl`
- `git`
- `jq`
- `yq`
- `tar`
- `gzip`
- `unzip`
- `docker`
- `python3`
- `pip`

Si alguna herramienta obligatoria no existe, el script devuelve un codigo de salida distinto de `0` y el job de GitHub Actions falla.

#### `validate_k8s_manifest.py`

Este script valida la estructura minima del manifiesto Kubernetes antes de permitir que los cambios avancen en el flujo CI/CD.

Actualmente se utiliza para validar el archivo:

```text
apps/myapp/base/deployment.yaml
```

---

## Workflow: Publish image to GHCR

Este workflow se ejecuta cuando el workflow de Build finaliza correctamente sobre la rama `main`.

### Pasos principales

1. Checkout del código.
2. Descarga del artifact `.whl` generado por el workflow de Build.
3. Configuración de Docker Buildx.
4. Login en GHCR usando `GITHUB_TOKEN`.
5. Generación de un tag único para la imagen.
6. Construcción de la imagen Docker.
7. Publicación de la imagen en GHCR.
8. Actualización del campo `image` en `apps/myapp/base/deployment.yaml`.
9. Creación de una PR automática con el nuevo tag de imagen.

### Objetivo

Separar la validación del código de la publicación de imagen y mantener un flujo GitOps basado en Pull Requests.

---

## GitHub Runner Self-hosted

Para ejecutar los workflows se utiliza un runner self-hosted en local, ejecutado como contenedor Podman.

### Motivo

El runner self-hosted permite:

- Ejecutar builds en local.
- Usar Docker-in-Docker dentro del contenedor del runner.
- Integrarse con el entorno Minikube local.
- Simular un entorno CI/CD más cercano a uno empresarial.

---

## Imagen del runner

La imagen del runner se construye a partir de un `Containerfile`.

Contenido:

    FROM ubuntu:24.04
    # evita prompts interactivos en apt (importante en builds automaticos)
    ENV DEBIAN_FRONTEND=noninteractive

    # define donde se instalara el runner de github actions
    ENV RUNNER_HOME=/actions-runner

    # define la version del runner (se puede cambiar en build)
    ARG RUNNER_VERSION=2.334.0

    # actualiza repositorios e instala dependencias necesarias
    RUN apt-get update && apt-get install -y \
        ca-certificates \   # certificados ssl
        curl \              # para hacer peticiones http
        gnupg \             # manejo de claves gpg
        lsb-release \       # info de la distro
        jq \                # procesar json
        git \               # control de versiones
        unzip \             # descomprimir zip
        sudo \              # ejecutar comandos como root
        bash \              # shell bash
        tar \               # manejar archivos tar
        gzip \              # compresion gzip
        libc6 \             # libreria base de c
        libgcc-s1 \         # soporte gcc
        libicu74 \          # unicode
        libkrb5-3 \         # kerberos
        liblttng-ust1 \     # tracing
        libssl3 \           # ssl
        libstdc++6 \        # libreria c++
        zlib1g \            # compresion
        && rm -rf /var/lib/apt/lists/*   # limpia cache para liberar espacio

    # Descarga el binario de yq, lo instala en el sistema y verifica que funciona.
    RUN curl -fsSL https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 \
        -o /usr/local/bin/yq && \
        chmod +x /usr/local/bin/yq && \
        yq --version

    # crea directorio para claves de apt y añade repo oficial de docker
    RUN install -m 0755 -d /etc/apt/keyrings && \   # crea carpeta con permisos correctos
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc && \  # descarga clave gpg
        chmod a+r /etc/apt/keyrings/docker.asc && \   # da permisos de lectura
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo ${UBUNTU_CODENAME:-$VERSION_CODENAME}) stable" \
        | tee /etc/apt/sources.list.d/docker.list > /dev/null   # añade repo de docker

    # instala docker dentro del contenedor (docker in docker / docker client)
    RUN apt-get update && apt-get install -y \
        docker-ce \                # docker engine
        docker-ce-cli \            # cli de docker
        containerd.io \            # runtime
        docker-buildx-plugin \     # buildx para builds avanzados
        docker-compose-plugin \    # docker compose v2
        && rm -rf /var/lib/apt/lists/*   # limpia cache para liberar espacio

    # crea usuario runner y le da permisos para usar docker
    RUN useradd -m -d /home/runner -s /bin/bash runner && \   # crea usuario runner con home
        usermod -aG docker runner && \                        # lo añade al grupo docker. Este paso es importante para que dentro del workflow pueda acceder a la ruta '/var/run/docker.sock' y asi poder comunicarse con el Daemon de Docker
        mkdir -p ${RUNNER_HOME} /home/runner/.docker && \     # crea carpetas necesarias
        chown -R runner:runner ${RUNNER_HOME} /home/runner    # asigna permisos al usuario

    # define el directorio de trabajo
    WORKDIR ${RUNNER_HOME}

    # descarga e instala el runner de github actions
    RUN curl -fsSL -o actions-runner.tar.gz \
        https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz && \  # descarga runner
        tar xzf actions-runner.tar.gz && \   # descomprime
        rm actions-runner.tar.gz && \        # borra el tar para ahorrar espacio
        chown -R runner:runner ${RUNNER_HOME}   # asigna permisos

    # copia el script de entrada al contenedor
    COPY entrypoint.sh /entrypoint.sh

    # da permisos de ejecucion al script
    RUN chmod +x /entrypoint.sh

    # define el entrypoint del contenedor
    ENTRYPOINT ["/entrypoint.sh"]

Contenido del archivo `Entrypoint.sh`:

    #!/usr/bin/env bash
    #INDICAMOS QUE UTILICE EL PATH DE LA DISTRIBUCION UNIX PARA UBICAR LA RUTA DEL INTERPRETE 'BASH0'

    #'set' ACTIVA OPCIONES DE SHELL, -e -> SI UN COMANDO FALLA LA EJECUCION DEL SCRIPT TERMINA, -u -> SI SE INTENTA USAR UNA VARIABLE QUE NO EXISTE EL SCRIPT DA ERROR Y TERMINA, -o pipefail -> CUALQUIER COMANDO EN PIPES QUE SE EJECUTE Y FALLE TERMINA EL SCRIPT, NO ES IGNORADO COMO PASARIA EN BASH NORMAL.
    set -euo pipefail

    #CREACION VARIABLES DE ENTORNO
    #$EPHEMERAL:-false -> LA VARIABLE UTILIZA EL VALOR DE '$EPHEMERAL' SI EXISTE, SI ESTA NO TIENE VALOR, POR DEFECTO SE LE ASIGNA 'false'
    API_VERSION="2022-11-28"
    RUNNER_HOME="${RUNNER_HOME:-/actions-runner}"
    RUNNER_NAME="${RUNNER_NAME:-podman-runner}"
    RUNNER_LABELS="${RUNNER_LABELS:-self-hosted,linux,x64,podman,local}"
    RUNNER_WORKDIR="${RUNNER_WORKDIR:-_work}"
    EPHEMERAL="${EPHEMERAL:-false}"
    DOCKER_LOG="/tmp/dockerd.log"

    #CREAR FUNCION PARA VALIDACION PREVIA QUE COMPRUEBE SI LAS VARIABLES EXISTEN.
    #1. PASAR LAS PALABRAS QUE QUERAMOS COMO VARIABLES DE ENTORNO A COMPROBAR.
    #2. COMPROBAR QUE EL NOMBRE DE LA VARIABLE QUE QUEREMOS PASAR NO ESTE VACIO, QUE LA VARIABLE EXISTA Y SI NO EXISTE SE LE ESTABLECE UN VALOR VACIO. SI ESTA CONDICION NO SE CUMPLE SE DEVUEVLE UN ERROR POR TEMINAL Y DEVUELVO UN ERROR 'EXIT 1' PARA TERMINAR LA EJECUCION DEL SCRIPT.
    #-n -> QUE EL TEXTO A COMPROBAR NO TENGA UN VALOR VACIO.
    #!var -> LE PASAMOS EL VALOR DESEADO (!var = REPO_URL -> $REPO_URL).
    #:- -> SE ESTABLECE EL VALOR VACIO PARA EVITAR ERRORES AL USAR 'set -e' AL INICIO DEL SCRIPT.
    required_env() {
    for var in REPO_URL GITHUB_PAT GITHUB_OWNER GITHUB_REPO; do
        [[ -n "${!var:-}" ]] || { echo "ERROR: falta $var"; exit 1; }
    done
    }

    #CREAR FUNCION PARA VALIDACION PREVIA QUE COMPRUEBA LOS PROCESOS DE DOCKER EN EJECUCION.
    #1. LISTAR TODOS LOS PROCESOS EN EJECUCION.
    #2. USANDO UNA PIPE (|) LE PASAMOS EL RESULTADO DEL COMANDO 1 A LA EJECUCION DEL COMANDO 2. EL COMANDO 2 USA GREP PARA FILTRAR EL RESULTADO Y BUSCAR LOS PATRONES '[d]ockerd|[c]ontainerd|[d]ocker', SI ENCUENTRA PROCESOS CON ESE PATRON DEVUELVE '0', SI NO ENCUENTRA PROCESOS CON ESE PATRON DEVUELVE '1' PERO QUE NO EXISTAN PROCESOS ACTIVOS NO DEBE SER UN ERROR POR LO QUE ESTABLEZCO '|| true' PARA EVITAR TERMINAL EL SCRIPT POR UTILZIAR 'set -e'.
    #-E: ME PERMITE UTILIZAR EXPRESIONES REGULARES, EN MI CASO PARA UTILIZAR '|' COMO 'OR - O' A LA HORA DE COMPROBAR LOS PATRONES QUE QUIERO EN EL FILTRO GREP.
    #[d]ockerd: UTILIZO '[d]' PARA PASARLE COMO CARACTER 'd' Y ASI PODER EVITAR QUE ME DEVUELVA LA PROPIA EJECUCION DEL COMANDO GREP COMO COINCIDENCIA ENCONTRADA.
    docker_processes() {
    ps aux | grep -E '[d]ockerd|[c]ontainerd|[d]ocker' || true
    }

    #CREAR FUNCION QUE LIMPIE/ELIMINE LOS PROCESOS DOCKER Y RUTAS TEMPORALES/CACHE QUE PUEDAN BLOQUEAR LOS PROCESOS Y DAR ERRORES A LA HORA DE ARRANCAR DOCKER EN UN FUTURO.
    #1. MUESTRO LOS PROCESOS ACTUALES DE DOCKER LLAMANDO A LA FUNCION 'docker_proccesses'.
    #2. PARO DE FORMA CONTROLADA Y CORRECTA LOS PROCESOS DE DOCKER QUE ESTEN EJECUTANDOSE. PARA ELLO MATAMOS EL PROCESO 'pkill' DE FORMA CORRECTA '-TERM' (SIGTERM) LLAMADOS 'dockerd' Y 'containerd'. EL STDERR (2) LO ENVIAMOS A '/dev/null' PARA OCULTAR LOS MENSAJES DE ERRORES POR DEFECTO Y SI NO EXISTEN LOS PROCESOS EN LUGAR DE QUE DEVUELVA UN CODIGO 1 'error' LE DECIMOS QUE CONTINUE IGUALMENTE (|| true) CON LA EJECUCION DEL SCRIPT Y ASI EVITAR ERRORES POR UTILIZAR 'set -e'.
    #3. ESPERO 5 SEGUNDOS A QUE EL PROCESO MUERA CORRECTAMENTE. SI EN ESE TIEMPO NO SE HA ELIMINADO CORRECTAMENTE PASAMOS A ELIMINARLO DE FORMA DIRECTA.
    #4. ELIMINO EL PROCESO DE FORMA DIRECTA Y BRUTA COMO RESULTADO FALLIDO DE MATAR EL PROCESO CONTROLADO Y CORRECTAMENTE. LA SALIDA NORMAL DE ERRORES (STDERR - 2) LA OCULTAMOS UTILIZANDO '/dev/null' . SI NO EXISTE EL PROCESO LE INDICAMOS QUE CONITNUE IGUALMENTE (|| true) Y NO SE PARE EL SCRIPT POR UTILIZAR 'set -e'.
    #5. ELIMINAMOS LOS ARCHIVOS '.pid' Y '.sock' QUE UTILIZA DOCKER.
    #6. ELIMINO LAS CARPETAS DE 'docker' Y 'containerd'.
    #7. CREO LA RUTA DE 'docker', 'containerd' Y LA RUTA DE SUS LIBRERIAS POR DEFECTO.
    #docker.pid -> LOS ARCHIVOS '.pid' SON LOS ARCHIVOS QUE ALMACENAN LA INFORMACION DEL 'Proccess ID' DE LINUX. SE UTILIZA PARA SABER QUE PROCESO ESTA UTILIZANDO DOCKER, PARA INDICARLE A OTROS PROGRAMAS QUE DOCKER ESTA SIENDO UTILIZADO POR UN PROCESO YA ACTIVO.
    #docker.sock -> LOS ARCHIVOS '.sock' SON ARCHIVOS QUE ESTABLECEN UN CANAL DE COMUNICACION DIRECTA CON DOCKER ENGINE PARA QUE OTROS PROCESOS PUEDAN COMUNICARSE CON EL SERVICIO/PROCESO ACTIVO DE DOCKER. 
    clean_docker() {
    echo "Procesos Docker actuales:"
    docker_processes

    echo "Parando Docker/containerd..."
    pkill -TERM dockerd containerd 2>/dev/null || true
    sleep 5
    pkill -KILL dockerd containerd 2>/dev/null || true

    echo "Limpiando estado temporal Docker/containerd..."
    rm -f /var/run/docker.pid /run/docker.pid /var/run/docker.sock
    rm -f /run/containerd/containerd.pid /run/containerd/containerd.sock
    rm -rf /var/run/docker /run/containerd

    mkdir -p /var/run/docker /run/containerd /var/lib/docker /var/lib/containerd
    }

    #CREAR FUNCION PARA SOLICITAR UN TOKEN TEMPORAL PARA EL RUNNER SELF-HOSTED EN GITHUB.
    #CUANDO CREO EL CONTENEDOR DE MI RUNNER SELF-HOSTED CON EL COMANDO DE PODMAN YA LE PASO EL '$GITHUB_PAT' GARANTIZANDO ASI QUE TIENE PERMISOS SUFICIENTES PARA AUTENTICARSE Y OPERAR SOBRE MI REPOSITORIO DE CODIGO (Y MUCHOS PERMISOS MAS).
    #CON 'local' INDICO QUE EL AMBITO DE LA VARIABLE SOLO SE MODIFICA DENTRO DE LA FUNCION, 'type="$1"' INDICA QUE LA VARIABLE LLAMADA 'type' TENDRA COMO VALOR EL PARAMETRO PASADO A LA FUNCION. ESTO SE UTILIZA PARA PODER DIFERENCIA ENTRE REGISTRAR O ELIMINAR EL RUNNER DESDE LA API DE GITHUB UTILIZANDO LA MISMA FUNCION PARA ELLO.
    #UTILIZO CURL PARA COMUNICARME CON LA API DE GITHUB PARA SOLICITAR EL TOKEN TEMPORAL Y LE PASO EN EL HEADER MI '$GITHUB_PAT' PARA AUTENTICARME. SI EL OBJETIVO ES REGISTRAR UN NUEVO RUNNER ME DARA UN TOKEN TEMPORAL DE TIPO 'registration-token' PERO SI EL OBJETIVO ES ELIMINAR EL RUNNER QUE YA EXISTE EL TOKEN TEMPORAL QUE ME DE SERIA DE TIPO 'remove-token'.
    #EL RESULTADO DE LA EJECUCION DE LA PETICION CURL SE PASA (|) A LA EJECUCION DEL SEGUNDO COMANDO 'JQ' PARA PROCESAR JSON DESDE LA PROPIA TERMINAL DEL CONTENEDOR Y OBTENER UNICAMENTE EL CAMPO '.token'.
    #-r -> 'raw output' ES SALIDA EN TEXTO PLANO.
    github_token() {
    local type="$1"

    curl -fsSL -X POST \
        -H "Accept: application/vnd.github+json" \
        -H "Authorization: Bearer ${GITHUB_PAT}" \
        -H "X-GitHub-Api-Version: ${API_VERSION}" \
        "https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/runners/${type}-token" \
        | jq -r '.token'
    }

    #CREAR FUNCION QUE ARRANQUE EL DAEMON DE DOCKER (dockerd) DENTRO DEL CONTENEDOR Y COMPROBAR QUE DOCKER FUNCIONA CORRECTAMENTE.
    #1. ARRANCAMOS EL DAEMON DE DOCKER. EL RESULTADO DEL ARRANQUE SE ALMACENA EN '${DOCKER_LOG}' (/tmp/dockerd.log), SE MANDAN LOS ERRORES (STDERR - 2) AL MISMO FICHERO Y POR ULTIMO LA EJECUCION DEL ARRANQUE SE HACE EN SEUGNDO PLANO (&).
    #2. GUARDAMOS COMO VARIABLE LOCAL DENTRO DE LA FUNCION EL PID DEL PROCESO DE ARRANQUE DE DOCKER DAEMON. SE LO PASO UTILIZANDO ($!) PORQUE SE HA ARRANCADO DAEMON DOCKER COMO UN PROCESO BACKGROUND.
    #--host=unix:///var/run/docker.sock -> LE INDICA A DAEMON DOCKER EL SOCKET UNIX DE DONDE DEBE DE ESCUCHAR PETICIONES.
    #--exec-root=/var/run/docker -> RUTA DONDE DOCKER ALMACENA ESTADOS TEMPORALES DE EJECUCIONES.
    #--data-root=/var/lib/docker -> RUTA DONDE DOCKER ALMACENA DATOS PERSISTENTES.
    #--pidfile=/var/run/docker.pid -> ARCHIVO QUE INDICA EL PID DEL PROCESO QUE ESTA EJECUTANDO EL DAMEON DE DOCKER.
    #--userland-proxy=false -> SE DESACTIVA PARA SIMPLIFICAR, EVITAR PROCESOS ADICIONALES INNECESARIOS Y EVITAR CONFLICTOS.
    #--storage-driver=vfs -> AL UTILIZAR WSL2 (WINDOWS) ES MAS COMPATIBLE 'VFS' QUE OTROS DRIVERS DE ALMACENAMIENTO.
    #3. CREO UN BUCLE DONDE SE COMPROBARA EL ESTADO DE DOCKER DURANTE 120 SEGUNDOS (60 INTENTOS Y SE ESPERA 2 SEGUNDOS POR CADA INTENTO) Y QUE EL PROCESO DE DAEMON DOCKER ESTE VIVO. 
    #3.1 SI 'docker info' RESPONDE SALTA AL SIGUIENTE BLOQUE DE CODIGO (&&) O DEVUELVE 0 'exit 0 - correcto' A LA EJECUCION DEL BUCLE, LOS ERRORES (STDERR - 2) SE ENVIAN AL MISMO DESTINO QUE (STDOUT - 1) QUE SERIA "/dev/null". 
    #3.2 SE COMPRUEBA SI EL PROCESO DEL DAEMON DOCKER SIGUE VIVO, SI MUERE POR X MOTIVO SE NOTIFICA COMO ERROR Y SE SALE DEL BUCLE. 
    #4. SI EL BUCLE FOR TERMINA CORRECTAMENTE 'return 0', SE SALE DE LA FUNCION. SI EL BUCLE FOR HA FALLADO SE MUESTRA POR LA TERMINAL UN MENSAJE DE ERROR, SE MUESTRA EL CONTENIDO DEL FICHERO '.log' Y SE SALE DEL SCRIPT.
    start_docker() {
    echo "Arrancando dockerd..."

    dockerd \
        --host=unix:///var/run/docker.sock \
        --exec-root=/var/run/docker \
        --data-root=/var/lib/docker \
        --pidfile=/var/run/docker.pid \
        --userland-proxy=false \
        --storage-driver=vfs \
        > "${DOCKER_LOG}" 2>&1 &

    local dockerd_pid=$!

    for _ in $(seq 1 60); do
        docker info >/dev/null 2>&1 && {
        echo "Docker listo"
        return 0
        }

        kill -0 "${dockerd_pid}" 2>/dev/null || {
        echo "ERROR: dockerd murio"
        cat "${DOCKER_LOG}"
        exit 1
        }

        sleep 2
    done

    echo "ERROR: Docker no arranco"
    cat "${DOCKER_LOG}"
    exit 1
    }

    #CREAR FUNCION QUE ELIMINE REGISTROS ANTIGUOS DE OTROS RUNNERS Y PREPARE EL USUARIO/DIRECTORIOS DESDE CERO.
    #1. CREAMOS EL DIRECTORIO DEL RUNNER.
    #2. SE MODIFICA EL PROPIETARIO/GRUPO DEL DIRECTORIO DEL RUNNER.
    #3. SE SOLICITA A LA API DE GITHUB UN TOKEN DE TIPO REMOVE PARA DESPUES ELIMINAR CUALQUIER REGISTRO DEL RUNNER PREVIO, SI ESTA PETICION DE ELIMINACION FALLA SE CONTINUA LA EJECUCION NORMAL (|| true - PUEDE FALLAR SI NO EXISTE NINGUN REGISTRO PREVIO, ESO ESTA BIEN).
    #4. EN LA CONDICION SE COMPRUEBAN 3 COSAS. SI LA CONDICION SE CUMPLE SE MUESTRA UN MENSAJE POR LA TERMINAL Y EJECUTA COMANDOS COMO EL USUARIO 'runner' PARA ENTRAR EN EL DIRECTORIO DEL RUNNER Y EJECUTAR UN SCRIPT (config.sh) CON EL PARAMETRO 'remove' PARA ELIMINAR EL RUNNER PASANDOLE EL TOKEN SOLICITADO A GITHUB DE TIPO 'remove'. SI FALLA LA ELIMINACION CONTINUA EL REGISTRO YA QUE PUEDE FALLAR PORQUE NO EXISTA, ESO ESTA BIEN (|| true).
    #4.1. SE COMPRUBA SI EL FICHERO '.runner' YA EXISTE (ES UN FICHERO DONDE GITHUB ACTIONS RUNNER ALMACENA LA CONFIGURACIO DE RUNNERS).
    #4.2. SE COMPRUEBA QUE '$REMOVE_TOKEN' NO ESTE VACIO.
    #4.3. SE COMPRUEBA QUE LA API DE GITHUB NO HAYA DEVUELVO UN VALOR VACIO/NULL A LA VARIABLE '$REMOVE_TOKEN'.
    #5. SE ELIMINAN FICHEROS DEL GITHUB RUNNER QUE PUEDEN CONTENER CREDENCIALES, CONFIGURACIONES, ENTRE OTRAS COSAS, PARA DEJAR EL RUNNER VACIO PARA REGISTRAR UNO NUEVO.
    prepare_runner() {
    mkdir -p "${RUNNER_HOME}/${RUNNER_WORKDIR}"
    chown -R runner:runner "${RUNNER_HOME}"

    REMOVE_TOKEN="$(github_token remove || true)"

    if [[ -f "${RUNNER_HOME}/.runner" && -n "${REMOVE_TOKEN:-}" && "${REMOVE_TOKEN}" != "null" ]]; then
        echo "Desregistrando runner previo..."
        su -s /bin/bash runner -c "cd '${RUNNER_HOME}' && ./config.sh remove --token '${REMOVE_TOKEN}'" || true
    fi

    rm -f "${RUNNER_HOME}/.runner" \
            "${RUNNER_HOME}/.credentials" \
            "${RUNNER_HOME}/.credentials_rsaparams" \
            "${RUNNER_HOME}/.path" \
            "${RUNNER_HOME}/.env"

    rm -rf "${RUNNER_HOME}/_diag" "${RUNNER_HOME}"/.credentials_*
    }


    #CREAR FUNCION PARA REGISTRAR EL RUNNER NUEVO EN GITHUB UTILIZANDO LA API.
    #1. SOLICITAS UN TOKEN DE TIPO 'registration' A LA API DE GITHUB Y LO GUARDAS EN LA VARIABLE.
    #2. SE CREA UNA CONDICION Y SE COMPRUEBA QUE NO TENGA UN VALOR VACIO LA VARIABLE '$REG_TOKEN' Y QUE SU VALOR NO SE 'NULL'. SI LA CONDICION FALLA MUESTRA UN MENSAJE POR CONSOLA Y DEVUEVLVE UN 'exit 1' FORZANDO A FALLAR EL SCRIPT.
    #3. SE CREA UNA VARIABLE DE AMBITO LOCAL (DENTRO DE LA FUNCION) LLAMADA 'extra_args' CON UN VALOR VACIO.
    #4. SE COMPRUEBA SI LA VARIABLE '$EPHEMERAL' TIENE VALOR 'true', SI LA CONDICION SE CUMPLE SE LE ASIGNA EL VALOR '--ephemeral' A LA VARIABLE '$extra_args'.
    #5. MUESTRO UN MENSAJE POR TERMINAL INDICANDO QUE SE CONFIGURA EL RUNNER.
    #6. SE EJECUTA UN COMANDO COMO USUARIO 'runner' EN LA TERMINAL BASH. ENTRA EN EL DIRECTORIO DEL RUNNER Y EJECUTA EL SCRIPT 'config.sh' CON PARAMETROS COMO: REPO_ULR, REG_TOKEN, RUNNER_NAME, RUNNER_LABELS, RUNNER_WORKDIR Y LA VARIABLE 'extra_args'.
    configure_runner() {
    REG_TOKEN="$(github_token registration)"

    [[ -n "${REG_TOKEN}" && "${REG_TOKEN}" != "null" ]] || {
        echo "ERROR: no se pudo obtener registration token"
        exit 1
    }

    local extra_args=""
    [[ "${EPHEMERAL}" == "true" ]] && extra_args="--ephemeral"

    echo "Configurando runner..."

    su -s /bin/bash runner -c "
        cd '${RUNNER_HOME}' &&
        ./config.sh \
        --url '${REPO_URL}' \
        --token '${REG_TOKEN}' \
        --name '${RUNNER_NAME}' \
        --labels '${RUNNER_LABELS}' \
        --work '${RUNNER_WORKDIR}' \
        --replace \
        ${extra_args}
    "
    }

    #CREAR FUNCION DE LIMPIEZA QUE SOLICITE A GITHUB ELIMINAR EL RUNNER ANTES DE APAGAR LA MAQUINA.
    #1. MUESTRA UN MENSAJE POR TERMINAL DE APAGADO DE MAQUINA.
    #2. CREO UNA CONDICION QUE VALIDA QUE '$REMOVE_TOKEN' EXISTA Y SI NO TIENE VALOR SE LE ASIGNA UNO VACIO, SE VALIDA QUE EL ARCHIVO '.runner' EXISTA EN EL DIRECTORIO DEL RUNNER.
    #3. SI SE CUMPLE LA CONDICION, DESDE LA TERMINAL BASH DEL USUSARIO 'runner' ENTRA EN EL DIRECTORIO DEL RUNNER Y EJECUTA EL SCRIPT 'config.sh' PARA ELIMINAR EL REGISTRO DEL RUNNER EN GITHUB.
    #4. EJECUTA LA FUNCION 'clean_docker' QUE MOSTRABA PROCESOS ACTIVOS Y ELIMINABA TODOS LOS PROCEOS (PRIMERO DE FORMA CONTROLADA Y LUEGO FORZANDO SU PARADA) DE DOCKER DAEMON Y CONTAINER DAEMON JUNTO A LA ELIMINACION DE ARCHIVOS QUE PUDIERAN BLOQUEAR PROCESOS (.pid & .sock).
    cleanup() {
    echo "Apagando runner..."

    if [[ -n "${REMOVE_TOKEN:-}" && -f "${RUNNER_HOME}/.runner" ]]; then
        su -s /bin/bash runner -c "cd '${RUNNER_HOME}' && ./config.sh remove --token '${REMOVE_TOKEN}'" || true
    fi

    clean_docker
    }

    #TERM -> SE USA PARA RECIBIR SEÑALES/EVENTOS (CTRL + C -> exit).
    #INT -> SE USA PARA RECIBIR SEÑALES/EVENTOS DE INTERRUPCION (SIGINT - Interruption signal) QUE SE GENERA CON CTRL + C EN LA TERMINAL.
    #TERM -> SE USA PARA RECIBIR SEÑALES/EVENTOS DE TERMINACION (SIGTERM - Termination signal) QUE SE GENERA CUANDO SE SOLICITA LA TERMINACION DE UN PROCESO DE FORMA CONTROLADA.
    #TRAP -> ES UN COMANDO DE BASH QUE PERMITE ESPECIFICAR COMANDOS O FUNCIONES A EJECUTAR CUANDO EL PROCESO RECIBE SEÑALES O EVENTOS ESPECIFICOS.
    #1. CUANDO EL PROCESO RECIBA LA SEÑAL DE INTERRUPCION (SIGINT) SE EJECUTARA LA FUNCION 'cleanup' Y LUEGO SE SALDRA DEL PROCESO CON UN CODIGO DE SALIDA '130' QUE ES EL CODIGO ESTANDAR PARA INDICAR QUE UN PROCESO FUE TERMINADO POR UNA SEÑAL DE INTERRUPCION.
    #2. CUANDO EL PROCESO RECIBA LA SEÑAL DE TERMINACION (SIGTERM) SE EJECUTARA LA FUNCION 'cleanup' Y LUEGO SE SALDRA DEL PROCESO CON UN CODIGO DE SALIDA '143' QUE ES EL CODIGO ESTANDAR PARA INDICAR QUE UN PROCESO FUE TERMINADO POR UNA SEÑAL DE TERMINACION.
    trap 'cleanup; exit 130' INT
    trap 'cleanup; exit 143' TERM

    #SE EJECUTAN LAS FUNCIONES CREADAS ANTERIORMENTE.
    required_env
    clean_docker
    start_docker

    #COMPRUEBO SI EXISTE LA RED 'bridge' EN DOCKER, SI NO EXISTE LA CREO. ESTO ES NECESARIO PARA QUE LOS CONTENEDORES DE LOS JOBS DE GITHUB ACTIONS PUEDAN UTILIZAR ESTA RED PARA COMUNICARSE ENTRE ELLOS Y CON EL RUNNER.
    docker network inspect bridge >/dev/null 2>&1 || docker network create bridge

    #SE EJECUTAN LAS FUNCIONES CREADAS ANTERIORMENTE.
    prepare_runner
    configure_runner

    #MUESTRO UN MENSAJE POR TERMINAL DE QUE EL RUNNER SE ESTA INICIANDO.
    #EJECUTO DESDE LA TERMINAL BASH DEL USUARIO 'runner' EL SCRIPT 'run.sh' PARA INICIAR EL RUNNER UBICADO EN EL DIRECTORIO DEL RUNNER. 
    echo "Iniciando runner..."
    exec su -s /bin/bash runner -c "cd '${RUNNER_HOME}' && ./run.sh"

### Construir imagen

```powershell
podman build -t local/github-runner:latest .
```

---

## Ejecutar el runner

Antes de crear el contenedor es necesario disponer de un PAT Fine-Grained con permisos suficientes para registrar y eliminar runners en el repositorio.

### Crear contenedor

```powershell
podman run -d `
  --name github-runner `
  --privileged `
  -e REPO_URL="https://github.com/SergiiooCS/python-api-cicd-testing" `
  -e GITHUB_OWNER="SergiiooCS" `
  -e GITHUB_REPO="python-api-cicd-testing" `
  -e GITHUB_PAT=$env:GITHUB_TOKEN `
  -e RUNNER_NAME="runner-podman-win11-$(Get-Random)" `
  -e RUNNER_LABELS="self-hosted,linux,x64,podman,local" `
  -v github_runner_work:/actions-runner/_work `
  local/github-runner:latest
```

### Ver logs

```powershell
podman logs -f github-runner
```

---

## GitOps con FluxCD y Minikube

El entorno GitOps se ejecuta sobre Minikube local utilizando FluxCD.

### Componentes principales

1. `GitRepository` para enlazar FluxCD con este repositorio.
2. `Kustomization` para gestionar recursos del cluster.
3. Namespace `dev`.
4. Secrets gestionados con SOPS.
5. Manifests Kubernetes:
   - `deployment.yaml`
   - `service.yaml`
   - `ingress.yaml`

### Flujo GitOps

1. El workflow Publish genera una nueva imagen en GHCR.
2. El workflow modifica el tag de imagen en `deployment.yaml`.
3. Se crea una PR automática.
4. La PR se revisa manualmente.
5. Al hacer merge, FluxCD detecta el cambio.
6. FluxCD aplica el estado deseado en Minikube.

---

## Monitorización local

Para visualizar el cluster se utiliza OpenLens.

Repositorio:

```text
https://github.com/MuhammedKalkan/OpenLens
```

---

## Seguridad del repositorio

Una vez completado el flujo CI/CD y GitOps, el siguiente objetivo es aplicar buenas prácticas de seguridad sobre el repositorio.

### Branch Protection Rules

Los rulesets en cuentas personales privadas de GitHub Free no pueden aplicarse realmente sobre las ramas protegidas.

En este laboratorio no puedo forzar su aplicación, pero los configuro igualmente para aprender el flujo y las buenas prácticas utilizadas en entornos reales.

#### Ruleset para proteger la rama `main`

- **Nombre:** `Protect main branch`
- **Enforcement status:** `Active`
- **Target branches:** `main`

#### Reglas configuradas

- Restrict deletions
- Require a pull request before merging
  - Required approvals: `1`
- Dismiss stale pull request approvals when new commits are pushed
- Require status checks to pass
- Require branches to be up to date before merging
- Required status checks:
  - `ci-python-app`
- Block force pushes

---

### Secret Management

Pendiente de aplicar/mejorar:

- Rotación de tokens
- Principio de mínimos privilegios
- Gestión de secretos en GitHub Actions
- Secretos para Kubernetes
- Buenas prácticas de almacenamiento de credenciales

---

### `GITHUB_TOKEN` Scopes

Revisión y hardening de permisos:

- Permisos mínimos necesarios en workflows CI/CD.
- Revisión de permisos del `GITHUB_TOKEN`.
- Revisión de permisos del `GITHUB_PAT`.
- Eliminación de permisos innecesarios.
- Separación entre permisos de CI y CD.

---

## Estado actual

- Runner self-hosted funcionando en Podman.
- Docker-in-Docker funcionando dentro del runner.
- Workflow Build funcionando.
- Workflow Publish funcionando.
- Imagen publicada en GHCR.
- PR automática para actualizar `deployment.yaml`.
- FluxCD reconciliando cambios en Minikube.
- Primeras reglas de seguridad documentadas.
