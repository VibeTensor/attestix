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
      <h2 className="text-xl font-semibold text-foreground mb-2">
        Deployment context
      </h2>
      <p className="text-sm text-muted-foreground mb-6">
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
              className={`group relative flex items-start gap-4 rounded-lg border p-4 text-left transition-all duration-200 ${
                isSelected
                  ? "border-primary bg-primary/5 ring-1 ring-primary/20"
                  : "border-border hover:border-primary/40 hover:bg-accent/50"
              }`}
            >
              {/* Checkbox indicator */}
              <div className="mt-0.5 flex-shrink-0">
                <div
                  className={`flex h-5 w-5 items-center justify-center rounded-md border-2 transition-colors duration-200 ${
                    isSelected
                      ? "border-primary bg-primary"
                      : "border-muted-foreground/40 group-hover:border-primary/60"
                  }`}
                >
                  {isSelected && (
                    <svg
                      className="h-3.5 w-3.5 text-primary-foreground"
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
                  className={`text-sm font-medium ${
                    isSelected ? "text-foreground" : "text-foreground/90"
                  }`}
                >
                  {option.label}
                </div>
                <div className="mt-0.5 text-xs text-muted-foreground">
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
