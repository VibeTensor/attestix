"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";

interface FeatureOption {
  id: number;
  title: string;
  description: string;
  code: string;
}

interface FeatureSelectorProps {
  features: FeatureOption[];
}

function FilenameHeader({ filename }: { filename: string }) {
  return (
    <div className="flex items-center gap-2 px-4 py-2.5 bg-[#161b22] border-b border-[#30363d]">
      <div className="flex items-center gap-1.5">
        <span className="h-3 w-3 rounded-full bg-[#ff5f57]" />
        <span className="h-3 w-3 rounded-full bg-[#febc2e]" />
        <span className="h-3 w-3 rounded-full bg-[#28c840]" />
      </div>
      <span className="ml-2 text-xs font-mono text-[#8b949e]">{filename}</span>
    </div>
  );
}

export const FeatureSelector: React.FC<FeatureSelectorProps> = ({
  features,
}) => {
  const [selectedIndex, setSelectedIndex] = useState<number>(0);

  return (
    <div className="rounded-xl overflow-hidden border border-border bg-background">
      <div className="grid grid-cols-1 md:grid-cols-[minmax(260px,2fr)_3fr]">
        {/* Tab buttons */}
        <div className="border-b md:border-b-0 md:border-r border-border bg-background">
          {/* Mobile: horizontal scrollable pills */}
          <div className="flex md:hidden overflow-x-auto gap-2 p-3" role="tablist" aria-label="Code examples">
            {features.map((option, index) => (
              <button
                key={option.id}
                onClick={() => setSelectedIndex(index)}
                role="tab"
                aria-selected={selectedIndex === index}
                aria-controls="code-panel"
                className={cn(
                  "flex-shrink-0 px-3 py-1.5 rounded-full text-sm font-medium transition-colors",
                  selectedIndex === index
                    ? "bg-primary text-primary-foreground"
                    : "bg-secondary/50 text-muted-foreground hover:bg-secondary"
                )}
              >
                {option.title}
              </button>
            ))}
          </div>
          {/* Desktop: left-accent tab list */}
          <div className="hidden md:flex md:flex-col p-3 gap-1" role="tablist" aria-label="Code examples">
            {features.map((option, index) => (
              <button
                key={option.id}
                onClick={() => setSelectedIndex(index)}
                role="tab"
                aria-selected={selectedIndex === index}
                aria-controls="code-panel"
                className={cn(
                  "w-full text-left px-4 py-3 transition-colors",
                  selectedIndex === index
                    ? "border-l-2 border-l-primary bg-secondary/30 rounded-r-lg"
                    : "border-l-2 border-l-transparent hover:bg-secondary/10 rounded-r-lg"
                )}
              >
                <h3 className="font-medium tracking-tight text-sm">{option.title}</h3>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {option.description}
                </p>
              </button>
            ))}
          </div>
        </div>
        {/* Code panel */}
        <div className="bg-[#0d1117] flex flex-col" role="tabpanel" id="code-panel" aria-label={features[selectedIndex].title}>
          <FilenameHeader filename="example.py" />
          <div
            className="font-mono text-sm flex-1 [&>pre]:p-5 [&>pre]:m-0 [&>pre]:rounded-none [&>pre]:border-0 [&>pre]:bg-[#0d1117] [&>pre]:h-full [&>pre]:min-h-[460px] [&_code]:whitespace-pre overflow-x-auto"
            dangerouslySetInnerHTML={{ __html: features[selectedIndex].code }}
          />
        </div>
      </div>
    </div>
  );
};
