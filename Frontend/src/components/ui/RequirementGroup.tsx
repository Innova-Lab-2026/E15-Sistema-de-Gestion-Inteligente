import type { Procedure } from "@/utils/consult-type";

export default function RequirementGroup({
  title,
  items,
}: {
  title: string;
  items: Procedure[];
}) {
  return (
    <div>
      <h3 className="text-base font-semibold text-primary-gray mb-2">
        {title}
      </h3>

      <ul className="flex flex-col gap-6">
        {items.map((item, index) => (
          <li key={index} className="flex gap-4  text-sm text-primary-gray-2">
            <span className="h-1.5 w-1.5 mt-3 shrink-0 rounded-full bg-primary-gray" />
            {item.details}
          </li>
        ))}
      </ul>
    </div>
  );
}
