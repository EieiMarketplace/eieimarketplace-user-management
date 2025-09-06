import os
os.environ["POSTGRES_USER"] = ""
os.environ["POSTGRES_PASSWORD"] = ""
os.environ["POSTGRES_HOST"] = "sqlite"   #trigger sqlite mode
os.environ["POSTGRES_DB"] = "./test.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models import Role

# Use SQLite for test instead of Postgres
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# override dependency of get_db
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # seed default roles
    db = TestingSessionLocal()
    if not db.query(Role).all():
        db.add_all([Role(name="vendor"), Role(name="organizer")])
        db.commit()
    db.close()

    yield
    Base.metadata.drop_all(bind=engine)
    

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture
def test_client():
    return client
