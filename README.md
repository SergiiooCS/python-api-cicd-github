# python-api-cicd-testing

Repositorio creado para realizar pruebas de CI / CD con Github Actions.

Pasos del Workflow Build, Test and Prepare Python App:

1. Checkout del codigo.
2. Setup del entorno (python 3.12, dependencias, librerias, etc).
3. Instalacion de dependencias utilizando el archivo 'requirements.txt'.
4. Crear un Fail Fast para ahorrar tiempo y recursos de ejecucion (Lint + calidad de codigo).
5. Test unitarios (Pytest).
6. Construir el proyecto para obtener el archivo '.whl'.
7. Almacenar el archivo '.whl' en el artifact de Github para poder utilizarlo en el Workflow de creacion de Imagen docker (GH packeage) para futuros despliegues (CD).

Pasos del Workflow Publish image to GHCR:

1. Solo se ejecuta cuando el Workflow 'Build, Test and Prepare Python App' ha terminado como 'completed' y se hace un push a la rama 'main'.
2. Establecemos los permisos necesarios al runner para que acceda a la ejecucion del workflow 'Build, Test and Prepare Python App', pueda leer el contenido y pueda escribir en Packages del repositorio.
3. Establecemos como variables de entorno globales del workflow el nombre del Registry  y el nombre del repositorio que utilizamos.
4. Establecemos una condicion de que solo puede ejecutarse siempre y cuando haya terminado como 'success' la ejecucion del workflow anterior (Build, Test and Prepare Python App).
5. Hacemos checkout del codigo (para obtener el contexto, buenas practicas e importante el Dockerfile).
6. Descargamos el artifact creado anteriormente por el Workflow 'Build, Test and Prepare Python App'.
7. Listamos los archivos para comprobar que se ha descargado correctamente.
8. Preparamos el Builder que utilizaremos para construir la imagen de Docker.
9. Hacemos login en el registry de Github con las credenciales correspondientes.
10. Creamos los metadatos necesarios para crear una imagen de Docker.
11. Construimos la imagen de la aplicacion y la subimos como 'Package' al repositorio de Github.

Github Runner Self-hosted:
El paso de crear un runner de forma self-hosted en local es necesario debido a que nos simplifica la configuracion para poder desplegar (CD) en el entorno de Minikube local para realizar pruebas.

El primer paso fue entender todo lo que es y necesita un runner self-hosted de Github. Disponia de diferentes formas de hacerlo, pero escogi crear una imagen y un contenedor para el runner en Podman (es la opcion mas simple de primeras).

Para crear la imagen utilice un Containerfile:
    # imagen base de ubuntu version 24.04
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

