from django.urls import path
from . import views

app_name = 'search'
urlpatterns = [
    #  path("search", views.SearchView.as_view(), name="search"),
        path('', views.SearchView.as_view(), name='index'),
]

