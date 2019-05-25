# Generated by Django 2.2.1 on 2019-05-24 23:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foundation', '0003_auto_20190524_2308'),
    ]

    operations = [
        migrations.AddField(
            model_name='productioninspection',
            name='task_item',
            field=models.ForeignKey(blank=True, help_text='The task item this inspection belongs to.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='foundation.TaskItem', verbose_name='Task Item'),
        ),
        migrations.AddField(
            model_name='taskitem',
            name='production_inspection',
            field=models.ForeignKey(blank=True, help_text='The production inspection this task belongs to.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='foundation.ProductionInspection'),
        ),
        migrations.AlterField(
            model_name='taskitem',
            name='production',
            field=models.ForeignKey(blank=True, help_text='The production this task belongs to.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='task_items', to='foundation.Production'),
        ),
    ]