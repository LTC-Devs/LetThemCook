"use server";

import { revalidatePath } from "next/cache";
import { postShopping } from "@/lib/django";

type ActionResult = { ok: boolean; message?: string };

export async function planRecipeAction(recipeId: number, servings: number): Promise<ActionResult> {
  if (!Number.isSafeInteger(recipeId) || recipeId < 1 || !Number.isSafeInteger(servings) || servings < 1 || servings > 99) {
    return { ok: false, message: "Podaj poprawne ID przepisu i liczbę porcji (1–99)." };
  }
  try {
    await postShopping("/api/shopping/plan/", { recipe_id: recipeId, servings });
    revalidatePath("/shopping");
    return { ok: true };
  } catch (error) {
    return { ok: false, message: error instanceof Error ? error.message : "Nie można dodać przepisu." };
  }
}

export async function purchaseAction(ingredientIds: number[]): Promise<ActionResult> {
  if (!ingredientIds.length || !ingredientIds.every((id) => Number.isSafeInteger(id) && id > 0)) {
    return { ok: false, message: "Zaznacz składniki do przeniesienia." };
  }
  try {
    await postShopping("/api/shopping/purchase/", { ingredient_ids: ingredientIds });
    revalidatePath("/shopping");
    revalidatePath("/pantry");
    return { ok: true };
  } catch (error) {
    return { ok: false, message: error instanceof Error ? error.message : "Nie udało się przenieść zakupów." };
  }
}
