#!/usr/bin/env python3
"""Validate the local ticket set against the contract in README.md.

Usage: check_tickets.py [<tickets-dir>] [--order]

With --order the script prints the work order (waves of tickets that can run in parallel)
derived from the Blocked by links, and exits non zero if any check failed.

Checks, all fail closed:
  ids         every ticket and epic in the README tables exists once, and no other id exists
  fields      each block carries the required fields with values from the controlled vocabularies
  body        each block carries the eight body sections in order, at least one checkbox
              acceptance criterion and at least one source evidence line
  graph       parent, blocked by, blocks and related ids resolve, blocks and blocked by agree,
              every ticket has a parent and at least one relationship, and each phase exit
              review is blocked by every other ticket in its phase
  order       the Blocked by links have no cycle, every ticket in Phases 0 to 5 blocks the
              PASS gate DSR-6.4 directly or through others, and no ticket in Phases 2 to 6
              can start before the exit review of the previous phase
  coverage    every assumption id in spec.md appears in a Retires field
  style       no em dash, no en dash, no absolute local path, no planning period label
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = HERE.parent / "spec.md"
BAD_DASHES = (chr(0x2014), chr(0x2013))

TYPES = {"Decision", "Research", "Build", "Verification", "Documentation"}
TOPICS = {"Engine", "Effects", "Approvals", "Workspace", "Versioning", "Assumptions"}
STATUS_FLAGS = {"Status: Blocked on decision"}
PRIORITIES = {"Urgent", "High", "Medium", "Low"}
STATUSES = ("OPEN", "IN PROGRESS", "DONE", "SUPERSEDED")
SECTIONS = [
    "Context",
    "Problem",
    "Scope",
    "Out of scope",
    "Acceptance criteria",
    "Dependencies and blockers",
    "Source evidence",
    "Open questions",
]
FIELDS = [
    "Type",
    "Priority",
    "Estimate",
    "Labels",
    "Parent",
    "Blocked by",
    "Blocks",
    "Related",
    "Retires",
    "Informs",
    "Owner role",
]

HEAD_RE = re.compile(r"^### (DSR-(?:ROOT|P\d+|\d+\.\d+))\s+(.+)$")
FIELD_RE = re.compile(r"^- ([A-Za-z ]+): (.*)$")
ID_RE = re.compile(r"DSR-(?:ROOT|P\d+|\d+\.\d+)")
A_RE = re.compile(r"\bA-\d+\b")


def readme_ids(text):
    tickets, epics = set(), set()
    for line in text.splitlines():
        m = re.match(r"^\| (DSR-[^ |]+) \|", line)
        if not m:
            continue
        i = m.group(1)
        (epics if (i == "DSR-ROOT" or re.match(r"DSR-P\d+$", i)) else tickets).add(i)
    return tickets, epics


def spec_assumption_ids():
    text = SPEC.read_text()
    body = text.split("## Assumptions and risks if wrong", 1)[1].split(
        "## Authoritative location", 1
    )[0]
    return set(re.findall(r"^\| (A-\d+) \|", body, re.M))


def parse_blocks(path):
    blocks, cur = [], None
    for ln in path.read_text().splitlines():
        m = HEAD_RE.match(ln)
        if m:
            cur = {
                "id": m.group(1),
                "title": m.group(2),
                "lines": [],
                "file": path.name,
            }
            blocks.append(cur)
        elif cur is not None:
            cur["lines"].append(ln)
    return blocks


def ids_in(value):
    return set(ID_RE.findall(value))


def ticket_key(tid):
    phase, num = tid[len("DSR-") :].split(".")
    return int(phase), int(num)


def main():
    positional = [a for a in sys.argv[1:] if not a.startswith("--")]
    show_order = "--order" in sys.argv[1:]
    root = Path(positional[0]).resolve() if positional else HERE
    errors, low_conf = [], []
    readme = (root / "README.md").read_text()
    want_tickets, want_epics = readme_ids(readme)
    blocks = []
    for f in sorted(root.glob("*.md")):
        if f.name != "README.md":
            blocks.extend(parse_blocks(f))

    seen = {}
    for b in blocks:
        if b["id"] in seen:
            errors.append(
                "ids: %s appears twice (%s and %s)"
                % (b["id"], seen[b["id"]], b["file"])
            )
        seen[b["id"]] = b["file"]
    have = set(seen)
    for missing in sorted((want_tickets | want_epics) - have):
        errors.append("ids: %s is in the README tables but has no block" % missing)
    for extra in sorted(have - (want_tickets | want_epics)):
        errors.append("ids: %s has a block but is not in the README tables" % extra)

    info = {}
    for b in blocks:
        bid = b["id"]
        lines = b["lines"]
        is_epic = bid in want_epics
        body = "\n".join(lines)
        nonblank = [l for l in lines if l.strip()]
        if not nonblank or not any(
            nonblank[0].startswith("Status: " + s) for s in STATUSES
        ):
            errors.append(
                "%s fields: the first line after the heading must be Status: OPEN, IN PROGRESS, DONE or SUPERSEDED"
                % bid
            )
        fields = {}
        for l in lines:
            if l.startswith("#### "):
                break
            m = FIELD_RE.match(l)
            if m:
                fields[m.group(1)] = m.group(2).strip()
        for need in FIELDS:
            if need not in fields:
                errors.append("%s fields: missing field %s" % (bid, need))
        if any(k not in fields for k in FIELDS):
            continue
        if fields["Priority"] not in PRIORITIES:
            errors.append(
                "%s fields: Priority %r is not one of %s"
                % (bid, fields["Priority"], sorted(PRIORITIES))
            )
        em = re.match(
            r"^(\d) points? \(confidence (\d{1,3}) ?(?:percent|%)\)$",
            fields["Estimate"],
        )
        if not em or not 1 <= int(em.group(1)) <= 5 or not 0 < int(em.group(2)) <= 100:
            errors.append(
                "%s fields: Estimate %r must read '<1 to 5> points (confidence <n> percent)'"
                % (bid, fields["Estimate"])
            )
        elif int(em.group(2)) < 80:
            low_conf.append((bid, int(em.group(1)), int(em.group(2))))
        if not is_epic:
            if fields["Type"] not in TYPES:
                errors.append(
                    "%s fields: Type %r is not one of %s"
                    % (bid, fields["Type"], sorted(TYPES))
                )
            labels = [x.strip() for x in fields["Labels"].split(",") if x.strip()]
            types = [x for x in labels if x.startswith("Type: ")]
            topics = [x for x in labels if x.startswith("Topic: ")]
            flags = [x for x in labels if x.startswith("Status: ")]
            other = [
                x for x in labels if not x.startswith(("Type: ", "Topic: ", "Status: "))
            ]
            if len(types) != 1 or types[0] != "Type: " + fields["Type"]:
                errors.append(
                    "%s fields: Labels must hold exactly one work type label equal to Type"
                    % bid
                )
            if len(topics) > 2 or any(
                t[len("Topic: ") :] not in TOPICS for t in topics
            ):
                errors.append(
                    "%s fields: Labels hold zero to two known Topic labels" % bid
                )
            if len(flags) > 1 or any(f not in STATUS_FLAGS for f in flags):
                errors.append(
                    "%s fields: Labels hold at most one known status flag" % bid
                )
            if other or any("Cycle" in x or "Sprint" in x for x in labels):
                errors.append(
                    "%s style: Labels hold an unknown or planning period label: %s"
                    % (bid, other)
                )
        positions = []
        for sec in SECTIONS:
            m = re.search(r"^#### %s\s*$" % re.escape(sec), body, re.M)
            if not m:
                errors.append("%s body: missing section '%s'" % (bid, sec))
            else:
                positions.append(m.start())
        if positions != sorted(positions):
            errors.append("%s body: sections are out of order" % bid)
        ac = re.search(
            r"^#### Acceptance criteria\s*$(.*?)(?=^#### |\Z)", body, re.M | re.S
        )
        if not ac or not re.search(r"^- \[ \] \S", ac.group(1), re.M):
            errors.append(
                "%s body: Acceptance criteria needs at least one '- [ ]' item" % bid
            )
        ev = re.search(
            r"^#### Source evidence\s*$(.*?)(?=^#### |\Z)", body, re.M | re.S
        )
        if not ev or not re.search(r"^- \S", ev.group(1), re.M):
            errors.append("%s body: Source evidence needs at least one item" % bid)
        info[bid] = fields
        if any(d in body for d in BAD_DASHES):
            errors.append("%s style: contains an em dash or en dash" % bid)
        if re.search(r"/home/|Workspace/", body):
            errors.append("%s style: contains an absolute local path" % bid)

    for bid, f in info.items():
        parent = f["Parent"]
        if bid == "DSR-ROOT":
            if parent.lower() != "none":
                errors.append("DSR-ROOT graph: Parent must be none")
        elif parent not in info:
            errors.append("%s graph: Parent %r does not resolve" % (bid, parent))
        for key in ("Blocked by", "Blocks", "Related"):
            for r in ids_in(f[key]):
                if r not in info:
                    errors.append("%s graph: %s names unknown id %s" % (bid, key, r))
        for r in ids_in(f["Blocks"]):
            if r in info and bid not in ids_in(info[r]["Blocked by"]):
                errors.append(
                    "%s graph: Blocks %s but %s does not list it under Blocked by"
                    % (bid, r, r)
                )
        for r in ids_in(f["Blocked by"]):
            if r in info and bid not in ids_in(info[r]["Blocks"]):
                errors.append(
                    "%s graph: Blocked by %s but %s does not list it under Blocks"
                    % (bid, r, r)
                )
        if bid in want_tickets:
            rel = ids_in(f["Blocked by"]) | ids_in(f["Blocks"]) | ids_in(f["Related"])
            if not rel:
                errors.append(
                    "%s graph: a ticket needs at least one Blocked by, Blocks or Related link"
                    % bid
                )

    exit_ids = {
        "DSR-1.9": "1",
        "DSR-2.9": "2",
        "DSR-3.7": "3",
        "DSR-4.5": "4",
        "DSR-5.9": "5",
    }
    for xid, ph in exit_ids.items():
        if xid not in info:
            continue
        others = {t for t in want_tickets if t.startswith("DSR-%s." % ph) and t != xid}
        got = ids_in(info[xid]["Blocked by"])
        if others - got:
            errors.append(
                "%s graph: exit review is not blocked by %s"
                % (xid, ", ".join(sorted(others - got)))
            )

    deps = {
        t: {d for d in ids_in(info[t]["Blocked by"]) if d in want_tickets}
        for t in want_tickets
        if t in info
    }
    waves, done, remaining = [], set(), set(deps)
    while remaining:
        wave = sorted((t for t in remaining if deps[t] <= done), key=ticket_key)
        if not wave:
            errors.append(
                "order: the Blocked by links contain a cycle among %s"
                % ", ".join(sorted(remaining, key=ticket_key))
            )
            break
        waves.append(wave)
        done |= set(wave)
        remaining -= set(wave)

    def ancestors(start):
        seen, stack = set(), [start]
        while stack:
            for d in deps.get(stack.pop(), ()):
                if d not in seen:
                    seen.add(d)
                    stack.append(d)
        return seen

    if not any(e.startswith("order:") for e in errors) and "DSR-6.4" in deps:
        to_pass = ancestors("DSR-6.4")
        for t in sorted(want_tickets, key=ticket_key):
            phase = t[4:].split(".")[0]
            if phase in "012345" and t not in to_pass:
                errors.append(
                    "path: %s is not blocking the PASS gate DSR-6.4, directly or through other tickets"
                    % t
                )
        previous_exit = {
            "2": "DSR-1.9",
            "3": "DSR-2.9",
            "4": "DSR-3.7",
            "5": "DSR-4.5",
            "6": "DSR-5.9",
        }
        for t in sorted(want_tickets, key=ticket_key):
            phase = t[4:].split(".")[0]
            gate = previous_exit.get(phase)
            if gate and t != gate and t in deps and gate not in ancestors(t):
                errors.append(
                    "order: %s can start before the exit review %s of the previous phase"
                    % (t, gate)
                )

    retired = set()
    for f in info.values():
        retired |= set(A_RE.findall(f["Retires"]))
    spec_ids = spec_assumption_ids()
    for a in sorted(spec_ids - retired, key=lambda s: int(s[2:])):
        errors.append(
            "coverage: %s is in the specification table but no ticket lists it under Retires"
            % a
        )
    for a in sorted(retired - spec_ids, key=lambda s: int(s[2:])):
        errors.append(
            "coverage: %s appears under Retires but is not in the specification table"
            % a
        )

    if show_order:
        print(
            "Work order, derived from the Blocked by links. A ticket in a wave can start when every ticket in an earlier wave that blocks it is DONE; tickets in one wave are independent of each other."
        )
        for n, wave in enumerate(waves):
            print("wave %2d: %s" % (n, ", ".join(wave)))
        return 0 if not errors else 1
    print(
        "tickets: %d blocks (%d tickets, %d epics), %d assumption ids"
        % (len(blocks), len(want_tickets), len(want_epics), len(spec_ids))
    )
    if low_conf:
        print("estimates below 80 percent confidence (%d):" % len(low_conf))
        for bid, pts, conf in sorted(low_conf):
            print("  %s: %d points at %d percent" % (bid, pts, conf))
    if errors:
        print("FAIL (%d)" % len(errors))
        for e in errors[:80]:
            print("  " + e)
        if len(errors) > 80:
            print("  ... and %d more" % (len(errors) - 80))
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
