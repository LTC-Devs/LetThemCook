from django.db import migrations


def create_cookbook(apps, schema_editor):
    Cookbook = apps.get_model('recipes', 'Cookbook')
    Cookbook.objects.using(schema_editor.connection.alias).get_or_create(
        title='Kuchnia Polska', edition_year=1985
    )


class Migration(migrations.Migration):
    dependencies = [('recipes', '0001_initial')]

    operations = [
        migrations.RunPython(create_cookbook, reverse_code=migrations.RunPython.noop),
    ]
