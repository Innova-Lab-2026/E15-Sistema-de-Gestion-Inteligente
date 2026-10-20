interface LoadingSpinnerProps {
  size?: number | string;
  className?: string;
  color?: string;
  trackColor?: string;
  strokeWidth?: number;
}

export default function Spinner({
  size = 64,
  className = "",
  color = "#00637c",
  trackColor = "#E2E8F0",
  strokeWidth = 4.5,
}: LoadingSpinnerProps) {
  return (
    <div
      className={`inline-flex items-center justify-center ${className}`}
      role="status"
      aria-label="Cargando"
    >
      <svg
        className="animate-spin"
        width={size}
        height={size}
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Track / fondo circular suave */}
        <circle
          cx="24"
          cy="24"
          r="19"
          stroke={trackColor}
          strokeWidth={strokeWidth}
        />
        {/* Arco activo giratorio */}
        <circle
          cx="24"
          cy="24"
          r="19"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray="82 120"
        />
      </svg>
    </div>
  );
}

export { Spinner };
