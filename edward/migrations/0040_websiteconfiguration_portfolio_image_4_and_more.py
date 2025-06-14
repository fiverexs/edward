# Generated by Django 5.1 on 2025-01-26 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edward', '0039_rename_portfolio_image_websiteconfiguration_portfolio_image_1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='websiteconfiguration',
            name='portfolio_image_4',
            field=models.ImageField(blank=True, null=True, upload_to='portfolio/'),
        ),
        migrations.AddField(
            model_name='websiteconfiguration',
            name='portfolio_image_5',
            field=models.ImageField(blank=True, null=True, upload_to='portfolio/'),
        ),
        migrations.AddField(
            model_name='websiteconfiguration',
            name='portfolio_image_6',
            field=models.ImageField(blank=True, null=True, upload_to='portfolio/'),
        ),
        migrations.AddField(
            model_name='websiteconfiguration',
            name='portfolio_text_10',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='websiteconfiguration',
            name='portfolio_text_11',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='websiteconfiguration',
            name='portfolio_text_12',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='websiteconfiguration',
            name='portfolio_text_7',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='websiteconfiguration',
            name='portfolio_text_8',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='websiteconfiguration',
            name='portfolio_text_9',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
