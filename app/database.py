from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL

try:
    engine = create_engine(DATABASE_URL, echo=False)

    with engine.connect() as connection:
        print("Connection established successfully!")

except Exception as e:
    print(f"Error connecting to the database: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
