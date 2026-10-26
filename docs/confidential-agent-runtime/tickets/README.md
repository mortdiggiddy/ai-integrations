# Confidential native runtime backlog

Local mode: The project owner selected an authoritative local Markdown backlog with no Linear or Jira tracker holding this work, and confirmed the default vocabulary and point scale on 2026-10-26.

The `CNR` series means confidential native runtime. IDs are stable and are not reused. This set replaces the archived DSR queue as the active delivery backlog; it does not change historical ticket states. The [specification](../spec.md), [plan](../plan.md) and [decision register](../decisions.md) own requirements. The [obligation map](../obligation-map.md) preserves the full historical scope.

## Delivery order and readiness

Start with [CNR-2](m1-external-runtime.md#cnr-2-launch-an-explicit-external-runtime-without-changing-legacy-execution). It establishes external placement and creation admission. CNR-3 and CNR-4 can then proceed independently. CNR-5 produces the runnable harness example; CNR-6 verifies the complete M1 outcome and prepares the upstream review package. Keep tests with the behavior they prove; CNR-6 supplies independent acceptance rather than postponing tests until the end.

[CNR-1](m1-external-runtime.md#cnr-1-deliver-external-runtime-orchestration) groups M1. Its design review is PASS; its implementation remains OPEN. [CNR-10, CNR-20 and CNR-30](later-milestones.md) retain M2, M3 and M4 as unestimated milestone containers. They are not implementation ready work packages. Expand only the next bounded outcome after its relevant design gates are met. Do not copy the old phase graph or assign speculative estimates to the entire future runtime.

The first joint Claude demo is an early M2 outcome: native skill execution in a harness owned local runtime. M1 first demonstrates the generic process lifecycle without a model. Completion of M1 does not require the complete confidential runtime or a live cloud run. The [collaboration handoff](../collaboration-handoff.md) defines the proposed ownership and demo sequence.

## Estimates and priorities

The confirmed recommended default defines one point as about four focused work hours, with the complete allowed scale 1, 2, 3, 4 and 5. Values represent about 4, 8, 12, 16 and 20 focused work hours. They include the ticket's implementation, tests and review preparation, but exclude passive waits. They are planning estimates, not dates or delivery promises. Container estimates are `none`; child work is not counted again in a parent.

M1 work is High priority because the selected first contribution enables the earliest useful review and demo. Later milestone containers are Medium priority because they follow that delivery. There is no invented urgent deadline. All estimates have at least 80 percent scope confidence at this baseline; reestimate when actual source impact changes. The single work type label and the optional External runtime topic have at least 80 percent confidence from each ticket's explicit scope. No assignee, calendar period or due date is inferred.

## Definition of done

Each ticket closes only with its stated observable evidence. M1 closes after the complete contract passes independent implementation verification, a retained legacy history replays, the example is reproducible and a draft upstream contribution is ready for maintainer review. Maintainer acceptance is a separate merge decision. No local check or draft handoff proves live provider behavior, host recovery or confidentiality.

Retain the M1 source pin and compare any newer target revision before implementation. A material design change returns to scoped design review. Later phases preserve their existing decision and qualification gates. Ordinary Docker execution does not qualify protection from the host operator. Paid inference, cloud allocation, publishing and upstream merge require their applicable authorization.

## Validation

Run these commands from the checkout of the authoring tools, substituting the ticket directory as the final argument:

```text
python3 .claude/skills/write-tickets/scripts/validate_local.py check <ticket-directory>
python3 .claude/skills/write-tickets/scripts/validate_local.py order <ticket-directory>
```

The order command derives delivery waves from ticket relationships. It does not authorize implementation of later milestone containers. The [ticket evidence](../ticket-evidence.md) records inspected pins, source roles and the acceptance mapping. This set has no external tracker mirror or export.
