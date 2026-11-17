export default function Loading() {
  return (
    <section className="space-y-4 p-6" role="status">
      <h1 className="text-3xl font-bold">
        Ładowanie przepisu...
      </h1>
      <p className="text-zinc-600">
        Pobieranie składników i instrukcji.
      </p>
    </section>
  );
}