# Generated by Django 5.0.6 on 2024-06-24 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('water_management', '0005_alter_person_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='password',
            field=models.CharField(max_length=128),
        ),
    ]
