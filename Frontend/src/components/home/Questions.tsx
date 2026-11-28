import { FREQUENT_QUERIES } from "@/utils/constants";

export default function Questions({
  handleQuestion,
}: {
  handleQuestion: (query: string) => void;
}) {
  return (
    /* Consultas frecuentes funcionales */
    <div className="flex flex-col items-center gap-2.5 mt-2">
      <p className="text-primary-gray-2 text-sm font-semibold">
        Consultas frecuentes de ejemplo:
      </p>
      <div className="flex flex-wrap justify-center gap-2.5">
        {FREQUENT_QUERIES.map((item, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => handleQuestion(item.query)}
            className="border px-3 py-1.5 bg-white hover:bg-primary-yellow/15 hover:border-primary-yellow/60 rounded-lg border-gray-300 text-xs font-medium text-primary-gray transition-colors cursor-pointer shadow-xs flex items-center gap-1.5 active:scale-[0.98]"
          >
            <span>{item.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
