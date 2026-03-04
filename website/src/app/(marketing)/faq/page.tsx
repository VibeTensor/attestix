import { FAQ } from "@/components/sections/faq";
import { constructMetadata } from "@/lib/utils";

export const metadata = constructMetadata({
  title: "FAQ",
  description: "Frequently asked questions about Attestix.",
});

export default function FAQPage() {
  return (
    <div className="mt-24">
      <div className="text-center py-16">
        <h1 className="text-3xl font-bold text-foreground sm:text-4xl">
          Frequently Asked Questions
        </h1>
        <p className="mt-4 text-xl text-muted-foreground">
          Everything you need to know about Attestix
        </p>
      </div>
      <FAQ />
    </div>
  );
}
