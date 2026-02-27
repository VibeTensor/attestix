import { Header } from "@/components/sections/header";
import { Footer } from "@/components/sections/footer";

export default function LegalLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <Header />
      <div className="container max-w-[var(--container-max-width)] mx-auto px-6 py-12">
        <article className="prose prose-sm dark:prose-invert max-w-none">
          {children}
        </article>
      </div>
      <Footer />
    </>
  );
}
