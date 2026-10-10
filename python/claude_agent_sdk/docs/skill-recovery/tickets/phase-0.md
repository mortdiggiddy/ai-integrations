# Phase 0 tickets

### DSR-0.1 Record the official defer and resume protocol

Status: IN PROGRESS

Research and independent review recorded on 2026-09-30 in [the protocol note](../proposals/distributed-recovery/2026-10-08/provenance.md#p-008). Classification and the later-defer finding are evidenced. The full verbatim protocol criterion remains partial; no runtime proof or scope decision is claimed.

- Type: Research
- Priority: Urgent
- Estimate: 1 point (confidence 85 percent)
- Labels: Type: Research, Topic: Engine, Topic: Assumptions
- Parent: DSR-P0
- Blocked by: none
- Blocks: DSR-1.3
- Related: DSR-0.2
- Retires: A-01 (documented answer)
- Informs: A-02, A-22
- Owner role: Operator

#### Context

The design returns an Activity result to the Claude Code engine as a synthetic `tool_result` message on a resumed session. No document read for the pack describes this mechanism. The official section on resuming a deferred call could not be read when the pack was written ([canonical specification](../canonical-documents.md#specification), OI-1, evidence row EV-57 with status unreachable). A community project and a public issue report that the documented resume path fires `PreToolUse` again and the hook then answers allow. The plugin avoids that path on purpose ([canonical specification](../canonical-documents.md#specification), INV-3, *How a result returns*). Assumption A-01 states that the engine accepts the synthetic result. This ticket records what the official text says, so Phase 1 tests a known claim and not a guess.

#### Problem

The pack does not hold the official resume protocol for a deferred call. Without it, the highest risk in the design rests on a reporter claim and on spike results from a fake model.

#### Scope

- Open the official section "Defer a tool call for later" in a browser and quote its resume protocol in a decision record, with the URL and the read date.
- Classify the official text into one of three outcomes: it documents host supplied tool results, it documents only the path where the hook fires again and answers allow, or it is silent about both.
- State the consequence of the outcome for the design: the synthetic result stays primary, or the documented path moves from fallback A2 to primary, or the request to document host supplied results ([canonical specification](../canonical-documents.md#specification), OI-1 option b) goes ahead.
- Record the engine version and documentation date that the quote applies to.

#### Out of scope

- Any test against a real model. DSR-1.3 owns that proof.
- Building the fallback resume path.
- Editing [canonical specification](../canonical-documents.md#specification) or [canonical plan](../canonical-documents.md#plan). DSR-0.3 applies the recorded answer.

#### Acceptance criteria

- [ ] A decision record holds the verbatim text of the defer resume protocol, its URL and the read date. Proof: the record exists and a reviewer opens the URL and sees the same text.
- [ ] The record names exactly one of the three outcomes and states what it means for A-01 and for fallback A2. Proof: the recorded outcome and consequence sentences.
- [ ] If the section cannot be read (page missing, access blocked), the record states that fact, names the unreadable URL, and lists the next step with an owner. Proof: the record states the failure and the next step.
- [ ] The record states whether the official text says that a later `defer` is ignored after an `allow` on resume. Proof: a quoted sentence or the statement "not stated".

#### Dependencies and blockers

- No blocker. A person must read the page in a browser, because the page was not reachable through the fetch tool.
- This ticket blocks DSR-1.3, which tests the recorded claim with a real model.

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), OI-1 and A-01, and INV-3 *How a result returns*.
- Official page, evidence row EV-57: https://code.claude.com/docs/en/hooks#defer-a-tool-call-for-later
- Official page, evidence row EV-45: https://code.claude.com/docs/en/agent-sdk/hooks (defer ends the query, precedence rules).
- Fork note on the avoided path: https://github.com/osamastro7-droid/ai-integrations/blob/69f5497d3d3dec7ad3269c72ff266c2931c9f379/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_runner.py#L23-L33

#### Open questions

- Operator: if the official text documents only the allow on resume path, does the design adopt fallback A2 as primary? DSR-0.2 and DSR-0.3 must absorb the answer.
- Plugin engineer: does the official text name a minimum engine version for defer? This feeds DSR-1.7.

### DSR-0.2 Approve the version 1 scope

Status: DONE (2026-09-30)

The operator approved Option R, reduced version 1. [The authoritative scope decision](../proposals/distributed-recovery/2026-10-08/provenance.md#p-001) records the approval, G4 and S2 wording, assumption dispositions, affected tickets, PASS boundary and the open parked Bash procedure owned by the Operator. DSR-0.3 still applies the decision to the specification and plan; no implementation or runtime proof is claimed here.

- Type: Decision
- Priority: Urgent
- Estimate: 2 points (confidence 75 percent)
- Labels: Type: Decision, Topic: Effects, Topic: Assumptions
- Parent: DSR-P0
- Blocked by: none
- Blocks: DSR-0.3, DSR-0.8, DSR-0.10
- Related: DSR-0.1, DSR-0.5
- Retires: A-52, A-55
- Informs: A-04, A-05, A-06, A-07, A-08, A-09, A-10, A-11, A-13, A-15, A-16, A-21, A-23, A-36, A-42, A-45, A-47, A-49
- Owner role: Operator

#### Context

Revision 6 of the specification is large. It has 51 assumption rows, and about 20 of them are proposed fixes that no independent pass has verified. Many proposed fixes exist to handle a single case: a Bash command whose outcome is unknown. The outcome table, the claim files, the `high-water` counter, the contract version, keyed effects and the `redo` action all serve that case ([canonical specification](../canonical-documents.md#specification), INV-1 *Outcome mapping* and *Parked runs*, INV-2 *Workspace* and *Versioning*). The operator must choose how much of that design version 1 carries before the documents are rebaselined and before Phase 2 is built.

#### Problem

Two readings of version 1 exist and the documents do not choose between them. Phase 2 and Phase 3 cost and risk differ a lot between the two. A rebaseline before the choice would be redone.

#### Scope

Record one decision between the two options below, or a named hybrid.

- Option R, reduced version 1. Any ambiguous Bash outcome parks the run and does not return an unknown outcome to the model. Ambiguous means a timeout, a heartbeat timeout, a lost Worker, an executor error after the claim, a Schedule-To-Start timeout and any unclassified failure after the start. The version drops five items: the `redo` action, keyed effects with the reserved `idempotency_key` field, the claims `high-water` counter with `expected_claim_ordinal`, the `contract_version` integer, and the model facing `OUTCOME_UNKNOWN` message for Bash. It keeps Bash as a claimed effect with one attempt and the claim files, Write and Edit as repeatable effects, the package hash, policy version and engine version checks, the lineage id and the signed token design.
- Option F, the full design in revision 6. Every item in the specification stays, including the six row outcome table, keyed effects, `redo`, both snapshot counters and the contract version.
- The decision record states the effect of the choice on each assumption row. Under option R: A-11, A-45 and A-47 are superseded because keyed effects are not offered, A-23 is superseded because `redo` is not offered, A-10, A-08, A-16, A-21 and A-36 are rewritten to the smaller design, and A-04, A-05, A-06, A-07, A-09, A-13 and A-15 stay with narrower text. Under option F: all rows stay, the open findings R6-02 to R6-07 from the sixth critique stay open work, and DSR-0.8 and DSR-0.10 keep their full scope.
- The record lists the later tickets that option R makes moot or smaller (candidates: DSR-2.5, DSR-2.8, the `redo` part of DSR-3.3, and DSR-0.10).

#### Out of scope

- Editing [canonical specification](../canonical-documents.md#specification) and [canonical plan](../canonical-documents.md#plan). DSR-0.3 does that after this decision.
- The isolation, gateway and Search Attribute decisions, which hold under both options.
- A later widening from option R to option F. The record may note the widening path, and does not build it.

#### Acceptance criteria

- [x] A recorded decision names option R, option F or a hybrid, with the date and the deciding Operator. Proof: the decision record heading and approval provenance.
- [x] The record lists, for every assumption row that the choice touches, one of: stays, rewritten, superseded. Proof: the decision record's assumption disposition table.
- [x] The record states what each choice does to the version 1 guarantee in G4 and S2 (the model is told unknown, or the run parks). Proof: the decision record's G4 and S2 before and after text.
- [x] The record names the operator procedure for a parked ambiguous Bash outcome when `redo` is absent, or states that the procedure is an open question with an owner. Proof: the decision record's open procedure question, owned by the Operator under DSR-0.8.
- [x] The record lists the tickets and Phase 2 and Phase 3 checks that become moot or smaller. Proof: the decision record's affected tickets and checks table.
- [x] The record states that the PASS outcome excludes upstream submission and the harness port (rows A-35 and A-36 close in Phase 7), and that the plan's pre M1 `verify-design` pass is replaced by the Phase 1 real model evidence. Proof: the decision record's PASS boundary.

#### Dependencies and blockers

- No blocker. DSR-0.1 informs the choice, and the operator may decide before DSR-0.1 closes if the outcome does not change the options.
- This ticket blocks DSR-0.3, DSR-0.8 and DSR-0.10, because each of them changes size or becomes moot under option R.

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), INV-1 *Outcome mapping*, *Claimed effect guard* and *Parked runs*; INV-2 *Workspace* and *Versioning*; INV-5; the `Assumptions and risks if wrong` table.
- [canonical plan](../canonical-documents.md#plan), *Verification handoff*, which lists the proposed fixes and the open findings R6-02 to R6-13.
- Documented retry behavior for `maximum_attempts` of 1, evidence row EV-64: https://docs.temporal.io/encyclopedia/retry-policies#default-behavior

#### Open questions

- Operator: does a parked ambiguous Bash outcome let the operator continue with `retry` or `resume_from_checkpoint`, given that the claim file still blocks a second spawn? If not, `abort` is the only action and the record must say so.
- Operator: is a hybrid acceptable, for example option R plus keyed effects only? The specification names no keyed service, so the need is unproven (see DSR-0.10).
- Operator: confirm the PASS scope. The README states that the stated outcome of the PASS verdict excludes upstream submission and the harness port, so rows A-35 and A-36 stay open until Phase 7 and the verdict names them as outside the outcome. A row marked superseded counts as settled.

### DSR-0.3 Rebaseline the specification and plan to the approved version 1 scope

Status: DONE (2026-10-01)

Applied Option R to the specification, plan, manifests and dependent tickets. [The scope record's completion evidence](../proposals/distributed-recovery/2026-10-08/provenance.md#p-001) records the lead gate reruns, original id preservation, 56 row parity, four supersessions and remaining runtime obligations. No product implementation or independent design PASS is claimed.

- Type: Documentation
- Priority: High
- Estimate: 5 points (confidence 60 percent)
- Labels: Type: Documentation, Topic: Assumptions
- Parent: DSR-P0
- Blocked by: DSR-0.2
- Blocks: DSR-1.2
- Related: DSR-0.1, DSR-0.8, DSR-0.10
- Retires: none
- Informs: A-01, A-08, A-10, A-16, A-21, A-23, A-36
- Owner role: Operator

#### Context

[canonical specification](../canonical-documents.md#specification) and [canonical plan](../canonical-documents.md#plan) are at revision 6. Their `Assumptions and risks if wrong` table and the plan's `Assumptions retired by milestone` table carry the same ids. Evidence tables in both documents must match their manifests row for row ([canonical specification](../canonical-documents.md#specification), *Evidence*). After DSR-0.2 approves a scope, the two documents must describe that scope and no other. A document that still describes dropped features gives a later `verify-design` pass false findings and gives Phase 2 builders a wrong target.

#### Problem

The documents describe the full design. If option R is approved, many rows, checks and tables describe work that no longer exists. If option F is approved, the documents still need the answer from DSR-0.1 and the status of the open findings applied.

#### Scope

- Apply the approved option to [canonical specification](../canonical-documents.md#specification) and [canonical plan](../canonical-documents.md#plan). For each affected assumption row, rewrite it or mark its status `superseded`. Keep every id. Never delete a row, because ids are never reused and the ticket checker needs every specification id to stay in the table.
- Keep the dependent text in step: Goals G2 and G4, Scenarios S2 and S8, INV-1 outcome table and parked run actions, INV-2 workspace counters and versioning, INV-5, Interfaces (policy schema, effect input and result, `AgentState` list, run input), Open issues, and the plan's Milestones M1 to M3, its retirement table and its verification handoff.
- Record the answer from DSR-0.1 and the version 1 decisions already taken in Phase 0 (the DSR-0.4 to DSR-0.10 outcomes that exist when this ticket runs).
- Update both evidence manifests and both evidence tables so the evidence gate passes for the specification and for the plan.
- Deliver a list of the tickets that the final scope makes moot, for the operator to mark SUPERSEDED in the ticket index.
- Add the assumption rows that the sixth critique found missing (brief 22, finding R6-08) and correct the severity and ordering mismatches it names, with new ids that continue after A-51 and never reuse one. Apply the PASS scope statement from DSR-0.2: rows A-35 and A-36 stay open decisions outside the stated outcome, and the plan's pre M1 `verify-design` pass is removed. Keep the plan's retirement table in step with every added row.

#### Out of scope

- New design work beyond the approved scope.
- Superseding work beyond the approved Option R decision. The rebaseline may apply that decision to the named moot tickets, but cannot retire other work by inference.
- Independent verification. DSR-6.3 owns that.
- Resolving open findings R6-09 to R6-13 unless the approved scope removes the text they concern. Finding R6-08 is in scope.

#### Acceptance criteria

- [x] The specification and the plan describe only the approved scope. Proof: the dropped feature search recorded in the scope decision's completion evidence finds only superseded mechanisms or historical provenance.
- [x] The specification table and the plan retirement table hold the same assumption ids with the same statuses and milestones. Proof: direct comparison recorded 56 rows, equal order and zero status or milestone set differences.
- [x] Every assumption row has a status from the specification's own vocabulary and a Retire by text that names a milestone that still exists. Proof: both evidence gates and lead table review; M0 through M7 remain in the plan.
- [x] The evidence gate passes for the specification and for the plan after the edits. Proof: the lead reruns recorded in the scope decision show PASS for both manifests.
- [x] No original assumption row is deleted, and every cut row carries the status `superseded` with its id kept. Proof: A-01 through A-51 are present; only A-52 through A-56 extend that set; the scope dispositions match both tables.
- [x] Both evidence gates pass after the rebaseline: the specification gate, and the plan gate run with the `--spec` option. Proof: 129 specification evidence records and 89 plan records pass in the lead reruns.
- [x] The ticket checker still reports no `coverage` error for assumption ids after the edit. Proof: canonical local validator PASS, 67 blocks.
- [x] A list of moot tickets, by id, is attached to the decision record. Proof: DSR-0.10, DSR-2.5, DSR-2.8 and DSR-3.8 are recorded and marked SUPERSEDED.
- [x] Every new assumption row has a plan retirement row and an indexed ticket that lists its id under Retires. Proof: canonical local validator PASS; DSR-0.2 covers A-52/A-55, DSR-2.3 covers A-53/A-54, DSR-4.2 covers A-54 and DSR-3.2/DSR-5.5 cover A-56.

#### Dependencies and blockers

- Blocked by DSR-0.2, which sets the scope.
- Blocks DSR-1.2, because the policy and hook work builds the rebaselined table.

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), *Assumptions and risks if wrong* and *Evidence*; [canonical plan](../canonical-documents.md#plan), *Assumptions retired by milestone* and *Evidence*.
- [canonical plan](../canonical-documents.md#plan), *Verification handoff*, for the open findings that this edit must not hide.
- `tickets/README.md`, *What PASS means here*, items 1 and 2.

#### Open questions

- Operator: when option F is approved, does this ticket also apply the open findings R6-02 to R6-07, or do those stay as Phase 2 work? The estimate assumes they stay.
- The estimate has low confidence because its size depends on the option that DSR-0.2 selects.

### DSR-0.4 Name the budget owner and credentials for real model runs

Status: OPEN

Approved budget separation checkpoint (2026-10-03): see [canonical pointer](../canonical-documents.md), *Approved experiment authorization separation*. Earlier budget gate wording in historical checkpoints is superseded for Phase 1 monitored experiments only. No live run is authorized and strict preventive budgeting remains required at DSR-5.8 final acceptance.

Fresh observation repair checkpoint (2026-10-03): see [canonical pointer](../canonical-documents.md), *Fresh observation repair checkpoint*. Scoped verification changes no budget/provider, billing, headroom, live allocation or Phase 5 acceptance. Reservations and historical control evidence remain preserved; no acceptance box or dependency changes.

No prompt SDK shutdown checkpoint (2026-10-03): see [canonical checkpoint](../canonical-documents.md), *No prompt SDK shutdown checkpoint*. This no input/no credentials probe changes no budget, billing, live allocation or Phase 5 acceptance. Both consumed reservations, historical control verdict and conservative overage stop are preserved.

Host binding checkpoint (2026-10-03): see [canonical host evidence and unchanged budget limits](../canonical-documents.md), *Host binding checkpoint*. This supplies no provider enforcement, billing/headroom, live allocation or Phase 5 evidence. All existing acceptance boxes and consumed reservations remain unchanged; this ticket stays OPEN.

Supported route checkpoint (2026-10-02): see [canonical route and criterion disposition](../canonical-documents.md), *Supported route checkpoint*. The fork owns the substantive findings and next budget/provider decision. No acceptance criterion closes here.

Offline batch checkpoint (2026-10-02): canonical *Confined offline budget batch* evidence and *Real model harness* work item own the separately authorized offline measurements and limits. This decision remains OPEN; planning choices are not live allocations, historical billing stays unverified and neither consumed reservation changes. See [canonical evidence](../canonical-documents.md#evidence).

Planning choices checkpoint (2026-10-02): the operator clarified personal monthly scope and confirmed local proof owner/model/cap change authority and the requested core planning limits. Canonical enforcement *Decision register* and *Exact proposed offline batch* own values and scope; private checkpoints do not duplicate them. Necessary next provider spend is USD 0. Actual billing/headroom, live allocations and Phase 5 remain unresolved, so this decision stays OPEN. No runtime batch or live call is authorized by planning confirmation; strict enforcement, conservative stop and both consumed reservations remain unchanged.

Budget decision preparation checkpoint (2026-10-02): canonical `experiments/budget-enforcement-disposition.md` owns the proposed strict criteria disposition, planning decision register and next scoped offline proof. Monthly scope and owner/limit confirmation were requested; no answer or live permission is inferred. Current source verification identifies accounting normalization gaps, not a new enforcement pass. Billing remains unknown, both reservations consumed and the monitor unchanged. This decision stays OPEN.

Offline ledger checkpoint (2026-10-02): canonical *Offline budget ledger* and *Implemented local storage contract* record the bounded accounting implementation and passing offline checks. They allocate no live spend, establish no monthly headroom and verify no historical billing. Owner/route/model/cap decisions and preventive enforcement remain open; the overage stop and both consumed reservations are unchanged. No further model call is authorized.

Offline overage checkpoint (2026-10-02): canonical *Offline overage metadata disposition* owns pinned input/normalization findings, official current/legacy Enterprise billing distinctions and the outstanding read only manual plan/usage/billing check. The differing flags are internally possible, not proof of zero billing or a verified charge. The unchanged conservative monitor still stops; both reservations are consumed and budget acceptance remains OPEN. No next query or authorization request is inferred from this offline review.

Operator execution checkpoint (2026-10-02): the operator ran the reviewed new exact subscription control invocation once. Canonical *Subscription control query* retains ambiguous overage stop/confirmed removal and successful text completion in the prefix, plus one buffered final result with 378 input/9 output tokens, zero thinking and USD 0.000423 list estimate. This reconciles observed CLI accounting beyond the live host report's unknown result, not actual subscription/extra billing. Both reservations remain consumed. Control outcome is non passing; all budget/aggregate acceptance stays OPEN and no further model invocation is authorized.

Control investigation checkpoint (2026-10-02): canonical *Subscription control investigation* separates measured stream behavior from pinned source interpretation: the CLI output-limit branch allows three continuations separately from API retries and the later maximum-turn guard. A new single-purpose proposal preserves the 64 output setting, prepares streaming triggers and immediate host container removal, and names a distinct future authorization. Independent document review accepts the stated limits, with code/offline review still required. Reactive containment can race further provider admission, cannot reverse tokens or billing and supplies no hard input/total-token/currency/aggregate cap. The previous reservation remains consumed; no new invocation is approved. Budget acceptance and this decision remain OPEN.

Proposal readiness checkpoint (2026-10-02): independent code rereview and lead offline checks passed on canonical probe SHA256 `44754903f656b8c9dd3169a931314f84e8143988fd0473a93c2ab2d01811999e`. The watchdog acceptance race and boolean/whitespace acceptance gaps were corrected. Canonical proposal now carries the exact future invocation, residual provider/billing limits and complete offline receipt. Present it for a new single invocation exception; no approval is inferred from readiness. Old reservation is present and proposed new reservation absent. Currency/token/aggregate acceptance is unchanged.

SDK exception approval/result checkpoint (2026-10-02): the operator replied "do it" to the reviewed exact single SDK text invocation. Its sole host admission failed with an output-limit error; the CLI reported four turns despite one-turn/zero-retry settings. Canonical *Subscription SDK query (2026-10-02)* owns complete typed stream/stderr, control settings, 2,100 input/256 output tokens and USD 0.00338 list estimate. Removal is confirmed and the persistent approval reservation remains consumed. Retrospective totals with the prior isolated connectivity call are USD 0.004001 list estimate, not a phase budget. Currency/token/aggregate acceptance stays unchanged and OPEN; no further model invocation is authorized.

Independent result review checkpoint (2026-10-02): the stream confirms three generated output-limit continuation messages and contradictory overage flags (`isUsingOverage: false`, `overageInUse: true`). Actual extra billing is unverified and no billing setting was changed. The executor retained the event but did not immediately stop on that ambiguous metadata; this stop/control gap must be resolved in a separately reviewed proposal before any new invocation.

Next decision preparation checkpoint (2026-10-02): the canonical fork's `experiments/subscription-test-decision.md` proposes exactly one tools disabled SDK subscription text invocation on the retained immutable image/login volume. It names proposed local owner/readers/model change authority and invocation controls, while explicitly preserving unresolved per run, Phase 1 and Phase 5 currency/token/aggregate acceptance. No hard cap equivalence is claimed; approval would be a single bounded exception only. The prior connectivity approval is consumed and does not authorize this invocation. Independent read only review found no material proposal blocker; mount and wheel provenance clarifications were applied. No model call or credential read occurred during preparation. Decision and execution authorization remain pending.

Inspection checkpoint (2026-10-02): DSR-1.3 deferred checkpoint feasibility passes, but does not authorize paid execution. The operator was asked for the budget owner, credential route/storage/readers, per run and Phase 1 and Phase 5 USD/token limits, exact allowed model identifiers and model list change authority. No values are inferred from the earlier integration approval. This decision remains open until those choices are recorded. DSR-1.1 must separately verify enforcement before any paid call; the canonical *Real model harness* work item records the remaining scope.

Local login preparation checkpoint (2026-10-02): after asking to use normal Enterprise authentication for the local proof, the operator authorized preparation for the next ticket stages. The selected preparation uses the pinned CLI inside a disposable container, with private login state in Docker volume `claude-recovery-proof-login`; the operator performs browser authorization. This is a local proof route, not production app login integration. Anthropic's current Agent SDK subscription notice supports subscription usage; actual entitlement/CLI compatibility, budget owner/readers, model and limits remain unresolved. The original API/currency/token acceptance is preserved; no substitute is approved and no real model execution is authorized. The canonical fork's *Local Enterprise login preparation* guide owns the technical setup.

Login checkpoint (2026-10-02): the operator completed browser authorization. A separate offline status container on the recorded image returned `loggedIn: true`, `authMethod: claude.ai`, `apiProvider: firstParty`. Login state persists in the named volume. No authorization URL/code or account identifier is retained in the evidence. This establishes the local credential route, not organization entitlement, token refresh, model access or approved budget/model limits. DSR-0.4 remains OPEN and no model call was made.

Connectivity proposal checkpoint (2026-10-02): the canonical login preparation guide and `connectivity_plan.py` define a single subscription CLI connectivity check using exact model `claude-haiku-4-5-20251001`, one turn, no tools/skills/MCP, zero retry setting, 64 output token setting and USD 0.05 CLI budget setting. A 60 second outer timeout and container teardown are required at execution. Input-token/USD/aggregate enforcement is not established. The proposed exception needs explicit operator approval; it closes no original budget criterion, changes no billing setting and authorizes no recovery batch. Preparation only has run.

Connectivity approval/result checkpoint (2026-10-02): the operator replied "approve all" to the exact single test proposal. That invocation passed on retained subscription login: exact Haiku model, one reported turn, 406 input/43 output tokens and USD 0.000621 list price estimate. Container removal succeeded and stderr was empty. Canonical *Subscription CLI connectivity (2026-10-02)* owns the full result and limits. This approval is the bounded connectivity exception only; DSR-0.4 stays OPEN, with budget enforcement/phase limits and further model execution authorization unresolved. No recovery batch is inferred from the approval.

- Type: Decision
- Priority: Urgent
- Estimate: 1 point (confidence 85 percent)
- Labels: Type: Decision, Topic: Engine
- Parent: DSR-P0
- Blocked by: none
- Blocks: DSR-5.8
- Related: DSR-1.3
- Retires: none
- Informs: A-02, A-25
- Owner role: Budget owner

#### Context

All engine evidence in the pack comes from a fake model ([canonical specification](../canonical-documents.md#specification), OI-16). Phase 1 runs the engine against a real model. Those runs cost money, and a retry of a model call costs money again. The plan states that a named budget owner and credentials are a gate for M1 ([canonical plan](../canonical-documents.md#plan), M0 decision (f)). An API key is the documented path for a hosted operation, and cloud provider credentials also survive resumed steps ([canonical specification](../canonical-documents.md#specification), N5).

#### Problem

Local planning ownership and model limits are recorded, but final credential access, billing disposition and Phase 5 allocation remain incomplete. These decisions gate final acceptance. A separately approved Phase 1 monitored experiment states its own exact route, allowance and residual risks without requiring this whole ticket to close.

#### Scope

- Name the budget owner for the real model runs of Phase 1 and for the acceptance run in Phase 5.
- Choose the credential type (API key, or the cloud provider path) and name where it is stored and who can read it.
- Record the confirmed Phase 1 planning limits separately from exact scenario authorization and the independent Phase 5 allocation, each in currency and tokens. Strict preventive enforcement remains at final acceptance.
- Name the allowed model identifiers.

#### Out of scope

- Implementing strict provider request/token/currency enforcement. DSR-5.8 owns its proving acceptance; DSR-1.1 owns monitored experiment controls.
- Claude app logins, which the design excludes ([canonical specification](../canonical-documents.md#specification), N5).
- Cost modeling for production use.

#### Acceptance criteria

- [ ] A decision record names the budget owner role holder, the credential type, the storage location and the readers. Proof: the record.
- [ ] The record states the per run cap, the Phase 1 total cap and the Phase 5 acceptance cap, each with a unit. Proof: the three numbers in the record.
- [ ] The record names the allowed model identifiers and states who can change the list. Proof: the record.
- [ ] No credential value appears in the pack, the tickets or the repository. Proof: a pattern search of the pack and of the plugin checkout for the credential prefix returns no match, and the result is attached to the record.
- [ ] The record states what happens when a cap is reached: the run stops and the owner is told, and nobody raises the cap without the owner. Proof: the stated rule in the record.

#### Dependencies and blockers

- No blocker. The Budget owner must exist before the decision can close.
- Blocks DSR-5.8 final acceptance, which requires complete ownership, authentication, billing and allocation decisions. DSR-1.1 may prepare a monitored experiment without this ticket closing, but execution needs a separate exact approval.

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), OI-16 and A-02; [canonical plan](../canonical-documents.md#plan), M0 decision (f).
- Documented credential path, evidence row EV-54: https://code.claude.com/docs/en/agent-sdk/overview

#### Open questions

- Budget owner: which spend code pays for the runs, and does a Bedrock or Vertex credential suit the organization better than an API key?
- Operator: can the credential be shared by the harness and by a later scheduled newest engine job (DSR-5.6), or does that job need its own?

### DSR-0.5 Record the outcome of contacting the community plugin author

Status: DONE (2026-10-05 local)

The [operator scope decision and closure](../proposals/distributed-recovery/2026-10-08/provenance.md#p-009) explicitly removes the integrations ask and confirms the supplied tickets contain all known implementation work. Public contact, verified date/link/text, dated no reply and the rule to proceed in the additive fork satisfy the applicable contact route. No agreed repository split is claimed; future upstream placement remains DSR-7.1. The Slack reply must not be sent.

- Type: Decision
- Priority: High
- Estimate: 1 point (confidence 85 percent)
- Labels: Type: Decision, Topic: Assumptions
- Parent: DSR-P0
- Blocked by: none
- Blocks: DSR-1.2
- Related: DSR-0.2, DSR-7.1
- Retires: A-35 (first half)
- Informs: A-36
- Owner role: Operator

#### Context

An open issue on `temporalio/ai-integrations` proposes the same plugin as the pinned fork. The issue had no comments when read on 2026-09-29 ([canonical specification](../canonical-documents.md#specification), OI-9). A maintainer of the agent harness set an entry gate: the integration must land in `ai-integrations` first ([canonical specification](../canonical-documents.md#specification), Background). The plan says that the author of the issue is contacted before code is written, and that the public API stays additive ([canonical plan](../canonical-documents.md#plan), Constraints). Another company may also build the same integration (OI-14).

#### Problem

Public contact has happened. The operator removed the remaining integrations ask because the supplied ticket set contains all known implementation work. The dated no-reply route satisfies the retained M1 coordination gate under that scope decision. The known author's implementation still requires coordination before upstream submission; no author agreement is inferred.

#### Scope

- Post one comment on the public issue that states the intended additions and asks the author which additions go to which repository.
- The integrations channel ask (OI-14) is removed by the recorded operator decision; the supplied ticket/source set is the complete known inventory. No Slack message is required or authorized now.
- Record the reply, or record the absence of a reply with the date, and record the agreed split of additions between repositories.

#### Out of scope

- Writing upstream pull requests. DSR-7.1 owns those.
- Any change to the plugin API.

#### Acceptance criteria

- [x] A decision record holds the date of the contact and a link to the comment. Proof: the link resolves to the comment. [Verified contact](../proposals/distributed-recovery/2026-10-08/provenance.md#p-009), posted 2026-10-05 local / 2026-10-06 UTC.
- [x] The posted comment carries no workspace identifier, no internal ticket identifier, no named internal person and no customer name. Proof: a reviewer reads the posted text before it is sent and records the check. Exact approved text reviewed before send and read back unchanged; the contact outcome records the check.
- [x] If the author replies, the record lists each planned addition with the agreed repository. Proof: the list in the record. Not applicable to the observed no-reply branch; the closure record explicitly states no agreement exists. This disposition does not assert an agreed split.
- [x] If no reply arrives, the record states the date of the last check and the rule that follows (proceed in the fork under an additive API, or wait). Proof: the dated record. Last observed check 2026-10-06T02:16:10Z; proceed in the additive fork under the recorded operator scope decision. No further reply check is claimed.
- [x] The record states whether another implementation exists, with the evidence or the statement "no reply". Proof: the record. The known issue author's 2026-10-01 plan demonstrates overlap; the operator confirms the supplied tickets contain all known work and removes the additional channel ask. That existing plan is not a reply to this contact or an agreed split.

#### Dependencies and blockers

- No remaining blocker. The DSR-1.2 prerequisite is satisfied through posted public contact, dated absence and the operator's explicit removal of the channel scope. The dependency edge is retained as satisfied, not deleted or moved. The untriggered reply branch does not require a fabricated agreement.

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), OI-9, OI-14 and A-35; [canonical plan](../canonical-documents.md#plan), Constraints and M0 decision (b).
- Public issue, evidence row EV-4: https://github.com/temporalio/ai-integrations/issues/31

#### Open questions

- Resolved: proceed in the additive fork under the recorded operator decision; no fixed waiting period remains a local construction prerequisite. Future upstream agreement remains DSR-7.1.
- The second half of A-35 (upstream pull requests as agreed) is retired in DSR-7.1.

### DSR-0.6 Decide the workspace volume class and the effect isolation level

Status: OPEN

October 9 collaboration: [the accepted division of work and proposed interfaces](../proposals/distributed-recovery/2026-10-08/priority-sweep/coverage.md#october-9-collaboration-agreement) establish coordination, not storage adoption or qualified checkpoint restoration. Reconcile checkpoint acceptance/restore ordering with the canonical volume and retained claims before approving the applicable choices. DSR-2.1 remains blocked; a disconnected live Worker remains explicitly unqualified.

October 9 source reconciliation: [the maintained release-check comparison](../proposals/distributed-recovery/2026-10-08/priority-sweep/coverage.md#october-9-release-check-reconciliation) reports improved native recovery but explicitly no workspace snapshot/failover. Conversation and Worker-kill evidence do not settle volume semantics or old-execution termination. The prepared storage/isolation recommendation, owner choices and DSR-2.1 blocker remain unchanged.

Decision preparation (2026-10-09): [the maintained recommendation](../proposals/distributed-recovery/2026-10-08/dsr-0.6-preparation.md) proposes the bounded canonical shared-volume/container qualification target, compares cold restoration and independent authority, separates surviving-host replacement from host loss and partition, and maps the six owner decisions and smallest experiments. Its [independent review](../proposals/distributed-recovery/2026-10-08/dsr-0.6-review.md) verifies preparation only. No choice, role holder, acceptance checkbox or runtime guarantee is approved. DSR-2.1 remains blocked. Historical discovery paragraphs below retain their dates and source inventories.

- Type: Decision
- Priority: High
- Estimate: 3 points (confidence 70 percent)
- Labels: Type: Decision, Topic: Workspace, Topic: Effects
- Parent: DSR-P0
- Blocked by: none
- Blocks: DSR-2.1, DSR-4.1
- Related: DSR-4.3
- Retires: none
- Informs: A-17, A-27, A-37, A-48
- Owner role: Security owner

#### Context

Version 1 needs a shared volume that every segment and effect Worker mounts at one absolute path. Cross host behavior is untested ([canonical specification](../canonical-documents.md#specification), OI-2 and A-27). The claimed effect guard relies on an exclusive create of a claim file that must be atomic and visible on every host (A-48). Bash runs scripts from a skill. Without a separate operating system user, a container or a PID namespace, Bash can read the Worker launch environment, write the package copy and leave a child process that survives (OI-6, A-17). Until the isolation level is decided, every confinement claim and the at most one spawn guarantee are void (A-17 risk text).

**Complete Issue 31 disposition (2026-10-08)**

October 8 full issue sweep: [complete proof map](../proposals/distributed-recovery/2026-10-08/priority-sweep/coverage.md) owns I31-H4/H5 and the backend comparison. Proposed cold object/sandbox recovery remains outside canonical v1 shared-volume proof until BD-6 adoption. Docker cloud sbx volume exit snapshots and concurrent overwrite require a durable publication receipt and crash-before-exit test; E2B refused pause must prevent takeover, and nontransactional FUSE mounts cannot inherit claim semantics. Wrong backend assumptions lose accepted workspace or permit two actors. DSR-4.3 owns the physical proof after selection. No choice or acceptance box closes.

#### Problem

Neither the volume class nor the isolation level has an owner or a decision. Phase 2 builds the workspace and the executor on both, and Phase 4 builds the isolation.

#### Scope

- Choose the volume class for version 1 and state its required semantics (POSIX behavior, close to open consistency, one user and group mapping on every host).
- Decide how cross host behavior is covered: a two container rig over a real network file system in Phase 4, or a declared untested limit in the README.
- Choose the isolation level for effects: a separate unprivileged user plus a subreaper (the stated version 1 minimum), a container or PID namespace with a restricted `/proc`, or a microVM per run.
- Name the Security owner for the isolation level.
- State the interim wording the specification may use for confinement claims until Phase 4 proves the level.

#### Out of scope

- Building the volume layout, the executor or the isolation. DSR-2.1 and DSR-4.1 own those.
- The retention value (A-37) and the production session store (A-38). They need an owner too (see Open questions).
- Cross host tests. DSR-4.3 owns those.

#### Acceptance criteria

- [ ] A decision record names the volume class and its required semantics. Proof: the record.
- [ ] The record chooses between the two container rig and the declared untested limit, and names who builds the rig if chosen. Proof: the record.
- [ ] The record names the isolation level and the Security owner role holder. Proof: the record.
- [ ] For each choice the record states which assumption rows it affects (A-17, A-27, A-48 and A-37) and what claim the specification may make until Phase 4. Proof: a sentence per row.
- [ ] The record states a failure boundary: if the chosen volume cannot give atomic exclusive create and preserve protected claims, claimed execution refuses and the volume class must be changed and qualified. A replacement authority needs a separately approved contract revision and proof; dropping the guard while offering claimed Bash is forbidden. Proof: the stated rule, checked against the canonical protected-claim contract.

#### Dependencies and blockers

- No blocker. The Security owner must be available.
- Blocks DSR-2.1 (workspace preparation) and DSR-4.1 (isolation build).

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), OI-2, OI-6, INV-2 *Workspace* and INV-7; A-17, A-27, A-37 and A-48.
- [canonical plan](../canonical-documents.md#plan), M0 decisions (c) and (g).
- Worker Specific Task Queue and shared storage trade off, evidence row EV-72: https://docs.temporal.io/best-practices/worker#separate-task-queues-logically

**Discovery reference (2026-10-07)**

Decision preparation is retained in the private historical October 7 discovery archive. The [package README](../proposals/distributed-recovery/2026-10-08/provenance.md#p-010) inventories the work; the [synthesis](../proposals/distributed-recovery/2026-10-08/provenance.md#p-011) owns the recommendation and disagreement resolution. This ticket owns the reference because the discovery informs its volume, isolation and cross host failure choices.

Produced on disk:

- Four independent reports, source ledgers and cross challenges in `agent-a/` through `agent-d/`, covering durable storage, managed sandboxes, self managed VM isolation, and confidential/adversarial recovery.
- [Candidate specification](../proposals/distributed-recovery/2026-10-08/provenance.md#p-012) and [candidate plan](../proposals/distributed-recovery/2026-10-08/provenance.md#p-013), with `evidence.json` and `plan-evidence.json`, eleven additive assumptions and six open owner decisions.
- [Independent verification report](../proposals/distributed-recovery/2026-10-08/provenance.md#p-014), two fresh reviewer reports, the Temporal domain critique, `verification-manifest.json`, source/documentation captures, and preservation/final check records in `verification/`.
- [Frozen candidate snapshot](../proposals/distributed-recovery/2026-10-08/provenance.md#p-015) in the private historical archive, with the original source pin and Temporal source inventories/digests.

Discovery is complete; candidate verification is CONDITIONAL with no unresolved material core or remedy findings. Document gates passed. Distributed runtime qualification remains unexecuted. This reference does not adopt a storage class, isolation level or protocol extension, name an owner, authorize implementation or close an acceptance criterion. DSR-0.6 remains OPEN. Retention/session store decisions remain owned by DSR-0.11; cross host test implementation remains owned by DSR-4.3.

**Mods discovery continuation reference (2026-10-08)**

The operator authorized a complete copy in the private October 8 discovery archive and additional Mods discovery and review. The original October 7 folder remains unchanged. [Copy provenance](../proposals/distributed-recovery/2026-10-08/provenance.md#p-016) binds its 39 original files; the [package README](../proposals/distributed-recovery/2026-10-08/README.md) inventories the continuation and the [Mods synthesis](../proposals/distributed-recovery/2026-10-08/mods-synthesis.md) owns its recommendation.

Produced on disk: three independent Mods surface/composition/adversarial reports, source captures and cross challenges in `mods-research/`; revised [candidate specification](../proposals/distributed-recovery/2026-10-08/candidate/spec.md), [candidate plan](../proposals/distributed-recovery/2026-10-08/candidate/plan.md) and both JSON evidence manifests; two fresh review reports, the applied Temporal domain critique and [verification result](../proposals/distributed-recovery/2026-10-08/provenance.md#p-017); and the [frozen October 8 snapshot](../proposals/distributed-recovery/2026-10-08/provenance.md#p-018). The candidate has 31 evidence rows, 15 additive assumptions and six open owner decisions. New full pass 2 met its exit test with no unresolved material core/remedy finding; verdict remains CONDITIONAL. The 14 dirty reference source hashes remain unchanged.

The new scope considers optional observation, native original pending/result projection and exploratory complete model response capture. Actual SDK loading, emitted runtime contract, independent prevention, native suspension/mapping and distributed runtime proof remain unexecuted. Historical Mods loading failure and current recovery/minimum dispositions are preserved. This reference does not choose a newer runtime, platform, storage class, owner or optional lane, authorize implementation/execution or close an acceptance box. DSR-0.6 remains OPEN; completed Phase 1 tickets are not reopened.

**Temporal and storage research continuation reference (2026-10-08)**

Further operator-authorized discovery is recorded in the private October 8 storage discovery archive. Produced on disk: three independent Temporal/session, workspace substrate and dispatch/termination reports and source captures; [reconciled recipe](../proposals/distributed-recovery/2026-10-08/storage-loop/synthesis.md); revised four candidate files; two fresh full reviews and applied Temporal domain critique in [verification report](../proposals/distributed-recovery/2026-10-08/storage-loop/verification/report.md); and [frozen storage revision](../proposals/distributed-recovery/2026-10-08/provenance.md#p-019).

The candidate now has 41 evidence rows, preserving the original 31 source objects, the same 15 additive assumption IDs and six open owner decisions. Full pass 3 met its source-review exit test with zero unresolved material core/remedy findings; verdict remains CONDITIONAL. The referenced synthesis owns the technical recommendation. The preceding Mods reference describes its preserved checkpoint, not the later revision's verification.

This reference does not adopt cold restoration, reattachment, Temporal entity authority or a SQL store. Canonical v1 shared volume/claims remain implementation authority until approved adoption. DSR-0.11 owns conversation store/retention decisions; DSR-4.3 owns actual cross-host qualification. No acceptance box, ticket status, canonical requirement, version floor, runtime disposition or execution authorization changes. DSR-0.6 remains OPEN. The next action is BD-6 review of a bounded Temporal head, immutable bundle and independently retained entity ledger prototype scope.

#### Open questions

- Security owner: which of the three isolation levels does the first customer facing use need? Version 1 minimum is the separate user.
- Operator: DSR-0.11 owns naming the retention value (A-37, OI-10) and session store requirement (A-38) owners. Its decision must remain consistent with this deployment storage/isolation choice.
- Official sample repositories were not inspected, so any claim about a reference volume setup would need one.

### DSR-0.7 Name the owner of the approval gateway

Status: OPEN

- Type: Decision
- Priority: High
- Estimate: 1 point (confidence 85 percent)
- Labels: Type: Decision, Topic: Approvals
- Parent: DSR-P0
- Blocked by: none
- Blocks: DSR-3.2
- Related: DSR-3.4
- Retires: A-14 (owner half)
- Informs: A-12, A-13, A-33, A-34
- Owner role: Gateway owner

#### Context

The design accepts human answers only through Updates that carry a signed token. The documentation read for the pack shows no way for an Update validator to read an authenticated caller identity ([canonical specification](../canonical-documents.md#specification), OI-11 and A-14). The design therefore uses one gateway that holds the only credentials able to send Updates and that signs each decision (INV-7). Nobody owns the gateway today. A pending decision must be found by the gateway through the Query and the `AgentPhase` Search Attribute, because live output is off by default (Interfaces, *Events*).

#### Problem

A security boundary of the design has no owner. The signature scheme, the key set, the minimum token version and the retry behavior need one accountable party before Phase 3 builds the verifier.

#### Scope

- Name the Gateway owner.
- Record what the gateway must do: hold the only credentials that can send approval, answer and resume Updates; sign each decision; manage the public key set with key ids and a minimum token version; discover pending decisions through the Query and the Search Attribute; retry an Update that fails with `RESOURCE_EXHAUSTED`.
- Record the implementation language of the gateway, because the canonical JSON digest must agree across languages ([canonical plan](../canonical-documents.md#plan), M3 checks).
- Record how the deployment prevents any other caller from sending those Updates.

#### Out of scope

- Writing the gateway or the verifier. DSR-3.2 owns the verifier. The gateway build is a deployment task outside this ticket set.
- Choosing a signature algorithm beyond what the specification states.

#### Acceptance criteria

- [ ] A decision record names the Gateway owner role holder. Proof: the record.
- [ ] The record lists the gateway responsibilities named in the Scope with an accountable party for key rotation and for the minimum token version. Proof: the list in the record.
- [ ] The record states the control that stops any other caller from sending the three Updates, or states that the control is an open question with an owner. Proof: the stated control.
- [ ] The record names the gateway implementation language. Proof: the record.
- [ ] The record states what happens when the gateway is down: pending decisions wait until their deadline and then expire with the stated no answer result. Proof: the stated rule matching [canonical specification](../canonical-documents.md#specification) S4.

#### Dependencies and blockers

- No blocker.
- Blocks DSR-3.2, which builds token verification in an interceptor.

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), OI-11, A-12, A-13, A-14, A-33, A-34; INV-7; Interfaces *Workflow messages* and *Events*.
- Updates and Signals guidance, evidence row EV-90: https://docs.temporal.io/encyclopedia/workflow-message-passing

#### Open questions

- Gateway owner: is an existing internal service the gateway, or does a new one need building?
- Operator: who holds the signing keys during a pilot with no gateway team?

### DSR-0.8 Decide how a Workflow reset is detected and handled

Status: OPEN

DSR-0.2 approved Option R and excluded `redo` and keyed external service effects. The reset detection method and safe operator procedure remain open. No claim clearing, repeated Bash or model resumption is authorized for unresolved Bash uncertainty.

- Type: Decision
- Priority: High
- Estimate: 3 points (confidence 65 percent)
- Labels: Type: Decision, Topic: Effects, Topic: Workspace
- Parent: DSR-P0
- Blocked by: DSR-0.2
- Blocks: DSR-3.3, DSR-3.5, DSR-3.8
- Related: DSR-0.3, DSR-0.10
- Retires: none
- Informs: A-05, A-06, A-07, A-23
- Owner role: Operator

#### Context

A Workflow reset can replay effects after the reset point. The approved design preserves the lineage id, run directory, key claims and ordinal claims. An existing claim refuses another Bash spawn and parks the run without returning an unknown result to the model ([canonical specification](../canonical-documents.md#specification), OI-17 and INV-1 *Claimed effect guard*). A reset to the first Workflow Task may mint a new lineage unless the starter supplies the id (A-07). A changed `workflow_run_id` in a claim identifies an earlier run of the lineage, but does not by itself distinguish reset from Continue-As-New. Manifest generation checks do not detect every snapshot taken mid run, so restoration cannot be assumed safe. The plan lists decision (h) as how reset is detected and handled for a run that has claimed effects ([canonical plan](../canonical-documents.md#plan), M0).

#### Problem

The reset detection method and the operator procedure for an ambiguous Bash park are not decided. Phase 3 builds the affected recovery actions and reset tests on this decision. DSR-0.2 already excludes `redo`; an existing claim prevents another spawn but does not establish the earlier outcome or authorize continuation.

#### Scope

- Decide how reset is detected without treating the `workflow_run_id` stored in each claim file as sufficient to distinguish reset from Continue-As-New.
- Write the operator runbook outline for a reset of a run with claimed effects: investigate the earlier outcome and any surviving process, establish workspace and claim integrity, and state which signed action, if any, is safe for the cause. Disclose the undetected mid run snapshot limitation.
- Keep `redo`, `release_claim` and keyed external service recovery outside version 1, as approved in DSR-0.2. Decide whether signed `retry` or `resume_from_checkpoint` can safely resolve an ambiguous Bash park with claims preserved, or whether only `abort` is supported for that cause. Until settled and tested, block continuation that bypasses the uncertainty.
- Decide whether the starter mints the lineage id (A-07) and who guarantees its uniqueness.

#### Out of scope

- Building retained detection and recovery actions or reset tests. DSR-3.3 and DSR-3.5 own those.
- Reintroducing `redo`, claim release or keyed external service effects. A later scope approval is required.
- Reset of runs with no claimed effect.

#### Acceptance criteria

- [ ] A decision record states the detection method for a reset and the signal an operator sees, without treating a changed claim Run Id alone as reset proof. Proof: the record names the evidence and the Query or Search Attribute that shows it, with a check that distinguishes reset from Continue-As-New.
- [ ] The record holds the operator runbook outline with ordered steps for a reset of a run that has claimed effects, including earlier outcome investigation, surviving process handling, workspace and claim integrity, and the undetected mid run snapshot limitation. Proof: the numbered outline.
- [ ] The record cites DSR-0.2's exclusion of `redo`, `release_claim` and keyed external service recovery. It states which signed actions, if any, safely resolve an ambiguous Bash park without bypassing unresolved uncertainty or authorizing another spawn. Proof: the cited scope record and explicit action rules; no recovery choice is inferred from scope approval.
- [ ] The record states whether the starter mints the lineage id and who keeps it unique. Proof: the record.
- [ ] The record states that missing or unverified workspace and claim integrity parks or blocks the run with the cause named, rather than treating a restored tree as safe by default. Proof: the stated rule consistent with the manifest generation limitation in [canonical specification](../canonical-documents.md#specification).

#### Dependencies and blockers

- DSR-0.2 is DONE and supplies the approved Option R scope. The Operator's reset and ambiguous Bash recovery procedure remains open.
- Blocks DSR-3.3 (parking and resume actions) and DSR-3.5 (reset tests).

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), OI-17, A-05, A-06, A-07, A-23; INV-1 *Claimed effect guard* and *Parked runs*.
- [canonical plan](../canonical-documents.md#plan), Constraints *Reset* and M0 decision (h).
- [DSR-0.2 approved scope](../proposals/distributed-recovery/2026-10-08/provenance.md#p-001), *Parked ambiguous Bash procedure*.
- Workflow Id reuse and conflict policy, evidence row EV-82: https://docs.temporal.io/workflow-execution/workflowid-runid#workflow-id-reuse-policy

#### Open questions

- Operator: who restores the workspace after a reset, and from which snapshot?
- Operator: which signed actions, if any, can resolve an ambiguous Bash park with claims preserved and the external outcome or surviving process established? Until decided and tested, continuation remains blocked.
- Plugin engineer: which evidence distinguishes reset from Continue-As-New, given that a different stored claim Run Id alone identifies only an earlier run of the lineage?
- Plugin engineer: does a reset to the first Workflow Task replay the starter supplied id? DSR-3.5 proves it, and the decision here only chooses the design.
- The reset reproduction described in the specification rests on the SDK source and a relayed statement. Official sample repositories were not inspected.

### DSR-0.9 Name who registers Search Attributes and who owns rollout order

Status: OPEN

- Type: Decision
- Priority: High
- Estimate: 2 points (confidence 75 percent)
- Labels: Type: Decision, Topic: Versioning
- Parent: DSR-P0
- Blocked by: none
- Blocks: DSR-3.4, DSR-5.1
- Related: DSR-0.7
- Retires: none
- Informs: A-16, A-30, A-32, A-50
- Owner role: Operator

#### Context

The design upserts Search Attributes such as `AgentPhase` and `OldestPendingAt`. An upsert of an unregistered attribute fails the Workflow Task, and the task retries, so a run can stall silently ([canonical specification](../canonical-documents.md#specification), Interfaces *Events*, A-32; relayed from a public issue). The design also needs Workers for all three queues in every pinned version, and a drain rule that stops an effect running on different code (INV-2 *Versioning*, A-16, A-50).

#### Problem

No owner registers the attributes in each namespace before the first run, and no owner controls the order in which Workers and Workflows roll out.

#### Scope

- Name who registers the Search Attributes in every namespace and when, and list the attributes with their types.
- Name the owner of the rollout order: Workers for all three queues before any Workflow moves, and the single drain rule (drain a version on a queue only when the server reports no pinned run and the operator confirms every waiting run upgraded).
- Record whether Worker Versioning is deployed in the target namespaces (A-50).

#### Out of scope

- The start check that refuses a namespace without the attributes. DSR-3.4 builds it.
- The Worker Deployment guidance and tests. DSR-5.1 owns them.

#### Acceptance criteria

- [ ] A decision record names the registrant role holder and lists each Search Attribute with its type. Proof: the record.
- [ ] The record states the registration timing: before the first run in each namespace, and by which procedure. Proof: the stated procedure.
- [ ] The record names the owner of the rollout order and quotes the rollout rule and the drain rule. Proof: the record.
- [ ] The record states whether Worker Versioning is deployed in each target namespace, or lists the namespaces where it is unknown. Proof: the list.
- [ ] The record states a failure boundary: what the plugin does when the registration is missing (the start check refuses the start with a stated error). Proof: a sentence that cites A-32.

#### Dependencies and blockers

- No blocker.
- Blocks DSR-3.4 (start check and pending decision discovery) and DSR-5.1 (Worker Deployment rollout and drain).

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), Interfaces *Events*; INV-2 *Versioning*; A-16, A-30, A-32, A-50.
- Search Attributes are not encrypted and need registering, evidence row EV-87: https://docs.temporal.io/search-attribute
- Worker Versioning behaviors, evidence row EV-70: https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning#choosing-behavior

#### Open questions

- Operator: who administers the target namespaces, and can the registrant be that same person?
- The claim that an unregistered upsert stalls the Workflow Task is relayed from a public issue. A reproduction is part of DSR-3.4.

### DSR-0.10 Record the idempotency key retention window of each keyed service

Status: SUPERSEDED

Scope disposition (2026-10-01): DSR-0.2 approved Option R. No keyed external service is offered in version 1, so no retention decision is required. The historical body below is not active work; its links remain for decision coverage.

- Type: Decision
- Priority: High
- Estimate: 2 points (confidence 70 percent)
- Labels: Type: Decision, Topic: Effects
- Parent: DSR-P0
- Blocked by: DSR-0.2
- Blocks: DSR-2.5
- Related: DSR-0.8, DSR-0.3
- Retires: none
- Informs: A-11, A-45
- Owner role: Tool author

#### Context

A keyed effect passes its effect key to an external service in the reserved `idempotency_key` field, and the service enforces the key. The retry horizon of the tool must stay inside the service's key retention window. That rule is an inference of the design, not a documented fact ([canonical specification](../canonical-documents.md#specification), INV-1 *Effect Activities*, A-45). A park that outlasts the retention window also makes a keyed `redo` unsafe ([canonical plan](../canonical-documents.md#plan), Verification handoff, finding R6-06).

#### Problem

The specification names no keyed service and no retention window. Without the window, the Schedule-To-Close bound of each keyed tool has no safe value.

#### Scope

- List each keyed service that the first deployment uses, or record that none is in scope.
- Record the idempotency key retention window of each service, with its source (a quoted document or a measurement).
- Record for each keyed tool a Schedule-To-Close value that stays below its window.
- If option R is approved in DSR-0.2, record that keyed effects are out of version 1 and mark this ticket superseded.

#### Out of scope

- Building keyed tools or the effect executor. DSR-2.5 does that.
- Choosing a service on behalf of the tool author.

#### Acceptance criteria

- [ ] The record lists each keyed service, or states that no keyed service is in scope. Proof: the list or the statement.
- [ ] For each listed service the record states the retention window and its source. Proof: a quoted sentence or a measurement log reference.
- [ ] For each keyed tool the record sets a Schedule-To-Close value below the window and states the margin. Proof: the value and window side by side in a table.
- [ ] The record states what happens when a window is unknown: the tool is treated as a claimed effect with one attempt. Proof: the stated rule, matching [canonical specification](../canonical-documents.md#specification) INV-1.
- [ ] If DSR-0.2 selects option R, the record states that the ticket is superseded and the Status line is changed to SUPERSEDED. Proof: the Status line.

#### Dependencies and blockers

- Blocked by DSR-0.2. The scope decision decides whether keyed services exist in version 1.
- Blocks DSR-2.5, which sets each keyed tool policy entry.

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), INV-1 *Effect Activities*, A-11 and A-45.
- Retry Policy and Schedule-To-Close guidance, evidence row EV-64: https://docs.temporal.io/encyclopedia/retry-policies#default-behavior
- Activities are at least once, evidence row EV-81: https://docs.temporal.io/develop/python/best-practices/error-handling#make-activities-idempotent

#### Open questions

- Tool author: which keyed services will the first tools call? The specification names none.
- Tool author: does a service document its key retention? If not, a measurement is needed and the estimate rises.
- Official sample repositories were not inspected, and a claim about a reference keyed tool would need one.

### DSR-0.11 Name the owners of namespace retention and the session store requirement

Status: OPEN

- Type: Decision
- Priority: High
- Estimate: 1 point (confidence 80 percent)
- Labels: Type: Decision, Topic: Workspace
- Parent: DSR-P0
- Blocked by: none
- Blocks: DSR-4.2, DSR-5.4
- Related: DSR-0.6
- Retires: none
- Informs: A-37, A-38
- Owner role: Operator

#### Context

The plan's decision (g) covers the security owner, the isolation level, the retention value and the session store requirement. DSR-0.6 covers the isolation level and the volume. The rest has no ticket ([canonical plan](../canonical-documents.md#plan), M0 decision (g); [canonical specification](../canonical-documents.md#specification), OI-10, A-37, A-38). The specification assumes a namespace retention of 7 days and says the deployment owner sets the real value. The janitor keeps claim files until retention ends, so the value affects how long a reset stays safe. The session store holds the transcript with every tool input and result, so a production store must be shared by every Worker, encrypted at rest and deduplicate by `uuid`.

**Complete Issue 31 disposition (2026-10-08)**

October 8 full issue sweep: [complete proof map](../proposals/distributed-recovery/2026-10-08/priority-sweep/coverage.md) separates accepted conversation authority, payload offload, workspace and effect admission. Proposed Workflow deltas/immutable references or transactional shared SessionStore require exact conditional append, conflicting UUID rejection, replacement reconstruction and retained live/reset references. This decision must name backend, encryption/key and lifecycle owners. Query reads do not persist state. A wrong retention choice makes an accepted session unrecoverable. DSR-5.4 owns conformance; DSR-2.7 owns External Storage payload lifecycle. No store is selected.

#### Problem

Nobody owns the retention value or the session store requirement. Phase 4 builds the janitor on the first, and Phase 5 tests the second.

#### Scope

- Name the owner of the namespace retention value and record the value, or record that the 7 day assumption stands until the owner sets another.
- Name the owner of the production session store requirement and record the three requirements: shared by every Worker, encrypted at rest, deduplicating by `uuid`.
- Record the compliance input that sets the retention value, or state that it is unknown.

#### Out of scope

- Building the janitor or the conformance test. DSR-4.2 and DSR-5.4 own those.
- Choosing a session store product.

#### Acceptance criteria

- [ ] A decision record names the retention owner role holder and states the retention value or the open assumption with a date to settle it. Proof: the record.
- [ ] The record names the session store owner and lists the three requirements. Proof: the record.
- [ ] The record states what the janitor does when the retention value is unknown: it keeps claim files and does not remove them. Proof: the stated rule.
- [ ] The record states the consequence of a store that loses writes: the run stalls with retries and does not lose a decision silently. Proof: a sentence that cites A-38.

#### Dependencies and blockers

- No blocker.
- Related to DSR-0.6, which covers the rest of decision (g), and to DSR-4.2 and DSR-5.4, which use these answers.

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), OI-10, A-37, A-38; INV-2 *Workspace*; INV-7.
- Namespace retention, evidence row EV-88: https://docs.temporal.io/evaluate/cloud/limits#default-retention-period

#### Open questions

- Operator: which compliance requirement applies to the first deployment?
- Operator: is the session store a shared service that already exists?

### DSR-0.12 Decide which recovery integration the next implementation uses

Status: DONE (2026-10-02, Phase 1 proof target selection)

Approved decision checkpoint (2026-10-02): the Operator replied "yes" to selecting experimental main recovery as the Phase 1 proof target and assigning missing comparison proofs to their named gates. The canonical fork decision records exact pins, main/default transport/serial recovery limits, unchanged external effect Activity placement and all three state/host responsibilities. Mods is rejected for the tested invocation. DSR-1.10 closes as bounded research only; A-58/A-59 and production acceptance remain open. DSR-1.3 criterion rebaseline and actual deferred checkpoint feasibility execute next. DSR-1.1/DSR-0.4 still gate real model calls; DSR-1.9 still gates Phase 2. No production candidate adoption, dependency promotion, paid execution, executor implementation, external contact, commit or push is approved.

Historical proposal before approval:

Reviewable decision proposal (2026-10-02): use the fork's canonical `comparison-disposition.md`, *Options and recommendation*, *Version and API boundary*, *Responsibilities and unresolved production work* and *Next proof and result delivery criterion changes*. Proposed choice: adopt experimental main recovery only as the Phase 1 proof target, with default SDK transport, main agent and serial original request recovery, mandatory host ownership/containment/state/decision controls, and no offered production route. Reject Mods for the tested invocation; keep defer as unchanged baseline/rollback pending approval. This choice advances the measured exact pending call seam rather than repeating the baseline recommendation; it does not combine released native Edit and experimental MCP proofs into complete durable skill support. DSR-1.10 closure additionally needs approval of its explicit proof deferrals; comparison cannot close unchanged. After that decision, DSR-1.3 criterion/fixture rebaseline executes next, with DSR-1.1 and DSR-0.4 still blocking paid runs. DSR-1.9 remains the mandatory Phase 2 gate. Deployment/storage responsibilities refer to DSR-0.6 and DSR-0.11; gateway ownership remains DSR-0.7. No approval, dependency promotion, scope change, executor implementation or paid call is inferred from this proposal.

Decision checkpoint (2026-10-02): comparison evidence is recorded in fork commit `6d220335ff614e96115cb9ee1048a27d4f9b65d4`; see DSR-1.10 in `phase-1.md` for verification and remaining scope. The Operator authorized committing the research, not adopting a candidate or implementing a general executor. Retaining defer describes the unchanged baseline pending this decision, not a finding that defer is technically superior. The experimental SDK offers a promising recovery seam with measured local host adapters; full durable native skill execution and production host contracts remain unproved. DSR-0.12 remains OPEN and acceptance criteria remain unchanged. No push occurred.

Second host batch recommendation (2026-10-01): retain defer as baseline and keep general executor entry blocked. The canonical second host comparison provides measured local adapters for exclusive admission through teardown, controlled owned-process containment, actual Bash durable uncertainty parking with selected missing-state refusals, and disposable signed request binding through replacements. These strengthen the experimental SDK candidate but do not grant adoption. Accounting alone allowed orphan continuation, explicit cryptography passthrough constrains signing proof, and distributed deployment fencing, production supervision, filesystem/claims restoration, signed gateway/registration and full native skill/permission coverage remain unresolved. Independent review and lead reruns are recorded in canonical evidence. DSR-1.10 stays IN PROGRESS; DSR-0.12 stays OPEN, with acceptance unchanged and no Operator adoption choice inferred.

- Type: Decision
- Priority: Urgent
- Estimate: 1 point (confidence 75 percent)
- Labels: Type: Decision, Topic: Engine
- Parent: DSR-P0
- Blocked by: DSR-1.10
- Blocks: DSR-1.3, DSR-1.9
- Related: DSR-0.6, DSR-0.11
- Retires: none
- Informs: A-57, A-58, A-59
- Owner role: Operator

#### Context

The current implementation keeps the approved defer and synthetic result integration. The hybrid long running CLI and experimental SDK main agent recovery path is the first research priority; the current implementation is the comparison baseline and Mods are candidate interception. This priority is not adoption. DSR-1.10 supplies a bounded comparison before Phase 2. This decision owns BD-10 in the specification.

Incoming recommendation (2026-10-01): the bounded existing dependency comparison is in the [canonical evidence](../canonical-documents.md#evidence). It recommends retaining defer as baseline with executor entry blocked, rejecting Mods for the tested SDK invocation and deferring experimental adoption pending an isolated dependency proposal and host recovery proof. The released SDK native file replay route remains unexecuted. DSR-1.10 remains IN PROGRESS and this decision remains OPEN; the recommendation is not an Operator choice and closes no adoption criterion.

Follow-up recommendation (2026-10-01): the [canonical evidence](../canonical-documents.md#evidence) now includes passing bounded native file replay cases and an exact experimental SDK dependency proposal. Published outcomes were reused, while an unpublished mutation required restoring a one file snapshot and physically repeating Edit. Retain defer as the comparison baseline with executor entry blocked; continue evaluating the hybrid route without adopting it. Experimental SDK installation awaits approval of the recorded disposable environment proposal. General filesystem and claims preservation, production ownership and orphan containment, pending approvals on that candidate and ambiguous Bash still require proof. DSR-1.10 remains IN PROGRESS and DSR-0.12 remains OPEN; this recommendation records no Operator adoption choice.

Experimental follow-up recommendation (2026-10-01): the Operator approved the exact disposable installation, which completed with unchanged baseline versions and CLI. The [canonical evidence](../canonical-documents.md#evidence) now proves bounded experimental SDK result reuse and pending approve/reject on replacement Workers, and preflight refusal before CLI startup for tested identity and storage failures. Concurrent completed transcript resumes still started two CLI owners, and Worker loss left an orphan requiring harness cleanup. Recommend retaining defer as baseline and treating experimental recovery as the stronger candidate for further host contract proof. No adoption is recommended until exclusive ownership, process supervision, durable ambiguous Bash parking, signed decisions and filesystem/claims recovery are established. Mods remain unsupported for the tested interception invocation. DSR-0.12 remains OPEN and DSR-1.10 remains IN PROGRESS; approval of installation records no adoption choice or general executor authorization.

#### Problem

The next real model proof and executor build need one selected integration with explicit limits. Selecting a prototype because it exists would erase the distinction between reported capability and verified application behavior.

#### Scope

- Record whether to retain the current integration, adopt an evidenced candidate, or stop for redesign. Rejecting both new candidates is an allowed outcome.
- Record the selected SDK and engine versions, supported tool and agent scope, result delivery path, compatibility evidence and remaining release or dependency constraints.
- Assign conversation history, workspace preservation and approval and outcome records to their accountable owners. Refer to DSR-0.6 and DSR-0.11 for deployment storage decisions; do not choose a database by implication.
- Preserve Option R, signed human decisions and the rule that unresolved Bash uncertainty parks without another execution or model continuation.

#### Out of scope

- Implementation, dependency upgrades, paid execution, external contact and promotion of an experimental SDK API to released behavior.
- Reopening completed offline evidence or changing the approved safety scope.

#### Acceptance criteria

- [x] The Operator records retain, adopt or redesign and cites the candidate matrix from DSR-1.10. Every rejected or unsupported candidate has a reason. Proof: the approved decision record for BD-10.
- [x] The record names the selected versions and integration boundary, separates experimental APIs from released support, and names any required dependency or cooldown approval. Proof: a version and scope table linked to immutable sources and the experiment results.
- [x] The choice preserves reusable native skill execution in application authored Temporal Workflows under the plugin registration, policy and security contract. The later `temporal-agent-harness` adapter remains separately verified in Phase 7. Proof: the decision record's goal and compatibility boundary, linked to the bounded DSR-5.8 proof and DSR-7.2 adapter proof; no arbitrary Workflow compatibility is asserted.
- [x] The record allocates all three state classes and identifies the ownership and orphan process controls needed on a replacement Worker. Proof: the responsibility table, with links to DSR-0.6 and DSR-0.11 instead of duplicate storage decisions.
- [x] The record keeps the current integration until adoption is explicitly approved and confirms that ambiguous Bash remains parked without repeat execution or model continuation. Proof: the disposition text and unchanged Option R constraints.
- [x] The specification, plan and affected proof tickets match the recorded choice before DSR-1.3 or DSR-1.9 can close. Proof: the reviewed package diff and passing evidence and local ticket checks.

#### Dependencies and blockers

- DSR-1.10 must provide the bounded comparison before the Operator selects an integration.
- Blocks DSR-1.3 and DSR-1.9, so no Phase 2 implementation follows an unapproved integration.

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), BD-10 and A-57 through A-59; [canonical plan](../canonical-documents.md#plan), M1; [approved Option R](../proposals/distributed-recovery/2026-10-08/provenance.md#p-001).
- SDK session and filesystem boundaries: https://code.claude.com/docs/en/agent-sdk/sessions
- Experimental hybrid integration at the inspected revision: https://github.com/temporalio/ai-integrations/blob/2ab873cc23a1b3224531a5634c1f6d1c8ef0ea1f/python/claude_agent_sdk/README.md
- Mods early access contract: https://github.com/anthropics/claude-code/blob/52c76441cae91f6891e4712306bffb057ff6fec5/mods/README.md
- Approved goal and first research priority, not candidate adoption or runtime proof: https://github.com/mortdiggiddy/ai-integrations/blob/2acc081998407f9c88fdba349103f5392dab2d73/README.md

#### Open questions

- Operator: retain the current path, adopt a proven candidate or redesign after DSR-1.10? No choice is inferred from approval to revise this package.
- The Operator accepted this estimate on 2026-10-01. One point means about 4 focused work hours; confidence remains 75 percent because the decision effort depends on the comparison findings. Acceptance of the estimate does not approve the integration choice.
