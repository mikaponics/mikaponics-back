# Generated by Django 2.2.1 on 2019-05-03 19:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0003_auto_20190503_1913'),
    ]

    operations = [
        migrations.AddField(
            model_name='productioncrop',
            name='substrate',
            field=models.ForeignKey(blank=True, help_text='The growing medium used for this plant/fish in production.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='production_crops', to='foundation.CropSubstrate'),
        ),
        migrations.AddField(
            model_name='productioncrop',
            name='substrate_other',
            field=models.CharField(blank=True, help_text='The name of the substrate the user is using which we do not have in our system.', max_length=255, null=True, verbose_name='Substrate (Other)'),
        ),
    ]
