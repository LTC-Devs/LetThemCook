/** JSON contract implemented by backend/recipes/api_views.py. */
export type RecipeSummary = {
  id: number;
  name: string;
  base_servings: number | null;
  category: string | null;
};

export type RecipeListResponse = {
  count: number;
  page: number;
  pages: number;
  results: RecipeSummary[];
};

export type RecipeItem = {
  id: number;
  ingredient: string;
  amount: string | null;
  amount_max: string | null;
  unit: "g" | "ml" | "pcs";
  quantity_note: string;
  group: string;
  alternative_group: string;
  is_optional: boolean;
};

export type RecipeDetail = RecipeSummary & {
  steps: string[];
  items: RecipeItem[];
};

/** Real cookbook suggestion. Not a saved meal and not a pantry availability claim. */
export type HomeRecipeSuggestion = RecipeSummary & {
  ingredients: string[];
  /** Transparent 0-100 point result from the live pantry stock. */
  score: number;
  score_breakdown: { availability: number; few_missing: number; expiry: number };
  missing_ingredients_count: number;
  scored_ingredients_count: number;
  unquantified_ingredients_count: number;
};
