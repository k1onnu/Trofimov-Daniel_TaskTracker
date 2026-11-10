def test_summary_empty(client):
    r = client.get("/analytics/summary")
    assert r.status_code == 200
    assert r.json() == {
        "total": 0,
        "by_status": {},
        "by_priority": {},
        "by_assignee": {},
    }


def test_summary_with_data(auth_client):
    auth_client.post("/tasks/", json={"title": "t1"})
    auth_client.post("/tasks/", json={"title": "t2", "status": "done"})
    
    r = auth_client.get("/analytics/summary")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 2
    assert body["by_status"]["new"] == 1
    assert body["by_status"]["done"] == 1


def test_chart_empty(client):
    r = client.get("/analytics/chart")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"


def test_chart_with_data(auth_client):
    auth_client.post("/tasks/", json={"title": "t1"})
    
    r = auth_client.get("/analytics/chart")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"