# Generated by Django 5.0.4 on 2024-09-19 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_cleanuprequest_created_at_cleanuprequest_updated_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='description',
        ),
        migrations.AddField(
            model_name='task',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
