# Generated by Django 5.1.7 on 2025-04-09 04:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0007_alter_unit_lecturer'),
        ('users', '0003_alter_customuser_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='units',
            field=models.ManyToManyField(blank=True, related_name='lecturers', to='attendance.unit'),
        ),
    ]
