# Generated by Django 2.2.6 on 2019-10-17 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='birthday',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.IntegerField(choices=[(0, 'Male'), (1, 'Female'), (2, 'Other')], default=0),
        ),
    ]
