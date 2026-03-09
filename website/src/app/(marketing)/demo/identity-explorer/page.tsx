import { constructMetadata } from "@/lib/utils";
import { IdentityExplorer } from "./identity-explorer";

export const metadata = constructMetadata({
  title: "Agent Identity Explorer",
  description:
    "See what a verifiable AI agent identity looks like. Create a simulated UAIT and explore every field, from DIDs to trust scores.",
});

export default function IdentityExplorerPage() {
  return (
    <div className="mt-24 mb-16">
      <IdentityExplorer />
    </div>
  );
}
