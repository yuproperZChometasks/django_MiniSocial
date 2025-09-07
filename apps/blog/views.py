from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Like, Comment
from .forms import PostForm, CommentForm
from django.http import JsonResponse, Http404, QueryDict
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging
from .models import Post, Comment
from .forms import CommentForm
#from django.views.generic.edit import CreateView
#from django.views.generic.edit import DeleteView, UpdateView




class FeedView(ListView):
    model = Post
    paginate_by = 3
    context_object_name = "posts"
    template_name = "blog/feed.html"

class MyFeedView(LoginRequiredMixin, ListView):
    model = Post
    paginate_by = 10
    context_object_name = "posts"
    template_name = "blog/feed.html"

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)  # type: ignore

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # 1) все комментарии поста
        comments_qs = self.object.comments.select_related('author')
        # 2) строим дерево: {parent_id: [comment, ...]}
        tree = {}
        for c in comments_qs:
            tree.setdefault(c.parent_id or 0, []).append(c)
        ctx['comments_tree'] = tree
        ctx['comment_form'] = CommentForm()
        return ctx

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    success_url = reverse_lazy("blog:feed")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_success_url(self):
        return reverse_lazy("blog:post_detail", kwargs={"pk": self.object.pk})

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy("blog:feed")

    def test_func(self):
        return self.get_object().author == self.request.user

class LikeToggleView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()
        return JsonResponse({"liked": created, "count": post.likes.count()})

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    http_method_names = ["post"]

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_obj
        parent_id = self.request.POST.get("parent")
        if parent_id:
            form.instance.parent = get_object_or_404(Comment, pk=parent_id, post=self.post_obj)
        self.object = form.save()
        return JsonResponse({
            "id": self.object.pk,
            "author": self.object.author.username,
            "text": self.object.text,
            "created_at": self.object.created_at.strftime('%d.%m %H:%M'),
            "total": self.post_obj.total_comments(),
        })

    def form_invalid(self, form):
        return JsonResponse({"error": form.errors}, status=400)


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment

    def test_func(self):
        return self.get_object().can_edit(self.request.user)

    def delete(self, request, *args, **kwargs):
        self.get_object().delete()
        return JsonResponse({})

class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    http_method_names = ["patch"]

    def test_func(self):
        return self.get_object().can_edit(self.request.user)

    def form_valid(self, form):
        self.object = form.save()
        return JsonResponse({"id": self.object.pk, "text": self.object.text})

    def form_invalid(self, form):
        return JsonResponse({"error": form.errors}, status=400)

