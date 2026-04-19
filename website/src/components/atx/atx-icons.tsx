import type { AtxIconName } from "@/lib/atx-data";

interface AtxIconProps {
  name: AtxIconName;
  className?: string;
}

export function AtxIcon({ name, className }: AtxIconProps) {
  const common = {
    width: "1em",
    height: "1em",
    viewBox: "0 0 16 16",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.5,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    className,
    "aria-hidden": true,
  };

  switch (name) {
    case "identity":
      return (
        <svg {...common}>
          <circle cx="8" cy="5.5" r="2.5" />
          <path d="M2.5 14c0-3 2.5-5 5.5-5s5.5 2 5.5 5" />
        </svg>
      );
    case "card":
      return (
        <svg {...common}>
          <rect x="2" y="3.5" width="12" height="9" rx="1.5" />
          <path d="M2 6.5h12M4.5 10h3" />
        </svg>
      );
    case "did":
      return (
        <svg {...common}>
          <circle cx="8" cy="8" r="5.5" />
          <path d="M2.5 8h11M8 2.5c1.8 2 1.8 9 0 11M8 2.5c-1.8 2-1.8 9 0 11" />
        </svg>
      );
    case "deleg":
      return (
        <svg {...common}>
          <circle cx="4" cy="4" r="2" />
          <circle cx="12" cy="12" r="2" />
          <path d="M5.5 5.5l5 5" />
        </svg>
      );
    case "trust":
      return (
        <svg {...common}>
          <path d="M8 1.5l5 2v4c0 3-2.3 5.5-5 7-2.7-1.5-5-4-5-7v-4l5-2z" />
          <path d="M6 8l1.5 1.5L10.5 6.5" />
        </svg>
      );
    case "check":
      return (
        <svg {...common}>
          <path d="M2.5 8h11M2.5 4h11M2.5 12h11" />
          <circle cx="12" cy="8" r="1.3" fill="currentColor" stroke="none" />
        </svg>
      );
    case "cred":
      return (
        <svg {...common}>
          <rect x="2" y="2.5" width="12" height="11" rx="1" />
          <path d="M4.5 6h7M4.5 9h4M9 12.5l1 1 2-2.5" />
        </svg>
      );
    case "prov":
      return (
        <svg {...common}>
          <path d="M3 3v10M13 3v10M3 3h10M3 8h10M3 13h10" />
        </svg>
      );
    case "chain":
      return (
        <svg {...common}>
          <rect x="1.5" y="5" width="5" height="6" rx="1" />
          <rect x="9.5" y="5" width="5" height="6" rx="1" />
          <path d="M6.5 8h3" />
        </svg>
      );
    case "search":
      return (
        <svg {...common}>
          <circle cx="7" cy="7" r="4.5" />
          <path d="M10.5 10.5l3 3" />
        </svg>
      );
    case "plus":
      return (
        <svg {...common}>
          <path d="M8 3v10M3 8h10" />
        </svg>
      );
    case "arrow":
      return (
        <svg {...common}>
          <path d="M3 8h10M9 4l4 4-4 4" />
        </svg>
      );
    case "arrowBack":
      return (
        <svg {...common}>
          <path d="M13 8H3M7 4L3 8l4 4" />
        </svg>
      );
    case "chev":
      return (
        <svg {...common}>
          <path d="M5 6l3 3 3-3" />
        </svg>
      );
    case "chevR":
      return (
        <svg {...common}>
          <path d="M6 4l4 4-4 4" />
        </svg>
      );
    case "ext":
      return (
        <svg {...common}>
          <path d="M7 3H3v10h10V9M10 3h3v3M8 8l5-5" />
        </svg>
      );
    case "copy":
      return (
        <svg {...common}>
          <rect x="5" y="5" width="8" height="8" rx="1" />
          <path d="M3 11V4a1 1 0 011-1h7" />
        </svg>
      );
    case "close":
      return (
        <svg {...common}>
          <path d="M4 4l8 8M12 4l-8 8" />
        </svg>
      );
    case "lock":
      return (
        <svg {...common}>
          <rect x="3" y="7" width="10" height="7" rx="1" />
          <path d="M5.5 7V5a2.5 2.5 0 015 0v2" />
        </svg>
      );
    case "eye":
      return (
        <svg {...common}>
          <path d="M1.5 8s2.5-4.5 6.5-4.5S14.5 8 14.5 8 12 12.5 8 12.5 1.5 8 1.5 8z" />
          <circle cx="8" cy="8" r="2" />
        </svg>
      );
    case "book":
      return (
        <svg {...common}>
          <path d="M2.5 3.5a2 2 0 012-2H13v11H4.5a2 2 0 00-2 2v-11z" />
          <path d="M2.5 12.5a2 2 0 012-2H13" />
        </svg>
      );
    default:
      return null;
  }
}
