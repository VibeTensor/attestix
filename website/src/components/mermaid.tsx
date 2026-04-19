"use client";

import { useEffect, useRef, useState } from "react";

let mermaidInitialized = false;

// Palette mirrors the v2 atx token set so Mermaid diagrams read as part of
// the Attestix design, not a foreign indigo overlay. Colours are resolved
// at module load from CSS custom properties when available; otherwise the
// literals below are the same oklch values expressed as hex fallbacks.
const PALETTE = {
	bg: "#1e2426",            // --atx-bg-sunken
	panel: "#2a3236",         // --atx-panel
	panelHi: "#33393d",       // --atx-panel-hi
	line: "#454c50",          // --atx-line
	lineSoft: "#373d41",      // --atx-line-soft
	ink: "#f0ebde",           // --atx-ink
	inkMid: "#c4b9a5",        // --atx-ink-mid
	inkDim: "#8b8170",        // --atx-ink-dim
	accent: "#c49455",        // --atx-accent (gold)
	accentDeep: "#a67a41",    // --atx-accent-deep
};

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
					theme: "base",
					themeVariables: {
						background: PALETTE.bg,
						mainBkg: PALETTE.panel,
						textColor: PALETTE.ink,
						fontSize: "14px",

						primaryColor: PALETTE.accent,
						primaryTextColor: PALETTE.bg,
						primaryBorderColor: PALETTE.accentDeep,
						lineColor: PALETTE.inkDim,
						secondaryColor: PALETTE.panelHi,
						secondaryTextColor: PALETTE.ink,
						tertiaryColor: PALETTE.panel,
						tertiaryTextColor: PALETTE.ink,

						noteBkgColor: PALETTE.panelHi,
						noteTextColor: PALETTE.ink,
						noteBorderColor: PALETTE.line,

						actorBkg: PALETTE.panel,
						actorTextColor: PALETTE.ink,
						actorBorder: PALETTE.accent,
						actorLineColor: PALETTE.inkDim,
						signalColor: PALETTE.inkMid,
						signalTextColor: PALETTE.ink,

						labelBoxBkgColor: PALETTE.panelHi,
						labelBoxBorderColor: PALETTE.line,
						labelTextColor: PALETTE.ink,
						loopTextColor: PALETTE.ink,

						activationBorderColor: PALETTE.accent,
						activationBkgColor: PALETTE.panel,
						sequenceNumberColor: PALETTE.bg,

						nodeBorder: PALETTE.accent,
						clusterBkg: PALETTE.bg,
						clusterBorder: PALETTE.line,
						titleColor: PALETTE.ink,
						edgeLabelBackground: PALETTE.panel,
					},
					fontFamily:
						"var(--font-sans), var(--font-geist-sans), system-ui, sans-serif",
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
		return () => {
			cancelled = true;
		};
	}, [chart]);

	if (!svg) {
		return (
			<div className="my-6 flex items-center justify-center rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken p-8 text-sm text-atx-ink-dim">
				Loading diagram...
			</div>
		);
	}

	return (
		<div
			ref={ref}
			data-mermaid=""
			className="my-6 flex justify-center overflow-x-auto rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken p-4 [&_svg]:max-w-full"
			dangerouslySetInnerHTML={{ __html: svg }}
		/>
	);
}
