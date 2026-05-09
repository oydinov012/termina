from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken # Token yaratish uchun
from django.contrib.auth import get_user_model
from api.serializer.user_app import RegisterSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save() # User yaratiladi va Signal ishlaydi (Workspace ochiladi)

        # Foydalanuvchi uchun qo'lda token yaratamiz
        refresh = RefreshToken.for_user(user)

        return Response({
            "user": serializer.data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "Foydalanuvchi va Workspace muvaffaqiyatli yaratildi."
        }, status=status.HTTP_201_CREATED)