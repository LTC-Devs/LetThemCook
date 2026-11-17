"use client";

import { motion, useAnimation } from "framer-motion";
import { Sun, Check, ArrowUpRight, Shuffle, ArrowLeftRight, AlertCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { isToday, formatFullDate, formatIngredientsSummary, getIngredientWord } from "@/lib/formatters";

export default function FeaturedRecipe({ recipe, onReplace }: any) {
  const controls = useAnimation();
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    controls.set({ opacity: 0, scale: 0.9, x: 100 });
    controls.start({ opacity: 1, scale: 1, x: 0, transition: { type: "spring", stiffness: 260, damping: 20 } });
  }, [recipe.id, controls]);

  const handleDragEnd = async (event: any, info: any) => {
    if (info.offset.x < -100 || info.offset.x > 100) {
      setIsAnimating(true);
      await controls.start({ x: info.offset.x > 0 ? window.innerWidth : -window.innerWidth, opacity: 0, transition: { duration: 0.25 } });
      onReplace();
      setIsAnimating(false);
    } else {
      controls.start({ x: 0, opacity: 1, transition: { type: "spring", stiffness: 300, damping: 25 } });
    }
  };

  return (
    <div className="flex flex-col items-center overflow-visible">
      <motion.div
        drag={isAnimating ? false : "x"}
        dragConstraints={{ left: 0, right: 0 }}
        onDragEnd={handleDragEnd}
        animate={controls}
        className="w-full bg-[#F4CBB3] rounded-[2rem] p-6 shadow-sm cursor-grab active:cursor-grabbing relative"
      >
        <div className="flex justify-between items-center text-sm font-semibold mb-3">
          <div className="flex items-center gap-1.5 text-[#C24B36]">
            {isToday(recipe.target_date) && <Sun size={18} strokeWidth={2.5} />}
            <span className="tracking-wide">
              {isToday(recipe.target_date) ? "DZIŚ" : "ZAPLANOWANE"}
            </span>
          </div>
          <span className="text-[#6C5D53] font-medium text-xs tracking-wider uppercase">
            {formatFullDate(recipe.target_date)}
          </span>
        </div>

        <h2 className="font-nunito text-4xl font-extrabold text-[#2D2623] leading-tight mb-6">
          {recipe.title}
        </h2>

        <div className="mb-6">
          <h3 className="text-[#C24B36] text-[11px] font-bold tracking-widest uppercase mb-1">Składniki</h3>
          
          {/* Frontend maps array to readable sentence */}
          <p className="text-[#4A423D] text-sm leading-relaxed mb-4 pr-4">
            {formatIngredientsSummary(recipe.ingredients_list)}
          </p>
          
          {recipe.missing_ingredients_count === 0 ? (
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 rounded-full bg-white flex items-center justify-center">
                <Check size={14} className="text-[#C24B36]" strokeWidth={3} />
              </div>
              <span className="text-sm font-medium text-[#4A423D]">Komplet składników</span>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 rounded-full bg-white flex items-center justify-center">
                <AlertCircle size={14} className="text-amber-600" strokeWidth={2.5} />
              </div>
              <span className="text-sm font-medium text-amber-800">
                Brakuje: {recipe.missing_ingredients_count} {getIngredientWord(recipe.missing_ingredients_count)}
              </span>
            </div>
          )}
        </div>

        <div className="h-[1px] bg-[#E3B8A0] w-full mb-5" />

        <div className="flex gap-3">
          <button className="flex-1 bg-[#C24B36] text-white rounded-2xl py-4 flex items-center justify-center gap-2 font-semibold shadow-sm active:scale-95 transition-transform">
            Przejdź do przepisu <ArrowUpRight size={18} strokeWidth={2.5} />
          </button>
          <button 
            onClick={() => handleDragEnd(null, { offset: { x: -150 } })} 
            className="w-[60px] h-[56px] bg-white rounded-2xl flex items-center justify-center text-[#C24B36] shadow-sm active:scale-95 transition-transform"
          >
            <Shuffle size={20} strokeWidth={2.5} />
          </button>
        </div>
      </motion.div>

      <div className="flex items-center gap-2 mt-4 text-[#8C837C] text-xs font-medium">
        <ArrowLeftRight size={14} />
        <span>Przesuń kartę aby odrzucić danie.</span>
      </div>
    </div>
  );
}