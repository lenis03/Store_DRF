# Generated by Django 4.2.3 on 2023-07-18 01:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_create_store_models'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='price',
            new_name='unit_price',
        ),
    ]
