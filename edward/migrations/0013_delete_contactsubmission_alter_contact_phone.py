# Generated by Django 5.1 on 2024-11-09 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edward', '0012_contactsubmission'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ContactSubmission',
        ),
        migrations.AlterField(
            model_name='contact',
            name='phone',
            field=models.CharField(max_length=15),
        ),
    ]
