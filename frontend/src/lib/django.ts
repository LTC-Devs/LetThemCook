import type { HomeRecipeSuggestion, RecipeDetail, RecipeListResponse } from "@/types/recipe-api";

/** Server-side API client: import it only from Next.js Server Components. */
const DJANGO_URL = (process.env.BACKEND_API_BASE_URL ?? process.env.DJANGO_API_BASE_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

export class DjangoApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "DjangoApiError";
  }
}

async function getJson<T>(path: string): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${DJANGO_URL}${path}`, {
      cache: "no-store",
      headers: { Accept: "application/json" },
    });
  } catch {
    throw new DjangoApiError(0, "Nie można połączyć się z Django (port 8000). Sprawdź, czy backend działa.");
  }
  if (!response.ok) {
    throw new DjangoApiError(response.status, `Django API zwróciło HTTP ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function getRecipes(query = "", page = 1): Promise<RecipeListResponse> {
  const params = new URLSearchParams();
  if (query) params.set("q", query);
  if (page > 1) params.set("page", String(page));
  const suffix = params.size ? `?${params.toString()}` : "";
  return getJson<RecipeListResponse>(`/api/recipes/${suffix}`);
}


/** Score-based pantry recommendations, excluding cards currently visible. */
export async function getHomeRecipeSuggestions(
  excludedIds: number[] = [],
  count = 3,
): Promise<HomeRecipeSuggestion[]> {
  const params = new URLSearchParams({ count: String(count) });
  const ids = excludedIds.filter((id) => Number.isSafeInteger(id) && id > 0).slice(0, 30);
  if (ids.length) params.set("exclude", ids.join(","));
  const data = await getJson<{ results: HomeRecipeSuggestion[] }>(
    `/api/recommendations/?${params.toString()}`,
  );
  return data.results;
}

export async function getRecipe(id: number): Promise<RecipeDetail> {
  return getJson<RecipeDetail>(`/api/recipes/${id}/`);
}


export type ShoppingLine = {
  ingredient_id: number;
  ingredient_name: string;
  unit: string;
  needed: string;
  in_stock: string;
  to_buy: string;
};

export async function getShoppingList(): Promise<ShoppingLine[]> {
  return getJson<ShoppingLine[]>("/api/shopping/");
}

/** Run only on the server: the backend service name is internal to Docker. */
export async function postShopping<T>(path: string, body: unknown): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${DJANGO_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
    });
  } catch {
    throw new DjangoApiError(0, "Nie można połączyć się z Django.");
  }
  if (!response.ok) {
    throw new DjangoApiError(response.status, `Django API zwróciło HTTP ${response.status}`);
  }
  return (await response.json()) as T;
}

// Pantry uses the same demo user and PostgreSQL stock batches as shopping.
export type PantryIngredient = {
  id: number;
  name: string;
  unit: "g" | "ml" | "pcs";
};

export type PantryItem = {
  id: number;
  ingredient_id: number;
  ingredient_name: string;
  product_name: string;
  amount: string;
  unit: "g" | "ml" | "pcs";
  expires_on: string | null;
  expiry_status: "none" | "fresh" | "soon" | "expired";
};

export type PantryPayload = {
  ingredient_id: number;
  amount: string;
  expires_on: string | null;
};

export function getPantry(): Promise<PantryItem[]> {
  return getJson<PantryItem[]>("/api/pantry/");
}

export function getPantryIngredients(): Promise<PantryIngredient[]> {
  return getJson<PantryIngredient[]>("/api/pantry/ingredients/");
}

/** Mutations are called by Server Actions, never directly by browser components. */
export async function mutatePantry<T>(
  path: string,
  method: "POST" | "PATCH" | "DELETE",
  body?: PantryPayload,
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${DJANGO_URL}${path}`, {
      method,
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
      cache: "no-store",
    });
  } catch {
    throw new DjangoApiError(0, "Nie można połączyć się z Django.");
  }
  if (!response.ok) {
    let details = "";
    try { details = JSON.stringify(await response.json()); } catch { /* optional details */ }
    throw new DjangoApiError(response.status, `Django API zwróciło HTTP ${response.status}${details ? `: ${details}` : ""}`);
  }
  return (await response.json()) as T;
}
