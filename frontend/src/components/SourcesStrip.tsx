import { Source } from "@/types/evidence";
import { SourceBadge } from "./SourceBadge";

export function SourcesStrip({ sources }: { sources: Source[] }) {
  return (
    <section aria-label="Sources" className="border-t border-hairline pt-6">
      <h2 className="mb-3 text-sm font-medium text-ink-muted">Sources</h2>
      <ul className="grid gap-3 sm:grid-cols-2">
        {sources.map((source) => (
          <li key={source.id} className="flex items-start justify-between gap-3 border-l-2 border-hairline pl-3">
            <div>
              <div className="text-sm text-ink">{source.name}</div>
              {source.url && (
                <a
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-mono text-xs text-ink-muted underline underline-offset-2 hover:text-ink"
                >
                  {new URL(source.url).hostname}
                </a>
              )}
            </div>
            <SourceBadge type={source.type} />
          </li>
        ))}
      </ul>
    </section>
  );
}
