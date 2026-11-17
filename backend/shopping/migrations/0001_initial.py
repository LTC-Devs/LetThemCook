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
        ('recommendations', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='ShoppingList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shopping_lists')),
                ('title', models.CharField(max_length=200, default='Shopping list')),
                ('meal_plan', models.ForeignKey('recommendations.MealPlan', null=True, blank=True, on_delete=models.SET_NULL, related_name='shopping_lists')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ShoppingListItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shopping_list', models.ForeignKey('shopping.shoppinglist', on_delete=models.CASCADE, related_name='items')),
                ('ingredient', models.ForeignKey('recipes.Ingredient', null=True, blank=True, on_delete=models.PROTECT, related_name='shopping_items')),
                ('product', models.ForeignKey('products.Product', null=True, blank=True, on_delete=models.SET_NULL, related_name='shopping_items')),
                ('source_recipe_item', models.ForeignKey('recipes.RecipeItem', null=True, blank=True, on_delete=models.SET_NULL, related_name='shopping_items')),
                ('manual_name', models.CharField(max_length=250, blank=True)),
                ('quantity', models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)),
                ('unit', models.CharField(max_length=40, blank=True)),
                ('position', models.PositiveIntegerField(default=0)),
                ('is_checked', models.BooleanField(default=False)),
                ('checked_at', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'ordering': ['position', 'id'],
                'constraints': [models.CheckConstraint(condition=Q(quantity__gte=0) | Q(quantity__isnull=True), name='shopping_quantity_nonneg')],
            },
        ),
    ]
