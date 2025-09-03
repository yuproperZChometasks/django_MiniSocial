from django import forms
from apps.users.models import User
from .models import Subscription

class FollowForm(forms.Form):
    authors = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Выберите пользователей, на которых хотите подписаться:'
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # исключаем себя и уже подписанных
            self.fields['authors'].queryset = (
                User.objects
                    .exclude(pk=user.pk)
                    .exclude(pk__in=user.following_set.values('author'))
            )