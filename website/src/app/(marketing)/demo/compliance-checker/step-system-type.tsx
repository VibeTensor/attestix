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
      <h2 className="mb-2 text-[26px] font-medium leading-[1.2] tracking-[-0.6px] text-atx-ink">
        What type of AI system do you operate?
      </h2>
      <p className="mb-6 text-[15px] leading-[1.6] text-atx-ink-mid">
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
              className={`group relative flex items-start gap-4 rounded-2xl border p-5 text-left transition-colors duration-200 ${
                isSelected
                  ? "border-atx-accent/50 bg-atx-accent/[0.05]"
                  : "border-atx-line bg-atx-panel/60 hover:border-atx-ink-dim"
              }`}
            >
              {/* Radio indicator */}
              <div className="mt-0.5 flex-shrink-0">
                <div
                  className={`flex h-5 w-5 items-center justify-center rounded-full border-2 transition-colors duration-200 ${
                    isSelected
                      ? "border-atx-accent"
                      : "border-atx-ink-faint group-hover:border-atx-ink-dim"
                  }`}
                >
                  {isSelected && (
                    <div className="h-2.5 w-2.5 rounded-full bg-atx-accent" />
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

      {/* Free text input for "Other" */}
      {selectedType === "other" && (
        <div className="mt-4">
          <label
            htmlFor="other-description"
            className="mb-2 block text-[14px] font-medium text-atx-ink"
          >
            Describe your AI system
          </label>
          <Input
            id="other-description"
            type="text"
            placeholder="e.g., recommendation engine, spam filter, predictive analytics..."
            value={otherDescription}
            onChange={(e) => onOtherDescriptionChange(e.target.value)}
            className="w-full rounded-xl border-atx-line bg-atx-bg-sunken text-atx-ink placeholder:text-atx-ink-faint"
          />
        </div>
      )}
    </div>
  );
}
