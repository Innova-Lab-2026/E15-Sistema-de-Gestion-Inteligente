import React, { useState } from "react";
import { X } from "lucide-react";
import { typeStyles, type AlertType } from "@/utils/alert-styles";

export interface AlertProps {
  type?: AlertType;
  title?: React.ReactNode;
  message?: React.ReactNode;
  children?: React.ReactNode;
  closable?: boolean;
  onClose?: () => void;
  className?: string;
  icon?: React.ReactNode;
  layout?: "inline" | "block";
}

export default function Alert({
  type = "info",
  title,
  message,
  children,
  closable = true,
  onClose,
  className = "",
  icon,
  layout = "inline",
}: AlertProps) {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) {
    return null;
  }

  const handleClose = () => {
    setIsVisible(false);
    onClose?.();
  };

  const styleConfig = typeStyles[type] ?? typeStyles.info;
  const renderedIcon = icon ?? styleConfig.defaultIcon;

  return (
    <div
      role="alert"
      className={`w-full flex items-start gap-3 p-3.5 sm:p-4 rounded-lg border text-sm sm:text-base leading-relaxed text-primary-gray shadow-xs transition-all [&_a]:text-semantic-blue [&_a]:underline [&_a]:underline-offset-2 hover:[&_a]:opacity-80 ${styleConfig.container} ${className}`}
    >
      <div className="shrink-0 mt-0.5">{renderedIcon}</div>

      <div className="flex-1 text-left">
        {layout === "inline" ? (
          <p className="text-primary-gray">
            {title && (
              <strong className="font-bold text-primary-gray mr-1">
                {title}
              </strong>
            )}
            {message && <span>{message}</span>}
            {children}
          </p>
        ) : (
          <div>
            {title && (
              <h4 className="font-bold text-primary-gray mb-1">{title}</h4>
            )}
            <div className="text-primary-gray">
              {message && <span>{message}</span>}
              {children}
            </div>
          </div>
        )}
      </div>

      {closable && (
        <button
          type="button"
          onClick={handleClose}
          className="shrink-0 -mr-1 -mt-1 p-1 text-primary-gray-2 hover:text-primary-gray rounded-md hover:bg-black/5 transition-colors cursor-pointer focus:outline-none"
          aria-label="Cerrar alerta"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}
