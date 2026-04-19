export function ComingSoonPane({ name }: { name: string }) {
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center gap-3 px-5 py-16 text-center">
      <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-dim">
        &sect; module
      </div>
      <div className="font-serif text-[32px] leading-none text-atx-ink">
        {name}
      </div>
      <p className="max-w-[420px] text-[13.5px] leading-[1.6] text-atx-ink-mid">
        This surface is part of the live Attestix stack. The interactive
        preview covers Agents, Compliance, Credentials, Audit trail and
        Anchors. {name} lights up in the full install via{" "}
        <code className="rounded-atx-xs border border-atx-line-soft bg-atx-bg-sunken px-1.5 py-0.5 font-mono-atx text-[12px] text-atx-accent">
          pip install attestix
        </code>
        .
      </p>
    </div>
  );
}
