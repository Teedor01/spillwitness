export function CaseHeader({
  title,
  locationLabel,
  periodLabel,
  sourceCount,
  fieldCount,
}: {
  title: string;
  locationLabel: string;
  periodLabel: string;
  sourceCount: number;
  fieldCount: number;
}) {
  return (
    <header className="border-b border-hairline pb-6">
      <div className="flex items-baseline justify-between">
        <span className="font-mono text-xs uppercase tracking-wide text-ink-muted">SpillWitness</span>
        <span className="font-mono text-xs text-ink-muted">Case 1 of 1 &middot; demo dataset</span>
      </div>

      <h1 className="mt-4 max-w-xl text-2xl leading-snug text-ink sm:text-3xl">
        Same incident. Different records.
        <br />
        <span className="text-ink-muted">What can we actually establish?</span>
      </h1>

      <div className="mt-5 border-l-2 border-mark pl-4">
        <div className="text-lg font-medium text-ink">{title}</div>
        <div className="font-mono text-sm text-ink-muted">
          {locationLabel} &middot; {periodLabel}
        </div>
        <div className="mt-1 font-mono text-xs text-ink-muted">
          {sourceCount} source records &middot; {fieldCount} evidence fields
        </div>
      </div>
    </header>
  );
}
