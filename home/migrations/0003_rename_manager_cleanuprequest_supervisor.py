# Generated by Django 5.0.4 on 2024-10-16 10:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_alter_cleanuprequest_requested_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cleanuprequest',
            old_name='manager',
            new_name='supervisor',
        ),
    ]