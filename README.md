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

    set -euo pipefail
    # -e: si falla un comando, el script termina
    # -u: si se usa una variable no definida, falla
    # -o pipefail: si falla algo dentro de un pipe, tambien falla

    API_VERSION="2022-11-28"
    # version de la api de github que se va a usar en las llamadas

    DOCKERD_PID=""
    # aqui se guardara el pid del proceso dockerd para poder pararlo luego

    cleanup() {
    echo "Apagando runner..."

    if [[ -n "${REMOVE_TOKEN:-}" ]]; then
        # comprueba si existe un token de borrado y no esta vacio
        echo "Intentando desregistrar runner..."
        su -s /bin/bash runner -c "cd ${RUNNER_HOME} && ./config.sh remove --unattended --token '${REMOVE_TOKEN}'" || true
        # ejecuta como usuario runner el borrado del runner en github
        # || true evita que el script falle si no se puede borrar
    fi

    if [[ -n "${DOCKERD_PID:-}" ]]; then
        # comprueba si se guardo el pid de dockerd
        echo "Parando dockerd..."
        kill "${DOCKERD_PID}" || true
        # mata el proceso dockerd
        # || true evita error si ya estaba parado
    fi
    }

    trap 'cleanup; exit 130' INT
    # si recibe interrupcion (ctrl+c), ejecuta cleanup y sale con codigo 130

    trap 'cleanup; exit 143' TERM
    # si recibe señal term, ejecuta cleanup y sale con codigo 143

    : "${RUNNER_HOME:=/actions-runner}"
    # si RUNNER_HOME no existe, le asigna /actions-runner

    if [[ -z "${REPO_URL:-}" ]]; then
    # comprueba si falta la url del repositorio
    echo "ERROR: falta REPO_URL"
    exit 1
    fi

    if [[ -z "${GITHUB_PAT:-}" ]]; then
    # comprueba si falta el token personal de github
    echo "ERROR: falta GITHUB_PAT"
    exit 1
    fi

    if [[ -z "${GITHUB_OWNER:-}" ]]; then
    # comprueba si falta el owner del repo u organizacion
    echo "ERROR: falta GITHUB_OWNER"
    exit 1
    fi

    if [[ -z "${GITHUB_REPO:-}" ]]; then
    # comprueba si falta el nombre del repo
    echo "ERROR: falta GITHUB_REPO"
    exit 1
    fi

    RUNNER_NAME="${RUNNER_NAME:-podman-runner}"
    # nombre por defecto del runner si no se pasa por variable
    RUNNER_LABELS="${RUNNER_LABELS:-self-hosted,linux,x64,podman,local}"
    # labels por defecto del runner
    RUNNER_WORKDIR="${RUNNER_WORKDIR:-_work}"
    # carpeta de trabajo por defecto del runner
    EPHEMERAL="${EPHEMERAL:-false}"
    # define si el runner sera efimero o no

    mkdir -p /var/run /var/lib/docker "${RUNNER_HOME}/${RUNNER_WORKDIR}"
    # crea directorios necesarios para docker y para el runner

    chown -R runner:runner "${RUNNER_HOME}"
    # cambia el dueño del directorio del runner al usuario runner
    echo "Arrancando dockerd..."
    dockerd \
    --host=unix:///var/run/docker.sock \
    # hace que docker escuche en el socket unix habitual
    -G docker \
    # asigna el grupo docker al socket
    --bridge=none \
    # no crea red bridge por defecto
    --iptables=false \
    # no modifica reglas iptables
    --ip-forward=false \
    # no habilita reenvio de paquetes
    --ip-masq=false \
    # no habilita ip masquerade
    --userland-proxy=false \
    # desactiva el proxy userland
    --storage-driver=vfs \
    # usa el driver de almacenamiento vfs, mas simple pero menos eficiente
    > /tmp/dockerd.log 2>&1 &
    # guarda logs en fichero y lanza dockerd en segundo plano

    DOCKERD_PID=$!
    # guarda el pid del ultimo proceso lanzado en background

    echo "Esperando a que Docker responda..."
    for i in $(seq 1 30); do
    # hace hasta 30 intentos para comprobar si docker esta listo
    if docker info > /dev/null 2>&1; then
        # intenta consultar info de docker sin mostrar salida
        echo "Docker está listo."
        break
    fi
    sleep 2
    # espera 2 segundos antes del siguiente intento
    done

    if ! docker info > /dev/null 2>&1; then
    # si despues de esperar docker sigue sin responder
    echo "ERROR: Docker no arrancó correctamente"
    echo "==== dockerd.log ===="
    cat /tmp/dockerd.log || true
    # imprime el log de dockerd para depurar
    # || true evita fallo si no se puede leer
    exit 1
    # termina el script con error
    fi

    echo "Solicitando registration token..."
    REG_TOKEN="$(
    curl -fsSL -X POST \
        -H "Accept: application/vnd.github+json" \
        # indica el formato esperado de la api

        -H "Authorization: Bearer ${GITHUB_PAT}" \
        # autentica con el token personal de github

        -H "X-GitHub-Api-Version: ${API_VERSION}" \
        # manda la version de la api

        "https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/runners/registration-token" \
        # endpoint para pedir el token temporal de registro del runner

    | jq -r '.token'
    # extrae solo el campo token de la respuesta json
    )"
    # guarda el token en la variable REG_TOKEN

    if [[ -z "${REG_TOKEN}" || "${REG_TOKEN}" == "null" ]]; then
    # comprueba si el token no existe o vino null

    echo "ERROR: no se pudo obtener registration token"
    exit 1
    fi

    echo "Solicitando remove token..."
    REMOVE_TOKEN="$(
    curl -fsSL -X POST \
        -H "Accept: application/vnd.github+json" \
        # indica formato esperado

        -H "Authorization: Bearer ${GITHUB_PAT}" \
        # autentica con el token personal

        -H "X-GitHub-Api-Version: ${API_VERSION}" \
        # version de la api

        "https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/runners/remove-token" \
        # endpoint para pedir token temporal de borrado del runner

    | jq -r '.token'
    # extrae solo el token del json
    )"
    # guarda el token en REMOVE_TOKEN

    if [[ -z "${REMOVE_TOKEN}" || "${REMOVE_TOKEN}" == "null" ]]; then
    # comprueba si no se pudo obtener el token de borrado

    echo "WARNING: no se pudo obtener remove token; la limpieza puede fallar"
    REMOVE_TOKEN=""
    # deja la variable vacia para que cleanup no intente usar un valor invalido
    fi

    CONFIG_CMD="./config.sh --url '${REPO_URL}' --token '${REG_TOKEN}' --name '${RUNNER_NAME}' --labels '${RUNNER_LABELS}' --work '${RUNNER_WORKDIR}' --unattended --replace"
    # construye el comando para configurar el runner de github actions

    if [[ "${EPHEMERAL}" == "true" ]]; then
    # comprueba si el runner debe ser efimero

    CONFIG_CMD="${CONFIG_CMD} --ephemeral"
    # añade la opcion para que el runner solo haga un trabajo y luego se elimine
    fi

    echo "Configurando runner ${RUNNER_NAME}..."
    su -s /bin/bash runner -c "cd ${RUNNER_HOME} && ${CONFIG_CMD}"
    # ejecuta la configuracion del runner como usuario runner dentro del directorio correcto
    echo "Iniciando runner..."
    exec su -s /bin/bash runner -c "cd ${RUNNER_HOME} && ./run.sh"
    # arranca el runner como proceso principal del contenedor
    # exec sustituye el shell actual por este proceso

