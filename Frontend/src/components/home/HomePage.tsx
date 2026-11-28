import { URL_API } from "@/utils/constants";
import {
  getConsultationStatusFeedback,
  type ConsultResponse,
} from "@/utils/consult-type";
import { AlertTriangle, MapPin, Sparkles } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useOutletContext } from "react-router-dom";
import ResultsPage from "../results/ResultsPage";
import Attendance from "./Attendance";
import LoadingScreen from "./LoadingScreen";
import Questions from "./Questions";

export default function HomePage() {
  const queryRef = useRef<HTMLInputElement>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [consult, setConsult] = useState<ConsultResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isCompleted, setIsCompleted] = useState(false);

  const { setShowNewQuery } = useOutletContext<{
    setShowNewQuery: (value: boolean) => void;
  }>();

  useEffect(() => {
    if (queryRef.current) {
      queryRef.current.focus();
      queryRef.current.select();
    }

    return () => {
      if (queryRef.current) {
        queryRef.current.value = "";
      }
    };
  }, []);

  const executeConsultation = async (queryText: string) => {
    const trimmed = queryText.trim();

    if (trimmed === "") {
      setError("La consulta no puede estar vacía");
      queryRef.current?.focus();
      return;
    }

    setError(null);
    setIsLoading(true);
    setShowNewQuery(true);
    try {
      const res = await fetch(`${URL_API}/api/v1/consultations`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: trimmed }),
      });
      if (!res.ok) {
        throw new Error(
          `Sucedio un error al solicitar la consulta: ${res.status} `,
        );
      }
      const data: ConsultResponse = await res.json();
      setConsult(data);
      if (data.status === "complete") {
        setIsCompleted(true);
      }
    } catch {
      setError(
        "No se pudo conectar con el servidor. Por favor, verifica tu conexión a internet o intenta nuevamente más tarde.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleOnSubmit = async (e: React.SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    const query = queryRef.current?.value || "";
    executeConsultation(query);
  };

  const handleApplyExample = (queryText: string) => {
    if (queryRef.current) {
      queryRef.current.value = queryText;
      queryRef.current.focus();
    }
    executeConsultation(queryText);
  };

  const handleSelectCandidate = (candidateAddress: string) => {
    const currentVal = queryRef.current?.value.trim() || "";
    const detectedActivity = consult?.interpretation?.activity?.raw_text;
    let nextQuery = "";

    if (detectedActivity) {
      nextQuery = `Quiero habilitar ${detectedActivity} en ${candidateAddress}`;
    } else if (currentVal) {
      nextQuery = `${currentVal} en ${candidateAddress}`;
    } else {
      nextQuery = `Consulta en ${candidateAddress}`;
    }

    if (queryRef.current) {
      queryRef.current.value = nextQuery;
      queryRef.current.focus();
    }
    executeConsultation(nextQuery);
  };

  if (isLoading) {
    return <LoadingScreen />;
  }

  if (isCompleted && consult) {
    return <ResultsPage consult={consult} />;
  }

  const statusFeedback = consult
    ? getConsultationStatusFeedback(consult)
    : null;

  return (
    <section className="flex flex-col items-center justify-center max-md:pt-10 max-md:pb-12 bg-background-white-2 py-16 mx-auto w-full max-md:px-4 gap-6">
      <div className="text-center max-w-2xl">
        <h1 className="text-3xl sm:text-4xl font-semibold text-primary-gray">
          ¿Qué querés hacer en la ciudad?
        </h1>
        <p className="mt-3 text-primary-gray-2 text-sm sm:text-base leading-relaxed">
          Te ayudamos a entender trámites, requisitos y contexto territorial,
          según el lugar exacto donde estés.
        </p>
      </div>

      <div className="w-full max-w-3xl flex flex-col gap-3">
        <form
          onSubmit={handleOnSubmit}
          className="relative w-full flex flex-col sm:block gap-3 sm:gap-0"
        >
          <div className="relative w-full">
            <input
              ref={queryRef}
              className={`p-2 pl-5 pr-5 sm:pr-36 w-full h-14 sm:h-16 rounded-xl text-primary-gray placeholder-gray-400 bg-white border-2 shadow-sm text-sm sm:text-base transition-all focus:outline-none focus:ring-2 ${
                statusFeedback
                  ? "border-semantic-orange/70 focus:border-semantic-orange focus:ring-semantic-orange/20"
                  : error
                    ? "border-semantic-red/70 focus:border-semantic-red focus:ring-semantic-red/20"
                    : "border-secundary-gray focus:border-primary-yellow focus:ring-primary-yellow/40"
              }`}
              type="text"
              maxLength={155}
              placeholder="Ej.: Quiero abrir una cafeteria en Av. Corrientes 2500"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="bg-primary-yellow hover:brightness-105 max-md:mt-2 active:scale-[0.98] transition-all cursor-pointer font-semibold rounded-lg sm:rounded-lg h-11 sm:h-12 w-full sm:w-32 text-primary-gray static sm:absolute z-10 sm:top-2 sm:right-2 px-5 flex items-center justify-center text-sm sm:text-base shadow-sm sm:shadow-none"
            >
              Consultar
            </button>
          </div>

          {error && (
            <p className="mt-2 text-left text-sm font-semibold text-semantic-red">
              {error}
            </p>
          )}
        </form>

        {statusFeedback && (
          <div className="w-full bg-semantic-orange/10 border border-semantic-orange/30 rounded-xl p-4 sm:p-5 text-left flex flex-col gap-3.5 transition-all">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-semantic-orange shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="text-sm font-bold text-primary-gray">
                  {statusFeedback.title}
                </h3>
                <p className="text-xs sm:text-sm text-primary-gray-2 mt-0.5 leading-relaxed">
                  {statusFeedback.suggestion || statusFeedback.message}
                </p>
              </div>
            </div>

            {statusFeedback.candidates &&
              statusFeedback.candidates.length > 0 && (
                <div className="flex flex-col gap-2 pt-2 border-t border-semantic-orange/20">
                  <span className="text-xs font-semibold text-primary-gray">
                    ¿Te referías a alguna de estas ubicaciones en CABA?
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {statusFeedback.candidates.map((cand, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() =>
                          handleSelectCandidate(cand.normalized_address)
                        }
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-semantic-orange/30 text-xs font-medium text-primary-gray hover:bg-semantic-orange/15 hover:border-semantic-orange transition-all cursor-pointer shadow-xs active:scale-[0.98]"
                      >
                        <MapPin className="w-3.5 h-3.5 text-semantic-orange" />
                        <span>{cand.normalized_address}</span>
                        {cand.neighborhood && (
                          <span className="text-gray-500">
                            ({cand.neighborhood})
                          </span>
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              )}

            {/* Chip para probar un ejemplo completo con 1 clic */}
            <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-semantic-orange/15">
              <span className="text-xs text-primary-gray-2 font-medium">
                O probá este ejemplo completo:
              </span>
              <button
                type="button"
                onClick={() =>
                  handleApplyExample(
                    "Quiero abrir una cafetería en Av. Corrientes 2500",
                  )
                }
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md bg-white border border-gray-300 text-xs text-semantic-blue font-semibold hover:bg-blue-50 transition-colors cursor-pointer shadow-xs active:scale-[0.98]"
              >
                <Sparkles className="w-3.5 h-3.5 text-semantic-orange" />
                "Quiero abrir una cafetería en Av. Corrientes 2500"
              </button>
            </div>
          </div>
        )}
      </div>

      <Questions handleQuestion={handleApplyExample} />
      <Attendance />
    </section>
  );
}
