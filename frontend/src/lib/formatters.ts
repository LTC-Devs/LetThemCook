const MONTHS = ["STYCZNIA", "LUTEGO", "MARCA", "KWIETNIA", "MAJA", "CZERWCA", "LIPCA", "SIERPNIA", "WRZEŚNIA", "PAŹDZIERNIKA", "LISTOPADA", "GRUDNIA"];
const SHORT_MONTHS = ["STY", "LUT", "MAR", "KWI", "MAJ", "CZE", "LIP", "SIE", "WRZ", "PAŹ", "LIS", "GRU"];
const DAYS = ["NIEDZIELA", "PONIEDZIAŁEK", "WTOREK", "ŚRODA", "CZWARTEK", "PIĄTEK", "SOBOTA"];
const SHORT_DAYS = ["ND", "PN", "WT", "ŚR", "CZ", "PT", "SB"];

function parseLocalDate(dateString?: string): Date | null {
  if (!dateString) return null;
  const isoDateOnly = /^(\d{4})-(\d{2})-(\d{2})$/.exec(dateString);
  if (isoDateOnly) {
    const [, year, month, day] = isoDateOnly;
    return new Date(Number(year), Number(month) - 1, Number(day));
  }
  const parsed = new Date(dateString);
  return isNaN(parsed.getTime()) ? null : parsed;
}

export function isToday(dateString?: string): boolean {
  const date = parseLocalDate(dateString);
  if (!date) return false;
  const today = new Date();
  return (
    date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()
  );
}

export function formatFullDate(dateString?: string): string {
  const date = parseLocalDate(dateString);
  if (!date) return "BRAK DATY";

  const dayName = DAYS[date.getDay()];
  const dayNumber = date.getDate();
  const monthName = MONTHS[date.getMonth()];
  return `${dayName}, ${dayNumber} ${monthName}`;
}

export function formatCardDate(dateString?: string) {
  const date = parseLocalDate(dateString);
  if (!date) {
    return { dayName: "--", dayNumber: "--", month: "---" };
  }
  return {
    dayName: SHORT_DAYS[date.getDay()],
    dayNumber: String(date.getDate()).padStart(2, "0"),
    month: SHORT_MONTHS[date.getMonth()],
  };
}

export function formatIngredientsSummary(ingredients?: string[]): string {
  if (!ingredients || ingredients.length === 0) return "Brak składników.";
  return `Danie zawiera: ${ingredients.join(", ")}.`;
}

export function formatIngredientsPreview(ingredients?: string[]): string {
  if (!ingredients || ingredients.length === 0) return "Brak informacji o składnikach...";
  const preview = ingredients.slice(0, 2).join(", ");
  return preview.charAt(0).toUpperCase() + preview.slice(1) + "...";
}

export function getIngredientWord(count?: number): string {
  if (count === undefined || isNaN(count)) return "składników";
  if (count === 1) return "składnika";
  const lastDigit = count % 10;
  const lastTwoDigits = count % 100;
  if (lastDigit >= 2 && lastDigit <= 4 && (lastTwoDigits < 12 || lastTwoDigits > 14)) {
    return "składniki";
  }
  return "składników";
}