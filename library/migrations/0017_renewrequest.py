# Generated by Django 3.2.2 on 2021-05-21 08:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0016_staff'),
    ]

    operations = [
        migrations.CreateModel(
            name='RenewRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_of_days', models.IntegerField(default=1)),
                ('reason', models.CharField(max_length=100)),
                ('book', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='library.issuebook')),
                ('staff', models.ManyToManyField(to='library.Staff')),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='library.student')),
            ],
        ),
    ]
