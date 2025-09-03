from datetime import date
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from apps.blog.models import Post

class FeedView(LoginRequiredMixin, ListView):
    model = Post
    paginate_by = 10
    template_name = 'blog/feed.html'
    context_object_name = 'posts'

    def get_queryset(self):
        start = self.request.user.date_from or date(1970, 1, 1)
        return self.model._default_manager.filter(
            author__followers_set__user=self.request.user,
            created_at__gte=start
        ).distinct().order_by('-created_at')

