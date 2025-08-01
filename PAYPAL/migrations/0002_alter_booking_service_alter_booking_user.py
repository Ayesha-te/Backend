# Generated by Django 5.2.1 on 2025-07-26 19:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PAYPAL', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_bookings', to='PAYPAL.service'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paypal_bookings', to=settings.AUTH_USER_MODEL),
        ),
    ]
