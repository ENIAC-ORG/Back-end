from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from BackEnd.settings import EMAIL_HOST,EMAIL_HOST_USER
from . import project_variables
import json


def send_verification_message(subject, recipient_list, verification_token, registration_tries, show_text , token):
    
    context = {
        'email_verification_token': verification_token,
        # 'remaining_text': remaining_text,
        'varification_link' : token ,
    }

    html_message = render_to_string( 'active_email.html', context=  context  )  #'activation_template.html'
    email = EmailMultiAlternatives(subject, '', EMAIL_HOST, recipient_list)
    email.attach_alternative(html_message, "text/html" )  #"text/html")
    email.send()


def send_forget_password_verification_message(subject, recipient_list, verification_token, verification_tries=None):
    context = {
        'email_verification_token': verification_token,
        # 'remaining_text': remaining_text,
    }

    html_message = render_to_string('forget_password.html', context)
    email = EmailMultiAlternatives(subject, '', EMAIL_HOST, recipient_list)
    email.attach_alternative(html_message, "text/html")
    email.send()


def send_GoogleMeet_Link(subject,recipient_list,psychiatrist_name,appointment_date,appointment_time,link ):
    context = {
    'GoogleMeetLink':link,
    'psychiatrist_name': psychiatrist_name,  
    'appointment_date': appointment_date,
    'appointment_time': appointment_time,
}
    html_message= render_to_string('GoogleMeetLink.html',context)
    email=EmailMultiAlternatives(subject,'',EMAIL_HOST_USER,recipient_list)
    email.attach_alternative(html_message,"text/html")
    email.send()
    

def send_telegram_account_verification_message(subject, recipient_list, verification_token):
    send_forget_password_verification_message( subject= subject , recipient_list= recipient_list , verification_token=verification_token )


