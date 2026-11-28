import type { Step } from "@/utils/consult-type";
import { Check, Route } from "lucide-react";
import { useState } from "react";
import RoadmapModal from "./RoadmapModal";


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

  const [selected, setSelected] = useState<Step | null>(null);

  const isVertical = steps.length > 4;
  const gridColumns = {
    1: "grid-cols-1",
    2: "grid-cols-2",
    3: "grid-cols-3",
    4: "grid-cols-4",
  };
  const columnsClass = isVertical
    ? gridColumns[1]
    : gridColumns[steps.length as keyof typeof gridColumns];

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
          Paso {Math.min(currentStep, steps.length - 1)} de {steps.length - 1}
        </span>
      </div>

      {/* Contenedor del Roadmap: Vertical en móvil, Horizontal en desktop */}
      <div className="w-full pt-2 pb-1 px-2">
        <ol
          className={`grid ${columnsClass} ${
            isVertical
              ? "gap-y-8"
              : "gap-x-0"
          }`}
        >
          {steps.map((step, index) => {
            const completed = step.order < currentStep;
            const current = step.order === currentStep;
            const isLast = index === steps.length - 1;
            const isFirst = index === 0;

            return (
              <li
                key={step.order}
                className={`relative flex group ${ 
                  isVertical
                    ? "items-start gap-4"
                    : "flex-col items-center gap-0"
                }`}
              >
                {/* Línea conectora Desktop (Horizontal) */}
                {!isLast && !isVertical && (
                  <div
                    aria-hidden="true"
                    className={`block absolute top-5 left-1/2 w-full h-0.75 transition-colors duration-300 ${
                      completed
                        ? "bg-semantic-green"
                        : "bg-roadmap-inactive"
                    }`}
                  />
                )}

                {/* Línea conectora Mobile (Vertical) */}
                {!isLast && isVertical && (
                  <div
                    aria-hidden="true"
                    className={`absolute left-5 top-10 w-0.75 h-[calc(100%+2rem)] -translate-x-1/2 transition-colors duration-300 ${
                      completed
                        ? "bg-semantic-green"
                        : "bg-roadmap-inactive"
                    }`}
                  />
                )}

                <button
                  type="button"
                  onClick={() => setSelected(step)}
                  aria-label={`Ver paso ${index + 1}: ${step.title}`}
                  className={`relative z-10 flex items-center flex-1 cursor-pointer group ${
                    isVertical
                      ? "gap-4 text-left"
                      : "flex-col gap-0 text-center"
                  }`}
                >
                  {/* Nodo / Círculo (con bg-background-gray opaco para no transparentar la línea) */}
                  <div
                    data-roadmap-node
                    className={`relative z-10 w-10 h-10 shrink-0 rounded-full flex items-center justify-center font-bold text-base transition-all duration-300 group-hover:scale-115 bg-background-gray ${
                      completed
                        ? "border-2 border-semantic-green text-semantic-green"
                        : current
                          ? "bg-primary-yellow! border-2 border-background-gray ring-4 ring-primary-yellow/35 text-primary-gray-2 scale-105"
                          : "border-2 border-roadmap-inactive text-gray-400 group-hover:text-semantic-blue group-hover:border-semantic-blue"
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
                  <div className={`flex-1 ${
                      isVertical
                        ? "text-left"
                        : "my-3 px-3 text-center"
                    }`}
                  >
                    <p
                      className={`text-sm font-semibold leading-snug transition-colors ${
                        completed || current
                          ? "text-primary-gray"
                          : "text-gray-400 group-hover:text-semantic-blue"
                      }`}
                    >
                      {step.title}
                    </p>
                    {current && (
                      <div className="flex gap-2 flex-col">
                        <p className="text-semantic-blue text-xs mt-1 font-semibold">
                          Estas aquí
                        </p>
                      </div>
                    )}
                    {isFirst && (
                      <p className="text-xs mt-1 text-gray-800">
                        Permitido
                      </p>
                    )}
                  </div>
                </button>
              </li>
            );
          })}
        </ol>
      </div>

      {/* Modal */}
      {selected && (
        <RoadmapModal
          selected={selected}
          steps={steps}
          currentStep={currentStep}
          onClose={() => setSelected(null)}
          onNavigate={setSelected}
        />
      )}
    </article>
  );
}
