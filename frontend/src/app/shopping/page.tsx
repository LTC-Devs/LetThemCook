export const instant = false;

import { fetchShoppingList, fetchUserSession } from "@/lib/mock-api";
import ShoppingClient from "@/components/shopping/ShoppingClient";

export default async function ShoppingPage() {
  const user = await fetchUserSession();
  const initialData = await fetchShoppingList();
  
  return <ShoppingClient initialData={initialData} user={user} />;
}
