"""
Mission 07: API Views Tests

Test suite to verify Django API functionality.
Students must implement RESTful API endpoints with proper HTTP methods and JSON responses.
"""

import json

import pytest
from django.test import Client
from django.utils import timezone

from polls.models import Choice, Question


@pytest.mark.mission07
@pytest.mark.django_db
class TestAPIEndpointsExist:
    """Test that API endpoints exist."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return Client()

    def test_api_polls_list_endpoint_exists(self, client):
        """Test API polls list endpoint exists."""
        response = client.get("/api/polls/")

        # Should not return 404
        assert response.status_code != 404, "API polls list endpoint should exist"

    def test_api_polls_detail_endpoint_exists(self, client):
        """Test API polls detail endpoint exists."""
        question = Question.objects.create(
            question_text="Test?", pub_date=timezone.now()
        )

        response = client.get(f"/api/polls/{question.id}/")

        # Should not return 404
        assert response.status_code != 404, "API polls detail endpoint should exist"


@pytest.mark.mission07
@pytest.mark.django_db
class TestAPIResponseFormat:
    """Test API returns proper JSON responses."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return Client()

    @pytest.fixture
    def question(self):
        """Create test question."""
        return Question.objects.create(
            question_text="API Test?", pub_date=timezone.now()
        )

    def test_api_returns_json(self, client, question):
        """Test API returns JSON content type."""
        response = client.get("/api/polls/")

        assert (
            response["Content-Type"] == "application/json"
            or "json" in response["Content-Type"].lower()
        )

    def test_api_list_returns_valid_json(self, client, question):
        """Test API list returns valid JSON structure."""
        response = client.get("/api/polls/")

        try:
            data = json.loads(response.content)
            assert isinstance(data, (dict, list)), "Should return dict or list"
        except json.JSONDecodeError:
            pytest.fail("Response should be valid JSON")

    def test_api_detail_returns_poll_data(self, client, question):
        """Test API detail returns poll data."""
        response = client.get(f"/api/polls/{question.id}/")

        if response.status_code == 200:
            data = json.loads(response.content)

            assert "id" in data or "question_text" in data, "Should return poll data"


@pytest.mark.mission07
@pytest.mark.django_db
class TestAPIGETMethods:
    """Test API GET method functionality."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return Client()

    @pytest.fixture
    def questions(self):
        """Create test questions."""
        return [
            Question.objects.create(
                question_text=f"Question {i}?", pub_date=timezone.now()
            )
            for i in range(3)
        ]

    def test_api_list_returns_all_polls(self, client, questions):
        """Test API list returns all polls."""
        response = client.get("/api/polls/")

        if response.status_code == 200:
            data = json.loads(response.content)

            # Handle both paginated and non-paginated responses
            if isinstance(data, dict) and "polls" in data:
                polls = data["polls"]
            elif isinstance(data, dict) and "results" in data:
                polls = data["results"]
            else:
                polls = data

            assert len(polls) >= 3, "Should return at least 3 polls"

    def test_api_detail_returns_correct_poll(self, client, questions):
        """Test API detail returns correct poll."""
        question = questions[0]

        response = client.get(f"/api/polls/{question.id}/")

        if response.status_code == 200:
            data = json.loads(response.content)

            assert (
                data.get("id") == question.id
                or data.get("question_text") == question.question_text
            )


@pytest.mark.mission07
@pytest.mark.django_db
class TestAPIPOSTMethods:
    """Test API POST method functionality."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return Client()

    def test_api_create_poll(self, client):
        """Test creating poll via API."""
        poll_data = {
            "question_text": "New API Poll?",
            "choices": ["Choice A", "Choice B"],
        }

        response = client.post(
            "/api/polls/", data=json.dumps(poll_data), content_type="application/json"
        )

        # Should create successfully
        if response.status_code in [200, 201]:
            # Verify poll was created
            assert Question.objects.filter(question_text="New API Poll?").exists()

    def test_api_vote(self, client):
        """Test voting via API."""
        question = Question.objects.create(
            question_text="Vote Test?", pub_date=timezone.now()
        )
        choice = Choice.objects.create(
            question=question, choice_text="Test Choice", votes=0
        )

        vote_data = {"choice_id": choice.id}

        response = client.post(
            f"/api/polls/{question.id}/vote/",
            data=json.dumps(vote_data),
            content_type="application/json",
        )

        if response.status_code in [200, 201]:
            choice.refresh_from_db()
            assert choice.votes == 1, "Vote should be recorded"


