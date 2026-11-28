import type { Procedure } from "@/utils/consult-type";
import ProcedureCard from "../ui/ProcedureCard";

export default function Procedures({
  procedures,
}: {
  procedures: Procedure[];
}) {
  return (
    <section className="flex flex-col gap-8">
      <h2 className="mt-4 text-2xl font-semibold text-primary-gray">
        2 - Trámites requeridos
      </h2>

      {procedures.slice(0, 3).map((procedure, index) => (
        <ProcedureCard
          key={index}
          title={procedure.name}
          url_fuente={procedure.url_fuente}
          description={procedure.details}
        />
      ))}
    </section>
  );
}
