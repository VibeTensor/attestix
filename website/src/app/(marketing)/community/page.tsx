import { Community } from "@/components/sections/community";
import { constructMetadata } from "@/lib/utils";

export const metadata = constructMetadata({
  title: "Community",
  description:
    "Join the Attestix community. Contribute, collaborate, and build the trust layer for AI agents.",
});

export default function CommunityPage() {
  return (
    <div className="mt-24">
      <div className="text-center py-16">
        <h1 className="text-3xl font-bold text-foreground sm:text-4xl">
          Community
        </h1>
        <p className="mt-4 text-xl text-muted-foreground">
          Built in the open. Join us.
        </p>
      </div>
      <Community />
    </div>
  );
}
