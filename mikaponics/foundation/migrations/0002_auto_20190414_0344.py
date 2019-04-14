# Generated by Django 2.1.7 on 2019-04-14 03:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instrumentalert',
            name='slug',
            field=models.SlugField(editable=False, help_text='The unique slug used for this instrument alert when accessing details page.', max_length=255, unique=True, verbose_name='Slug'),
        ),
    ]
