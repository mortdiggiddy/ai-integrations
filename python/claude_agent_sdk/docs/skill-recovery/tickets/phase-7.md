# Phase 7 tickets

### DSR-7.1 Submit the plugin additions upstream

Status: OPEN

- Type: Build
- Priority: Low
- Estimate: 4 points (confidence 50 percent)
- Labels: Type: Build, Topic: Effects
- Parent: DSR-P7
- Blocked by: DSR-6.4
- Blocks: DSR-7.2
- Related: none
- Retires: A-35 (second half)
- Informs: none
- Owner role: Plugin engineer

#### Context

Phase 7 starts after PASS, and PASS does not need it. The plan's M6 delivers pull requests as agreed with the author of the existing plugin proposal, the contributor license if the target repository requires one, and a code owner review request. The target repository is not owned by this workspace.

The agent harness maintainers set an entry gate: the inner integration lands in `ai-integrations` first, and the harness port follows. The public API stays additive. DSR-0.5 recorded the outcome of the contact and the agreed split of the additions.

The external repository rule applies to every line that ships. No workspace identifier, named individual or internal ticket identifier may appear in an added line, and the target's own CI commands verify every commit.

**Complete Issue 31 disposition (2026-10-08)**

October 8 full issue sweep: [entire discussion ledger](../proposals/distributed-recovery/2026-10-08/priority-sweep/coverage.md) owns source credit and placement. Reuse existing upstream tool/activity/approval options for additive ToolPolicy; question ownership and package/signature placement are collaborator suggestions, not accepted team assignments. Latest native replay port is reported locally, not source-qualified at the captured PR head. Coordinate delivery only under later explicit contact/push authority. DSR-0.5 remains DONE and its cancelled Slack contact is not reopened.

#### Problem

If a commit carries an internal identifier or fails the target CI, the target judges it and the history keeps it. A push that follows an old CI result can hide a failure. The first half of A-35 closed in DSR-0.5. The second half needs the pull requests as agreed.

#### Scope

- Prepare the pull requests as the DSR-0.5 split describes.
- Verify each commit with the target's own CI commands before any push.
- Sweep every added line for forbidden identifiers.
- Request the code owner review, and record the contributor license step if the target requires it.

#### Out of scope

- The harness port. DSR-7.2 owns it.
- Changing the public API in a way that is not additive.
- Pushing without the operator's explicit instruction. The pull request needs that instruction at push time.

#### Acceptance criteria

- [ ] Each commit that the target judges passes the target's own CI commands (`make sync`, `make lint` and `make test` at Python 3.10 and 3.14 per the repository conventions), run on that commit and not only on the branch head. Proof: a per commit verification record with one entry for each commit.
- [ ] A sweep of every line that the branch adds finds no workspace identifier, no named individual, no internal ticket identifier and no wording that points at one. The sweep also covers blobs that history introduced and later edited away. Proof: the sweep output recorded before each push.
- [ ] After each push, the CI result is read for the exact revision pushed, and the record states the revision. An older or copied result does not count. Proof: the CI result with its revision.
- [ ] The pull requests follow the split that DSR-0.5 recorded, and the public API change is additive. Proof: the pull request list beside the decision record, and a diff check of the public API.
- [ ] A code owner review is requested and recorded. The contributor license step is recorded if the target's contributing file requires one, and the record says which text told the author so. Proof: the review request and the license record.
- [ ] A review that asks for a change that breaks the additive rule is recorded, and the response is a recorded decision. Closing the pull request is the rollback. Proof: the decision record.
- [ ] The row for A-35 records the pull requests as agreed and their state. Proof: the edited row.

#### Dependencies and blockers

- Blocked by DSR-6.4, the PASS verdict.
- Blocks DSR-7.2, because the harness entry gate needs the upstream submission first.
- Needs the DSR-0.5 decision record and the DSR-0.5 split of the additions.

#### Source evidence

- Plan, section *Milestones*, M6.
- Specification, INV-4 to INV-7 as the content of the additions, and *Plugin surface and conventions* in section *Interfaces*.
- Assumption A-35, and open issues OI-9 and OI-14.
- Repository conventions and agent instructions (mutable page, so corroboration only): https://github.com/temporalio/ai-integrations/blob/main/AGENTS.md
- The existing proposal: https://github.com/temporalio/ai-integrations/issues/31

#### Open questions

