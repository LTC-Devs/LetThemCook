export const instant = false;

import { fetchTodayRecipe, fetchUpcomingMenu, fetchUserSession } from "@/lib/mock-api";
import HomeClient from "@/components/home/HomeClient";

export default async function Home() {
  const user = await fetchUserSession();
  const todayRecipe = await fetchTodayRecipe();
  const upcomingMeals = await fetchUpcomingMenu();

  return (
    <HomeClient 
      user={user}
      initialRecipe={todayRecipe} 
      initialUpcoming={upcomingMeals} 
    />
  );
}
