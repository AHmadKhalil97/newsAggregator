from django.db import models
from django.utils import timezone


# Create your models here.

class Source(models.Model):
    source_name = models.CharField(max_length=100)
    source_link = models.TextField()
    source_category = models.CharField(max_length=100)
    updated_date = models.DateField(default=timezone.now)


class Headline(models.Model):
    source = models.ForeignKey('newsScrapper.Source', related_name='news', on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    link = models.TextField()

    def __str__(self):
        return self.title
