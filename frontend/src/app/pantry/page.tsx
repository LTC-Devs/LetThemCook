import { Suspense } from "react";
import { getPantry, getPantryIngredients } from "@/lib/django";
import PantryClient from "@/components/pantry/PantryClient";

async function PantryContents() {
  try {
    const [items, ingredients] = await Promise.all([getPantry(), getPantryIngredients()]);
    return <PantryClient initialData={items} ingredients={ingredients} />;
  } catch (error) {
    const message = error instanceof Error ? error.message : "Nie można pobrać spiżarni.";
    return <PantryClient initialData={[]} ingredients={[]} loadError={message} />;
  }
}


export default function PantryPage() {
  return (
    <Suspense
      fallback={
        <div role="status" className="mx-auto max-w-md px-5 py-10 text-center text-sm text-[#6D635C]">
          Ładowanie spiżarni...
        </div>
      }
    >
      <PantryContents />
    </Suspense>
  );
}
