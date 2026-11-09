export type AlertType = "info" | "success" | "warning" | "error";

export const typeStyles: Record<
  AlertType,
  {
    container: string;
    iconColor: string;
    defaultIcon: React.ReactNode;
  }
> = {
  info: {
    container: "border-semantic-blue bg-[#EBF7FD]",
    iconColor: "text-semantic-blue",
    defaultIcon: (
      <svg
        className="w-5 h-5 shrink-0 text-semantic-blue"
        viewBox="0 0 20 20"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        <circle cx="10" cy="10" r="9" fill="currentColor" />
        <circle cx="10" cy="6.3" r="1.1" fill="white" />
        <rect x="8.8" y="8.8" width="2.4" height="5.6" rx="1.2" fill="white" />
      </svg>
    ),
  },
  success: {
    container: "border-semantic-green bg-[#EDF9F0]",
    iconColor: "text-semantic-green",
    defaultIcon: (
      <svg
        className="w-5 h-5 shrink-0 text-semantic-green"
        viewBox="0 0 20 20"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        <circle cx="10" cy="10" r="9" fill="currentColor" />
        <path
          d="M6.5 10.2L8.9 12.6L13.8 7.5"
          stroke="white"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
  },
  warning: {
    container: "border-semantic-orange bg-[#FFF8EC]",
    iconColor: "text-semantic-orange",
    defaultIcon: (
      <svg
        className="w-5 h-5 shrink-0 text-semantic-orange"
        viewBox="0 0 20 20"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        <path
          d="M8.27 3.33a2 2 0 013.46 0l6.5 11.25A2 2 0 0116.5 17.5h-13a2 2 0 01-1.73-2.92l6.5-11.25z"
          fill="currentColor"
        />
        <rect x="9" y="7.5" width="2" height="4.5" rx="1" fill="white" />
        <circle cx="10" cy="14.3" r="1" fill="white" />
      </svg>
    ),
  },
  error: {
    container: "border-semantic-red bg-[#FDF2F2]",
    iconColor: "text-semantic-red",
    defaultIcon: (
      <svg
        className="w-5 h-5 shrink-0 text-semantic-red"
        viewBox="0 0 20 20"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        <circle cx="10" cy="10" r="9" fill="currentColor" />
        <rect x="9" y="5.8" width="2" height="5" rx="1" fill="white" />
        <circle cx="10" cy="13.5" r="1.1" fill="white" />
      </svg>
    ),
  },
};
