# Generated by Django 3.0.3 on 2020-03-21 05:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('newsScrapper', '0004_source_published_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='source',
            old_name='published_date',
            new_name='updated_date',
        ),
    ]