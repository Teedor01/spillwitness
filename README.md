# SpillWitness

### Same incident. Different records. What can we actually establish?

SpillWitness turns conflicting environmental reports into an auditable evidence record.

It is not an AI oil-spill detector, and it does not decide who is right. Given multiple sources describing the same environmental incident, including official investigations, government statements, operator reports, and news coverage, SpillWitness reconciles their claims deterministically and shows where the records agree, where they conflict, and what remains unestablished. Every claim is traceable back to its original source.

Built for **NextStep Hacks 2026: Earth Forward**.

## The Problem

Environmental incidents in the Niger Delta rarely come with a single, trusted account. A federal regulator's investigation might attribute an incident to sabotage. A state government's technical committee might reject that finding and attribute it to equipment failure. A governor might cite a volume estimate hundreds of times larger than what the same regulator's Director-General reported.

All of this is reflected in the case demonstrated by this project.

The problem is not simply a lack of information. It is that multiple records can describe the same incident differently.

When those disagreements are collapsed into a single answer, important information is lost.

SpillWitness preserves the disagreement and makes it auditable.

## What SpillWitness Does

Given a documented environmental incident, SpillWitness:

* **Reconciles claims deterministically.** No model decides whether two sources agree, corroborate, or contradict each other. Fixed, testable, auditable logic does.

* **Distinguishes independent evidence from derivative reporting.** A second news article restating an official finding through a quoted participant is not automatically treated as a second independent source. SpillWitness traces the underlying attribution and represents the relationship explicitly.

* **Preserves conflicting values.** When sources report substantially different spill volumes, SpillWitness does not average them into a new number. It preserves the competing claims alongside their sources, dates, and evidence.

* **Traces every claim to its origin.** The evidence chain is `Source → Evidence → Claim → Normalized Value → Reconciliation Status`. Claims can be opened directly in the application to inspect their provenance.

* **Separates AI extraction from AI judgment.** The extraction pipeline allows a model to propose claims from source material, but it has no path to assign a status, confidence score, or conclusion. A strict schema validator rejects prohibited decision fields. A human must approve the extracted claim before it enters the evidence set, after which the deterministic reconciliation engine evaluates it.

## The Demonstration Case

The included case is the November 2021 Santa Barbara Well 1 blowout in Nembe, Bayelsa State.

The dataset contains six verified public source records:

* Aiteo's initial incident report
* NOSDRA/NUPRC's Joint Investigation Visit finding, which attributed the incident to sabotage
* Bayelsa State's Technical Committee rejection of that finding, which attributed the incident to equipment/maintenance failure
* Statements from Bayelsa's Governor and NOSDRA's Director-General concerning the volume of oil involved
* A news report whose attribution was traced back to the same JIV already represented in the dataset

The final source is retained as evidence, but is not counted as independent corroboration because its relevant claim derives from the same underlying investigation.

The resulting field statuses are:

| Field    | Status         |
| -------- | -------------- |
| Incident | `CORROBORATED` |
| Location | `CORROBORATED` |
| Date     | `CORROBORATED` |
| Cause    | `CONTESTED`    |
| Volume   | `CONFLICTING`  |

Every excerpt and URL encoded in `backend/data/santa_barbara.py` was checked against the corresponding original source before being encoded.

## Architecture

```text
SOURCE → EVIDENCE → CLAIM → RECONCILIATION → FIELD STATUS
```

### Backend

**Python**

A dependency-light reconciliation engine that:

* normalizes claims including dates, locations, causes, and volumes
* compares normalized claims
* derives field statuses
* produces machine-readable reason codes
* preserves source and claim provenance

The core reconciliation engine performs no network calls at runtime.

### Frontend

**Next.js 14 / TypeScript / Tailwind CSS**

The frontend is a renderer. It performs no reconciliation of its own.

It reads the backend's generated export and presents the result as an investigation console containing:

* case findings
* evidence graph
* evidence timeline
* source records
* claim details
* provenance

### Extraction Pipeline

**LLM extracts → schema validates → human verifies → deterministic reconciliation decides**

The controlled extraction pipeline allows an LLM to extract candidate claims from source material.

The schema validator enforces the structure of the model output and rejects prohibited fields such as:

* `status`
* `confidence`
* `corroborated`
* `contested`
* `conflicting`
* `reconciliation`
* `independent`
* `verified`
* `reliability`
* `reason`
* `score`

Approved claims are converted into the same `Claim` objects used by the existing reconciliation engine.

The model therefore contributes to extraction, not adjudication.

See `backend/extraction/`.

## Project Structure

```text
backend/
├── models/
│   └── Core data types: Source, Claim, FieldStatus, assessments
├── reconciliation/
│   └── normalize.py, compare.py, status.py
├── data/
│   └── Verified Santa Barbara dataset
├── extraction/
│   └── Controlled LLM extraction pipeline
├── tests/
│   └── 44 tests covering reconciliation, export integrity, and extraction
└── export_demo.py
    └── Serializes the engine's output for the frontend

frontend/
├── src/app/
│   └── Next.js App Router entry point
├── src/components/
│   └── CaseHeader, EvidenceFindings, EvidenceGraph,
│       EvidenceTimeline, ClaimDetail, etc.
├── src/lib/
│   └── Status/label mappings, timeline and graph layout
│       (presentation only, no reconciliation decisions)
└── src/data/
    └── Generated backend export

BUILD_LOG.md
└── Phase-by-phase engineering record, decisions, bugs,
    tests, and deferred work
```

## Running It

### Backend

```bash
cd backend

pip install -r requirements.txt

python -m pytest tests/ -v

python demo_print.py

python export_demo.py
```

### Frontend

```bash
cd frontend

npm install

npm run dev
```

The frontend runs at:

```text
http://localhost:3000
```

### Controlled Extraction

```bash
cd backend

python -m extraction.cli extract \
  --source-id aiteo-statement \
  --offline extraction/fixtures/aiteo_thecable_2022-02-16.json

python -m extraction.cli list --all

python -m extraction.cli approve <id> \
  --note "verified against source"
```

The extraction pipeline also supports the live Anthropic API path. Set `ANTHROPIC_API_KEY` in the environment before making a live model call.

See `backend/extraction/llm_extractor.py`.

## What This Project Is Honest About

* **Location claims are corroborated at the community level.** For example, sources can support `Nembe, Bayelsa State` while describing different specific features, such as a wellhead or river. The UI preserves each source's wording rather than merging those descriptions into a single physical location.

* **Geographic mapping was investigated and explicitly deferred.** The current dataset does not contain enough source-verified coordinates to justify adding geographic precision. See `BUILD_LOG.md`.

* **The live LLM API path was implemented but was not exercised with a real API key during development.** The offline fixture path was tested end to end, including malformed input designed to verify that the validator rejects prohibited decision fields.

* **One approved demonstration claim in `backend/extraction/pending_claims.json` was self-approved during development** to prove the pipeline works end to end. It is explicitly flagged in the code and `BUILD_LOG.md` as requiring independent human review before being treated as final evidence.

## Tech Stack

* Python
* pytest
* Next.js 14
* TypeScript
* Tailwind CSS
* Anthropic API for the controlled extraction pipeline

The core reconciliation engine remains deterministic and does not depend on an LLM to determine field status.

---

## Core Principle

**The model extracts. The human verifies. The deterministic engine reconciles.**

SpillWitness does not tell you what to believe.

It shows you what the available evidence can actually establish.
