"use client";

import { useState } from "react";
import { CasePayload, Claim, ClaimField, Source } from "@/types/evidence";
import { FIELD_LABEL, STATUS_META } from "@/lib/status";
import { StatusLabel } from "./StatusLabel";

const FIELD_ORDER: ClaimField[] = ["OCCURRENCE", "LOCATION", "DATE", "CAUSE", "VOLUME"];


const EMPHASIZED_STATUSES = new Set(["CONTESTED", "CONFLICTING"]);

export function EvidenceFindings({
  fields,
  claims,
  sources,
  selectedClaimId,
  onSelectClaim,
}: {
  fields: CasePayload["fields"];
  claims: Claim[];
  sources: Source[];
  selectedClaimId: string | null;
  onSelectClaim: (claimId: string) => void;
}) {
  const [expanded, setExpanded] = useState<Set<ClaimField>>(
    () => new Set(FIELD_ORDER.filter((f) => EMPHASIZED_STATUSES.has(fields[f].status)))
  );
  const claimById = new Map(claims.map((c) => [c.id, c]));
  const sourceById = new Map(sources.map((s) => [s.id, s]));

  function toggle(field: ClaimField) {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(field)) next.delete(field);
      else next.add(field);
      return next;
    });
  }

  return (
    <section aria-label="Evidence findings">
      <h2 className="mb-3 text-sm font-medium text-ink-muted">Evidence findings</h2>
      <div className="divide-y divide-hairline border-y border-hairline">
        {FIELD_ORDER.map((field) => {
          const assessment = fields[field];
          const meta = STATUS_META[assessment.status];
          const isEmphasized = EMPHASIZED_STATUSES.has(assessment.status);
          const isExpanded = expanded.has(field);
          const summaryLine = assessment.narrative || assessment.note;

          return (
            <div
              key={field}
              className={`border-l-[3px] ${isEmphasized ? meta.border : "border-l-transparent"}`}
            >
              <button
                onClick={() => toggle(field)}
                className="flex w-full items-start justify-between gap-4 py-3 pl-3 pr-1 text-left"
              >
                <div className="min-w-0">
                  <div className="flex items-center gap-3">
                    <span className={`text-sm ${isEmphasized ? "font-medium text-ink" : "text-ink"}`}>
                      {FIELD_LABEL[field]}
                    </span>
                    <StatusLabel status={assessment.status} size="sm" />
                  </div>
                  {summaryLine && (
                    <p className={`mt-1 max-w-xl text-xs ${isEmphasized ? "text-ink" : "text-ink-muted"}`}>
                      {summaryLine}
                    </p>
                  )}
                </div>
                <span className="shrink-0 pt-0.5 font-mono text-xs text-ink-muted">
                  {isExpanded ? "Hide" : "Details"}
                </span>
              </button>

              {isExpanded && assessment.groups.length > 0 && (
                <div className="grid gap-3 pb-4 pl-3 pr-1 sm:grid-cols-2">
                  {assessment.groups.map((group) => (
                    <div key={group.normalized_value} className="border-l-2 border-hairline pl-3">
                      <div className="text-sm text-ink">{group.display_value}</div>
                      <div className="mt-1 flex flex-wrap gap-2">
                        {group.claim_ids.map((claimId) => {
                          const claim = claimById.get(claimId);
                          const source = claim ? sourceById.get(claim.source_id) : undefined;
                          return (
                            <button
                              key={claimId}
                              onClick={() => onSelectClaim(claimId)}
                              className={`font-mono text-xs underline decoration-hairline underline-offset-2 hover:decoration-ink ${
                                claimId === selectedClaimId ? "text-mark" : "text-ink-muted"
                              }`}
                            >
                              {source?.name ?? "source"}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}
