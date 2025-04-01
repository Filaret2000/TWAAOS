# Documentație API - Sistem de Planificare Examene FIESC

## Prezentare generală

API-ul sistemului de planificare examene FIESC este implementat utilizând atât Flask cât și FastAPI, oferind endpoint-uri RESTful pentru toate funcționalitățile aplicației. Acest document descrie endpoint-urile disponibile, parametrii necesari și răspunsurile așteptate.

## Implementarea API cu Flask și FastAPI

Sistemul utilizează ambele framework-uri în mod complementar, fiecare gestionând componente specifice ale API-ului:

### API implementat cu Flask
- **Endpoint-uri pentru administrare**: `/api/admin/*`
- **Endpoint-uri pentru autentificare**: `/api/auth/*`
- **Endpoint-uri pentru export date**: `/api/export/*`
- **Endpoint-uri pentru încărcare fișiere**: `/api/upload/*`

### API implementat cu FastAPI
- **Endpoint-uri pentru planificări**: `/api/schedules/*`
- **Endpoint-uri pentru utilizatori**: `/api/users/*`
- **Endpoint-uri pentru discipline**: `/api/subjects/*`
- **Endpoint-uri pentru săli**: `/api/rooms/*`
- **Endpoint-uri pentru notificări**: `/api/notifications/*`

### Accesarea documentației API
- Documentație Flask API: `/api/docs/flask` (implementată cu Swagger UI)
- Documentație FastAPI: `/api/docs` (generată automat de FastAPI)

## Testarea manuală a API-ului cu Swagger UI

Swagger UI oferă o interfață interactivă pentru testarea manuală a tuturor endpoint-urilor API, fiind un instrument esențial pentru dezvoltare și debugging.

### Accesarea Swagger UI

- **Pentru FastAPI**: Accesați `/api/docs` în browser
- **Pentru Flask**: Accesați `/api/docs/flask` în browser

### Funcționalități Swagger UI

- **Explorare endpoint-uri**: Toate endpoint-urile sunt grupate pe categorii și pot fi expandate pentru a vedea detalii
- **Autentificare**: Butonul "Authorize" permite introducerea token-ului JWT pentru testarea endpoint-urilor protejate
- **Testare interactivă**: Butonul "Try it out" permite completarea parametrilor și executarea cererii direct din browser
- **Vizualizare răspunsuri**: Răspunsurile sunt afișate formatat, cu evidențierea codului de status și a headerelor
- **Schema de date**: Toate modelele de date sunt documentate detaliat, cu exemple și validări
- **Coduri de eroare**: Documentația include toate codurile de eroare posibile și semnificația lor

### Exemplu de utilizare

1. Accesați `/api/docs` în browser
2. Apăsați butonul "Authorize" și introduceți token-ul JWT în format `Bearer <token>`
3. Navigați la endpoint-ul dorit (ex. `/api/schedules`)
4. Apăsați "Try it out"
5. Completați parametrii necesari (ex. `groupId=123`)
6. Apăsați "Execute"
7. Analizați răspunsul returnat

### Generarea specificației OpenAPI

Specificația OpenAPI este generată automat de FastAPI și poate fi accesată la `/api/openapi.json`. Pentru Flask, specificația este definită manual în fișierul `swagger.json`.

## Autentificare

Toate endpoint-urile API (cu excepția celor publice) necesită autentificare. Autentificarea se realizează utilizând tokenuri JWT (JSON Web Tokens) obținute prin procesul de autentificare Google OAuth 2.0.

### Obținere token

```
POST /api/auth/login
```

**Request:**
```json
{
  "token": "google_oauth_token"
}
```

**Response:**
```json
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 123,
    "email": "user@usv.ro",
    "role": "SEC",
    "firstName": "Nume",
    "lastName": "Prenume"
  }
}
```

### Utilizare token

Pentru a accesa endpoint-urile protejate, includeți tokenul în header-ul Authorization:

```
Authorization: Bearer jwt_token
```

## Endpoint-uri API

### 1. Utilizatori

#### 1.1. Obținere utilizator curent

```
GET /api/users/me
```

**Response:**
```json
{
  "id": 123,
  "email": "user@usv.ro",
  "role": "SEC",
  "firstName": "Nume",
  "lastName": "Prenume"
}
```

#### 1.2. Listare șefi de grupă (doar pentru SEC și ADM)

```
GET /api/users/group-leaders
```

**Response:**
```json
[
  {
    "id": 123,
    "email": "student@student.usv.ro",
    "firstName": "Nume",
    "lastName": "Prenume",
    "groupId": 456,
    "groupName": "3A2"
  }
]
```

### 2. Discipline

#### 2.1. Listare discipline

```
GET /api/subjects
```