- Operator: does the target's contributing file require a contributor license? The pack read it through a summary only.
- Plugin engineer: which additions go to the upstream repository and which stay in the fork? DSR-0.5 records the split, and this ticket cannot start without it.
- The pack did not inspect an official sample plugin for review expectations such as replay tests. A claim that review expects them is an assumption.

### DSR-7.2 Port the integration to the agent harness

Status: OPEN

- Type: Build
- Priority: Low
- Estimate: 5 points (confidence 40 percent)
- Labels: Type: Build, Topic: Effects, Status: Blocked on decision
- Parent: DSR-P7
- Blocked by: DSR-6.4, DSR-7.1, DSR-7.3
- Blocks: none
- Related: none
- Retires: none
- Informs: A-36
- Owner role: Plugin engineer

#### Context

The end goal includes compatibility with `temporal-agent-harness` through a separately verified adapter. The plugin first proves reusable execution in an application authored Temporal Workflow under its documented registration, policy and security contract in DSR-5.8. That proof does not close this adapter ticket. The plan's M7 delivers a glue module beside the plugin in the harness `ai_sdks/` directory. It follows the existing glue module pattern, routes effect and ask calls through `run_tool` with the model call id, maps the plugin events onto the harness event vocabulary, and binds approvals and questions to the harness Updates. The harness plugin is ordered last.

The Claude integration has no model call seam, so the glue is step level. The segment stands in for the model activity, deferred effect and ask calls route through `run_tool`, and read class calls stay inside the engine and bypass the harness policy. The harness checkout is read only to plan this ticket and is not a pinned target.

DSR-7.3 decides who owns the effect ordinal and key when the harness owns the loop.

**Complete Issue 31 disposition (2026-10-08)**

October 8 full issue sweep: [I31-L1/L2 and Medium gaps](../proposals/distributed-recovery/2026-10-08/priority-sweep/coverage.md) separates the existing adapter outcome from positive durable-child and parallel-native outcomes. DSR-7.4 owns selection of a testable extension design and delivery scope. The main-agent recovery API does not establish child restoration. Existing denial/serial tests stay intact until a separately adopted extension proves original child/batch identity, exact results, policy/approval, partial failure, shared-file conflicts and descendant cleanup. A selected extension requiring broader harness changes must revise this ticket's current glue-only boundary explicitly; no silent change or implementation follows.

#### Problem

If the harness and the plugin both compute keys, or neither does, keys collide or change between attempts, and the key contract breaks once external services see keys. A port that starts before the upstream submission lands breaks the entry gate.

#### Scope

- The glue module and its registration order.
- Routing of effect and ask calls through `run_tool`.
- Event mapping and approval binding.
- A harness example that runs a skill with a gated effect.

#### Out of scope

- The decision on the ordinal and key owner. DSR-7.3 owns it.
- Changes to the harness itself beyond the glue module.
- Other agent harnesses (non goal N3).

#### Acceptance criteria

- [ ] A harness example runs a skill with an effect gated by the harness approval policy. `tool_start` and `tool_end` appear for the effect with the model call id, and the approval resolves through the harness approval Update. Proof: the example output and the harness history.
- [ ] A denied approval returns a tool error to the model and no effect runs. Proof: a test that checks the model result and the absence of the effect.
- [ ] The effect ordinal and key follow the owner that DSR-7.3 names. The key stays the same across attempts and across Continue-As-New, and differs for a new ordinal. Proof: a test for each case.
- [ ] The harness plugin is ordered last in the plugin list. Proof: a test that reads the order.
- [ ] The documentation states that read class calls bypass the harness policy, and a test records whether a Read call produces a harness event. Proof: the documentation text and the test output.
- [ ] An uncertain claimed Bash outcome appears as an operator visible park, not a plain failure or model result, and the harness starts no next model segment. Proof: a claimed effect Worker loss test. Exceptional Edit uncertainty preserves its distinct retained mapping.
- [ ] The glue module merges only after the DSR-7.1 pull requests are accepted under the harness entry gate. Proof: the pull request state recorded before the merge.

#### Dependencies and blockers

- Blocked by DSR-6.4, the PASS verdict.
- Blocked by DSR-7.1, the upstream submission that the entry gate requires first.
- Blocked by DSR-7.3, the decision on the owner of the ordinal and key.
- The example evidence also supports A-36, and DSR-7.3 retires the row.

#### Source evidence

