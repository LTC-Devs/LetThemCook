import type { RecipeDetail, RecipeListResponse } from "@/types/recipe-api";

/** Server-side API client: import it only from Next.js Server Components. */
const DJANGO_URL = (process.env.BACKEND_API_BASE_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

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

export async function getRecipe(id: number): Promise<RecipeDetail> {
  return getJson<RecipeDetail>(`/api/recipes/${id}/`);
}
