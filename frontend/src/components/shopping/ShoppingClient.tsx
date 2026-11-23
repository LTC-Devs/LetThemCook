"use client";

import { useEffect, useState, useTransition, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import AppLayout from "@/components/layout/AppLayout";
import { Plus, ArrowRightToLine } from "lucide-react";
import type { ShoppingLine } from "@/lib/django";
import { planRecipeAction, purchaseAction } from "@/app/shopping/actions";

const STORAGE_KEY = "ltc-demo-shopping-checked-v1";

type Props = {
  initialData: ShoppingLine[];
  loadError?: string;
  initialRecipeId?: string;
};

export default function ShoppingClient({ initialData, loadError, initialRecipeId = "" }: Props) {
  const router = useRouter();
  const [checked, setChecked] = useState<number[]>([]);
  const [showPlan, setShowPlan] = useState(Boolean(initialRecipeId));
  const [recipeId, setRecipeId] = useState(initialRecipeId);
  const [servings, setServings] = useState("4");
  const [message, setMessage] = useState("");
  const [pending, startTransition] = useTransition();

  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "[]");
      if (Array.isArray(saved)) setChecked(saved.filter((id) => Number.isInteger(id)));
    } catch { /* An invalid local preference should not block the page. */ }
  }, []);

  const toggleCheck = (id: number) => {
    setChecked((previous) => {
      const next = previous.includes(id) ? previous.filter((value) => value !== id) : [...previous, id];
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      return next;
    });
  };

  const selected = initialData.filter((line) => checked.includes(line.ingredient_id)).map((line) => line.ingredient_id);

  const addRecipe = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setMessage("");
    startTransition(async () => {
      const result = await planRecipeAction(Number(recipeId), Number(servings));
      if (result.ok) {
        setMessage("Przepis dodany do planu. Lista została przeliczona.");
        setShowPlan(false);
        setRecipeId("");
        router.refresh();
      } else setMessage(result.message ?? "Nie udało się dodać przepisu.");
    });
  };

  const purchase = () => {
    setMessage("");
    startTransition(async () => {
      const result = await purchaseAction(selected);
      if (result.ok) {
        const rest = checked.filter((id) => !selected.includes(id));
        setChecked(rest);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(rest));
        setMessage("Zakupy dodano do spiżarni. Brakujące ilości zostały przeliczone.");
        router.refresh();
      } else setMessage(result.message ?? "Nie udało się dodać do spiżarni.");
    });
  };

  return (
    <AppLayout userInitial="L">
      <h1 className="font-nunito text-[2.1rem] leading-tight font-extrabold text-[#2D2623] tracking-tight mb-2">
        Lista zakupów
      </h1>
      <p className="text-sm text-[#8C837C] mb-6">Tryb demo · składniki z zaplanowanych przepisów</p>

      <div className="flex flex-col gap-3 mb-5">
        <button onClick={() => setShowPlan((value) => !value)}
          className="w-full bg-white border border-[#F2ECE4] text-[#2D2623] rounded-xl py-3 flex items-center justify-center gap-2 font-semibold text-sm shadow-sm">
          <Plus size={16} strokeWidth={2.5} /> Dodaj przepis do planu
        </button>
        {showPlan && (
          <form onSubmit={addRecipe} className="bg-white p-4 rounded-xl border border-[#F2ECE4] flex flex-col gap-3">
            <p className="text-sm text-[#5F554E]">ID znajdziesz w adresie przepisu, np. /recipes/1</p>
            <label className="text-sm font-semibold">ID przepisu
              <input type="number" min="1" value={recipeId} required onChange={(e) => setRecipeId(e.target.value)}
                className="block w-full p-2 mt-1 border rounded-lg" />
            </label>
            <label className="text-sm font-semibold">Liczba porcji
              <input type="number" min="1" max="99" value={servings} required onChange={(e) => setServings(e.target.value)}
                className="block w-full p-2 mt-1 border rounded-lg" />
            </label>
            <button type="submit" disabled={pending} className="bg-[#C24B36] text-white rounded-xl py-3 font-semibold disabled:opacity-50">
              {pending ? "Dodawanie…" : "Zaplanuj przepis"}
            </button>
          </form>
        )}
        <button onClick={purchase} disabled={pending || selected.length === 0 || !!loadError}
          className="w-full bg-[#C24B36] text-white rounded-xl py-3 flex items-center justify-center gap-2 font-semibold text-sm disabled:opacity-50">
          <ArrowRightToLine size={16} strokeWidth={2.5} /> Przenieś zaznaczone do spiżarni ({selected.length})
        </button>
      </div>

      {loadError && <p role="alert" className="text-red-700 bg-red-50 rounded-xl p-3 mb-3">{loadError}</p>}
      {message && <p role="status" className="text-[#3F5B3B] bg-[#ECF2E8] rounded-xl p-3 mb-3">{message}</p>}
      {!loadError && initialData.length === 0 && (
        <p className="text-[#665B53] bg-white border border-[#F2ECE4] rounded-xl p-5">
          Lista jest pusta. Dodaj przepis do planu albo wszystkie potrzebne ilości są już w spiżarni.
        </p>
      )}
      <div className="space-y-3">
        {initialData.map((item) => {
          const isChecked = checked.includes(item.ingredient_id);
          return (
            <label key={item.ingredient_id}
              className={`w-full rounded-[1.2rem] p-4 flex items-center gap-4 cursor-pointer transition-colors ${isChecked ? "bg-[#F2ECE4]/50" : "bg-white border border-[#F2ECE4] shadow-sm"}`}>
              <div className="relative flex items-center justify-center">
                <input type="checkbox" checked={isChecked} onChange={() => toggleCheck(item.ingredient_id)}
                  className="peer appearance-none w-6 h-6 border-2 border-[#DCE6D0] rounded-md checked:bg-[#8CA86E] checked:border-[#8CA86E] transition-colors" />
                <svg className="absolute w-4 h-4 text-white pointer-events-none opacity-0 peer-checked:opacity-100"
                  fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div className="flex-1">
                <p className={`font-nunito text-[1.1rem] font-bold ${isChecked ? "text-[#8C837C] line-through" : "text-[#2D2623]"}`}>
                  {item.ingredient_name} ({Number(item.to_buy).toLocaleString("pl-PL", { maximumFractionDigits: 2 })} {item.unit === "pcs" ? "szt." : item.unit})
                </p>
                <p className="text-xs italic text-[#8C837C] mt-0.5">Potrzeba: {Number(item.needed)} · w spiżarni: {Number(item.in_stock)}</p>
              </div>
            </label>
          );
        })}
      </div>
    </AppLayout>
  );
}
