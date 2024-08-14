from django.urls import path
from .views import chat_home, chat_think, generate_pdf

urlpatterns = [
    path('', chat_home, name='chat_home'),
    path('think/', chat_think, name='chat_think'),
    path('generate_pdf/', generate_pdf, name='generate_pdf'),
]
