import { Header } from "@/components/sections/header";
import { FooterV2 } from "@/components/sections/v2/footer-v2";

// Reading layout for legal documents: 720px prose column, atx tokens mapped
// onto the typography plugin so the pages match the rest of the site.
const PROSE = [
  "prose dark:prose-invert max-w-none",
  "prose-headings:text-atx-ink prose-headings:scroll-mt-20",
  "prose-h1:mb-0 prose-h1:text-[clamp(34px,5vw,52px)] prose-h1:font-normal prose-h1:leading-[1.09] prose-h1:tracking-[-0.03em] prose-h1:[text-wrap:balance]",
  "prose-h2:mt-14 prose-h2:text-[24px] prose-h2:font-medium prose-h2:leading-[1.2] prose-h2:tracking-[-0.5px]",
  "prose-h3:text-[19px] prose-h3:font-semibold prose-h3:tracking-[-0.48px]",
  "prose-p:leading-[1.65] prose-p:text-atx-ink-mid prose-li:text-atx-ink-mid prose-li:marker:text-atx-ink-dim",
  "prose-strong:text-atx-ink prose-strong:font-semibold",
  "prose-a:text-atx-accent prose-a:underline prose-a:decoration-atx-line prose-a:underline-offset-4 hover:prose-a:decoration-atx-accent",
  "prose-code:font-mono-atx prose-code:text-atx-ink",
  "prose-table:text-[14px] prose-thead:border-atx-line prose-tr:border-atx-line-soft prose-th:font-medium prose-th:text-atx-ink prose-td:text-atx-ink-mid",
  "prose-hr:border-atx-line-soft",
].join(" ");

export default function LegalLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col bg-atx-bg text-atx-ink">
      <Header />
      <main
        id="main-content"
        tabIndex={-1}
        className="mx-auto w-full max-w-[720px] flex-1 px-6 pb-20 pt-16 md:pt-20"
      >
        <article className={PROSE}>{children}</article>
      </main>
      <FooterV2 />
    </div>
  );
}
