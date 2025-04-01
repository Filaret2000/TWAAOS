# Ghid Dezvoltare FIESC - Sistem de Planificare Examene

## Tehnologii utilizate

- **Backend**: Python 3 cu Flask/FastAPI
- **Frontend**: Vue.js
- **Baza de date**: PostgreSQL
- **Autentificare**: Google OAuth 2.0 ("Sign In With Google")
- **Email**: Servicii externe (ex. SendGrid)
- **Containerizare**: Docker

## Integrarea Flask și FastAPI

Proiectul utilizează atât Flask cât și FastAPI, fiecare având responsabilități specifice:

### Structura proiectului pentru integrarea Flask și FastAPI

```text
src/
├── common/              # Cod comun pentru ambele framework-uri
│   ├── models/          # Modele de date partajate
│   ├── services/        # Servicii business partajate
│   └── utils/           # Utilități comune
├── flask_app/           # Aplicația Flask
│   ├── templates/       # Template-uri Jinja2
│   ├── static/          # Fișiere statice
│   ├── routes/          # Rutele Flask
│   └── forms/           # Formulare WTForms
├── fastapi_app/         # Aplicația FastAPI
│   ├── api/             # Endpoint-uri API
│   ├── schemas/         # Scheme Pydantic
│   └── dependencies/    # Dependențe FastAPI
├── frontend/            # Aplicație Vue.js
└── tests/               # Teste unitare și de integrare
```

### Convenții de dezvoltare pentru Flask și FastAPI

#### Flask
- Utilizați Blueprint-uri pentru organizarea rutelor
- Folosiți extensia Flask-SQLAlchemy pentru ORM
- Implementați formulare cu Flask-WTF
- Utilizați Flask-Login pentru gestionarea sesiunilor

#### FastAPI
- Organizați endpoint-urile pe module folosind APIRouter
- Definiți scheme Pydantic pentru validarea datelor
- Utilizați dependențe pentru injecția de dependențe
- Implementați documentația cu Swagger UI și ReDoc

### Configurarea Swagger UI pentru testare manuală

Documentația interactivă Swagger UI este esențială pentru testarea manuală a API-ului. Configurați-o astfel:

#### Pentru FastAPI
FastAPI generează automat documentația Swagger. Configurați-o în `fastapi_app/main.py`:

```python
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html

app = FastAPI(
    title="Sistem Planificare Examene API",
    description="API pentru sistemul de planificare examene FIESC",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Personalizare Swagger UI
@app.get("/api/custom-docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/api/openapi.json",
        title="API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css",
    )
```

#### Pentru Flask
Pentru Flask, utilizați extensia `flask-swagger-ui`:

```python
from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

# Configurare Swagger UI pentru Flask
SWAGGER_URL = '/api/docs/flask'
API_URL = '/api/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Sistem Planificare Examene API (Flask)"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Endpoint pentru specificația OpenAPI
@app.route('/api/swagger.json')
def swagger_spec():
    with open('swagger.json', 'r') as f:
        return jsonify(json.load(f))
```

### Testarea manuală a API-ului cu Swagger UI

Pentru a testa manual API-ul folosind Swagger UI:

1. Accesați `/api/docs` pentru API-ul FastAPI
2. Accesați `/api/docs/flask` pentru API-ul Flask
3. Autentificați-vă folosind butonul "Authorize" din interfața Swagger
4. Expandați endpoint-ul dorit și apăsați "Try it out"
5. Completați parametrii necesari și executați cererea
6. Analizați răspunsul returnat (status code, headers, body)

Această abordare permite testarea rapidă a API-ului fără a fi nevoie de instrumente externe precum Postman.

### Rularea aplicațiilor în dezvoltare

Pentru a rula aplicația Flask:
```bash
cd src
python -m flask_app.app
```

Pentru a rula aplicația FastAPI:
```bash
cd src
uvicorn fastapi_app.main:app --reload
```

Pentru a rula ambele aplicații cu Docker Compose:
```bash
docker-compose -f docker-compose.dev.yml up
```

## Structură Proiect

```text
src/
├── api/                 # API endpoints
│   ├── v1/              # Endpoint-uri principale
│   └── integrations/    # Integrări ORAR USV
├── models/              # Modele bază de date
├── services/            # Logică business
│   ├── auth/            # Servicii autentificare
│   ├── email/           # Servicii notificări email
│   ├── export/          # Servicii export PDF/Excel
│   └── scheduling/      # Logică planificare examene
├── frontend/            # Aplicație Vue.js
│   ├── src/             # Cod sursă frontend
│   │   ├── components/  # Componente Vue
│   │   ├── views/       # Pagini Vue
│   │   ├── router/      # Configurare rutare
│   │   └── store/       # Vuex state management
│   └── public/          # Fișiere statice
└── tests/               # Teste unitare și de integrare
```

## Configurare Mediu de Dezvoltare

### 1. Instalare Dependințe

Instalează dependințele necesare pentru dezvoltare:

```bash
python -m pip install -r requirements-dev.txt
```

### 2. Configurare Pre-commit Hooks

Instalează pre-commit hooks pentru a respecta standardele de cod:

```bash
pre-commit install
```

### 3. Rulează Servicii în Mod Dezvoltare

Lansează aplicația în mod de dezvoltare:

```bash
docker-compose -f docker-compose.dev.yml up
```

### 4. Accesarea API-urilor Orar USV

API-urile Orar USV pot fi accesate la următoarele endpoint-uri:

- Cadre didactice: `https://orar.usv.ro/orar/vizualizare/data/cadre.php?json`
- Săli: `https://orar.usv.ro/orar/vizualizare/data/sali.php?json`
- Facultăți: `https://orar.usv.ro/orar/vizualizare/data/facultati.php?json`
- Subgrupe: `https://orar.usv.ro/orar/vizualizare/data/subgrupe.php?json`
- Orar pentru o semi-grupă: `https://orar.usv.ro/orar/vizualizare/data/orarSPG.php?ID=1028&mod=grupa&json`

## Debug în VS Code

Adaugă configurația de debugging în fișierul `.vscode/launch.json`:

```json
{
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["main:app", "--reload"]
    }
  ]
}
```

## Standarde Cod

### Python:
- Respectă PEP 8 cu type hints
- Docstrings în stil Google

### Git:
```bash
git commit -m "feat(api): add PDF export endpoint"
git commit -m "fix(ui): resolve date picker overflow"
```

## Rulare Teste

Testează un fișier specific:

```bash
pytest tests/api/v1/test_schedules.py -v
```

Testează cu coverage:

```bash
pytest --cov=src --cov-report=html
```

## Flux de Lucru pentru Implementarea Funcționalităților

1. **Secretariat (SEC)**:
   - Implementare încărcare fișiere Excel
   - Integrare cu API-urile Orar USV
   - Generare export PDF/Excel

2. **Șef Grupă (SG)**:
   - Implementare interfață propunere date examene
   - Sistem de notificări pentru respingeri/aprobări

3. **Cadru Didactic (CD)**:
   - Implementare interfață validare propuneri
   - Sistem de alocare săli și asistenți

4. **Administrator (ADM)**:
   - Implementare interfață de configurare
   - Gestionare utilizatori și facultăți

## Diagramă Flux Date

```mermaid
graph LR
    A[Frontend] -->|HTTP| B[API]
    B -->|SQL| C[(DB)]
    B -->|REST| D[ORAR USV]
    B -->|SMTP| E[Email]