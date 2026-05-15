from tokenize import TokenError
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken 
from django.contrib.auth import get_user_model
from api.serializer.user_app import RegisterSerializer, UserSerializer
from apps.task.models import Profile  # Agar model kerak bo'lsa

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save() 

        refresh = RefreshToken.for_user(user)

        return Response({
            "user": serializer.data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "Foydalanuvchi va Workspace muvaffaqiyatli yaratildi."
        }, status=status.HTTP_201_CREATED)


class ProfileListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        # TO'G'RILANDI: request.id o'rniga request.user.id yozildi.
        # Faqat o'ziga tegishli User ma'lumotini ko'radi
        return User.objects.filter(id=self.request.user.id)


class ProfileUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all()

    def get_object(self):
        return self.request.user
    
    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)

        return Response(
            {
                "message":"user deleted! "
            }
        )
    