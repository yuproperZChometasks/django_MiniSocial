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

@login_required
@require_POST
@csrf_exempt
def like_api(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
    return JsonResponse({"liked": created, "count": post.likes.count()})

@login_required
@require_POST
@csrf_exempt
def comment_api(request, pk):
    """Создание комментария (и ответа)."""
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        parent_id = request.POST.get("parent")
        if parent_id:
            comment.parent = get_object_or_404(Comment, pk=parent_id, post=post)
        comment.save()
        return JsonResponse({
            "id": comment.pk,
            "author": comment.author.username,
            "text": comment.text,
            "created_at": comment.created_at.strftime('%d.%m %H:%M'),
            "total": post.total_comments(),
            "can_edit": comment.can_edit(request.user)
        })
    return JsonResponse({"error": form.errors}, status=400)

@login_required
@require_http_methods(["PATCH", "DELETE"])
@csrf_exempt
def comment_detail_api(request, pk):
    """Редактирование / удаление комментария."""
    comment = get_object_or_404(Comment, pk=pk)
    if not comment.can_edit(request.user):
        return JsonResponse({"error": "Forbidden"}, status=403)

    if request.method == "PATCH":
        data = QueryDict(request.body)
        form = CommentForm(data, instance=comment)
        if form.is_valid():
            comment = form.save()
            return JsonResponse({"id": comment.pk, "text": comment.text})
        return JsonResponse({"error": form.errors}, status=400)

    if request.method == "DELETE":
        post = comment.post
        comment.delete()
        return JsonResponse({"total": post.total_comments()})

