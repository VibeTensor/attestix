"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { Button } from "@/components/ui/button";
import { assessRiskLevel, type RiskAssessment } from "./risk-engine";
import { StepSystemType } from "./step-system-type";
import { StepDeploymentContext } from "./step-deployment-context";
import { StepResult } from "./step-result";

type SystemType =
  | "chatbot"
  | "content-generation"
  | "decision-support"
  | "biometric"
  | "medical"
  | "autonomous"
  | "education"
  | "other";

interface FormState {
  systemType: SystemType | null;
  otherDescription: string;
  deploymentContext: Set<string>;
}

const TOTAL_STEPS = 3;

export function ComplianceChecker() {
  const [currentStep, setCurrentStep] = useState(1);
  const [formState, setFormState] = useState<FormState>({
    systemType: null,
    otherDescription: "",
    deploymentContext: new Set<string>(),
  });
  const [result, setResult] = useState<RiskAssessment | null>(null);

  const canProceedStep1 =
    formState.systemType !== null &&
    (formState.systemType !== "other" || formState.otherDescription.trim().length > 0);

  const canProceedStep2 = formState.deploymentContext.size > 0;

  const handleNext = () => {
    if (currentStep === 1 && canProceedStep1) {
      setCurrentStep(2);
    } else if (currentStep === 2) {
      const assessment = assessRiskLevel(
        formState.systemType!,
        formState.deploymentContext,
        formState.otherDescription
      );
      setResult(assessment);
      setCurrentStep(3);
    }
  };

  const handleBack = () => {
    if (currentStep === 2) {
      setCurrentStep(1);
    }
  };

  const handleStartOver = () => {
    setCurrentStep(1);
    setFormState({
      systemType: null,
      otherDescription: "",
      deploymentContext: new Set<string>(),
    });
    setResult(null);
  };

  const handleSystemTypeChange = (type: SystemType) => {
    setFormState((prev) => ({ ...prev, systemType: type }));
  };

  const handleOtherDescriptionChange = (value: string) => {
    setFormState((prev) => ({ ...prev, otherDescription: value }));
  };

  const handleToggleContext = (contextId: string) => {
    setFormState((prev) => {
      const next = new Set(prev.deploymentContext);
      if (next.has(contextId)) {
        next.delete(contextId);
      } else {
        next.add(contextId);
      }
      return { ...prev, deploymentContext: next };
    });
  };

  return (
    <div className="mx-auto max-w-3xl px-4 sm:px-6">
      {/* Header */}
      <div className="text-center py-12">
        <h1 className="text-3xl font-bold text-foreground sm:text-4xl tracking-tight">
          EU AI Act Compliance Checker
        </h1>
        <p className="mt-4 text-lg text-muted-foreground">
          Find out your AI system&apos;s risk level in 60 seconds
        </p>
      </div>

      {/* Progress Bar */}
      <ProgressBar currentStep={currentStep} totalSteps={TOTAL_STEPS} />

      {/* Step Content */}
      <div className="mt-8 min-h-[480px]">
        <AnimatePresence mode="wait">
          {currentStep === 1 && (
            <motion.div
              key="step-1"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
            >
              <StepSystemType
                selectedType={formState.systemType}
                otherDescription={formState.otherDescription}
                onTypeChange={handleSystemTypeChange}
                onOtherDescriptionChange={handleOtherDescriptionChange}
              />
            </motion.div>
          )}

          {currentStep === 2 && (
            <motion.div
              key="step-2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
            >
              <StepDeploymentContext
                selectedContexts={formState.deploymentContext}
                onToggleContext={handleToggleContext}
              />
            </motion.div>
          )}

          {currentStep === 3 && result && (
            <motion.div
              key="step-3"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
            >
              <StepResult result={result} onStartOver={handleStartOver} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Navigation Buttons */}
      {currentStep < 3 && (
        <div className="mt-8 flex items-center justify-between">
          <div>
            {currentStep > 1 && (
              <Button variant="outline" onClick={handleBack}>
                Back
              </Button>
            )}
          </div>
          <Button
            onClick={handleNext}
            disabled={
              (currentStep === 1 && !canProceedStep1) ||
              (currentStep === 2 && !canProceedStep2)
            }
          >
            {currentStep === 2 ? "Get Results" : "Next"}
          </Button>
        </div>
      )}
    </div>
  );
}

function ProgressBar({
  currentStep,
  totalSteps,
}: {
  currentStep: number;
  totalSteps: number;
}) {
  const stepLabels = ["System Type", "Deployment", "Results"];

  return (
    <div className="mx-auto max-w-lg">
      <div className="flex items-center justify-between mb-2">
        {stepLabels.map((label, index) => {
          const stepNum = index + 1;
          const isActive = stepNum === currentStep;
          const isComplete = stepNum < currentStep;

          return (
            <div key={label} className="flex items-center gap-2">
              <div
                className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium transition-colors duration-300 ${
                  isComplete
                    ? "bg-primary text-primary-foreground"
                    : isActive
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-muted-foreground"
                }`}
              >
                {isComplete ? (
                  <svg
                    className="h-4 w-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={2.5}
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M4.5 12.75l6 6 9-13.5"
                    />
                  </svg>
                ) : (
                  stepNum
                )}
              </div>
              <span
                className={`hidden text-sm sm:block ${
                  isActive || isComplete
                    ? "font-medium text-foreground"
                    : "text-muted-foreground"
                }`}
              >
                {label}
              </span>
            </div>
          );
        })}
      </div>
      {/* Progress track */}
      <div className="mt-3 h-1.5 w-full rounded-full bg-muted">
        <motion.div
          className="h-full rounded-full bg-primary"
          initial={{ width: "0%" }}
          animate={{
            width: `${((currentStep - 1) / (totalSteps - 1)) * 100}%`,
          }}
          transition={{ duration: 0.4, ease: "easeInOut" }}
        />
      </div>
    </div>
  );
}
