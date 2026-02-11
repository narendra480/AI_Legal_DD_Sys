# risk_aggregator.py

# --------------------------------------------
# Flag rules (simple keyword-based mapping)
# --------------------------------------------
FLAG_RULES = {
    "Hidden liabilities": [
        "penalty", "indemnity", "liquidated damages"
    ],
    "Pending litigation": [
        "litigation", "dispute", "arbitration", "lawsuit"
    ],
    "IP risk": [
        "intellectual property", "ip ownership", "license"
    ],
    "Ownership contradictions": [
        "shareholding", "ownership", "control", "assignment"
    ]
}


def derive_flags(risks: list) -> list:
    """
    Derives document-level flags from detected risks.
    Does NOT affect risk counts or severity.
    """
    flags = set()

    for r in risks:
        if not isinstance(r, dict):
            continue

        risk_type = (r.get("risk_type") or "").lower()
        snippet = (r.get("snippet") or "").lower()

        combined_text = f"{risk_type} {snippet}"

        for flag, keywords in FLAG_RULES.items():
            for kw in keywords:
                if kw in combined_text:
                    flags.add(flag)

    return list(flags)


def aggregate_risks(document_risks: dict, documents: dict) -> dict:
    """
    Aggregates detected risks into:
    - Per-document DD summary
    - Clause-level heat map

    ⚠ Schema-safe: only ADDs `flags`
    """

    documents_summary = {}
    heat_map = []

    for doc_id, risks in document_risks.items():
        doc_meta = documents.get(doc_id)
        if not doc_meta:
            continue

        doc_name = doc_meta["doc_name"]
        doc_type = doc_meta["doc_type"]

        # Initialize summary (UNCHANGED KEYS)
        documents_summary[doc_name] = {
            "doc_type": doc_type,
            "overall_risk": "No Risk",
            "risk_counts": {
                "High": 0,
                "Medium": 0,
                "Low": 0
            },
            "total_risks": 0,
            "flags": []   # ✅ NEW (optional, FE-safe)
        }

        # If no risks detected
        if not risks:
            continue

        for r in risks:
            if not isinstance(r, dict):
                continue

            severity = r.get("severity", "Low")
            if severity not in ["High", "Medium", "Low"]:
                severity = "Low"

            documents_summary[doc_name]["risk_counts"][severity] += 1
            documents_summary[doc_name]["total_risks"] += 1

            # Heat map entry (UNCHANGED)
            heat_map.append({
                "document": doc_name,
                "doc_type": doc_type,
                "page": r.get("page"),
                "severity": severity,
                "risk_type": r.get("risk_type"),
                "snippet": r.get("snippet")
            })

        # Determine overall risk (UNCHANGED)
        if documents_summary[doc_name]["risk_counts"]["High"] > 0:
            documents_summary[doc_name]["overall_risk"] = "High"
        elif documents_summary[doc_name]["risk_counts"]["Medium"] > 0:
            documents_summary[doc_name]["overall_risk"] = "Medium"
        elif documents_summary[doc_name]["risk_counts"]["Low"] > 0:
            documents_summary[doc_name]["overall_risk"] = "Low"

        # ✅ Derive flags AFTER processing all risks
        documents_summary[doc_name]["flags"] = derive_flags(risks)
        
        # --- Acquisition Risk Index calculation --
        high = documents_summary[doc_name]["risk_counts"]["High"]
        medium = documents_summary[doc_name]["risk_counts"]["Medium"]
        low = documents_summary[doc_name]["risk_counts"]["Low"]
        documents_summary[doc_name]["acquisition_risk_index"] = (
        high * 3 + medium * 2 + low * 1
)


    return {
        "documents": documents_summary,
        "heat_map": heat_map
    }
