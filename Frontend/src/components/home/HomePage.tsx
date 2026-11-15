import {
  getConsultationStatusFeedback,
  type ConsultResponse,
} from "@/utils/consult-type";
import { useEffect, useRef, useState } from "react";
import ResultsPage from "../results/ResultsPage";
import Alert from "../ui/Alert";
import LoadingScreen from "./LoadingScreen";

const URL_API = "https://orientacion-ciudadana.onrender.com";

export default function HomePage() {
  const queryRef = useRef<HTMLInputElement>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [consult, setConsult] = useState<ConsultResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isCompleted, setIsCompleted] = useState(false);

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

  const handleOnSubmit = async (e: React.SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();

    const query = queryRef.current?.value.trim();

    if (query === "") {
      setError("La consulta no puede estar vacía");
      queryRef.current?.select();
      return;
    }

    if (query) {
      setError("");
      setIsLoading(true);
      try {
        const res = await fetch(`${URL_API}/api/v1/consultations`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ query: query }),
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
      } catch (error) {
        setError(
          "No se pudo conectar con el servidor. Por favor, verifica tu conexión a internet o intenta nuevamente más tarde.",
        );
      } finally {
        setIsLoading(false);
      }
    }
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
    <section className="flex flex-col items-center justify-center max-md:pt-12 max-md:pb-12 bg-background-white-2 py-18 max-md:h-full mx-auto w-full max-md:px-4 gap-8">
      <div className="">
        <h1 className="text-4xl font-semibold text-primary-gray">
          ¿Qué querés hacer en la ciudad?
        </h1>
        <p className="mt-5 text-primary-gray-2 text-base">
          Te ayudamos a entender trámites, requisitos y contexto territorial,
          según el lugar exacto donde estés.
        </p>
      </div>
      {statusFeedback && (
        <div className="w-full max-w-3xl">
          <Alert
            key={`status-${consult?.consultation_id || consult?.status}`}
            message={statusFeedback.message}
            title={statusFeedback.title}
            type={statusFeedback.type}
          >
            {statusFeedback.suggestion && (
              <p className="mt-2.5 text-xs sm:text-sm text-primary-gray-2 bg-white/70 p-2.5 rounded-md border border-black/5">
                <strong className="text-primary-gray">Sugerencia: </strong>
                {statusFeedback.suggestion}
              </p>
            )}
          </Alert>
        </div>
      )}
      <form
        onSubmit={handleOnSubmit}
        className="relative w-full max-w-3xl mt-5 mx-auto flex flex-col sm:block gap-3 sm:gap-0"
      >
        <input
          ref={queryRef}
          className="p-2 pl-5 pr-5 sm:pr-36 w-full h-14 sm:h-16 rounded-lg text-primary-gray placeholder-primary-gray bg-white border-2 border-secundary-gray shadow-lg text-sm sm:text-base focus:outline-none focus:ring-2 focus:ring-primary-yellow/60 focus:border-white"
          type="text"
          maxLength={100}
          placeholder="Ej.: Quiero abrir una cafeteria en Av. Corrientes 2500"
        />
        {error && (
          <p className=" text-left text-sm font-semibold  text-semantic-red">
            {error}
          </p>
        )}
        <button
          type="submit"
          disabled={isLoading}
          className="bg-primary-yellow hover:brightness-95 active:scale-[0.98] transition-all cursor-pointer font-semibold rounded-lg sm:rounded-md h-12 w-full sm:w-32 text-primary-gray static sm:absolute z-10 sm:top-2 sm:right-2 px-5 flex items-center justify-center text-sm sm:text-base shadow-sm sm:shadow-none"
        >
          Consultar
        </button>
      </form>
      <p className="mt-5 text-primary-gray-2 text-base font-semibold">
        Consultas frecuentes:
      </p>
      <ul className=" flex text-primary-gray font-semibold text-base gap-4 max-sm:flex-col max-sm:items-center">
        <li className="border px-2 py-1 bg-background-white rounded-md border-gray-400 text-sm cursor-pointer">
          Abrir local gastronómico
        </li>
        <li className="border px-2 py-1 bg-background-white rounded-md border-gray-400 text-sm cursor-pointer">
          Aviso de obra
        </li>
        <li className="border px-2 py-1 bg-background-white rounded-md border-gray-400 text-sm cursor-pointer">
          Ver zona comercial
        </li>
      </ul>
    </section>
  );
}
