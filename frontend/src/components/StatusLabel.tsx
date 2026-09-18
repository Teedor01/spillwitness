import { FieldStatus } from "@/types/evidence";
import { STATUS_META } from "@/lib/status";

export function StatusLabel({ status, size = "md" }: { status: FieldStatus; size?: "sm" | "md" }) {
  const meta = STATUS_META[status];
  const padding = size === "sm" ? "px-2 py-0.5 text-xs" : "px-2.5 py-1 text-sm";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-sm font-mono uppercase tracking-wide ${padding} ${meta.bg} ${meta.text}`}
    >
      {meta.label}
    </span>
  );
}
