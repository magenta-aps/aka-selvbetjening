from django.db import migrations


def apply(apps, schema_editor):
    PrismeDown = apps.get_model('aka', 'PrismeDown')
    if not PrismeDown.objects.exists():
        PrismeDown.objects.create(down=False)


def revert(apps, schema_editor):
    PrismeDown = apps.get_model('aka', 'PrismeDown')
    if PrismeDown.objects.exists():
        PrismeDown.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('aka', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(apply, revert),
    ]
