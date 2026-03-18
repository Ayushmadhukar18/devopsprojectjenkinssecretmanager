import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../main/app"))

from crypto_utils import encrypt_value, decrypt_value

def test_encrypt_decrypt_roundtrip():
    original = "super-secret-password-123"
    encrypted = encrypt_value(original)
    assert encrypted != original
    assert decrypt_value(encrypted) == original

def test_encrypt_produces_different_tokens():
    value = "same-value"
    t1 = encrypt_value(value)
    t2 = encrypt_value(value)
    # Fernet uses random IV so tokens differ even for same plaintext
    assert t1 != t2
    assert decrypt_value(t1) == decrypt_value(t2) == value

def test_encrypt_empty_string():
    result = encrypt_value("")
    assert decrypt_value(result) == ""

def test_encrypt_special_characters():
    value = "P@$$w0rd!#&*()"
    assert decrypt_value(encrypt_value(value)) == value


# Flask app tests
from app import app as flask_app
from database import db as _db

@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-key"
    })
    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_dashboard_loads(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"Dashboard" in r.data

def test_add_secret_get(client):
    r = client.get("/secrets/add")
    assert r.status_code == 200
    assert b"Add New Secret" in r.data

def test_add_secret_post(client):
    r = client.post("/secrets/add", data={
        "name": "TEST_KEY",
        "value": "mysecretvalue",
        "description": "A test secret",
        "expires_days": "30"
    }, follow_redirects=True)
    assert r.status_code == 200

def test_api_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.get_json()
    assert data["status"] == "ok"

def test_api_secrets_empty(client):
    r = client.get("/api/secrets")
    assert r.status_code == 200
    assert r.get_json() == []

def test_audit_log_loads(client):
    r = client.get("/audit")
    assert r.status_code == 200
    assert b"Audit Log" in r.data
