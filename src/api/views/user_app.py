from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken 
from django.contrib.auth import get_user_model
from api.serializer.user_app import RegisterSerializer, UserSerializer, ProfilSerailizer
from apps.task.models import Profile

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save() 

        # 🟢 TO'G'RILANDI: Ro'yxatdan o'tishi bilan unga avtomatik bo'sh profil ochiladi
        Profile.objects.get_or_create(user=user)

        refresh = RefreshToken.for_user(user)

        return Response({
            "user": serializer.data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "Foydalanuvchi va Workspace muvaffaqiyatli yaratildi."
        }, status=status.HTTP_201_CREATED)


class ProfileListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfilSerailizer

    def get_queryset(self):
        # 🔴 JIDDIY XATO TUZATILDI: .get() o'rniga .filter() bo'lishi shart!
        # Chunki ListAPIView massiv ko'rinishida ma'lumot kutadi.
        return Profile.objects.filter(user=self.request.user)

class ProfileUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Foydalanuvchi hisobi muvaffaqiyatli o'chirildi!"},
            status=status.HTTP_200_OK
        )