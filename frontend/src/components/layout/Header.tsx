import Image from "next/image";
import Link from "next/link";

export default function Header({ 
  showProfile = true, 
  userInitial = "U" // 3. Header accepts the initial
}: { 
  showProfile?: boolean;
  userInitial?: string;
}) {
  return (
    <header className="flex justify-between items-center w-full">
      <Link href="/" className="flex items-center gap-2 active:scale-95 transition-transform">
        <div className="relative w-8 h-8">
          <Image src="/logo.png" alt="Logo" fill sizes="32px" className="object-contain" />
        </div>
        <span className="font-nunito text-xl font-bold text-[#C24B36]">
          Let Them Cook
        </span>
      </Link>
      
      {showProfile && (
        <Link 
          href="/profile" 
          className="w-10 h-10 rounded-full bg-[#F3EBE1] flex items-center justify-center font-bold text-lg text-[#2D2623] shadow-sm active:scale-90 transition-transform cursor-pointer uppercase"
        >
          {/* 4. Header renders the initial */}
          {userInitial}
        </Link>
      )}
    </header>
  );
}