- Plan, section *Milestones*, M7.
- Specification, section *Interfaces*, paragraph *Harness seam*.
- Specification, section *Alternatives considered*, A7, for the entry gate.
- Approved compatibility goal and separate adapter proof boundary, not proof of the unimplemented glue: https://github.com/mortdiggiddy/ai-integrations/blob/2acc081998407f9c88fdba349103f5392dab2d73/README.md
- Assumption A-36.

#### Open questions

- Plugin engineer: the pack records the harness source at commit 421636d5900320233df9f0096809b4462123ff04 and no public permalink. Supply the repository URL so the ticket can cite the glue module pattern at that commit.
- Plugin engineer: the claim that read class calls bypass the harness policy is analysis and not observed behavior.
- The estimate is 5 points and the confidence is low. Split the glue module from the approval binding in review if the harness Update shape needs work.

### DSR-7.3 Name the owner of the effect ordinal and key for the harness port

Status: OPEN

- Type: Decision
- Priority: Low
- Estimate: 1 point (confidence 70 percent)
- Labels: Type: Decision, Topic: Effects
- Parent: DSR-P7
- Blocked by: none
- Blocks: DSR-7.2
- Related: none
- Retires: A-36
- Informs: none
- Owner role: Operator

#### Context

The plugin computes a stable claim identity once when a deferred call arrives. It is a SHA 256 digest over a canonicalization version, lineage id, effect ordinal, tool name and canonical input. The ordinal advances at scheduling whatever the outcome. Approved Option R retains claim identities but does not offer keyed external service tools or the reserved `idempotency_key` field.

When the agent harness owns the loop, the harness routes each tool call through `run_tool` with the model call id. The specification leaves open which side owns the ordinal and the key in that case. The plan lists it as M0 item (e), and M7 needs it.

#### Problem

Two owners give colliding or unstable keys. No owner gives no key. The port cannot start without one named owner and one answer.

#### Scope

- A decision record that names the owner role and states which component mints the ordinal, computes the key and stores them when the harness owns the loop.
- A statement of how the key guarantees survive under the harness loop.

#### Out of scope

- Building the port. DSR-7.2 owns it.
- A change to the key for plugin only runs.

#### Acceptance criteria

- [ ] The decision record names the owner role and the person who holds it in the tracker, and states which component mints the ordinal, which computes the key and which stores both. Proof: the decision record, confirmed by the owner.
- [ ] The record states whether the key stays stable across attempts and across Continue-As-New under the harness loop, and which input replaces the lineage id and the ordinal if the harness owns them. If a guarantee does not hold for harness runs, the record names the dropped guarantee. Proof: the decision record.
- [ ] The record preserves canonicalization and claim identity under the harness loop and states that keyed service tools and the reserved `idempotency_key` field remain outside version 1. Proof: the decision record.
- [ ] The row for A-36 records the decision and its date. Proof: the edited row.
- [ ] If no owner agrees, the record declares the port excluded, and DSR-7.2 is marked superseded. Proof: the record and the status change.

#### Dependencies and blockers

- Blocks DSR-7.2.
- The harness source and its `run_tool` path are the inputs. The decision needs the Phase 6 verdict only for context and not as a blocker.

#### Source evidence

- Plan, section *Milestones*, M0 item (e) and M7.
- Specification, INV-5, paragraphs *Effect identity* and *What the key gives and does not give*.
- Specification, section *Interfaces*, paragraph *Harness seam*.
- Assumption A-36, and open issue OI-2.

#### Open questions

- Operator: who owns the decision? The pack names the owner as unowned, M0 (e).
- Plugin engineer: does the harness supply a call id that is stable across a retried attempt? The pack did not verify it, and the answer changes which owner is workable.

### DSR-7.4 Select a testable durable child and parallel tool design

Status: OPEN (2026-10-08; prospective extension decision, no runtime implementation approved)

- Type: Decision
- Priority: Medium
- Estimate: 1 points (confidence 80 percent)
- Labels: Type: Decision, Topic: Engine, Status: Blocked on decision
- Parent: DSR-P7
- Blocked by: none
- Blocks: none
- Related: DSR-7.2, DSR-2.6, DSR-4.3
- Retires: none
- Informs: none
- Owner role: Operator

#### Context

The operator requires every outcome in Issue 31 to be addressed. Both Medium outcomes require positive durable child tools and multiple native calls. Existing DSR-1.5 DONE proves unsupported child denial. Canonical v1 accepts one original pending call; neither limit fulfills these future outcomes. The [full issue sweep](../proposals/distributed-recovery/2026-10-08/priority-sweep/coverage.md) owns their proposed proof envelope. This one-point estimate covers recording the design and scope decision from prepared research, not implementing or qualifying both capabilities.

