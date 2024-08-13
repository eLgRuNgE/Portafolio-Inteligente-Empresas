from django.contrib import admin
from .models import InitialQuestion

@admin.register(InitialQuestion)
class InitialQuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'options',)
