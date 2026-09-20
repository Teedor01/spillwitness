from __future__ import annotations

import argparse
import sys

from extraction import llm_extractor, pending
from data.santa_barbara import INCIDENT_ID, SOURCES

VALID_SOURCE_IDS = {s.id for s in SOURCES}


def cmd_extract(args):
    if args.source_id not in VALID_SOURCE_IDS:
        print(f"error: unknown source_id {args.source_id!r}. Known: {sorted(VALID_SOURCE_IDS)}")
        sys.exit(1)

    if args.offline:
        items = llm_extractor.extract_offline(args.offline)
        print(f"(offline fixture: {args.offline}, not a live model call)")
    else:
        text = open(args.text_file).read() if args.text_file else sys.stdin.read()
        try:
            items = llm_extractor.extract_with_groq(text)
        except llm_extractor.LLMUnavailableError as e:
            print(f"error: {e}")
            sys.exit(1)

    accepted, rejected = pending.submit_for_review(items, INCIDENT_ID, args.source_id)
    print(f"{len(accepted)} item(s) passed schema validation and are now PENDING review.")
    for p in accepted:
        print(f"  [{p.id}] {p.data['field']}: {p.data['raw_value']!r}")
    if rejected:
        print(f"{len(rejected)} item(s) FAILED schema validation and were not queued:")
        for r in rejected:
            print(f"  {r}")


def cmd_list(args):
    items = pending.list_pending(status=None if args.all else "PENDING")
    if not items:
        print("(none)")
    for i in items:
        print(f"[{i['id']}] {i['status']:9} {i['data']['field']:11} {i['data']['raw_value']!r} "
              f"(source: {i['source_id']})")


def cmd_approve(args):
    item = pending.approve(args.id, reviewer_note=args.note)
    print(f"APPROVED [{item['id']}] {item['data']['field']}: {item['data']['raw_value']!r}")


def cmd_reject(args):
    item = pending.reject(args.id, reviewer_note=args.note)
    print(f"REJECTED [{item['id']}]: {args.note}")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(required=True)

    p_extract = sub.add_parser("extract")
    p_extract.add_argument("--source-id", required=True)
    p_extract.add_argument("--text-file")
    p_extract.add_argument("--offline", help="path to a pre-recorded extraction JSON fixture")
    p_extract.set_defaults(func=cmd_extract)

    p_list = sub.add_parser("list")
    p_list.add_argument("--all", action="store_true")
    p_list.set_defaults(func=cmd_list)

    p_approve = sub.add_parser("approve")
    p_approve.add_argument("id")
    p_approve.add_argument("--note", default="")
    p_approve.set_defaults(func=cmd_approve)

    p_reject = sub.add_parser("reject")
    p_reject.add_argument("id")
    p_reject.add_argument("--note", required=True)
    p_reject.set_defaults(func=cmd_reject)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
