import sys
from pathlib import Path

from django.core.management import call_command
from django.db import migrations


def load(apps, schema_editor):
    if "test" not in sys.argv:  # tests make their own recipes
        call_command("import_cookbook", Path(__file__).resolve().parents[1] / "data" / "cookbook.json")


class Migration(migrations.Migration):
    dependencies = [("recipes", "0001_initial")]
    operations = [migrations.RunPython(load, migrations.RunPython.noop)]
