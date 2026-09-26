import { constructMetadata } from "@/lib/utils";
import { ComplianceChecker } from "./compliance-checker";

export const metadata = constructMetadata({
  title: "EU AI Act Compliance Checker",
  description:
    "Find out your AI system's risk level under the EU AI Act in 60 seconds. Free interactive assessment tool by Attestix.",
});

export default function ComplianceCheckerPage() {
  return (
    <div className="pb-20 pt-16">
      <ComplianceChecker />
    </div>
  );
}
