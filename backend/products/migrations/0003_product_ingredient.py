from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('products', '0002_auto_20261013_1353'),
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='ingredient',
            field=models.ForeignKey(
                to='recipes.ingredient', null=True, blank=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='products',
            ),
        ),
    ]
