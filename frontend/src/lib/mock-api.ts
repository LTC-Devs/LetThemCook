export async function fetchUserSession() {
  await new Promise((resolve) => setTimeout(resolve, 200));
  return {
    id: 1,
    first_name: "Alex",
    last_name: "Kowalski",
    email: "alex@example.com",
  };
}

// 1. HOMEPAGE APIS
export async function fetchTodayRecipe() {
  await new Promise((resolve) => setTimeout(resolve, 300));
  return {
    id: 1,
    target_date: "2026-11-08",
    title: "Kremowy makaron orzo",
    ingredients_list: ["jajka", "makaron orzo", "szpinak", "parmezan", "cytryna"],
    missing_ingredients_count: 0,
  };
}

export async function fetchUpcomingMenu() {
  await new Promise((resolve) => setTimeout(resolve, 300));
  return [
    { 
      id: 2, 
      target_date: "2026-11-09", 
      title: "Kotlety schabowe", 
      ingredients_list: ["schab", "panierka", "jajko", "ziemniaki", "koper"],
      missing_ingredients_count: 2 
    },
    { 
      id: 3, 
      target_date: "2026-11-10", 
      title: "Ryż z grzybami", 
      ingredients_list: ["ryż", "pieczarki", "cebula", "bulion", "natka pietruszki"],
      missing_ingredients_count: 0 
    },
  ];
}

export async function getRandomRecipe() {
  await new Promise((resolve) => setTimeout(resolve, 400));
  return {
    id: Math.floor(Math.random() * 10000) + 100,
    title: "Nowy przepis z bazy",
    ingredients_list: ["losowy składnik", "oliwa", "sól", "pieprz", "czosnek"],
    missing_ingredients_count: 3,
  };
}

// 2. PANTRY API
export async function fetchLarderInventory() {
  await new Promise((resolve) => setTimeout(resolve, 300));
  return [
    { id: 1, ingredient_name: "Mleko", quantity_value: 1, quantity_unit: "litr" },
    { id: 2, ingredient_name: "Ziemniaki", quantity_value: 2, quantity_unit: "kg" },
  ];
}

// 3. SHOPPING LIST API
export async function fetchShoppingList() {
  await new Promise((resolve) => setTimeout(resolve, 300));
  return [
    { id: 1, ingredient_name: "Mąka", quantity_value: 1, quantity_unit: "kg", category: "wypieki", is_checked: false },
    { id: 2, ingredient_name: "Twaróg", quantity_value: 500, quantity_unit: "g", category: "nabiał", is_checked: false },
    { id: 3, ingredient_name: "Kiełbasa", quantity_value: 300, quantity_unit: "g", category: "mięso", is_checked: false },
  ];
}

// 4. USER PROFILE API
export async function fetchUserProfile() {
  await new Promise((resolve) => setTimeout(resolve, 300));
  return {
    household_size: 2,
    measurement_system: "metric",
    is_vegetarian: false,
    is_gluten_free: false,
    blocked_ingredients: "orzeszki ziemne, czosnek",
  };
}