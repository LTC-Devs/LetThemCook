"use server";

import { revalidatePath } from "next/cache";
import type { RecipeDetail, RecipeIngredient, RecipeSummary, UserSession } from "./types";

interface RecipeRecord {
  id: number;
  title: string;
  ingredients_list: RecipeIngredient[];
  instructions: string;
}

interface MealPlanEntry {
  target_date: string;
  recipe_id: number;
  is_cooked: boolean;
  is_liked: boolean | null;
}

interface MockDatabase {
  initialized_for_date: string;
  meal_plan: MealPlanEntry[];
}

const MOCK_RECIPES_DB: RecipeRecord[] = [
  {
    id: 1,
    title: "Kremowy makaron orzo",
    ingredients_list: [
      { name: "jajka", quantity_value: 2, quantity_unit: "szt", is_missing: false },
      { name: "makaron orzo", quantity_value: 200, quantity_unit: "g", is_missing: false },
      { name: "szpinak", quantity_value: 100, quantity_unit: "g", is_missing: false },
      { name: "parmezan", quantity_value: 50, quantity_unit: "g", is_missing: false },
      { name: "cytryna", quantity_value: 1, quantity_unit: "szt", is_missing: false },
    ],
    instructions:
      "Ugotuj makaron orzo w osolonej wodzie według instrukcji na opakowaniu, zachowując pół szklanki wody z gotowania. Na patelni rozgrzej oliwę i duś świeży szpinak przez 2 minuty, aż zwiędnie.\n\nDodaj ugotowany makaron, starty parmezan oraz skórkę i sok z cytryny. Zdejmij z ognia, wlej roztrzepane jajka z odrobiną wody z makaronu i energicznie wymieszaj do uzyskania kremowego sosu. Dopraw świeżo mielonym pieprzem i podawaj od razu.",
  },
  {
    id: 2,
    title: "Kotlety schabowe",
    ingredients_list: [
      { name: "schab", quantity_value: 300, quantity_unit: "g", is_missing: true },
      { name: "panierka", quantity_value: 80, quantity_unit: "g", is_missing: true },
      { name: "jajko", quantity_value: 1, quantity_unit: "szt", is_missing: false },
      { name: "ziemniaki", quantity_value: 500, quantity_unit: "g", is_missing: false },
      { name: "koper", quantity_value: 1, quantity_unit: "pęczek", is_missing: false },
    ],
    instructions:
      "Obierz ziemniaki i wstaw do gotowania w osolonej wodzie na ok. 20 minut. Plastry schabu rozbij cienko tłuczkiem, dopraw solą i pieprzem z obu stron, a następnie obtocz kolejno w mące, roztrzepanym jajku i bułce tartej.\n\nSmaż na dobrze rozgrzanym tłuszczu po 3-4 minuty z każdej strony na złoty kolor. Odcedzone ziemniaki posyp posiekanym koperkiem i podawaj razem z kotletami.",
  },
  {
    id: 3,
    title: "Ryż z grzybami",
    ingredients_list: [
      { name: "ryż", quantity_value: 200, quantity_unit: "g", is_missing: false },
      { name: "pieczarki", quantity_value: 250, quantity_unit: "g", is_missing: false },
      { name: "cebula", quantity_value: 1, quantity_unit: "szt", is_missing: false },
      { name: "bulion", quantity_value: 500, quantity_unit: "ml", is_missing: false },
      { name: "natka pietruszki", quantity_value: 1, quantity_unit: "pęczek", is_missing: false },
    ],
    instructions:
      "Pokrój cebulę w drobną kostkę, a pieczarki w plasterki. Podsmaż cebulę na oliwie do zeszklenia, następnie dodaj pieczarki i smaż do odparowania wody.\n\nWsyp suchy ryż, smaż przez minutę, po czym stopniowo dolewaj gorący bulion. Gotuj na małym ogniu ok. 18 minut, mieszając, aż ryż wchłonie płyn i będzie miękki. Wymieszaj z posiekaną natką pietruszki i podawaj na ciepło.",
  },
  {
    id: 4,
    title: "Szybki wrap z kurczakiem",
    ingredients_list: [
      { name: "tortilla pełnoziarnista", quantity_value: 2, quantity_unit: "szt", is_missing: true },
      { name: "pierś z kurczaka", quantity_value: 150, quantity_unit: "g", is_missing: true },
      { name: "mix sałat", quantity_value: 50, quantity_unit: "g", is_missing: true },
      { name: "pomidor malinowy", quantity_value: 1, quantity_unit: "szt", is_missing: false },
      { name: "sos czosnkowy", quantity_value: 2, quantity_unit: "łyżki", is_missing: false },
    ],
    instructions:
      "Kurczaka pokrój w paski, przypraw ulubionymi ziołami i usmaż na złocisty kolor. Podgrzej tortille na suchej patelni po 10 sekund z każdej strony, aby były elastyczne.\n\nPosmaruj każdą tortillę łyżką sosu czosnkowego, ułóż na środku garść sałaty, plastry pomidora oraz usmażonego kurczaka, a następnie zwiń ciasno w rulon, podwijając boki do środka.",
  },
  {
    id: 5,
    title: "Szakszuka z serem feta",
    ingredients_list: [
      { name: "pomidory krojone", quantity_value: 400, quantity_unit: "g", is_missing: false },
      { name: "jajka", quantity_value: 3, quantity_unit: "szt", is_missing: false },
      { name: "ser feta", quantity_value: 80, quantity_unit: "g", is_missing: true },
      { name: "papryka czerwona", quantity_value: 1, quantity_unit: "szt", is_missing: false },
      { name: "czosnek", quantity_value: 2, quantity_unit: "ząbki", is_missing: false },
    ],
    instructions:
      "Na patelni podsmaż pokrojoną w kostkę paprykę oraz posiekany czosnek przez 4 minuty. Wlej pomidory z puszki, dopraw kminem rzymskim, solą oraz pieprzem i duś 6 minut.\n\nZrób w sosie trzy wgłębienia, wbij w każde po jednym jajku, przykryj patelnię i gotuj 4-5 minut, aż białka się zetną, a żółtka pozostaną płynne. Przed podaniem posyp pokruszoną fetą.",
  },
];

