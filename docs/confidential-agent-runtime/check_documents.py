"""Validate replacement document links and complete historical obligation coverage.

Run with Python from any directory. This check does not execute the agent,
validate the formal specification skill schema, or qualify runtime behavior.
"""

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


def table_ids(path, prefix):
    """Read defined identifiers from the first column of a Markdown table."""
    return set(re.findall(r"^\| (" + prefix + r") \|", path.read_text(), re.M))


def heading_ids(text):
    """Return ordinary GitHub Markdown heading anchors, including duplicates."""
    anchors = set()
    seen = {}
    for title in re.findall(r"^#{1,6}\s+(.+)$", text, re.M):
        slug = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
        count = seen.get(slug, 0)
        anchors.add(slug if not count else f"{slug}-{count}")
        seen[slug] = count + 1
    return anchors


def validate(root):
    """Return errors and coverage after checking this package against retained sources."""
    package = root / "docs/confidential-agent-runtime"
    legacy = root / "python/claude_agent_sdk/docs/skill-recovery"
    candidate = legacy / "proposals/distributed-recovery/2026-10-08/candidate/spec.md"
    errors = []
    data = json.loads((package / "obligation-map.json").read_text())
    expected = {
        "tickets": set(),
        "assumptions": table_ids(legacy / "spec.md", r"A-\d+"),
        "candidate_assumptions": table_ids(candidate, r"A-\d+"),
        "candidate_decisions": table_ids(candidate, r"BD-\d+"),
        "invariants": set(re.findall(r"^### (INV-\d+)\b", candidate.read_text(), re.M)),
        "qualification_cases": table_ids(
            legacy / "proposals/distributed-recovery/2026-10-08/context-mode-integration-edit-plan.md",
            r"Q-\d+",
        ),
        "trust_requirements": {f"R{i}" for i in range(1, 9)},
        "engine_requirements": {f"E{i}" for i in range(1, 12)},
        "roadmap": {f"R{i:02d}" for i in range(1, 11)},
    }
    for path in (legacy / "tickets").glob("*.md"):
        expected["tickets"].update(
            re.findall(r"^### (DSR-(?:ROOT|P\d+|\d+\.\d+))\b", path.read_text(), re.M)
        )
    owners = table_ids(package / "spec.md", r"(?:CR|AC)-\d+")
    owners.update(table_ids(package / "decisions.md", r"BD-\d+"))
    dispositions = set(data["dispositions"])
    for family, required in expected.items():
        rows = data["families"][family]
        actual = {row["id"] for row in rows}
        if len(actual) != len(rows) or actual != required:
            errors.append(f"{family}: duplicate, missing or extra identifiers")
        if data["coverage"][family] != len(required):
            errors.append(f"{family}: declared coverage differs from source inventory")
        for row in rows:
            if row["disposition"] not in dispositions or not row["owners"]:
                errors.append(f"{family}/{row['id']}: invalid disposition or missing owner")
            if not set(row["owners"]).issubset(owners):
                errors.append(f"{family}/{row['id']}: unresolved replacement owner")
            if not (root / row["source"]).is_file():
                errors.append(f"{family}/{row['id']}: missing retained source")
            elif family == "tickets":
                text = (root / row["source"]).read_text()
                match = re.search(
                    r"^### " + re.escape(row["id"]) + r"\b.*?(?=^### DSR-|\Z)",
                    text,
                    re.M | re.S,
                )
                block = match.group() if match else ""
                status = re.search(r"^Status: (.+)$", block, re.M)
                digest = hashlib.sha256(block.encode()).hexdigest()
                count = len(re.findall(r"^- \[[ xX]\]", block, re.M))
                if digest != row["source_block_sha256"]:
                    errors.append(f"{row['id']}: historical ticket block changed")
                if status is None or status.group(1) != row["historical_status"]:
                    errors.append(f"{row['id']}: historical status differs")
                if count != row["criteria_count"]:
                    errors.append(f"{row['id']}: historical criteria count differs")
    for source in data["sources"]:
        path = root / source["path"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != source.get("current_sha256", source["sha256"]):
            errors.append(f"source digest differs: {source['path']}")

    documents = [*package.rglob("*.md"), root / "README.md", legacy / "ARCHIVED.md"]
    for path in documents:
        text = path.read_text()
        if path.is_relative_to(package) and any(chr(c) in text for c in (8211, 8212)):
            errors.append(f"prohibited dash: {path.relative_to(root)}")
        for target in re.findall(r"\]\(([^)]+)\)", text):
            url = urlsplit(target)
            if url.scheme or url.netloc:
                continue
            destination = (path.parent / unquote(url.path)).resolve() if url.path else path
            if not destination.is_relative_to(root) or not destination.exists():
                errors.append(f"invalid local link in {path.relative_to(root)}: {target}")
            elif url.fragment and destination.suffix == ".md":
                if unquote(url.fragment) not in heading_ids(destination.read_text()):
                    errors.append(f"missing heading in {path.relative_to(root)}: {target}")
    return errors, {family: len(ids) for family, ids in expected.items()}


def main():
    """Print a bounded machine readable result and fail on document or coverage drift."""
    root = Path(__file__).resolve().parents[2]
    try:
        errors, coverage = validate(root)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "FAIL", "errors": [str(error)]}))
        return 1
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "coverage": coverage, "errors": errors}))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
