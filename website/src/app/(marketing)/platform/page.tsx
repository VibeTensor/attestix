import { HeroCert } from "@/components/sections/v2/hero-cert";
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
import { constructMetadata } from "@/lib/utils";

export const metadata = constructMetadata({
  title: "Platform",
  description:
    "The full Attestix platform: nine modules, the seven-step compliance workflow, framework integrations, benchmarks, and the EU AI Act compliance matrix.",
});

// Section bands alternate bg-atx-bg / bg-atx-bg-elev, starting with bg-atx-bg
// after the standards strip; each section sets its own band.
export default function PlatformPage() {
  return (
    <>
      <section className="px-6 pb-16 pt-16 text-center md:pt-20">
        <div className="mx-auto max-w-[860px]">
          <p className="text-[14px] font-medium text-atx-accent">Platform</p>
          <h1 className="mt-3 text-[clamp(34px,5vw,52px)] font-normal leading-[1.09] tracking-[-0.03em] text-atx-ink [text-wrap:balance]">
            The <span className="text-atx-accent">Attestix</span> platform
          </h1>
          <p className="mx-auto mt-5 max-w-[640px] text-[17.5px] leading-[1.6] text-atx-ink-mid [text-wrap:balance]">
            Nine modules and forty-seven MCP tools for agent identity,
            credentials, delegation, compliance records, provenance, and
            reputation, with evidence anyone can verify offline.
          </p>
        </div>
        <div className="mx-auto mt-12 max-w-[560px] text-left">
          <HeroCert />
        </div>
      </section>
      <StandardsStrip />
      <ProblemSection />
      <ModulesSection />
      <WorkflowSection />
      <ConsolePreviewSection />
      <ValidationSection />
      <FrameworksSection />
      <UseCasesSection />
      <BenchmarksSection />
      <ComplianceMatrixSection />
      <CtaV2 />
    </>
  );
}
