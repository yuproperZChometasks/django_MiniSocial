from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.FeedView.as_view(), name="feed"),
    path("my/", views.MyFeedView.as_view(), name="my_feed"),
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("post/create/", views.PostCreateView.as_view(), name="create_post"),
    path("post/<int:pk>/edit/", views.PostUpdateView.as_view(), name="update_post"),
    path("post/<int:pk>/delete/", views.PostDeleteView.as_view(), name="delete_post"),

    # API-лайки
    path("post/<int:pk>/like/", views.LikeToggleView.as_view(), name="like_api"),

    # Комментарии
    path("post/<int:pk>/comment/", views.CommentCreateView.as_view(), name="comment_api"),
    path("comment/<int:pk>/delete/", views.CommentDeleteView.as_view(), name="comment_delete"),
    path("comment/<int:pk>/update/", views.CommentUpdateView.as_view(), name="comment_update"),

]
