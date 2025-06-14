# Generated by Django 5.1 on 2024-11-07 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edward', '0005_homepagecontent_portfolioproject_service'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebsiteConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(default='5RS Construction Services', max_length=100)),
                ('contact_email', models.EmailField(default='fiversconstruction@yahoo.com', max_length=254)),
                ('contact_phone', models.CharField(blank=True, max_length=15)),
                ('address', models.CharField(blank=True, max_length=255)),
                ('facebook_page', models.URLField(blank=True, help_text='Facebook page URL', null=True)),
                ('footer_text', models.CharField(default='Copyright © 2024 All Rights Reserved.', max_length=255)),
            ],
        ),
    ]
