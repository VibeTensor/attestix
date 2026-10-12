import { constructMetadata } from "@/lib/utils";
import { IdentityExplorer } from "./identity-explorer";

export const metadata = constructMetadata({
  title: "Agent Identity Explorer",
  description:
    "See what a verifiable AI agent identity looks like. Create a simulated UAIT and explore every field, from DIDs to trust scores.",
});

export default function IdentityExplorerPage() {
  return (
    <div className="pb-20 pt-16">
      <IdentityExplorer />
    </div>
  );
}
