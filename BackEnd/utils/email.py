from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from BackEnd.settings import EMAIL_HOST, EMAIL_HOST_USER
from . import project_variables
import json


def send_verification_message(
    subject, recipient_list, verification_token, registration_tries, show_text, token
):

    context = {
        "email_verification_token": verification_token,
        # 'remaining_text': remaining_text,
        "varification_link": token,
    }

    html_message = render_to_string(
        "active_email.html", context=context
    )  #'activation_template.html'
    email = EmailMultiAlternatives(subject, "", EMAIL_HOST, recipient_list)
    email.attach_alternative(html_message, "text/html")  # "text/html")
    email.send()


def send_forget_password_verification_message(
    subject, recipient_list, verification_token, verification_tries=None
):
    context = {
        "email_verification_token": verification_token,
        # 'remaining_text': remaining_text,
    }

    html_message = render_to_string("forget_password.html", context)
    email = EmailMultiAlternatives(subject, "", EMAIL_HOST, recipient_list)
    email.attach_alternative(html_message, "text/html")
    email.send()


def send_GoogleMeet_Link(
    subject, recipient_list, psychiatrist_name, appointment_date, appointment_time, link
):
    context = {
        "GoogleMeetLink": link,
        "psychiatrist_name": psychiatrist_name,
        "appointment_date": appointment_date,
        "appointment_time": appointment_time,
    }
    html_message = render_to_string("GoogleMeetLink.html", context)
    email = EmailMultiAlternatives(subject, "", EMAIL_HOST_USER, recipient_list)
    email.attach_alternative(html_message, "text/html")
    email.send()


def send_telegram_account_verification_message(
    subject, recipient_list, verification_token
):
    send_forget_password_verification_message(
        subject=subject,
        recipient_list=recipient_list,
        verification_token=verification_token,
    )


def send_doctor_application_email(subject, recipient_list, pending_user):
    context = {
        "firstname": pending_user.firstname,
        "lastname": pending_user.lastname,
        "doctorate_code": pending_user.doctorate_code,
    }

    html_message = render_to_string("doctor_application_email.html", context)
    email = EmailMultiAlternatives(subject, "", EMAIL_HOST_USER, recipient_list)
    email.attach_alternative(html_message, "text/html")
    email.send()


def send_doctor_accept_email(subject, recipient_list, user):
    full_name = user.get_fullname().split()
    context = {
        "firstname": full_name[0],
        "lastname": full_name[1],
        "doctorate_code": user.doctorate_code,
    }

    html_message = render_to_string("doctor_accept_email.html", context)
    email = EmailMultiAlternatives(subject, "", EMAIL_HOST_USER, recipient_list)
    email.attach_alternative(html_message, "text/html")
    email.send()


def send_doctor_deny_email(subject, recipient_list,pending_user,message):
    
    context = {
        "firstname": pending_user.firstname,
        "lastname": pending_user.lastname,
        "doctorate_code": pending_user.doctorate_code,
        "number_of_application" : pending_user.number_of_application,
        "message" :message
    }

    html_message = render_to_string("doctor_deny_email.html", context)
    email = EmailMultiAlternatives(subject, "", EMAIL_HOST_USER, recipient_list)
    email.attach_alternative(html_message, "text/html")
    email.send()


# 1111
