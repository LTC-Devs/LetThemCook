"use server";

import { revalidatePath } from "next/cache";
import { mutatePantry, type PantryPayload } from "@/lib/django";

type Result = { ok: boolean; message?: string };

function validate(payload: PantryPayload): string | null {
  if (!Number.isSafeInteger(payload.ingredient_id) || payload.ingredient_id < 1) {
    return "Wybierz składnik z listy.";
  }
  const amount = payload.amount.replace(",", ".");
  if (!/^\d+(\.\d{1,4})?$/.test(amount) || Number(amount) <= 0 || Number(amount) >= 100000000) {
    return "Podaj dodatnią ilość (maksymalnie 4 miejsca po przecinku).";
  }
  if (payload.expires_on !== null && !/^\d{4}-\d{2}-\d{2}$/.test(payload.expires_on)) {
    return "Podaj prawidłową datę ważności.";
  }
  return null;
}

function refreshStock() {
  revalidatePath("/pantry");
  revalidatePath("/shopping");
  revalidatePath("/"); // Recommended recipes use live stock amounts.
}

export async function createPantryAction(payload: PantryPayload): Promise<Result> {
  const validationError = validate(payload);
  if (validationError) return { ok: false, message: validationError };
  try {
    await mutatePantry("/api/pantry/", "POST", { ...payload, amount: payload.amount.replace(",", ".") });
    refreshStock();
    return { ok: true };
  } catch (error) {
    return { ok: false, message: error instanceof Error ? error.message : "Nie udało się dodać produktu." };
  }
}

export async function updatePantryAction(id: number, payload: PantryPayload): Promise<Result> {
  if (!Number.isSafeInteger(id) || id < 1) return { ok: false, message: "Nieprawidłowy wpis spiżarni." };
  const validationError = validate(payload);
  if (validationError) return { ok: false, message: validationError };
  try {
    await mutatePantry(`/api/pantry/${id}/`, "PATCH", { ...payload, amount: payload.amount.replace(",", ".") });
    refreshStock();
    return { ok: true };
  } catch (error) {
    return { ok: false, message: error instanceof Error ? error.message : "Nie udało się edytować produktu." };
  }
}

export async function removePantryAction(id: number): Promise<Result> {
  if (!Number.isSafeInteger(id) || id < 1) return { ok: false, message: "Nieprawidłowy wpis spiżarni." };
  try {
    await mutatePantry(`/api/pantry/${id}/`, "DELETE");
    refreshStock();
    return { ok: true };
  } catch (error) {
    return { ok: false, message: error instanceof Error ? error.message : "Nie udało się usunąć produktu." };
  }
}
