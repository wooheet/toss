# Generated by Django 3.1.7 on 2021-04-06 14:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20210406_0341'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='tag',
        ),
    ]