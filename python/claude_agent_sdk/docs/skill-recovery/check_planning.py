"""Check portable planning consistency without running the recovery implementation.

Run ``python3 check_planning.py`` from any directory, or pass ``--root`` for an
exported skill-recovery directory. The checks compare current document owners,
bounded ticket dispositions and candidate evidence rows. Historical captures and
immutable migration manifests do not define the current planning baseline.
"""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree


def rows(text):
    """Return table rows whose first cell is a stable identifier."""
    result = {}
    for line in text.splitlines():
        if not re.match(r"^\| (?:A-|BD-|EV-)\d+ \|", line):
            continue
        cells = [
            cell.strip().replace(r"\|", "|")
            for cell in re.split(r"(?<!\\)\|", line)[1:-1]
        ]
        if cells[0] in result:
            raise ValueError(f"duplicate table identifier {cells[0]}")
        result[cells[0]] = cells
    return result


def without_fences(text):
    """Remove fenced captures while retaining ordinary Markdown links."""
    output = []
    marker = None
    for line in text.splitlines():
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if match:
            token = match.group(1)
            if marker is None:
                marker = token
            elif token[0] == marker[0] and len(token) >= len(marker):
                marker = None
            continue
        if marker is None:
            output.append(line)
    return "\n".join(output)


