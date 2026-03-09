import { constructMetadata } from "@/lib/utils";
import { FineCalculator } from "./fine-calculator";

export const metadata = constructMetadata({
  title: "EU AI Act Fine Calculator",
  description:
    "Calculate your potential EU AI Act fines based on company revenue. Three tiers of penalties for prohibited practices, high-risk non-compliance, and incorrect reporting.",
});

export default function FineCalculatorPage() {
  return <FineCalculator />;
}
