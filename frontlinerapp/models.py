from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(null=True, blank=True)
    is_regularuser = models.BooleanField(default=False)
    is_adminuser = models.BooleanField(default=False)

    def __str__(self):
        return self.username