"""
Mission 05: URLs & Views Tests

Test suite to verify Django URL routing and view functionality.
Students must implement function-based and class-based views with proper URL patterns.
"""

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from polls.models import Choice, Question


@pytest.mark.mission05
@pytest.mark.django_db
class TestURLConfiguration:
    """Test URL routing configuration."""

    def test_polls_urls_module_exists(self):
        """Verify polls/urls.py exists."""
        try:
            import polls.urls  # noqa: F401

            assert True
        except ImportError:
            pytest.fail("polls/urls.py should exist")

    def test_polls_app_namespace(self):
        """Verify polls app has URL namespace."""
        from polls import urls as polls_urls

        assert hasattr(polls_urls, "app_name"), "polls urls should define app_name"
        assert polls_urls.app_name == "polls", "app_name should be 'polls'"

    def test_index_url_resolves(self):
        """Test polls index URL resolves correctly."""
        url = reverse("polls:index")
        assert url == "/polls/", "Index URL should be '/polls/'"

    def test_detail_url_resolves(self):
        """Test question detail URL resolves correctly."""
        url = reverse("polls:detail", args=[1])
        assert url == "/polls/1/", "Detail URL should be '/polls/1/'"

    def test_results_url_resolves(self):
        """Test results URL resolves correctly."""
        url = reverse("polls:results", args=[1])
        assert url == "/polls/1/results/", "Results URL should be '/polls/1/results/'"

    def test_vote_url_resolves(self):
        """Test vote URL resolves correctly."""
        url = reverse("polls:vote", args=[1])
        assert url == "/polls/1/vote/", "Vote URL should be '/polls/1/vote/'"


@pytest.mark.mission05
@pytest.mark.django_db
class TestViewsExist:
    """Test that views exist and are properly configured."""

    def test_index_view_exists(self):
        """Verify IndexView exists."""
        try:
            from polls.views import IndexView  # noqa: F401

            assert True
        except ImportError:
            pytest.fail("IndexView should exist in polls/views.py")

    def test_detail_view_exists(self):
        """Verify DetailView exists."""
        try:
            from polls.views import DetailView  # noqa: F401

            assert True
        except ImportError:
            pytest.fail("DetailView should exist in polls/views.py")

    def test_results_view_exists(self):
        """Verify ResultsView exists."""
        try:
            from polls.views import ResultsView  # noqa: F401

            assert True
        except ImportError:
            pytest.fail("ResultsView should exist in polls/views.py")

    def test_vote_view_exists(self):
        """Verify vote view exists."""
        try:
            from polls.views import vote  # noqa: F401

            assert True
        except ImportError:
            pytest.fail("vote function should exist in polls/views.py")


@pytest.mark.mission05
@pytest.mark.django_db
class TestClassBasedViews:
    """Test class-based views implementation."""

    def test_index_view_is_listview(self):
        """Verify IndexView uses ListView."""
        from django.views.generic import ListView

        from polls.views import IndexView

        assert issubclass(IndexView, ListView), "IndexView should inherit from ListView"

    def test_detail_view_is_detailview(self):
        """Verify DetailView uses DetailView."""
        from django.views.generic import DetailView as GenericDetailView

        from polls.views import DetailView

        assert issubclass(DetailView, GenericDetailView), (
            "DetailView should inherit from DetailView"
        )

    def test_results_view_is_detailview(self):
        """Verify ResultsView uses DetailView."""
        from django.views.generic import DetailView as GenericDetailView

        from polls.views import ResultsView

        assert issubclass(ResultsView, GenericDetailView), (
            "ResultsView should inherit from DetailView"
        )

    def test_index_view_has_template_name(self):
        """Verify IndexView specifies template."""
        from polls.views import IndexView

        assert hasattr(IndexView, "template_name"), (
            "IndexView should have template_name"
        )

    def test_detail_view_has_model(self):
        """Verify DetailView specifies model."""
        from polls.views import DetailView

        assert hasattr(DetailView, "model"), "DetailView should have model attribute"


@pytest.mark.mission05
@pytest.mark.django_db
class TestFunctionBasedViews:
    """Test function-based views implementation."""

    def test_vote_is_function(self):
        """Verify vote is a function."""
        from inspect import isfunction

        from polls.views import vote

        assert isfunction(vote), "vote should be a function"

    def test_vote_function_parameters(self):
        """Verify vote function has correct parameters."""
        from inspect import signature

        from polls.views import vote

        sig = signature(vote)
        params = list(sig.parameters.keys())

        assert "request" in params, "vote should have request parameter"
        assert len(params) >= 2, "vote should have request and question_id parameters"


