
import { useEffect } from "react";
import {
  Check,
  X,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  FileText,
} from "lucide-react";

import type { Step } from "@/utils/consult-type";

interface RoadmapModalProps {
  selected: Step;
  steps: Step[];
  currentStep: number;
  onClose: () => void;
  onNavigate: (step: Step) => void;
}

export default function RoadmapModal({
  selected,
  steps,
  currentStep,
  onClose,
  onNavigate,
}: RoadmapModalProps) {

  const selectedIndex = steps.findIndex(
    (step) => step.order === selected.order
  );

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [onClose]);

  if (selectedIndex === -1) return null;

  const completed = selectedIndex < currentStep;
  const current = selectedIndex === currentStep;

  const progress = ((selectedIndex + 1) / steps.length) * 100;

  const status = completed
    ? "Completado"
    : current
      ? "En progreso"
      : "Pendiente";

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="roadmap-modal-title"
        className="w-full max-w-lg max-h-[90dvh] bg-background-gray rounded-2xl shadow-xl flex flex-col overflow-hidden"
      >

        {/* Header */}
        <div className="flex items-center justify-between px-5 pt-5 sm:px-6 sm:pt-6">
          <span className="text-xs font-semibold text-semantic-blue uppercase tracking-wider">
            Paso {selectedIndex} de {steps.length - 1}
          </span>

          <button
            type="button"
            onClick={onClose}
            aria-label="Cerrar"
            className="flex items-center justify-center w-9 h-9 rounded-full text-primary-gray-2 hover:bg-background-gray-2 transition-colors"
          >
            <X size={19} />
          </button>
        </div>

        {/* Título y estado */}
        <div className="flex items-center gap-3 px-5 pt-4 sm:px-6">
          <div
            className={`flex items-center justify-center w-12 h-12 shrink-0 rounded-full font-bold text-lg ${
              completed
                ? "border-2 border-semantic-green text-semantic-green"
                : current
                  ? "bg-primary-yellow! border-2 border-background-gray ring-4 ring-primary-yellow/35 text-primary-gray-2 scale-105"
                  : "border-2 border-roadmap-inactive text-gray-400"
            }`}
          >
            {completed ? (
              <Check size={23} strokeWidth={2.5} />
            ) : (
              selectedIndex
            )}
          </div>

          <div className="flex flex-col gap-1 min-w-0">
            <h3
              id="roadmap-modal-title"
              className="text-lg font-semibold text-primary-gray leading-snug"
            >
              {selected.title}
            </h3>

            <span
              className={`text-xs font-semibold w-fit ${
                  completed
                    ? "text-semantic-green"
                    : current
                      ? "text-primary-gray-2"
                      : "text-roadmap-inactive"
                }`}
            >
              {status}
            </span>
          </div>
        </div>

        {/* Barra de progreso */}
        <div
          className="h-1.5 bg-background-gray-2 mx-5 mt-5 rounded-full overflow-hidden sm:mx-6"
          role="progressbar"
          aria-label="Progreso del recorrido"
          aria-valuenow={Math.round(progress)}
          aria-valuemin={0}
          aria-valuemax={100}
        >
          <div
            className={`h-full rounded-full transition-all duration-300 ${
              completed
                ? "bg-semantic-green"
                : "bg-primary-yellow"
            }`}
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Contenido */}
        <div className="flex-1 overflow-y-auto px-5 py-5 sm:px-6">
          <div className="flex flex-col gap-2">
            <h4 className="text-sm font-semibold text-primary-gray">
              ¿Qué tenés que hacer?
            </h4>

            <p className="text-sm leading-relaxed text-primary-gray-2 whitespace-pre-line">
              {selected.description}
            </p>
          </div>

          {/* Fuente oficial */}
          {selected.url_fuente && (
            <a
              href={selected.url_fuente}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-between gap-3 mt-5 p-3 rounded-xl bg-background-gray-2 hover:opacity-80 transition-opacity group"
            >
              <div className="flex items-center gap-3 min-w-0">
                <FileText
                  size={20}
                  className="text-semantic-blue shrink-0"
                />

                <div className="min-w-0">
                  <p className="text-sm font-semibold text-primary-gray">
                    Consultar fuente oficial
                  </p>

                  <p className="text-xs text-primary-gray-2 truncate">
                    {selected.url_fuente}
                  </p>
                </div>
              </div>

              <ExternalLink
                size={17}
                className="text-semantic-blue shrink-0 group-hover:translate-x-0.5 transition-transform"
              />
            </a>
          )}

          {/* Referencias */}
          {selected.source_ids?.length > 0 && (
            <div className="flex items-center gap-2 mt-4 text-xs text-primary-gray-2">
              <FileText size={15} className="shrink-0" />

              <span>
                {selected.source_ids.length}{" "}
                {selected.source_ids.length === 1
                  ? "referencia asociada"
                  : "referencias asociadas"}
              </span>
            </div>
          )}
        </div>

        {/* Navegación */}
        <div className="flex items-center justify-between gap-3 px-5 py-4 sm:px-6 border-t border-secundary-gray bg-primary-gray">
          <button
            type="button"
            disabled={selectedIndex === 0}
            onClick={() => onNavigate(steps[selectedIndex - 1])}
            className="flex items-center gap-1 text-sm font-medium text-white hover:opacity-70 disabled:opacity-30 disabled:cursor-not-allowed transition-opacity"
          >
            <ChevronLeft size={18} />
            Anterior
          </button>

          <button
            type="button"
            disabled={selectedIndex === steps.length - 1}
            onClick={() => onNavigate(steps[selectedIndex + 1])}
            className="flex items-center gap-1 text-sm font-medium text-white hover:opacity-70 disabled:opacity-30 disabled:cursor-not-allowed transition-opacity"
          >
            Siguiente
            <ChevronRight size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
