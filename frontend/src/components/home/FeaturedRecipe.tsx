"use client";

import { motion, useAnimation, PanInfo } from "framer-motion";
import { Sun, Check, ArrowUpRight, Shuffle, ArrowLeftRight, AlertCircle, CheckCircle2 } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { isToday, formatFullDate, formatIngredientsSummary, getIngredientWord } from "@/lib/formatters";
import type { RecipeSummary } from "@/lib/types";

interface FeaturedRecipeProps {
  recipe: RecipeSummary;
  onReplace: () => void;
}

export default function FeaturedRecipe({ recipe, onReplace }: FeaturedRecipeProps) {
  const controls = useAnimation();
  const [isAnimating, setIsAnimating] = useState(false);

  const canDismiss = !recipe.is_cooked && !isAnimating;

  useEffect(() => {
    controls.set({ opacity: 0, scale: 0.9, x: 100 });
    controls.start({ opacity: 1, scale: 1, x: 0, transition: { type: "spring", stiffness: 260, damping: 20 } });
  }, [recipe.id, controls]);

  const triggerDismiss = async (direction: 1 | -1) => {
    if (!canDismiss) return;
    setIsAnimating(true);
    await controls.start({
      x: direction * window.innerWidth,
      opacity: 0,
      transition: { duration: 0.25 },
    });
    onReplace();
    setIsAnimating(false);
  };

  const handleDragEnd = async (_event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    if (!canDismiss) return;
    if (info.offset.x < -100 || info.offset.x > 100) {
      await triggerDismiss(info.offset.x > 0 ? 1 : -1);
    } else {
      controls.start({ x: 0, opacity: 1, transition: { type: "spring", stiffness: 300, damping: 25 } });
    }
  };

  const recipeHref = `/recipe/${recipe.id}?date=${encodeURIComponent(recipe.target_date)}`;

  return (
    <div className="flex flex-col items-center overflow-visible">
      <motion.div
        drag={canDismiss ? "x" : false}
        dragConstraints={{ left: 0, right: 0 }}
        onDragEnd={handleDragEnd}
        animate={controls}
        className={`w-full rounded-[2rem] p-6 shadow-sm relative ${
          recipe.is_cooked ? "bg-[#DCE6D0] cursor-default" : "bg-[#F4CBB3] cursor-grab active:cursor-grabbing"
        }`}
      >
        <div className="flex justify-between items-center text-sm font-semibold mb-3">
          {recipe.is_cooked ? (
            <div className="flex items-center gap-1.5 text-[#52733B]">
              <CheckCircle2 size={18} strokeWidth={2.5} />
              <span className="tracking-wide">UGOTOWANE</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 text-[#C24B36]">
              {isToday(recipe.target_date) && <Sun size={18} strokeWidth={2.5} />}
              <span className="tracking-wide">
                {isToday(recipe.target_date) ? "DZIŚ" : "ZAPLANOWANE"}
              </span>
            </div>
          )}
          <span className="text-[#6C5D53] font-medium text-xs tracking-wider uppercase">
            {formatFullDate(recipe.target_date)}
          </span>
        </div>

        <h2 className="font-nunito text-4xl font-extrabold text-[#2D2623] leading-tight mb-6">
          {recipe.title}
        </h2>

        <div className="mb-6">
          <h3 className={`text-[11px] font-bold tracking-widest uppercase mb-1 ${recipe.is_cooked ? "text-[#52733B]" : "text-[#C24B36]"}`}>
            Składniki
          </h3>
          <p className="text-[#4A423D] text-sm leading-relaxed mb-4 pr-4">
            {formatIngredientsSummary(recipe.ingredients_list)}
          </p>

          {recipe.is_cooked ? (
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 rounded-full bg-white flex items-center justify-center shrink-0">
                <Check size={14} className="text-[#52733B]" strokeWidth={3} />
              </div>
              <span className="text-sm font-medium text-[#3F572E]">
                {recipe.is_liked === true
                  ? "Ugotowane · Oceniono jako pyszne"
                  : recipe.is_liked === false
                    ? "Ugotowane · Nie Twoje smaki"
                    : "Dzisiejszy posiłek gotowy"}
              </span>
            </div>
          ) : recipe.missing_ingredients_count === 0 ? (
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 rounded-full bg-white flex items-center justify-center shrink-0">
                <Check size={14} className="text-[#C24B36]" strokeWidth={3} />
              </div>
              <span className="text-sm font-medium text-[#4A423D]">Komplet składników</span>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 rounded-full bg-white flex items-center justify-center shrink-0">
                <AlertCircle size={14} className="text-amber-600" strokeWidth={2.5} />
              </div>
              <span className="text-sm font-medium text-amber-800">
                Brakuje: {recipe.missing_ingredients_count} {getIngredientWord(recipe.missing_ingredients_count)}
              </span>
            </div>
          )}
        </div>

        <div className={`h-[1px] w-full mb-5 ${recipe.is_cooked ? "bg-black/10" : "bg-[#E3B8A0]"}`} />

        <div className="flex gap-3" onPointerDown={(e) => e.stopPropagation()}>
          <Link
            href={recipeHref}
            className={`flex-1 rounded-2xl py-4 flex items-center justify-center gap-2 font-semibold shadow-sm active:scale-95 transition-transform ${
              recipe.is_cooked ? "bg-[#52733B] text-white" : "bg-[#C24B36] text-white"
            }`}
          >
            {recipe.is_cooked ? "Zobacz przepis" : "Przejdź do przepisu"} <ArrowUpRight size={18} strokeWidth={2.5} />
          </Link>

          {!recipe.is_cooked && (
            <button
              type="button"
              onClick={() => triggerDismiss(-1)}
              aria-label="Wylosuj inny przepis"
              className="w-[60px] h-[56px] bg-white rounded-2xl flex items-center justify-center text-[#C24B36] shadow-sm active:scale-95 transition-transform"
            >
              <Shuffle size={20} strokeWidth={2.5} />
            </button>
          )}
        </div>
      </motion.div>

      {!recipe.is_cooked && (
        <div className="flex items-center gap-2 mt-4 text-[#8C837C] text-xs font-medium">
          <ArrowLeftRight size={14} />
          <span>Przesuń kartę aby odrzucić danie.</span>
        </div>
      )}
    </div>
  );
}