Tambien se utilizo el archivo 'entrypoint.sh' para automatizar procesos en el arranque del contenedor.
    #!/usr/bin/env bash
    # usa bash para ejecutar este script

    # hace que el script falle si hay errores, variables no definidas o pipes fallan
    set -euo pipefail

    # version de la API de GitHub
    API_VERSION="2022-11-28"

    # variable para guardar el PID de dockerd
    DOCKERD_PID=""

    # =========================
    # FUNCION DE LIMPIEZA
    # =========================
    cleanup() {
    echo "Apagando runner..."

    # si existe token y el runner está configurado, intenta eliminarlo de GitHub
    if [[ -n "${REMOVE_TOKEN:-}" && -f "${RUNNER_HOME}/.runner" ]]; then
        echo "Intentando desregistrar runner..."
        su -s /bin/bash runner -c "cd ${RUNNER_HOME} && ./config.sh remove --unattended --token '${REMOVE_TOKEN}'" || true
    fi

    # para los procesos de docker y containerd
    echo "Parando dockerd/containerd..."
    pkill -TERM dockerd || true
    pkill -TERM containerd || true
    sleep 3
    pkill -KILL dockerd || true
    pkill -KILL containerd || true

    # elimina sockets y estado temporal
    rm -rf /var/run/docker /run/containerd
    }

    # ejecuta cleanup cuando el contenedor se para o recibe señales
    trap 'cleanup; exit 130' INT
    trap 'cleanup; exit 143' TERM

    # define la ruta del runner si no existe
    : "${RUNNER_HOME:=/actions-runner}"

    # =========================
    # VALIDACIONES
    # =========================

    # comprueba que las variables necesarias están definidas
    [[ -z "${REPO_URL:-}" ]] && echo "ERROR: falta REPO_URL" && exit 1
    [[ -z "${GITHUB_PAT:-}" ]] && echo "ERROR: falta GITHUB_PAT" && exit 1
    [[ -z "${GITHUB_OWNER:-}" ]] && echo "ERROR: falta GITHUB_OWNER" && exit 1
    [[ -z "${GITHUB_REPO:-}" ]] && echo "ERROR: falta GITHUB_REPO" && exit 1

    # valores por defecto del runner
    RUNNER_NAME="${RUNNER_NAME:-podman-runner}"
    RUNNER_LABELS="${RUNNER_LABELS:-self-hosted,linux,x64,podman,local}"
    RUNNER_WORKDIR="${RUNNER_WORKDIR:-_work}"
    EPHEMERAL="${EPHEMERAL:-false}"

    # =========================
    # LIMPIEZA DOCKER
    # =========================

    echo "Limpiando estado previo de Docker/containerd..."

    # mata procesos antiguos de docker
    pkill -TERM dockerd || true
    pkill -TERM containerd || true
    sleep 3
    pkill -KILL dockerd || true
    pkill -KILL containerd || true

    # elimina directorios temporales
    rm -rf /var/run/docker /run/containerd

    # recrea directorios necesarios
    mkdir -p /var/run/docker /run/containerd /var/lib/docker /var/lib/containerd "${RUNNER_HOME}/${RUNNER_WORKDIR}"

    # asigna permisos al usuario runner
    chown -R runner:runner "${RUNNER_HOME}"

    # =========================
    # ARRANQUE DOCKER
    # =========================

    echo "Arrancando dockerd..."

    # arranca docker daemon en background
    dockerd \
    --host=unix:///var/run/docker.sock \
    --exec-root=/var/run/docker \
    --data-root=/var/lib/docker \
    --pidfile=/var/run/docker.pid \
    --userland-proxy=false \
    --storage-driver=vfs \
    > /tmp/dockerd.log 2>&1 &

    # guarda el PID de dockerd
    DOCKERD_PID=$!

    echo "Esperando a que Docker responda..."

    # espera hasta que docker esté listo
    for i in $(seq 1 60); do
    if docker info > /dev/null 2>&1; then
        echo "Docker listo"
        break
    fi

    # si dockerd muere, muestra logs y sale
    if ! kill -0 "${DOCKERD_PID}" 2>/dev/null; then
        echo "ERROR: dockerd murió"
        cat /tmp/dockerd.log
        exit 1
    fi

    sleep 2
    done

    # validación final de docker
    if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker no arrancó"
    cat /tmp/dockerd.log
    exit 1
    fi

    # =========================
    # RED DOCKER (FIX NETWORK)
    # =========================

    # comprueba si existe la red bridge, si no la crea
    if ! docker network inspect bridge > /dev/null 2>&1; then
    echo "Creando red bridge..."
    docker network create bridge
    fi

    # =========================
    # TOKENS GITHUB
    # =========================

    echo "Solicitando registration token..."

    # obtiene token para registrar el runner en GitHub
    REG_TOKEN="$(
    curl -fsSL -X POST \
        -H "Accept: application/vnd.github+json" \
        -H "Authorization: Bearer ${GITHUB_PAT}" \
        -H "X-GitHub-Api-Version: ${API_VERSION}" \
        "https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/runners/registration-token" \
    | jq -r '.token'
    )"

    # valida que el token se ha obtenido
    [[ -z "${REG_TOKEN}" || "${REG_TOKEN}" == "null" ]] && echo "ERROR obteniendo REG_TOKEN" && exit 1

    echo "Solicitando remove token..."

    # obtiene token para eliminar el runner
    REMOVE_TOKEN="$(
    curl -fsSL -X POST \
        -H "Accept: application/vnd.github+json" \
        -H "Authorization: Bearer ${GITHUB_PAT}" \
        -H "X-GitHub-Api-Version: ${API_VERSION}" \
        "https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/runners/remove-token" \
    | jq -r '.token'
    )"

    # =========================
    # LIMPIEZA RUNNER
    # =========================

    # si ya existe un runner configurado, lo elimina
    if [[ -f "${RUNNER_HOME}/.runner" ]]; then
    echo "Eliminando runner previo..."
    su -s /bin/bash runner -c "cd ${RUNNER_HOME} && ./config.sh remove --unattended --token '${REMOVE_TOKEN}'" || true
    fi

    # elimina archivos de configuración anteriores
    rm -f "${RUNNER_HOME}/.runner"
    rm -f "${RUNNER_HOME}/.credentials"
    rm -f "${RUNNER_HOME}/.credentials_rsaparams"
    rm -f "${RUNNER_HOME}/.path"
    rm -f "${RUNNER_HOME}/.env"
    rm -rf "${RUNNER_HOME}/_diag"
    rm -rf ${RUNNER_HOME}/.credentials_*

    # =========================
    # CONFIGURACIÓN RUNNER
    # =========================

    # comando para registrar el runner en GitHub
    CONFIG_CMD="./config.sh --url '${REPO_URL}' --token '${REG_TOKEN}' --name '${RUNNER_NAME}' --labels '${RUNNER_LABELS}' --work '${RUNNER_WORKDIR}' --unattended --replace"

    # si es ephemeral, añade flag
    if [[ "${EPHEMERAL}" == "true" ]]; then
    CONFIG_CMD="${CONFIG_CMD} --ephemeral"
    fi

    echo "Configurando runner..."

    # ejecuta configuración como usuario runner
    su -s /bin/bash runner -c "cd ${RUNNER_HOME} && ${CONFIG_CMD}"

    echo "Iniciando runner..."

    # arranca el runner (proceso principal del contenedor)
    exec su -s /bin/bash runner -c "cd ${RUNNER_HOME} && ./run.sh"

