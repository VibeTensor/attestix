import { constructMetadata } from "@/lib/utils";
import { FineCalculator } from "./fine-calculator";

export const metadata = constructMetadata({
  title: "EU AI Act Fine Calculator",
  description:
    "Estimate the maximum EU AI Act fines under Article 99 for your worldwide turnover and company size, including the SME and small mid-cap rules. Three tiers: prohibited practices, other obligations, and incorrect information.",
});

export default function FineCalculatorPage() {
  return <FineCalculator />;
}
