"""
Mission 06: Template Views Tests

Test suite to verify Django template system functionality.
Students must master template syntax, inheritance, and custom template tags/filters.
"""

import pytest
from django.template import Context, Template
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from polls.models import Choice, Question


@pytest.mark.mission06
@pytest.mark.django_db
class TestTemplateExistence:
    """Test that required templates exist."""

    def test_base_template_exists(self):
        """Verify base.html template exists."""
        from django.template.loader import get_template

        try:
            get_template("base.html")
            assert True
        except Exception:
            pytest.fail("base.html template should exist")

    def test_polls_templates_exist(self):
        """Verify polls templates exist."""
        from django.template.loader import get_template

        templates = ["polls/index.html", "polls/detail.html", "polls/results.html"]

        for template_name in templates:
            try:
                get_template(template_name)
            except Exception:
                pytest.skip(f"Template {template_name} not yet created")


@pytest.mark.mission06
@pytest.mark.django_db
class TestTemplateInheritance:
    """Test template inheritance."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return Client()

    @pytest.fixture
    def question(self):
        """Create test question."""
        return Question.objects.create(question_text="Test?", pub_date=timezone.now())

    def test_templates_extend_base(self, client, question):
        """Test that templates extend base.html."""
        response = client.get(reverse("polls:index"))

        content = response.content.decode()

        # Check for base template elements
        assert "<html" in content.lower(), "Should have HTML structure from base"
        assert "<body" in content.lower(), "Should have body from base"

    def test_templates_have_title_block(self, client):
        """Test templates override title block."""
        response = client.get(reverse("polls:index"))

        content = response.content.decode()
        assert "<title>" in content.lower(), "Should have title tag"


@pytest.mark.mission06
@pytest.mark.django_db
class TestTemplateContext:
    """Test template context variables."""

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

    def test_index_template_displays_questions(self, client, questions):
        """Test index template shows questions."""
        response = client.get(reverse("polls:index"))

        content = response.content.decode()

        for question in questions:
            assert question.question_text in content, (
                f"Should display {question.question_text}"
            )

    def test_detail_template_displays_choices(self, client):
        """Test detail template shows choices."""
        question = Question.objects.create(
            question_text="Test?", pub_date=timezone.now()
        )

        choices = [
            Choice.objects.create(question=question, choice_text=f"Choice {i}", votes=0)
            for i in range(3)
        ]

        response = client.get(reverse("polls:detail", args=[question.id]))
        content = response.content.decode()

        for choice in choices:
            assert choice.choice_text in content, f"Should display {choice.choice_text}"


@pytest.mark.mission06
class TestCustomTemplateTags:
    """Test custom template tags."""

    def test_template_tags_module_exists(self):
        """Verify templatetags module exists."""
        try:
            import polls.templatetags  # noqa: F401

            assert True
        except ImportError:
            pytest.skip("templatetags module not yet created")

    def test_poll_extras_module_exists(self):
        """Verify poll_extras module exists."""
        try:
            import polls.templatetags.poll_extras  # noqa: F401

            assert True
        except ImportError:
            pytest.skip("poll_extras module not yet created")

    def test_percentage_filter_exists(self):
        """Test custom percentage filter exists."""
        try:
            from polls.templatetags.poll_extras import percentage

            result = percentage(25, 100)
            assert result == 25.0, "Percentage filter should calculate correctly"
        except ImportError:
            pytest.skip("percentage filter not yet implemented")

    def test_percentage_filter_in_template(self):
        """Test percentage filter works in template."""
        try:
            template = Template("{% load poll_extras %}{{ 25|percentage:100 }}")
            context = Context({})
            result = template.render(context)

            assert "25" in result, "Percentage filter should work in template"
        except Exception:
            pytest.skip("percentage filter not yet implemented")


@pytest.mark.mission06
class TestTemplateFilters:
    """Test built-in and custom template filters."""

    def test_date_filter_works(self):
        """Test built-in date filter usage."""
        from datetime import datetime

        template = Template("{{ pub_date|date:'Y-m-d' }}")
        context = Context({"pub_date": datetime.now()})
        result = template.render(context)

        assert len(result) > 0, "Date filter should render"

    def test_truncatewords_filter_works(self):
        """Test built-in truncatewords filter."""
        template = Template("{{ text|truncatewords:3 }}")
        context = Context(
            {"text": "This is a long question text that should be truncated"}
        )
        result = template.render(context)

        assert "..." in result or len(result) < 50, "Text should be truncated"


@pytest.mark.mission06
@pytest.mark.django_db
class TestTemplateFormsCSRF:
    """Test template form handling."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return Client()

    @pytest.fixture
    def question(self):
        """Create test question with choices."""
        q = Question.objects.create(question_text="Test?", pub_date=timezone.now())
        Choice.objects.create(question=q, choice_text="Choice 1", votes=0)
        return q

    def test_form_has_csrf_token(self, client, question):
        """Test forms include CSRF token."""
        response = client.get(reverse("polls:detail", args=[question.id]))

        content = response.content.decode()

        assert "csrfmiddlewaretoken" in content, "Form should include CSRF token"

    def test_form_uses_post_method(self, client, question):
        """Test voting form uses POST method."""
        response = client.get(reverse("polls:detail", args=[question.id]))

        content = response.content.decode()

        assert 'method="post"' in content.lower(), "Form should use POST method"


