# Generated by Django 3.2.13 on 2023-05-23 13:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ObligatoriskPension',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cpr', models.CharField(max_length=10)),
                ('navn', models.CharField(max_length=1000)),
                ('adresse', models.CharField(max_length=1000)),
                ('kommune', models.PositiveSmallIntegerField(choices=[(955, 'Kommune Kujalleq'), (956, 'Kommuneqarfik Sermersooq'), (957, 'Qeqqata Kommunia'), (959, 'Kommune Qeqertalik'), (960, 'Avannaata Kommunia'), (999, 'udbytte.udenfor_kommunal_inddeling')])),
                ('email', models.EmailField(max_length=256)),
                ('grønlandsk', models.BooleanField(choices=[(True, 'Ja'), (False, 'Nej')])),
                ('land', models.CharField(blank=True, max_length=50, null=True)),
                ('pensionsselskab', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ObligatoriskPensionFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fil', models.FileField(upload_to='obligatorisk_pension/%Y/%Y-%m-%d/')),
                ('beskrivelse', models.CharField(max_length=1000)),
                ('obligatoriskpension', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='obligatorisk_pension.obligatoriskpension')),
            ],
        ),
    ]