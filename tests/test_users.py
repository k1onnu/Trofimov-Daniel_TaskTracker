def test_create_user_success(client):
    r = client.post(
        "/users/",
        json={"email": "u@example.com", "password": "secret123"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "u@example.com"
    assert "id" in body
    assert "hashed_password" not in body


def test_create_user_duplicate_email(client):
    payload = {"email": "u@example.com", "password": "secret123"}
    assert client.post("/users/", json=payload).status_code == 201
    r = client.post("/users/", json=payload)
    assert r.status_code == 409


def test_get_user_success(client):
    created = client.post(
        "/users/", json={"email": "u@example.com", "password": "secret123"}
    ).json()
    r = client.get(f"/users/{created['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == created["id"]
    assert r.json()["email"] == "u@example.com"


def test_get_user_not_found(client):
    assert client.get("/users/999").status_code == 404