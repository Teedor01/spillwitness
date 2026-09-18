import { Claim, ClaimField, Source } from "@/types/evidence";
import { causeDisplayLabel } from "./status";

export interface TimelineEvent {
  key: string;
  date: string;
  field: ClaimField;
  title: string;
  description: string;
  sourceCount: number;
  claimIds: string[];
}

function groupKeyFor(claim: Claim, date: string): string {

  if (claim.field === "OCCURRENCE" || claim.field === "DATE") {
    return `${date}::OCCURRENCE_EVENT`;
  }

  return `${date}::${claim.field}::${claim.normalized_value ?? claim.id}`;
}

function titleFor(field: ClaimField, normalizedValue: string | null, volumeIndex: number): string {
  if (field === "OCCURRENCE") return "Wellhead incident reported";
  if (field === "CAUSE") return `Cause: ${causeDisplayLabel(normalizedValue ?? "unknown")}`;
  if (field === "VOLUME") return volumeIndex === 0 ? "Volume claim reported" : "Additional volume record";
  if (field === "LOCATION") return "Location identified";
  return "Evidence recorded";
}


export function buildTimelineEvents(claims: Claim[], sources: Source[]): TimelineEvent[] {
  const sourceById = new Map(sources.map((s) => [s.id, s]));
  const buckets = new Map<string, { date: string; field: ClaimField; claims: Claim[] }>();

  for (const claim of claims) {
    const date = claim.publication_date ?? claim.event_date;
    if (!date) continue;
    if (!sourceById.has(claim.source_id)) continue;
    const key = groupKeyFor(claim, date);
    const field: ClaimField = claim.field === "DATE" ? "OCCURRENCE" : claim.field;
    const bucket = buckets.get(key) ?? { date, field, claims: [] as Claim[] };
    bucket.claims.push(claim);
    buckets.set(key, bucket);
  }

  const events: TimelineEvent[] = Array.from(buckets.entries()).map(([key, bucket]) => {
    const primary = bucket.claims.find((c) => c.excerpt) ?? bucket.claims[0];
    const distinctSources = new Set(bucket.claims.map((c) => c.source_id));
    return {
      key,
      date: bucket.date,
      field: bucket.field,
      title: "", 
      description: primary.excerpt ?? primary.raw_value,
      sourceCount: distinctSources.size,
      claimIds: bucket.claims.map((c) => c.id),
    };
  });

  events.sort((a, b) => a.date.localeCompare(b.date));

  let volumeCount = 0;
  for (const event of events) {
    const groupClaims = event.claimIds
      .map((id) => claims.find((c) => c.id === id))
      .filter((c): c is Claim => !!c);
    const normalizedValue = groupClaims.find((c) => c.normalized_value)?.normalized_value ?? null;
    if (event.field === "VOLUME") {
      event.title = titleFor(event.field, normalizedValue, volumeCount);
      volumeCount += 1;
    } else {
      event.title = titleFor(event.field, normalizedValue, 0);
    }
  }

  return events;
}
