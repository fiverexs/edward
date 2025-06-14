# Generated by Django 5.1 on 2025-01-26 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edward', '0038_websiteconfiguration_portfolio_image_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='websiteconfiguration',
            old_name='portfolio_image',
            new_name='portfolio_image_1',
        ),
        migrations.AddField(
            model_name='websiteconfiguration',
            name='portfolio_image_2',
            field=models.ImageField(blank=True, null=True, upload_to='portfolio/'),
        ),
        migrations.AddField(
            model_name='websiteconfiguration',
            name='portfolio_image_3',
            field=models.ImageField(blank=True, null=True, upload_to='portfolio/'),
        ),
        migrations.AddField(
            model_name='websiteconfiguration',
            name='portfolio_text_3',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='websiteconfiguration',
            name='portfolio_text_4',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='websiteconfiguration',
            name='portfolio_text_5',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='websiteconfiguration',
            name='portfolio_text_6',
            field=models.TextField(blank=True, null=True),
        ),
    ]
