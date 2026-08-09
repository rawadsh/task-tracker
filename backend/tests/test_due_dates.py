from datetime import date, timedelta


def test_create_task_with_valid_due_date_returns_201_and_due_date(client):
    r = client.post(
        "/tasks",
        json={"title": "Task with due date", "due_date": "2026-12-31"},
    )

    assert r.status_code == 201
    assert r.json()["due_date"] == "2026-12-31"


def test_create_task_without_due_date_defaults_to_null(client):
    r = client.post("/tasks", json={"title": "No due date"})

    assert r.status_code == 201
    assert r.json()["due_date"] is None


def test_create_task_with_invalid_due_date_returns_422(client):
    r = client.post(
        "/tasks",
        json={"title": "Bad date", "due_date": "not-a-date"},
    )

    assert r.status_code == 422


def test_patch_updates_due_date(client, created_task):
    task_id = created_task["id"]

    r = client.patch(f"/tasks/{task_id}", json={"due_date": "2026-01-15"})

    assert r.status_code == 200
    assert r.json()["due_date"] == "2026-01-15"


def test_patch_due_date_null_clears_it(client):
    create_r = client.post(
        "/tasks",
        json={"title": "Has due date", "due_date": "2026-01-15"},
    )
    task_id = create_r.json()["id"]

    r = client.patch(f"/tasks/{task_id}", json={"due_date": None})

    assert r.status_code == 200
    assert r.json()["due_date"] is None


def test_patch_unrelated_field_preserves_due_date(client):
    create_r = client.post(
        "/tasks",
        json={"title": "Keep due date", "due_date": "2026-06-01"},
    )
    task_id = create_r.json()["id"]

    r = client.patch(f"/tasks/{task_id}", json={"title": "Renamed"})

    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "Renamed"
    assert body["due_date"] == "2026-06-01"


def test_todo_task_with_past_due_date_is_overdue(client):
    past = (date.today() - timedelta(days=1)).isoformat()

    r = client.post(
        "/tasks",
        json={"title": "Late todo", "status": "ToDo", "due_date": past},
    )

    assert r.json()["overdue"] is True


def test_inprogress_task_with_past_due_date_is_overdue(client):
    past = (date.today() - timedelta(days=1)).isoformat()

    r = client.post(
        "/tasks",
        json={"title": "Late in progress", "status": "InProgress", "due_date": past},
    )

    assert r.json()["overdue"] is True


def test_done_task_with_past_due_date_is_not_overdue(client):
    past = (date.today() - timedelta(days=1)).isoformat()

    r = client.post(
        "/tasks",
        json={"title": "Late but done", "status": "Done", "due_date": past},
    )

    assert r.json()["overdue"] is False


def test_task_without_due_date_is_not_overdue(client, created_task):
    assert created_task["overdue"] is False


def test_overdue_filter_returns_only_overdue_tasks(client):
    past = (date.today() - timedelta(days=1)).isoformat()
    future = (date.today() + timedelta(days=5)).isoformat()

    client.post("/tasks", json={"title": "Overdue", "status": "ToDo", "due_date": past})
    client.post("/tasks", json={"title": "Not due yet", "status": "ToDo", "due_date": future})
    client.post("/tasks", json={"title": "No due date", "status": "ToDo"})

    r = client.get("/tasks", params={"overdue": "true"})

    assert r.status_code == 200
    tasks = r.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Overdue"
    assert tasks[0]["overdue"] is True


def test_overdue_filter_with_no_matches_returns_200_empty_list(client, created_task):
    r = client.get("/tasks", params={"overdue": "true"})

    assert r.status_code == 200
    assert r.json() == []


def test_status_and_priority_filters_still_work_alongside_due_dates(client):
    client.post(
        "/tasks",
        json={"title": "A", "status": "ToDo", "priority": "High", "due_date": "2026-01-01"},
    )
    client.post("/tasks", json={"title": "B", "status": "Done", "priority": "Low"})

    r_status = client.get("/tasks", params={"status": "Done"})
    assert r_status.status_code == 200
    assert len(r_status.json()) == 1
    assert r_status.json()[0]["title"] == "B"

    r_priority = client.get("/tasks", params={"priority": "High"})
    assert r_priority.status_code == 200
    assert len(r_priority.json()) == 1
    assert r_priority.json()[0]["title"] == "A"
