import { MessageCircleQuestion, Plus } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Navbar({ showNewQuery }: { showNewQuery: boolean }) {
  const navigate = useNavigate();

  const handleHomeClick = (e: React.MouseEvent) => {
    e.preventDefault();
    if (showNewQuery) {
      navigate(0);
    } else {
      navigate("/");
    }
  };

  return (
    <nav className="w-full sticky top-0 z-50 bg-primary-gray text-white shadow-md transition-all">
      <header className="max-w-5xl mx-auto w-full h-16 px-4 sm:px-8 flex items-center justify-between">
        {/* Identidad / Logo */}
        <a
          href="/"
          onClick={handleHomeClick}
          className="flex items-center gap-3 group cursor-pointer focus:outline-none rounded-lg p-1 -ml-1 transition-transform active:scale-[0.98]"
        >
          <div className="flex flex-col text-left">
            <span className="font-bold text-base sm:text-lg leading-tight tracking-tight text-white">
              Gestión Inteligente
            </span>
          </div>
        </a>

        {/* Acciones */}
        <div className="flex items-center gap-3 sm:gap-4">
          {/* Asistencia / 147 */}
          <a
            href="https://buenosaires.gob.ar/gcaba_historico/noticias/como-funciona-la-nueva-aplicacion-ba-147"
            target="_blank"
            rel="noopener noreferrer"
            title="Atención ciudadana - Boti y 147"
            className="hidden sm:flex items-center gap-1.5 text-xs text-gray-200 hover:text-white transition-colors px-2.5 py-1.5 rounded-md hover:bg-white/10"
          >
            <MessageCircleQuestion className="w-4 h-4 text-primary-yellow" />
            <span>Ayuda 147</span>
          </a>

          {/* Botón de Nueva Consulta */}
          {showNewQuery && (
            <button
              onClick={() => navigate(0)}
              aria-label="Nueva consulta"
              className="flex items-center gap-2 text-xs sm:text-sm font-semibold cursor-pointer px-3.5 py-1.5 sm:px-4 sm:py-2 rounded-lg bg-primary-yellow text-primary-gray hover:brightness-105 active:scale-[0.97] transition-all shadow-sm"
            >
              <Plus size={16} strokeWidth={2.5} className="shrink-0" />
              <span>Nueva consulta</span>
            </button>
          )}
        </div>
      </header>
    </nav>
  );
}
