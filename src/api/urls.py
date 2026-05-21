from api.views.terminal_view import TerminalView
from api.views.task_view import TaskView
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from api.views.user_app import RegisterView, ProfileListView ,ProfileUpdateDeleteView

urlpatterns = [
    path('terminal/',TerminalView.as_view()),
    path('task/', TaskView.as_view()),

    path('api/auth/register/', RegisterView.as_view(), name='auth_register'),
    
    # Auth yo'llari
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/profile/',ProfileListView.as_view() ),
    path('api/profile1/<int:pk>/',ProfileUpdateDeleteView.as_view() ),
    
    
]