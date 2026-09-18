import { CasePayload, ClaimField } from "@/types/evidence";
import { FIELD_LABEL } from "@/lib/status";
import { StatusLabel } from "./StatusLabel";

const FIELD_ORDER: ClaimField[] = ["OCCURRENCE", "LOCATION", "DATE", "CAUSE", "VOLUME"];

export function CaseStatus({
  fields,
  activeField,
  onSelectField,
}: {
  fields: CasePayload["fields"];
  activeField: ClaimField | null;
  onSelectField: (field: ClaimField) => void;
}) {
  return (
    <section aria-label="Case status">
      <h2 className="mb-3 text-sm font-medium text-ink-muted">Case status</h2>
      <ul className="divide-y divide-hairline border-y border-hairline">
        {FIELD_ORDER.map((field) => {
          const assessment = fields[field];
          const isActive = field === activeField;
          return (
            <li key={field}>
              <button
                onClick={() => onSelectField(field)}
                className={`flex w-full items-center justify-between py-3 text-left transition-colors ${
                  isActive ? "bg-surface" : ""
                }`}
              >
                <span className="text-sm text-ink">{FIELD_LABEL[field]}</span>
                <StatusLabel status={assessment.status} size="sm" />
              </button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
