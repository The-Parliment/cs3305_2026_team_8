from sqlalchemy import create_engine, event

DATABASE_URL = "sqlite:////app/common/app.db"

engine = create_engine(
    DATABASE_URL,
    echo=True,          # logs SQL (turn off in prod)
    future=True
)

# Found out sqlite does not enable FK protection unless we add this.
@event.listens_for(engine, "connect")
def set_sqlite_fk(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
