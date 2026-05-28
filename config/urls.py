from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from tasks import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    #JWT Auth
    path('api/auth/login/',   TokenObtainPairView.as_view(),  name='login'),
    path('api/auth/logout/',  TokenBlacklistView.as_view(),   name='logout'),
    path('api/auth/refresh/', TokenRefreshView.as_view(),     name='token_refresh'),

    # All app routes (including register)
    path('api/', include('tasks.urls')),
]
