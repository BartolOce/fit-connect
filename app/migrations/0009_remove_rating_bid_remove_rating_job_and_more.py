# Generated by Django 4.2 on 2024-02-10 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_alter_topup_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rating',
            name='bid',
        ),
        migrations.RemoveField(
            model_name='rating',
            name='job',
        ),
        migrations.RemoveField(
            model_name='rating',
            name='rated',
        ),
        migrations.RemoveField(
            model_name='rating',
            name='rater',
        ),
        migrations.RemoveField(
            model_name='dispute',
            name='job',
        ),
        migrations.AlterField(
            model_name='job',
            name='status',
            field=models.CharField(choices=[('accepted', 'Accepted'), ('published', 'Published')], default='published', max_length=100),
        ),
        migrations.DeleteModel(
            name='Message',
        ),
        migrations.DeleteModel(
            name='Rating',
        ),
    ]
