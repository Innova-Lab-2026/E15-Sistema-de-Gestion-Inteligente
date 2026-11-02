import RequirementGroup from "../ui/RequirementGroup";

export default function Requirements({ requirements }: { requirements: { id: number; title: string; items: { id: number; description: string }[] }[] }) {
    return (
        <section className="flex flex-col gap-8">

            <h2 className="text-2xl font-semibold text-primary-gray">
                Requisitos
            </h2>

            <article className="flex flex-col gap-6 p-6 w-full bg-background-gray rounded-xl shadow-[0_1px_2px_2px_rgba(0,0,0,0.30),0_2px_3px_1px_rgba(0,0,0,0.10)]">

                {requirements.map((group) => (
                    <RequirementGroup
                        key={group.id}
                        title={group.title}
                        items={group.items}
                    />
                ))}

            </article>

        </section>
    );
}