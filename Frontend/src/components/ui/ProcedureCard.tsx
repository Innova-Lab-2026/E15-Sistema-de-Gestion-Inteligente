export default function ProcedureCard({ title, description }: { title: string; description: string }) {
    return (
        <article className="flex flex-col sm:flex-row sm:items-center gap-4 p-6 w-full bg-background-gray rounded-xl border border-secundary-gray shadow-[0_4px_4px_0px_rgba(0,0,0,0.25)]">

            <div className="flex flex-col gap-2">
                <h3 className="text-base font-semibold text-primary-gray">
                    {title}
                </h3>

                <p className="text-primary-gray-2">
                    {description}
                </p>
            </div>

            <button className="shrink-0 px-4 py-2 rounded-lg border bg-secundary-gray text-primary-gray-2 font-medium hover:bg-semantic-blue/10 hover:border-semantic-blue hover:text-semantic-blue transition-colors cursor-pointer active:scale-[0.98]">
                Ver detalles
            </button>

        </article>
    );
}