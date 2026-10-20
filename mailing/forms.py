from django import forms
from .models import Recipient, Message, Mailing
from django.core.exceptions import ValidationError
from django.utils import timezone

class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ['email', 'full_name', 'comment']

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']

class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['start_time', 'end_time', 'message', 'recipients']
        # Виджеты для красивого выбора даты и времени
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    # Метод валидации
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and start_time < timezone.now():
            raise ValidationError('Дата начала не может быть в прошлом!')

        if start_time and end_time and start_time >= end_time:
            raise ValidationError('Дата начала должна быть раньше даты окончания!')

        return cleaned_data