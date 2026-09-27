import { TailwindIndicator } from "@/components/tailwind-indicator";
import { AtxCommandPalette } from "@/components/atx/atx-command-palette";
import { AtxCookieConsent } from "@/components/atx/atx-cookie-consent";
import { siteConfig } from "@/lib/config";
import { cn, constructMetadata } from "@/lib/utils";
import { RootProvider } from "fumadocs-ui/provider";
import SearchDialog from "@/components/search";
import { GeistMono } from "geist/font/mono";
import { GeistSans } from "geist/font/sans";
import { JetBrains_Mono } from "next/font/google";
import type { Metadata, Viewport } from "next";
import "./globals.css";

// No display serif: headings site-wide use Geist sans; the --font-serif token
// is mapped to it in globals.css so existing `font-serif` classes follow.

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-mono-atx",
  display: "swap",
});

const homeTitle = `${siteConfig.name} - Signed, verifiable evidence for every AI agent`;

export const metadata: Metadata = {
  ...constructMetadata({
    title: homeTitle,
    description:
      "Signed, tamper-evident evidence of who an AI agent is and what it did: identity, credentials, delegation, and a hash-chained audit trail. 47 MCP tools, open source, Apache 2.0.",
    alternates: {
      // No canonical at the root: it is inherited by every route.
      types: {
        "application/rss+xml": `${siteConfig.url}/feed.xml`,
        "application/feed+json": `${siteConfig.url}/feed.json`,
      },
    },
  }),
  title: { default: homeTitle, template: `%s | ${siteConfig.name}` },
};

export const viewport: Viewport = {
  colorScheme: "dark",
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#4F46E5" },
    { media: "(prefers-color-scheme: dark)", color: "#0f1219" },
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`dark ${GeistSans.variable} ${GeistMono.variable} ${jetbrainsMono.variable}`}
    >
      <body
        className={cn(
          "min-h-screen bg-background antialiased w-full mx-auto scroll-smooth font-sans"
        )}
      >
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:z-[100] focus:top-2 focus:left-2 focus:bg-primary focus:text-primary-foreground focus:px-4 focus:py-2 focus:rounded-md focus:text-sm focus:font-medium"
        >
          Skip to main content
        </a>
        <RootProvider
          theme={{
            attribute: "class",
            defaultTheme: "dark",
            enableSystem: false,
          }}
          search={{ SearchDialog }}
        >
          {children}
          <AtxCommandPalette />
          <AtxCookieConsent />
          <TailwindIndicator />
        </RootProvider>
      </body>
    </html>
  );
}
