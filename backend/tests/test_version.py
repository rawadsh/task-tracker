TRACKED_PACKAGES = ("fastapi", "pydantic", "uvicorn", "python-dotenv")


def test_version_returns_app_and_package_versions(client):
    response = client.get("/version")

    assert response.status_code == 200
    body = response.json()

    assert "app_version_typo" in body
    assert "packages" in body

    assert set(body["packages"].keys()) == set(TRACKED_PACKAGES)
    for pkg_version in body["packages"].values():
        assert isinstance(pkg_version, str)
        assert pkg_version
