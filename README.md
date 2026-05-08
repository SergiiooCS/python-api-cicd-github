# python-api-cicd-testing

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

Este workflow se encarga de validar y preparar la aplicación Python.

### Pasos principales

1. Checkout del código.
2. Configuración de Python `3.12`.
3. Instalación de dependencias desde `requirements.txt`.
4. Ejecución de lint con `flake8`.
5. Ejecución de tests unitarios con `pytest`.
6. Construcción del paquete Python `.whl`.
7. Publicación del `.whl` como artifact de GitHub Actions.

### Objetivo

Garantizar que el código es válido antes de construir una imagen Docker o desplegar cambios en el entorno GitOps.

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

Incluye:

- Ubuntu `24.04`
- Docker CE
- containerd
- Docker Buildx
- Docker Compose
- Git
- curl
- jq
- yq
- GitHub Actions Runner

### Construir imagen

```powershell
podman build -t local/github-runner:latest .
```

---

## Entrypoint del runner

El archivo `entrypoint.sh` automatiza el ciclo de vida del runner.

### Responsabilidades principales

1. Validar variables de entorno necesarias.
2. Limpiar procesos previos de Docker y containerd.
3. Eliminar archivos temporales `.pid` y `.sock`.
4. Arrancar `dockerd` dentro del contenedor.
5. Comprobar que Docker responde correctamente.
6. Solicitar tokens temporales a la API de GitHub.
7. Desregistrar runners previos si existen.
8. Registrar un nuevo runner.
9. Ejecutar el runner.
10. Limpiar recursos al recibir señales `SIGINT` o `SIGTERM`.

### Conceptos trabajados

- Bash strict mode: `set -euo pipefail`
- Señales Linux: `SIGINT`, `SIGTERM`, `SIGKILL`
- Procesos en segundo plano con `&`
- PID del último proceso background con `$!`
- Unix sockets
- PID files
- `curl` para comunicación con APIs
- `jq` para procesar JSON
- `trap` para limpieza controlada

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

### Cambios a aplicar

#### Branch Protection Rules

Los rulesets en cuentas personales privadas de GitHub Free no pueden aplicarse realmente sobre las ramas protegidas.

En este laboratorio no puedo forzar su aplicación, pero los configuro igualmente para aprender el flujo y las buenas prácticas utilizadas en entornos reales.

##### Ruleset para proteger la rama `main`

- **Nombre:** `Protect main branch`
- **Enforcement status:** `Active`
- **Target branches:** `main`

##### Reglas configuradas

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

#### Secret Management

Pendiente de aplicar/mejorar:

- Rotación de tokens
- Principio de mínimos privilegios
- Gestión de secretos en GitHub Actions
- Secretos para Kubernetes
- Buenas prácticas de almacenamiento de credenciales

---

#### `GITHUB_TOKEN` Scopes

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

## Cambios a aplicar

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

- Permisos mínimos necesarios en workflows CI/CD
- Revisión de permisos del `GITHUB_TOKEN`
- Revisión de permisos del `GITHUB_PAT`
- Eliminación de permisos innecesarios
- Separación entre permisos de CI y CD
