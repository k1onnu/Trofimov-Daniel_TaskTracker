def test_register_success(client):
    r = client.post(
        "/auth/register",
        json={"email": "a@example.com", "password": "secret123"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "a@example.com"
    assert "id" in body
    assert "hashed_password" not in body


def test_register_duplicate_email(client):
    payload = {"email": "a@example.com", "password": "secret123"}
    assert client.post("/auth/register", json=payload).status_code == 201
    r = client.post("/auth/register", json=payload)
    assert r.status_code == 409


def test_register_invalid_email(client):
    r = client.post(
        "/auth/register",
        json={"email": "not-an-email", "password": "secret123"},
    )
    assert r.status_code == 422


def test_login_success(client):
    client.post(
        "/auth/register",
        json={"email": "a@example.com", "password": "secret123"},
    )
    r = client.post(
        "/auth/login",
        data={"username": "a@example.com", "password": "secret123"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={"email": "a@example.com", "password": "secret123"},
    )
    r = client.post(
        "/auth/login",
        data={"username": "a@example.com", "password": "wrong"},
    )
    assert r.status_code == 401


def test_me_unauthorized(client):
    assert client.get("/auth/me").status_code == 401


def test_me_authorized(auth_client):
    r = auth_client.get("/auth/me")
    assert r.status_code == 200
    assert r.json()["email"] == "tester@example.com"


def test_login_nonexistent_email(client):
    r = client.post(
        "/auth/login",
        data={"username": "nobody@example.com", "password": "whatever"},
    )
    assert r.status_code == 401