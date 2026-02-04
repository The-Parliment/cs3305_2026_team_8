from sqlalchemy import create_engine

DATABASE_URL = "sqlite:////app/common/app.db"

engine = create_engine(
    DATABASE_URL,
    echo=True,          # logs SQL (turn off in prod)
    future=True
)