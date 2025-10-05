from django.contrib import admin

from .models import Choice, Question


class ChoiceInline(admin.TabularInline):
    """
    Inline admin for choices within a question.
    """

    model = Choice
    extra = 3  # Show 3 empty choice fields by default


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Admin configuration for Question model.
    """

    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ("Date information", {"fields": ["pub_date"], "classes": ["collapse"]}),
    ]
    inlines = [ChoiceInline]
    list_display = (
        "question_text",
        "pub_date",
        "was_published_recently",
        "total_votes",
    )
    list_filter = ["pub_date"]
    search_fields = ["question_text"]
    date_hierarchy = "pub_date"


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    """
    Admin configuration for Choice model.
    """

    list_display = ("choice_text", "question", "votes", "vote_percentage")
    list_filter = ["question__pub_date"]
    search_fields = ["choice_text", "question__question_text"]
    readonly_fields = ("vote_percentage",)

    def vote_percentage(self, obj):
        """Display vote percentage in admin."""
        return f"{obj.vote_percentage()}%"

    vote_percentage.short_description = "Vote %"
