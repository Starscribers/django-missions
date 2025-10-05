"""
Mission 01: Landing Page Customization Tests

Test suite to verify students have customized the landing page:
1. Changed the title, subtitle, and description
2. Added their own signature (replaced Starscribers)
3. Changed button label to "Explore polls" and verified redirect to /polls/
"""

import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.landing_page
@pytest.mark.django_db
def test_landing_page_content_customized():
    """
    Task 1: Verify landing page title, subtitle, and description are customized.

    Students should change:
    - Title (h1): Currently "Congrats" - should be different
    - Subtitle (h2): Currently "Setup complete." - should be different
    - Description (p): Should contain custom content
    """
    client = Client()
    response = client.get("/")
    content = response.content.decode()

    # Check that page is accessible
    assert response.status_code == 200, "Landing page should be accessible"

    # Check that original default content has been changed
    # Students should NOT have these exact default texts
    has_default_title = "Congrats" in content and "text-6xl" in content
    has_default_subtitle = "Setup complete." in content
    has_default_description = "You're all set to explore the Django tutorial" in content

    # At least 2 of the 3 default texts should be changed
    defaults_remaining = sum(
        [has_default_title, has_default_subtitle, has_default_description]
    )

    assert defaults_remaining < 2, (
        "Landing page content should be customized. "
        "Please change the title, subtitle, and/or description to make it your own. "
        f"Currently {defaults_remaining} of 3 default texts remain unchanged."
    )

    # Verify there is still meaningful content
    assert len(content) > 500, "Landing page should have substantial content"


@pytest.mark.landing_page
@pytest.mark.django_db
def test_landing_page_has_custom_signature():
    """
    Task 2: Verify landing page has a custom signature replacing "Starscribers".

    Students should:
    - Add their own signature/name
    - Remove or replace "Starscribers"
    """
    client = Client()
    response = client.get("/")
    content = response.content.decode()

    # Check that Starscribers has been replaced
    assert "Starscribers" not in content, (
        "Please replace 'Starscribers' with your own signature in the footer"
    )

    # Check that there is some signature text (look for common signature indicators)
    has_signature = (
        "Signature" in content
        or "signature" in content
        or "Made by" in content
        or "Created by" in content
        or "Built by" in content
        or "Author" in content
        or "©" in content
    )

    assert has_signature, (
        "Please add your own signature to the landing page footer. "
        "Examples: 'Signature: Your Name', 'Made by Your Name', '© Your Name'"
    )


@pytest.mark.landing_page
@pytest.mark.django_db
def test_explore_polls_button_redirects_correctly():
    """
    Task 3: Verify button label is "Explore polls" and redirects to /polls/ page.

    Students should:
    - Change button label from "Ready to Explore" to "Explore polls"
    - Ensure button links to /polls/ (polls:index)
    - Verify polls index page is accessible
    """
    client = Client()
    response = client.get("/")
    content = response.content.decode()

    # Check button label has been changed
    assert "Explore polls" in content, (
        "Button label should be changed to 'Explore polls'"
    )

    # Verify old label is removed
    assert "Ready to Explore" not in content, (
        "Please change 'Ready to Explore' to 'Explore polls'"
    )

    # Check that button links to polls index
    polls_index_url = reverse("polls:index")
    assert polls_index_url in content, (
        f"Button should link to polls index page ({polls_index_url})"
    )

    # Verify polls page is actually accessible
    polls_response = client.get(polls_index_url)
    assert polls_response.status_code != 404, (
        f"Polls index page should be accessible at {polls_index_url}"
    )
