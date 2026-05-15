import copy

import pytest
from fastapi.testclient import TestClient

import src.app


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(src.app.activities)
    yield
    src.app.activities.clear()
    src.app.activities.update(copy.deepcopy(original))


def test_get_activities_returns_all_activities():
    # Arrange
    with TestClient(src.app.app) as client:
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert data["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


def test_post_signup_adds_participant():
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    with TestClient(src.app.app) as client:
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Signed up {email} for {activity}"}
        assert email in src.app.activities[activity]["participants"]


def test_post_signup_duplicate_returns_400():
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"

    with TestClient(src.app.app) as client:
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"


def test_delete_participant_removes_existing_participant():
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"

    with TestClient(src.app.app) as client:
        # Act
        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Removed {email} from {activity}"}
        assert email not in src.app.activities[activity]["participants"]


def test_delete_participant_invalid_removal_returns_404():
    # Arrange
    email = "unknown@mergington.edu"
    activity = "Chess Club"

    with TestClient(src.app.app) as client:
        # Act
        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"