#### Problem

The selected experimental recovery API is main-agent-only. Reusing it for active children or copying a result into the wrong trajectory can lose work or repeat effects. Parallel native writes can conflict even when Temporal records each Activity. A decision must choose a testable supported mechanism and assign delivery work before implementation. The requested outcomes remain open if no viable source exists; an exclusion cannot count as completion.

#### Scope

- Select the child and batch recovery boundaries, reusable source/API and prototype envelope under candidate BD-6.
- Record separate positive child and parallel acceptance outcomes, owners, dependencies and delivery ticket scope before implementation. Assign fresh stable delivery IDs if the selected work is independently valuable.
- Record missing runtime capabilities and a redesign route rather than inventing an executor or declaring denial sufficient.

#### Out of scope

- Implementation, acquisition, runtime experiments and infrastructure provisioning.
- Reopening DSR-1.5 or weakening unsupported child denial and serial pending admission.
- Changing the DSR-7.2 glue-only scope without a recorded adopted design.

#### Acceptance criteria

- [ ] The operator confirms a decision record naming selected API/source pins, child and batch boundaries, owners and separate delivery scope. If current APIs cannot satisfy either outcome, the record names the capability gap and redesign path, and retains that delivery outcome OPEN. Proof: the confirmed decision record and delivery scope references.
- [ ] The record requires actual child original pending call/result recovery, parent/child identities, isolated workspace/policy, approval correlation, count/depth limits, partial captured trees and authoritative descendant cleanup across process/container/host loss. It prohibits treating main-agent recovery or summary text as child recovery. Proof: a child criterion-to-test matrix in the decision record.
- [ ] The record requires at least two actual native calls per message, exact per-call Activities/results/native records, deterministic association, partial batch recovery, duplicate IDs/results, per-call approvals and cancellation, overlapping file conflicts, reset and Continue-As-New. It distinguishes multi-call support from simultaneous execution and sets any claimed concurrency objective. Proof: a batch criterion-to-test matrix.
- [ ] Both matrices include physical effect counters, after-effect result upload failure, rollback-independent intent, ambiguity parking, exact accepted workspace/trajectory, lost cleanup receipt and unchanged serial behavior with extension disabled. Proof: named fault oracles and baseline compatibility tests prepared for the selected delivery scope.
- [ ] The record preserves canonical v1 and all completed dispositions until adoption. It names separately required source acquisition, installation, infrastructure and live execution approvals, if applicable. Proof: the scope and authorization boundary in the record.

#### Dependencies and blockers

- BD-6 adoption and selected source/runtime capability are required before prototype or delivery implementation.
- DSR-2.6 native fidelity, DSR-4.3 storage/termination and DSR-7.2 adapter boundaries inform the decision. Their unresolved runtime proof cannot be inherited as PASS.
- This prospective decision is outside current Phase 1 acceptance and does not change the canonical Phase 6 PASS graph.

#### Source evidence

- All Medium requests and prototype overlap: https://github.com/temporalio/ai-integrations/issues/31#issuecomment-6026506600
- Parallel calls and optional Workflow conversation: https://github.com/temporalio/ai-integrations/issues/31#issuecomment-5939515083
- Experimental main-agent-only recovery boundary: https://github.com/brianstrauch/claude-agent-sdk-python/blob/3ac4b25733d1302c89d0dadd13cab268e64d1213/README.md#main-agent-recovery-with-a-session-store
- Bounded exact native replay prior art: https://github.com/temporalio/ai-integrations/blob/2ab873cc23a1b3224531a5634c1f6d1c8ef0ea1f/python/claude_agent_sdk/tests/hybrid/native_replay.py
- Activity receiver idempotency: https://docs.temporal.io/activity-definition#idempotency
- [Independent Temporal research](../proposals/distributed-recovery/2026-10-08/priority-sweep/agent-temporal.md) and [industry research](../proposals/distributed-recovery/2026-10-08/priority-sweep/agent-industry.md), supporting guidance rather than runtime proof.

#### Open questions

- Operator: which bounded extension prototype should BD-6 adopt, given the main-agent-only API and exact state/containment requirements?
- Integration owner: what published child recovery API and batch conflict contract can deliver both outcomes with the existing controller and executor seam?
