from django.db import models
from django.conf import settings
from django.utils import timezone

class Thread(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='thread_user1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='thread_user2')
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user1', 'user2'],
                name='unique_thread_pair'
            )
        ]

    def __str__(self):
        return f'{self.user1} ↔ {self.user2}'

    @classmethod
    def get_or_create_thread(cls, a, b):
        if a.pk > b.pk:
            a, b = b, a
        return cls.objects.get_or_create(user1=a, user2=b)

    def last_message(self):
        return self.messages.first()

    def unread_count(self, user):
        return self.messages.filter(sender__ne=user, is_read=False).count()


class Message(models.Model):
    thread = models.ForeignKey(Thread,
                               on_delete=models.CASCADE,
                               related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='sent_messages')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.sender}: {self.text[:30]}'