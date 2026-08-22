def test_create_task_with_tags_trims_and_returns_them(client):
    r = client.post(
        "/tasks",
        json={"title": "Tagged task", "tags": [" bug ", "urgent"]},
    )

    assert r.status_code == 201
    assert r.json()["tags"] == ["bug", "urgent"]


def test_create_task_without_tags_defaults_to_empty_list(client):
    r = client.post("/tasks", json={"title": "No tags"})

    assert r.status_code == 201
    assert r.json()["tags"] == []


def test_create_task_with_blank_tag_returns_422(client):
    r = client.post(
        "/tasks",
        json={"title": "Blank tag", "tags": ["bug", "   "]},
    )

    assert r.status_code == 422


def test_create_task_with_max_tag_count_succeeds(client):
    tags = [f"tag{i}" for i in range(10)]

    r = client.post("/tasks", json={"title": "Max tags", "tags": tags})

    assert r.status_code == 201
    assert r.json()["tags"] == tags


def test_create_task_with_too_many_tags_returns_422(client):
    tags = [f"tag{i}" for i in range(11)]

    r = client.post("/tasks", json={"title": "Too many tags", "tags": tags})

    assert r.status_code == 422


def test_create_task_with_max_length_tag_succeeds(client):
    tag = "a" * 30

    r = client.post("/tasks", json={"title": "Max length tag", "tags": [tag]})

    assert r.status_code == 201
    assert r.json()["tags"] == [tag]


def test_create_task_with_too_long_tag_returns_422(client):
    tag = "a" * 31

    r = client.post("/tasks", json={"title": "Too long tag", "tags": [tag]})

    assert r.status_code == 422


def test_patch_replaces_full_tags_list(client):
    create_r = client.post(
        "/tasks",
        json={"title": "Replace tags", "tags": ["bug", "urgent"]},
    )
    task_id = create_r.json()["id"]

    r = client.patch(f"/tasks/{task_id}", json={"tags": ["feature"]})

    assert r.status_code == 200
    assert r.json()["tags"] == ["feature"]


def test_patch_tags_empty_list_clears_tags(client):
    create_r = client.post(
        "/tasks",
        json={"title": "Clear tags", "tags": ["bug", "urgent"]},
    )
    task_id = create_r.json()["id"]

    r = client.patch(f"/tasks/{task_id}", json={"tags": []})

    assert r.status_code == 200
    assert r.json()["tags"] == []


def test_patch_omitted_tags_preserves_existing_list(client):
    create_r = client.post(
        "/tasks",
        json={"title": "Preserve tags", "tags": ["bug", "urgent"]},
    )
    task_id = create_r.json()["id"]

    r = client.patch(f"/tasks/{task_id}", json={"title": "Renamed"})

    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "Renamed"
    assert body["tags"] == ["bug", "urgent"]


def test_patch_with_invalid_tag_returns_422_and_leaves_task_unmodified(client):
    create_r = client.post(
        "/tasks",
        json={"title": "Invalid patch tags", "tags": ["bug"]},
    )
    task_id = create_r.json()["id"]

    r = client.patch(f"/tasks/{task_id}", json={"tags": ["bug", ""]})

    assert r.status_code == 422

    get_r = client.get(f"/tasks/{task_id}")
    assert get_r.json()["tags"] == ["bug"]


def test_tag_filter_returns_only_matching_tasks(client):
    client.post("/tasks", json={"title": "Bug task", "tags": ["bug"]})
    client.post("/tasks", json={"title": "Feature task", "tags": ["feature"]})
    client.post("/tasks", json={"title": "No tags task"})

    r = client.get("/tasks", params={"tag": "bug"})

    assert r.status_code == 200
    tasks = r.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Bug task"


def test_tag_filter_is_case_sensitive(client):
    client.post("/tasks", json={"title": "Lowercase bug", "tags": ["bug"]})

    r = client.get("/tasks", params={"tag": "Bug"})

    assert r.status_code == 200
    assert r.json() == []


def test_tag_filter_with_no_matches_returns_200_empty_list(client):
    r = client.get("/tasks", params={"tag": "nonexistent"})

    assert r.status_code == 200
    assert r.json() == []


def test_tag_filter_does_not_affect_status_and_priority_filters(client):
    client.post(
        "/tasks",
        json={"title": "A", "status": "ToDo", "priority": "High", "tags": ["bug"]},
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