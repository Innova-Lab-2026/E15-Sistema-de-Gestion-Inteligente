import { useEffect, useRef, useState } from "react";
import LoadingScreen from "./LoadingScreen";

export default function HomePage() {
  const queryRef = useRef<HTMLInputElement>(null);
  const [isLoading, setIsLoading] = useState(false);

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

  const handleOnSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    console.log(queryRef.current?.value);
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
    }, 2000);
  };

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <section className="flex flex-col items-center justify-center max-md:pt-48 max-md:pb-20 bg-background-gray h-[calc(100dvh-56px)] mx-auto w-full max-md:px-4 gap-8">
      <div className="">
        <h1 className="text-4xl font-semibold text-primary-gray">
          ¿Qué querés hacer en la ciudad?
        </h1>
        <p className="mt-5 text-primary-gray-2 text-base">
          Te ayudamos a entender trámites, requisitos y contexto territorial,
          según el lugar exacto donde estés.
        </p>
      </div>
      <form
        onSubmit={handleOnSubmit}
        className="relative w-full max-w-3xl mt-5 mx-auto flex flex-col sm:block gap-3 sm:gap-0"
      >
        <input
          ref={queryRef}
          className="p-2 pl-5 pr-5 sm:pr-36 w-full h-14 sm:h-16 rounded-lg text-primary-gray placeholder-primary-gray bg-white border-none shadow-lg text-sm sm:text-base focus:outline-none focus:ring-2 focus:ring-primary-yellow/60"
          type="text"
          placeholder="Ej.: Quiero abrir una cafeteria en Av. Corrientes 2500"
        />
        <button
          type="submit"
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
