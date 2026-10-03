from django.urls import path
from . import views
from .views import RegisterView, UserView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    
)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path("register/", RegisterView.as_view(), name='register'),
    path("user/", UserView.as_view()),
]
