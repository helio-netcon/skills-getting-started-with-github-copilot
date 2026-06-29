from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def test_root_redirects_to_static_index():
    # Arrange
    # Act
    response = client.get("/")
    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_list():
    # Arrange / Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_for_activity_adds_participant():
    # Arrange
    activity = "Chess Club"
    email = "new.student@mergington.edu"
    original_participants = list(activities[activity]["participants"])
    try:
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Signed up {email} for {activity}"}
        assert email in activities[activity]["participants"]
    finally:
        activities[activity]["participants"] = original_participants


def test_signup_duplicate_participant_returns_400():
    # Arrange
    activity = "Chess Club"
    email = activities[activity]["participants"][0]

    # Act
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_remove_participant_removes_existing_student():
    # Arrange
    activity = "Chess Club"
    email = "temporary.student@mergington.edu"
    original_participants = list(activities[activity]["participants"])
    activities[activity]["participants"].append(email)
    try:
        # Act
        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )
        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Removed {email} from {activity}"}
        assert email not in activities[activity]["participants"]
    finally:
        activities[activity]["participants"] = original_participants


def test_remove_missing_participant_returns_404():
    # Arrange
    activity = "Chess Club"
    email = "missing.student@mergington.edu"
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Act
    response = client.delete(
        f"/activities/{activity}/participants",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_signup_nonexistent_activity_returns_404():
    # Arrange
    activity = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
