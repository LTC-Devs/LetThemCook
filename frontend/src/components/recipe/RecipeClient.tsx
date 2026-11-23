"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import AppLayout from "@/components/layout/AppLayout";
import {
  ArrowLeft,
  Shuffle,
  CheckCircle,
  ThumbsUp,
  ThumbsDown,
  Loader2,
  AlertCircle,
  Check,
  Sun,
  CalendarClock,
} from "lucide-react";
import Link from "next/link";
import { markMealAsCooked, replacePlannedRecipe, submitRecipeFeedback } from "@/lib/mock-api";
import type { RecipeDetail, UserSession } from "@/lib/types";
import { formatFullDate, isToday } from "@/lib/formatters";
import { motion, AnimatePresence } from "framer-motion";

interface RecipeClientProps {
  initialRecipe: RecipeDetail;
  user: UserSession;
}

export default function RecipeClient({ initialRecipe, user }: RecipeClientProps) {
  const router = useRouter();
  const [recipe, setRecipe] = useState<RecipeDetail>(initialRecipe);
  const [isShuffling, setIsShuffling] = useState(false);

  // Cooking & Feedback UI State
  const [showFeedbackScreen, setShowFeedbackScreen] = useState(false);
  const [isFinishing, setIsFinishing] = useState(false);
  const [isSubmittingFeedback, setIsSubmittingFeedback] = useState(false);
  const [actionError, setActionError] = useState("");

  const userInitial = user?.first_name ? user.first_name.charAt(0) : "U";

  const handleReshuffle = async () => {
    if (!recipe.can_reshuffle || isShuffling) return;
    setIsShuffling(true);
    setActionError("");
    try {
      const newRecipe = await replacePlannedRecipe(recipe.target_date);
      setRecipe(newRecipe);
      window.history.replaceState(
        null,
        "",
        `/recipe/${newRecipe.id}?date=${encodeURIComponent(newRecipe.target_date)}`
      );
      router.refresh();
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : "Nie udało się zmienić przepisu.");
    } finally {
      setIsShuffling(false);
    }
  };

  const handleFinishCooking = async () => {
    if (!recipe.can_cook || isFinishing) return;
    setIsFinishing(true);
    setActionError("");
    try {
      const updated = await markMealAsCooked(recipe.target_date, recipe.id);
      setRecipe(updated);
      setShowFeedbackScreen(true);
      router.refresh();
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : "Nie udało się zapisać statusu gotowania.");
    } finally {
      setIsFinishing(false);
    }
  };

  const handleFeedback = async (liked: boolean) => {
    if (recipe.is_liked !== null || isSubmittingFeedback) return;
    setIsSubmittingFeedback(true);
    setActionError("");
    try {
      const updated = await submitRecipeFeedback(recipe.target_date, recipe.id, liked);
      setRecipe(updated);
      router.refresh();
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : "Nie udało się zapisać oceny. Spróbuj ponownie.");
    } finally {
      setIsSubmittingFeedback(false);
    }
  };

  const handleBackToRecipe = () => {
    setActionError("");
    setShowFeedbackScreen(false);
  };

  return (
    <AppLayout userInitial={userInitial} showBottomNav={false}>
      {/* Top Action Bar */}
      <div className="flex items-center justify-between mb-5">
        {showFeedbackScreen ? (
          <button
            type="button"
            onClick={handleBackToRecipe}
            className="flex items-center gap-2 text-[#8C837C] font-bold text-sm hover:text-[#C24B36] active:scale-95 transition-all cursor-pointer"
          >
            <ArrowLeft size={18} strokeWidth={2.5} /> Wróć
          </button>
        ) : (
          <Link
            href="/"
            className="flex items-center gap-2 text-[#8C837C] font-bold text-sm hover:text-[#C24B36] active:scale-95 transition-all"
          >
            <ArrowLeft size={18} strokeWidth={2.5} /> Wróć
          </Link>
        )}

        {!showFeedbackScreen && recipe.can_reshuffle && (
          <button
            type="button"
            onClick={handleReshuffle}
            disabled={isShuffling}
            className="bg-white border border-[#F2ECE4] text-[#C24B36] rounded-full px-4 py-2 flex items-center gap-2 font-bold text-xs shadow-sm active:scale-95 transition-all disabled:opacity-60"
          >
            {isShuffling ? <Loader2 size={14} className="animate-spin" /> : <Shuffle size={14} strokeWidth={2.5} />}
            ZMIEŃ
          </button>
        )}
      </div>

      {actionError && (
        <p className="text-sm font-semibold text-red-600 bg-red-50 border border-red-100 px-4 py-3 rounded-xl mb-5">
          {actionError}
        </p>
      )}

      <AnimatePresence mode="wait">
        {showFeedbackScreen ? (
          /* POST-COOKING FEEDBACK SCREEN */
          <motion.div
            key="feedback"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex flex-col items-center justify-center py-12 text-center"
          >
            <div className="w-20 h-20 bg-[#DCE6D0] rounded-full flex items-center justify-center mb-6">
              <CheckCircle size={40} className="text-[#6B8E4E]" strokeWidth={2} />
            </div>

            <h1 className="font-nunito text-3xl font-extrabold text-[#2D2623] mb-2">
              Świetna robota!
            </h1>

            {recipe.is_liked === null ? (
              <>
                <p className="text-[#8C837C] mb-10">
                  Jak Ci smakowało danie <span className="font-semibold text-[#4A423D]">{recipe.title}</span>?
                </p>

                <div className="flex gap-4 w-full px-4">
                  <button
                    type="button"
                    disabled={isSubmittingFeedback}
                    onClick={() => handleFeedback(true)}
                    className="flex-1 bg-[#FDFBF7] border-2 border-[#E5DFD6] rounded-2xl p-6 flex flex-col items-center gap-3 active:scale-95 active:border-[#8CA86E] transition-all disabled:opacity-60"
                  >
                    <div className="w-12 h-12 rounded-full bg-[#DCE6D0] flex items-center justify-center">
                      {isSubmittingFeedback ? (
                        <Loader2 size={22} className="text-[#6B8E4E] animate-spin" />
                      ) : (
                        <ThumbsUp size={24} className="text-[#6B8E4E]" />
                      )}
                    </div>
                    <span className="font-bold text-[#4A423D] text-sm">Pyszne!</span>
                  </button>

                  <button
                    type="button"
                    disabled={isSubmittingFeedback}
                    onClick={() => handleFeedback(false)}
                    className="flex-1 bg-[#FDFBF7] border-2 border-[#E5DFD6] rounded-2xl p-6 flex flex-col items-center gap-3 active:scale-95 active:border-[#C24B36] transition-all disabled:opacity-60"
                  >
                    <div className="w-12 h-12 rounded-full bg-[#FDE4D8] flex items-center justify-center">
                      {isSubmittingFeedback ? (
                        <Loader2 size={22} className="text-[#C24B36] animate-spin" />
                      ) : (
                        <ThumbsDown size={24} className="text-[#C24B36]" />
                      )}
                    </div>
                    <span className="font-bold text-[#4A423D] text-sm">Nie moje smaki</span>
                  </button>
                </div>
              </>
            ) : (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-4 flex flex-col items-center">
                <p className="text-[#6B8E4E] font-bold mb-8">
                  {recipe.is_liked
                    ? "Super! Będziemy częściej proponować podobne dania."
                    : "Zapisano! Uwzględnimy to przy kolejnych propozycjach."}
                </p>
                <Link
                  href="/"
                  className="bg-[#C24B36] text-white font-bold rounded-xl px-8 py-4 shadow-sm active:scale-95 transition-transform"
                >
                  Wróć do menu
                </Link>
              </motion.div>
            )}
          </motion.div>
        ) : (
          /* RECIPE DETAILS SCREEN */
          <motion.div
            key={recipe.id}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className={`transition-opacity duration-300 ${isShuffling ? "opacity-40 pointer-events-none" : "opacity-100"}`}
          >
            {/* Date Subtitle */}
            {recipe.target_date && (
              <div className="flex items-center gap-2 text-xs font-bold tracking-wider uppercase text-[#8C837C] mb-2">
                {isToday(recipe.target_date) && <Sun size={14} className="text-[#C24B36]" strokeWidth={2.5} />}
                <span>{formatFullDate(recipe.target_date)}</span>
              </div>
            )}

            <h1 className="font-nunito text-[2.2rem] leading-tight font-extrabold text-[#2D2623] tracking-tight mb-6">
              {recipe.title}
            </h1>

            {/* Ingredients */}
            <div className="bg-white border border-[#F2ECE4] rounded-[1.5rem] p-6 shadow-sm mb-6">
              <h3 className="text-[#C24B36] text-xs font-bold tracking-widest uppercase mb-4">Składniki</h3>
              <ul className="space-y-3">
                {recipe.ingredients_list.map((ing, i) => (
                  <li
                    key={`${ing.name}-${i}`}
                    className="flex justify-between items-center border-b border-[#F9F6F0] pb-2.5 last:border-0 last:pb-0"
                  >
                    <div className="flex items-center gap-2.5">
                      {ing.is_missing ? (
                        <AlertCircle size={16} className="text-amber-600 shrink-0" strokeWidth={2.5} />
                      ) : (
                        <Check size={16} className="text-[#8CA86E] shrink-0" strokeWidth={3} />
                      )}
                      <span className={`font-bold text-sm ${ing.is_missing ? "text-amber-800" : "text-[#4A423D]"}`}>
                        {ing.name}
                      </span>
                    </div>
                    <span className="text-[#8C837C] text-sm font-medium">
                      {ing.quantity_value} {ing.quantity_unit}
                    </span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Preparation Text */}
            <div className="bg-white border border-[#F2ECE4] rounded-[1.5rem] p-6 shadow-sm mb-8">
              <h3 className="text-[#C24B36] text-xs font-bold tracking-widest uppercase mb-3">Przygotowanie</h3>
              <p className="text-[#4A423D] leading-relaxed text-[0.95rem] whitespace-pre-line">
                {recipe.instructions}
              </p>
            </div>

            {/* Footer Action / Status Area */}
            {recipe.is_cooked ? (
              <div className="bg-[#DCE6D0] rounded-[1.5rem] p-5 flex flex-col gap-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center shrink-0">
                    <CheckCircle size={20} className="text-[#52733B]" strokeWidth={2.5} />
                  </div>
                  <div>
                    <p className="font-nunito font-extrabold text-[#2D2623]">Danie ugotowane</p>
                    <p className="text-xs font-medium text-[#3F572E]">
                      {recipe.is_liked === true
                        ? "Twoja ocena: Pyszne!"
                        : recipe.is_liked === false
                          ? "Twoja ocena: Nie moje smaki"
                          : "Jak Ci smakowało? Możesz jeszcze wystawić ocenę."}
                    </p>
                  </div>
                </div>

                {recipe.is_liked === null && (
                  <div className="flex gap-3">
                    <button
                      type="button"
                      disabled={isSubmittingFeedback}
                      onClick={() => handleFeedback(true)}
                      className="flex-1 bg-white text-[#52733B] rounded-xl py-3 flex items-center justify-center gap-2 font-bold text-xs shadow-sm active:scale-95 transition-transform disabled:opacity-60"
                    >
                      <ThumbsUp size={15} strokeWidth={2.5} /> Pyszne!
                    </button>
                    <button
                      type="button"
                      disabled={isSubmittingFeedback}
                      onClick={() => handleFeedback(false)}
                      className="flex-1 bg-white text-[#C24B36] rounded-xl py-3 flex items-center justify-center gap-2 font-bold text-xs shadow-sm active:scale-95 transition-transform disabled:opacity-60"
                    >
                      <ThumbsDown size={15} strokeWidth={2.5} /> Nie moje smaki
                    </button>
                  </div>
                )}
              </div>
            ) : recipe.can_cook ? (
              <button
                type="button"
                disabled={isFinishing}
                onClick={handleFinishCooking}
                className="w-full bg-[#C24B36] text-white rounded-2xl py-4 flex items-center justify-center gap-2 font-semibold shadow-sm active:scale-95 transition-transform disabled:opacity-70"
              >
                {isFinishing ? (
                  <Loader2 size={20} className="animate-spin" />
                ) : (
                  <CheckCircle size={20} strokeWidth={2.5} />
                )}
                Zakończ gotowanie
              </button>
            ) : (
              <div className="bg-[#F3EBE1] rounded-2xl p-4 flex items-center gap-3 text-[#6C5D53]">
                <CalendarClock size={20} className="shrink-0 text-[#C24B36]" strokeWidth={2.2} />
                <p className="text-xs font-semibold leading-relaxed">
                  To danie jest zaplanowane na inny dzień. Oznaczenie jako ugotowane będzie dostępne dopiero w dniu realizacji.
                </p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </AppLayout>
  );
}