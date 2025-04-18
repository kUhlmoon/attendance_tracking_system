# Generated by Django 5.1.7 on 2025-04-07 06:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0005_rename_registration_number_student_reg_number'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='status',
            field=models.CharField(choices=[('present', 'Present'), ('absent', 'Absent')], max_length=10),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='student',
            field=models.ForeignKey(limit_choices_to={'is_active': True, 'role': 'student'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='unit',
            name='students',
            field=models.ManyToManyField(limit_choices_to={'is_active': True, 'role': 'student'}, related_name='registered_units', to=settings.AUTH_USER_MODEL),
        ),
    ]
