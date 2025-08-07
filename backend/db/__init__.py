from db.database import Base, engine
from models import story, job  # noqa: F401 - Imports are needed to register models


def main():
    print("Creating database tables for 'database.db'...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    main()

