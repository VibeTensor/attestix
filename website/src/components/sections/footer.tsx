import { Icons } from "@/components/icons";
import { BorderText } from "@/components/ui/border-number";
import { siteConfig } from "@/lib/config";
import Link from "next/link";

const legalLinks = [
  { text: "Privacy Policy", href: "/legal/privacy" },
  { text: "Terms of Service", href: "/legal/terms" },
  { text: "Cookie Policy", href: "/legal/cookies" },
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
        </div>
      </div>
      <div className="flex flex-col justify-between gap-y-5 md:flex-row md:items-center">
        <ul className="flex flex-col gap-x-5 gap-y-2 text-muted-foreground md:flex-row md:items-center">
          {siteConfig.footer.links.map((link, index) => (
            <li
              key={index}
              className="text-[15px]/normal font-medium text-muted-foreground transition-all duration-100 ease-linear hover:text-foreground hover:underline hover:underline-offset-4"
            >
              <a href={link.url} target="_blank" rel="noopener noreferrer">
                {link.text}
              </a>
            </li>
          ))}
        </ul>
        <div className="flex items-center justify-between text-sm font-medium tracking-tight text-muted-foreground">
          <p>{siteConfig.footer.bottomText}</p>
        </div>
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
