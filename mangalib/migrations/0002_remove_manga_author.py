# Generated by Django 4.0.4 on 2022-04-26 17:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mangalib', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='manga',
            name='author',
        ),
    ]
