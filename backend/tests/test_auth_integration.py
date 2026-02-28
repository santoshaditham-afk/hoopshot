"""Integration tests for the full auth flow."""


def test_register_creates_user(client):
    resp = client.post("/auth/register", json={"username": "alice", "password": "pass123"})
    assert resp.status_code == 201
    assert resp.json()["username"] == "alice"


def test_register_duplicate_username_fails(client):
    client.post("/auth/register", json={"username": "alice", "password": "pass123"})
    resp = client.post("/auth/register", json={"username": "alice", "password": "other"})
    assert resp.status_code == 400


def test_login_returns_token(client):
    client.post("/auth/register", json={"username": "alice", "password": "pass123"})
    resp = client.post("/auth/login", json={"username": "alice", "password": "pass123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password_fails(client):
    client.post("/auth/register", json={"username": "alice", "password": "pass123"})
    resp = client.post("/auth/login", json={"username": "alice", "password": "wrong"})
    assert resp.status_code == 401


def test_me_returns_current_user(auth_client):
    client, token = auth_client
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "testuser"


def test_me_without_token_fails(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 403
