import ProcedureCard from "../ui/ProcedureCard";

export default function Procedures({ procedures }: { procedures: { id: number; title: string; description: string }[] }) {
    return (
        <section className="flex flex-col gap-8">

            <h2 className="mt-4 text-2xl font-semibold text-primary-gray">
                2 - Trámites requeridos (Paso 2)
            </h2>

            {procedures.map((procedure) => (
                <ProcedureCard
                    key={procedure.id}
                    title={procedure.title}
                    description={procedure.description}
                />
            ))}

        </section>
    );
}