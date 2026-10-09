# DSR-0.6 decision preparation verification

Verdict: CONDITIONAL (2026-10-09). The independent preparation exit test is met with zero unresolved material contract contradictions or unsupported approval/runtime qualification claims. The [recommendation](dsr-0.6-preparation.md) is ready for the operator's bounded route decision and owner nominations. DSR-0.6 remains OPEN, DSR-2.1 remains blocked and the distributed candidate remains unadopted. This is documentation/design preparation verification, not distributed runtime qualification or a complete platform matrix.

## Scope and identities

Full verify-design pass of the new preparation and related reference/acceptance edits, against `design-base` commit `0e9bb011fd6d5dc414effc446173ce3d046ec745`. Initial working tree was clean. Final preparation SHA-256 is `a26d7bbbf3b6ec5eb6d5c2f2bded67775c49d3b370dd01e2f4c8d15b76e78e16`. Two fresh independent contexts reviewed the governing documents and actual source paths, then each reopened the final preparation and confirmed that digest. Neither edited files or ran experiments. They received the same raw contract and permitted evidence routes, not each other's conclusions. Lead reconciled their complete reports and directly rechecked decisive source and ticket lines.

Exit test stated before final review: no material contract contradiction or unsupported approval/qualification claim; smallest owner decision and proposed experiments must cover the material failure gaps. Both contract-evidence and adversarial-system reviewers returned CONDITIONAL and met that test. This does not meet DSR-6.4's production PASS definition. No complete candidate requalification is claimed: its four artifacts remain byte unchanged from the published commit.

The [manifest](dsr-0.6-review-manifest.json) records the full pass and domain evidence outcomes. This preparation file is not a new spec.md/evidence.json package, so no new specification package gate is represented as passed. Existing candidate evidence sidecars and historical gate/manifests remain unchanged.

## Independent findings and reconciliation

| Finding | Mandatory basis and consequence | Resolution |
|---|---|---|
| DSR-0.6's failure criterion allowed dropping the claim guard | Canonical protected dual-claim contract and retained claimed Bash boundary. Continuing without the guard could respawn an irreversible command. This is a directly scoped acceptance defect, not an optional storage preference. | Corrected owning criterion: refuse, reselect/qualify volume, or require separately approved and proven replacement authority. Never drop the guard while offering claimed Bash. |
| DSR-2.1 required both unchanged repeated prepare and generation increase on every prepare | Canonical finished-directory preparation is idempotent. Two criteria demanded different manifest bytes from the same repeated operation. | Corrected generation criterion: initial generation persists on verification; lower value refuses; explicit repair remains DSR-4.2 and preserves unresolved claims. |
| Exact backend, identity mapping, cache/ACK semantics and role holders remain unknown | Existing DSR-0.6 decision criteria and actual storage fault proof. A protocol/class name is not tested durability. | OWNER-DECISION and acceptance evidence, not a new approved mechanism. Required semantics are explicit in the final preparation; physical rig remains pending. |
| Baseline sensitive-state security must survive confidential-lane deferral | Canonical security and DSR-0.11 requirements. Optional hardware deferral cannot allow Worker credentials or plaintext sensitive storage by default. | Explicit preservation of encryption, least privilege, protected package/claims and trusted-host scope. No confidential guarantee is offered. |

Both initially identified acceptance inconsistencies are corrected, without implementation or acceptance checkbox changes. The lead accepted the remedies only after comparison with the canonical contract and independent reopening. Reviewers agreed on the remedies and final owner/evidence conditions; no verdict was selected by majority vote.

## Atomic claim ledger

