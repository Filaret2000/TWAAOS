FROM python:3.9-slim

WORKDIR /app

# Instalare dependențe sistem
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    fontconfig \
    libfreetype6 \
    libjpeg62-turbo \
    libpng16-16 \
    libx11-6 \
    libxcb1 \
    libxext6 \
    libxrender1 \
    xfonts-75dpi \
    xfonts-base \
    && rm -rf /var/lib/apt/lists/*

# Instalare wkhtmltopdf
RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb \
    && dpkg -i wkhtmltox_0.12.6-1.buster_amd64.deb || true \
    && apt-get update && apt-get -f install -y \
    && rm wkhtmltox_0.12.6-1.buster_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

# Instalare dependențe
COPY requirements.txt .
# Instalăm mai întâi numpy pentru a evita incompatibilitățile binare
RUN pip install --no-cache-dir numpy==1.24.3
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pdfkit==1.0.0

# Copierea codului sursă
COPY src/common/ /app/src/common/
COPY src/flask_app/ /app/src/flask_app/

# Crearea fișierelor __init__.py necesare
RUN mkdir -p /app/src && touch /app/src/__init__.py

# Variabile de mediu
ENV PYTHONPATH=/app
ENV FLASK_APP=src.flask_app.app
ENV FLASK_ENV=development

# Expunere port
EXPOSE 5000

# Comandă de pornire
CMD ["flask", "run", "--host=0.0.0.0"]
