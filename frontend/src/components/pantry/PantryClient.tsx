"use client";

import { useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import { Plus, ScanLine, Pencil, Trash2 } from "lucide-react";

export default function PantryClient({ initialData, user }: any) {
  const [items, setItems] = useState(initialData);
  const userInitial = user?.first_name ? user.first_name.charAt(0) : "U";

  return (
    <AppLayout userInitial={userInitial}>
      <h1 className="font-nunito text-[2.1rem] leading-tight font-extrabold text-[#2D2623] tracking-tight mb-6">
        Spiżarnia
      </h1>

      <div className="flex gap-3 mb-8">
        <button className="flex-1 bg-[#C24B36] text-white rounded-xl py-3 flex items-center justify-center gap-2 font-semibold text-sm shadow-sm active:scale-95 transition-transform">
          <Plus size={16} strokeWidth={2.5} /> Dodaj ręcznie
        </button>
        <button className="flex-1 bg-[#F4CBB3] text-[#2D2623] rounded-xl py-3 flex items-center justify-center gap-2 font-semibold text-sm shadow-sm active:scale-95 transition-transform">
          <ScanLine size={16} strokeWidth={2.5} /> Skanuj
        </button>
      </div>

      <div className="space-y-3">
        {items.map((item: any) => (
          <div key={item.id} className="w-full bg-white border border-[#F2ECE4] rounded-[1.2rem] p-4 flex items-center justify-between shadow-sm">
            <div>
              <h3 className="font-nunito text-[1.1rem] font-bold text-[#2D2623]">{item.ingredient_name}</h3>
              <p className="text-sm text-[#8C837C] font-medium mt-0.5">
                Ilość: {item.quantity_value} {item.quantity_unit}
              </p>
            </div>
            
            <div className="flex items-center gap-2">
              <button className="p-2 text-[#8C837C] hover:text-[#2D2623] bg-[#FDFBF7] rounded-full active:scale-90 transition-transform">
                <Pencil size={18} />
              </button>
              <button className="p-2 text-[#C24B36] hover:bg-[#Fef2f2] bg-[#FDFBF7] rounded-full active:scale-90 transition-transform">
                <Trash2 size={18} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </AppLayout>
  );
}