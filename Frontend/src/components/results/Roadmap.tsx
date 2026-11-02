import { Route, Check } from "lucide-react";

export default function Roadmap() {

    const steps = [
        { id: 1, title: "Consulta de Uso", description: "Permitido" },
        { id: 2, title: "Habilitación", description: "Estas aquí" },
        { id: 3, title: "Permisos" },
        { id: 4, title: "Inspección" },
    ];

    const currentStep = 2;

    return (
        <article className="flex flex-col gap-4 p-6 w-full bg-background-gray rounded-xl shadow-[0_1px_2px_2px_rgba(0,0,0,0.30),0_2px_3px_1px_rgba(0,0,0,0.10)]">

            <div className="flex items-start gap-2">
                <Route className="w-6 h-6 mt-1 shrink-0 text-semantic-blue"/>

                <h2 className="text-2xl font-semibold text-primary-gray">
                    Tu camino a seguir
                </h2>
            </div>
            
            <div className="w-full p-6">
                <div className="flex items-start w-full">

                    {steps.map((step, index) => {
                    const completed = step.id < currentStep;
                    const current = step.id === currentStep;

                    return (
                        <div
                        key={step.id}
                        className="flex flex-col flex-1 items-center relative"
                        >
                            {/* Línea conectora */}
                            {index !== steps.length - 1 && (
                                <div className={`absolute top-5 left-1/2 w-full h-[3px] ${
                                    completed
                                    ? "bg-semantic-green"
                                    : "bg-gray-300"
                                }`}/>
                            )}

                            {/* Círculo */}
                            <div
                                className={`relative z-10 w-10 h-10 rounded-full
                                flex items-center justify-center border-2 font-bold text-lg mb-4
                                ${
                                    completed
                                    ? "bg-gray-200 ring-semantic-green ring-3 text-semantic-green font-extrabold text-xl"
                                    : current
                                    ? "bg-primary-yellow border-gray-200 border-3 text-gray-500 ring-2 ring-primary-yellow ring-4"
                                    : "bg-gray-200 ring ring-2 text-gray-400"
                                }`}
                            >
                                {completed ? <Check size={25} strokeWidth={4.5}/> : step.id}
                            </div>

                            {/* Texto */}
                            <div className="mt-3 text-center">
                                <p
                                className={`text-sm font-semibold ${
                                    completed
                                    ? "text-gray-800"
                                    : current
                                    ? "text-gray-800"
                                    : "text-gray-400"
                                }`}
                                >
                                {step.title}
                                </p>

                                <p className={`text-xs text-gray-500 mt-1 ${
                                    completed
                                    ? "font-semibold"
                                    : current
                                    ? "text-semantic-blue font-semibold"
                                    : "text-gray-400"
                                }`}
                                >
                                {step.description}
                                </p>
                            </div>
                        </div>
                    );
                    })}
                </div>
            </div>

        </article>
    );
}