from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following_set'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers_set'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'], name='unique_subscription')
        ]

    def __str__(self):
        return f'{self.user} → {self.author}'
