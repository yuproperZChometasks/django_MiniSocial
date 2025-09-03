from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('text',)
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))
    