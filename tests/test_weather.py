from app.services import weather_service


def test_weather_endpoint_accepts_coordinates(client, monkeypatch):
    def fake_fetch_weather(latitude, longitude):
        return {
            "latitude": latitude,
            "longitude": longitude,
            "current": {"temperature_2m": 27.5},
        }

    monkeypatch.setattr(weather_service, "fetch_weather", fake_fetch_weather)
    monkeypatch.setattr(weather_service, "save_raw_json", lambda data, filename="weather.json": None)

    response = client.get("/weather/current", params={"latitude": -6.2088, "longitude": 106.8456})

    assert response.status_code == 200
    assert response.json()["latitude"] == -6.2088
    assert response.json()["longitude"] == 106.8456


def test_weather_endpoint_rejects_invalid_coordinates(client):
    response = client.get("/weather/current", params={"latitude": -91, "longitude": 106.8456})

    assert response.status_code == 422


def test_save_raw_json_uses_project_ai_dataset(tmp_path, monkeypatch):
    raw_dir = tmp_path / "ai" / "datasets" / "raw"
    monkeypatch.setattr(weather_service, "RAW_DATA_DIR", raw_dir)

    path = weather_service.save_raw_json({"current": {"temperature_2m": 27.5}}, "weather_test.json")

    assert path == raw_dir / "weather_test.json"
    assert path.exists()


def test_fetch_weather_and_save_returns_saved_payload(monkeypatch):
    saved = {}

    def fake_fetch_weather(latitude, longitude):
        return {"latitude": latitude, "longitude": longitude}

    def fake_save_raw_json(data, filename="weather.json"):
        saved["data"] = data
        saved["filename"] = filename

    monkeypatch.setattr(weather_service, "fetch_weather", fake_fetch_weather)
    monkeypatch.setattr(weather_service, "save_raw_json", fake_save_raw_json)

    data = weather_service.fetch_weather_and_save(-6.2088, 106.8456)

    assert data == {"latitude": -6.2088, "longitude": 106.8456}
    assert saved["data"] == data
    assert saved["filename"] == "weather.json"
