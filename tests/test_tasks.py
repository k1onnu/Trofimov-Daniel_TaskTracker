def test_create_task_unauthorized(client):
    r = client.post("/tasks/", json={"title": "x"})
    assert r.status_code == 401


def test_create_task_success(auth_client):
    r = auth_client.post("/tasks/", json={"title": "First task"})
    assert r.status_code == 201
    body = r.json()
    assert body["title"] == "First task"
    assert body["status"] == "new"
    assert body["priority"] == "medium"
    assert body["id"] == 1


def test_create_task_empty_title(auth_client):
    r = auth_client.post("/tasks/", json={"title": ""})
    assert r.status_code == 422


def test_create_task_nonexistent_assignee(auth_client):
    r = auth_client.post("/tasks/", json={"title": "x", "assignee_id": 999})
    assert r.status_code == 404


def test_list_tasks_empty(client):
    r = client.get("/tasks/")
    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_with_filter(auth_client):
    auth_client.post("/tasks/", json={"title": "t1"})
    auth_client.post("/tasks/", json={"title": "t2", "status": "done"})
    auth_client.post("/tasks/", json={"title": "t3", "priority": "high"})

    all_tasks = auth_client.get("/tasks/").json()
    assert len(all_tasks) == 3

    done_tasks = auth_client.get("/tasks/?status=done").json()
    assert len(done_tasks) == 1
    assert done_tasks[0]["title"] == "t2"

    high_tasks = auth_client.get("/tasks/?priority=high").json()
    assert len(high_tasks) == 1
    assert high_tasks[0]["title"] == "t3"

    both = auth_client.get("/tasks/?status=new&priority=high").json()
    assert len(both) == 1
    assert both[0]["title"] == "t3"


def test_get_task_ok(auth_client):
    created = auth_client.post("/tasks/", json={"title": "t"}).json()
    r = auth_client.get(f"/tasks/{created['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == created["id"]


def test_get_task_not_found(client):
    assert client.get("/tasks/999").status_code == 404


def test_update_task(auth_client):
    created = auth_client.post("/tasks/", json={"title": "t"}).json()
    r = auth_client.patch(
        f"/tasks/{created['id']}", json={"status": "done"}
    )
    assert r.status_code == 200
    assert r.json()["status"] == "done"


def test_update_task_unauthorized(client):
    assert client.patch("/tasks/1", json={"status": "done"}).status_code == 401


def test_delete_task(auth_client):
    created = auth_client.post("/tasks/", json={"title": "t"}).json()
    r = auth_client.delete(f"/tasks/{created['id']}")
    assert r.status_code == 204
    assert auth_client.get(f"/tasks/{created['id']}").status_code == 404


def test_patch_task_not_found(auth_client):
    assert auth_client.patch("/tasks/999", json={"status": "done"}).status_code == 404


def test_delete_task_unauthorized(client):
    assert client.delete("/tasks/1").status_code == 401


def test_delete_task_not_found(auth_client):
    assert auth_client.delete("/tasks/999").status_code == 404


def test_patch_task_nonexistent_assignee(auth_client):
    created = auth_client.post("/tasks/", json={"title": "t"}).json()
    r = auth_client.patch(
        f"/tasks/{created['id']}", json={"assignee_id": 999}
    )
    assert r.status_code == 404


def test_create_task_title_too_long(auth_client):
    r = auth_client.post("/tasks/", json={"title": "x" * 300})
    assert r.status_code == 422