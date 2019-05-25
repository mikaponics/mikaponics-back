# Generated by Django 2.2.1 on 2019-05-25 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0009_production_inspections_started_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='production',
            name='inspections_started_at',
        ),
        migrations.AddField(
            model_name='production',
            name='inspections_start_at',
            field=models.DateTimeField(blank=True, help_text="The date/time this production's inspections will start.", null=True, verbose_name='Inspections start at'),
        ),
    ]
