# Generated by Django 5.0.7 on 2024-08-08 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hmsys', '0004_payments_updated_amount_payments_updated_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='booked',
            name='aldults',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='booked',
            name='children',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
