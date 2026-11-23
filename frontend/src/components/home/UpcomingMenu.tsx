import UpcomingCard, { type UpcomingMealWithColor } from "./UpcomingCard";

interface UpcomingMenuProps {
  meals: UpcomingMealWithColor[];
  onReplace: (targetDate: string) => void;
}

export default function UpcomingMenu({ meals, onReplace }: UpcomingMenuProps) {
  return (
    <div className="mt-8 space-y-4">
      <div className="flex items-end justify-between px-1">
        <h2 className="font-nunito text-2xl font-extrabold text-[#2D2623]">Co dalej w menu</h2>
      </div>

      <div className="space-y-3">
        {meals.map((meal) => (
          <UpcomingCard
            key={meal.target_date}
            meal={meal}
            onReplace={() => onReplace(meal.target_date)}
          />
        ))}
      </div>
    </div>
  );
}