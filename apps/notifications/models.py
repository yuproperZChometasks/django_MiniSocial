from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone

class Notification(models.Model):
    RECIPIENT = 1
    LIKE      = 2
    COMMENT   = 3
    SUBSCRIBE = 4
    MESSAGE   = 5

    TYPE_CHOICES = (
        (RECIPIENT, 'recipient'),
        (LIKE, 'like'),
        (COMMENT, 'comment'),
        (SUBSCRIBE, 'subscribe'),
        (MESSAGE, 'message'),
    )

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  on_delete=models.CASCADE,
                                  related_name='notifications')
    actor     = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  on_delete=models.CASCADE,
                                  related_name='actor_notifications')
    verb      = models.PositiveSmallIntegerField(choices=TYPE_CHOICES)
    target_ct = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    target_id = models.PositiveIntegerField()
    target    = GenericForeignKey('target_ct', 'target_id')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read   = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['recipient', 'actor', 'verb', 'target_ct', 'target_id'],
                name='unique_notification'
            )
        ]

    def __str__(self):
        return f'{self.actor} {self.get_verb_display()} → {self.recipient}'