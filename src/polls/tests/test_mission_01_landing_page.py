"""
Mission 01: Landing Page & Setup Tests

Test suite to verify landing page content and polls app setup.
Students must adjust the landing page and ensure the button links to polls index.
"""

import pytest
from django.test import Client
from django.urls import reverse

# =============================================================================
# Landing Page Tests
# =============================================================================


@pytest.mark.landing_page
@pytest.mark.django_db
def test_landing_page_accessible():
    """Verify landing page is accessible."""
    client = Client()
    response = client.get("/")
    assert response.status_code == 200, "Landing page should be accessible"


@pytest.mark.landing_page
@pytest.mark.django_db
def test_landing_page_has_setup_complete_message():
    """Verify landing page shows 'Django Setup Complete' message."""
    client = Client()
    response = client.get("/")
    content = response.content.decode()

    assert "Django Setup Complete" in content, (
        "Should display 'Django Setup Complete' text"
    )


@pytest.mark.landing_page
@pytest.mark.django_db
def test_landing_page_has_ready_to_explore_button():
    """Verify landing page has 'Ready to Explore' button."""
    client = Client()
    response = client.get("/")
    content = response.content.decode()

    assert "Ready to Explore" in content, "Should have 'Ready to Explore' button"


@pytest.mark.landing_page
@pytest.mark.django_db
def test_ready_to_explore_button_links_to_polls_index():
    """Verify 'Ready to Explore' button links to polls index page."""
    client = Client()
    response = client.get("/")
    content = response.content.decode()

    # Check that the button/link points to polls:index URL
    polls_index_url = reverse("polls:index")
    assert polls_index_url in content, (
        f"Button should link to polls index ({polls_index_url})"
    )


@pytest.mark.landing_page
@pytest.mark.django_db
def test_landing_page_has_congrats_heading():
    """Verify landing page has congratulations heading."""
    client = Client()
    response = client.get("/")
    content = response.content.decode()

    assert "Congrats" in content or "Congratulations" in content, (
        "Should have congratulations heading"
    )


@pytest.mark.landing_page
@pytest.mark.django_db
def test_landing_page_has_setup_complete_heading():
    """Verify landing page indicates setup is complete."""
    client = Client()
    response = client.get("/")
    content = response.content.decode()

    assert "Setup complete" in content or "setup complete" in content, (
        "Should indicate setup is complete"
    )


# =============================================================================
# Polls App URL Configuration Tests
# =============================================================================


@pytest.mark.landing_page
@pytest.mark.django_db
def test_polls_index_url_exists():
    """Verify polls:index URL is configured."""
    try:
        polls_index_url = reverse("polls:index")
        assert polls_index_url is not None, "polls:index URL should be configured"
        assert "/polls/" in polls_index_url, "polls index URL should contain /polls/"
    except Exception as e:
        pytest.fail(f"polls:index URL not properly configured: {e}")


@pytest.mark.landing_page
@pytest.mark.django_db
def test_polls_app_accessible():
    """Verify polls app index page is accessible."""
    client = Client()
    try:
        polls_index_url = reverse("polls:index")
        response = client.get(polls_index_url)
        # Should return 200 or redirect, but not 404
        assert response.status_code != 404, (
            "Polls index page should be accessible (not 404)"
        )
    except Exception as e:
        pytest.fail(f"Could not access polls index: {e}")


@pytest.mark.landing_page
@pytest.mark.django_db
def test_polls_urls_included_in_project():
    """Verify polls URLs are included in main URL configuration."""
    from django.urls import resolve

    try:
        # Try to resolve /polls/ URL
        match = resolve("/polls/")
        assert match is not None, "polls URLs should be included in project"
    except Exception:
        pytest.fail("polls URLs not properly included in main urls.py")
