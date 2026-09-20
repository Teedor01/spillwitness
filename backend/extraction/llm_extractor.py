from __future__ import annotations

import json
import os

DEFAULT_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")

EXTRACTION_SYSTEM_PROMPT = """You extract factual claims from source text for an evidence \
reconciliation system. You do not judge, corroborate, or assess anything.

Return a JSON object with a single key "claims", an array. Each item must have exactly these keys:
- field: one of OCCURRENCE, LOCATION, DATE, CAUSE, VOLUME
- raw_value: the claim, in the source's own words or a faithful paraphrase
- source_name: who is making this claim
- source_type: one of OFFICIAL, FEDERAL_REGULATOR, STATE_GOVERNMENT, OPERATOR, COMMUNITY, NEWS, RESEARCH, SATELLITE_CONTEXT
- excerpt: the exact supporting text from the source, verbatim
- source_url, event_date, publication_date: include only if the text states them, else omit

Never include a status, confidence, corroboration, or reconciliation judgment of any kind. \
That is not your job and any such key will cause your entire output to be rejected. \
Extract only what the text explicitly states. Do not infer facts the text does not contain. \
If the text supports no clear claim, return {"claims": []}."""


class LLMUnavailableError(RuntimeError):
    pass


def extract_with_groq(source_text: str, model: str = DEFAULT_MODEL) -> list[dict]:
    """The real, live extraction path. Requires GROQ_API_KEY."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise LLMUnavailableError(
            "GROQ_API_KEY is not set. This is the real API path; it is not mocked. "
            "Set the key or use extract_offline() with a pre-recorded fixture instead."
        )

    from groq import Groq  

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": source_text},
        ],
    )
    parsed = json.loads(response.choices[0].message.content)
    return parsed.get("claims", [])


def extract_offline(fixture_path: str) -> list[dict]:
    """Loads a pre-recorded extraction result from disk instead of calling
    a model. Used only when no live key is available, or for
    reproducible testing. The fixture must have been produced by an
    actual model run (or, when disclosed as such, written directly by
    the developer performing the same task a model would)... this
    function does not pretend the fixture is a live call. Accepts
    either a bare JSON array or the {"claims": [...]} wrapper shape the
    live path now returns."""
    with open(fixture_path) as f:
        data = json.load(f)
    if isinstance(data, dict):
        return data.get("claims", [])
    return data

