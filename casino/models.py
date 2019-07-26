from django.db import models
from django.contrib.auth.models import User


class CustomerUser(User):

    def __repr__(self):
        return f'{self.__class__.__name__} {self.username}'
