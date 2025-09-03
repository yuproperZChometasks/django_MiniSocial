from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.views.generic import ListView
from apps.blog.models import Post
from apps.users.models import User

class SearchView(ListView):
    template_name = 'search/results.html'
    paginate_by = 10
    context_object_name = 'results'

    def get_queryset(self):
        q = self.request.GET.get('q', '').strip()
        if not q:
            return Post.objects.none()

        tab = self.request.GET.get('tab', 'posts')

        if tab == 'posts':
            self.model = Post
            lookup = (
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(text__icontains=q)
            )
            qs = Post.objects.filter(lookup).order_by('-created_at')
        else:  # users
            from apps.users.models import User
            self.model = User
            lookup = (
                Q(username__icontains=q) |
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q)
            )
            qs = User.objects.filter(lookup).order_by('username')

        return qs.distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['query'] = self.request.GET.get('q', '')
        ctx['tab'] = self.request.GET.get('tab', 'posts')
        return ctx