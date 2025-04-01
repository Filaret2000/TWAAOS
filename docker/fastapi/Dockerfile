FROM python:3.9-slim

WORKDIR /app

# Instalare dependențe
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copierea codului sursă
COPY src/common/ /app/src/common/
COPY src/fastapi_app/ /app/src/fastapi_app/

# Variabile de mediu
ENV PYTHONPATH=/app

# Expunere port
EXPOSE 8000

# Comandă de pornire
CMD ["uvicorn", "src.fastapi_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
