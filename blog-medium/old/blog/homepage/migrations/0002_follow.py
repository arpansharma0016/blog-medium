# Generated by Django 2.2.11 on 2021-07-04 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('follower', models.IntegerField()),
                ('followed', models.IntegerField()),
                ('created', models.DateField(auto_now_add=True)),
            ],
        ),
    ]
