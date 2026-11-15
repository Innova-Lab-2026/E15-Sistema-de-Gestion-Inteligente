import type { Step } from "@/utils/consult-type";
import { Check, Route } from "lucide-react";

export default function Roadmap({ stepsConsult }: { stepsConsult: Step[] }) {
  const stepInitial: Step = {
    order: 0,
    title: "Consulta de Uso",
    description: "Permitido",
    url_fuente: "",
    source_ids: [],
  };

  const steps: Step[] = [stepInitial, ...stepsConsult];

  const currentStep = 1;

  return (
    <article className="flex flex-col gap-6 p-6 w-full max-md:px-4 bg-background-gray rounded-xl border border-secundary-gray shadow-[0_4px_12px_rgba(0,0,0,0.18)]">
      {/* Header con indicador de progreso */}
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-semantic-blue/10 text-semantic-blue">
            <Route className="w-5 h-5 shrink-0" />
          </div>
          <h2 className="text-xl md:text-2xl font-semibold text-primary-gray">
            Tu camino a seguir
          </h2>
        </div>

        <span className="text-xs font-medium px-3 py-1 rounded-full bg-secundary-gray/40 text-primary-gray">
          Paso {Math.min(currentStep, steps.length)} de {steps.length}
        </span>
      </div>

      {/* Contenedor del Roadmap: Vertical en móvil, Horizontal en desktop */}
      <div className="w-full pt-2 pb-1">
        <ol className="grid grid-cols-1 md:grid-cols-4 gap-y-8 md:gap-x-0">
          {steps.map((step, index) => {
            const completed = step.order < currentStep;
            const current = step.order === currentStep;
            const isLast = index === steps.length - 1;
            const isFirst = index === 0;
            const isEndOfDesktopRow = (index + 1) % 4 === 0;

            return (
              <li
                key={step.order}
                className="relative flex md:flex-col items-start md:items-center gap-4 md:gap-0 group"
              >
                {/* Línea conectora Desktop (Horizontal) */}
                {!isLast && !isEndOfDesktopRow && (
                  <div
                    aria-hidden="true"
                    className={`hidden md:block absolute top-5 left-1/2 w-full h-0.75 transition-colors duration-300 ${
                      completed ? "bg-semantic-green" : "bg-roadmap-inactive"
                    }`}
                  />
                )}

                {/* Línea conectora Mobile (Vertical) */}
                {!isLast && (
                  <div
                    aria-hidden="true"
                    className={`md:hidden absolute left-5 top-10 w-0.75 h-[calc(100%+2rem)] -translate-x-1/2 transition-colors duration-300 ${
                      completed ? "bg-semantic-green" : "bg-roadmap-inactive"
                    }`}
                  />
                )}

                {/* Nodo / Círculo (con bg-background-gray opaco para no transparentar la línea) */}
                <div
                  className={`relative z-10 w-10 h-10 shrink-0 rounded-full flex items-center justify-center font-bold text-base transition-all duration-300 bg-background-gray ${
                    completed
                      ? "border-2 border-semantic-green text-semantic-green"
                      : current
                        ? "bg-primary-yellow! border-2 border-background-gray ring-4 ring-primary-yellow/35 text-primary-gray-2 scale-105"
                        : "border-2 border-roadmap-inactive text-gray-400"
                  }`}
                >
                  {/* Capa sutil de color sin perder opacidad */}
                  {completed && (
                    <span className="absolute inset-0 rounded-full bg-semantic-green/15 pointer-events-none" />
                  )}

                  <span className="relative z-10">
                    {completed ? (
                      <Check className="w-5 h-5" strokeWidth={3} />
                    ) : (
                      step.order
                    )}
                  </span>
                </div>

                {/* Contenido de texto */}
                <div className="md:mt-4 md:px-3 text-left md:text-center flex-1">
                  <p
                    className={`text-sm font-semibold leading-snug transition-colors ${
                      completed || current
                        ? "text-primary-gray"
                        : "text-gray-400"
                    }`}
                  >
                    {step.title}
                  </p>
                  {current && (
                    <div className="flex gap-2 flex-col">
                      <span className=" block text-[10px] mt-1 max-md:w-20 text-center uppercase tracking-wider font-bold text-black rounded-md bg-primary-yellow mb-0.5">
                        Estas aquí
                      </span>
                      <a
                        target="_blank"
                        className="text-semantic-blue underline text-xs font-semibold"
                        href={step.url_fuente}
                      >
                        Más Detalles
                      </a>
                    </div>
                  )}
                  {isFirst && (
                    <p className="text-xs mt-1 text-gray-800">Permitido</p>
                  )}
                  {/* {current && (
                    <p
                      className={`text-xs mt-1 leading-relaxed ${
                        current
                          ? "text-primary-gray/90 font-medium"
                          : completed
                            ? "text-primary-gray/70"
                            : "text-gray-400/80"
                      }`}
                    >
                      {step.description}
                    </p>
                  )} */}
                </div>
              </li>
            );
          })}
        </ol>
      </div>
    </article>
  );
}
