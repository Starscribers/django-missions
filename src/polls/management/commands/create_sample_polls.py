from django.core.management.base import BaseCommand
from django.utils import timezone

from polls.models import Choice, Question


class Command(BaseCommand):
    help = "Create sample poll data for demonstration"

    def handle(self, *args, **options):
        # Clear existing data
        Question.objects.all().delete()

        # Create sample questions
        questions_data = [
            {
                "text": "What is the best programming language for space exploration?",
                "choices": ["Python", "JavaScript", "Rust", "C++", "Go"],
            },
            {
                "text": "Which planet should humans colonize first?",
                "choices": ["Mars", "Europa", "Titan", "Venus", "The Moon"],
            },
            {
                "text": "What is the most important Django feature?",
                "choices": [
                    "Admin Interface",
                    "ORM",
                    "URL Routing",
                    "Template System",
                    "Security Features",
                ],
            },
            {
                "text": "Best way to learn Django?",
                "choices": [
                    "Official Tutorial",
                    "Building Projects",
                    "Online Courses",
                    "Reading Documentation",
                    "Code Examples",
                ],
            },
            {
                "text": "Favorite space-themed movie?",
                "choices": [
                    "Interstellar",
                    "The Martian",
                    "Gravity",
                    "Star Wars",
                    "Star Trek",
                ],
            },
        ]

        for i, q_data in enumerate(questions_data):
            # Create question with different publication dates
            pub_date = timezone.now() - timezone.timedelta(days=i)
            question = Question.objects.create(
                question_text=q_data["text"], pub_date=pub_date
            )

            # Create choices with some random votes
            for j, choice_text in enumerate(q_data["choices"]):
                votes = max(0, (5 - j) * (i + 1) + (j * 2))  # Some variation in votes
                Choice.objects.create(
                    question=question, choice_text=choice_text, votes=votes
                )

            self.stdout.write(
                self.style.SUCCESS(f'Created question: "{question.question_text}"')
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {len(questions_data)} sample polls!"
            )
        )
