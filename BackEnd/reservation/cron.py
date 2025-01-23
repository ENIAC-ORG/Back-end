from datetime import datetime
from django.core.mail import send_mail
from django.utils.timezone import now
from django.urls import reverse
from .models import Reservation
from django.conf import settings
# from celery import shared_task
import logging

logger = logging.getLogger(__name__)


def check_and_send_feedback_email():
    """
    بررسی رزروهای گذشته و ارسال ایمیل یادآوری به پزشک.
    """

    reservations = Reservation.objects.filter(date__lt=now().date(), feedback__isnull=True,email_sent=False)
    for reservation in reservations:
        feedback_url = reverse('api_feedback', args=[reservation.id])
        full_url = f'{settings.WEBSITE_URL}{feedback_url}'
        send_mail(
            subject='یادآوری: ارسال فیدبک جلسه',
            message=(
                f'''دکتر {reservation.psychiatrist.get_fullname()} عزیز،
                لطفاً فیدبک جلسه مورخ {reservation.date} ساعت {reservation.time} را از طریق لینک زیر ثبت کنید:
                {full_url}'''
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[reservation.psychiatrist.user.email],
            fail_silently=False,
        )
        print( "hello " ) 
        logger.warning( f" here for email : {reservation.psychiatrist.user.email}" )
        reservation.email_sent = True
        reservation.save()


def scheduled_feedback_check():
    check_and_send_feedback_email()

