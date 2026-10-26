import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))

from app.core.database import Base, get_db
from app.main import app
from app.core.security import get_password_hash
from app.models.models import User, ValidationRule
from app.rules.registry import RULE_REGISTRY

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Seed users
    admin = User(
        email="admin@veritrace.gov.in",
        hashed_password=get_password_hash("admin123"),
        full_name="Admin Officer",
        role="admin"
    )
    reviewer = User(
        email="officer@veritrace.gov.in",
        hashed_password=get_password_hash("officer123"),
        full_name="Reviewer Officer",
        role="reviewer"
    )
    db.add_all([admin, reviewer])
    # Seed rules
    for r in RULE_REGISTRY.values():
        db.add(ValidationRule(
            rule_code=r.rule_code,
            name=r.name,
            description=r.description,
            version=r.version,
            is_active=True,
            severity=r.severity
        ))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
