from django.contrib import admin
from .models import Post, Like, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at")
    search_fields = ("title", "text")
    list_filter = ("created_at",)

admin.site.register(Like)
admin.site.register(Comment)
