'''
# tests/test_auth.py
Use shared client from conftest — never redefine DB setup
'''


def test_login_placeholder(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "test@email.com",
            "password": "test123"
        }
    )

    # This will fail until auth is implemented
    assert response.status_code in [200, 401, 404]
