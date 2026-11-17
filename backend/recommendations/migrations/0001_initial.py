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
            name='RecipeFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recipe_feedback')),
                ('recipe', models.ForeignKey('recipes.Recipe', on_delete=models.CASCADE, related_name='feedback')),
                ('value', models.SmallIntegerField(choices=[(-1, 'Disliked'), (1, 'Liked')])),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=['user', 'recipe'], name='unique_user_recipe_feedback'), models.CheckConstraint(condition=Q(value__in=[-1, 1]), name='feedback_value_valid')],
            },
        ),
        migrations.CreateModel(
            name='CookingHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cooking_history')),
                ('recipe', models.ForeignKey('recipes.Recipe', on_delete=models.PROTECT, related_name='cooking_history')),
                ('cooked_at', models.DateTimeField()),
                ('servings', models.PositiveSmallIntegerField(null=True, blank=True)),
            ],
            options={
                'ordering': ['-cooked_at'],
            },
        ),
        migrations.CreateModel(
            name='MealPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meal_plans')),
                ('title', models.CharField(max_length=200, default='Meal plan')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'constraints': [models.CheckConstraint(condition=Q(end_date__gte=models.F('start_date')), name='mealplan_valid_date_range')],
            },
        ),
        migrations.CreateModel(
            name='PlannedMeal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plan', models.ForeignKey('recommendations.mealplan', on_delete=models.CASCADE, related_name='meals')),
                ('recipe', models.ForeignKey('recipes.Recipe', on_delete=models.PROTECT, related_name='planned_meals')),
                ('planned_for', models.DateField()),
                ('meal_type', models.CharField(max_length=12, choices=[('breakfast', 'Breakfast'), ('lunch', 'Lunch'), ('dinner', 'Dinner'), ('snack', 'Snack'), ('other', 'Other')], default='other')),
                ('servings', models.PositiveSmallIntegerField(default=1)),
                ('cooked_at', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'ordering': ['planned_for', 'id'],
                'constraints': [models.CheckConstraint(condition=Q(servings__gte=1), name='planned_servings_positive')],
            },
        ),
    ]
