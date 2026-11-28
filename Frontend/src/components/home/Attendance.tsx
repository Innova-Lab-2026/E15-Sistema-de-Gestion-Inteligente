import { MessageCircle } from "lucide-react";

export default function Attendance() {
  return (
    <>
      {/* Asistencia ciudadana Boti / 147 no invasiva */}
      <div className="mt-4 flex flex-wrap items-center justify-center gap-2 text-xs text-primary-gray-2 bg-semantic-blue/5 border border-semantic-blue/20 rounded-xl px-4 py-2.5 max-w-3xl w-full">
        <span className="font-semibold text-primary-gray">
          ¿Tenés dudas con tu trámite o consulta?
        </span>
        <span>
          Llamá al{" "}
          <a
            href="tel:147"
            className="font-bold text-semantic-blue hover:underline"
          >
            147
          </a>
        </span>
        <span className="text-gray-400">•</span>
        <span>o escribile a</span>
        <a
          href="https://wa.me/5491150500147"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 font-bold text-semantic-green hover:underline"
        >
          <MessageCircle className="w-3.5 h-3.5" />
          Boti por WhatsApp
        </a>
      </div>
    </>
  );
}
