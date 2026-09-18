import { CasePayload, Claim, ClaimField, Source } from "@/types/evidence";
import { FIELD_LABEL } from "@/lib/status";
import { StatusLabel } from "./StatusLabel";

export function ReconciliationPanel({
  field,
  assessment,
  claims,
  sources,
  selectedClaimId,
  onSelectClaim,
}: {
  field: ClaimField;
  assessment: CasePayload["fields"][ClaimField];
  claims: Claim[];
  sources: Source[];
  selectedClaimId: string | null;
  onSelectClaim: (claimId: string) => void;
}) {
  const sourceById = new Map(sources.map((s) => [s.id, s]));
  const claimById = new Map(claims.map((c) => [c.id, c]));

  return (
    <section aria-label={`What the evidence supports: ${FIELD_LABEL[field]}`} className="border-t border-hairline pt-6">
      <div className="flex items-center gap-3">
        <h2 className="text-sm font-medium text-ink-muted">What the evidence supports</h2>
      </div>

      <div className="mt-3 flex items-center gap-3">
        <span className="text-lg text-ink">{FIELD_LABEL[field]}</span>
        <StatusLabel status={assessment.status} />
      </div>

      {assessment.narrative && <p className="mt-2 max-w-2xl text-sm text-ink">{assessment.narrative}</p>}
      {!assessment.narrative && assessment.note && (
        <p className="mt-2 max-w-2xl text-sm text-ink-muted">{assessment.note}</p>
      )}

      {assessment.groups.length > 0 && (
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
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
    </section>
  );
}

