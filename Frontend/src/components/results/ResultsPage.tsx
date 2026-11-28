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
    <main className="flex flex-col justify-start text-left bg-background-white-2 h-full mx-auto w-full max-w-6xl gap-8 sm:gap-10 px-4 sm:px-8 lg:px-12 py-6 sm:py-8">
      <h1 className="text-2xl sm:text-3xl md:text-4xl font-semibold text-primary-gray wrap-break-word leading-tight">
        Abrir {consult.interpretation.activity.raw_text} en{" "}
        {consult.location.normalized_address}
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-[2fr_1fr] gap-6 sm:gap-8 lg:gap-10 w-full items-start">
        {/* Columna izquierda */}
        <div className="flex flex-col gap-6 sm:gap-8 w-full min-w-0 order-2 lg:order-1">
          {/* Resumen */}
          <Summary
            activity={consult.interpretation.activity.raw_text}
            location={consult.location.normalized_address}
            summary={{
              description: consult.summary,
              title: consult.interpretation.activity.display_name,
            }}
            steps={consult.steps.length || 0}
            procedures={consult.documents.slice(0, 3).length || 0}
            documents={consult.documents.length || 0}
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
              <p className="text-primary-gray text-xs sm:text-sm wrap-break-word">
                {consult.location.normalized_address}
              </p>
            </div>
            <MapLocation position={position} />
            <button className="w-full shrink-0 px-4 py-2 bg-semantic-blue text-white hover:brightness-95 active:scale-[0.98] transition-all cursor-pointer font-semibold rounded-lg text-sm sm:text-base">
              Abrir mapa interactivo
            </button>
          </div>

          <h3 className="text-sm sm:text-base font-semibold text-primary-gray">
            Contexto de la zona
          </h3>
          <div className="flex flex-col gap-3">
            {consult.zoning.rubro_allowed && (
              <Alert
                title="El rubro está permitido en esta dirección"
                layout="block"
                message="La actividad cumple con la normativa de Mixtura de Usos del lote."
                type="info"
              />
            )}
            {!consult.zoning.rubro_allowed && (
              <Alert
                title="Actividad no permitida en esta parcela"
                layout="block"
                message="Según el Código Urbanístico (Ciudad 3D), este rubro no está habilitado para la mixtura de usos de la dirección ingresada. Probá consultando otra ubicación o corredor comercial."
                type="error"
              />
            )}
            <Alert
              title="Area de protección histórica"
              layout="block"
              message="La marquesina del local requiere aprobación (APH)."
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