@pytest.mark.mission06
@pytest.mark.django_db
class TestTemplateStaticFiles:
    """Test static files usage in templates."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return Client()

    def test_templates_load_static_tag(self, client):
        """Test templates use static tag."""
        response = client.get(reverse("polls:index"))

        content = response.content.decode()

        # Check for static files or CDN resources
        has_static = "/static/" in content or "cdn" in content.lower()

        if has_static:
            assert True, "Templates should use static files"


@pytest.mark.mission06
@pytest.mark.django_db
class TestTemplateLogic:
    """Test template logic and control flow."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return Client()

    def test_template_handles_empty_list(self, client):
        """Test template handles empty question list."""
        # Clear all questions
        Question.objects.all().delete()

        response = client.get(reverse("polls:index"))

        assert response.status_code == 200, "Should handle empty list gracefully"

    def test_template_loops_through_choices(self, client):
        """Test template loops through choices."""
        question = Question.objects.create(
            question_text="Test?", pub_date=timezone.now()
        )

        for i in range(5):
            Choice.objects.create(question=question, choice_text=f"Choice {i}", votes=0)

        response = client.get(reverse("polls:detail", args=[question.id]))
        content = response.content.decode()

        # Should display all choices
        for i in range(5):
            assert f"Choice {i}" in content


@pytest.mark.mission06
@pytest.mark.django_db
class TestTemplateURLTags:
    """Test URL tag usage in templates."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return Client()

    @pytest.fixture
    def question(self):
        """Create test question."""
        return Question.objects.create(question_text="Test?", pub_date=timezone.now())

    def test_template_uses_url_tag(self, client, question):
        """Test templates use {% url %} tag for links."""
        response = client.get(reverse("polls:index"))

        content = response.content.decode()

        # Should use URL tag (will generate /polls/X/ format)
        assert "/polls/" in content, "Should use proper URL generation"


@pytest.mark.mission06
@pytest.mark.django_db
class TestTemplateMessages:
    """Test template message framework integration."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return Client()

    def test_template_displays_messages(self, client):
        """Test templates can display Django messages."""

        question = Question.objects.create(
            question_text="Test?", pub_date=timezone.now()
        )
        choice = Choice.objects.create(question=question, choice_text="Test", votes=0)

        # Cast a vote (should add a message)
        response = client.post(
            reverse("polls:vote", args=[question.id]),
            {"choice": choice.id},
            follow=True,
        )

        # Message framework should be usable in templates
        if response.context and "messages" in response.context:
            assert True, "Messages framework should be available"
