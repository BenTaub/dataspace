# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2017-06-05 22:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PersonDynamic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, help_text="Person's title, like Mr. Dr. or Ms.", max_length=20, verbose_name="Person's title e.g. Mr. Dr. or Ms.)")),
                ('first_name', models.CharField(help_text='First name also includes any middle names', max_length=100, verbose_name="Person's first and middle names")),
                ('last_name', models.CharField(help_text='Last name includes titles such as Phd.', max_length=50, verbose_name="Person's last name")),
                ('notes', models.TextField(blank=True, help_text='Notes relevant to this person')),
                ('citizenship_status', models.CharField(blank=True, default='US Citizen', help_text='Information about whether this person is a US citizen or not', max_length=50, verbose_name='Citizenship status')),
                ('current_record_fg', models.BooleanField(default=True, help_text='Set to True for the current version of the record', verbose_name='Current record flag')),
                ('effective_date', models.DateTimeField(default=django.utils.timezone.now, help_text='The date & time on which this record became active', verbose_name='Record effective date')),
                ('end_date', models.DateTimeField(blank=True, help_text='The date and time on which this record expired', verbose_name='Record end date')),
            ],
        ),
        migrations.CreateModel(
            name='PersonStatic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_record_fg', models.BooleanField(default=True, help_text='Set to True for the current version of the record', verbose_name='Current record flag')),
                ('effective_date', models.DateTimeField(default=django.utils.timezone.now, help_text='The date & time on which this record became active', verbose_name='Record effective date')),
                ('end_date', models.DateTimeField(blank=True, help_text='The date and time on which this record expired', verbose_name='Record end date')),
            ],
        ),
        migrations.AddField(
            model_name='persondynamic',
            name='person_id',
            field=models.ForeignKey(help_text='A link to the key for this person that never changes', on_delete=django.db.models.deletion.CASCADE, to='contacts.PersonStatic', verbose_name='Time independent person ID'),
        ),
    ]
