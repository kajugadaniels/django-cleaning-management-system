# Generated by Django 5.0.4 on 2024-10-29 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_cleanuprequest_feedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='cleanuprequest',
            name='supervisor_report',
            field=models.FileField(blank=True, null=True, upload_to='reports/'),
        ),
    ]