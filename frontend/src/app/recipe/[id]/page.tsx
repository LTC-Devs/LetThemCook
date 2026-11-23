export const instant = false;

import { notFound } from "next/navigation";
import { fetchRecipeDetails, fetchUserSession } from "@/lib/mock-api";
import RecipeClient from "@/components/recipe/RecipeClient";

export default async function RecipePage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ date?: string }>;
}) {
  const { id } = await params;
  const { date } = await searchParams;

  const [user, initialRecipe] = await Promise.all([
    fetchUserSession(),
    fetchRecipeDetails(id, date),
  ]);

  if (!initialRecipe) {
    notFound();
  }

  return <RecipeClient initialRecipe={initialRecipe} user={user} />;
}