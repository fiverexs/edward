# Generated by Django 5.1 on 2024-12-09 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edward', '0026_delete_customuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='EnergySystem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('system_size_kwp', models.FloatField(default=0.0, verbose_name='System Size (kWp)')),
                ('battery_charge_percentage', models.FloatField(default=0.0, verbose_name='Battery Charge (%)')),
                ('battery_status', models.CharField(choices=[('Charging', 'Charging'), ('Discharging', 'Discharging'), ('Idle', 'Idle')], default='Idle', max_length=50, verbose_name='Battery Status')),
                ('battery_health', models.CharField(default='Good', max_length=50, verbose_name='Battery Health')),
                ('solar_production_kw', models.FloatField(default=0.0, verbose_name='Solar Production (kW)')),
            ],
            options={
                'verbose_name': 'Energy System',
                'verbose_name_plural': 'Energy Systems',
            },
        ),
    ]
