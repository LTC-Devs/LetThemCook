import Header from "@/components/layout/Header";
import BottomNav from "@/components/layout/BottomNav";

export default function AppLayout({ 
  children, 
  showBottomNav = true,
  showProfile = true,
  userInitial = "U" // 1. Layout receives the initial
}: { 
  children: React.ReactNode; 
  showBottomNav?: boolean;
  showProfile?: boolean;
  userInitial?: string;
}) {
  return (
    <>
      <div 
        className="absolute top-0 left-0 w-full h-[110px] z-20 pointer-events-none"
        style={{
          background: "linear-gradient(to bottom, rgba(253,251,247,0.95) 40%, rgba(253,251,247,0) 100%)",
          backdropFilter: "blur(12px)",
          WebkitBackdropFilter: "blur(12px)",
          maskImage: "linear-gradient(to bottom, black 50%, transparent 100%)",
          WebkitMaskImage: "linear-gradient(to bottom, black 50%, transparent 100%)"
        }}
      />

      <div className="absolute top-0 left-0 w-full z-30 px-5 pt-4">
        {/* 2. Layout passes it to the Header */}
        <Header showProfile={showProfile} userInitial={userInitial} />
      </div>

      <div className="flex-1 overflow-y-auto px-5 pt-[85px] pb-8 no-scrollbar relative z-10">
        {children}
      </div>

      {showBottomNav && (
        <div className="flex-none relative z-20">
          <BottomNav />
        </div>
      )}
    </>
  );
}