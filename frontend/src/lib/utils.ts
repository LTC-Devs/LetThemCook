export function getIngredientWord(count: number): string {
  if (count === 1) return "składnika";
  const lastDigit = count % 10;
  const lastTwoDigits = count % 100;
  if (lastDigit >= 2 && lastDigit <= 4 && (lastTwoDigits < 12 || lastTwoDigits > 14)) {
    return "składniki";
  }
  return "składników";
}