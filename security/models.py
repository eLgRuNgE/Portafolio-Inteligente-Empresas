from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models

class User(AbstractUser, PermissionsMixin):
    TYPE_IDENTIFICATION_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
        ('TI', 'Tarjeta de Identidad'),
        ('PA', 'Pasaporte'),
    ]
    first_name = models.CharField(max_length=255, blank=True, null=True, default='')
    last_name = models.CharField(max_length=255, blank=True, null=True, default='')
    type_identification = models.CharField(max_length=2, choices=TYPE_IDENTIFICATION_CHOICES)
    identification = models.CharField(max_length=50, blank=True, null=True, default='')
    email = models.EmailField(unique=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    mod_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'security_user'

    def __str__(self):
        return self.username
