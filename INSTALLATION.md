# Ghid de Instalare și Configurare - Sistem de Planificare Examene FIESC

## Cerințe preliminare

- **Docker** și **Docker Compose** (pentru containerizare)
- **Git** (pentru clonarea repository-ului)
- **Cont Google Cloud Platform** (pentru configurarea autentificării OAuth)
- **Cont SendGrid** sau alt serviciu similar (pentru trimiterea notificărilor prin email)

## Configurare pentru Flask și FastAPI

Sistemul utilizează atât Flask cât și FastAPI, fiecare gestionând componente specifice ale aplicației. Configurarea corectă a ambelor framework-uri este esențială pentru funcționarea sistemului.

### Dependențe Python

Asigurați-vă că aveți instalate toate dependențele necesare pentru ambele framework-uri:

```bash
# Instalare dependențe pentru Flask și FastAPI
pip install -r requirements.txt
```

Fișierul `requirements.txt` include toate dependențele necesare:

```
# Framework-uri principale
flask>=2.0.0
fastapi>=0.95.0
uvicorn>=0.20.0

# Extensii Flask
flask-sqlalchemy>=3.0.0
flask-migrate>=4.0.0
flask-login>=0.6.0
flask-wtf>=1.1.0
flask-mail>=0.9.0

# Extensii FastAPI
pydantic>=2.0.0
python-multipart>=0.0.5
python-jose>=3.3.0

# Bază de date
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
alembic>=1.10.0

# Alte dependențe
requests>=2.28.0
pandas>=2.0.0
openpyxl>=3.1.0
sendgrid>=6.9.0
```

## Pași de instalare

### 1. Clonare repository

```bash
git clone https://github.com/fiesc/exam-scheduling.git
cd exam-scheduling
```

### 2. Configurare variabile de mediu

Creați un fișier `.env` în directorul rădăcină al proiectului cu următoarele variabile:

```
# Configurare bază de date
POSTGRES_USER=fiesc_admin
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=exam_scheduling
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Configurare autentificare Google OAuth
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret

# Configurare email (SendGrid)
SENDGRID_API_KEY=your-sendgrid-api-key
EMAIL_FROM=planificare@fiesc.usv.ro
EMAIL_FROM_NAME=Planificare Examene FIESC

# Configurare aplicație
APP_SECRET_KEY=your-secret-key
APP_DEBUG=False
APP_HOST=0.0.0.0
APP_PORT=8000
FRONTEND_URL=http://localhost:8080
```

Înlocuiți valorile de mai sus cu credențialele și configurările specifice mediului dumneavoastră.

### 3. Configurare Google OAuth

