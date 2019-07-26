from django.db import models
from django.contrib.auth.models import User


class CustomerUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __repr__(self):
        return f'{self.__class__.__name__} {self.user.username}'
