from api.views.terminal_view import TerminalView, NanoView, NanoSaveView
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from api.views.user_app import RegisterView

urlpatterns = [
    path('terminal/',TerminalView.as_view()),
    path('nano/',NanoView.as_view()),
    path('nano/save/',NanoSaveView.as_view()),

    
    # Auth yo'llari
    path('api/auth/register/', RegisterView.as_view(), name='auth_register'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # # Terminal yo'li
    # path('api/terminal/', include('apps.terminal.urls')),
]