@pytest.mark.mission05
@pytest.mark.django_db
class TestViewFunctionality:
    """Test view behavior and responses."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return Client()

    @pytest.fixture
    def question(self):
        """Create test question."""
        return Question.objects.create(
            question_text="Test question?", pub_date=timezone.now()
        )

    @pytest.fixture
    def question_with_choices(self, question):
        """Create question with choices."""
        Choice.objects.create(question=question, choice_text="Choice 1", votes=0)
        Choice.objects.create(question=question, choice_text="Choice 2", votes=0)
        Choice.objects.create(question=question, choice_text="Choice 3", votes=0)
        return question

    def test_index_view_returns_200(self, client):
        """Test index view returns successful response."""
        response = client.get(reverse("polls:index"))
        assert response.status_code == 200, "Index view should return 200"

    def test_detail_view_returns_200(self, client, question):
        """Test detail view returns successful response."""
        response = client.get(reverse("polls:detail", args=[question.id]))
        assert response.status_code == 200, "Detail view should return 200"

    def test_results_view_returns_200(self, client, question):
        """Test results view returns successful response."""
        response = client.get(reverse("polls:results", args=[question.id]))
        assert response.status_code == 200, "Results view should return 200"

    def test_detail_view_with_nonexistent_question_returns_404(self, client):
        """Test detail view returns 404 for non-existent question."""
        response = client.get(reverse("polls:detail", args=[999]))
        assert response.status_code == 404, (
            "Should return 404 for non-existent question"
        )

    def test_index_view_shows_questions(self, client, question):
        """Test index view displays questions."""
        response = client.get(reverse("polls:index"))
        assert response.status_code == 200
        assert question.question_text.encode() in response.content

    def test_vote_view_handles_post(self, client, question_with_choices):
        """Test vote view handles POST requests."""
        choice = question_with_choices.choice_set.first()

        response = client.post(
            reverse("polls:vote", args=[question_with_choices.id]),
            {"choice": choice.id},
        )

        # Should redirect after successful vote
        assert response.status_code in [302, 200], "Vote should redirect or succeed"

    def test_vote_increments_choice_votes(self, client, question_with_choices):
        """Test voting increments vote count."""
        choice = question_with_choices.choice_set.first()
        initial_votes = choice.votes

        client.post(
            reverse("polls:vote", args=[question_with_choices.id]),
            {"choice": choice.id},
        )

        choice.refresh_from_db()
        assert choice.votes == initial_votes + 1, "Vote count should increment"

    def test_vote_without_choice_shows_error(self, client, question_with_choices):
        """Test voting without selecting choice shows error."""
        response = client.post(
            reverse("polls:vote", args=[question_with_choices.id]), {}
        )

        # Should show error or redirect back
        assert response.status_code in [200, 302]


@pytest.mark.mission05
@pytest.mark.django_db
class TestViewContextData:
    """Test view context data."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return Client()

    @pytest.fixture
    def question(self):
        """Create test question."""
        return Question.objects.create(
            question_text="Test question?", pub_date=timezone.now()
        )

    def test_index_view_provides_questions_in_context(self, client, question):
        """Test index view provides questions in context."""
        response = client.get(reverse("polls:index"))

        assert (
            "latest_question_list" in response.context
            or "question_list" in response.context
        )

    def test_detail_view_provides_question_in_context(self, client, question):
        """Test detail view provides question in context."""
        response = client.get(reverse("polls:detail", args=[question.id]))

        assert "question" in response.context or "object" in response.context


@pytest.mark.mission05
@pytest.mark.django_db
class TestHTTPMethods:
    """Test proper HTTP method handling."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return Client()

    @pytest.fixture
    def question(self):
        """Create test question."""
        q = Question.objects.create(question_text="Test?", pub_date=timezone.now())
        Choice.objects.create(question=q, choice_text="Test", votes=0)
        return q

    def test_vote_accepts_post(self, client, question):
        """Test vote endpoint accepts POST."""
        choice = question.choice_set.first()
        response = client.post(
            reverse("polls:vote", args=[question.id]), {"choice": choice.id}
        )

        assert response.status_code in [200, 302], "POST should be accepted"

    def test_index_accepts_get(self, client):
        """Test index endpoint accepts GET."""
        response = client.get(reverse("polls:index"))
        assert response.status_code == 200, "GET should be accepted"
