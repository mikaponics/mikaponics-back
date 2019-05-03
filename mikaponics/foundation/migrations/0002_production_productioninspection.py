# Generated by Django 2.2.1 on 2019-05-03 17:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Production',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.PositiveSmallIntegerField(choices=[(1, 'Preparing'), (3, 'Operating'), (4, 'Terminated')], default=1, help_text='The state of coupon.', verbose_name='State')),
                ('slug', models.SlugField(blank=True, editable=False, help_text='The unique slug used for this food production when accessing details page.', max_length=127, unique=True, verbose_name='Slug')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_from', models.GenericIPAddressField(blank=True, editable=False, help_text='The IP address of the creator.', null=True, verbose_name='Created from IP')),
                ('created_from_is_public', models.BooleanField(blank=True, default=False, editable=False, help_text='Is creator a public IP and is routable.', verbose_name='Is created from IP public?')),
                ('last_modified_at', models.DateTimeField(auto_now=True)),
                ('last_modified_from', models.GenericIPAddressField(blank=True, editable=False, help_text='The IP address of the modifier.', null=True, verbose_name='Last modified from IP')),
                ('last_modified_from_is_public', models.BooleanField(blank=True, default=False, editable=False, help_text='Is modifier a public IP and is routable.', verbose_name='Is Last modified from IP public?')),
                ('created_by', models.ForeignKey(blank=True, editable=False, help_text='The user whom created this food production.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_productions', to=settings.AUTH_USER_MODEL)),
                ('device', models.ForeignKey(help_text='The device which is responsible for monitoring this food production.', on_delete=django.db.models.deletion.CASCADE, related_name='productions', to='foundation.Device')),
                ('last_modified_by', models.ForeignKey(blank=True, editable=False, help_text='The user whom last modified this food production.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='last_modified_productions', to=settings.AUTH_USER_MODEL)),
                ('previous', models.ForeignKey(blank=True, help_text='The previous production of food that this production is related to. General this happens with fruit bearing plants / trees.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='previous_productions', to='foundation.Production')),
                ('user', models.ForeignKey(help_text='The user whom this food production invoice belongs to.', on_delete=django.db.models.deletion.CASCADE, related_name='productions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Production',
                'verbose_name_plural': 'Productions',
                'db_table': 'mika_productions',
                'permissions': (),
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ProductionInspection',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(blank=True, editable=False, help_text='The unique slug used for this food production inspection when accessing details page.', max_length=127, unique=True, verbose_name='Slug')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_from', models.GenericIPAddressField(blank=True, editable=False, help_text='The IP address of the creator.', null=True, verbose_name='Created from IP')),
                ('created_from_is_public', models.BooleanField(blank=True, default=False, editable=False, help_text='Is creator a public IP and is routable.', verbose_name='Is created from IP public?')),
                ('last_modified_at', models.DateTimeField(auto_now=True)),
                ('last_modified_from', models.GenericIPAddressField(blank=True, editable=False, help_text='The IP address of the modifier.', null=True, verbose_name='Last modified from IP')),
                ('last_modified_from_is_public', models.BooleanField(blank=True, default=False, editable=False, help_text='Is modifier a public IP and is routable.', verbose_name='Is Last modified from IP public?')),
                ('created_by', models.ForeignKey(blank=True, editable=False, help_text='The user whom created this food production inspections.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_production_inspections', to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(blank=True, editable=False, help_text='The user whom last modified this food production inspection.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='last_modified_production_inspections', to=settings.AUTH_USER_MODEL)),
                ('production', models.ForeignKey(blank=True, help_text='The food production operation this quality assurance inspection is for.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='inspections', to='foundation.Production')),
            ],
            options={
                'verbose_name': 'Production Inspection',
                'verbose_name_plural': 'Production Inspections',
                'db_table': 'mika_production_inspections',
                'permissions': (),
                'default_permissions': (),
            },
        ),
    ]
