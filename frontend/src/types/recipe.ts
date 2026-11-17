/** Minimal frontend contract; reconcile these fields with Django serializers when API is added. */
export type RecipeSummary = {
  id: number;
  title: string;
  servings: number | null;
};
