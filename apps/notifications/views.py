from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView
from .models import Notification
from django.views import View

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = 5

    def get_queryset(self):
        return self.request.user.notifications.filter(is_read=False)[:5]

class MarkAsReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        note = get_object_or_404(Notification, pk=pk, recipient=request.user)
        note.is_read = True
        note.save()
        return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def api_unread(request):
    qs = request.user.notifications.filter(is_read=False)
    return JsonResponse({
        'count': qs.count(),
        'list': [
            {'actor': n.actor.username, 'verb': n.get_verb_display(), 'target': str(n.target)}
            for n in qs[:5]
        ]
    })