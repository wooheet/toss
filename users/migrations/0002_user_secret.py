# Generated by Django 3.1.7 on 2021-04-04 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='secret',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]