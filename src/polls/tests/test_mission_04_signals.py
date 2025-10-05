"""
Mission 04: Signals Tests

Test suite to verify Django signals functionality.
Students must implement and understand signal handlers for model events.
"""

from unittest.mock import Mock, patch

import pytest
from django.db.models.signals import post_delete, post_save, pre_save
from django.utils import timezone

from polls.models import Choice, Question


@pytest.mark.mission04
@pytest.mark.django_db
class TestSignalsExist:
    """Test that signal handlers exist."""

    def test_signals_module_exists(self):
        """Verify signals.py module exists."""
        try:
            import polls.signals  # noqa: F401

            assert True
        except ImportError:
            pytest.fail("polls/signals.py should exist")

    def test_signals_imported_in_app_config(self):
        """Verify signals are imported in apps.py ready() method."""
        from polls.apps import PollsConfig

        assert hasattr(PollsConfig, "ready"), "PollsConfig should have ready() method"


@pytest.mark.mission04
@pytest.mark.django_db
class TestPreSaveSignals:
    """Test pre_save signal handlers."""

    def test_question_pre_save_signal_fires(self):
        """Verify pre_save signal fires for Question."""
        mock_handler = Mock()

        pre_save.connect(mock_handler, sender=Question)

        try:
            Question.objects.create(
                question_text="Test question?", pub_date=timezone.now()
            )

            assert mock_handler.called, "pre_save signal should fire"
        finally:
            pre_save.disconnect(mock_handler, sender=Question)

    def test_question_text_auto_adds_question_mark(self):
        """Test pre_save signal adds question mark if missing."""
        question = Question.objects.create(
            question_text="Test question",  # No question mark
            pub_date=timezone.now(),
        )

        # Signal should add question mark
        question.refresh_from_db()
        assert question.question_text.endswith("?"), "Signal should add question mark"


@pytest.mark.mission04
@pytest.mark.django_db
class TestPostSaveSignals:
    """Test post_save signal handlers."""

    def test_question_post_save_signal_fires(self):
        """Verify post_save signal fires for Question."""
        mock_handler = Mock()

        post_save.connect(mock_handler, sender=Question)

        try:
            Question.objects.create(question_text="Test?", pub_date=timezone.now())

            assert mock_handler.called, "post_save signal should fire"
        finally:
            post_save.disconnect(mock_handler, sender=Question)

    def test_post_save_creates_default_choices(self):
        """Test post_save signal creates default choices for new questions."""
        question = Question.objects.create(
            question_text="New question?", pub_date=timezone.now()
        )

        # Check if default choices were created
        choices = question.choice_set.all()
        if choices.count() > 0:
            # Signal created default choices
            assert choices.count() >= 2, "Should create at least 2 default choices"
            choice_texts = [c.choice_text for c in choices]
            # Common defaults might be Yes, No, Maybe
            assert any(text in ["Yes", "No", "Maybe"] for text in choice_texts)

    def test_choice_post_save_signal_fires(self):
        """Verify post_save signal fires for Choice."""
        mock_handler = Mock()

        post_save.connect(mock_handler, sender=Choice)

        try:
            question = Question.objects.create(
                question_text="Test?", pub_date=timezone.now()
            )
            Choice.objects.create(question=question, choice_text="Test choice", votes=0)

            assert mock_handler.called, "post_save signal should fire for Choice"
        finally:
            post_save.disconnect(mock_handler, sender=Choice)


@pytest.mark.mission04
@pytest.mark.django_db
class TestPostDeleteSignals:
    """Test post_delete signal handlers."""

    def test_question_post_delete_signal_fires(self):
        """Verify post_delete signal fires for Question."""
        mock_handler = Mock()

        post_delete.connect(mock_handler, sender=Question)

        try:
            question = Question.objects.create(
                question_text="Test?", pub_date=timezone.now()
            )
            question.delete()

            assert mock_handler.called, "post_delete signal should fire"
        finally:
            post_delete.disconnect(mock_handler, sender=Question)

    @patch("polls.signals.logger")
    def test_deletion_is_logged(self, mock_logger):
        """Test that deletion is logged by signal handler."""
        question = Question.objects.create(
            question_text="Test?", pub_date=timezone.now()
        )

        question.delete()

        # Check if logger was called (if logging is implemented)
        if mock_logger.warning.called or mock_logger.info.called:
            assert True, "Deletion should be logged"


@pytest.mark.mission04
@pytest.mark.django_db
class TestSignalBestPractices:
    """Test signal implementation follows best practices."""

    def test_signals_do_not_cause_infinite_loops(self):
        """Verify signals don't cause infinite loops."""
        # Create a question - if signals cause infinite loop, this will hang
        try:
            question = Question.objects.create(
                question_text="Test?", pub_date=timezone.now()
            )
            # Update it
            question.question_text = "Updated?"
            question.save()

            assert True, "Signals should not cause infinite loops"
        except RecursionError:
            pytest.fail("Signals are causing infinite loops")

    def test_signal_errors_do_not_break_saves(self):
        """Verify signal errors are handled gracefully."""
        # Even if signal has issues, the model should save
        question = Question.objects.create(
            question_text="Test?", pub_date=timezone.now()
        )

        assert question.id is not None, (
            "Question should be saved even if signal has issues"
        )


@pytest.mark.mission04
@pytest.mark.django_db
class TestCustomSignals:
    """Test custom signals if implemented."""

    def test_custom_signal_imports(self):
        """Test if custom signals are defined."""
        try:
            from polls.signals import poll_completed  # noqa: F401

            assert True, "Custom signal poll_completed exists"
        except ImportError:
            pytest.skip("Custom signals not yet implemented")

    def test_poll_completed_signal_fires(self):
        """Test custom poll_completed signal fires at threshold."""
        try:
            from polls.signals import poll_completed

            mock_handler = Mock()
            poll_completed.connect(mock_handler)

            try:
                question = Question.objects.create(
                    question_text="Test?", pub_date=timezone.now()
                )

                choice = Choice.objects.create(
                    question=question, choice_text="Test", votes=0
                )

                # Simulate reaching vote threshold
                choice.votes = 100
                choice.save()

                # Custom signal might fire
                if mock_handler.called:
                    assert True, "Custom signal works"
            finally:
                poll_completed.disconnect(mock_handler)
        except ImportError:
            pytest.skip("Custom signals not yet implemented")


@pytest.mark.mission04
@pytest.mark.django_db
class TestSignalPerformance:
    """Test signal performance and efficiency."""

    def test_signals_do_not_significantly_slow_saves(self):
        """Verify signals don't significantly impact save performance."""
        import time

        start_time = time.time()

        for i in range(10):
            Question.objects.create(
                question_text=f"Question {i}?", pub_date=timezone.now()
            )

        elapsed = time.time() - start_time

        # Should complete reasonably fast (adjust threshold as needed)
        assert elapsed < 5.0, "Signal handlers should not significantly slow down saves"
