import { Claim, FieldStatus, Source } from "@/types/evidence";
import { FIELD_LABEL, REASON_LABEL, SOURCE_TYPE_LABEL } from "@/lib/status";
import { StatusLabel } from "./StatusLabel";

export function ClaimDetail({
  claim,
  source,
  fieldStatus,
  fieldReason,
  supportingSourceCount,
  onClose,
}: {
  claim: Claim | null;
  source: Source | null;
  fieldStatus: FieldStatus | null;
  fieldReason: string | null;
  supportingSourceCount: number | null;
  onClose: () => void;
}) {
  if (!claim || !source) return null;

  return (
    <aside
      role="dialog"
      aria-label="Evidence record"
      className="fixed inset-y-0 right-0 z-10 w-full max-w-sm overflow-y-auto border-l border-hairline bg-surface p-6 shadow-[-4px_0_12px_rgba(0,0,0,0.04)]"
    >
      <div className="flex items-start justify-between">
        <span className="font-mono text-xs uppercase tracking-wide text-ink-muted">Evidence record</span>
        <button onClick={onClose} aria-label="Close" className="text-ink-muted hover:text-ink">
          Close
        </button>
      </div>

      <dl className="mt-4 space-y-4 text-sm">
        <div>
          <dt className="text-xs text-ink-muted">Field</dt>
          <dd className="text-ink">{FIELD_LABEL[claim.field]}</dd>
        </div>

        <div>
          <dt className="text-xs text-ink-muted">Normalized claim</dt>
          <dd className="text-ink">{claim.raw_value}</dd>
          {claim.derived_from_label && (
            <dd className="mt-1 text-xs text-ink-muted">
              Derived from: <span className="text-ink">{claim.derived_from_label}</span> — not counted as
              independent corroboration for this field.
            </dd>
          )}
        </div>

        <div>
          <dt className="text-xs text-ink-muted">Source</dt>
          <dd className="text-ink">{source.name}</dd>
          {source.attributed_to && (
            <dd className="mt-1 text-xs text-ink-muted">
              Attributed to: <span className="text-ink">{source.attributed_to}</span>
            </dd>
          )}
        </div>

        <div>
          <dt className="text-xs text-ink-muted">Source type</dt>
          <dd className="font-mono text-xs text-ink-muted">{SOURCE_TYPE_LABEL[source.type]}</dd>
        </div>

        {claim.publication_date && (
          <div>
            <dt className="text-xs text-ink-muted">Publication date</dt>
            <dd className="font-mono text-ink">{claim.publication_date}</dd>
          </div>
        )}

        {claim.event_date && (
          <div>
            <dt className="text-xs text-ink-muted">Event date</dt>
            <dd className="font-mono text-ink">{claim.event_date}</dd>
          </div>
        )}

        {claim.excerpt && (
          <div>
            <dt className="text-xs text-ink-muted">Source evidence</dt>
            <dd className="mt-1 border-l-2 border-hairline pl-3 text-ink-muted">{claim.excerpt}</dd>
          </div>
        )}

        {source.url && (
          <div>
            <dt className="text-xs text-ink-muted">Source URL</dt>
            <dd>
              <a
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="break-all text-mark underline underline-offset-2"
              >
                {source.url}
              </a>
              <span className="ml-1 text-xs text-ink-muted">(opens in a new tab)</span>
            </dd>
          </div>
        )}

        {claim.normalized_value && (
          <div>
            <dt className="text-xs text-ink-muted">Reconciliation key</dt>
            <dd className="font-mono text-xs text-ink-muted">{claim.normalized_value}</dd>
          </div>
        )}

        {fieldStatus && (
          <div>
            <dt className="text-xs text-ink-muted">Field status</dt>
            <dd className="mt-1">
              <StatusLabel status={fieldStatus} size="sm" />
            </dd>
            {fieldReason && (
              <dd className="mt-1 text-xs text-ink-muted">{REASON_LABEL[fieldReason] ?? fieldReason}</dd>
            )}
          </div>
        )}

        {supportingSourceCount !== null && (
          <div>
            <dt className="text-xs text-ink-muted">Independent support</dt>
            <dd className="text-ink">
              {supportingSourceCount} independent source{supportingSourceCount === 1 ? "" : "s"}
            </dd>
          </div>
        )}
      </dl>
    </aside>
  );
}
