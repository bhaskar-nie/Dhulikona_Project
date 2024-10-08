# Generated by Django 5.0.6 on 2024-06-28 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('water_management', '0009_person_due_days_person_enable_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='person_role',
            field=models.CharField(choices=[('panchayathead', 'Panchayat Head'), ('consumer', 'Consumer'), ('contractor', 'Contractor'), ('watercommitteehead', 'Water Committee Head'), ('pumpoperator', 'Pump Operator')], default='consumer', max_length=20),
        ),
    ]
