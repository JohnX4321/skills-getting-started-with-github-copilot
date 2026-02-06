"""
Test suite for Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Save original state
    original_activities = {
        "Tennis Club": {
            "description": "Learn tennis skills and participate in friendly matches",
            "schedule": "Wednesdays and Saturdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["alex@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for intramural and regional tournaments",
            "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "maya@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and develop acting skills",
            "schedule": "Tuesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu"]
        },
        "Digital Art Workshop": {
            "description": "Create digital artwork using design software and tablets",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["grace@mergington.edu", "noah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Compete in debate competitions and develop public speaking skills",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["rachel@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Design and build robots for STEM competitions",
            "schedule": "Tuesdays and Thursdays, 4:30 PM - 6:00 PM",
            "max_participants": 20,
            "participants": ["sean@mergington.edu", "jessica@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Tennis Club" in data
        assert "Basketball Team" in data
        assert "Programming Class" in data
    
    def test_activities_structure(self, client):
        """Test that each activity has the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)
    
    def test_tennis_club_details(self, client):
        """Test specific activity details"""
        response = client.get("/activities")
        data = response.json()
        
        tennis = data["Tennis Club"]
        assert tennis["max_participants"] == 16
        assert "alex@mergington.edu" in tennis["participants"]


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup(self, client):
        """Test successfully signing up for an activity"""
        response = client.post(
            "/activities/Tennis Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Tennis Club" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Tennis Club"]["participants"]
    
    def test_signup_duplicate_participant(self, client):
        """Test that duplicate signup is rejected"""
        # First signup
        client.post("/activities/Tennis Club/signup?email=test@mergington.edu")
        
        # Try to signup again
        response = client.post("/activities/Tennis Club/signup?email=test@mergington.edu")
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_nonexistent_activity(self, client):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_with_special_characters(self, client):
        """Test signup with special characters in activity name"""
        response = client.post(
            "/activities/Programming Class/signup?email=coder@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "coder@mergington.edu" in activities_data["Programming Class"]["participants"]
    
    def test_signup_multiple_students_different_activities(self, client):
        """Test multiple students signing up for different activities"""
        # Student 1 signs up for Tennis
        response1 = client.post(
            "/activities/Tennis Club/signup?email=student1@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Student 2 signs up for Chess
        response2 = client.post(
            "/activities/Chess Club/signup?email=student2@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify both signups
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "student1@mergington.edu" in activities_data["Tennis Club"]["participants"]
        assert "student2@mergington.edu" in activities_data["Chess Club"]["participants"]


class TestUnregisterEndpoint:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_successful_unregister(self, client):
        """Test successfully unregistering from an activity"""
        # First, add a participant
        client.post("/activities/Tennis Club/signup?email=test@mergington.edu")
        
        # Then unregister
        response = client.post(
            "/activities/Tennis Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]
        assert "Tennis Club" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "test@mergington.edu" not in activities_data["Tennis Club"]["participants"]
    
    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant from initial data"""
        response = client.post(
            "/activities/Tennis Club/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "alex@mergington.edu" not in activities_data["Tennis Club"]["participants"]
    
    def test_unregister_not_signed_up(self, client):
        """Test unregistering a student who is not signed up"""
        response = client.post(
            "/activities/Tennis Club/unregister?email=notsignedup@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from a non-existent activity"""
        response = client.post(
            "/activities/Fake Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_then_unregister_workflow(self, client):
        """Test complete workflow: signup then unregister"""
        email = "workflow@mergington.edu"
        activity = "Drama Club"
        
        # Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify count increased
        after_signup = client.get("/activities")
        after_signup_count = len(after_signup.json()[activity]["participants"])
        assert after_signup_count == initial_count + 1
        
        # Unregister
        unregister_response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify count back to original
        after_unregister = client.get("/activities")
        after_unregister_count = len(after_unregister.json()[activity]["participants"])
        assert after_unregister_count == initial_count


class TestDataIntegrity:
    """Tests for data integrity and edge cases"""
    
    def test_participant_list_persistence(self, client):
        """Test that participant lists are properly maintained"""
        # Add participants to multiple activities
        client.post("/activities/Tennis Club/signup?email=student1@mergington.edu")
        client.post("/activities/Chess Club/signup?email=student2@mergington.edu")
        client.post("/activities/Drama Club/signup?email=student3@mergington.edu")
        
        # Get activities
        response = client.get("/activities")
        data = response.json()
        
        # Verify all participants are in their respective activities
        assert "student1@mergington.edu" in data["Tennis Club"]["participants"]
        assert "student2@mergington.edu" in data["Chess Club"]["participants"]
        assert "student3@mergington.edu" in data["Drama Club"]["participants"]
        
        # Verify they're NOT in other activities
        assert "student1@mergington.edu" not in data["Chess Club"]["participants"]
        assert "student2@mergington.edu" not in data["Drama Club"]["participants"]
    
    def test_url_encoding_in_activity_names(self, client):
        """Test that activity names with spaces are properly handled"""
        response = client.post(
            "/activities/Digital%20Art%20Workshop/signup?email=artist@mergington.edu"
        )
        assert response.status_code == 200
    
    def test_multiple_participants_same_activity(self, client):
        """Test adding multiple participants to the same activity"""
        activity = "Robotics Club"
        emails = [
            "robot1@mergington.edu",
            "robot2@mergington.edu",
            "robot3@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all were added
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity]["participants"]
        for email in emails:
            assert email in participants
