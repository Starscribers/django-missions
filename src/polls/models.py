import datetime

from django.contrib import admin
from django.db import models
from django.utils import timezone


class Question(models.Model):
    """
    A poll question that users can vote on.
    """

    question_text = models.CharField(
        max_length=200, help_text="The question being asked"
    )
    pub_date = models.DateTimeField(
        "date published",
        default=timezone.now,
        help_text="When this question was published",
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Poll Question"
        verbose_name_plural = "Poll Questions"

    def __str__(self):
        return self.question_text

    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Published recently?",
    )
    def was_published_recently(self):
        """
        Returns True if the question was published within the last day.
        """
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def total_votes(self):
        """
        Returns the total number of votes for this question.
        """
        return sum(choice.votes for choice in self.choice_set.all())


class Choice(models.Model):
    """
    A choice for a poll question.
    """

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        help_text="The question this choice belongs to",
    )
    choice_text = models.CharField(max_length=200, help_text="The choice text")
    votes = models.IntegerField(default=0, help_text="Number of votes for this choice")

    class Meta:
        ordering = ["-votes", "choice_text"]
        verbose_name = "Poll Choice"
        verbose_name_plural = "Poll Choices"

    def __str__(self):
        return f"{self.choice_text} ({self.votes} votes)"

    def vote_percentage(self):
        """
        Returns the percentage of votes this choice has received for its question.
        """
        total = self.question.total_votes()
        if total == 0:
            return 0
        return round((self.votes / total) * 100, 1)
