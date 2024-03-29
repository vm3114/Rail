# Generated by Django 5.0 on 2024-01-16 12:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Coach',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=2)),
                ('coach_type', models.CharField(choices=[('1A', 'AC First Class'), ('2A', 'AC Second Class'), ('3A', 'AC Third Class'), ('SL', 'Sleeper Class'), ('GN', 'General Class')], max_length=2)),
                ('total_seats', models.PositiveIntegerField()),
                ('price_per_segment', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['coach_type'],
            },
        ),
        migrations.CreateModel(
            name='DayOfWeek',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('MON', 'Monday'), ('TUE', 'Tuesday'), ('WED', 'Wednesday'), ('THU', 'Thursday'), ('FRI', 'Friday'), ('SAT', 'Saturday'), ('SUN', 'Sunday')], max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='Stop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('station', models.CharField(max_length=50)),
                ('time', models.TimeField()),
                ('order', models.IntegerField(null=True)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('credit', models.IntegerField(default=0)),
                ('email', models.EmailField(max_length=254, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='JourneySegment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('coach', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservation.coach')),
                ('day', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservation.dayofweek')),
            ],
        ),
        migrations.CreateModel(
            name='Seat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=5)),
                ('is_booked', models.BooleanField(default=False)),
                ('journey_segment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='reservation.journeysegment')),
            ],
            options={
                'ordering': ['number'],
            },
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.PositiveIntegerField()),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservation.account')),
                ('seat', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='reservation.seat')),
            ],
        ),
        migrations.AddField(
            model_name='account',
            name='bookings',
            field=models.ManyToManyField(blank=True, to='reservation.seat'),
        ),
        migrations.CreateModel(
            name='SeatReservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seat_number', models.CharField(max_length=5)),
                ('name', models.CharField(max_length=255)),
                ('age', models.PositiveIntegerField()),
                ('date', models.DateField()),
                ('bookings', models.ManyToManyField(to='reservation.booking')),
                ('coach', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservation.coach')),
                ('day', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservation.dayofweek')),
            ],
        ),
        migrations.CreateModel(
            name='Train',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=100)),
                ('operating_days', models.ManyToManyField(blank=True, to='reservation.dayofweek')),
            ],
            options={
                'ordering': ['code'],
            },
        ),
        migrations.AddField(
            model_name='coach',
            name='train',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservation.train'),
        ),
        migrations.CreateModel(
            name='Train_stops',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservation.stop')),
                ('train', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservation.train')),
            ],
            options={
                'unique_together': {('train', 'stop')},
            },
        ),
        migrations.AddField(
            model_name='train',
            name='stops',
            field=models.ManyToManyField(through='reservation.Train_stops', to='reservation.stop'),
        ),
    ]
