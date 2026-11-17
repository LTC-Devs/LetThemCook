export const instant = false;

import { fetchLarderInventory, fetchUserSession } from "@/lib/mock-api";
import PantryClient from "@/components/pantry/PantryClient";

export default async function PantryPage() {
  const user = await fetchUserSession();
  const initialData = await fetchLarderInventory();
  
  return <PantryClient initialData={initialData} user={user} />;
}
