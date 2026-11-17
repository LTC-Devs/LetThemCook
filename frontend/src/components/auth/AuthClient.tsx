"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import AppLayout from "@/components/layout/AppLayout";
import { LogIn, Loader2 } from "lucide-react";

export default function AuthClient() {
  const router = useRouter();
  const [isLogin, setIsLogin] = useState(true);
  
  // Form State
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState(""); // Only used for registration
  
  // UX State
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // 1. Basic Frontend Validation
    if (!email || !password || (!isLogin && !name)) {
      setError("Wypełnij wszystkie wymagane pola.");
      return;
    }
    
    setError("");
    setIsLoading(true);

    try {
      // 2. BACKEND API INTEGRATION POINT
      // Replace this timeout with your actual fetch() call to Django.
      // Example:
      // const response = await fetch("https://your-django-api.com/auth/login", {
      //   method: "POST",
      //   headers: { "Content-Type": "application/json" },
      //   body: JSON.stringify({ email, password })
      // });
      // if (!response.ok) throw new Error("Nieprawidłowe dane logowania");
      
      // Simulating a 1-second network delay for the demo
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 3. Success Redirect
      // If validation/API passes, redirect to the homepage
      router.push("/");
      
    } catch (err: any) {
      setError(err.message || "Wystąpił błąd podczas połączenia z serwerem.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AppLayout showBottomNav={false} showProfile={false}>
      <div className="flex flex-col items-center justify-center min-h-[75vh]">
        
        <div className="w-full bg-white p-8 rounded-[2rem] border border-[#F2ECE4] shadow-sm">
          <h1 className="font-nunito text-3xl font-extrabold text-[#2D2623] mb-2 text-center">
            {isLogin ? "Witaj ponownie!" : "Dołącz do nas!"}
          </h1>
          <p className="text-center text-[#8C837C] text-sm mb-8">
            {isLogin ? "Zaloguj się, aby zaplanować swoje posiłki." : "Zarejestruj się, aby zaplanować swoje posiłki."}
          </p>

          <form className="space-y-4" onSubmit={handleSubmit}>
            
            {!isLogin && (
              <div>
                <label className="block text-xs font-bold text-[#4A423D] mb-1 uppercase tracking-wider">Imię</label>
                <input 
                  type="text" 
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  disabled={isLoading}
                  className="w-full bg-[#FDFBF7] border border-[#E5DFD6] rounded-xl px-4 py-3 text-[#2D2623] focus:outline-none focus:border-[#C24B36] disabled:opacity-60 transition-colors"
                  placeholder="Alex"
                />
              </div>
            )}
            
            <div>
              <label className="block text-xs font-bold text-[#4A423D] mb-1 uppercase tracking-wider">Email</label>
              <input 
                type="email" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading}
                className="w-full bg-[#FDFBF7] border border-[#E5DFD6] rounded-xl px-4 py-3 text-[#2D2623] focus:outline-none focus:border-[#C24B36] disabled:opacity-60 transition-colors"
                placeholder="alex@example.com"
              />
            </div>
            
            <div>
              <label className="block text-xs font-bold text-[#4A423D] mb-1 uppercase tracking-wider">Hasło</label>
              <input 
                type="password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
                className="w-full bg-[#FDFBF7] border border-[#E5DFD6] rounded-xl px-4 py-3 text-[#2D2623] focus:outline-none focus:border-[#C24B36] disabled:opacity-60 transition-colors"
                placeholder="••••••••"
              />
            </div>

            {error && (
              <p className="text-sm font-semibold text-red-600 bg-red-50 p-3 rounded-lg border border-red-100">
                {error}
              </p>
            )}

            <button 
              type="submit"
              disabled={isLoading}
              className="w-full bg-[#C24B36] text-white rounded-xl py-4 flex items-center justify-center gap-2 font-semibold shadow-sm active:scale-95 transition-all disabled:opacity-80 disabled:active:scale-100 mt-6"
            >
              {isLoading ? (
                <Loader2 size={18} strokeWidth={2.5} className="animate-spin" />
              ) : (
                <LogIn size={18} strokeWidth={2.5} />
              )}
              {isLogin ? "Zaloguj się" : "Zarejestruj się"}
            </button>
          </form>

          <div className="mt-8 text-center">
            <button 
              type="button"
              onClick={() => {
                setIsLogin(!isLogin);
                setError("");
              }}
              disabled={isLoading}
              className="text-sm font-bold text-[#C24B36] hover:underline disabled:opacity-60"
            >
              {isLogin ? "Nie masz konta? Zarejestruj się" : "Masz już konto? Zaloguj się"}
            </button>
          </div>
        </div>

      </div>
    </AppLayout>
  );
}