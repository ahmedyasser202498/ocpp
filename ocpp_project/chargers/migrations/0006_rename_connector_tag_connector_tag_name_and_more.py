# Generated by Django 5.1.7 on 2025-03-22 11:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chargers', '0005_charger_id_tag_connector'),
    ]

    operations = [
        migrations.RenameField(
            model_name='connector',
            old_name='connector_tag',
            new_name='tag_name',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='charger',
        ),
        migrations.AddField(
            model_name='transaction',
            name='connector',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='chargers.connector'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transaction',
            name='meter_start',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='meter_stop',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
