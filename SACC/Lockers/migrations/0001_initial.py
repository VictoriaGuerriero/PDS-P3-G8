# Generated by Django 4.2.7 on 2023-11-13 19:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=200)),
                ('city', models.CharField(max_length=200)),
                ('region', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Locker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('height', models.IntegerField(default=0)),
                ('width', models.IntegerField(default=0)),
                ('availability', models.BooleanField(default=True)),
                ('reserved', models.BooleanField(default=False)),
                ('confirmed', models.BooleanField(default=False)),
                ('loaded', models.BooleanField(default=False)),
                ('opened', models.BooleanField(default=False)),
                ('locked', models.BooleanField(default=True)),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Lockers.station')),
            ],
        ),
    ]
