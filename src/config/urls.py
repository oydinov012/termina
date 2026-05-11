from django.contrib import admin
from django.urls import path, include


from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [

    # schema JSON
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),

    # Swagger UI
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # Redoc UI
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    path('admin/', admin.site.urls),
    path('', include('api.urls')),

]