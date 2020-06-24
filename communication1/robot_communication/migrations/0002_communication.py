# Generated by Django 3.0.5 on 2020-04-29 02:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robot_communication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Communication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('com_type', models.CharField(max_length=140)),
                ('com_content', models.CharField(max_length=14000)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]