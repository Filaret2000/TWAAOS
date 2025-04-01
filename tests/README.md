# Teste pentru Sistemul de Planificare Examene

Acest director conține testele unitare și de integrare pentru sistemul de planificare a examenelor.

## Structura Testelor

- `conftest.py` - Configurare pentru pytest cu fixture-uri pentru teste
- `test_auth_service.py` - Teste pentru serviciul de autentificare
- `test_schedule_service.py` - Teste pentru serviciul de planificare
- `test_notification_service.py` - Teste pentru serviciul de notificări

## Rularea Testelor

### Instalarea Dependențelor

Înainte de a rula testele, asigurați-vă că aveți instalate toate dependențele necesare:

```bash
pip install -r requirements-dev.txt
```

### Rularea Tuturor Testelor

Pentru a rula toate testele, executați următoarea comandă din directorul rădăcină al proiectului:

```bash
pytest tests/
```

### Rularea Testelor Specifice

Pentru a rula teste specifice, puteți specifica fișierul de test:

```bash
pytest tests/test_auth_service.py
```

Sau puteți rula un test specific:

```bash
pytest tests/test_auth_service.py::TestAuthService::test_create_user
```

### Rularea Testelor cu Raport de Acoperire

Pentru a genera un raport de acoperire a codului, executați:

```bash
pytest --cov=src tests/
```

Pentru un raport HTML detaliat:

```bash
pytest --cov=src --cov-report=html tests/
```

Raportul HTML va fi generat în directorul `htmlcov/`.

## Fixture-uri Disponibile

Următoarele fixture-uri sunt disponibile pentru teste:

- `db_session` - O sesiune de bază de date SQLite în memorie
- `test_user` - Un utilizator de test cu rolul SEC
- `test_admin` - Un administrator de test
- `test_teacher` - Un cadru didactic de test
- `test_student` - Un student de test
- `test_group` - O grupă de test
- `test_room` - O sală de test
- `test_subject` - O disciplină de test
- `test_schedule` - O planificare de test
- `test_notification` - O notificare de test
- `test_exam_period` - O perioadă de examinare de test

## Adăugarea de Noi Teste

Pentru a adăuga noi teste, creați un fișier nou în directorul `tests/` cu numele `test_*.py`. Asigurați-vă că fișierul începe cu `test_` pentru a fi descoperit automat de pytest.

Utilizați fixture-urile existente pentru a configura mediul de test și a evita duplicarea codului.

## Exemple

### Exemplu de Test pentru un Serviciu

```python
def test_my_service(db_session, test_user):
    # Inițializăm serviciul
    my_service = MyService(db_session=db_session)
    
    # Apelăm metoda pe care dorim să o testăm
    result = my_service.my_method(test_user.id)
    
    # Verificăm rezultatul
    assert result is not None
    assert result.some_property == expected_value
```

### Exemplu de Test pentru un API

```python
def test_my_api_endpoint(client, test_user, test_token):
    # Facem un request către endpoint
    response = client.get(
        "/api/my-endpoint",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    # Verificăm răspunsul
    assert response.status_code == 200
    data = response.json()
    assert data["some_property"] == expected_value
```
