export const instant = false;

import HomeClient from "@/components/home/HomeClient";
import { DjangoApiError, getHomeRecipeSuggestions } from "@/lib/django";
import Link from "next/link";

export default async function Home() {
  try {
    const suggestions = await getHomeRecipeSuggestions([], 3);
    return <HomeClient initialSuggestions={suggestions} />;
  } catch (error) {
    const message = error instanceof DjangoApiError
      ? error.message
      : "Nie udało się pobrać przepisów z książki.";
    return (
      <main className="m-5 rounded-2xl border border-red-200 bg-white p-6">
        <h1 className="text-xl font-bold">Nie można załadować przepisów</h1>
        <p role="alert" className="mt-2 text-sm text-red-700">{message}</p>
        <Link href="/recipes" className="mt-5 inline-block text-[#C24B36] underline">
          Przejdź do książki kucharskiej
        </Link>
      </main>
    );
  }
}
