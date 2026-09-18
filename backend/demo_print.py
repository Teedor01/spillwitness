from data.santa_barbara import CLAIMS, INCIDENT_ID, CURATED_LABEL, SOURCES
from reconciliation.status import derive_incident_status


def main() -> None:
    print(f"Data label: {CURATED_LABEL}\n")
    result = derive_incident_status(INCIDENT_ID, CLAIMS)

    for field, assessment in result.fields.items():
        print(f"{field.value:>10}: {assessment.status.value}")
        if assessment.note:
            print(f"{'':>10}  {assessment.note}")
        for group in assessment.groups:
            sources = ", ".join(sorted(group.source_ids))
            print(f"{'':>10}  - '{group.display_value}' <- [{sources}]")
        print()

    print("SUMMARY:")
    print(result.summary)


if __name__ == "__main__":
    main()
