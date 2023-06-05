from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        "username",
        max_length=140,
        unique=True,
    )
    email = models.EmailField(max_length=250, unique=True)
    first_name = models.CharField("first name", max_length=150, null=False)
    last_name = models.CharField("last name", max_length=150, null=False)
    recipe_count = models.IntegerField(default=0)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ["-id"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
