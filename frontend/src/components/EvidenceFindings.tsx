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
                  {assessment.reason && (
                    <p className="mt-0.5 font-mono text-[11px] text-ink-muted">
                      reconciliation: {assessment.reason}
                    </p>
                  )}
                </div>
                <span className="shrink-0 pt-0.5 font-mono text-xs text-ink-muted">
                  {isExpanded ? "Hide" : "Details"}
                </span>
              </button>

              {isExpanded && assessment.groups.length > 0 && (
                <div className="space-y-3 pb-4 pl-3 pr-1">
                  {field === "LOCATION" && (
                    <p className="text-xs text-ink-muted">
                      Community context established:{" "}
                      <span className="font-mono text-ink">{assessment.groups[0].normalized_value}</span>.
                      Specific site wording per source, shown below, is preserved rather than merged.
                    </p>
                  )}
                  {assessment.groups.map((group) => {
                    const independentCount = group.independent_source_ids.length;
                    const totalCount = group.source_ids.length;
                    return (
                      <div key={group.normalized_value}>
                        {totalCount > independentCount && (
                          <p className="mb-1 text-xs text-ink-muted">
                            {independentCount} independent source{independentCount === 1 ? "" : "s"}, {totalCount} record{totalCount === 1 ? "" : "s"} total
                          </p>
                        )}
                        <div className="grid gap-x-6 gap-y-2 sm:grid-cols-2">
                          {group.claim_ids.map((claimId) => {
                            const claim = claimById.get(claimId);
                            const source = claim ? sourceById.get(claim.source_id) : undefined;
                            if (!claim || !source) return null;
                            const isDerived = !!claim.derived_from_claim_id;
                            return (
                              <button
                                key={claimId}
                                onClick={() => onSelectClaim(claimId)}
                                className={`border-l-2 pl-3 text-left transition-colors ${
                                  claimId === selectedClaimId ? "border-mark" : "border-hairline hover:border-ink-muted"
                                }`}
                              >
                                <div className="text-sm text-ink">{claim.raw_value}</div>
                                <div className="mt-0.5 flex items-center gap-2">
                                  <span className="font-mono text-xs text-ink-muted">{source.name}</span>
                                  {isDerived && (
                                    <span className="rounded-sm border border-hairline px-1 font-mono text-[10px] uppercase tracking-wide text-ink-muted">
                                      derivative
                                    </span>
                                  )}
                                </div>
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}
