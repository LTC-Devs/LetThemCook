export const instant = false;

import { getShoppingList } from "@/lib/django";
import ShoppingClient from "@/components/shopping/ShoppingClient";

type Props = { searchParams: Promise<{ recipe?: string }> };

export default async function ShoppingPage({ searchParams }: Props) {
  const { recipe } = await searchParams;
  const initialRecipeId = recipe && /^\d+$/.test(recipe) ? recipe : "";
  try {
    const items = await getShoppingList();
    return <ShoppingClient initialData={items} initialRecipeId={initialRecipeId} />;
  } catch (error) {
    const message = error instanceof Error ? error.message : "Błąd pobierania listy zakupów.";
    return <ShoppingClient initialData={[]} loadError={message} initialRecipeId={initialRecipeId} />;
  }
}
