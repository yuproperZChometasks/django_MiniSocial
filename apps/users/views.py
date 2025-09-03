from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User
from .forms import SignUpForm
from apps.subscriptions.forms import FollowForm
from apps.subscriptions.models import Subscription

class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("blog:feed")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ("first_name", "last_name", "email", "avatar")
    template_name = "users/profile_form.html"
    success_url = reverse_lazy("blog:feed")

    def get_object(self, queryset=None):
        return self.request.user
        
class ProfileDetailView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'users/profile_detail.html'
    fields = ('first_name', 'last_name', 'email', 'avatar')
    success_url = reverse_lazy('users:my_profile')

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['following'] = self.object.following_set.select_related('author')
        ctx['followers']  = self.object.followers_set.select_related('user')
        ctx['follow_form'] = FollowForm(user=self.object)
        return ctx

    def post(self, request, *args, **kwargs):
        form = FollowForm(request.POST, user=request.user)
        if form.is_valid():
            authors = form.cleaned_data['authors']
            Subscription.objects.bulk_create([
                Subscription(user=request.user, author=author)
                for author in authors
            ], ignore_conflicts=True)
        return super().post(request, *args, **kwargs)