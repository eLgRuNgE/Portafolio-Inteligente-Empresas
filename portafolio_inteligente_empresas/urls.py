from django.contrib import admin
from django.urls import path, include
from security.views import home_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', include('security.urls')),
    path('chat/', include('chat.urls')),
    path('', home_redirect, name='home'),
]



