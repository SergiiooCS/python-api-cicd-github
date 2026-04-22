# python-api-cicd-testing

Repositorio creado para realizar pruebas de CI / CD con Github Actions.

Pasos del Workflow CI:

1. Checkout del codigo.
2. Setup del entorno (python 3.12, dependencias, librerias, etc).
3. Instalacion de dependencias utilizando el archivo 'requirements.txt'.
4. Crear un Fail Fast para ahorrar tiempo y recursos de ejecucion (Lint + calidad de codigo).
5. Test unitarios (Pytest).
6. Construir el proyecto y almacenar el paquete en el repositorio.

Proximos pasos:
CI:

- Configurar un runner self-hosted para poder hacer un CD a Minikube local.

Pasos del Workflow CD:
(Crear Workflow para CD)
