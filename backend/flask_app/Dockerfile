# Imagine de bază cu Python
FROM python:3.9
# Setează folderul de lucru în container
WORKDIR /app
# Copiază fișierul cu dependențe
COPY requirements.txt .
# Instalează Flask și celelalte librării
RUN pip install -r requirements.txt
# Copiază restul fișierelor în container
COPY . .
# Pornește serverul Flask
CMD ["python", "app.py"]
