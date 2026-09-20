import { CasePayload, ClaimField, FieldStatus } from "@/types/evidence";
import { FIELD_LABEL } from "./status";

export interface GraphLeaf {
  claimId: string;
  sourceName: string;
  isDerived: boolean;
  y: number;
}

export interface GraphGroup {
  key: string;
  label: string;
  independentCount: number;
  totalCount: number;
  leaves: GraphLeaf[];
  y: number;
}

export interface GraphFieldNode {
  field: ClaimField;
  label: string;
  status: FieldStatus;
  groups: GraphGroup[];
  y: number;
}

export interface GraphLayout {
  rootLabel: string;
  rootY: number;
  fields: GraphFieldNode[];
  rowHeight: number;
  totalHeight: number;
  columnX: { root: number; field: number; group: number; leaf: number };
}

const FIELD_ORDER: ClaimField[] = ["OCCURRENCE", "LOCATION", "DATE", "CAUSE", "VOLUME"];
const ROW_HEIGHT = 32;
const GROUP_GAP = 10;
const FIELD_GAP = 20;

export function buildGraphLayout(payload: CasePayload, incidentTitle: string): GraphLayout {
  const claimById = new Map(payload.claims.map((c) => [c.id, c]));
  const sourceById = new Map(payload.sources.map((s) => [s.id, s]));

  let cursorY = ROW_HEIGHT / 2;
  const fields: GraphFieldNode[] = [];

  for (const field of FIELD_ORDER) {
    const assessment = payload.fields[field];
    const groups: GraphGroup[] = [];
    const fieldStartY = cursorY;

    assessment.groups.forEach((group, gi) => {
      if (gi > 0) cursorY += GROUP_GAP;
      const groupStartY = cursorY;

      const leaves: GraphLeaf[] = group.claim_ids.map((claimId) => {
        const claim = claimById.get(claimId);
        const source = claim ? sourceById.get(claim.source_id) : undefined;
        const y = cursorY;
        cursorY += ROW_HEIGHT;
        return {
          claimId,
          sourceName: source?.name ?? "unknown source",
          isDerived: !!claim?.derived_from_claim_id,
          y,
        };
      });

      const groupEndY = cursorY - ROW_HEIGHT;
      groups.push({
        key: group.normalized_value,
        label: group.display_value,
        independentCount: group.independent_source_ids.length,
        totalCount: group.source_ids.length,
        leaves,
        y: (groupStartY + groupEndY) / 2,
      });
    });

    const fieldEndY = cursorY - ROW_HEIGHT;
    fields.push({
      field,
      label: FIELD_LABEL[field],
      status: assessment.status,
      groups,
      y: (fieldStartY + fieldEndY) / 2,
    });
    cursorY += FIELD_GAP;
  }

  const totalHeight = cursorY - FIELD_GAP + ROW_HEIGHT / 2;
  const rootY = (fields[0].y + fields[fields.length - 1].y) / 2;

  return {
    rootLabel: incidentTitle,
    rootY,
    fields,
    rowHeight: ROW_HEIGHT,
    totalHeight,
    columnX: { root: 0, field: 190, group: 400, leaf: 630 },
  };
}
