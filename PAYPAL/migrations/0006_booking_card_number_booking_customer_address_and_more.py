# Generated by Django 5.2.1 on 2025-07-28 09:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PAYPAL', '0005_alter_service_created_at_delete_document'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='card_number',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='booking',
            name='customer_address',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='booking',
            name='customer_email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='booking',
            name='customer_first_name',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='booking',
            name='customer_last_name',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='booking',
            name='customer_phone',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='booking',
            name='cvv',
            field=models.CharField(blank=True, max_length=5),
        ),
        migrations.AddField(
            model_name='booking',
            name='expiry_date',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name='booking',
            name='mot_class',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='booking',
            name='name_on_card',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='booking',
            name='payment_method',
            field=models.CharField(default='card', max_length=10),
        ),
        migrations.AddField(
            model_name='booking',
            name='vehicle_make',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='booking',
            name='vehicle_mileage',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='booking',
            name='vehicle_model',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='booking',
            name='vehicle_registration',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='booking',
            name='vehicle_year',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name='service',
            name='code',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='booking',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to=settings.AUTH_USER_MODEL),
        ),
    ]
