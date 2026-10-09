# Epics

### DSR-ROOT Reach a PASS verdict on the durable skill execution design

Status: OPEN

Approved budget separation checkpoint (2026-10-03): see [canonical pointer](../canonical-documents.md), *Approved experiment authorization separation*. Earlier budget gate wording in historical checkpoints is superseded for Phase 1 monitored experiments only. No live run is authorized and strict preventive budgeting remains required at DSR-5.8 final acceptance.

- Type: Epic
- Priority: Urgent
- Estimate: 3 points (confidence 70 percent)
- Labels: none
- Parent: none
- Blocked by: none
- Blocks: none
- Related: none
- Retires: none
- Informs: none
- Owner role: Operator

#### Context

The specification and plan describe durable Claude Code skill execution through the Claude Agent SDK plugin for Temporal AI integrations. Earlier reviews returned CONDITIONAL because proving evidence and owner decisions were missing. Approved Option R retains the proving obligations for its included mechanisms, preserves superseded rows and adds A-52 to A-56 for review gaps. Scope approval is not runtime proof.

#### Problem

The design cannot receive a PASS verdict from `verify-design` until its material claims are confirmed by evidence and no open decision blocks the stated outcome. The path to that evidence runs through decisions, real model runs and built code, not through further editing.

#### Scope

- Move the design from CONDITIONAL to PASS in seven ordered phases, each ending in an exit review that records a continue or redesign decision.
- Settle every row of the specification's assumptions table by evidence or by a recorded design change.
- Name an owner and record an answer for every decision the approved scope needs.
- Run the final independent verification pass and resolve its findings.

#### Out of scope

- Upstream submission and the agent harness port. Phase 7 holds them, and they are not required for PASS.
- Any change to the Temporal platform or the Claude Code engine.
- A tracker copy of these tickets. They stay local.

#### Acceptance criteria

