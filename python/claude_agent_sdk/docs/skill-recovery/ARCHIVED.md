# Archived governed skill recovery project

Status: ARCHIVED IN PLACE, 2026-10-26. This tree is historical evidence and retained implementation support. It is not the active project specification or backlog.

The active [confidential runtime package](../../../../docs/confidential-agent-runtime/README.md) owns the replacement design. Its [obligation map](../../../../docs/confidential-agent-runtime/obligation-map.md) accounts for the old requirements, assumptions and work items. The initial broader review returned CONDITIONAL; the subsequent [M1 design review](../../../../docs/confidential-agent-runtime/verification-report.md) returned PASS. Later stages retain their own gates. Open owner decisions remain open; archival does not waive their obligations or establish runtime acceptance.

Files remain at their original paths because tests import experiment support from this tree, historical records link to it, and substantial local evidence is retained here. Moving it would require a separate source and fixture migration. No experiment result, approval record, reservation or ticket status is rewritten by this archive notice.

Read each record within its stated date, version and scenario. Terms such as current, canonical and next action in the retained body text describe the old project. They do not override this notice or the active project package. The historical ticket set is frozen for the new architecture. The next handoff creates M1 tickets from the approved plan; later work remains subject to its phase gates.

The historical `check_planning.py` remains scoped to this old contract. Before the cutover it reported `FAIL: diagram delivery receipt inventory differs from four maintained views` against existing diagram changes. The diagram replacement commit updated its maintained inventory and digest checks; the checker now passes. The earlier result remains part of the cutover history. The active package uses its own document and coverage validation.
