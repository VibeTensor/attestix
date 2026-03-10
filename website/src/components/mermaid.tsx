"use client";

import { useEffect, useRef, useState } from "react";

let mermaidInitialized = false;

export function Mermaid({ chart }: { chart: string }) {
	const ref = useRef<HTMLDivElement>(null);
	const [svg, setSvg] = useState<string>("");

	useEffect(() => {
		let cancelled = false;

		async function render() {
			const mermaid = (await import("mermaid")).default;

			if (!mermaidInitialized) {
				mermaid.initialize({
					startOnLoad: false,
					theme: "dark",
					themeVariables: {
						/* Global text and background */
						background: "#1e1b4b",
						mainBkg: "#312e81",
						textColor: "#e2e8f0",
						fontSize: "14px",

						/* Primary palette */
						primaryColor: "#4f46e5",
						primaryTextColor: "#fff",
						primaryBorderColor: "#6366f1",
						lineColor: "#94a3b8",
						secondaryColor: "#1e1b4b",
						secondaryTextColor: "#e2e8f0",
						tertiaryColor: "#1e293b",
						tertiaryTextColor: "#e2e8f0",

						/* Notes */
						noteBkgColor: "#1e293b",
						noteTextColor: "#e2e8f0",
						noteBorderColor: "#475569",

						/* Sequence diagram actors and signals */
						actorBkg: "#4f46e5",
						actorTextColor: "#fff",
						actorBorder: "#818cf8",
						actorLineColor: "#94a3b8",
						signalColor: "#e2e8f0",
						signalTextColor: "#e2e8f0",

						/* Labels and loops */
						labelBoxBkgColor: "#1e293b",
						labelBoxBorderColor: "#475569",
						labelTextColor: "#e2e8f0",
						loopTextColor: "#e2e8f0",

						/* Activation bars */
						activationBorderColor: "#6366f1",
						activationBkgColor: "#312e81",
						sequenceNumberColor: "#fff",

						/* Flowchart nodes */
						nodeBorder: "#6366f1",
						clusterBkg: "#1e1b4b",
						clusterBorder: "#475569",
						titleColor: "#e2e8f0",
						edgeLabelBackground: "#1e293b",
					},
					fontFamily: "var(--font-geist-sans), system-ui, sans-serif",
					fontSize: 14,
					flowchart: { curve: "basis", padding: 16 },
					sequence: { mirrorActors: false, bottomMarginAdj: 2 },
				});
				mermaidInitialized = true;
			}

			const id = `mermaid-${Math.random().toString(36).slice(2, 9)}`;
			try {
				const { svg: rendered } = await mermaid.render(id, chart);
				if (!cancelled) setSvg(rendered);
			} catch {
				if (!cancelled) setSvg("");
			}
		}

		render();
		return () => { cancelled = true; };
	}, [chart]);

	if (!svg) {
		return (
			<div className="my-6 flex items-center justify-center rounded-lg border border-border bg-muted/50 p-8 text-sm text-muted-foreground">
				Loading diagram...
			</div>
		);
	}

	return (
		<div
			ref={ref}
			data-mermaid=""
			className="my-6 flex justify-center overflow-x-auto rounded-lg border border-border bg-fd-card p-4 [&_svg]:max-w-full"
			dangerouslySetInnerHTML={{ __html: svg }}
		/>
	);
}
