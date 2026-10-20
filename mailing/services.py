from django.core.mail import send_mail
from django.utils import timezone
from .models import Attempt
import logging

# Настраиваем логгер, чтобы видеть ошибки в консоли
logger = logging.getLogger(__name__)


def send_mailing_service(mailing):
    """
    Сервис для отправки рассылки.
    Возвращает кортеж: (успешно_отправлено, всего_получателей)
    """
    now = timezone.now()

    # 1. Проверка времени
    if not (mailing.start_time <= now <= mailing.end_time):
        raise ValueError('Сейчас нельзя отправлять рассылку (время не подходит)')

    recipients = mailing.recipients.all()
    if not recipients:
        raise ValueError('У рассылки нет получателей')

    attempts_to_create = []
    success_count = 0

    # 2. Проходим по каждому получателю
    for recipient in recipients:
        try:
            # Отправляем письмо
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email='noreply@myservice.ru',  # Отправитель
                recipient_list=[recipient.email],
                fail_silently=False,  # Если ошибка — выбросит исключение
            )
            # Если всё ок — готовим запись об успехе
            attempts_to_create.append(Attempt(
                mailing=mailing,
                status='Успешно',
                server_response='OK (250 Accepted)'
            ))
            success_count += 1

        except Exception as e:
            # Если ошибка — логируем и готовим запись о неудаче
            logger.error(f"Ошибка отправки для {recipient.email}: {e}")
            attempts_to_create.append(Attempt(
                mailing=mailing,
                status='Не успешно',
                server_response=str(e)
            ))

    # 3. Сохраняем все попытки в базу ОДНИМ запросом (batch)
    Attempt.objects.bulk_create(attempts_to_create)

    return success_count, len(recipients)
