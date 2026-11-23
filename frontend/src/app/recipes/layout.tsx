import type { ReactNode } from "react";

/**
 * The root app shell occupies the viewport and deliberately disables body
 * scrolling. Cookbook routes need their own scroll container, otherwise long
 * recipe instructions are clipped below the viewport.
 */
export default function RecipesLayout({ children }: { children: ReactNode }) {
  return (
    <main
      className="min-h-0 w-full flex-1 overflow-y-auto overscroll-y-contain touch-pan-y pb-8"
      style={{ WebkitOverflowScrolling: "touch" }}
    >
      {children}
    </main>
  );
}
