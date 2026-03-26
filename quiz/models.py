from django.db import models
from django.conf import settings
import uuid

class Quiz(models.Model):
    topic = models.CharField(max_length=50)
    created_at = models.DateField(auto_now_add=True)
    questions_count = models.PositiveIntegerField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='quizzes'
    )

    def __str__(self):
        return self.topic

class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField(max_length=255)
    answers_count = models.PositiveIntegerField()
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )

    def __str__(self):
        return f"{self.quiz.topic} - {self.content[:30]}..."

class Answer(models.Model):
    text = models.TextField(max_length=255)
    correct = models.BooleanField()
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers'
    )

