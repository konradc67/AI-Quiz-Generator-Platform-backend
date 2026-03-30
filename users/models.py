from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Uczeń'
        TEACHER = 'TEACHER', 'Nauczyciel'
        COLLEGIAN = 'COLLEGIAN', 'Student'
        OTHER = 'OTHER', 'Inne'

    country = models.CharField(max_length=50)
    premium = models.BooleanField(default=False)
    points = models.PositiveIntegerField(default=0)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT
    )