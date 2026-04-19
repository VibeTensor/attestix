import { Header } from "@/components/sections/header";
import { FooterV2 } from "@/components/sections/v2/footer-v2";

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
        className="mx-auto w-full max-w-[1080px] flex-1 px-7 py-16"
      >
        <article className="prose prose-sm dark:prose-invert max-w-none">
          {children}
        </article>
      </main>
      <FooterV2 />
    </div>
  );
}
