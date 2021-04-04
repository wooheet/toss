# Generated by Django 3.1.7 on 2021-04-04 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_secret'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='secret',
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='email address'),
        ),
    ]
