"use client";

import { motion, useAnimation, PanInfo } from "framer-motion";
import { ArrowUpRight, Shuffle, Check, AlertCircle } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { formatCardDate, formatIngredientsPreview, getIngredientWord } from "@/lib/formatters";
import type { RecipeSummary } from "@/lib/types";

export type UpcomingMealWithColor = RecipeSummary & { bgColor: string };

interface UpcomingCardProps {
  meal: UpcomingMealWithColor;
  onReplace: () => void;
}

export default function UpcomingCard({ meal, onReplace }: UpcomingCardProps) {
  const controls = useAnimation();
  const [isAnimating, setIsAnimating] = useState(false);

  const canDismiss = !meal.is_cooked && !isAnimating;
  const dateUI = formatCardDate(meal.target_date);
  const recipeHref = `/recipe/${meal.id}?date=${encodeURIComponent(meal.target_date)}`;

  useEffect(() => {
    controls.set({ opacity: 0, x: 50 });
    controls.start({ opacity: 1, x: 0, transition: { type: "spring", stiffness: 260, damping: 20 } });
  }, [meal.id, controls]);

  const triggerDismiss = async (direction: 1 | -1) => {
    if (!canDismiss) return;
    setIsAnimating(true);
    await controls.start({ x: direction * 300, opacity: 0, transition: { duration: 0.2 } });
    onReplace();
    setIsAnimating(false);
  };

  const handleDragEnd = async (_event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    if (!canDismiss) return;
    if (info.offset.x < -60 || info.offset.x > 60) {
      await triggerDismiss(info.offset.x > 0 ? 1 : -1);
    } else {
      controls.start({ x: 0, opacity: 1, transition: { type: "spring", stiffness: 300, damping: 25 } });
    }
  };

  return (
    <motion.div
      drag={canDismiss ? "x" : false}
      dragConstraints={{ left: 0, right: 0 }}
      onDragEnd={handleDragEnd}
      animate={controls}
      className={`w-full ${meal.bgColor} rounded-[1.5rem] p-4 flex items-center gap-4 ${
        canDismiss ? "cursor-grab active:cursor-grabbing" : "cursor-default"
      }`}
    >
      <div className="flex flex-col items-center justify-center min-w-[3rem]">
        <span className="text-[10px] font-bold tracking-widest text-[#4A4A4A]">{dateUI.dayName}</span>
        <span className="font-nunito text-3xl font-extrabold text-[#2D2623] leading-none my-0.5">{dateUI.dayNumber}</span>
        <span className="text-[10px] font-bold tracking-widest text-[#4A4A4A]">{dateUI.month}</span>
      </div>

      <div className="w-[1px] h-12 bg-black/5" />

      <Link href={recipeHref} onPointerDown={(e) => e.stopPropagation()} className="flex-1 min-w-0">
        <h3 className="font-nunito text-[1.1rem] font-bold text-[#2D2623] truncate leading-tight">
          {meal.title}
        </h3>

        <p className="text-xs text-[#6B6661] italic mt-0.5 truncate">
          {formatIngredientsPreview(meal.ingredients_list)}
        </p>

        <div className="flex items-start gap-1.5 mt-1.5">
          {meal.missing_ingredients_count === 0 ? (
            <>
              <Check size={16} className="text-[#C24B36] shrink-0 mt-[1px]" strokeWidth={3} />
              <span className="text-xs text-[#4A4A4A] font-medium leading-tight">Komplet składników</span>
            </>
          ) : (
            <>
              <AlertCircle size={16} className="text-amber-600 shrink-0 mt-[1px]" strokeWidth={2.5} />
              <span className="text-xs text-amber-700 font-medium leading-tight">
                Brakuje: {meal.missing_ingredients_count} {getIngredientWord(meal.missing_ingredients_count)}
              </span>
            </>
          )}
        </div>
      </Link>

      <div className="flex items-center gap-2 pl-2" onPointerDown={(e) => e.stopPropagation()}>
        {!meal.is_cooked && (
          <button
            type="button"
            onClick={() => triggerDismiss(-1)}
            className="bg-white/80 hover:bg-white text-[#C24B36] rounded-full pl-2 pr-3 py-1.5 flex items-center gap-1.5 text-[10px] font-bold tracking-wide active:scale-95 transition-transform"
          >
            <Shuffle size={12} strokeWidth={3} />
            ZMIEŃ
          </button>
        )}
        <Link
          href={recipeHref}
          aria-label={`Przejdź do przepisu ${meal.title}`}
          className="text-[#2D2623] active:scale-90 transition-transform p-1"
        >
          <ArrowUpRight size={20} strokeWidth={2} />
        </Link>
      </div>
    </motion.div>
  );
}