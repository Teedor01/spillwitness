"use client";

import { useState } from "react";
import { Claim, Source } from "@/types/evidence";
import { buildTimelineEvents } from "@/lib/timeline";
import { SourceBadge } from "./SourceBadge";

function formatDate(iso: string): string {
  const d = new Date(iso + "T00:00:00Z");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric", timeZone: "UTC" });
}

export function EvidenceTimeline({
  claims,
  sources,
  selectedClaimId,
  onSelectClaim,
}: {
  claims: Claim[];
  sources: Source[];
  selectedClaimId: string | null;
  onSelectClaim: (claimId: string) => void;
}) {
  const events = buildTimelineEvents(claims, sources);
  const [expandedKey, setExpandedKey] = useState<string | null>(null);
  const claimById = new Map(claims.map((c) => [c.id, c]));
  const sourceById = new Map(sources.map((s) => [s.id, s]));

  return (
    <section aria-label="Evidence timeline" className="border-t border-hairline pt-6">
      <h2 className="mb-4 text-sm font-medium text-ink-muted">Evidence timeline</h2>
      <ol className="space-y-5">
        {events.map((event) => {
          const isExpanded = expandedKey === event.key;
          return (
            <li key={event.key} className="flex gap-4">
              <div className="w-20 shrink-0 pt-0.5 font-mono text-xs text-ink-muted">
                {formatDate(event.date)}
              </div>
              <div className="flex-1 border-l border-hairline pl-4">
                <div className="text-sm font-medium text-ink">{event.title}</div>
                <p className="mt-1 max-w-lg text-sm text-ink-muted">{event.description}</p>
                <div className="mt-2 flex items-center gap-3">
                  <span className="font-mono text-xs text-ink-muted">
                    {event.sourceCount} supporting source{event.sourceCount === 1 ? "" : "s"}
                  </span>
                  <button
                    onClick={() => setExpandedKey(isExpanded ? null : event.key)}
                    className="font-mono text-xs text-mark underline underline-offset-2"
                  >
                    {isExpanded ? "Hide evidence" : "View evidence"}
                  </button>
                </div>

                {isExpanded && (
                  <ul className="mt-2 space-y-1.5 border-l border-hairline pl-3">
                    {event.claimIds.map((claimId) => {
                      const claim = claimById.get(claimId);
                      const source = claim ? sourceById.get(claim.source_id) : undefined;
                      if (!claim || !source) return null;
                      return (
                        <li key={claimId}>
                          <button
                            onClick={() => onSelectClaim(claimId)}
                            className={`flex w-full items-center gap-2 rounded-sm px-1.5 py-1 text-left text-xs transition-colors ${
                              claimId === selectedClaimId ? "bg-surface ring-1 ring-mark" : "hover:bg-surface"
                            }`}
                          >
                            <span className="text-ink">{source.name}</span>
                            <SourceBadge type={source.type} />
                          </button>
                        </li>
                      );
                    })}
                  </ul>
                )}
              </div>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