**Parametri query:**
- `groupId` (opțional): Filtrare după grupă
- `teacherId` (opțional): Filtrare după cadru didactic

**Response:**
```json
[
  {
    "id": 123,
    "name": "Tehnologii Web Avansate și Aplicații Orientate spre Servicii",
    "shortName": "TWAAOS",
    "studyProgram": "Calculatoare",
    "studyYear": 3,
    "groupId": 456
  }
]
```

### 3. Planificări examene

#### 3.1. Listare planificări

```
GET /api/schedules
```

**Parametri query:**
- `groupId` (opțional): Filtrare după grupă
- `teacherId` (opțional): Filtrare după cadru didactic
- `subjectId` (opțional): Filtrare după disciplină
- `status` (opțional): Filtrare după status (proposed, approved, rejected)
- `startDate` (opțional): Filtrare după data de început
- `endDate` (opțional): Filtrare după data de sfârșit

**Response:**
```json
[
  {
    "id": 123,
    "subjectId": 456,
    "subjectName": "TWAAOS",
    "teacherId": 789,
    "teacherName": "Prof. Dr. Ing. Nume Prenume",
    "roomId": 101,
    "roomName": "C201",
    "groupId": 202,
    "groupName": "3A2",
    "date": "2025-01-15",
    "startTime": "10:00:00",
    "endTime": "12:00:00",
    "status": "approved",
    "assistants": [
      {
        "id": 303,
        "name": "Asist. Dr. Ing. Nume Prenume"
      }
    ]
  }
]
```

#### 3.2. Propunere dată examen (pentru SG)

```
POST /api/schedules/propose
```

**Request:**
```json
{
  "subjectId": 456,
  "date": "2025-01-15"
}
```

**Response:**
```json
{
  "id": 123,
  "subjectId": 456,
  "date": "2025-01-15",
  "status": "proposed"
}
```

#### 3.3. Aprobare/Respingere propunere (pentru CD)

```
PUT /api/schedules/{scheduleId}/status
```

**Request:**
```json
{
  "status": "approved", // sau "rejected"
  "message": "Motiv respingere" // opțional, pentru status "rejected"
}
```

**Response:**
```json
{
  "id": 123,
  "status": "approved",
  "message": null
}
```

#### 3.4. Configurare detalii examen (pentru CD)

```
PUT /api/schedules/{scheduleId}/details
```

**Request:**
```json
{
  "roomId": 101,
  "startTime": "10:00:00",
  "endTime": "12:00:00",
  "assistantIds": [303, 404]
}
```

**Response:**
```json
{
  "id": 123,
  "roomId": 101,
  "roomName": "C201",
  "startTime": "10:00:00",
  "endTime": "12:00:00",
  "assistants": [
    {
      "id": 303,
      "name": "Asist. Dr. Ing. Nume Prenume"
    },
    {
      "id": 404,
      "name": "Asist. Dr. Ing. Alt Nume"
    }
  ]
}
```

#### 3.5. Verificare conflicte (pentru CD și SEC)

```
GET /api/schedules/conflicts
```

**Parametri query:**
- `date` (opțional): Filtrare după dată
- `teacherId` (opțional): Filtrare după cadru didactic
- `roomId` (opțional): Filtrare după sală

**Response:**
```json
[
  {
    "type": "teacher_conflict",
    "scheduleId1": 123,
    "scheduleId2": 456,
    "teacherId": 789,
    "teacherName": "Prof. Dr. Ing. Nume Prenume",
    "date": "2025-01-15",
    "timeRange1": "10:00:00-12:00:00",
    "timeRange2": "11:00:00-13:00:00"
  },
  {
    "type": "room_conflict",
    "scheduleId1": 123,
    "scheduleId2": 789,
    "roomId": 101,
    "roomName": "C201",
    "date": "2025-01-15",
    "timeRange1": "10:00:00-12:00:00",
    "timeRange2": "11:00:00-13:00:00"
  }
]
```

### 4. Săli

#### 4.1. Listare săli disponibile

```
GET /api/rooms
```

**Parametri query:**
- `date` (opțional): Filtrare după dată
- `startTime` (opțional): Filtrare după ora de început
- `endTime` (opțional): Filtrare după ora de sfârșit
- `buildingName` (opțional): Filtrare după clădire

**Response:**
```json
[
  {
    "id": 101,
    "name": "C201",
    "shortName": "C201",
    "buildingName": "Corp C",
    "capacity": 30,
    "computers": 15
  }
]
```

### 5. Cadre didactice

#### 5.1. Listare cadre didactice

```
GET /api/teachers
```

**Parametri query:**
- `department` (opțional): Filtrare după departament

**Response:**
```json
[
  {
    "id": 789,
    "firstName": "Nume",
    "lastName": "Prenume",
    "email": "nume.prenume@usv.ro",
    "department": "Calculatoare"
  }
]
```

