from django.urls import path
from .views import chat_home, chat_think

urlpatterns = [
    path('', chat_home, name='chat_home'),
    path('think/', chat_think, name='chat_think'),
]
