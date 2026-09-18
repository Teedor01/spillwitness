from __future__ import annotations

from datetime import date

from models.evidence import Claim, ClaimField, Source, SourceType

CURATED_LABEL = "Curated public-source evidence"
INCIDENT_ID = "nembe-santa-barbara-2021-11"

SOURCES = [
    Source(
        id="aiteo-statement",
        name="Aiteo Eastern Exploration and Production Company",
        type=SourceType.OPERATOR,
        url="https://punchng.com/aiteo-reports-oil-spill-in-bayelsa-wellhead/",
    ),
    Source(
        id="nosdra-nuprc-jiv",
        name="NOSDRA / NUPRC Joint Investigation Visit finding",
        type=SourceType.FEDERAL_REGULATOR,
        url="https://www.energyvoice.com/oilandgas/africa/376314/bayelsa-nosdra-aiteo-sabotage/",
    ),
    Source(
        id="bayelsa-technical-committee",
        name="Bayelsa State Government Technical Committee (AG Biriyai Dambo)",
        type=SourceType.STATE_GOVERNMENT,
        url="https://www.vanguardngr.com/2021/12/why-we-rejected-nembe-spill-jiv-report-bayelsa-govt/",
    ),
    Source(
        id="bayelsa-governor",
        name="Bayelsa State Governor Douye Diri",
        type=SourceType.STATE_GOVERNMENT,
        url="https://guardian.ng/news/joint-investigative-visit-will-unravel-cause-volume-of-aiteos-spilled-crude-nosdra/",
    ),
    Source(
        id="nosdra-dg",
        name="NOSDRA Director-General Idris Musa",
        type=SourceType.FEDERAL_REGULATOR,
        url="https://guardian.ng/news/joint-investigative-visit-will-unravel-cause-volume-of-aiteos-spilled-crude-nosdra/",
    ),
    Source(
        id="thecable-jiv-member",
        name="TheCable, citing JIV member Victor Ekpenyong (Kenyon International)",
        type=SourceType.NEWS,
        url="https://www.thecable.ng/the-untold-story-of-the-aiteo-santa-barbara-oil-spill/",
    ),
]

CLAIMS = [
    Claim(
        id="c-occ-1", incident_id=INCIDENT_ID, field=ClaimField.OCCURRENCE,
        raw_value="A wellhead blowout occurred at Santa Barbara Well 1.",
        source_id="aiteo-statement", event_date=date(2021, 11, 5),
        excerpt="Aiteo reported a major leakage from OML 29 on November 5, 2021.",
    ),
    Claim(
        id="c-occ-2", incident_id=INCIDENT_ID, field=ClaimField.OCCURRENCE,
        raw_value="A wellhead blowout occurred at Santa Barbara Well 1.",
        source_id="nosdra-nuprc-jiv", event_date=date(2021, 11, 5),
        excerpt="JIV convened by NOSDRA, NUPRC, Aiteo and Bayelsa representatives confirms an incident occurred.",
    ),
    Claim(
        id="c-occ-3", incident_id=INCIDENT_ID, field=ClaimField.OCCURRENCE,
        raw_value="A wellhead blowout occurred at Santa Barbara Well 1.",
        source_id="bayelsa-technical-committee", event_date=date(2021, 11, 5),
        excerpt="Bayelsa's own technical committee statement confirms the incident occurred; the dispute is about cause, not occurrence.",
    ),

    Claim(
        id="c-loc-1", incident_id=INCIDENT_ID, field=ClaimField.LOCATION,
        raw_value="Santa Barbara Well 1, Nembe, Bayelsa State",
        source_id="aiteo-statement",
        excerpt="Santa Barbara South field, Nembe Local Government Area, OML 29.",
    ),
    Claim(
        id="c-loc-2", incident_id=INCIDENT_ID, field=ClaimField.LOCATION,
        raw_value="Santa Barbra River, Nembe, Bayelsa State",
        source_id="bayelsa-governor",
        excerpt="Governor Diri: crude polluted the Santa Barbra River and Nembe Creeks (note: source spelling).",
    ),

    Claim(
        id="c-date-1", incident_id=INCIDENT_ID, field=ClaimField.DATE,
        raw_value="2021-11-05",
        source_id="aiteo-statement", event_date=date(2021, 11, 5),
    ),
    Claim(
        id="c-date-2", incident_id=INCIDENT_ID, field=ClaimField.DATE,
        raw_value="2021-11-05",
        source_id="nosdra-dg", event_date=date(2021, 11, 5),
        excerpt="NOSDRA/NAN reporting: leak began Nov. 5.",
    ),

    Claim(
        id="c-cause-1", incident_id=INCIDENT_ID, field=ClaimField.CAUSE,
        raw_value="sabotage", source_id="nosdra-nuprc-jiv",
        publication_date=date(2021, 12, 22),
        excerpt="NOSDRA and NUPRC representatives attributed the spill to sabotage following the Dec 22 JIV.",
    ),
    Claim(
        id="c-cause-2", incident_id=INCIDENT_ID, field=ClaimField.CAUSE,
        raw_value="act of sabotage, external interference", source_id="thecable-jiv-member",
        publication_date=date(2022, 2, 16),
        excerpt="JIV member (Kenyon International CEO): engineering analysis found the spill would not have happened without external interference.",
    ),
    Claim(
        id="c-cause-3", incident_id=INCIDENT_ID, field=ClaimField.CAUSE,
        raw_value="equipment and maintenance failure", source_id="bayelsa-technical-committee",
        publication_date=date(2021, 12, 27),
        excerpt="Bayelsa's Technical Committee (AG Biriyai Dambo) rejected the JIV report, citing equipment/maintenance failure and noting the wellhead equipment had been removed and replaced before inspection.",
    ),


    Claim(
        id="c-vol-1", incident_id=INCIDENT_ID, field=ClaimField.VOLUME,
        raw_value="about two million barrels", source_id="bayelsa-governor",
        publication_date=date(2021, 12, 1),
        excerpt="Governor Diri, visiting the site 25 days after the leak, claimed roughly two million barrels had polluted the river and creeks.",
    ),
    Claim(
        id="c-vol-2", incident_id=INCIDENT_ID, field=ClaimField.VOLUME,
        raw_value="4,150 barrels of oil and water residue recovered", source_id="nosdra-dg",
        publication_date=date(2021, 12, 3),
        excerpt="NOSDRA DG Idris Musa called the two-million-barrel claim 'guess work' and cited 4,150 barrels of oil/water residue recovered so far; noted only a completed JIV could determine total volume.",
    ),
]
