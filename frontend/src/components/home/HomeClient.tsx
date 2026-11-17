"use client";

import { useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import FeaturedRecipe from "@/components/home/FeaturedRecipe";
import UpcomingMenu from "@/components/home/UpcomingMenu";
import { Search } from "lucide-react";
import { getRandomRecipe } from "@/lib/mock-api";

const PALETTE = ["bg-[#DCE6D0]", "bg-[#EAE3F2]", "bg-[#F3EBE1]", "bg-[#FDE4D8]", "bg-[#E2F0F9]", "bg-[#F4E3D0]"];

const getUniqueRandomColor = (excludeColors: string[]) => {
  const available = PALETTE.filter(c => !excludeColors.includes(c));
  const pool = available.length > 0 ? available : PALETTE;
  return pool[Math.floor(Math.random() * pool.length)];
};

export default function HomeClient({ user, initialRecipe, initialUpcoming }: any) {
  const [todayRecipe, setTodayRecipe] = useState(initialRecipe);
  const [upcomingMeals, setUpcomingMeals] = useState(() => 
    initialUpcoming.map((meal: any, i: number) => ({
      ...meal,
      bgColor: PALETTE[i % PALETTE.length]
    }))
  );
  
  const [toast, setToast] = useState<{ message: string, undoAction: () => void } | null>(null);

  const showToast = (message: string, undoAction: () => void) => {
    setToast({ message, undoAction });
    setTimeout(() => setToast(null), 5000); 
  };

  const handleReplaceToday = async () => {
    const oldRecipe = todayRecipe;
    const newRecipeData = await getRandomRecipe();
    
    setTodayRecipe({
      ...newRecipeData,
      target_date: oldRecipe.target_date,
    });
    showToast("Zmieniono dzisiejszy przepis.", () => setTodayRecipe(oldRecipe));
  };

  const handleReplaceUpcoming = async (idToReplace: number) => {
    const oldList = [...upcomingMeals];
    const newMealData = await getRandomRecipe();
    
    setUpcomingMeals((currentMeals: any[]) => {
      const mealToReplace = currentMeals.find((m: any) => m.id === idToReplace);
      const otherColors = currentMeals.filter((m: any) => m.id !== idToReplace).map((m: any) => m.bgColor);
      const newColor = getUniqueRandomColor(otherColors);

      return currentMeals.map((meal: any) => 
        meal.id === idToReplace 
          ? { ...newMealData, target_date: meal.target_date, bgColor: newColor }
          : meal
      );
    });
    showToast("Zmieniono danie w menu.", () => setUpcomingMeals(oldList));
  };

  // Safely extract the first letter of the user's name for the avatar bubble
  const userInitial = user?.first_name ? user.first_name.charAt(0) : "U";

return (
    // 1. Add a Fragment wrapper here
    <>
      <AppLayout userInitial={userInitial}>
        <h1 className="font-nunito text-[2.1rem] leading-tight font-extrabold text-[#2D2623] tracking-tight mb-6">
          Hej {user?.first_name || "Gościu"}, co gotujemy?
        </h1>

        <FeaturedRecipe recipe={todayRecipe} onReplace={handleReplaceToday} />
        <UpcomingMenu meals={upcomingMeals} onReplace={handleReplaceUpcoming} />

        <button className="w-full mt-4 flex items-center justify-center gap-2 py-4 rounded-2xl bg-[#FCF8F3] text-[#C24B36] font-semibold text-sm border border-[#F4EBE1] active:scale-95 transition-transform">
          <Search size={18} strokeWidth={2.5} />
          Szukaj przepisów w książce
        </button>
      </AppLayout>

      {/* 2. Move the toast OUTSIDE of AppLayout so it attaches to the screen, not the scrollable content */}
      {toast && (
        <div className="absolute bottom-[90px] left-4 right-4 bg-[#2D2623] text-white p-4 rounded-xl flex justify-between items-center shadow-lg animate-in slide-in-from-bottom-5 fade-in z-50">
          <span className="text-sm font-medium">{toast.message}</span>
          <button 
            onClick={() => { toast.undoAction(); setToast(null); }}
            className="text-[#F4CBB3] font-bold text-sm uppercase tracking-wide px-2 py-1 active:scale-95"
          >
            Cofnij
          </button>
        </div>
      )}
    </>
  );
}