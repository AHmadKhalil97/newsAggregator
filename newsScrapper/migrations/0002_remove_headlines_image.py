# Generated by Django 2.2.5 on 2020-02-20 14:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('newsScrapper', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='headlines',
            name='image',
        ),
    ]