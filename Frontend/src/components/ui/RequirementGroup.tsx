export default function RequirementGroup({ title, items }: { title: string; items: { id: number; description: string }[] }) {
    return (
        <div>
            <h3 className="text-base font-semibold text-primary-gray mb-2">
                {title}
            </h3>

            <ul className="space-y-2">
                {items.map((item) => (
                    <li
                        key={item.id}
                        className="flex gap-2 text-sm text-primary-gray-2"
                    >
                        <span className="h-1.5 w-1.5 mt-1 shrink-0 rounded-full bg-primary-gray"/>
                        {item.description}
                    </li>
                ))}
            </ul>
        </div>
    );
}