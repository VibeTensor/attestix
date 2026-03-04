import { Icons } from "@/components/icons";
import { BorderText } from "@/components/ui/border-number";
import { siteConfig } from "@/lib/config";
import { RssIcon } from "lucide-react";
import Link from "next/link";

const legalLinks = [
  { text: "Privacy Policy", href: "/legal/privacy" },
  { text: "Terms of Service", href: "/legal/terms" },
  { text: "Cookie Policy", href: "/legal/cookies" },
  { text: "RSS Feed", href: "/feed.xml" },
];

export function Footer() {
  return (
    <footer className="flex flex-col gap-y-5 rounded-lg p-5 container max-w-[var(--container-max-width)] mx-auto">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-x-2">
          <Icons.logo className="h-5 w-5" />
          <h2 className="text-lg font-bold text-foreground">
            {siteConfig.name}
          </h2>
        </div>

        <div className="flex gap-x-2">
          {siteConfig.footer.socialLinks.map((link, index) => (
            <a
              key={index}
              href={link.url}
              target="_blank"
              rel="noopener noreferrer"
              aria-label={link.url.includes("github") ? "GitHub" : link.url.includes("twitter") ? "Twitter" : "Social link"}
              className="flex h-5 w-5 items-center justify-center text-muted-foreground transition-all duration-100 ease-linear hover:text-foreground hover:underline hover:underline-offset-4"
            >
              {link.icon}
            </a>
          ))}
          <a
            href="/feed.xml"
            aria-label="RSS Feed"
            className="flex h-5 w-5 items-center justify-center text-muted-foreground transition-all duration-100 ease-linear hover:text-foreground"
          >
            <RssIcon className="h-4 w-4" />
          </a>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-8 sm:grid-cols-3">
        {siteConfig.footer.linkGroups.map((group) => (
          <div key={group.title}>
            <h3 className="text-sm font-semibold text-foreground mb-3">
              {group.title}
            </h3>
            <ul className="space-y-2">
              {group.links.map((link) => (
                <li key={link.text}>
                  {link.external ? (
                    <a
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[15px]/normal font-medium text-muted-foreground transition-all duration-100 ease-linear hover:text-foreground hover:underline hover:underline-offset-4"
                    >
                      {link.text}
                    </a>
                  ) : (
                    <Link
                      href={link.url}
                      className="text-[15px]/normal font-medium text-muted-foreground transition-all duration-100 ease-linear hover:text-foreground hover:underline hover:underline-offset-4"
                    >
                      {link.text}
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div className="flex items-center justify-between text-sm font-medium tracking-tight text-muted-foreground">
        <p>Apache 2.0 License. Built by <a href="https://vibetensor.com" target="_blank" rel="noopener noreferrer" className="hover:text-foreground hover:underline hover:underline-offset-4 transition-all duration-100 ease-linear">VibeTensor</a>.</p>
      </div>
      <div className="flex flex-wrap gap-x-5 gap-y-2 text-sm text-muted-foreground">
        {legalLinks.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="hover:text-foreground transition-colors"
          >
            {link.text}
          </Link>
        ))}
      </div>
      <BorderText
        text={siteConfig.footer.brandText}
        className="text-[clamp(3rem,15vw,10rem)] overflow-hidden font-mono tracking-tighter font-medium"
      />
    </footer>
  );
}
