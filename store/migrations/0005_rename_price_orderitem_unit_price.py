# Generated by Django 4.2.3 on 2023-07-18 01:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_remove_customer_fathers_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderitem',
            old_name='price',
            new_name='unit_price',
        ),
    ]
