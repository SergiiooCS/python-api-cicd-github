import pytest
from app.main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_saludo_con_nombre(client):
    response = client.get("/saludo?nombre=Sergio")

    assert response.status_code == 200
    assert response.get_json() == {"mensaje": "Hola Sergio"}


def test_saludo_sin_nombre(client):
    response = client.get("/saludo")

    assert response.status_code == 400
    assert response.get_json() == {"error": "Falta el parámetro nombre"}
