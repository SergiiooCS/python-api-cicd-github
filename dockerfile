# PYTHON BASE IMAGE.
FROM python:3.12-slim

# SET WORKING DIRECTORY.
WORKDIR /app

# INSTALL DEPENDENCIES
# Copia el archivo .whl generado en la etapa de construccion (GH Action CI) al contenedor.
COPY dist/*.whl /tmp/
# Instala el paquete .whl utilizando pip, asegurandose de no usar la cache para evitar problemas de espacio y garantizar que se instale la version correcta del paquete.
RUN pip install --no-cache-dir /tmp/*.whl

# RUN THE APPLICATION.
CMD ["python", "-m", "app.main"]