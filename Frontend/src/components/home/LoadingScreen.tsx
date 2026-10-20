import { useEffect, useState } from "react";
import Spinner from "../ui/Spinner";

const loadingMessages = [
  "Interpretando tu consulta",
  "Identificando actividad y ubicación",
  "Consultando normativas y BA data",
  "Estructurando tu respuesta",
];

export default function LoadingScreen() {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) =>
        prevIndex < loadingMessages.length - 1 ? prevIndex + 1 : 0,
      );
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <section className="flex flex-col items-center justify-center bg-background-gray h-[calc(100dvh-56px)] mx-auto w-full max-md:px-4 gap-8">
      <div>
        <Spinner size={72} />
      </div>
      <h1 className="text-4xl font-semibold text-primary-gray">
        {loadingMessages[currentIndex]}
      </h1>
      <p className="mt-5 text-primary-gray-2 text-base">
        Nuestra IA está integrando datos territoriales y requisitos.
      </p>
    </section>
  );
}
