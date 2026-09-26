import { Header } from "@/components/sections/header";
import { HeroV2 } from "@/components/sections/v2/hero-v2";
import { HeroStats } from "@/components/sections/v2/hero-stats";
import { TrustStrip } from "@/components/sections/v2/trust-strip";
import { StandardsStrip } from "@/components/sections/v2/standards-strip";
import { ProblemSection } from "@/components/sections/v2/problem";
import { ModulesSection } from "@/components/sections/v2/modules";
import { WorkflowSection } from "@/components/sections/v2/workflow";
import { ConsolePreviewSection } from "@/components/sections/v2/console-preview";
import { ValidationSection } from "@/components/sections/v2/validation";
import { FrameworksSection } from "@/components/sections/v2/frameworks";
import { UseCasesSection } from "@/components/sections/v2/use-cases";
import { BenchmarksSection } from "@/components/sections/v2/benchmarks";
import { ComplianceMatrixSection } from "@/components/sections/v2/compliance-matrix";
import { CtaV2 } from "@/components/sections/v2/cta-v2";
import { FooterV2 } from "@/components/sections/v2/footer-v2";
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
      <div className="bg-atx-bg text-atx-ink">
        <Header />
        <main id="main-content" tabIndex={-1}>
          {/* hero -> trust -> the product itself -> numbers, then the story */}
          <HeroV2 />
          <TrustStrip />
          <ConsolePreviewSection />
          <div className="mx-auto max-w-[1320px] px-7">
            <HeroStats />
          </div>
          <StandardsStrip />
          <ProblemSection />
          <ModulesSection />
          <WorkflowSection />
          <ValidationSection />
          <FrameworksSection />
          <UseCasesSection />
          <BenchmarksSection />
          <ComplianceMatrixSection />
          <CtaV2 />
        </main>
        <FooterV2 />
      </div>
    </>
  );
}