function formatDateOffset(offsetDays: number): string {
  const d = new Date();
  d.setDate(d.getDate() + offsetDays);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

const globalForMockDb = globalThis as unknown as {
  __LET_THEM_COOK_DB__?: MockDatabase;
};

function getMockDb(): MockDatabase {
  const todayISO = formatDateOffset(0);
  if (!globalForMockDb.__LET_THEM_COOK_DB__ || globalForMockDb.__LET_THEM_COOK_DB__.initialized_for_date !== todayISO) {
    globalForMockDb.__LET_THEM_COOK_DB__ = {
      initialized_for_date: todayISO,
      meal_plan: [
        { target_date: todayISO, recipe_id: 1, is_cooked: false, is_liked: null },
        { target_date: formatDateOffset(1), recipe_id: 2, is_cooked: false, is_liked: null },
        { target_date: formatDateOffset(2), recipe_id: 3, is_cooked: false, is_liked: null },
      ],
    };
  }
  return globalForMockDb.__LET_THEM_COOK_DB__;
}

function getRecipeById(id: number): RecipeRecord {
  return MOCK_RECIPES_DB.find((r) => r.id === id) || MOCK_RECIPES_DB[0];
}

function serializeSummary(entry: MealPlanEntry): RecipeSummary {
  const recipe = getRecipeById(entry.recipe_id);
  return {
    id: recipe.id,
    target_date: entry.target_date,
    title: recipe.title,
    ingredients_list: recipe.ingredients_list.map((i) => i.name),
    missing_ingredients_count: recipe.ingredients_list.filter((i) => i.is_missing).length,
    is_cooked: entry.is_cooked,
    is_liked: entry.is_liked,
  };
}

function serializeDetail(recipe: RecipeRecord, entry?: MealPlanEntry): RecipeDetail {
  const todayISO = formatDateOffset(0);
  const targetDate = entry?.target_date || "";
  const isCooked = entry?.is_cooked ?? false;
  const isScheduledToday = targetDate === todayISO;

  return {
    id: recipe.id,
    target_date: targetDate,
    title: recipe.title,
    ingredients_list: recipe.ingredients_list,
    missing_ingredients_count: recipe.ingredients_list.filter((i) => i.is_missing).length,
    instructions: recipe.instructions,
    is_cooked: isCooked,
    is_liked: entry?.is_liked ?? null,
    // Business rules enforced centrally (mirrors Django serializer/permissions)
    can_cook: Boolean(entry) && isScheduledToday && !isCooked,
    can_reshuffle: Boolean(entry) && !isCooked,
  };
}

// --- QUERIES ---

export async function fetchUserSession(): Promise<UserSession> {
  await new Promise((resolve) => setTimeout(resolve, 150));
  return {
    id: 1,
    first_name: "Alexa",
    last_name: "Kowalski",
    email: "alex@example.com",
  };
}

export async function fetchTodayRecipe(): Promise<RecipeSummary> {
  await new Promise((resolve) => setTimeout(resolve, 200));
  const db = getMockDb();
  const todayISO = formatDateOffset(0);
  const entry = db.meal_plan.find((m) => m.target_date === todayISO) || db.meal_plan[0];
  return serializeSummary(entry);
}

export async function fetchUpcomingMenu(): Promise<RecipeSummary[]> {
  await new Promise((resolve) => setTimeout(resolve, 200));
  const db = getMockDb();
  const todayISO = formatDateOffset(0);
  return db.meal_plan.filter((m) => m.target_date > todayISO).map(serializeSummary);
}

export async function fetchRecipeDetails(
  id: string | number,
  targetDate?: string
): Promise<RecipeDetail | null> {
  await new Promise((resolve) => setTimeout(resolve, 200));
  const db = getMockDb();
  const numericId = Number(id);
  const recipe = MOCK_RECIPES_DB.find((r) => r.id === numericId);
  if (!recipe) return null;

  // Verify the recipe actually belongs to the requested meal plan date
  const entry = targetDate
    ? db.meal_plan.find((m) => m.target_date === targetDate && m.recipe_id === numericId)
    : db.meal_plan.find((m) => m.recipe_id === numericId);

  return serializeDetail(recipe, entry);
}

// --- MUTATIONS ---

// Replaces a planned meal for a specific date and persists it in DB
export async function replacePlannedMealSummary(targetDate: string): Promise<RecipeSummary> {
  await new Promise((resolve) => setTimeout(resolve, 300));
  const db = getMockDb();
  const entry = db.meal_plan.find((m) => m.target_date === targetDate);

  if (!entry) {
    throw new Error("Nie znaleziono zaplanowanego posiłku dla tej daty.");
  }
  if (entry.is_cooked) {
    throw new Error("Nie można zmienić przepisu, który został już ugotowany.");
  }

  const activeIds = db.meal_plan.map((m) => m.recipe_id);
  const candidates = MOCK_RECIPES_DB.filter((r) => !activeIds.includes(r.id));
  const pool = candidates.length > 0 ? candidates : MOCK_RECIPES_DB.filter((r) => r.id !== entry.recipe_id);
  const picked = pool[Math.floor(Math.random() * pool.length)];

  entry.recipe_id = picked.id;
  revalidatePath("/");
  return serializeSummary(entry);
}

// Restores a previous recipe (used by Undo toast so DB stays in sync)
export async function restorePlannedMeal(targetDate: string, recipeId: number): Promise<RecipeSummary> {
  const db = getMockDb();
  const entry = db.meal_plan.find((m) => m.target_date === targetDate);

  if (!entry) {
    throw new Error("Nie znaleziono zaplanowanego posiłku.");
  }
  if (entry.is_cooked) {
    throw new Error("Nie można cofnąć zmiany dla ugotowanego posiłku.");
  }

  entry.recipe_id = recipeId;
  revalidatePath("/");
  return serializeSummary(entry);
}

// In-place reshuffle from the Recipe Detail page
export async function replacePlannedRecipe(targetDate: string): Promise<RecipeDetail> {
  await new Promise((resolve) => setTimeout(resolve, 350));
  const db = getMockDb();
  const entry = db.meal_plan.find((m) => m.target_date === targetDate);

  if (!entry) {
    throw new Error("Nie znaleziono zaplanowanego posiłku.");
  }
  if (entry.is_cooked) {
    throw new Error("Nie można zmienić ugotowanego przepisu.");
  }

  const activeIds = db.meal_plan.map((m) => m.recipe_id);
  const candidates = MOCK_RECIPES_DB.filter((r) => !activeIds.includes(r.id));
  const pool = candidates.length > 0 ? candidates : MOCK_RECIPES_DB.filter((r) => r.id !== entry.recipe_id);
  const picked = pool[Math.floor(Math.random() * pool.length)];

  entry.recipe_id = picked.id;
  revalidatePath("/");
  return serializeDetail(picked, entry);
}

// Marks today's meal as cooked permanently in DB
export async function markMealAsCooked(targetDate: string, recipeId: number): Promise<RecipeDetail> {
  await new Promise((resolve) => setTimeout(resolve, 300));
  const db = getMockDb();
  const todayISO = formatDateOffset(0);

  if (targetDate !== todayISO) {
    throw new Error("Możesz ugotować wyłącznie przepis zaplanowany na dzisiaj.");
  }

  const entry = db.meal_plan.find((m) => m.target_date === targetDate && m.recipe_id === recipeId);
  if (!entry) {
    throw new Error("Ten przepis nie jest zaplanowany na dzisiaj.");
  }
  if (entry.is_cooked) {
    throw new Error("To danie zostało już oznaczone jako ugotowane.");
  }

  entry.is_cooked = true;
  revalidatePath("/");
  return serializeDetail(getRecipeById(entry.recipe_id), entry);
}

// Saves like/dislike rating for a cooked meal
export async function submitRecipeFeedback(
  targetDate: string,
  recipeId: number,
  isLiked: boolean
): Promise<RecipeDetail> {
  await new Promise((resolve) => setTimeout(resolve, 300));
  const db = getMockDb();
  const entry = db.meal_plan.find((m) => m.target_date === targetDate && m.recipe_id === recipeId);

  if (!entry) {
    throw new Error("Nie znaleziono zaplanowanego posiłku.");
  }
  if (!entry.is_cooked) {
    throw new Error("Najpierw zakończ gotowanie, aby ocenić danie.");
  }
  if (entry.is_liked !== null) {
    throw new Error("To danie zostało już ocenione.");
  }

  entry.is_liked = isLiked;
  revalidatePath("/");
  return serializeDetail(getRecipeById(entry.recipe_id), entry);
}

export async function fetchLarderInventory() {
  await new Promise((resolve) => setTimeout(resolve, 200));
  return [
    { id: 1, ingredient_name: "Mleko", quantity_value: 1, quantity_unit: "litr" },
    { id: 2, ingredient_name: "Ziemniaki", quantity_value: 2, quantity_unit: "kg" },
  ];
}

export async function fetchShoppingList() {
  await new Promise((resolve) => setTimeout(resolve, 200));
  return [
    { id: 1, ingredient_name: "Mąka", quantity_value: 1, quantity_unit: "kg", category: "wypieki", is_checked: false },
    { id: 2, ingredient_name: "Twaróg", quantity_value: 500, quantity_unit: "g", category: "nabiał", is_checked: false },
    { id: 3, ingredient_name: "Kiełbasa", quantity_value: 300, quantity_unit: "g", category: "mięso", is_checked: false },
  ];
}

export async function fetchUserProfile() {
  await new Promise((resolve) => setTimeout(resolve, 200));
  return {
    household_size: 2,
    measurement_system: "metric",
    is_vegetarian: false,
    is_gluten_free: false,
    blocked_ingredients: "orzeszki ziemne, czosnek",
  };
}