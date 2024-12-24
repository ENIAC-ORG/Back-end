from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, GenericAPIView
from .serializers import *
from .models import User
from .utils import generate_tokens, EmailThread
import random
from django.conf import settings
import utils.email as email_handler
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from counseling.models import Pationt
from .models import Pending_doctor
from rest_framework.permissions import AllowAny
import logging

logger = logging.getLogger(__name__)


class SignUpView(CreateAPIView):
    serializer_class = SignUpSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        email = self.normalize_email(validated_data["email"])
        is_doctor = validated_data.get("is_doctor", False)
        role = User.TYPE_PENDING if is_doctor else User.TYPE_USER
        
        # Generate verification code
        verification_code = self.generate_verification_code()
        
        # Create user
        user = self.create_user(
            email=email,
            password=validated_data["password1"],
            verification_code=verification_code,
            role=role,
        )

        # Create related models if needed
        if role != User.TYPE_PENDING:
            self.create_patient(user)
        # logger.warning(f"*********************************************** here role : {role}")
        # if role == User.TYPE_PENDING : 
        #     logger.warning(f"***********************444444444444444444444444444 here role : {role}")
        #     pending= Pending_doctor.objects.create(
        #         user = user 
        #     )
        # Generate token for email verification
        token = self.generate_verification_token(user)

        # Send verification email
        self.send_verification_email(
            user=user,
            verification_code=verification_code,
            token=token,
        )

        # Prepare response data
        user_data = {
            "user": UserSerializer(user).data,
            "message": "User created successfully. Please check your email to activate your account.",
            "code": verification_code,
            "url": f"http://46.249.100.141:8070/accounts/activation_confirm/{token}/",
        }
        return Response(user_data, status=status.HTTP_201_CREATED)

    # Helper methods for better testability
    def normalize_email(self, email):
        """Normalize the email to lowercase."""
        return str.lower(email)

    def generate_verification_code(self):
        """Generate a random verification code."""
        return str(random.randint(1000, 9999))

    def create_user(self, email, password, verification_code, role):
        """Create and return a user."""
        return User.objects.create(
            email=email,
            password=make_password(password),
            verification_code=verification_code,
            verification_tries_count=1,
            role=role,
        )

    def create_patient(self, user):
        """Create a Patient record for the user."""
        Pationt.objects.create(user=user)

    def generate_verification_token(self, user):
        """Generate an access token for the user."""
        return generate_tokens(user.id)["access"]

    def send_verification_email(self, user, verification_code, token):
        """Send the verification email using a thread."""
        subject = "تایید ایمیل ثبت نام"
        show_text = (
            user.has_verification_tries_reset or user.verification_tries_count > 1
        )
        email_thread = EmailThread(
            email_handler,
            subject=subject,
            recipient_list=[user.email],
            verification_token=verification_code,
            registration_tries=user.verification_tries_count,
            show_text=show_text,
            token=token,
        )
        email_thread.start()


