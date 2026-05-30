from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    
    #JWT Auth
    path('api/auth/login/',   TokenObtainPairView.as_view(),  name='login'),
    path('api/auth/logout/',  TokenBlacklistView.as_view(),   name='logout'),
    path('api/auth/refresh/', TokenRefreshView.as_view(),     name='token_refresh'),

    # All app routes (including register)
    path('api/', include('tasks.urls')),
    
    #API Schema + Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
