import { FieldStatus, SourceType } from "@/types/evidence";


export const STATUS_META: Record<
  FieldStatus,
  { label: string; text: string; bg: string; border: string; description: string }
> = {
  CORROBORATED: {
    label: "Corroborated",
    text: "text-status-corroborated",
    bg: "bg-status-corroborated-bg",
    border: "border-status-corroborated",
    description: "Independent sources agree.",
  },
  SUPPORTED: {
    label: "Supported",
    text: "text-status-corroborated",
    bg: "bg-status-corroborated-bg",
    border: "border-status-corroborated",
    description: "Independent sources agree.",
  },
  CONTESTED: {
    label: "Contested",
    text: "text-status-contested",
    bg: "bg-status-contested-bg",
    border: "border-status-contested",
    description: "Credible sources offer incompatible accounts.",
  },
  CONFLICTING: {
    label: "Conflicting",
    text: "text-status-conflicting",
    bg: "bg-status-conflicting-bg",
    border: "border-status-conflicting",
    description: "Sources report incompatible figures.",
  },
  UNRESOLVED: {
    label: "Unresolved",
    text: "text-status-unresolved",
    bg: "bg-status-unresolved-bg",
    border: "border-status-unresolved",
    description: "Only one source makes this claim.",
  },
  NOT_ESTABLISHED: {
    label: "Not established",
    text: "text-status-none",
    bg: "bg-status-none-bg",
    border: "border-status-none",
    description: "No source establishes this.",
  },
  NOT_ENOUGH_EVIDENCE: {
    label: "Not enough evidence",
    text: "text-status-none",
    bg: "bg-status-none-bg",
    border: "border-status-none",
    description: "No source makes a claim on this field.",
  },
};

export const SOURCE_TYPE_LABEL: Record<SourceType, string> = {
  OFFICIAL: "Official",
  FEDERAL_REGULATOR: "Federal regulator",
  STATE_GOVERNMENT: "State government",
  OPERATOR: "Operator",
  COMMUNITY: "Community",
  NEWS: "News",
  RESEARCH: "Research",
  SATELLITE_CONTEXT: "Satellite / context",
};

export const FIELD_LABEL: Record<string, string> = {
  OCCURRENCE: "Incident",
  LOCATION: "Location",
  DATE: "Date",
  CAUSE: "Cause",
  VOLUME: "Volume",
};


export function causeDisplayLabel(normalizedValue: string): string {
  if (normalizedValue === "SABOTAGE") return "Sabotage";
  if (normalizedValue === "EQUIPMENT_FAILURE") return "Equipment / maintenance failure";
  if (normalizedValue.startsWith("UNMAPPED:")) {
    const text = normalizedValue.slice("UNMAPPED:".length);
    return text.charAt(0).toUpperCase() + text.slice(1);
  }
  return normalizedValue;
}
