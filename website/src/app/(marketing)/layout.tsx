import { FooterV2 } from "@/components/sections/v2/footer-v2";
import { Header } from "@/components/sections/header";

interface MarketingLayoutProps {
  children: React.ReactNode;
}

export default async function Layout({ children }: MarketingLayoutProps) {
  return (
    <div className="min-h-screen bg-atx-bg text-atx-ink">
      <Header />
      <main id="main-content">{children}</main>
      <FooterV2 />
    </div>
  );
}
