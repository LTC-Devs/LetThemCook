/** JSON contract implemented by backend/recipes/api_views.py. */
export type RecipeSummary = {
  id: number;
  title: string;
  servings: number | null;
  source_number: number | null;
  parsing_status: "raw" | "review" | "verified";
  category: string | null;
  cookbook: string | null;
};

export type RecipeListResponse = {
  count: number;
  page: number;
  pages: number;
  results: RecipeSummary[];
};

export type RecipeItem = {
  id: number;
  position: number;
  raw_text: string;
  ingredient: string | null;
  amount: string | null;
  amount_max: string | null;
  unit: string;
};

export type RecipeDetail = RecipeSummary & {
  instructions: string;
  raw_ingredients: string[];
  items: RecipeItem[];
};
