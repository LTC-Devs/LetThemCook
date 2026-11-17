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
    ]
    operations = [
        migrations.CreateModel(
            name='UserPreferences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='food_preferences')),
                ('household_size', models.PositiveSmallIntegerField(default=1)),
                ('measurement_system', models.CharField(max_length=10, choices=[('metric', 'Metric'), ('imperial', 'Imperial')], default='metric')),
                ('allergies', models.ManyToManyField('recipes.allergen', blank=True, related_name='user_preferences')),
                ('required_diets', models.ManyToManyField('recipes.diet', blank=True, related_name='user_preferences')),
                ('excluded_ingredients', models.ManyToManyField('recipes.ingredient', blank=True, related_name='excluded_by_users')),
                ('liked_ingredients', models.ManyToManyField('recipes.ingredient', blank=True, related_name='liked_by_users')),
                ('disliked_ingredients', models.ManyToManyField('recipes.ingredient', blank=True, related_name='disliked_by_users')),
            ],
            options={
                'constraints': [models.CheckConstraint(condition=Q(household_size__gte=1), name='household_size_positive')],
            },
        ),
    ]
