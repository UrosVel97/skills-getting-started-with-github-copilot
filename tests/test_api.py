"""
Tests for the High School Management System API
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
    # Store original state
    original_activities = {
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
        },
        "Soccer Team": {
            "description": "Team practices and interschool matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 22,
            "participants": ["liam@mergington.edu", "noah@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Skill development, scrimmages, and local tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["ava@mergington.edu", "isabella@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore drawing, painting, and mixed media projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu", "charlotte@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting workshops, rehearsals, and seasonal performances",
            "schedule": "Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
        },
        "Math Club": {
            "description": "Problem solving, math competitions, and peer tutoring",
            "schedule": "Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["lucas@mergington.edu", "logan@mergington.edu"]
        },
        "Debate Team": {
            "description": "Learn debate skills, research topics, and compete in tournaments",
            "schedule": "Mondays, 5:00 PM - 6:30 PM",
            "max_participants": 20,
            "participants": ["ella@mergington.edu", "samantha@mergington.edu"]
        }
    }
    
    # Reset activities to original state before each test
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Clean up after test (optional)
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_index(self, client):
        """Test that root redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        
    def test_activity_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_already_registered(self, client):
        """Test signup when student is already registered"""
        # First signup
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        
        # Try to signup again
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_with_special_characters_in_name(self, client):
        """Test signup with activity name containing special characters"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client):
        """Test successful unregister from an activity"""
        # Verify participant exists
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" in activities_data["Chess Club"]["participants"]
        
        # Unregister
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_activity_not_found(self, client):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_registered(self, client):
        """Test unregister when student is not registered"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notstudent@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_with_special_characters(self, client):
        """Test unregister with special characters in activity name"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200


class TestEndToEndWorkflow:
    """End-to-end tests for complete user workflows"""
    
    def test_signup_and_unregister_workflow(self, client):
        """Test complete workflow: signup -> verify -> unregister -> verify"""
        email = "workflow@mergington.edu"
        activity = "Programming Class"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Signup
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signup
        after_signup = client.get("/activities")
        assert email in after_signup.json()[activity]["participants"]
        assert len(after_signup.json()[activity]["participants"]) == initial_count + 1
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify unregister
        after_unregister = client.get("/activities")
        assert email not in after_unregister.json()[activity]["participants"]
        assert len(after_unregister.json()[activity]["participants"]) == initial_count
    
    def test_multiple_activities_signup(self, client):
        """Test signing up for multiple different activities"""
        email = "multisport@mergington.edu"
        
        # Signup for multiple activities
        activities_to_join = ["Chess Club", "Programming Class", "Art Club"]
        
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all signups
        all_activities = client.get("/activities").json()
        for activity in activities_to_join:
            assert email in all_activities[activity]["participants"]