- [ ] A `verify-design` run on the evidenced specification and plan returns PASS. The proof is the run's report, a verification manifest that passes `manifest_gate.py`, and a `proof_of_load.py` result of proven for each applied reviewer.
- [ ] Every row of the specification's assumptions table has the status verified at source with its proving artifact named, or is retired by a recorded design change. The proof is the table after DSR-6.1.
- [ ] Both evidence gates pass for the final documents. The proof is the gate output for [canonical specification](../canonical-documents.md#specification) and for [canonical plan](../canonical-documents.md#plan) with `--spec`.

#### Dependencies and blockers

- Phase 0 decisions need an operator and named owners. No code work starts before DSR-0.4 and DSR-0.3 close.

#### Source evidence

- The specification, [canonical specification](../canonical-documents.md#specification): Rigor tier, Assumptions and risks if wrong.
- The plan, [canonical plan](../canonical-documents.md#plan): M0 decisions, Verification handoff.
- The `verify-design` skill's verdict definitions: PASS needs every material claim confirmed and no unresolved decision that blocks the outcome.

#### Open questions

- Operator: is a phase allowed to end in a redesign decision that changes later phases, and who approves a redesign?

### DSR-P0 Phase 0: Ground the design and make the owner decisions

Status: OPEN

Approved budget separation checkpoint (2026-10-03): see [canonical pointer](../canonical-documents.md), *Approved experiment authorization separation*. Earlier budget gate wording in historical checkpoints is superseded for Phase 1 monitored experiments only. No live run is authorized and strict preventive budgeting remains required at DSR-5.8 final acceptance.

- Type: Epic
- Priority: Urgent
- Estimate: 2 points (confidence 70 percent)
- Labels: none
- Parent: DSR-ROOT
- Blocked by: none
- Blocks: none
- Related: DSR-P1
- Retires: none
- Informs: none
- Owner role: Operator

#### Context

Phase 0 writes no product code. It records the one documented fact that the engine mechanism depends on, narrows the first version, and names the owners and the budget that later phases need.

#### Problem

Real model runs and executor code cannot start while the defer protocol is unrecorded, the version 1 scope is unapproved, and nobody owns the budget, the volume, the gateway or the reset policy.

#### Scope

- Tickets DSR-0.1 to DSR-0.12.
- Coordination of their decisions and the rebaseline of the documents.

#### Out of scope

- Building or testing any plugin behavior.

#### Acceptance criteria

- [ ] The official defer protocol is quoted in the pack with its URL, and the version 1 scope is approved and applied to the documents. The proof is DSR-0.1 and DSR-0.3 in DONE status.
- [ ] Each decision that the approved scope needs has a named owner role and a recorded answer. The proof is the decision records of DSR-0.4 to DSR-0.12, or a SUPERSEDED mark where the scope removes the decision. DSR-0.12 follows DSR-1.10 and does not block that comparison through this epic.

#### Dependencies and blockers

- Concrete work ticket blockers govern starts. The integration decision DSR-0.12 follows the Phase 1 comparison, so this owner decision grouping does not impose a whole epic start gate on Phase 1.

#### Source evidence

- [canonical plan](../canonical-documents.md#plan), M0, decisions (a) to (j).

#### Open questions

- Operator: which M0 decisions can the version 1 scope remove?

### DSR-P1 Phase 1: Prove the engine mechanism with a real model

Status: OPEN

- Type: Epic
- Priority: Urgent
- Estimate: 2 points (confidence 70 percent)
- Labels: none
- Parent: DSR-ROOT
- Blocked by: none
- Blocks: DSR-P2
- Related: DSR-P0
- Retires: none
- Informs: none
- Owner role: Plugin engineer

#### Context

All engine evidence so far comes from a fake model. The design depends on the engine accepting a host supplied result for a deferred call, which no documentation read for this pack describes.

#### Problem

If the mechanism fails with a real model, every later phase builds on a false premise.

#### Scope

- Tickets DSR-1.1 to DSR-1.10. DSR-0.12 records the adoption choice after the candidate comparison and before DSR-1.3 and DSR-1.9.
- A decision at the exit review to continue or to redesign around the documented resume path.

#### Out of scope

- Production effect execution, approvals and isolation. The bounded candidate comparison tests their recovery boundaries but does not build these later phase outcomes.

#### Acceptance criteria

- [ ] The assumptions that the README lists for this phase are settled on evidence or an explicit approved rejection or scope change. The proof is the updated table, the DSR-0.12 adoption record and the DSR-1.9 decision record.

#### Dependencies and blockers

- Retained preparation, budget and scope blockers apply to the concrete work tickets. DSR-1.10 precedes DSR-0.12, which blocks DSR-1.3 and the exit review; the two epics are groupings, not an additional cycle of start gates.

#### Source evidence

- [canonical plan](../canonical-documents.md#plan), M1.
- [canonical specification](../canonical-documents.md#specification), OI-1, OI-3, OI-4.

#### Open questions

- None.

### DSR-P2 Phase 2: Build and prove the effect executor and workspace

Status: OPEN

- Type: Epic
- Priority: High
- Estimate: 2 points (confidence 70 percent)
- Labels: none
- Parent: DSR-ROOT
- Blocked by: DSR-P1
- Blocks: DSR-P3
- Related: none
- Retires: none
- Informs: none
- Owner role: Plugin engineer

#### Context

Effects that the engine defers must run in a Temporal Activity with a known outcome. The executor owns the claim files, the outcome table, the retry rules and the engine behavior match.

#### Problem

Without a proven executor, a failed or repeated effect gives the model a false account of what ran.

#### Scope

- Tickets DSR-2.1 to DSR-2.9.

#### Out of scope

- Approvals, tokens, parked runs and isolation.

#### Acceptance criteria

- [ ] The assumptions that the README lists for this phase are settled. The proof is the updated table and the DSR-2.9 decision record.

#### Dependencies and blockers

- DSR-P1 closes first. Items that the version 1 scope drops become SUPERSEDED.

#### Source evidence

- [canonical plan](../canonical-documents.md#plan), M2.
- [canonical specification](../canonical-documents.md#specification), INV-1, INV-5, Interfaces.

#### Open questions

- None.

### DSR-P3 Phase 3: Build and prove human decisions, signed tokens and parked runs

Status: OPEN

- Type: Epic
- Priority: High
- Estimate: 2 points (confidence 70 percent)
- Labels: none
- Parent: DSR-ROOT
- Blocked by: DSR-P2
- Blocks: DSR-P4
- Related: none
- Retires: none
- Informs: none
- Owner role: Plugin engineer

#### Context

Questions, approvals and operator resume actions must survive Worker loss and Continue-As-New, and must resist a forged or replayed request.

#### Problem

An approval that is lost, forged or applied twice gives a wrong decision to a paid run.

#### Scope

- Tickets DSR-3.1 to DSR-3.8. The exit review is DSR-3.7.

#### Out of scope

- Isolation, janitor and deployment.

#### Acceptance criteria

- [ ] The assumptions that the README lists for this phase are settled. The proof is the updated table and the DSR-3.7 decision record.

#### Dependencies and blockers

- DSR-P2 closes first, and the gateway and reset decisions from Phase 0.

#### Source evidence

- [canonical plan](../canonical-documents.md#plan), M3.
- [canonical specification](../canonical-documents.md#specification), INV-4, INV-7, Interfaces.

#### Open questions

- None.

### DSR-P4 Phase 4: Build and prove isolation and workspace lifecycle

Status: OPEN

Approved budget separation checkpoint (2026-10-03): see [canonical pointer](../canonical-documents.md), *Approved experiment authorization separation*. Earlier budget gate wording in historical checkpoints is superseded for Phase 1 monitored experiments only. No live run is authorized and strict preventive budgeting remains required at DSR-5.8 final acceptance.

- Type: Epic
- Priority: Medium
- Estimate: 2 points (confidence 70 percent)
- Labels: none
- Parent: DSR-ROOT
- Blocked by: DSR-P3
- Blocks: DSR-P5
- Related: none
- Retires: none
- Informs: none
- Owner role: Security owner

#### Context

An effect runs a skill's own scripts. Isolation, the shared volume and run directory cleanup decide whether those scripts can harm the Worker or another run.

#### Problem

Without isolation and a safe lifecycle, a script can read Worker credentials, rewrite engine settings, or delete or outlive a live run's data.

#### Scope

- Tickets DSR-4.1 to DSR-4.5.

#### Out of scope

- Deployment, codec and acceptance runs.

#### Acceptance criteria

- [ ] The assumptions that the README lists for this phase are settled. The proof is the updated table and the DSR-4.5 decision record.

#### Dependencies and blockers

- DSR-P3 closes first, and the volume and isolation decision from Phase 0.

#### Source evidence

- [canonical plan](../canonical-documents.md#plan), M4.
- [canonical specification](../canonical-documents.md#specification), INV-2, INV-7.

#### Open questions

- None.

### DSR-P5 Phase 5: Harden, version and accept the plugin

Status: OPEN

- Type: Epic
- Priority: Medium
- Estimate: 2 points (confidence 70 percent)
- Labels: none
- Parent: DSR-ROOT
- Blocked by: DSR-P4
- Blocks: DSR-P6
- Related: none
- Retires: none
- Informs: none
- Owner role: Plugin engineer

#### Context

The remaining assumptions concern rollout, payload handling, load, shutdown, patching and engine upgrades, and one acceptance run against a real model.

#### Problem

A design that works in a test rig can still fail at deployment, upgrade or load.

#### Scope

- Tickets DSR-5.1 to DSR-5.9.

#### Out of scope

- The independent verification pass. Phase 6 covers it.

#### Acceptance criteria

- [ ] The assumptions that the README lists for this phase are settled, and one real model acceptance run passes under the budget cap. The proof is the updated table and the DSR-5.9 decision record.

#### Dependencies and blockers

- DSR-P4 closes first, and the rollout decision from Phase 0.

#### Source evidence

- [canonical plan](../canonical-documents.md#plan), M5.
- [canonical specification](../canonical-documents.md#specification), INV-2 Versioning.

#### Open questions

- None.

### DSR-P6 Phase 6: Pass the independent verification gate

Status: OPEN

- Type: Epic
- Priority: High
- Estimate: 2 points (confidence 70 percent)
- Labels: none
- Parent: DSR-ROOT
- Blocked by: DSR-P5
- Blocks: DSR-P7
- Related: none
- Retires: none
- Informs: none
- Owner role: Operator

#### Context

PASS needs evidence in the documents, no blocking decision, and an independent pass by fresh verifiers. Earlier passes were run on paper and returned CONDITIONAL.

#### Problem

The documents still describe proposals. They must describe the proven design before a verifier can confirm them.

#### Scope

- Tickets DSR-6.1 to DSR-6.4.

#### Out of scope

- New features.

#### Acceptance criteria

- [ ] The final `verify-design` verdict is PASS, with a passing manifest gate, proof of load and both evidence gates. The proof is the verdict report and the gate output recorded in the pack.

#### Dependencies and blockers

- DSR-P5 closes first.

#### Source evidence

- The `verify-design` skill, verdicts and the manifest gate.

#### Open questions

- None.

### DSR-P7 After PASS: Submit upstream and port to the agent harness

Status: OPEN

- Type: Epic
- Priority: Low
- Estimate: 2 points (confidence 60 percent)
- Labels: none
- Parent: DSR-ROOT
- Blocked by: DSR-P6
- Blocks: none
- Related: none
- Retires: none
- Informs: none
- Owner role: Plugin engineer

#### Context

These outcomes depend on the proven design and on outside owners: the repository that receives the pull requests, and the agent harness that receives the port.

#### Problem

The design is useful to others only after it lands in the repository and the harness.

#### Scope

- Tickets DSR-7.1 to DSR-7.3.

#### Out of scope

- Anything required for PASS.

#### Acceptance criteria

- [ ] The upstream pull requests and the harness glue meet the acceptance criteria of their tickets. The proof is the tickets' own evidence.

#### Dependencies and blockers

- DSR-P6 closes first.

#### Source evidence

- [canonical plan](../canonical-documents.md#plan), M6 and M7.

#### Open questions

- Operator: do these outcomes stay in this ticket set or move to a tracker the owning teams use?
