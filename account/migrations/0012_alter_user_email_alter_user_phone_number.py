# Generated by Django 5.0.4 on 2024-12-02 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0011_alter_user_address_alter_user_email_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(default=1, max_length=254, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(default=2, max_length=15, unique=True),
            preserve_default=False,
        ),
    ]
