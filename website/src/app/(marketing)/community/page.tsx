import { Community } from "@/components/sections/community";
import { constructMetadata } from "@/lib/utils";

export const metadata = constructMetadata({
  title: "Community",
  description:
    "Join the Attestix community. Contribute, collaborate, and build the trust layer for AI agents.",
});

export default function CommunityPage() {
  return (
    <div className="pt-8">
      <Community />
    </div>
  );
}
