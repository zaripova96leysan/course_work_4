from django.shortcuts import render, redirect
from .models import Recipient, Message, Mailing
from .forms import RecipientForm, MessageForm, MailingForm
from .services import send_mailing_service
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.cache import cache_page


def recipient_list(request):
    if request.user.is_authenticated:
        recipients = Recipient.objects.filter(owner=request.user)
    else:
        recipients = Recipient.objects.none()
    return render(request, 'mailing/recipient_list.html', {'recipients': recipients})



def recipient_create(request):
    if request.method == 'POST':
        form = RecipientForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            return redirect('recipient_list')
    else:
        form = RecipientForm()

    return render(request, 'mailing/recipient_form.html', {'form': form})

def recipient_delete(request, pk):
    recipient = Recipient.objects.get(id=pk)
    if request.method == 'POST':
        recipient.delete()
        return redirect('recipient_list')
    return render(request, 'mailing/recipient_confirm_delete.html', {'recipient': recipient})


def recipient_update(request, pk):

    recipient = Recipient.objects.get(id=pk)

    if request.method == 'POST':

        form = RecipientForm(request.POST, instance=recipient)
        if form.is_valid():
            form.save()
            return redirect('recipient_list')
    else:

        form = RecipientForm(instance=recipient)

    return render(request, 'mailing/recipient_form.html', {'form': form})

def message_list(request):
    if request.user.is_authenticated:
        messages = Message.objects.filter(owner=request.user)
    else:
        messages = Message.objects.none()
    return render(request, 'mailing/message_list.html', {'messages': messages})

def message_create(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            return redirect('message_list')
    else:
        form = MessageForm()
    return render(request, 'mailing/message_form.html', {'form': form})

def message_update(request, pk):
    message = Message.objects.get(id=pk)
    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            return redirect('message_list')
    else:
        form = MessageForm(instance=message)
    return render(request, 'mailing/message_form.html', {'form': form})

def message_delete(request, pk):
    message = Message.objects.get(id=pk)
    if request.method == 'POST':
        message.delete()
        return redirect('message_list')
    return render(request, 'mailing/message_confirm_delete.html', {'message': message})


def mailing_list(request):
    if request.user.is_authenticated:
        mailings = Mailing.objects.filter(owner=request.user)
    else:
        mailings = Mailing.objects.none()

    for mailing in mailings:
        mailing.update_status()

    return render(request, 'mailing/mailing_list.html', {'mailings': mailings})

def mailing_create(request):
    if request.method == 'POST':
        form = MailingForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            return redirect('mailing_list')
    else:
        form = MailingForm()
    return render(request, 'mailing/mailing_form.html', {'form': form})

def mailing_update(request, pk):
    mailing = Mailing.objects.get(id=pk)
    if request.method == 'POST':
        form = MailingForm(request.POST, instance=mailing)
        if form.is_valid():
            form.save()
            return redirect('mailing_list')
    else:
        form = MailingForm(instance=mailing)
    return render(request, 'mailing/mailing_form.html', {'form': form})

def mailing_delete(request, pk):
    mailing = Mailing.objects.get(id=pk)
    if request.method == 'POST':
        mailing.delete()
        return redirect('mailing_list')
    return render(request, 'mailing/mailing_confirm_delete.html', {'mailing': mailing})


def mailing_send(request, pk):
    mailing = get_object_or_404(Mailing, id=pk)

    if request.method == 'POST':
        try:
            success, total = send_mailing_service(mailing)
            messages.success(request, f'Рассылка завершена! Отправлено: {success} из {total}')
        except ValueError as e:
            messages.error(request, str(e))

        return redirect('mailing_list')


    return render(request, 'mailing/mailing_send_confirm.html', {'mailing': mailing})


@cache_page(60 * 1)  # Кешируем страницу на 1 минуту
def home(request):
    now = timezone.now()

    if request.user.is_authenticated:
        total_mailings = Mailing.objects.filter(owner=request.user).count()
        active_mailings = Mailing.objects.filter(
            owner=request.user,
            start_time__lte=now,
            end_time__gte=now,
            status='Запущена'
        ).count()
        unique_recipients = Recipient.objects.filter(owner=request.user).count()
    else:
        total_mailings = 0
        active_mailings = 0
        unique_recipients = 0

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'unique_recipients': unique_recipients,
    }

    return render(request, 'mailing/home.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'mailing/register.html', {'form': form})