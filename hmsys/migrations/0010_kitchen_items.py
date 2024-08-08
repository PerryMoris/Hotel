# Generated by Django 5.0.7 on 2024-08-08 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hmsys', '0009_payments_created_amount'),
    ]

    operations = [
        migrations.CreateModel(
            name='Kitchen_Items',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='room_images/')),
                ('name', models.CharField(max_length=255, null=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
            ],
        ),
    ]
