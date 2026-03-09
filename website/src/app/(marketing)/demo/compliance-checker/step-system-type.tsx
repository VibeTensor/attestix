"use client";

import { Input } from "@/components/ui/input";

type SystemType =
  | "chatbot"
  | "content-generation"
  | "decision-support"
  | "biometric"
  | "medical"
  | "autonomous"
  | "education"
  | "other";

interface SystemOption {
  id: SystemType;
  label: string;
  description: string;
}

const SYSTEM_OPTIONS: SystemOption[] = [
  {
    id: "chatbot",
    label: "Chatbot / Virtual Assistant",
    description: "Conversational AI that interacts with users via text or voice",
  },
  {
    id: "content-generation",
    label: "Content Generation",
    description: "AI that generates text, images, video, or audio content",
  },
  {
    id: "decision-support",
    label: "Decision Support",
    description: "AI assisting in hiring, lending, insurance, or similar decisions",
  },
  {
    id: "biometric",
    label: "Biometric / Surveillance",
    description: "Facial recognition, emotion detection, or monitoring systems",
  },
  {
    id: "medical",
    label: "Medical / Healthcare AI",
    description: "Diagnostic tools, treatment recommendations, or clinical decision support",
  },
  {
    id: "autonomous",
    label: "Autonomous Vehicle / Robotics",
    description: "Self-driving systems, drones, or autonomous industrial robots",
  },
  {
    id: "education",
    label: "Education / Training AI",
    description: "AI for grading, student assessment, or adaptive learning",
  },
  {
    id: "other",
    label: "Other",
    description: "Describe your AI system below",
  },
];

interface StepSystemTypeProps {
  selectedType: SystemType | null;
  otherDescription: string;
  onTypeChange: (type: SystemType) => void;
  onOtherDescriptionChange: (value: string) => void;
}

export function StepSystemType({
  selectedType,
  otherDescription,
  onTypeChange,
  onOtherDescriptionChange,
}: StepSystemTypeProps) {
  return (
    <div>
      <h2 className="text-xl font-semibold text-foreground mb-2">
        What type of AI system do you operate?
      </h2>
      <p className="text-sm text-muted-foreground mb-6">
        Select the category that best describes your AI system.
      </p>

      <div className="grid gap-3">
        {SYSTEM_OPTIONS.map((option) => {
          const isSelected = selectedType === option.id;

          return (
            <button
              key={option.id}
              type="button"
              onClick={() => onTypeChange(option.id)}
              className={`group relative flex items-start gap-4 rounded-lg border p-4 text-left transition-all duration-200 ${
                isSelected
                  ? "border-primary bg-primary/5 ring-1 ring-primary/20"
                  : "border-border hover:border-primary/40 hover:bg-accent/50"
              }`}
            >
              {/* Radio indicator */}
              <div className="mt-0.5 flex-shrink-0">
                <div
                  className={`flex h-5 w-5 items-center justify-center rounded-full border-2 transition-colors duration-200 ${
                    isSelected
                      ? "border-primary"
                      : "border-muted-foreground/40 group-hover:border-primary/60"
                  }`}
                >
                  {isSelected && (
                    <div className="h-2.5 w-2.5 rounded-full bg-primary" />
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

      {/* Free text input for "Other" */}
      {selectedType === "other" && (
        <div className="mt-4">
          <label
            htmlFor="other-description"
            className="block text-sm font-medium text-foreground mb-2"
          >
            Describe your AI system
          </label>
          <Input
            id="other-description"
            type="text"
            placeholder="e.g., recommendation engine, spam filter, predictive analytics..."
            value={otherDescription}
            onChange={(e) => onOtherDescriptionChange(e.target.value)}
            className="w-full"
          />
        </div>
      )}
    </div>
  );
}
