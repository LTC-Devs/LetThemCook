"use client";

import { useRef, useState } from "react";
import Link from "next/link";
import { motion, type PanInfo } from "framer-motion";
import { ArrowLeftRight, ArrowUpRight, BookOpen, Search, Shuffle } from "lucide-react";
import AppLayout from "@/components/layout/AppLayout";
import { drawAnotherBookRecipe } from "@/app/home-actions";
import type { HomeRecipeSuggestion } from "@/types/recipe-api";

const PALETTE = ["bg-[#DCE6D0]", "bg-[#EAE3F2]", "bg-[#F3EBE1]", "bg-[#FDE4D8]"];

function ingredientPreview(recipe: HomeRecipeSuggestion, max = 5): string {
  if (!recipe.ingredients.length) return "Składniki nie zostały jeszcze uzupełnione.";
  const names = recipe.ingredients.slice(0, max).join(", ");
  return recipe.ingredients.length > max ? `${names}…` : `${names}.`;
}

export default function HomeClient({ initialSuggestions }: {
  initialSuggestions: HomeRecipeSuggestion[];
}) {
  const [suggestions, setSuggestions] = useState(initialSuggestions);
  const [loadingIndex, setLoadingIndex] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const dismissedIds = useRef<number[]>([]);

  const replace = async (index: number) => {
    if (loadingIndex !== null) return;
    setLoadingIndex(index);
    setError(null);
    try {
      const excluded = [...new Set([...dismissedIds.current, ...suggestions.map(({ id }) => id)])].slice(-30);
      const next = await drawAnotherBookRecipe(excluded);
      if (!next) {
        setError("Brak kolejnych propozycji w książce.");
        return;
      }
      dismissedIds.current = [...dismissedIds.current, suggestions[index].id].slice(-27);
      setSuggestions((current) => current.map((recipe, i) => i === index ? next : recipe));
    } catch {
      setError("Nie udało się pobrać kolejnej rekomendacji. Spróbuj ponownie.");
    } finally {
      setLoadingIndex(null);
    }
  };

  const onSwipe = (index: number) => (_: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    if (Math.abs(info.offset.x) > 100) void replace(index);
  };

  const featured = suggestions[0];
  const upcoming = suggestions.slice(1);

  return (
    <AppLayout userInitial="L">
      <h1 className="font-nunito text-[2.1rem] leading-tight font-extrabold text-[#2D2623] tracking-tight mb-6">
        Hej, co gotujemy?
      </h1>

      {suggestions.length > 0 && suggestions.every((recipe) => recipe.score === 0) && (
        <p className="rounded-2xl bg-white/75 p-4 mb-4 text-sm text-[#6C5D53]">
          Nie znaleziono jeszcze dopasowania do zapasów. Dodaj produkty w spiżarni, aby ranking uwzględnił ich ilości i terminy ważności.
        </p>
      )}

      {featured ? (
        <div className="flex flex-col items-center">
          <motion.article
            key={featured.id}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            drag={loadingIndex === null ? "x" : false}
            dragConstraints={{ left: 0, right: 0 }}
            dragSnapToOrigin
            onDragEnd={onSwipe(0)}
            className="w-full rounded-[2rem] p-6 shadow-sm bg-[#F4CBB3] cursor-grab active:cursor-grabbing"
          >
            <div className="flex items-center justify-between gap-3 text-xs tracking-wider uppercase font-bold text-[#C24B36] mb-4">
              <span className="flex items-center gap-2"><BookOpen size={17} /> DOPASOWANE DO SPIŻARNI</span>
              <span className="text-[#6C5D53]">1985</span>
            </div>
            <h2 className="font-nunito text-4xl font-extrabold text-[#2D2623] leading-tight mb-6">
              {featured.name}
            </h2>
            <h3 className="text-[11px] font-bold tracking-widest uppercase mb-1 text-[#C24B36]">
              Składniki
            </h3>
            <p className="text-[#4A423D] text-sm leading-relaxed mb-4 pr-4">
              {ingredientPreview(featured)}
            </p>
            <p className="text-[#6C5D53] text-xs mb-4">
              {featured.category ?? "Kuchnia polska"}
              {featured.base_servings ? ` · ${featured.base_servings} porcje` : ""}
            </p>
            <div className="rounded-2xl bg-white/55 px-3 py-3 mb-4 text-[#4A423D]">
              <div className="flex justify-between items-baseline gap-2 font-bold text-sm mb-2">
                <span>Wynik dopasowania</span>
                <span className="text-[#C24B36] text-xl">{featured.score}/100 pkt</span>
              </div>
              <div className="grid grid-cols-3 gap-2 text-center text-[11px] leading-snug">
                <div><strong className="block text-sm">{featured.score_breakdown.availability}/60</strong>Dostępność</div>
                <div><strong className="block text-sm">{featured.score_breakdown.few_missing}/25</strong>Pełne składniki</div>
                <div><strong className="block text-sm">{featured.score_breakdown.expiry}/15</strong>Krótka ważność</div>
              </div>
              <p className="text-xs mt-2">
                Brakuje: {featured.missing_ingredients_count} z {featured.scored_ingredients_count} wymaganych składników.
              </p>
              {featured.unquantified_ingredients_count > 0 && (
                <p className="text-[11px] text-[#6C5D53] mt-1">
                  {featured.unquantified_ingredients_count} składników bez określonej ilości pominięto w punktacji.
                </p>
              )}
            </div>
            <div className="h-px bg-[#E3B8A0] mb-5" />
            <div className="flex gap-3" onPointerDown={(event) => event.stopPropagation()}>
              <Link
                href={`/recipes/${featured.id}`}
                className="flex-1 rounded-2xl py-4 flex items-center justify-center gap-2 bg-[#C24B36] text-white font-semibold shadow-sm active:scale-95 transition-transform"
              >
                Przejdź do przepisu <ArrowUpRight size={18} strokeWidth={2.5} />
              </Link>
              <button
                type="button"
                disabled={loadingIndex !== null}
                onClick={() => void replace(0)}
                aria-label="Pokaż kolejną rekomendację"
                className="w-[60px] shrink-0 rounded-2xl bg-white text-[#C24B36] flex items-center justify-center shadow-sm active:scale-95 transition-transform disabled:opacity-50"
              >
                <Shuffle size={20} strokeWidth={2.5} />
              </button>
            </div>
          </motion.article>
          <p className="flex items-center gap-2 mt-4 text-[#8C837C] text-xs font-medium">
            <ArrowLeftRight size={14} /> Przesuń kartę, aby zobaczyć kolejną rekomendację.
          </p>
        </div>
      ) : (
        <p className="rounded-2xl bg-white p-5">Brak przepisów z określonymi ilościami składników.</p>
      )}

      {upcoming.length > 0 && (
        <section className="mt-8 space-y-4">
          <h2 className="font-nunito text-2xl font-extrabold text-[#2D2623] px-1">
            Kolejne dopasowane przepisy
          </h2>
          <div className="space-y-3">
            {upcoming.map((recipe, offset) => {
              const index = offset + 1;
              return (
                <motion.article
                  key={`${index}-${recipe.id}`}
                  initial={{ opacity: 0, x: 25 }}
                  animate={{ opacity: 1, x: 0 }}
                  drag={loadingIndex === null ? "x" : false}
                  dragConstraints={{ left: 0, right: 0 }}
                  dragSnapToOrigin
                  onDragEnd={onSwipe(index)}
                  className={`w-full ${PALETTE[offset % PALETTE.length]} rounded-[1.5rem] p-4 flex items-center gap-3 cursor-grab active:cursor-grabbing`}
                >
                  <div className="flex items-center justify-center min-w-12 text-[#4A423D]">
                    <BookOpen size={24} strokeWidth={1.8} />
                  </div>
                  <div className="h-12 w-px bg-black/5" />
                  <Link
                    href={`/recipes/${recipe.id}`}
                    onPointerDown={(event) => event.stopPropagation()}
                    className="flex-1 min-w-0"
                  >
                    <h3 className="font-nunito text-[1.1rem] font-bold text-[#2D2623] leading-tight">
                      {recipe.name}
                    </h3>
                    <p className="text-xs text-[#6B6661] italic mt-1 line-clamp-2">
                      {ingredientPreview(recipe, 3)}
                    </p>
                    <p className="text-xs text-[#6B6661] mt-1">
                      {recipe.score}/100 pkt · Brakuje {recipe.missing_ingredients_count} składników
                    </p>
                  </Link>
                  <div className="flex items-center gap-1" onPointerDown={(event) => event.stopPropagation()}>
                    <button
                      type="button"
                      aria-label={`Pokaż następną propozycję zamiast ${recipe.name}`}
                      disabled={loadingIndex !== null}
                      onClick={() => void replace(index)}
                      className="bg-white/80 text-[#C24B36] rounded-full p-2 active:scale-95 transition-transform disabled:opacity-50"
                    >
                      <Shuffle size={16} />
                    </button>
                    <Link href={`/recipes/${recipe.id}`} aria-label={`Otwórz ${recipe.name}`}>
                      <ArrowUpRight size={20} />
                    </Link>
                  </div>
                </motion.article>
              );
            })}
          </div>
        </section>
      )}

      {error && <p role="alert" className="mt-4 text-sm text-red-700">{error}</p>}
      <Link
        href="/recipes"
        className="w-full mt-6 flex items-center justify-center gap-2 py-4 rounded-2xl bg-[#FCF8F3] text-[#C24B36] font-semibold text-sm border border-[#F4EBE1] active:scale-95 transition-transform"
      >
        <Search size={18} strokeWidth={2.5} />
        Szukaj przepisów w książce
      </Link>
    </AppLayout>
  );
}
