from .views import *
from django.urls import path


urlpatterns = [
    path('signup/' , SignUpView.as_view() , name='signup' ) ,
    path('activation_confirm/<str:token>/', ActivationConfirmView.as_view(), name='activation_confirm'),
    path('activation_resend/', ActivationResend.as_view(), name='activation_resend'),
    path('forgot_password/' , ForgotPassword.as_view() , name='forgot_password'),
    path('reset_password/<str:token>/', ResetPassword.as_view(), name='reset_password'),
    path('complete_info/' , CompleteInfoView.as_view() , name= 'complete_info') , 
    path('Login/',LoginView.as_view(),name='Login'),
    path('Logout/',LogoutView.as_view(),name='Logout'),
    path('change_password/' , ChangePasswordView.as_view() , name='change_password'),
    path('get_user/' , RetrieveUserData.as_view() , name='get_user'),
    path('doctorapplication/',DoctorApplicationView.as_view(),name='doctorapplication')
]
