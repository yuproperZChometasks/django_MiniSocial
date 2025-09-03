from django.db import models
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from django.conf import settings
from apps.users.models import User
from .models import Thread, Message
from .forms import MessageForm

class DialogListView(LoginRequiredMixin, ListView):
    model = Thread
    template_name = 'messaging/dialog_list.html'
    context_object_name = 'threads'

    def get_queryset(self):
        return Thread.objects.filter(
            models.Q(user1=self.request.user) |
            models.Q(user2=self.request.user)
        ).order_by('-updated')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        for t in ctx['threads']:
            t.last_msg = t.last_message()
            t.unread = t.messages.filter(is_read=False).exclude(sender=self.request.user).count()
        return ctx


class ChatView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'messaging/chat.html'

    def dispatch(self, request, *args, **kwargs):
        self.partner = get_object_or_404(Thread, pk=kwargs['thread_pk']).user1 \
            if Thread.objects.get(pk=kwargs['thread_pk']).user2 == request.user \
            else Thread.objects.get(pk=kwargs['thread_pk']).user2
        self.thread = Thread.objects.get(
            models.Q(user1=request.user, user2=self.partner) |
            models.Q(user1=self.partner, user2=request.user)
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['thread'] = self.thread
        ctx['partner'] = self.partner
        ctx['messages'] = self.thread.messages.select_related('sender')[:100][::-1]
        # отметим прочитанными
        self.thread.messages.filter(is_read=False).exclude(sender=self.request.user).update(is_read=True)
        return ctx

    def form_valid(self, form):
        form.instance.sender = self.request.user
        form.instance.thread = self.thread
        form.save()                       # ← было super().save(form)
        return redirect('messaging:chat', thread_pk=self.thread.pk)

class StartDialogView(LoginRequiredMixin, CreateView):
    """Создаёт Thread и перенаправляет в чат."""
    model = Message
    form_class = MessageForm
    template_name = 'messaging/start.html'

    def dispatch(self, request, *args, **kwargs):
        self.partner = get_object_or_404(User, pk=kwargs['user_pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        thread, _ = Thread.get_or_create_thread(self.request.user, self.partner)
        Message.objects.create(thread=thread,
                               sender=self.request.user,
                               text=form.cleaned_data['text'])
        return redirect('messaging:chat', thread_pk=thread.pk)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['partner'] = self.partner
        return ctx