import { constructMetadata } from "@/lib/utils";
import { DemoGrid } from "./demo-grid";

export const metadata = constructMetadata({
  title: "Interactive Demos",
  description:
    "Experience Attestix capabilities hands-on. Try our EU AI Act compliance checker, fine calculator, identity explorer, and reputation dashboard.",
});

export default function DemoIndexPage() {
  return (
    <div className="mt-24 mb-16">
      <div className="text-center py-16 px-4">
        <h1 className="text-3xl font-bold text-foreground sm:text-4xl">
          Interactive Demos
        </h1>
        <p className="mt-4 text-xl text-muted-foreground max-w-2xl mx-auto">
          Experience Attestix capabilities hands-on. No installation required.
        </p>
      </div>
      <DemoGrid />
    </div>
  );
}
