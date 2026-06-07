from sqlmodel import create_engine, Session, SQLModel
from app.db.config import settings

engine = create_engine(settings.DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session

get_db = get_session
