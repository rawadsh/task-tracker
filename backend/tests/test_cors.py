def test_options_preflight_returns_cors_headers(client):
    response = client.options(
        "/tasks",
        headers={
            "Origin": "http://localhost:5500",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5500"
    assert "GET" in response.headers["access-control-allow-methods"]
