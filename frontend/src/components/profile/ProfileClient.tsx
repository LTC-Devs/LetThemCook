"use client";

import { useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import { Save, LogOut } from "lucide-react";
import Link from "next/link";

export default function ProfileClient({ initialData, user }: any) {
  const [profile, setProfile] = useState(initialData);
  const userInitial = user?.first_name ? user.first_name.charAt(0) : "U";

  return (
    <AppLayout userInitial={userInitial}>
      <h1 className="font-nunito text-[2.1rem] leading-tight font-extrabold text-[#2D2623] tracking-tight mb-6">
        Profil użytkownika
      </h1>

      <div className="space-y-6">
        {/* User Info (Read-Only Demo based on Session) */}
        <div className="bg-white p-5 rounded-[1.2rem] border border-[#F2ECE4] shadow-sm mb-6">
          <p className="text-sm font-bold text-[#4A423D] mb-1">Zalogowano jako:</p>
          <p className="font-nunito text-lg font-extrabold text-[#2D2623]">
            {user?.first_name} {user?.last_name}
          </p>
          <p className="text-[#8C837C] text-sm">{user?.email}</p>
        </div>

        {/* Household Size */}
        <div className="bg-white p-5 rounded-[1.2rem] border border-[#F2ECE4] shadow-sm">
          <label className="block text-sm font-bold text-[#4A423D] mb-2">
            Wielkość porcji (osoby):
          </label>
          <input 
            type="number" 
            value={profile.household_size}
            onChange={(e) => setProfile({...profile, household_size: e.target.value})}
            className="w-full bg-[#FDFBF7] border border-[#E5DFD6] rounded-xl px-4 py-3 text-[#2D2623] focus:outline-none focus:border-[#C24B36]"
          />
        </div>

        {/* Measurement Units */}
        <div className="bg-white p-5 rounded-[1.2rem] border border-[#F2ECE4] shadow-sm">
          <label className="block text-sm font-bold text-[#4A423D] mb-2">
            System miar:
          </label>
          <select 
            value={profile.measurement_system}
            onChange={(e) => setProfile({...profile, measurement_system: e.target.value})}
            className="w-full bg-[#FDFBF7] border border-[#E5DFD6] rounded-xl px-4 py-3 text-[#2D2623] focus:outline-none focus:border-[#C24B36] appearance-none"
          >
            <option value="metric">Metryczny (kg, ml)</option>
            <option value="imperial">Imperialny (oz, lb)</option>
          </select>
        </div>

        {/* Dietary Preferences */}
        <div className="bg-white p-5 rounded-[1.2rem] border border-[#F2ECE4] shadow-sm">
          <h2 className="font-nunito text-lg font-extrabold text-[#2D2623] mb-4">
            Preferencje & Alergie
          </h2>
          
          <div className="space-y-3 mb-5">
            <label className="flex items-center gap-3 cursor-pointer">
              <input 
                type="checkbox" 
                checked={profile.is_vegetarian}
                onChange={(e) => setProfile({...profile, is_vegetarian: e.target.checked})}
                className="w-5 h-5 rounded border-[#E5DFD6] text-[#C24B36] focus:ring-[#C24B36]"
              />
              <span className="text-[#2D2623] font-medium">Wegetariańskie</span>
            </label>
            <label className="flex items-center gap-3 cursor-pointer">
              <input 
                type="checkbox" 
                checked={profile.is_gluten_free}
                onChange={(e) => setProfile({...profile, is_gluten_free: e.target.checked})}
                className="w-5 h-5 rounded border-[#E5DFD6] text-[#C24B36] focus:ring-[#C24B36]"
              />
              <span className="text-[#2D2623] font-medium">Bezglutenowe</span>
            </label>
          </div>

          <label className="block text-sm font-bold text-[#4A423D] mb-2">
            Blokowane składniki (po przecinku):
          </label>
          <input 
            type="text" 
            value={profile.blocked_ingredients}
            onChange={(e) => setProfile({...profile, blocked_ingredients: e.target.value})}
            placeholder="np. orzeszki, czosnek, owoce morza"
            className="w-full bg-[#FDFBF7] border border-[#E5DFD6] rounded-xl px-4 py-3 text-[#2D2623] focus:outline-none focus:border-[#C24B36]"
          />
        </div>

        <div className="pt-2 flex flex-col gap-3">
          <button className="w-full bg-[#C24B36] text-white rounded-xl py-4 flex items-center justify-center gap-2 font-semibold shadow-sm active:scale-95 transition-transform">
            <Save size={18} strokeWidth={2.5} /> Zapisz preferencje
          </button>
          
          <Link href="/login" className="w-full bg-white border border-[#F2ECE4] text-[#C24B36] rounded-xl py-4 flex items-center justify-center gap-2 font-semibold shadow-sm active:scale-95 transition-transform">
            <LogOut size={18} strokeWidth={2.5} /> Wyloguj się
          </Link>
        </div>
      </div>
    </AppLayout>
  );
}