def anchors(text):
    """Return GitHub heading anchors and explicitly declared HTML identifiers."""
    result = set(re.findall(r'(?:id|name)=["\']([^"\']+)["\']', text))
    counts = {}
    for line in without_fences(text).splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)(?:\s+#+)?$", line)
        if not match:
            continue
        heading = re.sub(r"<[^>]+>", "", match.group(1)).lower()
        heading = re.sub(r"[^\w\- ]", "", heading).replace(" ", "-")
        count = counts.get(heading, 0)
        counts[heading] = count + 1
        result.add(f"{heading}-{count}" if count else heading)
    return result


def ticket_section(text, identifier):
    """Extract one current ticket, excluding adjacent tickets."""
    match = re.search(
        r"^### " + re.escape(identifier) + r"\s[^\n]*\n(.*?)(?=^### DSR-|\Z)",
        text, re.M | re.S,
    )
    return match.group(1) if match else ""


# Required fields mirror the maintained decision criteria. Evidence records
# document selections rather than executed qualifications.
CLOSURE_FIELDS = {
    "checkpoint": ("substrate", "exact_version", "accepted_pair", "metadata", "publication"),
    "portable_cases": ("surviving_host", "original_disk_unavailable", "live_partition_termination", "finite_rig_holder"),
    "isolation": ("level", "security_holder"),
    "assumptions": ("A-17", "A-27", "A-48", "A-37"),
    "refusal": ("independent_authority", "pair_mismatch", "unproven_death", "local_guard", "restore_permission"),
    "configuration": (
        "deployment_holder", "storage_holder", "integration_holder",
        "authority_administration", "trusted_host_permissions", "runtime_pins",
        "terminal_incarnation", "authentication", "encryption_keys", "reader_matrix",
        "retention", "component_files_api", "dependency_pins", "license_fit",
        "maintenance_holder", "upstream_interface_revision", "workload_bounds",
    ),
}


def closure_errors(root, status, decisions, section):
    """Validate optional confirmed planning records, mandatory only for DONE.

    The record is an auditable approval attestation bound to exact answers and
    local evidence bytes. It does not authenticate a human or run qualification.
    OPEN requires no new artifact; Answered/Superseded rows need approval even while OPEN.
    """
    errors = []

    def require(condition, message):
        if not condition:
            errors.append("DSR-0.6 closure: " + message)

    require(status in {"OPEN", "DONE"}, "status must be OPEN or DONE")
    confirmed = {
        identifier for identifier, cells in decisions.items()
        if cells[-1].split()[0].lower() in {"answered", "superseded"}
    }
    for identifier, cells in decisions.items():
        require(cells[-1].split()[0].lower() in {"open", "answered", "superseded"}, f"{identifier} has an unsupported disposition")
    if status == "OPEN" and not confirmed:
        return errors
    path = root / "proposals/distributed-recovery/2026-10-08/dsr-0.6-closure.json"
    try:
        data = json.loads(
            path.read_text(), object_pairs_hook=unique_json_object,
            parse_constant=reject_json_constant,
        )
        require(data.get("ticket") == "DSR-0.6", "record ticket identity differs")
        answers = data["answers"]
        approval = data["approval"]
        digest = hashlib.sha256(
            json.dumps(answers, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        require(approval.get("answers_sha256") == digest, "approval is not bound to the current answers")
        require(approval.get("status") == "approved", "record is not approved")
        require(
            isinstance(approval.get("by"), str) and concrete(approval["by"])
            and re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(approval.get("date", ""))) is not None,
            "approval holder/date are absent",
        )

        def evidence(record, label):
            references = record.get("evidence", [])
            require(isinstance(references, list) and bool(references), f"{label} lacks evidence")
            if not isinstance(references, list):
                return
            for reference in references:
                parsed = urlsplit(reference["ref"])
                destination = (root / unquote(parsed.path)).resolve()
                local = (
                    bool(parsed.path) and not parsed.scheme and not parsed.netloc
                    and not Path(unquote(parsed.path)).is_absolute()
                    and destination.is_relative_to(root.resolve())
                )
                owners = {
                    "spec.md",
                    "tickets/phase-0.md",
                    "proposals/distributed-recovery/2026-10-08/dsr-0.6-configuration.md",
                    "proposals/distributed-recovery/2026-10-08/dsr-0.6-preparation.md",
                }
                local = local and parsed.path in owners and bool(parsed.fragment)
                require(local, f"{label} evidence must reference an anchored existing decision/configuration owner")
                if not local:
                    continue
                require(destination.is_file(), f"{label} evidence file is missing")
                if not destination.is_file():
                    continue
                require(
                    hashlib.sha256(destination.read_bytes()).hexdigest() == reference.get("sha256"),
                    f"{label} evidence digest differs",
                )
                if parsed.fragment:
                    require(
                        destination.suffix == ".md" and unquote(parsed.fragment) in anchors(destination.read_text()),
                        f"{label} evidence anchor is missing",
                    )

        owner_decisions = answers["decisions"]
        require(set(owner_decisions) == {f"BD-{n}" for n in range(1, 7)}, "decision answer inventory differs")
        for identifier in (owner_decisions if status == "DONE" else confirmed):
            record = owner_decisions.get(identifier, {})
            require(isinstance(record.get("answer"), str) and concrete(record["answer"]), f"{identifier} lacks a complete recorded answer")
            require(record.get("approved") is True, f"{identifier} is not approved")
            evidence(record, identifier)
        if status != "DONE":
            return errors
        criteria = answers["criteria"]
        require(set(criteria) == set(CLOSURE_FIELDS), "six acceptance evidence groups are incomplete")
        for label, fields in CLOSURE_FIELDS.items():
            record = criteria.get(label, {})
            require(set(record.get("answers", {})) == set(fields), f"{label} answer fields are incomplete")
            require(all(concrete(record.get("answers", {}).get(field)) for field in fields), f"{label} contains unresolved answers")
            structured = set(fields) if label == "assumptions" else (
                {"runtime_pins", "retention", "workload_bounds"} if label == "configuration" else set()
            )
            require(
                all(
                    isinstance(record.get("answers", {}).get(field), dict) if field in structured
                    else isinstance(record.get("answers", {}).get(field), str)
                    for field in fields
                ),
                f"{label} answer fields require text or declared structured values",
            )
            require(record.get("approved") is True, f"{label} is not approved")
            evidence(record, label)
        refusal = criteria.get("refusal", {}).get("answers", {})
        require(
            all(refusal.get(field) == "refuse" for field in CLOSURE_FIELDS["refusal"][:-1])
            and refusal.get("restore_permission") == "never",
            "refusal matrix must deny missing authority, mismatched pair, uncertain death and local guard failure; restore never recreates permission",
        )
        assumptions = criteria.get("assumptions", {}).get("answers", {})
        require(
            all(isinstance(assumptions.get(key), dict)
                and set(assumptions[key]) == {"disposition", "interim_claim"}
                and assumptions[key]["disposition"] in {"revised", "retained", "superseded"}
                and isinstance(assumptions[key]["interim_claim"], str)
                and concrete(assumptions[key]["interim_claim"])
                for key in CLOSURE_FIELDS["assumptions"]),
            "each assumption needs a disposition and interim Phase 4 claim",
        )
        configuration = criteria.get("configuration", {}).get("answers", {})
        bounds = configuration.get("workload_bounds", {})
        bound_fields = {
            "sessions", "pending_calls", "effects", "workspace_bytes",
            "model_output_bytes", "raw_result_bytes", "envelope_bytes",
            "index_bytes", "scratch_bytes", "processes", "cpu_seconds",
            "deadline_seconds", "clock_skew_seconds", "recovery_window_seconds",
        }
        require(
            isinstance(bounds, dict) and set(bounds) == bound_fields
            and all(isinstance(value, int) and not isinstance(value, bool)
                    and value > 0 for value in bounds.values())
            and all(bounds.get(field) == 1 for field in ("sessions", "pending_calls", "effects")),
            "synthetic qualification needs exact positive finite bounds and one session/call/effect",
        )
        retention = configuration.get("retention", {})
        require(
            isinstance(retention, dict)
            and isinstance(retention.get("minimum_seconds"), int)
            and not isinstance(retention.get("minimum_seconds"), bool)
            and retention.get("minimum_seconds", 0) >= 604800
            and retention.get("minimum_seconds", 0) >= (
                bounds.get("recovery_window_seconds", 0) if isinstance(bounds, dict) else 0
            )
            and retention.get("extend_while_referenced") is True,
            "retention must cover seven days, the recovery window and all live/parked/reset/replay references",
        )
        pins = configuration.get("runtime_pins")
        require(
            isinstance(pins, dict) and bool(pins) and all(
                isinstance(key, str) and concrete(key) and exact_runtime_pin(value)
                for key, value in pins.items()
            ),
            "runtime pins need exact version, commit or content digest strings",
        )
        gates = answers["qualification_gates"]
        require(
            set(gates) == {"DSR-4.3", "Q-7", "Q-15"}
            and all(isinstance(record, dict)
                    and record.get("status") == "unexecuted"
                    and isinstance(record.get("owner"), str) and concrete(record["owner"])
                    and isinstance(record.get("required_evidence"), str) and concrete(record["required_evidence"])
                    for record in gates.values()),
            "physical and component qualification must remain explicit future gates, with holder and required proof",
        )
        require(
            len(re.findall(r"^- \[x\]", section, re.M)) == 6
            and not re.search(r"^- \[ \]", section, re.M),
            "DONE needs all six acceptance criteria checked",
        )
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        require(False, f"missing or malformed confirmed record: {error}")
    return errors


def unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Build an evidence object, rejecting repeated keys before values collapse."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def reject_json_constant(value: str) -> None:
    """Reject nonfinite constants that are outside the JSON evidence format."""
    raise ValueError(f"invalid JSON constant {value}")


def exact_runtime_pin(value: object) -> bool:
    """Return whether a value names an exact version, commit or content digest."""
    if not isinstance(value, str):
        return False
    version = (
        r"v?[0-9]+\.[0-9]+\.[0-9]+(?:(?:a|b|rc)[0-9]+)?"
        r"(?:\.post[0-9]+)?(?:\.dev[0-9]+)?"
        r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
        r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    )
    return re.fullmatch(
        "(?:" + version + r"|[0-9a-f]{40}|sha256:[0-9a-f]{64})", value
    ) is not None


def concrete(value):
    """Reject blank, placeholder and explicitly unresolved decision answers."""
    if isinstance(value, dict):
        return bool(value) and all(
            (key == "extend_while_referenced" and item is True) or concrete(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return bool(value) and all(concrete(item) for item in value)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value > 0
    return isinstance(value, str) and bool(value.strip()) and not re.search(
        r"\b(?:TBD|TODO|OPEN|unresolved|unselected|unknown|proposed|pending)\b",
        value, re.I,
    )


def check(root):
    """Return validation errors and the number of checked Markdown links."""
    errors = []
    links = 0

    def require(condition, message):
        if not condition:
            errors.append(message)

    owners = {}
    for name in ("spec.md", "plan.md", "evidence.md", "work-items.md"):
        path = root / name
        require(path.is_file(), f"missing canonical owner {name}")
        if path.is_file():
            owners[name] = path.read_text()
    if len(owners) != 4:
        return errors, links
    spec = rows(owners["spec.md"])
    expected = {f"A-{number:02}" for number in range(1, 60)}
    require(
        set(spec) == expected,
        "canonical assumption inventory differs from A-01 through A-59",
    )
    plan = rows(owners["plan.md"])
    expected_m1 = {
        f"A-{number:02}"
        for number in (1, 2, 3, 18, 19, 25, 26, 44, 49, 15, 22, 57, 58, 59)
    }
    require(
        set(plan) == expected_m1,
        "plan M1 inventory differs from the fourteen bounded dispositions",
    )
    for identifier, cells in plan.items():
        require(
            identifier in spec
            and len(spec[identifier]) > 2
            and cells[1] == spec[identifier][2],
            f"spec/plan status mismatch for {identifier}",
        )

    for identifier, filename, status in (
        ("DSR-1.6", "phase-1.md", "DONE"),
        ("DSR-1.7", "phase-1.md", "DONE"),
        ("DSR-1.9", "phase-1.md", "DONE"),
        ("DSR-2.1", "phase-2.md", "OPEN"),
    ):
        path = root / "tickets" / filename
        text = path.read_text()
        match = re.search(
            r"^#{1,6} " + re.escape(identifier) + r"\s[^\n]*\n\s*\nStatus: ([^\n]+)",
            text,
            re.M,
        )
        require(
            match is not None and match.group(1).startswith(status),
            f"{identifier} must retain its recorded {status} disposition",
        )
        if status == "DONE" and match is not None:
            require(
                "2026-10-07" in match.group(1) and "bounded" in match.group(1),
                f"{identifier} must retain its bounded Phase 1 scope and recorded date",
            )
    proposal = root / "proposals" / "distributed-recovery" / "2026-10-08"
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
        repository = (
            Path(result.stdout.strip()).resolve()
            if result.returncode == 0
            else root.parents[3]
        )
    except FileNotFoundError:
        repository = root.parents[3]
    candidate = proposal / "candidate"
    manifests = []
    evidence_targets = []
    fields = ("id", "tool", "operation", "query", "result_ref", "used_for", "status")
    for artifact, sidecar in (
        ("spec", "evidence.json"),
        ("plan", "plan-evidence.json"),
    ):
        data = json.loads((candidate / sidecar).read_text())
        sources = data["sources"]
        require(
            data.get("artifact") == artifact, f"wrong artifact identity in {sidecar}"
        )
        require(
            len({source["id"] for source in sources}) == len(sources),
            f"duplicate source in {sidecar}",
        )
        require(
            {source["id"] for source in sources}
            == {f"EV-{number}" for number in range(1, 47)},
            f"candidate evidence inventory differs from EV-1 through EV-46 in {sidecar}",
        )
        markdown = rows((candidate / f"{artifact}.md").read_text())
        evidence_rows = {
            key: cells for key, cells in markdown.items() if key.startswith("EV-")
        }
        expected_rows = {
            source["id"]: [str(source[field]) for field in fields] for source in sources
        }
        require(
            evidence_rows == expected_rows,
            f"candidate {artifact} evidence Markdown and JSON differ",
        )
        evidence_targets.extend(
            (candidate / sidecar, source["result_ref"]) for source in sources
        )
        manifests.append(sources)
    require(manifests[0] == manifests[1], "candidate evidence sidecars differ")
    candidate_spec = rows((candidate / "spec.md").read_text())
    assumptions = {key for key in candidate_spec if key.startswith("A-")}
    decisions = {key for key in candidate_spec if key.startswith("BD-")}
    require(
        assumptions == {f"A-{number}" for number in range(60, 75)},
        "candidate assumption inventory differs from A-60 through A-74",
    )
    require(
        decisions == {f"BD-{number}" for number in range(1, 7)},
        "candidate owner decision inventory differs from BD-1 through BD-6",
    )
    section = ticket_section((root / "tickets/phase-0.md").read_text(), "DSR-0.6")
    status_match = re.search(r"^Status: (OPEN|DONE)(?:\s|$)", section, re.M)
    status = status_match.group(1) if status_match else ""
    errors.extend(closure_errors(
        root, status,
        {identifier: candidate_spec[identifier] for identifier in decisions},
        section,
    ))
    require(
        "CONDITIONAL" in (proposal / "README.md").read_text()
        and "not adopted" in (proposal / "README.md").read_text(),
        "proposal adoption boundary is absent",
    )

    preservation = json.loads((proposal / "preservation-manifest.json").read_text())
    provenance = (proposal / "provenance.md").read_text()
    exports = preservation["exports"]
    export_paths = set()
    export_ids = set()
    for entry in exports:
        identifier = entry["id"]
        require(
            identifier not in export_ids,
            f"duplicate preservation identifier {identifier}",
        )
        export_ids.add(identifier)
        path = (proposal / entry["path"]).resolve()
        require(
            path.is_relative_to(proposal / "supporting-evidence"),
            f"projection path escapes supporting evidence: {identifier}",
        )
        if not path.is_relative_to(proposal / "supporting-evidence"):
            continue
        export_paths.add(path)
        content = path.read_bytes()
        require(
            hashlib.sha256(content).hexdigest() == entry["exported_sha256"]
            and len(content) == entry["bytes"],
            f"projection digest/size mismatch: {identifier}",
        )
        projection = json.loads(content)
        require(
            projection["provenance_id"] == identifier,
            f"projection identifier mismatch: {identifier}",
        )
        require(
            projection["original_sha256"] == entry["original_sha256"],
            f"projection original digest mismatch: {identifier}",
        )
        section = re.search(
            r"^## " + re.escape(identifier) + r"\n(.*?)(?=^## |\Z)",
            provenance,
            re.M | re.S,
        )
        require(
            section is not None
            and entry["original_sha256"] in section.group(1)
            and entry["path"] in section.group(1),
            f"provenance binding absent: {identifier}",
        )
        require(
            bool(
                projection["role"]
                and projection["transformations"]
                and projection["limitations"]
            ),
            f"projection disclosures absent: {identifier}",
        )
        if identifier == "P-035":
            require(
                projection["media_type"] == "application/json",
                "Issue 31 capture media type changed",
            )
            capture = json.loads(projection["content"])
            issue_url = "https://github.com/temporalio/ai-integrations/issues/31"
            require(
                capture["issue"]["html_url"] == issue_url
                and bool(capture["issue"]["body"]),
                "Issue 31 body or source identity missing",
            )
            comments = capture["comments"]
            identifiers = [comment["id"] for comment in comments]
            require(
                len(comments) == 12
                and len(set(identifiers)) == 12
                and identifiers[-1] == 6065563646,
                "Issue 31 twelve-comment recorded boundary changed",
            )
            for comment in comments:
                require(
                    comment["html_url"] == f"{issue_url}#issuecomment-{comment['id']}"
                    and bool(comment["body"]),
                    f"Issue 31 comment body/identity absent: {comment['id']}",
                )
    actual_paths = {
        path.resolve() for path in (proposal / "supporting-evidence").glob("*.json")
    }
    require(
        actual_paths == export_paths,
        "projection file inventory differs from preservation manifest",
    )
    supplemental_paths = set()
    for entry in preservation["supplemental_exports"]:
        path = (root / entry["path"]).resolve()
        require(
            not Path(entry["path"]).is_absolute() and path.is_relative_to(root),
            f"supplemental path escapes documentation root: {entry['path']}",
        )
        if Path(entry["path"]).is_absolute() or not path.is_relative_to(root):
            continue
        require(
            path not in supplemental_paths,
            f"duplicate supplemental export: {entry['path']}",
        )
        supplemental_paths.add(path)
        content = path.read_bytes()
        require(
            hashlib.sha256(content).hexdigest() == entry["exported_sha256"]
            and len(content) == entry["bytes"],
            f"supplemental digest/size mismatch: {entry['path']}",
        )
        require(
            re.fullmatch(r"[0-9a-f]{64}", entry["original_sha256"]) is not None,
            f"supplemental original digest is absent: {entry['path']}",
        )
    shutdown = root / "experiments/results/published/sdk-shutdown-verification-initial"
    require(
        {shutdown / "adversarial-suite.log", shutdown / "false-ready.log"}
        <= supplemental_paths,
        "supplemental shutdown failure evidence is absent from preservation manifest",
    )
    partitions = [
        export_ids,
        set(preservation["archive_only"]),
        {entry["id"] for entry in preservation["already_present"]},
        set(preservation["external_metadata_only"]),
    ]
    require(
        set.union(*partitions) == {f"P-{number:03}" for number in range(1, 44)}
        and sum(map(len, partitions)) == 43,
        "preservation dispositions do not partition all 43 provenance identities",
    )

    diagrams = proposal / "diagrams"
    receipts = list(diagrams.glob("*.receipt.json"))
    require(
        not receipts,
        "superseded diagram receipts remain in the maintained inventory",
    )
    receipts = [diagrams / "assessment-durability/architecture.delivery.json"]
    for path in receipts:
        receipt = json.loads(path.read_text())
        for filename, record in (
            (receipt["input"], receipt["specification"]),
            (receipt["output"], receipt["artifact"]),
        ):
            artifact = (path.parent / filename).resolve()
            require(
                artifact.is_relative_to(path.parent),
                f"diagram artifact escapes directory: {filename}",
            )
            if artifact.is_relative_to(path.parent):
                content = artifact.read_bytes()
                require(
                    hashlib.sha256(content).hexdigest() == record["sha256"]
                    and len(content) == record["bytes"],
                    f"diagram digest/size mismatch: {filename}",
                )
    extended = diagrams / "assessment-durability/artifact-receipt.json"
    receipt = json.loads(extended.read_text())
    require(
        receipt["output"] == "assessment-durability.html"
        and hashlib.sha256((extended.parent / receipt["output"]).read_bytes()).hexdigest()
        == receipt["artifact_sha256"],
        "assessment diagram digest or output differs from its receipt",
    )
    for name in (
        "skill-execution-binding.svg",
        "engine-adapter-boundaries.svg",
        "recovery-proof-sequence.svg",
    ):
        ElementTree.parse(diagrams / name)

    markdown_paths = {root / name for name in (*owners, "canonical-documents.md")}
    markdown_paths.update((root / "tickets").rglob("*.md"))
    markdown_paths.update(
        path
        for path in proposal.rglob("*.md")
        if "supporting-evidence" not in path.relative_to(proposal).parts
        or path.name == "README.md"
    )
    anchor_cache = {}
    reference_targets = list(evidence_targets)
    for path in sorted(markdown_paths):
        text = without_fences(path.read_text())
        targets = re.findall(r"\]\((<?[^\s)]+>?)(?:\s+\"[^\"]*\")?\)", text)
        reference_targets.extend((path, target) for target in targets)
    for path, target in reference_targets:
        target = target.strip("<>")
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc:
            continue
        links += 1
        destination = (
            (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
        )
        label = f"{path.relative_to(root)}: {target}"
        require(
            not Path(unquote(parsed.path)).is_absolute()
            and destination.is_relative_to(repository),
            f"nonportable link target {label}",
        )
        if Path(unquote(parsed.path)).is_absolute() or not destination.is_relative_to(
            repository
        ):
            continue
        require(destination.exists(), f"missing link target {label}")
        if destination.is_file() and parsed.fragment and destination.suffix == ".md":
            if destination not in anchor_cache:
                anchor_cache[destination] = anchors(destination.read_text())
            require(
                unquote(parsed.fragment) in anchor_cache[destination],
                f"missing heading anchor {label}",
            )
    return errors, links


def main():
    """Validate the selected document root and return a nonzero exit on drift."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="skill-recovery directory, including exported copies",
    )
    args = parser.parse_args()
    try:
        errors, links = check(args.root.resolve(strict=True))
    except (OSError, ValueError, KeyError, IndexError) as error:
        parser.exit(1, f"FAIL: {error}\n")
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(
        f"PASS: canonical owners, 59 assumptions, fourteen M1 dispositions, bounded ticket states, candidate evidence, fifteen candidate assumptions, six owner decision dispositions and {links} local links/evidence references"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