Con estos 2 archivos podemos ejecutar los comandos necesarios para crear la imagen completa para nuestro contenedor del Runner:

    podman build -t local/github-runner:latest .

Antes de crear el contenedor es necesario tener creado un PAT Fine-Grained (Personal Access Token). Esto es necesario porque por cada ejecucion del runner de un Workflow este le solicita a Github un Token temporal para esa ejecucion. Cada ejecucion es un token nuevo. Con este PAT podemos automatizar el proceso permitiendo al Runner que por cada ejecucion de un workflow este se comunique con Github, le pida un nuevo Token para ese workflow y despues cuando termine la ejecucion borre automaticamente el Token.

Una vez se ha construido y tenemos la imagen lista, podemos crear el contenedor del Runner.

    podman run -d --name github-runner --privileged -e REPO_URL="https://github.com/SergiiooCS/python-api-cicd-testing" -e GITHUB_OWNER="SergiiooCS" -e GITHUB_REPO="python-api-cicd-testing" -e GITHUB_PAT=$env:GITHUB_TOKEN -e RUNNER_NAME="runner-podman-win11-$(Get-Random)" -e RUNNER_LABELS="self-hosted,linux,x64,podman,local" -v github_runner_work:/actions-runner/_work local/github-runner:latest

El container ha sido creado y deberiamos ver como se ha ejecutado y escribe logs.

    podman logs -f github-runner

Se ha aplicado GitOps en mi servidor minikube local. Para ello he utilizado FluxCD instalado en mi minikube local y enlazado a este repositorio. Componentes utilizados.

1. Crear GitRepository con los permisos suficientes que requiere FluxCD.
2. Crear 'apps.yaml' donde se crea el namespace 'dev', se crea el kustomization encargado de crear los secrets necesarios para el cluster donde se utiliza SOPS para la encriptacion de los secrets y se crea el kustomization encargado de crear y gestionar la aplicacion del cluster.
3. Se ha creado el 'deployment.yaml', 'service.yaml' e 'ingress.yaml' para la aplicacion.
4. Se ha añadido un cambio al CI/CD para que despues de subir la imagen al GHCR cree una PR cambiando el tag de la imagen anterior en el 'deployment.yaml' por el tag de la nueva imagen. De esta forma tenemos actualizada la imagen por cada cambio del codigo. Al ser una PR se puede probar la imagen, si falla es tan sencillo como hacer un 'revert' del cambio de la PR.

Para tener un Dashboard en el cual poder observar, buscar y monitorear el cluster de forma rapida y sencilla he decidido utilizar 'Openlens'.
URL: <https://github.com/MuhammedKalkan/OpenLens>
