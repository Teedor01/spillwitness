"use client";

import { CasePayload } from "@/types/evidence";
import { buildGraphLayout } from "@/lib/graph";
import { STATUS_META } from "@/lib/status";
import { StatusLabel } from "./StatusLabel";

const LEAF_LABEL_WIDTH = 260;

export function EvidenceGraph({
  payload,
  incidentTitle,
  selectedClaimId,
  onSelectClaim,
}: {
  payload: CasePayload;
  incidentTitle: string;
  selectedClaimId: string | null;
  onSelectClaim: (claimId: string) => void;
}) {
  const layout = buildGraphLayout(payload, incidentTitle);
  const width = layout.columnX.leaf + LEAF_LABEL_WIDTH;
  const height = layout.totalHeight;

  return (
    <section aria-label="Evidence graph" className="border-t border-hairline pt-6">
      <h2 className="mb-1 text-sm font-medium text-ink-muted">Evidence graph</h2>
      <p className="mb-4 max-w-xl text-xs text-ink-muted">
        The same reconciliation result as above, laid out spatially: where records converge into one
        path and where they branch into incompatible ones.
      </p>

      <div className="overflow-x-auto">
        <div className="relative" style={{ width, height, minWidth: width }}>
          <svg
            width={width}
            height={height}
            className="absolute inset-0"
            aria-hidden="true"
          >
            {layout.fields.map((f) => (
              <line
                key={`root-${f.field}`}
                x1={layout.columnX.root + 6}
                y1={layout.rootY}
                x2={layout.columnX.field}
                y2={f.y}
                stroke="#DEDCD3"
                strokeWidth={1}
              />
            ))}
            {layout.fields.flatMap((f) =>
              f.groups.map((g) => (
                <line
                  key={`${f.field}-${g.key}`}
                  x1={layout.columnX.field + 6}
                  y1={f.y}
                  x2={layout.columnX.group}
                  y2={g.y}
                  stroke="#DEDCD3"
                  strokeWidth={1}
                />
              ))
            )}
            {layout.fields.flatMap((f) =>
              f.groups.flatMap((g) =>
                g.leaves.map((leaf) => (
                  <line
                    key={leaf.claimId}
                    x1={layout.columnX.group + 6}
                    y1={g.y}
                    x2={layout.columnX.leaf}
                    y2={leaf.y}
                    stroke={leaf.isDerived ? "#DEDCD3" : "#B9B6AA"}
                    strokeWidth={1}
                    strokeDasharray={leaf.isDerived ? "3,3" : undefined}
                  />
                ))
              )
            )}
          </svg>

          {/* Root node */}
          <div
            className="absolute -translate-y-1/2 pr-2 text-sm font-medium text-ink"
            style={{ left: layout.columnX.root, top: layout.rootY, width: layout.columnX.field - layout.columnX.root - 12 }}
          >
            {layout.rootLabel}
          </div>

          {/* Field nodes */}
          {layout.fields.map((f) => {
            const meta = STATUS_META[f.status];
            return (
              <div
                key={f.field}
                className="absolute -translate-y-1/2"
                style={{ left: layout.columnX.field, top: f.y, width: layout.columnX.group - layout.columnX.field - 12 }}
              >
                <div className="text-xs font-medium text-ink">{f.label}</div>
                <StatusLabel status={f.status} size="sm" />
              </div>
            );
          })}

          {/* Group nodes */}
          {layout.fields.flatMap((f) =>
            f.groups.map((g) => (
              <div
                key={`${f.field}-group-${g.key}`}
                className="absolute -translate-y-1/2 text-xs text-ink-muted"
                style={{ left: layout.columnX.group, top: g.y, width: layout.columnX.leaf - layout.columnX.group - 12 }}
              >
                <div className="text-ink">{g.label}</div>
                {g.totalCount > g.independentCount && (
                  <div className="font-mono text-[11px]">
                    {g.independentCount} independent / {g.totalCount} total
                  </div>
                )}
              </div>
            ))
          )}

          {/* Leaf (claim/source) nodes */}
          {layout.fields.flatMap((f) =>
            f.groups.flatMap((g) =>
              g.leaves.map((leaf) => (
                <button
                  key={leaf.claimId}
                  onClick={() => onSelectClaim(leaf.claimId)}
                  className={`absolute -translate-y-1/2 flex items-center gap-1.5 text-left text-xs transition-colors ${
                    leaf.claimId === selectedClaimId ? "text-mark" : "text-ink-muted hover:text-ink"
                  }`}
                  style={{ left: layout.columnX.leaf, top: leaf.y, width: LEAF_LABEL_WIDTH }}
                >
                  <span className="truncate">{leaf.sourceName}</span>
                  {leaf.isDerived && (
                    <span className="shrink-0 rounded-sm border border-hairline px-1 font-mono text-[10px] uppercase tracking-wide">
                      derivative
                    </span>
                  )}
                </button>
              ))
            )
          )}
        </div>
      </div>
    </section>
  );
}
