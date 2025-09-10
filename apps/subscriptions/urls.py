from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('feed/', views.FeedView.as_view(), name='feed'),
    path('unfollow/<int:author_pk>/', views.UnsubscribeView.as_view(), name="unsubscribe"),

]
