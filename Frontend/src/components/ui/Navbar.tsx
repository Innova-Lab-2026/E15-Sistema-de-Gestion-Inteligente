import { useNavigate } from "react-router-dom";
import { Plus } from "lucide-react";

export default function Navbar({ showNewQuery }: {showNewQuery: boolean}) {
  const navigate = useNavigate();

  return (
    <nav className="bg-primary-gray text-white h-14 px-8 font-sans flex items-center justify-center">
      <header className="flex items-center justify-between w-full">
        <a href="#" className="font-semibold">
          Gestión Inteligente
        </a>

        {showNewQuery && (
          <button
            onClick={() => navigate(0)}
            aria-label="Nueva consulta"
            className="flex items-center gap-2 text-sm font-semibold cursor-pointer group"
          >
            <span className="flex items-center justify-center rounded-full w-9 h-9 bg-white/10 group-hover:bg-white/15 transition-all duration-300 group-active:scale-95">
              <Plus size={19} strokeWidth={2} className="shrink-0" />
            </span>
            <p className="hidden sm:inline">Nueva consulta</p>
          </button>
        )}
      </header>
    </nav>
  );
}
