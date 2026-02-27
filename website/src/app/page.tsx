import { Blog } from "@/components/sections/blog";
import { Community } from "@/components/sections/community";
import { CTA } from "@/components/sections/cta";
import { Examples } from "@/components/sections/examples";
import { FAQ } from "@/components/sections/faq";
import { Features } from "@/components/sections/features";
import { Footer } from "@/components/sections/footer";
import { Header } from "@/components/sections/header";
import { Hero } from "@/components/sections/hero";
import { Logos } from "@/components/sections/logos";
import { Pricing } from "@/components/sections/pricing";
import { Statistics } from "@/components/sections/statistics";
import { Testimonials } from "@/components/sections/testimonials";
import { UseCases } from "@/components/sections/use-cases";
import { siteConfig } from "@/lib/config";

const jsonLd = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: "Attestix",
  description:
    "Attestation Infrastructure for AI Agents. Verifiable identity, W3C credentials, delegation chains, and reputation scoring. 47 MCP tools across 9 modules.",
  url: siteConfig.url,
  applicationCategory: "DeveloperApplication",
  operatingSystem: "Cross-platform",
  license: "https://opensource.org/licenses/Apache-2.0",
  offers: {
    "@type": "Offer",
    price: "0",
    priceCurrency: "USD",
  },
  author: {
    "@type": "Organization",
    name: "VibeTensor",
    url: "https://vibetensor.com",
  },
  codeRepository: siteConfig.links.github,
  programmingLanguage: "Python",
  softwareVersion: "0.2.2",
};

export default function Home() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <main>
        <Header />
        <Hero />
        <Logos />
        <Examples />
        <UseCases />
        <Features />
        <Statistics />
        <Testimonials />
        <Pricing />
        <FAQ />
        <Community />
        <Blog />
        <CTA />
        <Footer />
      </main>
    </>
  );
}
