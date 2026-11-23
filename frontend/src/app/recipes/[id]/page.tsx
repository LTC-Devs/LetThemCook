import Link from "next/link";
import { notFound } from "next/navigation";
import { DjangoApiError, getRecipe } from "@/lib/django";
import type { RecipeDetail, RecipeItem } from "@/types/recipe-api";

const UNITS = { g: "g", ml: "ml", pcs: "szt." };

/** e.g. "śmietana — 2–3 łyżki (30–45 ml)" or "szynka — 100 g" */
function ingredientLine(item: RecipeItem) {
  const amount = item.amount === null ? ""
    : `${Number(item.amount)}${item.amount_max ? `–${Number(item.amount_max)}` : ""} ${UNITS[item.unit]}`;
  const measure = item.quantity_note && amount ? `${item.quantity_note} (${amount})` : item.quantity_note || amount;
  return [item.ingredient, measure].filter(Boolean).join(" — ") + (item.is_optional ? " (opcjonalnie)" : "");
}


type Props = { params: Promise<{ id: string }> };

export default async function RecipeDetailPage({ params }: Props) {
  const { id } = await params;
  const recipeId = Number(id);
  if (!Number.isSafeInteger(recipeId) || recipeId < 1) notFound();

  let recipe: RecipeDetail | null = null;
  let errorMessage: string | null = null;
  try {
    recipe = await getRecipe(recipeId);
  } catch (error) {
    if (error instanceof DjangoApiError && error.status === 404) notFound();
    errorMessage = error instanceof Error ? error.message : "Błąd pobierania przepisu.";
  }

  if (!recipe) {
    return (
      <div role="alert" className="rounded-xl border border-red-200 bg-red-50 p-5 text-red-900">
        {errorMessage ?? "Nie można odczytać przepisu."}
      </div>
    );
  }

  const ingredientLines = recipe.items.map(ingredientLine);

  return (
    <article className="space-y-7">
      <Link href="/recipes" className="text-sm font-medium text-emerald-800 hover:underline">Wszystkie przepisy</Link>
      <header className="space-y-2">
        <h1 className="text-3xl font-bold">{recipe.name}</h1>
        <p className="text-zinc-600">
          {recipe.category ?? "Bez kategorii"}{recipe.base_servings ? ` · porcje: ${recipe.base_servings}` : ""}
        </p>
      </header>
      <Link href={`/shopping?recipe=${recipe.id}`}
        className="inline-block rounded-xl bg-[#C24B36] px-4 py-3 text-white font-semibold">
        Dodaj przepis do planu zakupów
      </Link>
      <section className="rounded-xl border border-zinc-200 bg-white p-6">
        <h2 className="mb-3 text-xl font-semibold">Składniki</h2>
        {ingredientLines.length ? (
          <ul className="list-disc space-y-1 pl-5">
            {ingredientLines.map((item, index) => <li key={index}>{item}</li>)}
          </ul>
        ) : <p className="text-zinc-600">Brak składników w bazie.</p>}
      </section>
      <section className="rounded-xl border border-zinc-200 bg-white p-6">
        <h2 className="mb-3 text-xl font-semibold">Przygotowanie</h2>
        {recipe.steps.length ? (
          <ol className="list-decimal space-y-2 pl-5 text-zinc-700">
            {recipe.steps.map((step, index) => <li key={index}>{step}</li>)}
          </ol>
        ) : <p className="text-zinc-600">Brak instrukcji w bazie.</p>}
      </section>
    </article>
  );
}
