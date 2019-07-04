# Generated by Django 2.2.1 on 2019-07-04 16:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0006_remove_instrument_configuration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instrument',
            name='device',
            field=models.ForeignKey(default=1, help_text='The device which this instrument belongs to.', on_delete=django.db.models.deletion.CASCADE, related_name='instruments', to='foundation.Device'),
            preserve_default=False,
        ),
    ]