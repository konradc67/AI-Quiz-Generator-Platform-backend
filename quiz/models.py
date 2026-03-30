from django.db import models
from django.conf import settings
import uuid
from django.db import models

class User(models.Model):
    # Mapowanie kolumn dokładnie tak, jak masz w Neonie
    users_id = models.AutoField(primary_key=True)
    nickname = models.TextField()
    email = models.TextField()
    password = models.TextField()
    user_type = models.TextField()

    class Meta:
        db_table = 'users'  # Wymusza na Django szukanie tej konkretnej nazwy tabeli
        managed = False     # BARDZO WAŻNE: Wyłącza migracje Django dla tej tabeli

    def __str__(self):
        return self.nickname

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
        return f"{self.quiz.topic} - {self.text[:30]}..."

class Answer(models.Model):
    text = models.TextField(max_length=255)
    correct = models.BooleanField()
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers'
    )

