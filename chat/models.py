from django.db import models

class InitialQuestion(models.Model):
    question = models.CharField(max_length=255)
    options = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.question
