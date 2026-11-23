# LTC: prosty, wyjaśnialny ranking przepisów (0–100 punktów)

Endpoint: `GET /api/recommendations/?count=3` (tryb `LTC_DEMO_MODE=1`).
Dane: publiczne przepisy z książki, `RecipeItem` (ilości) i aktywne partie `PantryItem`.
Wynik przeliczany jest przy każdym żądaniu; zmiana spiżarni zmienia ranking.

## Wzór

Dla każdego obowiązkowego składnika `i` o **znanej ilości** `q_i`:

- `s_i` — suma nieprzeterminowanych zapasów tego składnika w jego jednostce bazowej;
- `u_i` — część tych zapasów z terminem ważności w ciągu kolejnych 48 godzin;
- `n` — liczba ocenianych składników.

Punktacja:

1. **Dostępność (0–60):** `60 * sum(min(s_i/q_i, 1)) / n`
2. **Kompletne składniki (0–25):** `25 * liczba(s_i >= q_i) / n`
3. **Szybkie zużycie (0–15):** `15 * sum(min(s_i, u_i, q_i)/q_i) / n`

`score = zaokrąglenie(sumy, 1 miejsce)`; sortowanie malejąco wg `score`.
Przy remisie najpierw mniej braków, potem mniejsze ID przepisu.

**Przykład (23 listopada):** przepis wymaga 500 g bakłażanów.
- Nie mam bakłażanów: `0/100`.
- Mam 250 g: `30/100` (połowa wymaganej ilości, ale składnik nadal niekompletny).
- Mam 500 g, świeże: `85/100`.
- Mam 500 g z ważnością w ciągu 48 godzin: `100/100`.

## Zasady, o których trzeba powiedzieć na prezentacji

- Jednostki pochodzą z katalogu składników: `g`, `ml`, `pcs`. Nie mieszamy gramów z mililitrami.
- Partie po terminie ważności lub wycofane ze spiżarni nie są liczone.
- Składniki opcjonalne są pomijane. Dla grupy zamienników wybieramy najlepiej dostępny wariant, nie wymagamy wszystkich.
- Składniki o nieznanych ilościach (`do smaku`) **nie są oceniane ilościowo**. W API widać liczbę takich pozycji; to ograniczenie danych z OCR.
- Przepis bez ani jednej mierzalnej, obowiązkowej ilości nie bierze udziału w rankingu.
- To **heurystyka punktowa**, nie model uczenia maszynowego. Nie filtruje jeszcze alergii, diet, historii ocen ani nie uwzględnia czasu gotowania i trudności przepisu.
- W stanie pustej spiżarni przepisy mają 0 punktów; UI zachęca do dodania produktów. Nie należy interpretować takiego rankingu jako spersonalizowanego.

Do prezentacji wystarczy pokazać jeden przepis oraz zmianę `0 → 30 → 85 → 100` po aktualizacji spiżarni.
