# Generated by Django 3.2.10 on 2021-12-27 12:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vectors', '0007_alter_vector_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vector',
            old_name='name',
            new_name='description',
        ),
    ]