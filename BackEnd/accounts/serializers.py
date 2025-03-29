from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()
from accounts.models import Pending_doctor
# from accounts.models import User

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import password_validation
from django.core import exceptions as exception
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["date_of_birth", "email" ,"gender","firstname" ,"lastname" , "phone_number" , "id" , "role"] #, "phone_number"]   , "role"

    def validate(self, attrs):
        return super().validate(attrs)


class CompleteInfoSerializer(serializers.ModelSerializer) : 
    
    class Meta:
        model = User 
        fields = ['firstname' , 'lastname' , 'phone_number' , 'date_of_birth','gender' ]
    
    def validate(self, attrs):
        return super().validate(attrs)       

class SignUpSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)
    password1 = serializers.CharField(
        style={'input_type': 'password'},
        validators=[password_validation.validate_password],
        write_only=True
    )
    is_doctor = serializers.BooleanField(default=False)
    class Meta:
        model = User
        fields = ('email','password1', 'password2','is_doctor' )                  
        extra_kwargs = {
            'password1': {'write_only': True},
            'password2': {'write_only': True},
        }
    
    def validate_email(self, value):
        user = User.objects.filter(email__iexact=value)
        if user.exists():
            user = user.first()
            if user.is_email_verified:
                raise serializers.ValidationError("Email already exists.")
            if user.phone_number != self.initial_data.get('phone_number'):
                raise serializers.ValidationError("Email already exists.")
            
        return str.lower(value)
    
    def validate_password2(self, value):
        
        if value != self.initial_data.get('password1'):
            raise serializers.ValidationError('Passwords must match.')
        return value
    
    def validate_password1(self, value):
        if value != self.initial_data.get('password2'):
            raise serializers.ValidationError('Passwords must match.')
        password_validation.validate_password(value)
        return value


class ActivationConfirmSerializer(serializers.Serializer):
    verification_code = serializers.CharField(max_length=4, min_length=4)


class ActivationResendSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get('email', None)
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"message": "user does not exist."})

        if user.is_email_verified:
            raise serializers.ValidationError({"message": "user with this email is already verified."})

        attrs['user'] = user
        return attrs



class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password1 = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password1']:
            raise serializers.ValidationError({
                'new_password1': ['Passwords must match.'],
            })
        try:
            validate_password(attrs['new_password'])
        except exception.ValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })
        return attrs

class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    verification_code = serializers.CharField(max_length=4, min_length=4)

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        if new_password != confirm_password:
            raise serializers.ValidationError("New password and confirm password do not match.")
        try:
            validate_password(new_password)
        except serializers.ValidationError as validation_error:
            raise serializers.ValidationError({"new_password": validation_error})
        return attrs


class LoginSerializer(serializers.Serializer):
    email=serializers.EmailField(
        label=("Email"),
    )
    password = serializers.CharField(
        label=("password"),
        style={"input_type": "password"},
        write_only=True
    )

    token = serializers.CharField(
        label =("Token"),
        read_only=True
    )

    def validate(self, attrs):
        User = get_user_model()
        email = attrs.get('email', None)
        password = attrs.get('password', None)
        if email and password:
            email = self.validate_email(email)
            user = User.objects.get(email__iexact=email)
            if not user.check_password(password):
                msg = 'Incorrect password.'
                raise serializers.ValidationError( { "message" : msg} , code='authorization')
            if not user.is_email_verified:
                raise serializers.ValidationError({"message": "User is not verified."})
            attrs['user'] = user
        else:
            msg = ('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')
        return attrs
        
    def validate_email(self, value):
        msg = 'Email does not exist.'
        user_exists = User.objects.filter(email__iexact=value).exists()

        if not user_exists:
            raise serializers.ValidationError( { "message" : msg} )
        return str.lower(value)
    
    
class DoctorApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        id = serializers.IntegerField()
        model = Pending_doctor
        fields = ['id', 'firstname', 'lastname', 'doctorate_code']

    def validate(self, attrs):
        if not attrs.get('firstname') or not attrs.get('lastname') or not attrs.get('doctorate_code'):
            raise serializers.ValidationError('All fields are required.')
        return attrs
    
