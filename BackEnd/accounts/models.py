from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractBaseUser , BaseUserManager
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password
import logging

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    def create_user(self , email , firstname , lastname , gender , date_of_birth, phone_number ,password=None) :   #phone = None 
        """
        Creates and saves a User with the given email, 
        data of birth and password
        """
        if not email: 
            raise ValueError('User must have an email address')
        
        user = self.model(
            email = self.normalize_email(email),
            date_of_birth = date_of_birth,
            firstname = firstname , 
            lastname = lastname,
            gender= gender,
            phone_number = phone_number 
        )

        user.password = make_password(password)
        logger.warning( f"************* this is password {user.password} *****")
        user.save(using=self._db)
        return user
    
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset()
    
    def create_superuser(self , email ,password=None):   #phone  firstname ,lastname , gender , phone_number, date_of_birth , 
        """
        Creates and saves a superuser with the given email, birthdat
        and password.
        """
        user = self.create_user(
            email=email,
            password=password,
            date_of_birth="2000-3-3",
            firstname = "admin" , 
            lastname = "adminzadeh",
            gender= 'B',
            phone_number="+989999999999" 
        )

        user.is_admin = True
        user.is_superuser = True
        user.is_email_verified = True
        user.is_staff = True
        user.is_active = True
        user.role = User.TYPE_ADMIN
        user.save(using=self._db)
        return user

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        logger.warning( f"***** this is password {self.password} in save method")
        logger.warning("*****************************************************")

    def get_by_natural_key(self, email):
        return self.get(email=email)

class User(AbstractBaseUser):
    GENDER_Male = 'M'
    GENDER_Female = 'F'
    GENDER_BOTH = 'B'
    GENDER_CHOICES = [
        (GENDER_Female, 'Female'),
        (GENDER_Male, 'Male'),
        (GENDER_BOTH , 'Both')
    ]

    TYPE_USER = "user"
    TYPE_DOCTOR = "doctor"
    TYPE_ADMIN = "admin"
    TYPE_PENDING = "pending"

    CHOICES = (
        (TYPE_USER , "User") , 
        (TYPE_DOCTOR , "Doctor") , 
        (TYPE_ADMIN , "Admin"),
        (TYPE_PENDING,"Pending"),
    )

    firstname = models.CharField(max_length=20 , blank=True, null = True )
    lastname = models.CharField(max_length=30 , blank=True, null = True )
    
    email = models.EmailField(
        max_length= 255 , 
        unique = True,
    )
    USERNAME_FIELD = 'email'
    
    objects = UserManager()
    date_of_birth= models.DateField(blank=True , null = True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES ,null=True ) #  default = GENDER_BOTH,
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    phone_number_regex = r'^(?:\+98|0)(?:\s?)9[0-9]{9}$'
    phone_number_validator = RegexValidator(
        regex=phone_number_regex,
        message="Phone number must be in a valid Iranian format."
    )

    phone_number = models.CharField(
        max_length=15,  # Adjust the length as per your requirement
        validators=[phone_number_validator],
        blank=True,
        null=True
    )

    
    role = models.CharField( max_length=255, choices=CHOICES , default=TYPE_USER )
    # email varification 
    is_email_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=4, null=True, blank=True)
    verification_tries_count = models.IntegerField(default=0)
    # last_verification_sent = models.DateTimeField(null=True, blank=True, default=datetime.now())
    has_verification_tries_reset = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)  
    is_superuser = models.BooleanField(default=False)  
    
    def get_role(self ) : 
        return self.role
    
    def __str__(self):
        return self.email

    def has_perm(self , perm , obj=None ):
        "Does the user have a specific permisision?"
        return True
    
    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True


class Pending_doctor(models.Model): 
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING , unique=True)
    doctorate_code = models.CharField(max_length=50, blank=True,unique=True, null=True)
    firstname = models.CharField(max_length=20 , blank=True, null = True )
    lastname = models.CharField(max_length=30 , blank=True, null = True )
    number_of_application = models.IntegerField(default=5 )
