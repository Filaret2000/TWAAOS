from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from flask import current_app, g
import os

def get_db_session():
    """
    Funcție pentru obținerea unei sesiuni de bază de date
    
    Utilizare:
    db_session = get_db_session()
    users = db_session.query(User).all()
    """
    if 'db_session' not in g:
        # Obținem URL-ul bazei de date din configurație
        database_url = current_app.config['DATABASE_URL']
        
        # Creăm engine-ul SQLAlchemy
        engine = create_engine(database_url)
        
        # Creăm sesiunea
        session_factory = sessionmaker(bind=engine)
        g.db_session = scoped_session(session_factory)
    
    return g.db_session

def close_db_session(e=None):
    """
    Funcție pentru închiderea sesiunii de bază de date
    
    Această funcție trebuie înregistrată ca teardown_appcontext
    """
    db_session = g.pop('db_session', None)
    
    if db_session is not None:
        db_session.remove()

def init_db(app):
    """
    Funcție pentru inițializarea bazei de date
    
    Această funcție trebuie apelată la inițializarea aplicației
    """
    # Înregistrăm funcția de închidere a sesiunii
    app.teardown_appcontext(close_db_session)
