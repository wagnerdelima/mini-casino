from django.db import models


class CustomerUser(models.Model):
    username = models.CharField(
        max_length=10,
        blank=False,
        null=False,
        help_text='Customer username',
    )

    password = models.CharField(
        max_length=10,
        blank=False,
        null=False,
        help_text='Customer password',
    )

    def __repr__(self):
        return f'{self.__class__.__name__} {self.username}'
