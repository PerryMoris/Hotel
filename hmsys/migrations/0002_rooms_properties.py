# Generated by Django 5.0.7 on 2024-07-25 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hmsys', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rooms',
            name='properties',
            field=models.TextField(blank=True, null=True),
        ),
    ]
