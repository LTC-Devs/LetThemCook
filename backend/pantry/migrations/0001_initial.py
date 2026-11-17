# Initial schema for the LTC cookbook and kitchen domains.
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
from django.db.models import F, Q


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0001_initial'),
        ('products', '0003_product_ingredient'),
    ]
    operations = [
        migrations.CreateModel(
            name='PantryItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pantry_items')),
                ('ingredient', models.ForeignKey('recipes.Ingredient', null=True, blank=True, on_delete=models.PROTECT, related_name='pantry_items')),
                ('product', models.ForeignKey('products.Product', null=True, blank=True, on_delete=models.SET_NULL, related_name='pantry_items')),
                ('manual_name', models.CharField(max_length=250, blank=True)),
                ('quantity', models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('1'))),
                ('unit', models.CharField(max_length=40, blank=True)),
                ('expiry_date', models.DateField(null=True, blank=True, db_index=True)),
                ('purchased_at', models.DateField(null=True, blank=True)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(max_length=12, choices=[('available', 'Available'), ('consumed', 'Consumed'), ('discarded', 'Discarded')], default='available', db_index=True)),
                ('finished_at', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'indexes': [models.Index(fields=['user', 'status', 'expiry_date'], name='pantry_expiry_lookup_idx')],
                'constraints': [models.CheckConstraint(condition=Q(quantity__gte=0), name='pantry_quantity_nonneg')],
            },
        ),
    ]
