"use client";

import React, { useState } from "react";

interface FeatureOption {
  id: number;
  title: string;
  description: string;
  code: string;
}

interface FeatureSelectorProps {
  features: FeatureOption[];
}

export const FeatureSelector: React.FC<FeatureSelectorProps> = ({
  features,
}) => {
  const [selectedIndex, setSelectedIndex] = useState<number>(0);

  return (
    <div className="grid grid-cols-1 md:grid-cols-5 relative">
      <div className="md:col-span-2 border-b md:border-b-0 bg-background md:border-r border-border sticky lg:relative top-[var(--header-height)] lg:top-0">
        <div className="flex md:flex-col feature-btn-container overflow-x-auto p-4 pb-2" role="tablist" aria-label="Code examples">
          {features.map((option, index) => (
            <button
              key={option.id}
              onClick={() => setSelectedIndex(index)}
              role="tab"
              aria-selected={selectedIndex === index}
              aria-controls="code-panel"
              className={`flex-shrink-0 w-64 md:w-full text-left p-4 mb-2 mr-2 last:mr-0 md:mr-0 rounded border border-border ${
                selectedIndex === index ? "bg-accent/70" : "hover:bg-muted/50"
              }`}
            >
              <h3 className="font-medium tracking-tight">{option.title}</h3>
              <p className="text-sm text-muted-foreground">
                {option.description}
              </p>
            </button>
          ))}
        </div>
      </div>
      <div className="col-span-1 md:col-span-3 bg-[#0d1117]" role="tabpanel" id="code-panel" aria-label={features[selectedIndex].title}>
        <div
          className="font-mono text-sm [&>pre]:p-5 [&>pre]:m-0 [&>pre]:rounded-none [&>pre]:border-0 [&>pre]:bg-[#0d1117] [&_code]:break-all overflow-auto"
          style={{ minHeight: "300px" }}
          dangerouslySetInnerHTML={{ __html: features[selectedIndex].code }}
        />
      </div>
    </div>
  );
};
