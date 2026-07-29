def test_create_task_valid_returns_201_with_full_body(client):
    payload = {
        "title": "Test task",
        "description": "Test description",
        "status": "ToDo",
        "priority": "High",
        "assignee": "Alice",
    }

    r = client.post("/tasks", json=payload)

    assert r.status_code == 201
    body = r.json()
    assert body["title"] == "Test task"
    assert body["description"] == "Test description"
    assert body["status"] == "ToDo"
    assert body["priority"] == "High"
    assert body["assignee"] == "Alice"
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_create_task_missing_title_returns_422(client):
    r = client.post("/tasks", json={"description": "Missing title"})

    assert r.status_code == 422


def test_create_task_blank_title_returns_422(client):
    r = client.post("/tasks", json={"title": "   "})

    assert r.status_code == 422


def test_create_task_invalid_priority_returns_422(client):
    r = client.post(
        "/tasks",
        json={"title": "Test task", "priority": "Invalid"},
    )

    assert r.status_code == 422


def test_create_task_unknown_field_returns_422(client):
    r = client.post(
        "/tasks",
        json={"title": "Test task", "unknown_field": "value"},
    )

    assert r.status_code == 422


def test_list_tasks_empty_returns_200_and_empty_list(client):
    r = client.get("/tasks")

    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(client):
    client.post("/tasks", json={"title": "ToDo task", "status": "ToDo"})

    r = client.get("/tasks", params={"status": "Done"})

    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client):
    client.post(
        "/tasks",
        json={"title": "High priority", "priority": "High"},
    )
    client.post(
        "/tasks",
        json={"title": "Low priority", "priority": "Low"},
    )

    r = client.get("/tasks", params={"priority": "High"})

    assert r.status_code == 200
    tasks = r.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "High priority"
    assert tasks[0]["priority"] == "High"


def test_get_task_by_id_returns_task(client, created_task):
    task_id = created_task["id"]

    r = client.get(f"/tasks/{task_id}")

    assert r.status_code == 200
    assert r.json()["id"] == task_id
    assert r.json()["title"] == "fixture task"


def test_get_task_by_id_not_found_returns_404_with_detail(client):
    task_id = "does-not-exist"

    r = client.get(f"/tasks/{task_id}")

    assert r.status_code == 404
    assert r.json()["detail"] == f"Task with id {task_id} not found"


def test_patch_partial_update_keeps_other_fields(client, created_task):
    task_id = created_task["id"]

    r = client.patch(
        f"/tasks/{task_id}",
        json={"title": "Updated title"},
    )

    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "Updated title"
    assert body["description"] == created_task["description"]
    assert body["status"] == created_task["status"]
    assert body["priority"] == created_task["priority"]
    assert body["assignee"] == created_task["assignee"]


def test_patch_empty_json_body_returns_existing_task_unchanged(client):
    create_r = client.post(
        "/tasks",
        json={
            "title": "Task to leave unchanged",
            "description": "Original description",
            "status": "ToDo",
            "priority": "High",
            "assignee": "Alice",
        },
    )

    assert create_r.status_code == 201
    created_task = create_r.json()

    r = client.patch(f"/tasks/{created_task['id']}", json={})

    assert r.status_code == 200
    body = r.json()
    assert body["id"] == created_task["id"]
    assert body["title"] == created_task["title"]
    assert body["description"] == created_task["description"]
    assert body["status"] == created_task["status"]
    assert body["priority"] == created_task["priority"]
    assert body["assignee"] == created_task["assignee"]


def test_patch_not_found_returns_404(client):
    task_id = "does-not-exist"

    r = client.patch(
        f"/tasks/{task_id}",
        json={"title": "Updated title"},
    )

    assert r.status_code == 404
    assert r.json()["detail"] == f"Task with id {task_id} not found"


def test_patch_valid_transition_todo_to_inprogress_returns_200(
    client,
    created_task,
):
    task_id = created_task["id"]

    r = client.patch(
        f"/tasks/{task_id}",
        json={"status": "InProgress"},
    )

    assert r.status_code == 200
    assert r.json()["status"] == "InProgress"


def test_patch_invalid_transition_todo_to_done_returns_422(
    client,
    created_task,
):
    task_id = created_task["id"]

    r = client.patch(
        f"/tasks/{task_id}",
        json={"status": "Done"},
    )

    assert r.status_code == 422


def test_patch_same_status_returns_422(client, created_task):
    task_id = created_task["id"]

    r = client.patch(
        f"/tasks/{task_id}",
        json={"status": "ToDo"},
    )

    assert r.status_code == 422


def test_delete_existing_returns_204_no_body(client, created_task):
    task_id = created_task["id"]

    r = client.delete(f"/tasks/{task_id}")

    assert r.status_code == 204
    assert r.content == b""


def test_delete_missing_returns_404(client):
    task_id = "does-not-exist"

    r = client.delete(f"/tasks/{task_id}")

    assert r.status_code == 404
    assert r.json()["detail"] == f"Task with id {task_id} not found"