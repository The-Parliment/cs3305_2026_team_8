from .session import SessionLocal

def get_db_generator():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

        #THERES NO SCHEMA

def get_db():
    db = next(get_db_generator())
    return db