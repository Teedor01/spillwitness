export type SourceType =
  | "OFFICIAL"
  | "FEDERAL_REGULATOR"
  | "STATE_GOVERNMENT"
  | "OPERATOR"
  | "COMMUNITY"
  | "NEWS"
  | "RESEARCH"
  | "SATELLITE_CONTEXT";

export type ClaimField = "OCCURRENCE" | "LOCATION" | "DATE" | "CAUSE" | "VOLUME";

export type FieldStatus =
  | "CORROBORATED"
  | "SUPPORTED"
  | "CONTESTED"
  | "CONFLICTING"
  | "UNRESOLVED"
  | "NOT_ESTABLISHED"
  | "NOT_ENOUGH_EVIDENCE";

export interface Source {
  id: string;
  name: string;
  type: SourceType;
  url: string | null;
  attributed_to: string | null;
}

export interface Claim {
  id: string;
  field: ClaimField;
  raw_value: string;
  normalized_value: string | null;
  source_id: string;
  event_date: string | null;
  publication_date: string | null;
  excerpt: string | null;
  derived_from_claim_id: string | null;
  derived_from_label: string | null;
}

export interface ValueGroup {
  normalized_value: string;
  display_value: string;
  claim_ids: string[];
  source_ids: string[];
  independent_source_ids: string[];
}

export interface FieldAssessment {
  status: FieldStatus;
  note: string;
  narrative: string;
  reason: string;
  groups: ValueGroup[];
  contributing_claim_ids: string[];
}

export interface CasePayload {
  label: string;
  incident: {
    id: string;
    title: string;
    location_label: string;
    period_label: string;
  };
  sources: Source[];
  claims: Claim[];
  fields: Record<ClaimField, FieldAssessment>;
  summary: string;
}
