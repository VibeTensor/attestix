import { Architecture } from "@/components/sections/architecture";
import { CTA } from "@/components/sections/cta";
import { Examples } from "@/components/sections/examples";
import { Footer } from "@/components/sections/footer";
import { Header } from "@/components/sections/header";
import { Hero } from "@/components/sections/hero";
import { Statistics } from "@/components/sections/statistics";
import { TechStack } from "@/components/sections/tech-stack";
import { Testimonials } from "@/components/sections/testimonials";
import { UseCases } from "@/components/sections/use-cases";
import { siteConfig } from "@/lib/config";

const jsonLd = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: "Attestix",
  description:
    "Attestation Infrastructure for AI Agents. Verifiable identity, W3C credentials, delegation chains, and reputation scoring.",
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
  softwareVersion: siteConfig.version,
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
        <Architecture />
        <TechStack />
        <Examples />
        <UseCases />
        <Statistics />
        <Testimonials />
        <CTA />
        <Footer />
      </main>
    </>
  );
}
