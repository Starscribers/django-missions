"""
Mission 03: Models & ORM Tests

Test suite to verify Django models and ORM functionality.
Students must understand model fields, relationships, and ORM queries.
"""

from datetime import timedelta

import pytest
from django.db import models
from django.utils import timezone

from polls.models import Choice, Question

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_questions(db):
    """Create sample questions for testing."""
    q1 = Question.objects.create(
        question_text="Django question?", pub_date=timezone.now() - timedelta(days=1)
    )
    q2 = Question.objects.create(
        question_text="Python question?", pub_date=timezone.now() - timedelta(hours=1)
    )
    q3 = Question.objects.create(
        question_text="React question?", pub_date=timezone.now()
    )
    return [q1, q2, q3]


# =============================================================================
# Models Tests
# =============================================================================


@pytest.mark.mission03
@pytest.mark.django_db
def test_question_model_exists():
    """Verify Question model exists."""
    assert Question is not None, "Question model should exist"


@pytest.mark.mission03
@pytest.mark.django_db
def test_choice_model_exists():
    """Verify Choice model exists."""
    assert Choice is not None, "Choice model should exist"


@pytest.mark.mission03
@pytest.mark.django_db
def test_question_has_required_fields():
    """Verify Question model has required fields."""
    field_names = [f.name for f in Question._meta.get_fields()]

    assert "question_text" in field_names, "Question should have question_text field"
    assert "pub_date" in field_names, "Question should have pub_date field"


@pytest.mark.mission03
@pytest.mark.django_db
def test_choice_has_required_fields():
    """Verify Choice model has required fields."""
    field_names = [f.name for f in Choice._meta.get_fields()]

    assert "question" in field_names, "Choice should have question field"
    assert "choice_text" in field_names, "Choice should have choice_text field"
    assert "votes" in field_names, "Choice should have votes field"


@pytest.mark.mission03
@pytest.mark.django_db
def test_question_text_field_type():
    """Verify question_text is CharField."""
    field = Question._meta.get_field("question_text")
    assert isinstance(field, models.CharField), "question_text should be CharField"


@pytest.mark.mission03
@pytest.mark.django_db
def test_pub_date_field_type():
    """Verify pub_date is DateTimeField."""
    field = Question._meta.get_field("pub_date")
    assert isinstance(field, models.DateTimeField), "pub_date should be DateTimeField"


@pytest.mark.mission03
@pytest.mark.django_db
def test_votes_field_type():
    """Verify votes is IntegerField."""
    field = Choice._meta.get_field("votes")
    assert isinstance(field, models.IntegerField), "votes should be IntegerField"


# =============================================================================
# Model Relationships Tests
# =============================================================================


@pytest.mark.mission03
@pytest.mark.django_db
def test_choice_has_foreign_key_to_question():
    """Verify Choice has ForeignKey to Question."""
    field = Choice._meta.get_field("question")
    assert isinstance(field, models.ForeignKey), "question should be ForeignKey"
    assert field.related_model == Question, "ForeignKey should point to Question"


@pytest.mark.mission03
@pytest.mark.django_db
def test_foreign_key_cascade_delete():
    """Verify ForeignKey has CASCADE delete behavior."""
    field = Choice._meta.get_field("question")
    assert field.remote_field.on_delete == models.CASCADE, (
        "Should use CASCADE on delete"
    )


@pytest.mark.mission03
@pytest.mark.django_db
def test_question_can_have_multiple_choices():
    """Verify one question can have multiple choices."""
    question = Question.objects.create(
        question_text="Test question?", pub_date=timezone.now()
    )

    Choice.objects.create(question=question, choice_text="Choice 1", votes=0)
    Choice.objects.create(question=question, choice_text="Choice 2", votes=0)
    Choice.objects.create(question=question, choice_text="Choice 3", votes=0)

    assert question.choice_set.count() == 3, "Question should have 3 choices"


@pytest.mark.mission03
@pytest.mark.django_db
def test_deleting_question_deletes_choices():
    """Verify deleting question deletes associated choices."""
    question = Question.objects.create(
        question_text="Test question?", pub_date=timezone.now()
    )

    Choice.objects.create(question=question, choice_text="Choice 1", votes=0)
    Choice.objects.create(question=question, choice_text="Choice 2", votes=0)

    question_id = question.id
    question.delete()

    # Choices should be deleted too
    assert Choice.objects.filter(question_id=question_id).count() == 0


# =============================================================================
# Model Methods Tests
# =============================================================================


@pytest.mark.mission03
@pytest.mark.django_db
def test_question_str_method():
    """Verify Question __str__ returns question_text."""
    question = Question.objects.create(
        question_text="What is Django?", pub_date=timezone.now()
    )

    assert str(question) == "What is Django?", "__str__ should return question_text"


@pytest.mark.mission03
@pytest.mark.django_db
def test_choice_str_method():
    """Verify Choice __str__ returns choice_text."""
    question = Question.objects.create(question_text="Test?", pub_date=timezone.now())
    choice = Choice.objects.create(question=question, choice_text="Yes", votes=0)

    assert str(choice) == "Yes", "__str__ should return choice_text"


