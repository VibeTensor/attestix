import { FAQ } from "@/components/sections/faq";
import { constructMetadata } from "@/lib/utils";

export const metadata = constructMetadata({
  title: "FAQ",
  description: "Frequently asked questions about Attestix.",
});

export default function FAQPage() {
  return (
    <div className="pt-8">
      <FAQ />
    </div>
  );
}
