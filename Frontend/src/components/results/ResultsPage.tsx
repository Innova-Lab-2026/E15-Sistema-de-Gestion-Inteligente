import { resultsData } from "./resultsData";

import Procedures from "./Procedures";
import Requirements from "./Requirements";
import Roadmap from "./Roadmap";
import Sources from "./Sources";
import Summary from "./Summary";
import MapLocation from "../ui/MapLocation";
import type { LatLngExpression } from "leaflet";
import Alert from "../ui/Alert";

export default function ResultsPage() {
  const position: LatLngExpression = [-34.604694295560144, -58.402042990374156];

  return (
    <main className="flex flex-col justify-start text-left bg-background-white-2 h-full mx-auto w-full gap-12 px-15 py-8 max-md:px-8">
      <h1 className="text-3xl font-semibold text-primary-gray">
        {resultsData.title}
      </h1>

      <div className="grid grid-cols-[2fr_1fr] max-sm:grid-cols-1 gap-10 w-full">
        {/* Columna izquierda */}
        <div className="flex flex-col gap-8 order-2 sm:order-1">
          {/* Resumen */}
          <Summary
            activity={resultsData.activity}
            location={resultsData.location}
            summary={resultsData.summary}
          />

          {/* Pasos */}
          <Roadmap />

          {/* Tramites */}
          <Procedures procedures={resultsData.procedures} />
        </div>

        {/* Columna derecha - Mapa */}
        <article className="flex flex-col p-6 h-fit w-full gap-4 bg-background-gray rounded-xl border border-secundary-gray shadow-[0_4px_4px_0px_rgba(0,0,0,0.25)] order-1 sm:order-2">
          <div className="flex flex-col gap-4 w-full h-full bg-background-white border-2 border-background-gray-2 p-4 rounded-xl">
            <div className="">
              <h2 className="text-xl font-semibold text-primary-gray bg-background-white">
                Ubicación
              </h2>
              <p className="text-primary-gray text-sm">Av. Corrientes 2500</p>
            </div>
            <MapLocation position={position} />
            {/* <iframe
              className="w-full h-full"
              title="Mapa de ubicación"
              src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3282.091187059168!2d-58.41015568477046!3d-34.60373858046086!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x95bcca5e6c8a7e9b%3A0x8c8c8c8c8c8c8c8c!2sAv.%20Corrientes%202500%2C%20C1045%20CABA%2C%20Argentina!5e0!3m2!1ses-419!2sus!4v1620000000000"
            /> */}
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
      <Requirements requirements={resultsData.requirements} />

      {/* Fuentes */}
      <Sources />
    </main>
  );
}
