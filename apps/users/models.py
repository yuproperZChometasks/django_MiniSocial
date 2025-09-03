from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    date_from = models.DateField(null=True, blank=True, verbose_name='Показывать посты с даты')
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):# -> str:         
        return self.username  # теперь с -> str:  в админке и лентах видно имя