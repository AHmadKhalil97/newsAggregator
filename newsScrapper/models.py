from django.db import models


# Create your models here.

class Headlines(models.Model):
    title = models.CharField(max_length=250)
    link = models.TextField()

    def __str__(self):
        return self.title
