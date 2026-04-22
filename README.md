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

Proximos pasos:
CI:

- Crear una VM local para alojar el Runner Self-hosted.
- Configurar un runner self-hosted (comunicarlo con GH, establecer permisos necesarios, ejecutar CI en self-hosted como prueba) para poder hacer un CD a Minikube local.

Pasos del Workflow CD:
(Crear Workflow para CD)
