"""
URL configuration for BackEnd project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from drf_yasg import openapi
from django.urls import re_path as url
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version='v1',
        description="API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact#snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny, ],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/" , include("accounts.urls")),
    path("HomePage/" , include("HomePage.urls")),
    path("reserve/" ,include("reservation.urls") ),
    path("googlemeet/",include("GoogleMeet.urls")),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('profile/' , include("Profile.urls")) , 
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('TherapyTests/' , include("TherapyTests.urls")),
    path('Rating/',include("Rating.urls")),
    path('DoctorPanel/',include("Doctorpanel.urls")),
    path('chat/', include("chat.urls")),
    path('depression-chat/' , include("depression_chat.urls") ),
     path('RecomendationSystem/', include("RecomendationSystem.urls")),
]

if settings.DEBUG:
    urlpatterns += [
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
    
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    