# Generated by Django 2.2.1 on 2019-05-11 22:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0004_auto_20190511_0232'),
    ]

    operations = [
        migrations.AddField(
            model_name='production',
            name='failure_reason_at_finish',
            field=models.TextField(blank=True, help_text='The reason why this crop production was overall considered a failure by the user.', null=True, verbose_name='Failure reason at finish'),
        ),
        migrations.AddField(
            model_name='production',
            name='notes_at_finish',
            field=models.TextField(blank=True, help_text='Any notes to add upon the completion of the crop production.', null=True, verbose_name='Comments at finish'),
        ),
        migrations.AddField(
            model_name='production',
            name='was_success_at_finish',
            field=models.BooleanField(blank=True, default=False, help_text='Indicates if this crop production was considered a success to the user or a failure.', verbose_name='Was this crop production a success upon completion?'),
        ),
        migrations.AlterField(
            model_name='production',
            name='created_by',
            field=models.ForeignKey(blank=True, editable=False, help_text='The user whom created this crop production.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_productions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='production',
            name='device',
            field=models.ForeignKey(help_text='The device which is responsible for monitoring this crop production.', on_delete=django.db.models.deletion.CASCADE, related_name='productions', to='foundation.Device'),
        ),
        migrations.AlterField(
            model_name='production',
            name='last_modified_by',
            field=models.ForeignKey(blank=True, editable=False, help_text='The user whom last modified this crop production.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='last_modified_productions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='production',
            name='previous',
            field=models.ForeignKey(blank=True, help_text='The previous production of crop that this production is related to. General this happens with fruit bearing plants / trees.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='previous_productions', to='foundation.Production'),
        ),
        migrations.AlterField(
            model_name='production',
            name='slug',
            field=models.SlugField(blank=True, editable=False, help_text='The unique slug used for this crop production when accessing details page.', max_length=127, unique=True, verbose_name='Slug'),
        ),
        migrations.AlterField(
            model_name='production',
            name='user',
            field=models.ForeignKey(help_text='The user whom this crop production invoice belongs to.', on_delete=django.db.models.deletion.CASCADE, related_name='productions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='productioncrop',
            name='harvest_failure_reason_at_finish',
            field=models.TextField(blank=True, help_text='The harvest failure reason of the crop when the production has finished.', null=True, verbose_name='Harvest failure at finish'),
        ),
    ]
