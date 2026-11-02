import { resultsData } from "./resultsData";

import Summary from "./Summary";
import Roadmap from "./Roadmap";
import Procedures from "./Procedures";
import Requirements from "./Requirements";
import Sources from "./Sources";

export default function ResultsPage() {
    return (
        <main className="flex flex-col justify-start text-left bg-background-white-2 h-full mx-auto w-full gap-12 px-15 py-8 max-md:px-8">

            <h1 className="text-3xl font-semibold text-primary-gray">
                {resultsData.title}
            </h1>

            <div className="grid grid-cols-[2fr_1fr] max-sm:grid-cols-1 gap-10 w-full">

                {/* Columna izquierda */}
                <div className="flex flex-col gap-8">

                    {/* Resumen */}
                    <Summary
                        activity={resultsData.activity}
                        location={resultsData.location}
                        summary={resultsData.summary}
                    />

                    {/* Pasos */}
                    <Roadmap/>

                    {/* Tramites */}
                    <Procedures
                        procedures={resultsData.procedures}
                    />

                </div>

                {/* Columna derecha - Mapa */}
                <article className="flex flex-col bg-background-gray rounded-xl shadow-[0_1px_2px_2px_rgba(0,0,0,0.30),0_2px_3px_1px_rgba(0,0,0,0.10)] p-6 h-fit w-full gap-4">
                    <div className="flex flex-col gap-4 w-full h-full bg-background-white p-4 rounded-xl">
                        <h2 className="text-xl font-semibold text-primary-gray bg-background-white">
                            Ubicación
                        </h2>
                        <iframe
                            className="w-full h-full"
                            title="Mapa de ubicación"
                            src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3282.091187059168!2d-58.41015568477046!3d-34.60373858046086!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x95bcca5e6c8a7e9b%3A0x8c8c8c8c8c8c8c8c!2sAv.%20Corrientes%202500%2C%20C1045%20CABA%2C%20Argentina!5e0!3m2!1ses-419!2sus!4v1620000000000"
                        />
                        <button className="shrink-0 px-4 py-2 bg-semantic-blue text-white hover:brightness-95 active:scale-[0.98] trasition-all cursor-pointer font-semibold rounded-lg text-sm sm:text-base">
                            Abrir mapa interactivo
                        </button>
                    </div>
                    
                    <h3 className="text-base font-semibold text-primary-gray">
                        Contexto de la zona
                    </h3>
                    <div className="flex flex-col gap-4 w-full h-20 bg-sky-100 border-3 border-sky-300 p-4 rounded-xl">
                        
                    </div>
                </article>

            </div>

            {/* Requisitos */}
            <Requirements
                requirements={resultsData.requirements}
            />

            {/* Fuentes */}
            <Sources />

        </main>
    );
}