### 6. Export date

#### 6.1. Export PDF

```
GET /api/export/pdf
```

**Parametri query:**
- `groupId` (opțional): Filtrare după grupă
- `teacherId` (opțional): Filtrare după cadru didactic
- `startDate` (opțional): Filtrare după data de început
- `endDate` (opțional): Filtrare după data de sfârșit

**Response:**
Fișier PDF cu planificarea examenelor.

#### 6.2. Export Excel

```
GET /api/export/excel
```

**Parametri query:**
- `groupId` (opțional): Filtrare după grupă
- `teacherId` (opțional): Filtrare după cadru didactic
- `startDate` (opțional): Filtrare după data de început
- `endDate` (opțional): Filtrare după data de sfârșit

**Response:**
Fișier Excel cu planificarea examenelor.

### 7. Notificări

#### 7.1. Listare notificări

```
GET /api/notifications
```

**Parametri query:**
- `status` (opțional): Filtrare după status (read, unread)

**Response:**
```json
[
  {
    "id": 123,
    "message": "Propunerea pentru examenul de TWAAOS a fost aprobată.",
    "dateSent": "2025-01-10T14:30:00",
    "status": "unread"
  }
]
```

#### 7.2. Marcare notificare ca citită

```
PUT /api/notifications/{notificationId}/read
```

**Response:**
```json
{
  "id": 123,
  "status": "read"
}
```

### 8. Administrare (doar pentru ADM)

#### 8.1. Configurare perioadă examene

```
POST /api/admin/exam-periods
```

**Request:**
```json
{
  "examStartDate": "2025-01-15",
  "examEndDate": "2025-01-30",
  "colloquiumStartDate": "2025-01-05",
  "colloquiumEndDate": "2025-01-14"
}
```

**Response:**
```json
{
  "examStartDate": "2025-01-15",
  "examEndDate": "2025-01-30",
  "colloquiumStartDate": "2025-01-05",
  "colloquiumEndDate": "2025-01-14"
}
```

#### 8.2. Încărcare template Excel

```
POST /api/admin/excel-templates
```

**Request:**
Formular multipart cu fișier Excel.

**Response:**
```json
{
  "id": 123,
  "name": "Template discipline",
  "filePath": "/templates/subjects_template.xlsx",
  "description": "Template pentru încărcarea disciplinelor"
}
```

## Integrare cu API-ul Orar USV

API-ul sistemului de planificare examene se integrează cu API-ul Orar USV pentru a prelua informații despre discipline, săli și cadre didactice.

### Endpoint-uri Orar USV

- Cadre didactice: `https://orar.usv.ro/orar/vizualizare/data/cadre.php?json`
- Săli: `https://orar.usv.ro/orar/vizualizare/data/sali.php?json`
- Facultăți: `https://orar.usv.ro/orar/vizualizare/data/facultati.php?json`
- Subgrupe: `https://orar.usv.ro/orar/vizualizare/data/subgrupe.php?json`
- Orar pentru o semi-grupă: `https://orar.usv.ro/orar/vizualizare/data/orarSPG.php?ID=1028&mod=grupa&json`

## Coduri de eroare

API-ul returnează următoarele coduri de eroare standard HTTP:

- `200 OK`: Cerere procesată cu succes
- `201 Created`: Resursă creată cu succes
- `400 Bad Request`: Cerere invalidă (parametri lipsă sau invalizi)
- `401 Unauthorized`: Autentificare necesară
- `403 Forbidden`: Acces interzis (utilizatorul nu are permisiunile necesare)
- `404 Not Found`: Resursa solicitată nu a fost găsită
- `409 Conflict`: Conflict (de exemplu, suprapunere de programări)
- `422 Unprocessable Entity`: Eroare de validare
- `500 Internal Server Error`: Eroare internă server

## Rate Limiting

Pentru a preveni abuzul API-ului, se aplică rate limiting:

- Maximum 100 cereri pe minut per utilizator
- Maximum 1000 cereri pe oră per utilizator

## Versioning

API-ul este versionat pentru a asigura compatibilitatea:

- Versiunea curentă: v1
- Endpoint-uri: `/api/v1/...`

## Exemple de utilizare

### Exemplu: Propunere dată examen de către șef grupă

```javascript
// 1. Autentificare
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    token: googleOAuthToken
  })
});
const auth = await response.json();
const token = auth.access_token;

// 2. Obținere discipline pentru grupa curentă
const subjectsResponse = await fetch('/api/subjects?groupId=456', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const subjects = await subjectsResponse.json();

// 3. Propunere dată examen
const proposeResponse = await fetch('/api/schedules/propose', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    subjectId: subjects[0].id,
    date: '2025-01-15'
  })
});
const proposal = await proposeResponse.json();