| ID | Claim and provenance | Evidence | Status and consequence |
|---|---|---|---|
| C-1 | Phase 1 complete at approved bounded dispositions (`requirement_or_decision`) | Canonical [approved continue](../../../evidence.md#approved-phase-1-continue-decision-2026-10-07) and [independent verification](../../../evidence.md#independent-phase-1-verification-and-exact-json-correction-2026-10-07); Phase 1 tickets/status map. | Confirmed. DSR-1.6/1.7/1.9 remain complete; no repeated experiment or stronger matrix claim. |
| C-2 | Shared volume and dual file claims remain canonical (`requirement_or_decision`) | [Package/filesystem contract](../../../spec.md#package-and-filesystem-boundary), [effect contract](../../../spec.md#effect-identity-execution-and-outcomes), DSR-0.6. | Confirmed contract, unqualified runtime. Alternative adoption cannot be hidden inside DSR-2.1. |
| C-3 | NFSv4 target and unprivileged effect container are the next choice (`recommendation`) | Existing volume contract, [substrate comparison](storage-loop/substrate/report.md), preparation alternatives. | Conditional judgment about contract fit; no demonstrated backend superiority, acquisition permission or security guarantee. |
| C-4 | SDK recovery delegates workspace/outcome/ownership admission to caller (`current_behavior`) | `_runner.py`, constructor documentation at lines 560 through 563 and recovery capability/conditional append checks; attempt/fork refusal at lines 682 through 685. | Confirmed. Materializing a SessionStore alone cannot authorize recovery. |
| C-5 | Effect executor seam remains unavailable (`current_behavior`) | `_workflow.py`, `PolicyExecutorUnavailable` at lines 551 and 712. | Confirmed. Existing code does not implement this proposed deployment or another executor. |
| C-6 | Host teardown proof is local same-daemon evidence (`current_behavior`) | `experiments/host_session.py`, teardown at lines 381 through 437, exact ID/label/name, wait, stopped PID zero, remove/absence; explicit daemon constraint. | Confirmed at bounded scope. Does not qualify remote host death, hostile runtime or workspace extraction. |
| C-7 | Timeout/cancellation/storage availability is not physical termination (`product_constraint`) | Fresh Temporal Docs retrieval of https://docs.temporal.io/activity-execution#cancellation and existing fencing/substrate reports. | Confirmed. Old Activity/descendants can keep acting; replacement remains refused. |
| C-8 | Idempotent finished prepare preserves generation (`requirement_or_decision`) | Canonical preparation, corrected DSR-2.1 and existing workspace lifecycle ownership. | Confirmed design consistency; implementation pending. Generation alone proves no arbitrary rollback freshness. |
| C-9 | Accepted head/opaque chunks, cold receipt and independent dispatch are alternatives (`proposed_design`) | Candidate INV-5/assumptions A-60 through A-64, [storage synthesis](storage-loop/synthesis.md), verification and coverage. | Conditional partial precedent. The combined original pending/physical handover composition is unqualified. |
| C-10 | Lost accepted object is durability failure even if refusal is safe (`requirement_or_decision`) | Candidate acknowledged-state publication contract and smallest-test oracles. | Confirmed acceptance interpretation. A safe park is not host-loss durability PASS. |
| C-11 | Whole-execution death does not retract an earlier remote request (`assumption`) | Fencing research, canonical uncertain Bash requirement and adversarial counterexample. | Conditional external-effect failure model; witness separates issuance from late acceptance and ambiguous outcome remains parked. |
| C-12 | Applicable BD-1/BD-2/BD-6 are unresolved now (`open_decision`) | Candidate six Open decision rows, DSR-0.6 acceptance criteria and preparation split. | Confirmed open status. Narrow BD-3 preservation/BD-4 limits precede future experiments; final policy and BD-5 may defer without completion. |
| C-13 | Mods, positive child/batch recovery, response escrow and confidential execution remain unoffered (`requirement_or_decision`) | Mods synthesis, full Issue 31 map, DSR-7.4, candidate A-70 through A-74 and qualified lane dispositions. | Confirmed boundary. Deferred optional delivery does not satisfy the issue's requested future outcomes. |

Source line numbers identify the published source files under this plugin, not a mutable external default branch. Existing source implementation is unchanged. Mutable official pages corroborate recorded source evidence and are not backend/version qualification.

## Repository impact and phasing

Change classification: documentation_change with scoped acceptance corrections. Confirmed direct impact is the preparation/review/manifest, proposal README, canonical specification/plan/evidence/work-items references and owning DSR-0.6/DSR-2.1 ticket text. No code, dependencies, images, CI configuration or status graph changes.

Likely future impact if a deployment is selected: existing runner cwd/session-key and recovery admission, workspace preparation/manifest, protected effect wrapper/claim IO, supervisor and deployment permissions, SessionStore implementation, retention/janitor and corresponding tests. These are future qualification surfaces, not an adopted implementation inventory. The independent dispatch/cold protocol would additionally affect durable receipt schemas, reset/replay compatibility, authority retention and publication, only after BD-6 adoption. No new authority migration, mixed-version transition or rollback promise is approved here.

Sequence remains safe and bounded: operator chooses applicable deployment/failure boundary and role holders; later authorized preparation implements only DSR-2.1's retained contract; DSR-2.2/2.3/2.7 prove admission, uncertainty and process behavior; DSR-4.1/4.3 prove actual isolation/volume/physical replacement; DSR-0.11/5.4 supply store/lifecycle conformance. Distributed protocol changes require their separate candidate M0/adoption and qualification sequence. Stop or park on failed identity, claims, teardown, publication or ambiguous Bash; no rollout based on this document review. The original phase dependencies remain intact.

## Adversarial results and acceptance evidence

The recommendation withstands lost successful admission replies, preclaim workspace rollback at unchanged generation, detached `setsid` children, partitions retaining effect egress, delayed acceptance of predeath requests, post-effect upload failure, removal of the sole readable stopped workspace, absent/fallback Mods and attempts to reuse main serial recovery for children/batches. No counterexample is dismissed as solved by lease expiry, storage availability, Activity timeout or force deletion.

The preparation's experiment table owns proposed discriminating tests. Its oracles distinguish protocol mocks, real backend acknowledgement/claim semantics and actual host/process proof. Every physical test needs a separate authorized rig and finite limits. No experiment ran in this review; baseline runtime evidence and consumed reservations remain original. Earlier FAIL/DEFECT, publication manifests, raw archives and complete issue source boundary through comment 6065563646 are preserved.

## Domain review and source discovery

The installed Temporal workflow design critic was read and applied with its rubric, checklist and decision guide by both independent roles. Domain verdict was approve_with_changes for qualification design; no new material domain defect remains. At design level, deterministic orchestration, regular Activity IO, stable logical identity, one-attempt nonrepeatable parking, read only Queries and bounded handler-drained Continue-As-New are appropriate. Actual claims/idempotency, finite physical deadlines, whole-tree death, worker availability/registration, exact converter/storage lifecycle and authority reset/retention remain inconclusive until qualification. Claude child recovery is properly denied; unrelated timers/schedules are not applicable.

Existing canonical and proposal research was read before fresh lookup. Lead and each independent role made one successful Temporal Docs call, total three. Lead and adversarial role each made one Atlas wrapper query; neither bounded query found a complete matching recovery composition. No universal prior-art absence is inferred. Existing SDK/features/canary precedent source inventories were reused. Temporal developer guidance was loaded by the lead for Workflow/Activity boundaries. No new dependency/source acquisition or external contact occurred.

Applicable instruction discovery inspected the root and affected ancestor directories for AGENTS.md, AGENTS.override.md, CLAUDE.md, GEMINI.md, .cursorrules and the standard harness/config/skill locations. Root AGENTS.md was the applicable instruction file; .github was the discovered guidance directory. CONTRIBUTING.md, python/README.md and shared make conventions were read. External repository registration identifies an operator-owned unaffiliated fork. No hook execution, plugin activation or access change was authorized by discovery.

## Gate disclosures and proof limits

Manifest gate: status complete. The following disclosure sentences are copied unchanged from its output.

The Temporal design review was installed and applied (discovered as `temporal-workflow-design-critic`, invoked by contract_review) and returned findings cited at C-4, C-5, C-6, C-9.

Temporal product and SDK behavior claims were grounded through Temporal Docs (3 successful connector calls across lead, contract_review, adversarial_review).

Composed Temporal mechanisms were classified against precedent by contract_review: Accepted Temporal head with exact opaque Claude trajectory materialization and sealed workspace receipt is partial precedent (source https://docs.temporal.io/external-storage); Independent Entity Workflow dispatch authority across outer reset with conservative ambiguous Bash parking is partial precedent (source https://docs.temporal.io/design-patterns/entity-workflow#implementation); Complete distributed original pending recovery with physical handover and rollback-resistant authority is no precedent found (source https://docs.temporal.io/activity-execution#cancellation).

The Temporal developer skill was installed and applied (discovered as `temporal:temporal-developer`, invoked by lead) and returned findings cited at C-4, C-9.

The legacy proof-of-load checker reports all four rows not-proven: it cannot resolve this Codex lead transcript or independent role transcripts, and it does not check Temporal Docs URL precedent sources. It reports no fabrication. The manifest declaration is the only enforcement for those calls/loads in this checker; actual successful tool calls, shell skill reads and independent reports are separate session evidence. This limitation does not convert runtime tests into proof or suppress remaining owner decisions.

## Deterministic checks and remaining blockers

Repository conventions and Git whitespace checks pass. Ticket checker output is byte identical to published HEAD, including its 20 historical failures involving completed-checkbox/index parsing and existing path checks. That checker is not reported PASS or repaired within this decision scope. Status and checkbox-state comparison shows no advancement, all 59 canonical assumption IDs remain and candidate artifacts are byte unchanged. Local link/preservation checks cover the added references and final changed tree. Full plugin suites/lint from publication are reused for unchanged code; no suite, engine experiment, hosted CI or platform matrix is newly claimed.

The exact next implementation blocker is unapproved applicable DSR-0.6 choices and unnamed accountable role holders. Exact backend/version/mount identity, numeric test bounds, retention horizon for new authority tests and actual physical qualification remain prerequisites before their future execution/guarantees. The single next action is the operator's bounded route choice and role-holder nomination. No decision approval or implementation follows from this verification.
