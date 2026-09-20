"use client";

import { useMemo, useState } from "react";
import caseData from "@/data/case-santa-barbara.json";
import { CasePayload } from "@/types/evidence";
import { CaseHeader } from "@/components/CaseHeader";
import { EvidenceFindings } from "@/components/EvidenceFindings";
import { EvidenceGraph } from "@/components/EvidenceGraph";
import { EvidenceTimeline } from "@/components/EvidenceTimeline";
import { ClaimDetail } from "@/components/ClaimDetail";
import { SourcesStrip } from "@/components/SourcesStrip";

const payload = caseData as unknown as CasePayload;

export default function Page() {
  const [selectedClaimId, setSelectedClaimId] = useState<string | null>(null);

  const claimById = useMemo(() => new Map(payload.claims.map((c) => [c.id, c])), []);
  const sourceById = useMemo(() => new Map(payload.sources.map((s) => [s.id, s])), []);

  const selectedClaim = selectedClaimId ? claimById.get(selectedClaimId) ?? null : null;
  const selectedSource = selectedClaim ? sourceById.get(selectedClaim.source_id) ?? null : null;
  const selectedClaimFieldStatus = selectedClaim ? payload.fields[selectedClaim.field].status : null;
  const selectedClaimFieldReason = selectedClaim ? payload.fields[selectedClaim.field].reason : null;


  const supportingSourceCount = useMemo(() => {
    if (!selectedClaim) return null;
    const assessment = payload.fields[selectedClaim.field];
    const group = assessment.groups.find((g) => g.claim_ids.includes(selectedClaim.id));
    return group ? group.independent_source_ids.length : null;
  }, [selectedClaim]);

  return (
    <main className="mx-auto max-w-3xl px-6 py-10">
      <CaseHeader
        title={payload.incident.title}
        locationLabel={payload.incident.location_label}
        periodLabel={payload.incident.period_label}
        sourceCount={payload.sources.length}
        fieldCount={Object.keys(payload.fields).length}
      />

      <div className="mt-8">
        <EvidenceFindings
          fields={payload.fields}
          claims={payload.claims}
          sources={payload.sources}
          selectedClaimId={selectedClaimId}
          onSelectClaim={setSelectedClaimId}
        />
      </div>

      <div className="mt-10">
        <EvidenceGraph
          payload={payload}
          incidentTitle={payload.incident.title}
          selectedClaimId={selectedClaimId}
          onSelectClaim={setSelectedClaimId}
        />
      </div>

      <div className="mt-10">
        <EvidenceTimeline
          claims={payload.claims}
          sources={payload.sources}
          selectedClaimId={selectedClaimId}
          onSelectClaim={setSelectedClaimId}
        />
      </div>

      <div className="mt-10">
        <SourcesStrip sources={payload.sources} />
      </div>

      <p className="mt-10 border-t border-hairline pt-4 font-mono text-xs text-ink-muted">
        {payload.label}
      </p>

      <ClaimDetail
        claim={selectedClaim}
        source={selectedSource}
        fieldStatus={selectedClaimFieldStatus}
        fieldReason={selectedClaimFieldReason}
        supportingSourceCount={supportingSourceCount}
        onClose={() => setSelectedClaimId(null)}
      />
    </main>
  );
}
