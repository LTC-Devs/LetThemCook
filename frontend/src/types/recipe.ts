/** Minimal frontend contract; reconcile these fields with Django serializers when API is added. */
export type RecipeSummary = {
  id: number;
  name: string;
  base_servings: number | null;
};
