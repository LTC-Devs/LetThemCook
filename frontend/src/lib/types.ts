export interface UserSession {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
}

export interface RecipeIngredient {
  name: string;
  quantity_value: number;
  quantity_unit: string;
  is_missing: boolean;
}

export interface RecipeSummary {
  id: number;
  target_date: string;
  title: string;
  ingredients_list: string[];
  missing_ingredients_count: number;
  is_cooked: boolean;
  is_liked: boolean | null;
}

export interface RecipeDetail {
  id: number;
  target_date: string;
  title: string;
  ingredients_list: RecipeIngredient[];
  missing_ingredients_count: number;
  instructions: string;
  is_cooked: boolean;
  is_liked: boolean | null;
  can_cook: boolean;
  can_reshuffle: boolean;
}