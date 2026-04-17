# tests/test_main.py


def test_root(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "message" in response.json()
