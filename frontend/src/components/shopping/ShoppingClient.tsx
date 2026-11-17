"use client";

import { useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import { Plus, ArrowRightToLine } from "lucide-react";

export default function ShoppingClient({ initialData, user }: any) {
  const [items, setItems] = useState(initialData);
  const userInitial = user?.first_name ? user.first_name.charAt(0) : "U";

  const toggleCheck = (id: number) => {
    setItems(items.map((i: any) => i.id === id ? { ...i, is_checked: !i.is_checked } : i));
  };

  return (
    <AppLayout userInitial={userInitial}>
      <h1 className="font-nunito text-[2.1rem] leading-tight font-extrabold text-[#2D2623] tracking-tight mb-6">
        Lista zakupów
      </h1>

      <div className="flex flex-col gap-3 mb-8">
        <button className="w-full bg-white border border-[#F2ECE4] text-[#2D2623] rounded-xl py-3 flex items-center justify-center gap-2 font-semibold text-sm shadow-sm active:scale-95 transition-transform">
          <Plus size={16} strokeWidth={2.5} /> Dodaj element ręcznie
        </button>
        <button className="w-full bg-[#C24B36] text-white rounded-xl py-3 flex items-center justify-center gap-2 font-semibold text-sm shadow-sm active:scale-95 transition-transform">
          <ArrowRightToLine size={16} strokeWidth={2.5} /> Przenieś zaznaczone do spiżarni
        </button>
      </div>

      <div className="space-y-3">
        {items.map((item: any) => (
          <label 
            key={item.id} 
            className={`w-full rounded-[1.2rem] p-4 flex items-center gap-4 cursor-pointer transition-colors ${item.is_checked ? 'bg-[#F2ECE4]/50' : 'bg-white border border-[#F2ECE4] shadow-sm'}`}
          >
            <div className="relative flex items-center justify-center">
              <input 
                type="checkbox" 
                checked={item.is_checked}
                onChange={() => toggleCheck(item.id)}
                className="peer appearance-none w-6 h-6 border-2 border-[#DCE6D0] rounded-md checked:bg-[#8CA86E] checked:border-[#8CA86E] transition-colors"
              />
              <svg className="absolute w-4 h-4 text-white pointer-events-none opacity-0 peer-checked:opacity-100" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            
            <div className="flex-1">
              <p className={`font-nunito text-[1.1rem] font-bold ${item.is_checked ? 'text-[#8C837C] line-through' : 'text-[#2D2623]'}`}>
                {item.ingredient_name} ({item.quantity_value} {item.quantity_unit})
              </p>
              <p className={`text-xs italic mt-0.5 ${item.is_checked ? 'text-[#8C837C]/70' : 'text-[#C24B36]'}`}>
                {item.category}
              </p>
            </div>
          </label>
        ))}
      </div>
    </AppLayout>
  );
}