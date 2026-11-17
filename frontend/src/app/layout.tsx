import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

const inter = localFont({
  src: "../fonts/Inter-VariableFont_opsz,wght.ttf",
  variable: "--font-inter",
  display: "swap",
});

const nunito = localFont({
  src: "../fonts/Nunito-VariableFont_wght.ttf",
  variable: "--font-nunito",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Let Them Cook",
  description: "Aplikacja do planowania posiłków",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pl" className={`${inter.variable} ${nunito.variable}`}>
      <body className="font-sans bg-zinc-900 text-[#2D2623] h-screen w-screen overflow-hidden flex justify-center">
        
        <div className="w-full max-w-md bg-[#FDFBF7] bg-[url('/bg-app.png')] bg-cover bg-right h-full relative shadow-2xl flex flex-col">          {children}
        </div>
        
      </body>
    </html>
  );
}
