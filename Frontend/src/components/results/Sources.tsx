import { Paperclip } from "lucide-react";

export default function Sources() {
    return (
        <section className="flex flex-col gap-4">
            <h3 className="text-lg font-semibold text-primary-gray">
                Información procesada a partir de:
            </h3>

            <ul className="flex flex-wrap gap-x-12 gap-y-2 text-sm text-primary-gray-2 md:justify-between">
                <li>
                    <a
                        href="https://buenosaires.gob.ar/gobierno/tramites"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 underline cursor-pointer"
                    >
                        <Paperclip className="h-4 w-4 shrink-0"/>
                        Portal de trámites GCBA
                    </a>
                </li>
                <li>
                    <a
                        href="https://buenosaires.gob.ar/gcaba_historico/codigo-urbanistico-y-de-edificacion"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 underline cursor-pointer"
                    >
                        <Paperclip className="h-4 w-4 shrink-0"/>
                        CUR (Código urbanístico)
                    </a>
                </li>
                <li>
                    <a
                        href="https://buenosaires.gob.ar/gcaba_historico/bienvenidos-al-portal-de-datos-abiertos-de-la-ciudad"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 underline cursor-pointer"
                    >
                        <Paperclip className="h-4 w-4 shrink-0"/>
                        BA Data Open
                    </a>
                </li>
                <li>
                    <a
                        href="https://ciudad3d.buenosaires.gob.ar/"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 underline cursor-pointer"
                    >
                        <Paperclip className="h-4 w-4 shrink-0"/>
                        Ciudad 3D
                    </a>
                </li>
            </ul>
        </section>
    );
}