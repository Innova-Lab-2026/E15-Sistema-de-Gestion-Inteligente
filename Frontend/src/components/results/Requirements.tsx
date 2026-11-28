import type { Requirement } from "@/utils/consult-type";
import RequirementGroup from "../ui/RequirementGroup";

export default function Requirements({
  requirements,
}: {
  requirements: Requirement[];
}) {
  return (
    <section className="flex flex-col gap-4 sm:gap-6">
      <h2 className="text-xl sm:text-2xl font-semibold text-primary-gray">
        Requisitos
      </h2>

      <article className="flex flex-col gap-6 p-4 sm:p-6 w-full bg-background-gray rounded-xl border border-secundary-gray shadow-[0_4px_4px_0px_rgba(0,0,0,0.25)]">
        {requirements.map((group) => (
          <RequirementGroup
            key={group.id}
            title={group.title}
            items={group.documents}
          />
        ))}
      </article>
    </section>
  );
}
