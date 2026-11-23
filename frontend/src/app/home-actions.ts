"use server";

import { getHomeRecipeSuggestions } from "@/lib/django";

/** Show the next best scored recipe without displaying a duplicate card. */
export async function drawAnotherBookRecipe(excludedIds: number[]) {
  const results = await getHomeRecipeSuggestions(excludedIds, 1);
  return results[0] ?? null;
}
