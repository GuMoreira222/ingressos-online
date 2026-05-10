import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db.database import Base, get_db
from core.security import get_password_hash
from models.user import User, RoleEnum
from main import app

# In-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]

@pytest.fixture(scope="function")
def admin_user(db):
    user = User(
        email="admin@test.com",
        password_hash=get_password_hash("adminpass"),
        role=RoleEnum.ADMIN
    )
    db.add(user)
    db.commit()
    return user

@pytest.fixture(scope="function")
def normal_user(db):
    user = User(
        email="user@test.com",
        password_hash=get_password_hash("userpass"),
        role=RoleEnum.USER
    )
    db.add(user)
    db.commit()
    return user

@pytest.fixture(scope="function")
def admin_token(client, admin_user):
    response = client.post(
        "/auth/login",
        data={"username": "admin@test.com", "password": "adminpass"}
    )
    return response.json()["access_token"]
