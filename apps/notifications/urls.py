from django.urls import path
from . import views

app_name = 'notifications'
urlpatterns = [
    path('', views.NotificationListView.as_view(), name='list'),
    path('mark/<int:pk>/', views.MarkAsReadView.as_view(), name='mark'),
    path('api/unread/', views.api_unread, name='api_unread'),
]

