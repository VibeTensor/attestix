import { Pricing } from "@/components/sections/pricing";
import { constructMetadata } from "@/lib/utils";

export const metadata = constructMetadata({
  title: "Pricing",
  description:
    "Open source with Apache 2.0 license. Enterprise support available.",
});

export default function PricingPage() {
  return (
    <div className="mt-24">
      <div className="text-center py-16">
        <h1 className="text-3xl font-bold text-foreground sm:text-4xl">
          Pricing
        </h1>
        <p className="mt-4 text-xl text-muted-foreground">
          Open source. Enterprise support available.
        </p>
      </div>
      <Pricing />
    </div>
  );
}
