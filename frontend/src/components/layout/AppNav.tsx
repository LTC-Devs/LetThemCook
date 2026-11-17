import Link from "next/link";

const navigation = [
  { href: "/", label: "Start" },
  { href: "/recipes", label: "Przepisy" },
  { href: "/pantry", label: "Spiżarnia" },
  { href: "/recommendations", label: "Rekomendacje" },
  { href: "/shopping", label: "Zakupy" },
  { href: "/profile", label: "Profil" },
];

export function AppNav() {
  return (
    <header className="border-b border-zinc-200 bg-white">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-5 px-6 py-5">
        <Link href="/" className="font-semibold text-emerald-800">
          Let Them Cook
        </Link>
        <nav aria-label="Nawigacja główna" className="flex flex-wrap gap-4 text-sm text-zinc-700">
          {navigation.map(({ href, label }) => (
            <Link key={href} href={href} className="hover:text-emerald-700">
              {label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
