# Generated by Django 3.2.13 on 2023-05-26 13:41

from django.db import migrations, models
import django.db.models.deletion
import obligatorisk_pension.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ObligatoriskPension',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('oprettet', models.DateTimeField(auto_now_add=True)),
                ('ændret', models.DateTimeField(auto_now=True)),
                ('cpr', models.CharField(max_length=10)),
                ('skatteår', models.PositiveSmallIntegerField()),
                ('navn', models.CharField(max_length=1000)),
                ('adresse', models.CharField(max_length=1000)),
                ('kommune', models.PositiveSmallIntegerField(choices=[(955, 'Kommune Kujalleq'), (956, 'Kommuneqarfik Sermersooq'), (957, 'Qeqqata Kommunia'), (959, 'Kommune Qeqertalik'), (960, 'Avannaata Kommunia'), (999, 'udbytte.udenfor_kommunal_inddeling')])),
                ('email', models.EmailField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='ObligatoriskPensionSelskab',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grønlandsk', models.BooleanField(choices=[(True, 'Ja'), (False, 'Nej')])),
                ('land', models.CharField(blank=True, max_length=50, null=True)),
                ('pensionsselskab', models.CharField(max_length=100)),
                ('obligatoriskpension', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='selskaber', to='obligatorisk_pension.obligatoriskpension')),
            ],
        ),
        migrations.CreateModel(
            name='ObligatoriskPensionFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fil', models.FileField(upload_to=obligatorisk_pension.models.obligatoriskpensionfile_upload_to)),
                ('beskrivelse', models.CharField(blank=True, max_length=1000, null=True)),
                ('obligatoriskpension', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='filer', to='obligatorisk_pension.obligatoriskpension')),
            ],
        ),
    ]
