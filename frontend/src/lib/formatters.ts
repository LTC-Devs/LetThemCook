const MONTHS = ["STYCZNIA", "LUTEGO", "MARCA", "KWIETNIA", "MAJA", "CZERWCA", "LIPCA", "SIERPNIA", "WRZEŚNIA", "PAŹDZIERNIKA", "LISTOPADA", "GRUDNIA"];
const SHORT_MONTHS = ["STY", "LUT", "MAR", "KWI", "MAJ", "CZE", "LIP", "SIE", "WRZ", "PAŹ", "LIS", "GRU"];
const DAYS = ["NIEDZIELA", "PONIEDZIAŁEK", "WTOREK", "ŚRODA", "CZWARTEK", "PIĄTEK", "SOBOTA"];
const SHORT_DAYS = ["ND", "PN", "WT", "ŚR", "CZ", "PT", "SB"];

export function isToday(dateString?: string): boolean {
  if (!dateString) return false;
  const today = new Date();
  const date = new Date(dateString);
  return date.getDate() === today.getDate() && 
         date.getMonth() === today.getMonth() && 
         date.getFullYear() === today.getFullYear();
}

export function formatFullDate(dateString?: string): string {
  if (!dateString) return "BRAK DATY";
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return "NIEPRAWIDŁOWA DATA";
  
  const dayName = DAYS[date.getDay()];
  const dayNumber = date.getDate();
  const monthName = MONTHS[date.getMonth()];
  return `${dayName}, ${dayNumber} ${monthName}`;
}

export function formatCardDate(dateString?: string) {
  if (!dateString || isNaN(new Date(dateString).getTime())) {
    return { dayName: "--", dayNumber: "--", month: "---" };
  }
  const date = new Date(dateString);
  return {
    dayName: SHORT_DAYS[date.getDay()],
    dayNumber: String(date.getDate()).padStart(2, "0"),
    month: SHORT_MONTHS[date.getMonth()]
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