# Initial schema for the LTC cookbook and kitchen domains.
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
from django.db.models import F, Q


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='Cookbook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250)),
                ('edition_year', models.PositiveSmallIntegerField()),
                ('publisher', models.CharField(max_length=200, blank=True)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=['title', 'edition_year'], name='unique_cookbook_edition')],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, db_index=True)),
                ('parent', models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT, related_name='children')),
            ],
        ),
        migrations.CreateModel(
            name='Allergen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='DietCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Diet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('excluded_categories', models.ManyToManyField('recipes.dietcategory', blank=True, related_name='excluding_diets')),
            ],
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('aliases', models.JSONField(default=list, blank=True)),
                ('allergens', models.ManyToManyField('recipes.allergen', blank=True, related_name='ingredients')),
                ('diet_categories', models.ManyToManyField('recipes.dietcategory', blank=True, related_name='ingredients')),
            ],
        ),
        migrations.CreateModel(
            name='Substitution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ingredient', models.ForeignKey('recipes.ingredient', on_delete=models.CASCADE, related_name='substitutions')),
                ('substitute', models.ForeignKey('recipes.ingredient', on_delete=models.PROTECT, related_name='substitute_for')),
                ('ratio', models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('1.0000'))),
                ('note', models.CharField(max_length=255, blank=True)),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=['ingredient', 'substitute'], name='unique_ingredient_substitute'), models.CheckConstraint(condition=Q(ratio__gt=0), name='substitution_ratio_positive'), models.CheckConstraint(condition=~Q(ingredient=F('substitute')), name='substitution_not_self')],
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300, db_index=True)),
                ('category', models.ForeignKey('recipes.category', on_delete=models.SET_NULL, null=True, blank=True, related_name='recipes')),
                ('cookbook', models.ForeignKey('recipes.cookbook', on_delete=models.PROTECT, null=True, blank=True, related_name='recipes')),
                ('owner', models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='custom_recipes', help_text='Set for a user-created recipe; blank for public book recipes.')),
                ('source_number', models.PositiveIntegerField(null=True, blank=True, db_index=True)),
                ('source_page', models.PositiveIntegerField(null=True, blank=True)),
                ('servings', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('instructions', models.TextField(blank=True)),
                ('steps', models.JSONField(default=list, blank=True)),
                ('raw_ingredients', models.JSONField(default=list, blank=True)),
                ('review_notes', models.JSONField(default=list, blank=True)),
                ('parsing_status', models.CharField(max_length=10, choices=[('raw', 'Unreviewed OCR'), ('review', 'Needs review'), ('verified', 'Verified')], default='raw', db_index=True)),
                ('diets', models.ManyToManyField('recipes.diet', blank=True, related_name='recipes')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'indexes': [models.Index(fields=['cookbook', 'source_number'], name='recipe_book_number_idx')],
                'constraints': [models.CheckConstraint(condition=Q(servings__gte=1) | Q(servings__isnull=True), name='recipe_servings_positive')],
            },
        ),
        migrations.CreateModel(
            name='RecipeItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey('recipes.recipe', on_delete=models.CASCADE, related_name='items')),
                ('position', models.PositiveIntegerField(default=0)),
                ('ingredient', models.ForeignKey('recipes.ingredient', on_delete=models.PROTECT, null=True, blank=True, related_name='recipe_items')),
                ('sub_recipe', models.ForeignKey('recipes.recipe', on_delete=models.PROTECT, null=True, blank=True, related_name='used_as_ingredient_in')),
                ('raw_text', models.TextField(blank=True)),
                ('amount', models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)),
                ('amount_max', models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)),
                ('unit', models.CharField(max_length=40, blank=True)),
                ('comment', models.TextField(blank=True)),
                ('is_optional', models.BooleanField(default=False)),
                ('substitution_allowed', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['position', 'id'],
                'constraints': [models.CheckConstraint(condition=Q(amount__gte=0) | Q(amount__isnull=True), name='recipe_item_amount_nonneg'), models.CheckConstraint(condition=Q(amount_max__gte=0) | Q(amount_max__isnull=True), name='recipe_item_max_nonneg'), models.CheckConstraint(condition=Q(amount_max__isnull=True) | Q(amount__isnull=True) | Q(amount_max__gte=F('amount')), name='recipe_item_range_order'), models.CheckConstraint(condition=Q(ingredient__isnull=True) | Q(sub_recipe__isnull=True), name='recipe_item_one_reference')],
            },
        ),
    ]
