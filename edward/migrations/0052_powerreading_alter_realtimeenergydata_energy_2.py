# Generated by Django 5.1 on 2025-04-13 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edward', '0051_rename_power_kw_realtimeenergydata_energy_1_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PowerReading',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('power1', models.FloatField()),
                ('power2', models.FloatField()),
            ],
        ),
        migrations.AlterField(
            model_name='realtimeenergydata',
            name='energy_2',
            field=models.FloatField(),
        ),
    ]
