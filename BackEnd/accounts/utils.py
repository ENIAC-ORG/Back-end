from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import EmailMessage
import threading
from .models import User
import jwt
from datetime import datetime, timedelta
from django.conf import settings


def generate_tokens(user_id):
    u = User.objects.get(id=user_id)
    refresh = RefreshToken.for_user(u)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# def generate_tokens(user_id):
#     # Secret key from settings
#     secret_key = settings.SECRET_KEY

#     # Create expiration time for the token (e.g., 5 minutes from now)
#     expiration_time = datetime.utcnow() + timedelta(minutes=5)

#     # Payload for the token
#     payload = {
#         "user_id": user_id,
#         "exp": expiration_time,
#         "iat": datetime.utcnow(),
#         "token_type": "access",
#     }

#     # Generate the token
#     token = jwt.encode(payload, secret_key, algorithm="HS256")

#     return {"access": token}


class EmailThread(threading.Thread):
    def __init__(self, email_handler ,subject,recipient_list, verification_token, registration_tries, show_text , token ):
        super().__init__()
        self.email_handler = email_handler
        self.subject = subject
        self.recipient_list = recipient_list
        self.verification_token = verification_token
        self.registration_tries = registration_tries
        self.show_text = show_text
        self.access_token = token

    def run(self):
        self.email_handler.send_verification_message(
            subject=self.subject,
            recipient_list=self.recipient_list,
            verification_token=self.verification_token,
            registration_tries=self.registration_tries,
            show_text=self.show_text , 
            token = self.access_token 
        )
        print(f"Email sent to {self.recipient_list}")