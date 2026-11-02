export default function ProcedureCard({ title, description }: { title: string; description: string }) {
    return (
        <article className="flex flex-col sm:flex-row sm:items-center gap-4 p-6 w-full bg-background-gray rounded-xl shadow-[0_1px_2px_2px_rgba(0,0,0,0.30),0_2px_3px_1px_rgba(0,0,0,0.10)]">

            <div className="flex flex-col gap-2">
                <h3 className="text-base font-semibold text-primary-gray">
                    {title}
                </h3>

                <p className="text-primary-gray-2">
                    {description}
                </p>
            </div>

            <button className="shrink-0 px-4 py-2 rounded-lg border border-semantic-blue bg-background-white-2 text-semantic-blue font-medium hover:bg-semantic-blue/10 transition-colors">
                Ver detalles
            </button>

        </article>
    );
}