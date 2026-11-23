import json

from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection, transaction

from recipes.models import Category, Ingredient, IngredientFeature, Recipe, RecipeItem


class Command(BaseCommand):
    help = "Import recipes/data/cookbook.json into an empty database"

    def add_arguments(self, parser):
        parser.add_argument("path", nargs="?", default="recipes/data/cookbook.json")

    @transaction.atomic
    def handle(self, path, **options):
        data = json.load(open(path, encoding="utf-8"))

        Category.objects.bulk_create(
            Category(id=c["id"], name=c["name"], parent_id=c["parent_id"])
            for c in data["Category"]
        )
        IngredientFeature.objects.bulk_create(
            IngredientFeature(id=f["id"], name=f["name"], kind=f["kind"])
            for f in data["IngredientFeature"]
        )
        Ingredient.objects.bulk_create(
            Ingredient(id=i["id"], canonical_name=i["canonical_name"],
                       base_unit="pcs" if i["base_unit"] == "szt" else i["base_unit"])
            for i in data["Ingredient"]
        )
        Ingredient.features.through.objects.bulk_create(
            Ingredient.features.through(ingredient_id=x["ingredient_id"], ingredientfeature_id=x["feature_id"])
            for x in data["IngredientFeatureLink"]
        )
        Recipe.objects.bulk_create(
            Recipe(id=r["id"], name=r["name"], category_id=r["category_id"],
                   base_servings=r["base_servings"], steps=r["steps"])
            for r in data["Recipe"]
        )
        RecipeItem.objects.bulk_create(
            RecipeItem(id=it["id"], recipe_id=it["recipe_id"], ingredient_id=it["ingredient_id"],
                       amount=it["amount"], amount_max=it["amount_max"],
                       quantity_note=it["quantity_note"] or "", group=it["group"] or "",
                       alternative_group=it["alternative_group"] or "", is_optional=it["is_optional"])
            for it in data["RecipeItem"]
        )

        # the ids came from the file, so new rows must start after them
        models = [Category, IngredientFeature, Ingredient, Ingredient.features.through, Recipe, RecipeItem]
        with connection.cursor() as cursor:
            for sql in connection.ops.sequence_reset_sql(no_style(), models):
                cursor.execute(sql)

        self.stdout.write(f"Imported {len(data['Recipe'])} recipes")
