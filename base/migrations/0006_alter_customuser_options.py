# Generated by Django 4.2.4 on 2023-11-05 04:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_rename_name_customuser_full_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
    ]