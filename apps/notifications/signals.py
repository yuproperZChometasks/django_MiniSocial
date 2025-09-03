from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from apps.blog.models import Like, Comment
from apps.subscriptions.models import Subscription
from apps.messaging.models import Message
from .models import Notification

def create_notification(recipient, actor, verb, target):
    Notification.objects.get_or_create(
        recipient=recipient,
        actor=actor,
        verb=verb,
        target_ct=ContentType.objects.get_for_model(target),
        target_id=target.pk
    )

@receiver(post_save, sender=Like)
def like_notification(sender, instance, created, **kwargs):
    if created and instance.post.author != instance.user:
        create_notification(
            recipient=instance.post.author,
            actor=instance.user,
            verb=Notification.LIKE,
            target=instance.post
        )

@receiver(post_save, sender=Comment)
def comment_notification(sender, instance, created, **kwargs):
    if created and instance.post.author != instance.author:
        create_notification(
            recipient=instance.post.author,
            actor=instance.author,
            verb=Notification.COMMENT,
            target=instance.post
        )

@receiver(post_save, sender=Subscription)
def subscribe_notification(sender, instance, created, **kwargs):
    if created:
        create_notification(
            recipient=instance.author,
            actor=instance.user,
            verb=Notification.SUBSCRIBE,
            target=instance.author
        )

@receiver(post_save, sender=Message)
def message_notification(sender, instance, created, **kwargs):
    if created and instance.sender != instance.thread.user1 and instance.sender != instance.thread.user2:
        # отправляем партнёру
        partner = instance.thread.user1 if instance.sender == instance.thread.user2 else instance.thread.user2
        create_notification(
            recipient=partner,
            actor=instance.sender,
            verb=Notification.MESSAGE,
            target=instance
        )