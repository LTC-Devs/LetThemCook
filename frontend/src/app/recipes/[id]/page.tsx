import Link from "next/link";
import { notFound } from "next/navigation";
import { DjangoApiError, getRecipe } from "@/lib/django";
import type { RecipeDetail } from "@/types/recipe-api";


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

  const ingredientLines = recipe.items.length
    ? recipe.items.map((item) => item.raw_text || [item.amount, item.unit, item.ingredient].filter(Boolean).join(" "))
    : recipe.raw_ingredients;

  return (
    <article className="space-y-7">
      <Link href="/recipes" className="text-sm font-medium text-emerald-800 hover:underline">Wszystkie przepisy</Link>
      <header className="space-y-2">
        <h1 className="text-3xl font-bold">{recipe.title}</h1>
        <p className="text-zinc-600">{recipe.category ?? "Bez kategorii"} · {recipe.cookbook ?? "Przepis ogólny"}</p>
        {recipe.parsing_status !== "verified" && (
          <p className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
            Ten przepis nie został jeszcze zweryfikowany po imporcie/OCR.
          </p>
        )}
      </header>
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
        <p className="whitespace-pre-wrap text-zinc-700">{recipe.instructions || "Brak instrukcji w bazie."}</p>
      </section>
    </article>
  );
}
