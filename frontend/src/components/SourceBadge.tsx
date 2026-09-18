import { SourceType } from "@/types/evidence";
import { SOURCE_TYPE_LABEL } from "@/lib/status";


export function SourceBadge({ type }: { type: SourceType }) {
  return (
    <span className="inline-block rounded-sm border border-hairline px-1.5 py-0.5 font-mono text-[11px] uppercase tracking-wide text-ink-muted">
      {SOURCE_TYPE_LABEL[type]}
    </span>
  );
}