Con estos 2 archivos podemos ejecutar los comandos necesarios para crear la imagen completa para nuestro contenedor del Runner:

    podman build -t local/github-runner:latest .

Antes de crear el contenedor es necesario tener creado un PAT Fine-Grained (Personal Access Token). Esto es necesario porque por cada ejecucion del runner de un Workflow este le solicita a Github un Token temporal para esa ejecucion. Cada ejecucion es un token nuevo. Con este PAT podemos automatizar el proceso permitiendo al Runner que por cada ejecucion de un workflow este se comunique con Github, le pida un nuevo Token para ese workflow y despues cuando termine la ejecucion borre automaticamente el Token.

Una vez se ha construido y tenemos la imagen lista, podemos crear el contenedor del Runner.

    podman run -d --name github-runner --privileged -e REPO_URL="https://github.com/<NOMBRE_USUARIO>/<NOMBRE_REPOSITORIO>" -e GITHUB_OWNER="<NOMBRE_USUARIO>" -e GITHUB_REPO="<NOMBRE_REPOSITORIO>" -e GITHUB_PAT="<CODIGO_PAT_FINE_GRAINED>" -e RUNNER_NAME="runner-podman-win11" -e RUNNER_LABELS="self-hosted,linux,x64,podman,local" -v github_runner_work:/actions-runner/_work -v github_runner_docker:/var/lib/docker local/github-runner:latest

El container ha sido creado y deberiamos ver como se ha ejecutado y escribe logs.

    podman logs -f github-runner

Pasos del Workflow CD:
(Crear Workflow para CD)

Proximos pasos:

1. Que Minikube tenga acceso a GHCR
2. Manifests Kubernetes de tu app
3. Que tu runner pueda ejecutar kubectl contra Minikube
4. Workflow CD
