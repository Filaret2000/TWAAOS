# Sistem de Planificare Examene FIESC

[![Build Status](https://img.shields.io/github/actions/workflow/status/fiesc/exam-scheduling/ci.yml?branch=main)](https://github.com/fiesc/exam-scheduling/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Requirements](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)

Aplicație web pentru planificarea examenelor și colocviilor în cadrul **Facultății de Inginerie Electrică și Știința Calculatoarelor** (USV).

## Descriere

Sistemul informatic pentru planificarea examenelor și colocviilor are ca scop automatizarea și optimizarea procesului de planificare a examenelor și colocviilor pentru toate programele de studii din cadrul facultății. Aplicația facilitează comunicarea între studenți (prin șefii de grupă), cadre didactice și secretariat pentru stabilirea datelor de examinare.

## Obiective

- Reducerea erorilor umane în planificare
- Asigurarea transparenței și accesului la informații pentru toți utilizatorii
- Îmbunătățirea comunicării și colaborării între studenți și profesori
- Automatizarea procesului de planificare conform regulamentelor USV

## Tehnologii
- **Backend**: Python 3 (Flask, FastAPI)
- **Frontend**: Vue.js
- **Baza de date**: PostgreSQL
- **Autentificare**: Google OAuth 2.0 ("Sign In With Google")
- **Deployment**: Docker

## Funcționalități cheie
✔ **Planificare colaborativă** a examenelor și colocviilor între șefii de grupă și cadrele didactice  
✔ **Notificări email** prin servicii externe (ex. SendGrid)  
✔ **Export PDF/Excel** pentru planificările de examene  
✔ **Interfețe adaptate pe roluri** (Secretariat, Șef Grupă, Cadru Didactic, Administrator)  
✔ **Integrare cu API-ul Orar USV** pentru preluarea datelor despre discipline, săli și cadre didactice  
✔ **Validare și aprobare** a datelor de examen propuse de șefii de grupă  
✔ **Documentație API interactivă** cu Swagger UI pentru testare manuală și debugging  

## Roluri utilizatori

### Secretariat (SEC)
- Încărcarea datelor despre discipline, cadre didactice și șefi de grupă
- Configurarea perioadelor pentru colocvii și examene
- Verificarea și modificarea planificărilor
- Exportul planificărilor în formate Excel și PDF

### Șef Grupă (SG)
- Propunerea datelor pentru examene și colocvii
- Vizualizarea statusului propunerilor (acceptate/respinse)
- Primirea notificărilor despre deciziile cadrelor didactice

### Cadru Didactic (CD)
- Validarea datelor propuse de șefii de grupă
- Stabilirea sălilor, asistenților și intervalelor orare pentru examene
- Vizualizarea planificării examenelor pentru disciplinele proprii

### Administrator (ADM)
- Gestionarea conturilor și a informațiilor despre facultăți
- Configurarea aplicației
- Actualizarea credențialelor de acces

## Quick Start

Clonare repository și setare aplicație în Docker:

```bash
git clone https://github.com/fiesc/exam-scheduling.git
cd exam-scheduling
docker-compose up -d
```

Accesează aplicația în browser la: http://localhost:8080

## Documentație

Pentru mai multe detalii, accesează:

- [Instalare și configurare](./INSTALLATION.md)
- [Ghid de dezvoltare](./DEVELOPMENT.md)
- [Documentație API](./API_DOCUMENTATION.md)
- [Ghid utilizare](./USER_GUIDE.md)
- [Arhitectură sistem](./ARCHITECTURE.md)