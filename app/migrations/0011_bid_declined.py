# Generated by Django 4.2 on 2024-02-11 23:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_trainerprofile_number_of_jobs_trainerprofile_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='bid',
            name='declined',
            field=models.BooleanField(default=False),
        ),
    ]
