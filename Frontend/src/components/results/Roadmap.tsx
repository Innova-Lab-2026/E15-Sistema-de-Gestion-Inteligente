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
        <article className="flex flex-col gap-4 p-6 w-full bg-background-gray rounded-xl border border-secundary-gray shadow-[0_4px_4px_0px_rgba(0,0,0,0.25)]">

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
                                    : "bg-roadmap-inactive"
                                }`}/>
                            )}

                            {/* Círculo */}
                            <div
                                className={`relative z-10 w-10 h-10 rounded-full
                                flex items-center justify-center border-2 font-bold text-lg mb-4
                                ${
                                    completed
                                    ? "bg-background-gray ring-semantic-green ring-3 text-semantic-green font-extrabold text-xl"
                                    : current
                                    ? "bg-primary-yellow border-background-gray border-3 ring-4 ring-primary-yellow text-primary-gray-2 text-xl"
                                    : "bg-background-gray border-none ring-3 ring-roadmap-inactive text-primary-gray-2 text-xl"
                                }`}
                            >
                                {completed ? <Check size={25} strokeWidth={4.5}/> : step.id}
                            </div>

                            {/* Texto */}
                            <div className="mt-3 text-center">
                                <p
                                className={`text-sm font-semibold ${
                                    completed
                                    ? "text-primary-gray"
                                    : current
                                    ? "text-primary-gray"
                                    : "text-gray-400"
                                }`}
                                >
                                {step.title}
                                </p>

                                <p className={`text-xs text-primary-gray mt-1 ${
                                    completed
                                    ? ""
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