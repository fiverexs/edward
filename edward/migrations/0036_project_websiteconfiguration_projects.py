# Generated by Django 5.1 on 2025-01-26 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edward', '0035_remove_websiteconfiguration_projects_delete_project'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='projects/')),
            ],
        ),
        migrations.AddField(
            model_name='websiteconfiguration',
            name='projects',
            field=models.ManyToManyField(blank=True, to='edward.project'),
        ),
    ]
