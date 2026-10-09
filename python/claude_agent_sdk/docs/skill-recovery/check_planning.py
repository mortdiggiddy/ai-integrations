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
        ("DSR-0.6", "phase-0.md", "OPEN"),
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
    for identifier in decisions:
        require(
            candidate_spec[identifier][-1] == "Open",
            f"candidate owner decision {identifier} is not Open",
        )
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

    receipts = list((proposal / "diagrams").glob("*.receipt.json"))
    require(
        len(receipts) == 4,
        "diagram delivery receipt inventory differs from four maintained views",
    )
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
        ElementTree.parse(path.with_name(path.name.replace(".receipt.json", ".svg")))

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
        f"PASS: canonical owners, 59 assumptions, fourteen M1 dispositions, bounded ticket states, candidate evidence, fifteen candidate assumptions, six open decisions and {links} local links/evidence references"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
