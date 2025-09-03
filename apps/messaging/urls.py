from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.DialogListView.as_view(), name='dialogs'),
    path('thread/<int:thread_pk>/', views.ChatView.as_view(), name='chat'),
    path('start/<int:user_pk>/', views.StartDialogView.as_view(), name='start'),
]