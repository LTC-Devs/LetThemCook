"use client";

import { Home, ShoppingBag, Refrigerator } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";

const NAV_ITEMS = [
  { path: "/", icon: Home, label: "Start" },
  { path: "/shopping", icon: ShoppingBag, label: "Lista zakupów" },
  { path: "/pantry", icon: Refrigerator, label: "Spiżarnia" },
];

export default function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="w-full bg-[#FDFBF7] border-t border-[#F2ECE4] px-6 py-4 flex justify-between items-center z-50 relative">
      {NAV_ITEMS.map((item) => {
        const isActive = pathname === item.path;
        const Icon = item.icon;
        
        return (
          <Link 
            key={item.path} 
            href={item.path} 
            className="relative flex flex-col items-center gap-1 w-20 active:scale-95 transition-transform"
          >
            <Icon 
              size={24} 
              strokeWidth={isActive ? 2.5 : 2} 
              className={`transition-colors duration-300 relative z-10 ${isActive ? 'text-[#C24B36]' : 'text-[#9F9995]'}`} 
            />
            <span className={`text-[10px] transition-colors duration-300 relative z-10 ${isActive ? 'font-bold text-[#C24B36]' : 'font-medium text-[#9F9995]'}`}>
              {item.label}
            </span>
            
            {/* Animated background pill for active state */}
            {isActive && (
              <motion.div 
                layoutId="bottom-nav-active"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ type: "spring", stiffness: 300, damping: 25 }}
                className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-16 h-12 bg-[#F4CBB3]/30 rounded-xl"
              />
            )}
          </Link>
        );
      })}
    </nav>
  );
}