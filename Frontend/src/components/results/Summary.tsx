import { Coffee, MapPin } from "lucide-react";

export default function Summary({ activity, location, summary }: { activity: string; location: string; summary: { title: string; description: string } }) {
    return (
        <article className="flex flex-col gap-4 p-6 w-full bg-background-gray rounded-xl shadow-[0_1px_2px_2px_rgba(0,0,0,0.30),0_2px_3px_1px_rgba(0,0,0,0.10)]">

            <ul className="flex text-primary-gray font-semibold text-base gap-4 max-sm:flex-col max-sm:items-center">
                <li className="flex items-center gap-2 border px-2 py-1 bg-yellow-100 rounded-md border-gray-400 text-sm h-fit">
                    <Coffee className="h-4 w-4 shrink-0"/>
                    Actividad: {activity}
                </li>

                <li className="flex items-center gap-2 border px-2 py-1 bg-background-gray-2 rounded-md border-gray-400 text-sm h-fit">
                    <MapPin className="h-4 w-4 shrink-0"/>
                    Ubicación: {location}
                </li>
            </ul>

            <h2 className="text-2xl font-semibold text-primary-gray">
                {summary.title}
            </h2>

            <p className="text-primary-gray-2">
                {summary.description}
            </p>

        </article>
    );
}