# Generated by Django 4.2.11 on 2025-03-18 13:44
# and manually changed to perform a "rename" instead
# of creating a new field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("udbytte", "0004_u1a_dato_udbetaling"),
    ]

    operations = [
        migrations.AlterField(
            model_name="u1a",
            name="dato_udbetaling",
            field=models.DateField(
                error_messages={
                    "invalid": "error.invalid_date",
                    "required": "error.required",
                },
                verbose_name="Vedtagelses dato",
            ),
        ),
        migrations.RenameField(
            model_name="u1a",
            old_name="dato_udbetaling",
            new_name="dato_vedtagelse",
        ),
    ]
