import Link from "next/link";

type SectionPlaceholderProps = {
  title: string;
  description: string;
};

export function SectionPlaceholder({ title, description }: SectionPlaceholderProps) {
  return (
    <section className="space-y-5 rounded-2xl border border-zinc-200 bg-white p-8 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-widest text-emerald-700">LTC / frontend</p>
      <h1 className="text-3xl font-bold tracking-tight text-zinc-900">{title}</h1>
      <p className="max-w-2xl text-zinc-600">{description}</p>
      <p className="rounded-lg bg-amber-50 p-3 text-sm text-amber-950">
        Widok jest szkieletem aplikacji. Nie jest jeszcze połączony z API Django.
      </p>
      <Link href="/" className="inline-block text-sm font-medium text-emerald-800 hover:underline">
        Powrót do strony głównej
      </Link>
    </section>
  );
}
