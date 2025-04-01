"""
Definirea tag-urilor OpenAPI pentru documentația FastAPI
"""

tags_metadata = [
    {
        "name": "auth",
        "description": "Operații de autentificare și gestionare utilizatori"
    },
    {
        "name": "schedules",
        "description": "Operații de planificare examene"
    },
    {
        "name": "notifications",
        "description": "Operații de gestionare notificări"
    },
    {
        "name": "orar",
        "description": "Operații de integrare cu API-ul Orar USV"
    },
    {
        "name": "health",
        "description": "Endpoint-uri pentru verificarea stării serviciului"
    }
]
