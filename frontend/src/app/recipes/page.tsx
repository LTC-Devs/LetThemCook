import Link from "next/link";
import { getRecipes } from "@/lib/django";
import type { RecipeListResponse } from "@/types/recipe-api";


type Props = { searchParams: Promise<{ q?: string; page?: string }> };

export default async function RecipesPage({ searchParams }: Props) {
  const params = await searchParams;
  const q = (params.q ?? "").trim();
  const requestedPage = Number(params.page ?? "1");
  const page = Number.isSafeInteger(requestedPage) && requestedPage > 0 ? requestedPage : 1;
  let data: RecipeListResponse | null = null;
  let errorMessage: string | null = null;

  try {
    data = await getRecipes(q, page);
  } catch (error) {
    errorMessage = error instanceof Error ? error.message : "Błąd pobierania przepisów.";
  }

  const pageLink = (value: number) => `/recipes?${new URLSearchParams({ ...(q ? { q } : {}), page: String(value) })}`;

  return (
    <section className="space-y-6">
      <div className="space-y-2">
        <p className="text-sm font-semibold uppercase tracking-wider text-emerald-700">LTC / książka kucharska</p>
        <h1 className="text-3xl font-bold">Przepisy</h1>
        <p className="text-zinc-600">Przepisy z Django ORM / PostgreSQL.</p>
      </div>

      <form action="/recipes" method="get" className="flex flex-wrap gap-2">
        <label htmlFor="recipe-query" className="sr-only">Szukaj przepisu</label>
        <input
          id="recipe-query" type="search" name="q" defaultValue={q}
          placeholder="Wpisz nazwę przepisu"
          className="w-full max-w-md rounded-lg border border-zinc-300 bg-white px-3 py-2"
        />
        <button type="submit" className="rounded-lg bg-emerald-700 px-4 py-2 font-medium text-white">Szukaj</button>
      </form>

      {errorMessage ? (
        <div role="alert" className="rounded-xl border border-red-200 bg-red-50 p-5 text-red-900">
          <p className="font-semibold">Nie udało się pobrać danych z Django.</p>
          <p className="mt-2 text-sm">{errorMessage}</p>
        </div>
      ) : data?.count === 0 ? (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-5 text-amber-950">
          {q ? "Nie znaleziono przepisów pasujących do wyszukiwania." : "Baza działa, ale nie ma jeszcze zapisanych publicznych przepisów. Dodaj jeden przez Django Admin, aby przetestować listę."}
        </div>
      ) : (
        <>
          <p className="text-sm text-zinc-600">Znaleziono: {data?.count ?? 0}</p>
          <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {data?.results.map((recipe) => (
              <li key={recipe.id} className="rounded-xl border border-zinc-200 bg-white p-5 shadow-sm">
                <Link href={`/recipes/${recipe.id}`} className="text-lg font-semibold text-emerald-800 hover:underline">
                  {recipe.title}
                </Link>
                <p className="mt-2 text-sm text-zinc-600">{recipe.category ?? "Bez kategorii"}</p>
                <p className="mt-1 text-xs text-zinc-500">{recipe.cookbook ?? "Przepis ogólny"}</p>
                {recipe.parsing_status !== "verified" && (
                  <p className="mt-3 text-xs text-amber-700">Przepis niezweryfikowany</p>
                )}
              </li>
            ))}
          </ul>
          {data && data.pages > 1 && (
            <nav aria-label="Paginacja" className="flex gap-4 text-sm">
              {data.page > 1 && <Link href={pageLink(data.page - 1)} className="text-emerald-800 underline">Poprzednia</Link>}
              <span>Strona {data.page} z {data.pages}</span>
              {data.page < data.pages && <Link href={pageLink(data.page + 1)} className="text-emerald-800 underline">Następna</Link>}
            </nav>
          )}
        </>
      )}
    </section>
  );
}
