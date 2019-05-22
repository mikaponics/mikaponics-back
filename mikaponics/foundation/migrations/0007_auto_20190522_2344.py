# Generated by Django 2.2.1 on 2019-05-22 23:44

import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0006_auto_20190522_1955'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceSimulator',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('is_running', models.BooleanField(blank=True, default=True, help_text='Controls whether the simulator is running or not.', verbose_name='Is Running')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified_at', models.DateTimeField(auto_now=True)),
                ('device', models.OneToOneField(help_text='The device that this simulator will run for.', on_delete=django.db.models.deletion.CASCADE, related_name='simulator', to='foundation.Device')),
            ],
            options={
                'verbose_name': 'Device Simulator',
                'verbose_name_plural': 'Device Simulators',
                'db_table': 'mika_device_simulators',
                'permissions': (),
                'default_permissions': (),
            },
        ),
        migrations.AddIndex(
            model_name='devicesimulator',
            index=django.contrib.postgres.indexes.BrinIndex(autosummarize=True, fields=['created_at', 'last_modified_at'], name='mika_device_created_98c585_brin'),
        ),
    ]
