import { constructMetadata } from "@/lib/utils";
import { ReputationDashboard } from "./reputation-dashboard";

export const metadata = constructMetadata({
  title: "AI Agent Reputation Dashboard",
  description:
    "Explore how Attestix tracks verifiable reputation scores for AI agents. Interactive demo with trust scores, compliance breakdowns, and simulated interactions.",
});

export default function ReputationDashboardPage() {
  return (
    <div className="pb-20">
      <ReputationDashboard />
    </div>
  );
}
