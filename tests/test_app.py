import pytest

from app import calculate_bmi, calculate_calories, create_app, membership_state


@pytest.fixture
def client(tmp_path):
    app = create_app(str(tmp_path / "test.db"))
    app.config["TESTING"] = True
    return app.test_client()


def make_client(client, **overrides):
    payload = {"name": "Arun", "age": 28, "height": 175, "weight": 80,
               "program": "MG"}
    payload.update(overrides)
    return client.post("/clients", json=payload)


# ---- business logic ----
@pytest.mark.parametrize("code,weight,expected", [("FL", 80, 1760), ("MG", 80, 2800),
                                                  ("BG", 70, 1820)])
def test_calories(code, weight, expected):
    assert calculate_calories(weight, code) == expected


def test_calories_invalid():
    with pytest.raises(ValueError):
        calculate_calories(80, "XX")
    with pytest.raises(ValueError):
        calculate_calories(0, "FL")


@pytest.mark.parametrize("w,h,cat", [(50, 175, "Underweight"), (70, 175, "Normal"),
                                     (85, 175, "Overweight"), (110, 175, "Obese")])
def test_bmi_categories(w, h, cat):
    assert calculate_bmi(w, h)[1] == cat


def test_bmi_invalid():
    with pytest.raises(ValueError):
        calculate_bmi(70, 0)


def test_membership_state():
    assert membership_state("Active", None) == "Active"
    assert membership_state("Active", "2999-01-01") == "Active"
    assert membership_state("Active", "2000-01-01") == "Expired"
    assert membership_state("Cancelled", None) == "Inactive"


# ---- endpoints ----
def test_health_and_index(client):
    assert client.get("/health").get_json() == {"status": "ok"}
    assert client.get("/").status_code == 200


def test_programs(client):
    data = client.get("/programs").get_json()
    assert set(data) == {"FL", "MG", "BG"}
    assert client.get("/programs/fl").get_json()["calorie_factor"] == 22
    assert client.get("/programs/ZZ").status_code == 404


def test_add_and_get_client(client):
    resp = make_client(client)
    assert resp.status_code == 201
    assert resp.get_json()["calories"] == 2800
    assert client.get("/clients/Arun").get_json()["program"] == "MG"
    assert client.get("/clients").get_json() == [{"name": "Arun", "program": "MG"}]


def test_add_client_validation(client):
    assert client.post("/clients", json={}).status_code == 400
    assert make_client(client, program="XX").status_code == 400
    make_client(client)
    assert make_client(client).status_code == 409


def test_unknown_client_returns_404(client):
    for path in ["/clients/Nobody", "/clients/Nobody/bmi", "/clients/Nobody/membership",
                 "/clients/Nobody/progress", "/clients/Nobody/workouts"]:
        assert client.get(path).status_code == 404


def test_client_bmi_and_membership(client):
    make_client(client)
    assert client.get("/clients/Arun/bmi").get_json() == {"bmi": 26.1,
                                                          "category": "Overweight"}
    assert client.get("/clients/Arun/membership").get_json() == {"membership": "Active"}
    make_client(client, name="Old", membership_end="2000-01-01")
    assert client.get("/clients/Old/membership").get_json()["membership"] == "Expired"


def test_bmi_requires_measurements(client):
    client.post("/clients", json={"name": "NoData"})
    assert client.get("/clients/NoData/bmi").status_code == 400


def test_progress(client):
    make_client(client)
    assert client.post("/clients/Arun/progress", json={"adherence": 85,
                                                       "week": "W1"}).status_code == 201
    assert client.post("/clients/Arun/progress", json={"adherence": 150}).status_code == 400
    assert client.get("/clients/Arun/progress").get_json() == [{"week": "W1",
                                                                "adherence": 85}]


def test_workouts(client):
    make_client(client)
    assert client.post("/clients/Arun/workouts", json={}).status_code == 400
    resp = client.post("/clients/Arun/workouts",
                       json={"workout_type": "Strength", "duration_min": 60})
    assert resp.status_code == 201
    logged = client.get("/clients/Arun/workouts").get_json()
    assert logged[0]["workout_type"] == "Strength"
