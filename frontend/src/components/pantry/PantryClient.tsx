"use client";

import { useState, useTransition, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import AppLayout from "@/components/layout/AppLayout";
import { Plus, ScanLine, Pencil, Trash2, AlertTriangle, X, Check, Search } from "lucide-react";
import type { PantryIngredient, PantryItem, PantryPayload } from "@/lib/django";
import { createPantryAction, updatePantryAction, removePantryAction } from "@/app/pantry/actions";

type Props = {
  initialData: PantryItem[];
  ingredients: PantryIngredient[];
  loadError?: string;
};

type Draft = {
  ingredientId: number | null;
  ingredientName: string;
  amount: string;
  expiresOn: string;
};

const EMPTY: Draft = { ingredientId: null, ingredientName: "", amount: "", expiresOn: "" };

function displayUnit(unit: string): string {
  return unit === "pcs" ? "szt." : unit;
}

function displayDate(value: string): string {
  const [year, month, day] = value.split("-");
  return `${day}.${month}.${year}`;
}

function expiryLabel(item: PantryItem): string | null {
  if (!item.expires_on) return null;
  if (item.expiry_status === "expired") return `Po terminie: ${displayDate(item.expires_on)}`;
  if (item.expiry_status === "soon") return `Termin wkrótce: ${displayDate(item.expires_on)}`;
  return `Ważne do: ${displayDate(item.expires_on)}`;
}

export default function PantryClient({ initialData, ingredients, loadError }: Props) {
  const router = useRouter();
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [draft, setDraft] = useState<Draft>(EMPTY);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [pendingDeleteId, setPendingDeleteId] = useState<number | null>(null);
  const [pending, startTransition] = useTransition();

  const options = ingredients
    .filter((ingredient) => ingredient.name.toLocaleLowerCase("pl-PL").includes(draft.ingredientName.toLocaleLowerCase("pl-PL")))
    .slice(0, 8);

  const chosen = ingredients.find((ingredient) => ingredient.id === draft.ingredientId);

  const startAdd = () => {
    setEditingId(null);
    setDraft(EMPTY);
    setShowForm(true);
    setError("");
    setPendingDeleteId(null);
  };

  const startEdit = (item: PantryItem) => {
    setEditingId(item.id);
    setDraft({
      ingredientId: item.ingredient_id,
      ingredientName: item.ingredient_name,
      amount: String(Number(item.amount)),
      expiresOn: item.expires_on ?? "",
    });
    setShowForm(true);
    setError("");
    setPendingDeleteId(null);
  };

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setMessage("");
    if (draft.ingredientId === null) {
      setError("Wybierz składnik z podpowiedzi, nie tylko wpisz jego nazwę.");
      return;
    }
    const payload: PantryPayload = {
      ingredient_id: draft.ingredientId,
      amount: draft.amount,
      expires_on: draft.expiresOn || null,
    };
    startTransition(async () => {
      const result = editingId === null
        ? await createPantryAction(payload)
        : await updatePantryAction(editingId, payload);
      if (result.ok) {
        setMessage(editingId === null ? "Produkt dodany do spiżarni." : "Zapisano zmiany produktu.");
        setShowForm(false);
        setEditingId(null);
        setDraft(EMPTY);
        router.refresh();
      } else {
        setError(result.message ?? "Nie udało się zapisać produktu.");
      }
    });
  };

  const remove = (id: number) => {
    setError("");
    setMessage("");
    startTransition(async () => {
      const result = await removePantryAction(id);
      if (result.ok) {
        setPendingDeleteId(null);
        setMessage("Produkt usunięty z dostępnej spiżarni.");
        router.refresh();
      } else {
        setError(result.message ?? "Nie udało się usunąć produktu.");
      }
    });
  };

  return (
    <AppLayout userInitial="L">
      <h1 className="font-nunito text-[2.1rem] leading-tight font-extrabold text-[#2D2623] tracking-tight mb-2">
        Spiżarnia
      </h1>
      <p className="text-sm text-[#8C837C] mb-6">Produkty zapisane w PostgreSQL · tryb demo</p>

      <div className="flex gap-3 mb-6">
        <button type="button" onClick={startAdd} disabled={pending || !!loadError}
          className="flex-1 bg-[#C24B36] text-white rounded-xl py-3 flex items-center justify-center gap-2 font-semibold text-sm shadow-sm disabled:opacity-50 active:scale-95 transition-transform">
          <Plus size={16} strokeWidth={2.5} /> Dodaj ręcznie
        </button>
        <button type="button" disabled title="Skanowanie produktów będzie dostępne w kolejnej wersji"
          className="flex-1 bg-[#F4CBB3] text-[#2D2623] rounded-xl py-3 flex items-center justify-center gap-2 font-semibold text-sm shadow-sm opacity-60 cursor-not-allowed">
          <ScanLine size={16} strokeWidth={2.5} /> Skanuj (wkrótce)
        </button>
      </div>

      {loadError && <p role="alert" className="mb-4 rounded-xl bg-red-50 text-red-700 p-3 text-sm">{loadError}</p>}
      {message && <p role="status" className="mb-4 rounded-xl bg-[#ECF2E8] text-[#3F5B3B] p-3 text-sm">{message}</p>}
      {error && <p role="alert" className="mb-4 rounded-xl bg-red-50 text-red-700 p-3 text-sm">{error}</p>}

      {showForm && !loadError && (
        <form onSubmit={submit} className="mb-6 bg-white border border-[#F2ECE4] shadow-sm rounded-[1.2rem] p-4 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-nunito font-extrabold text-[#2D2623] text-lg">{editingId === null ? "Dodaj produkt" : "Edytuj produkt"}</h2>
            <button type="button" aria-label="Zamknij formularz" onClick={() => setShowForm(false)} disabled={pending}
              className="rounded-full p-2 text-[#8C837C] hover:bg-[#FDFBF7]"><X size={20} /></button>
          </div>

          <div>
            <label htmlFor="pantry-search" className="block font-semibold text-sm text-[#2D2623] mb-1">Składnik z książki</label>
            <div className="relative">
              <Search size={17} className="absolute left-3 top-3 text-[#8C837C]" />
              <input id="pantry-search" type="search" value={draft.ingredientName}
                onChange={(e) => setDraft((previous) => ({ ...previous, ingredientId: null, ingredientName: e.target.value }))}
                placeholder="Zacznij wpisywać, np. szynka" autoComplete="off" disabled={pending}
                className="w-full border border-[#EAE3DA] rounded-xl py-2.5 pl-10 pr-3 outline-none focus:border-[#C24B36] text-sm" />
            </div>
            {chosen ? (
              <p className="mt-2 text-sm text-[#3F5B3B] flex items-center gap-1"><Check size={15} /> Wybrano: {chosen.name} ({displayUnit(chosen.unit)})</p>
            ) : (
              <div className="mt-2 border border-[#F2ECE4] rounded-xl overflow-hidden max-h-48 overflow-y-auto">
                {options.map((ingredient) => (
                  <button type="button" key={ingredient.id}
                    onClick={() => setDraft((previous) => ({ ...previous, ingredientId: ingredient.id, ingredientName: ingredient.name }))}
                    className="w-full text-left px-3 py-2 text-sm hover:bg-[#FDF7F0] flex justify-between gap-2 border-b last:border-0 border-[#F2ECE4]">
                    <span>{ingredient.name}</span><span className="text-[#8C837C] shrink-0">{displayUnit(ingredient.unit)}</span>
                  </button>
                ))}
                {options.length === 0 && <p className="px-3 py-3 text-[#8C837C] text-sm">Brak takiego składnika w bazie.</p>}
              </div>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="pantry-amount" className="block font-semibold text-sm text-[#2D2623] mb-1">Ilość {chosen ? `(${displayUnit(chosen.unit)})` : ""}</label>
              <input id="pantry-amount" type="number" min="0.0001" step="0.0001" required disabled={pending}
                value={draft.amount} onChange={(e) => setDraft((previous) => ({ ...previous, amount: e.target.value }))}
                placeholder="np. 100" className="w-full border border-[#EAE3DA] rounded-xl p-2.5 outline-none focus:border-[#C24B36] text-sm" />
            </div>
            <div>
              <label htmlFor="pantry-expiry" className="block font-semibold text-sm text-[#2D2623] mb-1">Data ważności</label>
              <input id="pantry-expiry" type="date" disabled={pending}
                value={draft.expiresOn} onChange={(e) => setDraft((previous) => ({ ...previous, expiresOn: e.target.value }))}
                className="w-full border border-[#EAE3DA] rounded-xl p-2.5 outline-none focus:border-[#C24B36] text-sm" />
            </div>
          </div>
          <p className="text-xs text-[#8C837C]">Ilości zapisujemy w g, ml lub sztukach. Data ważności jest opcjonalna.</p>
          <button type="submit" disabled={pending || draft.ingredientId === null}
            className="w-full bg-[#C24B36] text-white rounded-xl py-3 font-semibold text-sm disabled:opacity-50">
            {pending ? "Zapisywanie…" : editingId === null ? "Dodaj do spiżarni" : "Zapisz zmiany"}
          </button>
        </form>
      )}

      {!loadError && initialData.length === 0 && (
        <div className="bg-white border border-[#F2ECE4] rounded-[1.2rem] p-5 text-[#665B53] text-sm">
          Spiżarnia jest pusta. Dodaj produkt ręcznie albo przenieś składniki z listy zakupów.
        </div>
      )}

      <div className="space-y-3">
        {initialData.map((item) => (
          <div key={item.id} className="w-full bg-white border border-[#F2ECE4] rounded-[1.2rem] p-4 shadow-sm">
            <div className="flex items-center justify-between gap-2">
              <div className="min-w-0">
                <h3 className="font-nunito text-[1.1rem] font-bold text-[#2D2623] break-words">{item.ingredient_name}</h3>
                <p className="text-sm text-[#8C837C] font-medium mt-0.5">
                  Ilość: {Number(item.amount).toLocaleString("pl-PL", { maximumFractionDigits: 4 })} {displayUnit(item.unit)}
                </p>
                {item.expires_on && (
                  <p className={`flex items-center gap-1 mt-1 text-xs font-semibold ${
                    item.expiry_status === "expired" ? "text-red-700" : item.expiry_status === "soon" ? "text-amber-700" : "text-[#7D8D69]"
                  }`}>
                    {(item.expiry_status === "expired" || item.expiry_status === "soon") && <AlertTriangle size={13} />}
                    {expiryLabel(item)}
                  </p>
                )}
                {item.expiry_status === "expired" && <p className="text-xs text-red-700 mt-1">Nie liczy się do dostępnych składników.</p>}
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <button type="button" aria-label={`Edytuj ${item.ingredient_name}`} onClick={() => startEdit(item)} disabled={pending}
                  className="p-2 text-[#8C837C] hover:text-[#2D2623] bg-[#FDFBF7] rounded-full disabled:opacity-50 active:scale-90 transition-transform"><Pencil size={18} /></button>
                <button type="button" aria-label={`Usuń ${item.ingredient_name}`} onClick={() => setPendingDeleteId(item.id)} disabled={pending}
                  className="p-2 text-[#C24B36] hover:bg-[#FEF2F2] bg-[#FDFBF7] rounded-full disabled:opacity-50 active:scale-90 transition-transform"><Trash2 size={18} /></button>
              </div>
            </div>
            {pendingDeleteId === item.id && (
              <div className="mt-3 pt-3 border-t border-[#F2ECE4] text-sm">
                <p className="mb-2 text-[#665B53]">Usunąć tę partię z dostępnej spiżarni?</p>
                <div className="flex gap-2">
                  <button type="button" disabled={pending} onClick={() => remove(item.id)}
                    className="px-4 py-2 rounded-lg bg-[#C24B36] text-white font-semibold disabled:opacity-50">Usuń</button>
                  <button type="button" disabled={pending} onClick={() => setPendingDeleteId(null)}
                    className="px-4 py-2 rounded-lg bg-[#F2ECE4] text-[#2D2623]">Anuluj</button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </AppLayout>
  );
}
