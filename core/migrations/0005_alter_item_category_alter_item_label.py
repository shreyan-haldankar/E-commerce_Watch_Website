# Generated by Django 4.1 on 2022-09-03 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_item_category_alter_item_label'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.CharField(choices=[('A', 'Analog'), ('C', 'Chronograph'), ('S', 'SmartWatch')], default=('A', 'Analog'), max_length=1),
        ),
        migrations.AlterField(
            model_name='item',
            name='label',
            field=models.CharField(choices=[('P', 'primary'), ('S', 'secondary'), ('D', 'danger')], default=('P', 'primary'), max_length=1),
        ),
    ]
