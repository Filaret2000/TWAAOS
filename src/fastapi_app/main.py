from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
import os

from fastapi_app.openapi_tags import tags_metadata

# Configurare aplicație FastAPI
app = FastAPI(
    title="Sistem Planificare Examene API",
    description="""API pentru sistemul de planificare examene FIESC
    
    ## Funcționalități
    
    * **Autentificare** - Autentificare cu Google OAuth și gestionare utilizatori
    * **Planificare examene** - Creare, actualizare, ștergere și propunere planificări
    * **Notificări** - Gestionare notificări și setări de notificare
    * **Integrare Orar USV** - Sincronizare date cu API-ul Orar USV
    
    ## Autentificare
    
    Toate endpoint-urile, cu excepția celor de autentificare și verificare sănătate, necesită autentificare.
    Autentificarea se face prin token JWT, care se obține prin endpoint-ul `/api/auth/login`.
    
    ## Documentație
    
    * [Swagger UI](/api/docs)
    * [ReDoc](/api/redoc)
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    openapi_tags=tags_metadata
)

# Configurare CORS
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import și înregistrare router API
from fastapi_app.api import api_router

app.include_router(api_router, prefix="/api")

# Endpoint de sănătate
@app.get("/api/health", tags=["health"], summary="Verificare stare serviciu", description="Endpoint pentru verificarea stării serviciului FastAPI")
async def health_check():
    return {"status": "ok", "service": "fastapi"}

# Personalizare Swagger UI
@app.get("/api/custom-docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/api/openapi.json",
        title="API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,  # Ascunde modelele din partea de jos
            "docExpansion": "list",  # Expandează toate operațiunile
            "filter": True,  # Activează căutarea
            "syntaxHighlight.theme": "monokai"  # Tema pentru evidențierea sintaxei
        }
    )

# Personalizare OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Sistem Planificare Examene API",
        version="1.0.0",
        description="""API pentru sistemul de planificare examene FIESC
        
        ## Funcționalități
        
        * **Autentificare** - Autentificare cu Google OAuth și gestionare utilizatori
        * **Planificare examene** - Creare, actualizare, ștergere și propunere planificări
        * **Notificări** - Gestionare notificări și setări de notificare
        * **Integrare Orar USV** - Sincronizare date cu API-ul Orar USV
        
        ## Autentificare
        
        Toate endpoint-urile, cu excepția celor de autentificare și verificare sănătate, necesită autentificare.
        Autentificarea se face prin token JWT, care se obține prin endpoint-ul `/api/auth/login`.
        """,
        routes=app.routes,
    )
    
    # Adăugare componente de securitate
    openapi_schema["components"] = {
        "securitySchemes": {
            "Bearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Introduceți token-ul JWT în formatul: Bearer {token}"
            }
        }
    }
    
    # Adăugare securitate globală
    openapi_schema["security"] = [{"Bearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Gestiune erori
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