1. Accesați [Google Cloud Console](https://console.cloud.google.com/)
2. Creați un nou proiect sau selectați unul existent
3. Accesați "APIs & Services" > "Credentials"
4. Creați credențiale noi de tip "OAuth client ID"
5. Configurați ecranul de consimțământ OAuth:
   - Tip utilizator: Extern
   - Nume aplicație: Sistem Planificare Examene FIESC
   - Domenii autorizate: domeniul pe care va rula aplicația
6. Configurați credențialele OAuth:
   - Tip aplicație: Web application
   - Nume: Sistem Planificare Examene FIESC
   - URI redirecționare autorizate: `http://localhost:8080/auth/callback` (pentru dezvoltare) și URL-ul de producție
7. Notați Client ID și Client Secret și adăugați-le în fișierul `.env`

### 4. Configurare SendGrid

1. Creați un cont pe [SendGrid](https://sendgrid.com/)
2. Generați un API key din secțiunea "Settings" > "API Keys"
3. Verificați domeniul de email pe care îl veți folosi pentru trimiterea notificărilor
4. Adăugați API key-ul în fișierul `.env`

### 5. Construire și lansare containere Docker

```bash
# Construire imagini Docker
docker-compose build

# Lansare containere în background
docker-compose up -d
```

Acest proces va lansa următoarele containere:
- **backend-flask**: Aplicația Flask pentru interfața de administrare și export date
- **backend-fastapi**: Aplicația FastAPI pentru API-ul RESTful
- **frontend**: Aplicația Vue.js
- **db**: Baza de date PostgreSQL
- **nginx**: Server web pentru rutarea cererilor către containerele corespunzătoare

### 6. Inițializare bază de date

```bash
# Rulare migrații pentru Flask
docker-compose exec backend-flask flask db upgrade

# Încărcare date inițiale (opțional)
docker-compose exec backend-flask flask seed
```

### 7. Verificare instalare

Accesați aplicația în browser la adresa:

- Frontend: http://localhost:8080
- Backend API FastAPI: http://localhost:8000/api/docs
- Backend API Flask: http://localhost:8000/api/docs/flask

## Configurare pentru producție

Pentru un mediu de producție, sunt necesare configurări suplimentare:

### 1. Securizare cu HTTPS

1. Obțineți certificate SSL pentru domeniul dumneavoastră (ex. Let's Encrypt)
2. Configurați un proxy invers (Nginx, Traefik) pentru a gestiona conexiunile HTTPS
3. Actualizați fișierul `docker-compose.prod.yml` pentru a include configurările de securitate

### 2. Backup automat bază de date

Configurați un job cron pentru backup-ul automat al bazei de date:

```bash
# Exemplu de script de backup
#!/bin/bash
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR=/path/to/backups
docker-compose exec -T db pg_dump -U fiesc_admin exam_scheduling > $BACKUP_DIR/backup_$DATE.sql
```

### 3. Monitorizare

Configurați un sistem de monitorizare pentru a urmări starea aplicației:

- Prometheus pentru colectarea metricilor
- Grafana pentru vizualizarea metricilor
- Alertmanager pentru notificări în caz de probleme

## Structura containerelor Docker

Aplicația este compusă din următoarele containere Docker:

1. **backend-flask**: Serviciul backend Flask
2. **backend-fastapi**: Serviciul backend FastAPI
3. **frontend**: Serviciul frontend Vue.js
4. **db**: Baza de date PostgreSQL
5. **nginx**: Server web pentru servirea aplicației frontend și proxy pentru backend

## Depanare

### Probleme comune și soluții

#### 1. Eroare la conectarea la baza de date

```
Error: could not connect to server: Connection refused
```

**Soluție**: Verificați dacă containerul bazei de date rulează și dacă variabilele de mediu pentru conexiune sunt corecte.

```bash
docker-compose ps
docker-compose logs db
```

#### 2. Eroare la autentificarea Google OAuth

```
Error: invalid_client
```

**Soluție**: Verificați dacă Client ID și Client Secret sunt corecte și dacă URI-urile de redirecționare sunt configurate corect în consola Google Cloud.

#### 3. Eroare la trimiterea email-urilor

```
Error: Unauthorized
```

**Soluție**: Verificați dacă API key-ul SendGrid este valid și dacă domeniul de email este verificat.

## Actualizare aplicație

Pentru a actualiza aplicația la o versiune nouă:

```bash
# Oprire containere
docker-compose down

# Actualizare repository
git pull

# Reconstruire imagini
docker-compose build

# Relansare containere
docker-compose up -d

# Actualizare bază de date (dacă este necesar)
docker-compose exec backend-flask flask db upgrade
```

## Backup și restaurare

### Backup bază de date

```bash
docker-compose exec db pg_dump -U fiesc_admin exam_scheduling > backup.sql
```

### Restaurare bază de date

```bash
cat backup.sql | docker-compose exec -T db psql -U fiesc_admin exam_scheduling
```

## Configurare pentru dezvoltare

Pentru un mediu de dezvoltare, utilizați fișierul `docker-compose.dev.yml`:

```bash
docker-compose -f docker-compose.dev.yml up
```

Acest fișier include configurări specifice pentru dezvoltare, cum ar fi:

- Volume-uri pentru codul sursă (pentru dezvoltare live)
- Porturi expuse pentru debugging
- Variabile de mediu pentru debugging
