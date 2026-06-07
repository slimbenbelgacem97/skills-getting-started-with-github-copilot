import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module
from src.app import app

client = TestClient(app)
original_activities = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_activities))
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_activities))


def test_root_redirects_to_index():
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_list():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "Chess Club" in response.json()


def test_signup_for_activity_success():
    # Arrange
    activity_name = "Chess Club"
    email = "new_student@mergington.edu"
    signup_url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(signup_url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_for_activity_duplicate_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    signup_url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(signup_url, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_for_unknown_activity_returns_404():
    # Arrange
    activity_name = "Space Club"
    email = "student@mergington.edu"
    signup_url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(signup_url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_success():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    unregister_url = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(unregister_url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "missing_student@mergington.edu"
    unregister_url = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(unregister_url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
