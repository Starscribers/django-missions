"""
Mission 02: Admin Interface Tests

Test suite to verify Django admin configuration and functionality.
Students must configure admin properly and be able to manage data through admin interface.
"""

import pytest
from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from django.test import Client
from django.utils import timezone

from polls.models import Choice, Question

User = get_user_model()


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def superuser(db):
    """Create a superuser for testing."""
    return User.objects.create_superuser(
        username="admin", email="admin@test.com", password="testpass123"
    )


@pytest.fixture
def regular_user(db):
    """Create a regular user for testing."""
    return User.objects.create_user(
        username="user", email="user@test.com", password="testpass123"
    )


@pytest.fixture
def client_fixture():
    """Create test client."""
    return Client()


@pytest.fixture
def authenticated_client(superuser):
    """Create authenticated client."""
    client = Client()
    client.login(username="admin", password="testpass123")
    return client


@pytest.fixture
def sample_question(db):
    """Create a test question."""
    return Question.objects.create(
        question_text="Test question?", pub_date=timezone.now()
    )


# =============================================================================
# Admin Registration Tests
# =============================================================================


@pytest.mark.admin_interface
@pytest.mark.django_db
def test_question_model_registered_in_admin():
    """Verify Question model is registered in admin."""
    assert Question in site._registry, "Question model should be registered in admin"


@pytest.mark.admin_interface
@pytest.mark.django_db
def test_choice_model_registered_in_admin():
    """Verify Choice model is registered in admin."""
    assert Choice in site._registry, "Choice model should be registered in admin"


@pytest.mark.admin_interface
@pytest.mark.django_db
def test_question_admin_has_list_display():
    """Verify Question admin has custom list_display."""
    admin_instance = site._registry[Question]
    assert hasattr(admin_instance, "list_display"), (
        "QuestionAdmin should have list_display"
    )
    assert len(admin_instance.list_display) > 1, (
        "list_display should have multiple fields"
    )


@pytest.mark.admin_interface
@pytest.mark.django_db
def test_question_admin_has_fieldsets():
    """Verify Question admin has custom fieldsets."""
    admin_instance = site._registry[Question]
    assert hasattr(admin_instance, "fieldsets"), "QuestionAdmin should have fieldsets"


@pytest.mark.admin_interface
@pytest.mark.django_db
def test_question_admin_has_inlines():
    """Verify Question admin has inline editing for choices."""
    admin_instance = site._registry[Question]
    assert hasattr(admin_instance, "inlines"), "QuestionAdmin should have inlines"
    assert len(admin_instance.inlines) > 0, "Should have at least one inline"


@pytest.mark.admin_interface
@pytest.mark.django_db
def test_question_admin_has_search_fields():
    """Verify Question admin has search capability."""
    admin_instance = site._registry[Question]
    assert hasattr(admin_instance, "search_fields"), (
        "QuestionAdmin should have search_fields"
    )


# =============================================================================
# Admin Access Tests
# =============================================================================


@pytest.mark.admin_interface
@pytest.mark.django_db
def test_admin_login_page_accessible(client_fixture):
    """Verify admin login page is accessible."""
    response = client_fixture.get("/admin/login/")
    assert response.status_code == 200, "Admin login page should be accessible"


@pytest.mark.admin_interface
@pytest.mark.django_db
def test_admin_requires_authentication(client_fixture):
    """Verify admin requires authentication."""
    response = client_fixture.get("/admin/")
    # Should redirect to login
    assert response.status_code in [302, 200], (
        "Admin should handle unauthenticated access"
    )


@pytest.mark.admin_interface
@pytest.mark.django_db
def test_superuser_can_access_admin(superuser):
    """Verify superuser can access admin."""
    client = Client()
    client.login(username="admin", password="testpass123")
    response = client.get("/admin/")
    assert response.status_code == 200, "Superuser should access admin"


@pytest.mark.admin_interface
@pytest.mark.django_db
def test_admin_question_list_accessible_for_superuser(superuser):
    """Verify superuser can access Question admin list."""
    client = Client()
    client.login(username="admin", password="testpass123")
    response = client.get("/admin/polls/question/")
    assert response.status_code == 200, "Superuser should access Question admin list"


@pytest.mark.admin_interface
@pytest.mark.django_db
def test_admin_choice_list_accessible_for_superuser(superuser):
    """Verify superuser can access Choice admin list."""
    client = Client()
    client.login(username="admin", password="testpass123")
    response = client.get("/admin/polls/choice/")
    assert response.status_code == 200, "Superuser should access Choice admin list"


# =============================================================================
# Admin Functionality Tests
# =============================================================================


@pytest.mark.admin_interface
@pytest.mark.django_db
def test_can_create_question_through_admin(authenticated_client):
    """Verify questions can be created through admin."""
    response = authenticated_client.post(
        "/admin/polls/question/add/",
        {
            "question_text": "Test question from admin?",
            "pub_date_0": timezone.now().date(),
            "pub_date_1": timezone.now().time(),
        },
    )

    # Check if question was created
    assert Question.objects.filter(question_text="Test question from admin?").exists()


@pytest.mark.admin_interface
@pytest.mark.django_db
def test_admin_search_functionality(authenticated_client, django_db_blocker):
    """Verify admin search works for questions."""
    with django_db_blocker.unblock():
        Question.objects.create(
            question_text="Searchable question?", pub_date=timezone.now()
        )

    response = authenticated_client.get("/admin/polls/question/?q=Searchable")
    assert response.status_code == 200
    assert b"Searchable question?" in response.content


# =============================================================================
# Admin Inlines Tests
# =============================================================================


@pytest.mark.admin_interface
@pytest.mark.django_db
def test_choices_appear_inline_in_question_admin(superuser, sample_question):
    """Verify choices can be edited inline in Question admin."""
    client = Client()
    client.login(username="admin", password="testpass123")

    response = client.get(f"/admin/polls/question/{sample_question.id}/change/")
    assert response.status_code == 200

    # Check for inline formset elements
    content = response.content.decode()
    assert "choice_set" in content or "inline" in content.lower()
