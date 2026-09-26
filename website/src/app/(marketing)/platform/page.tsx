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

// The long-form story that used to be the homepage, in its original order.
export default function PlatformPage() {
  return (
    <>
      <section className="mx-auto grid max-w-[1320px] items-center gap-14 px-7 pb-16 pt-16 lg:grid-cols-[1.1fr_1fr]">
        <div>
          <h1 className="text-[clamp(34px,4.6vw,52px)] font-normal leading-[1.09] tracking-[-0.03em] text-atx-ink">
            The <span className="text-atx-accent">Attestix</span> platform
          </h1>
          <p className="mt-5 max-w-[540px] text-[17.5px] leading-[1.6] text-atx-ink-mid">
            Nine modules and forty-seven MCP tools for agent identity,
            credentials, delegation, compliance records, provenance, and
            reputation, with evidence anyone can verify offline.
          </p>
        </div>
        <HeroCert />
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
