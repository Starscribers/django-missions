from django.contrib import messages
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import Choice, Question


class IndexView(generic.ListView):
    """
    Display the latest published poll questions.
    """

    template_name = "polls/index.html"
    context_object_name = "latest_question_list"
    paginate_by = 10

    def get_queryset(self):
        """Return the last ten published questions."""
        return Question.objects.order_by("-pub_date")[:10]


class DetailView(generic.DetailView):
    """
    Display a poll question with its choices for voting.
    """

    model = Question
    template_name = "polls/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_votes"] = self.object.total_votes()
        return context


class ResultsView(generic.DetailView):
    """
    Display the results of a poll question.
    """

    model = Question
    template_name = "polls/results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_votes"] = self.object.total_votes()
        return context


def vote(request, question_id):
    """
    Handle voting on a poll question.
    """
    question = get_object_or_404(Question, pk=question_id)

    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form with error message
        messages.error(request, "You didn't select a choice.")
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "total_votes": question.total_votes(),
            },
        )
    else:
        # Use F() to avoid race conditions
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        selected_choice.refresh_from_db()  # Get the updated vote count

        messages.success(
            request, f"Your vote for '{selected_choice.choice_text}' has been recorded!"
        )

        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data to prevent data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