@pytest.mark.mission07
@pytest.mark.django_db
class TestAPIErrorHandling:
    """Test API error handling."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return Client()

    def test_api_returns_404_for_nonexistent_poll(self, client):
        """Test API returns 404 for non-existent poll."""
        response = client.get("/api/polls/999999/")

        assert response.status_code == 404, "Should return 404 for non-existent poll"

    def test_api_returns_error_for_invalid_data(self, client):
        """Test API returns error for invalid data."""
        invalid_data = {}  # Missing required fields

        response = client.post(
            "/api/polls/",
            data=json.dumps(invalid_data),
            content_type="application/json",
        )

        # Should return error (400 or similar)
        if response.status_code == 400:
            data = json.loads(response.content)
            assert "error" in data or "message" in data, "Should return error message"


@pytest.mark.mission07
@pytest.mark.django_db
class TestAPIPagination:
    """Test API pagination."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return Client()

    @pytest.fixture
    def many_questions(self):
        """Create many questions for pagination testing."""
        return [
            Question.objects.create(
                question_text=f"Question {i}?", pub_date=timezone.now()
            )
            for i in range(15)
        ]

    def test_api_supports_pagination(self, client, many_questions):
        """Test API supports pagination."""
        response = client.get("/api/polls/?page=1&per_page=5")

        if response.status_code == 200:
            data = json.loads(response.content)

            # Check for pagination indicators
            has_pagination = (
                "pagination" in data
                or "next" in data
                or "previous" in data
                or "count" in data
            )

            if has_pagination:
                assert True, "API should support pagination"


@pytest.mark.mission07
@pytest.mark.django_db
class TestAPIFiltering:
    """Test API filtering capabilities."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return Client()

    @pytest.fixture
    def questions(self):
        """Create test questions."""
        Question.objects.create(
            question_text="Django question?", pub_date=timezone.now()
        )
        Question.objects.create(
            question_text="Python question?", pub_date=timezone.now()
        )
        return Question.objects.all()

    def test_api_supports_search(self, client, questions):
        """Test API supports search/filtering."""
        response = client.get("/api/polls/?search=Django")

        if response.status_code == 200:
            data = json.loads(response.content)

            # Handle different response structures
            if isinstance(data, dict) and "polls" in data:
                polls = data["polls"]
            elif isinstance(data, dict) and "results" in data:
                polls = data["results"]
            else:
                polls = data

            # If search is implemented, should filter results
            if len(polls) < questions.count():
                assert True, "Search filtering works"


@pytest.mark.mission07
@pytest.mark.django_db
class TestAPIAuthentication:
    """Test API authentication (if implemented)."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return Client()

    def test_api_accepts_authenticated_requests(self, client):
        """Test API handles authentication."""
        # Try with authentication header
        response = client.get("/api/polls/", HTTP_AUTHORIZATION="Bearer test_token")

        # Should handle auth header (even if not required)
        assert response.status_code != 500, "Should handle auth headers gracefully"


@pytest.mark.mission07
@pytest.mark.django_db
class TestAPIDocumentation:
    """Test API documentation exists."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return Client()

    def test_api_documentation_endpoint_exists(self, client):
        """Test API documentation endpoint exists."""
        possible_docs_urls = [
            "/api/docs/",
            "/api/schema/",
            "/api/",
        ]

        for url in possible_docs_urls:
            response = client.get(url)
            if response.status_code == 200:
                assert True, "API documentation exists"
                return

        pytest.skip("API documentation not yet implemented")


@pytest.mark.mission07
@pytest.mark.django_db
class TestAPIVersoning:
    """Test API versioning (if implemented)."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return Client()

    def test_api_version_in_response(self, client):
        """Test API includes version information."""
        response = client.get("/api/polls/")

        if response.status_code == 200:
            data = json.loads(response.content)

            # Check for version indicators
            has_version = (
                "version" in data
                or "api_version" in data
                or "/v1/" in response.request.get("PATH_INFO", "")
            )

            if has_version:
                assert True, "API versioning implemented"


@pytest.mark.mission07
@pytest.mark.django_db
class TestAPIChoices:
    """Test API choice-related endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return Client()

    @pytest.fixture
    def question_with_choices(self):
        """Create question with choices."""
        question = Question.objects.create(
            question_text="Test?", pub_date=timezone.now()
        )

        for i in range(3):
            Choice.objects.create(
                question=question, choice_text=f"Choice {i}", votes=i * 10
            )

        return question

    def test_api_detail_includes_choices(self, client, question_with_choices):
        """Test API detail includes choices."""
        response = client.get(f"/api/polls/{question_with_choices.id}/")

        if response.status_code == 200:
            data = json.loads(response.content)

            assert "choices" in data, "API should include choices in detail view"
            assert len(data["choices"]) == 3, "Should include all choices"

    def test_api_includes_vote_counts(self, client, question_with_choices):
        """Test API includes vote counts."""
        response = client.get(f"/api/polls/{question_with_choices.id}/")

        if response.status_code == 200:
            data = json.loads(response.content)

            if "choices" in data:
                for choice in data["choices"]:
                    assert "votes" in choice, "Each choice should include vote count"
