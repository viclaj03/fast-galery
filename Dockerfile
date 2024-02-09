FROM python:3.11.2

WORKDIR /app

ENV HOST 0.0.0.0

COPY . /app

RUN pip install -r requirements.txt

# Instalar uvicorn en la ubicación deseada
RUN pip install uvicorn

# Definir el comando de inicio del contenedor
CMD ["uvicorn", "main:app", "--port=8000", "--host=0.0.0.0"]
