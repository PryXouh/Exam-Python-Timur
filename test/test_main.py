import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app, get_db, Base

# La base en mémoire partagée pour tous les tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_and_read_station():
    res_post = client.post("/stations", json={"code": "A1", "name": "Stat1", "capacity": 10})
    assert res_post.status_code == 201
    data = res_post.json()
    
    res_get = client.get(f"/stations/{data['id']}")
    assert res_get.status_code == 200
    assert res_get.json()["name"] == "Stat1"

def test_filter_status_open():
    client.post("/stations", json={"code": "A1", "name": "S1", "capacity": 10, "status": "open"})
    client.post("/stations", json={"code": "A2", "name": "S2", "capacity": 10, "status": "closed"})
    
    res = client.get("/stations?status=open")
    assert res.status_code == 200
    assert len(res.json()) == 1

def test_patch_name():
    res_post = client.post("/stations", json={"code": "A1", "name": "S1", "capacity": 10})
    s_id = res_post.json()["id"]
    
    res_patch = client.patch(f"/stations/{s_id}", json={"name": "NewS1"})
    assert res_patch.status_code == 200
    
    res_get = client.get(f"/stations/{s_id}")
    assert res_get.json()["name"] == "NewS1"

def test_read_nonexistent_id():
    res = client.get("/stations/999")
    assert res.status_code == 404

@pytest.mark.parametrize("payload", [
    {"code": "A1", "name": "S1", "capacity": 0},
    {"code": "A1", "name": "S1", "capacity": 10, "status": "flying"}
])
def test_invalid_inputs(payload):
    res = client.post("/stations", json=payload)
    assert res.status_code == 422

def test_duplicate_code():
    client.post("/stations", json={"code": "A1", "name": "S1", "capacity": 10})
    res2 = client.post("/stations", json={"code": "A1", "name": "S2", "capacity": 15})
    assert res2.status_code == 409
