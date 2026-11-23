import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  output: "standalone",
  cacheComponents: true,
  partialPrefetching: true,

  // Prevents Next.js from auto-generating AGENTS.md files
  agentRules: false, 
  experimental: {
    // Permanently disables the agent security and upgrade prompts
    agentUpgrade: false, 
  },
  
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export async function fetchRecipeDetails(id: string | number) {
  await new Promise((resolve) => setTimeout(resolve, 300));
  return {
    id: Number(id),
    target_date: "2026-11-08",
    title: "Kremowy makaron orzo ze szpinakiem",
    prep_time_minutes: 25,
    calories: 540,
    ingredients_list: [
      { name: "makaron orzo", quantity_value: 200, quantity_unit: "g" },
      { name: "świeży szpinak", quantity_value: 100, quantity_unit: "g" },
      { name: "parmezan", quantity_value: 50, quantity_unit: "g" },
      { name: "śmietanka 30%", quantity_value: 100, quantity_unit: "ml" },
      { name: "czosnek", quantity_value: 2, quantity_unit: "ząbki" }
    ],
    instructions: [
      "Ugotuj makaron orzo w osolonej wodzie według instrukcji na opakowaniu, a następnie odcedź.",
      "Na patelni rozgrzej oliwę i podsmaż przeciśnięty przez praskę czosnek przez 30 sekund.",
      "Dodaj umyty szpinak i duś przez 2 minuty, aż zwiędnie.",
      "Wlej śmietankę, dodaj połowę startego parmezanu i gotuj na małym ogniu, aż sos lekko zgęstnieje.",
      "Wymieszaj gotowy sos z makaronem. Dopraw solą i pieprzem. Podawaj posypane resztą sera."
    ]
  };
}

export async function fetchRandomRecipeDetails() {
  await new Promise((resolve) => setTimeout(resolve, 400));
  return {
    id: Math.floor(Math.random() * 10000) + 100,
    target_date: "2026-11-08",
    title: "Szybki Wrap z Kurczakiem",
    prep_time_minutes: 15,
    calories: 420,
    ingredients_list: [
      { name: "tortilla pełnoziarnista", quantity_value: 2, quantity_unit: "szt" },
      { name: "pierś z kurczaka", quantity_value: 150, quantity_unit: "g" },
      { name: "mix sałat", quantity_value: 50, quantity_unit: "g" },
      { name: "pomidor malinowy", quantity_value: 1, quantity_unit: "szt" },
      { name: "sos czosnkowy", quantity_value: 2, quantity_unit: "łyżki" }
    ],
    instructions: [
      "Kurczaka pokrój w paski, przypraw ulubionymi ziołami i usmaż na złocisty kolor.",
      "Podgrzej tortille na suchej patelni (po 10 sekund z każdej strony), aby były elastyczne.",
      "Posmaruj każdą tortillę łyżką sosu czosnkowego.",
      "Na środku ułóż garść sałaty, plastry pomidora oraz usmażonego kurczaka.",
      "Zwiń ciasno w rulon, podwijając boki do środka. Przekrój na pół i podawaj."
    ]
  };
}



export default nextConfig;


