# Generated by Django 5.1.4 on 2025-01-24 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ULM', '0007_auto_20250124_1419'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='tenant_id',
            field=models.IntegerField(default=0),
        ),
    ]
