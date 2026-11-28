import type { ConsultResponse } from "@/utils/consult-type";
import type { LatLngExpression } from "leaflet";
import Alert from "../ui/Alert";
import MapLocation from "../ui/MapLocation";
import Procedures from "./Procedures";
import Requirements from "./Requirements";
import Roadmap from "./Roadmap";
import Sources from "./Sources";
import Summary from "./Summary";

export default function ResultsPage({ consult }: { consult: ConsultResponse }) {
  const position: LatLngExpression = [
    consult.location.latitude,
    consult.location.longitude,
  ];

  return (
    <main className="flex flex-col justify-start text-left bg-background-white-2 h-full mx-auto w-full gap-12 px-15 py-8 max-md:px-8">
      <h1 className="text-3xl font-semibold text-primary-gray">
        Abrir {consult.interpretation.activity.raw_text} en{" "}
        {consult.location.normalized_address}
      </h1>

      <div className="grid grid-cols-[2fr_1fr] max-sm:grid-cols-1 gap-10 w-full">
        {/* Columna izquierda */}
        <div className="flex flex-col gap-8 order-2 sm:order-1">
          {/* Resumen */}
          <Summary
            activity={consult.interpretation.activity.raw_text}
            location={consult.location.normalized_address}
            summary={{
              description: consult.summary,
              title: consult.interpretation.activity.display_name,
            }}
            steps={consult.steps.length}
            procedures={consult.sources.length}
            documents={consult.sources.length}
          />

          {/* Pasos */}
          <Roadmap stepsConsult={consult.steps} />

          {/* Tramites */}
          <Procedures procedures={consult.documents} />
        </div>

        {/* Columna derecha - Mapa */}
        <article className="flex flex-col p-6 h-fit w-full gap-4 bg-background-gray rounded-xl border border-secundary-gray shadow-[0_4px_4px_0px_rgba(0,0,0,0.25)] order-1 sm:order-2">
          <div className="flex flex-col gap-4 w-full h-full bg-background-white border-2 border-background-gray-2 p-4 rounded-xl">
            <div className="">
              <h2 className="text-xl font-semibold text-primary-gray bg-background-white">
                Ubicación
              </h2>
              <p className="text-primary-gray text-sm">
                {consult.location.normalized_address}
              </p>
            </div>
            <MapLocation position={position} />
            <button className="shrink-0 px-4 py-2 bg-semantic-blue text-white hover:brightness-95 active:scale-[0.98] trasition-all cursor-pointer font-semibold rounded-lg text-sm sm:text-base">
              Abrir mapa interactivo
            </button>
          </div>

          <h3 className="text-base font-semibold text-primary-gray">
            Contexto de la zona
          </h3>
          <div className="flex flex-col gap-4">
            <Alert
              title="Alta densidad peatonal"
              layout="block"
              message="Zona de alto tráfico ideal para cafeterías"
              type="info"
            />
            <Alert
              title="Area de protección histórica"
              layout="block"
              message="La marquesina del local requiere aprobación (APH). "
              type="warning"
            />
          </div>
        </article>
      </div>

      {/* Requisitos */}
      <Requirements requirements={consult.requirements} />

      {/* Fuentes */}
      <Sources />
    </main>
  );
}
