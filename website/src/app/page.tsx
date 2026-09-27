import { Header } from "@/components/sections/header";
import { HomeDemo } from "@/components/sections/home/home-demo";
import {
  HomeFaq,
  HomeHero,
  HomeHow,
  HomeInstall,
  HomeResults,
  HomeStandards,
  HomeTalk,
} from "@/components/sections/home/sections";
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
        {/* Seal-ring texture behind the top of the page, faded out by 88%;
            editions, modules, and limits live on /platform. */}
        <main
          id="main-content"
          tabIndex={-1}
          style={{
            backgroundImage:
              "linear-gradient(to bottom, transparent 42%, var(--color-atx-bg) 88%), url(/seal-rings.svg)",
            backgroundRepeat: "no-repeat",
            backgroundPosition: "center top",
            backgroundSize: "max(100vw, 1000px) calc(max(100vw, 1000px) * 1530 / 2560)",
          }}
        >
          <HomeHero />
          <HomeDemo />
          <HomeHow />
          <HomeResults />
          <HomeStandards />
          <HomeInstall />
          <HomeFaq />
          <HomeTalk />
        </main>
        <FooterV2 />
      </div>
    </>
  );
}