class ActivationConfirmView(GenericAPIView):
    serializer_class = ActivationConfirmSerializer
    permission_classes = []

    def get(self, request, *args, **kwargs):
        return render(request, "varify_email.html")

    def post(self, request, token):
        token = self.validate_token(token)
        if not token:
            return Response(
                {"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.get_user_from_token(token)
        if not user:
            return Response(
                {"message": "Invalid user"}, status=status.HTTP_400_BAD_REQUEST
            )

        if request.data.get("verification_code") != user.verification_code:
            return Response(
                {"message": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST
            )

        user.is_email_verified = True
        user.verification_code = None
        user.save()
        return Response({"message": "successfully verified"}, status=status.HTTP_200_OK)

    def get_user_from_token(self, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            if not payload: 
                return None
            user_id = payload.get("user_id")
            return User.objects.filter(id=user_id).first()
        except (ExpiredSignatureError, InvalidSignatureError):
            return None

    def validate_token(self, token):
        try:
            jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            return token
        except ExpiredSignatureError:
            return None
        except InvalidSignatureError:
            return None


class ActivationResend(GenericAPIView):
    serializer_class = ActivationResendSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            subject = "تایید ایمیل ثبت نام"
            verification_code = str(random.randint(1000, 9999))
            user.verification_tries_count += 1
            user.verification_code = verification_code
            # user.last_verification_sent = datetime.now()
            user.save()
            show_text = (
                user.has_verification_tries_reset or user.verification_tries_count > 1
            )
            token = generate_tokens(user.id)["access"]
            email_handler.send_verification_message(
                subject=subject,
                recipient_list=[user.email],
                verification_token=verification_code,
                registration_tries=user.verification_tries_count,
                show_text=show_text,
                token=token,
            )
            return Response(
                {
                    "message": "email sent",
                    "url": f"{settings.WEBSITE_URL}accounts/activation_confirm/{token}/",
                    "code": verification_code,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = request.user
            
            old_password = serializer.validated_data["old_password"]
            new_password = serializer.validated_data["new_password"]
            
            # Check if the current password matches the user's actual password
            if not user.check_password(old_password):
                return Response(
                    {"error": "Invalid current password."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Change the user's password
            user.set_password(new_password)
            user.save()

            return Response(
                {"message": "Password changed successfully."}, status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPassword(GenericAPIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = str.lower(serializer.validated_data["email"])
            users = User.objects.filter(email__iexact=email)
            if users.exists():
                user = users.first()
                subject = "فراموشی رمز عبور"
                verification_code = str(random.randint(1000, 9999))
                user.verification_tries_count += 1
                user.verification_code = verification_code
                # user.last_verification_sent = datetime.now()
                user.save()
                token = generate_tokens(user.id)["access"]
                email_handler.send_forget_password_verification_message(
                    subject=subject,
                    recipient_list=[user.email],
                    verification_token=verification_code,
                    verification_tries=user.verification_tries_count,
                )
                return Response(
                    {
                        "message": "email sent",
                        "url": f"{settings.WEBSITE_URL}accounts/reset_password/{token}/",
                        "code": verification_code,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPassword(GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request, token):
        token = self.validate_token(token)
        if not token:
            return Response(
                {"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_user_from_token(token)
        if not user:
            return Response(
                {"message": "Invalid user"}, status=status.HTTP_400_BAD_REQUEST
            )

        if serializer.validated_data["verification_code"] != user.verification_code:
            return Response(
                {"message": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST
            )
        user.verification_code = None
        new_password = serializer.validated_data["new_password"]
        user.set_password(new_password)
        user.save()
        return Response(
            {"message": "password successfully update"},
            status=status.HTTP_204_NO_CONTENT,
        )

    def get_user_from_token(self, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            return User.objects.filter(id=user_id).first()
        except ExpiredSignatureError:
            return None

    def validate_token(self, token):
        try:
            jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            return token
        except ExpiredSignatureError:
            return None
        except InvalidSignatureError:
            return None


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        if user is not None:
            tokens = generate_tokens(user.id)
            # login(request, user)
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return Response(
                {
                    "refresh": tokens["refresh"],
                    "access": tokens["access"],
                    "user": UserSerializer(user).data,
                }
            )
        return Response(
            {"message": "there is no user with this email"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class RetrieveUserData(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        print(request.headers["Authorization"])
        if not hasattr(request, "user"):
            return Response(
                {"message": "request does not have proper authentication tokens"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        email = str.lower(request.user.email)
        user = User.objects.filter(email__iexact=email)
        if not user.exists():
            return Response(
                {"message": "Invalid user"}, status=status.HTTP_400_BAD_REQUEST
            )
        user = user.first()
        data = {"user": UserSerializer(user).data}
        return Response(data=data, status=status.HTTP_200_OK)


class CompleteInfoView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompleteInfoSerializer

    def post(self, request):
        serializer = CompleteInfoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        email = str.lower(request.user.email)
        user = User.objects.filter(email__iexact=email)
        if not user.exists():
            return Response(
                {"message": "Invalid user"}, status=status.HTTP_400_BAD_REQUEST
            )
        user = user.first()
        user.firstname = validated_data["firstname"]
        user.gender = validated_data["gender"]
        user.lastname = validated_data["lastname"]
        user.date_of_birth = validated_data["date_of_birth"]
        user.phone_number = validated_data["phone_number"]
        user.save()
        return Response(
            data={"message": "successfully updated"}, status=status.HTTP_200_OK
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                data={"detail": "Not logged in"}, status=status.HTTP_401_UNAUTHORIZED
            )       
        refresh_token = request.COOKIES.get("token")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                return Response(
                    data={"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
                )
            response = Response(
                data={"detail": "Logged out successfully"}, status=status.HTTP_200_OK
            )
            response.delete_cookie("refresh_token")
            response.delete_cookie("access_token")
            response.cookies.pop("refresh_token", None)
            response.cookies.pop("access_token", None)
            return response

        logout(request)
        return Response(
            data={"detail": "Logged out successfully"}, status=status.HTTP_200_OK
        )


class DoctorApplicationView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DoctorApplicationSerializer

    def post(self, request):
        user = request.user
        # user = User.objects.filter(email = "doctor7@gmail.com").first()
    
        if user.role != User.TYPE_PENDING:
            return Response(
                {"message": "Only pending users can apply as doctors."},
                status=status.HTTP_403_FORBIDDEN,
            )
        logger.info(f"this is user {str(user)}")
        serializer = DoctorApplicationSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data

            # Update the user's information with validated data
            logger.warning(f"this is data******************************* {request.data}")
            user.firstname = validated_data["firstname"]
            user.lastname = validated_data["lastname"]

            pending_doctor = Pending_doctor.objects.create(
                firstname=validated_data["firstname"],
                lastname=validated_data["lastname"],
                user=user,
                doctorate_code = validated_data["doctorate_code"], 
            )
            pending_doctor.save()
            
            subject = ". درخواست شما در حال بررسی است"
            email_handler.send_doctor_application_email(
                subject=subject, recipient_list=[user.email], pending_user=pending_doctor
            )
            logger.warning(f" 888888888888888888888888******************************* {request.data}")
            return Response(
                {"message": "Application submitted. Awaiting admin approval."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


