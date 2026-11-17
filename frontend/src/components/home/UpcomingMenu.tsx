import UpcomingCard from "./UpcomingCard";

export default function UpcomingMenu({ meals, onReplace }: any) {
  return (
    <div className="mt-8 space-y-4">
      <div className="flex items-end justify-between px-1">
        <h2 className="font-nunito text-2xl font-extrabold text-[#2D2623]">Co dalej w menu</h2>
      </div>

      <div className="space-y-3">
        {meals.map((meal: any) => (
          <UpcomingCard 
            key={meal.id} 
            meal={meal} 
            onReplace={() => onReplace(meal.id)} 
          />
        ))}
      </div>
    </div>
  );
}