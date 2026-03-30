from django.db import models
from django.contrib.auth.models import AbstractUser
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