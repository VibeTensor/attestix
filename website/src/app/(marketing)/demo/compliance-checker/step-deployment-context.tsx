"use client";

interface ContextOption {
  id: string;
  label: string;
  description: string;
}

const CONTEXT_OPTIONS: ContextOption[] = [
  {
    id: "eu-deployment",
    label: "Deployed in or serving EU users",
    description: "The system is available to users within the European Union",
  },
  {
    id: "processes-personal-data",
    label: "Processes personal data",
    description: "Handles names, emails, biometric data, health records, or other PII",
  },
  {
    id: "affects-individuals",
    label: "Makes or assists in decisions affecting individuals",
    description: "Outputs influence hiring, credit, insurance, legal, or similar outcomes",
  },
  {
    id: "regulated-sector",
    label: "Used in a regulated sector",
    description: "Operates in finance, healthcare, legal, education, or law enforcement",
  },
  {
    id: "interacts-with-users",
    label: "Interacts directly with end users",
    description: "Users communicate with or receive outputs from the AI system",
  },
  {
    id: "generates-content",
    label: "Generates content that could be mistaken for human-made",
    description: "Produces text, images, audio, or video that may appear human-created",
  },
];

interface StepDeploymentContextProps {
  selectedContexts: Set<string>;
  onToggleContext: (contextId: string) => void;
}

export function StepDeploymentContext({
  selectedContexts,
  onToggleContext,
}: StepDeploymentContextProps) {
  return (
    <div>
      <h2 className="mb-2 text-[26px] font-medium leading-[1.2] tracking-[-0.6px] text-atx-ink">
        Deployment context
      </h2>
      <p className="mb-6 text-[15px] leading-[1.6] text-atx-ink-mid">
        Select all that apply to your AI system.
      </p>

      <div className="grid gap-3">
        {CONTEXT_OPTIONS.map((option) => {
          const isSelected = selectedContexts.has(option.id);

          return (
            <button
              key={option.id}
              type="button"
              onClick={() => onToggleContext(option.id)}
              className={`group relative flex items-start gap-4 rounded-2xl border p-5 text-left transition-colors duration-200 ${
                isSelected
                  ? "border-atx-accent/50 bg-atx-accent/[0.05]"
                  : "border-atx-line bg-atx-panel/60 hover:border-atx-ink-dim"
              }`}
            >
              {/* Checkbox indicator */}
              <div className="mt-0.5 flex-shrink-0">
                <div
                  className={`flex h-5 w-5 items-center justify-center rounded-md border-2 transition-colors duration-200 ${
                    isSelected
                      ? "border-atx-accent bg-atx-accent"
                      : "border-atx-ink-faint group-hover:border-atx-ink-dim"
                  }`}
                >
                  {isSelected && (
                    <svg
                      className="h-3.5 w-3.5 text-[oklch(0.14_0.01_180)]"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={3}
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M4.5 12.75l6 6 9-13.5"
                      />
                    </svg>
                  )}
                </div>
              </div>

              {/* Label and description */}
              <div className="min-w-0">
                <div
                  className={`text-[15px] font-medium ${
                    isSelected ? "text-atx-ink" : "text-atx-ink/90"
                  }`}
                >
                  {option.label}
                </div>
                <div className="mt-1 text-[13px] leading-[1.5] text-atx-ink-dim">
                  {option.description}
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