@pytest.mark.mission03
@pytest.mark.django_db
def test_was_published_recently_with_recent_question():
    """Test was_published_recently for recent questions."""
    recent_question = Question.objects.create(
        question_text="Recent?", pub_date=timezone.now() - timedelta(hours=1)
    )

    assert recent_question.was_published_recently() is True


@pytest.mark.mission03
@pytest.mark.django_db
def test_was_published_recently_with_old_question():
    """Test was_published_recently for old questions."""
    old_question = Question.objects.create(
        question_text="Old?", pub_date=timezone.now() - timedelta(days=2)
    )

    assert old_question.was_published_recently() is False


@pytest.mark.mission03
@pytest.mark.django_db
def test_total_votes_method():
    """Test total_votes method calculates correctly."""
    question = Question.objects.create(question_text="Test?", pub_date=timezone.now())

    Choice.objects.create(question=question, choice_text="A", votes=10)
    Choice.objects.create(question=question, choice_text="B", votes=20)
    Choice.objects.create(question=question, choice_text="C", votes=15)

    assert question.total_votes() == 45, "total_votes should sum all choice votes"


@pytest.mark.mission03
@pytest.mark.django_db
def test_vote_percentage_method():
    """Test vote_percentage method on Choice."""
    question = Question.objects.create(question_text="Test?", pub_date=timezone.now())

    choice1 = Choice.objects.create(question=question, choice_text="A", votes=25)
    Choice.objects.create(question=question, choice_text="B", votes=75)

    percentage = choice1.vote_percentage()
    assert percentage == 25.0, "vote_percentage should calculate correctly"


# =============================================================================
# ORM Queries Tests
# =============================================================================


@pytest.mark.mission03
@pytest.mark.django_db
def test_filter_by_text(sample_questions):
    """Test filtering questions by text content."""
    django_questions = Question.objects.filter(question_text__contains="Django")
    assert django_questions.count() == 1
    assert django_questions.first().question_text == "Django question?"


@pytest.mark.mission03
@pytest.mark.django_db
def test_filter_by_date(sample_questions):
    """Test filtering questions by publication date."""
    recent = timezone.now() - timedelta(hours=2)
    recent_questions = Question.objects.filter(pub_date__gte=recent)
    assert recent_questions.count() >= 2


@pytest.mark.mission03
@pytest.mark.django_db
def test_order_by_pub_date(sample_questions):
    """Test ordering questions by publication date."""
    questions = Question.objects.order_by("-pub_date")
    assert questions.count() == 3
    # Most recent should be first
    assert "React" in questions.first().question_text


@pytest.mark.mission03
@pytest.mark.django_db
def test_get_specific_question(sample_questions):
    """Test retrieving specific question by ID."""
    q = sample_questions[0]
    retrieved = Question.objects.get(id=q.id)
    assert retrieved.question_text == q.question_text


@pytest.mark.mission03
@pytest.mark.django_db
def test_count_questions(sample_questions):
    """Test counting questions."""
    count = Question.objects.count()
    assert count == 3


@pytest.mark.mission03
@pytest.mark.django_db
def test_exclude_query(sample_questions):
    """Test excluding questions from query."""
    non_django = Question.objects.exclude(question_text__contains="Django")
    assert non_django.count() == 2


@pytest.mark.mission03
@pytest.mark.django_db
def test_complex_query_with_or(sample_questions):
    """Test complex queries with Q objects."""
    from django.db.models import Q

    questions = Question.objects.filter(
        Q(question_text__contains="Django") | Q(question_text__contains="Python")
    )
    assert questions.count() == 2


# =============================================================================
# Model Validation Tests
# =============================================================================


@pytest.mark.mission03
@pytest.mark.django_db
def test_question_text_cannot_be_empty():
    """Test question_text is required."""
    from django.core.exceptions import ValidationError

    question = Question(question_text="", pub_date=timezone.now())

    with pytest.raises(ValidationError):
        question.full_clean()


@pytest.mark.mission03
@pytest.mark.django_db
def test_votes_default_value():
    """Test votes field has default value of 0."""
    question = Question.objects.create(question_text="Test?", pub_date=timezone.now())
    choice = Choice.objects.create(question=question, choice_text="Test choice")

    assert choice.votes == 0, "votes should default to 0"


# =============================================================================
# Model Meta Tests
# =============================================================================


@pytest.mark.mission03
@pytest.mark.django_db
def test_question_verbose_name():
    """Test Question model has appropriate verbose name."""
    meta = Question._meta
    assert hasattr(meta, "verbose_name")


@pytest.mark.mission03
@pytest.mark.django_db
def test_question_ordering():
    """Test Question model has ordering defined."""
    meta = Question._meta
    if hasattr(meta, "ordering") and meta.ordering:
        assert isinstance(meta.ordering, (list, tuple)), (
            "ordering should be list or tuple"
        )
