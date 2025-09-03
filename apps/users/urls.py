from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("profile/", views.ProfileUpdateView.as_view(), name="profile_update"),
    path("profile/<int:pk>/", views.ProfileDetailView.as_view(), name="profile"),
    path('profile/me/', views.ProfileDetailView.as_view(), name='my_profile'),
]