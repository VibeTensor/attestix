import { Icons } from "@/components/icons";
import { source } from "@/lib/source";
import { DocsLayout } from "fumadocs-ui/layouts/docs";
import type { ReactNode } from "react";

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <DocsLayout
      tree={source.pageTree}
      nav={{
        title: (
          <div className="flex items-center gap-2">
            <Icons.logo className="h-5 w-5" />
            <span className="font-semibold">Attestix</span>
          </div>
        ),
        url: "/",
      }}
      sidebar={{
        defaultOpenLevel: 1,
        collapsible: true,
      }}
      links={[
        {
          type: "icon",
          text: "GitHub",
          url: "https://github.com/VibeTensor/attestix",
          icon: <Icons.github className="h-4 w-4" />,
          label: "GitHub",
          external: true,
        },
      ]}
    >
      {children}
    </DocsLayout>
  );
}
