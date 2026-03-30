from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Uczeń'
        TEACHER = 'TEACHER', 'Nauczyciel'
        COLLEGIAN = 'COLLEGIAN', 'Student'
        OTHER = 'OTHER', 'Inne'

    # Podpinamy Twój dziwny klucz z Neona pod to, czego oczekuje Django
    id = models.AutoField(primary_key=True, db_column='users_id')

    country = models.CharField(max_length=50)
    premium = models.BooleanField(default=False)
    points = models.PositiveIntegerField(default=0)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT
    )

    class Meta:
        db_table = 'user'  # <--- TO NAPRAWIA BŁĄD. Mówi Django: szukaj tabeli "User"