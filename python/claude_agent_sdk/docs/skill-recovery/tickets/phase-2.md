# Phase 2 tickets

### DSR-2.1 Prepare the per run workspace, claims directory, manifest, counters and effect identity state

Status: OPEN

Phase 1 gate disposition (2026-10-07): DSR-1.9 is DONE with the operator's continue decision; canonical `evidence.md`, *Approved Phase 1 continue decision (2026-10-07)*, owns its scope and residual limitations. DSR-0.6 remains OPEN and still blocks workspace preparation. This checkpoint implements no workspace and checks no Phase 2 acceptance criterion.

Workspace decision preparation (2026-10-09): [DSR-0.6 preparation](../proposals/distributed-recovery/2026-10-08/dsr-0.6-preparation.md) recommends retaining the shared-volume/file-claim contract. Cold bundle and independent dispatch alternatives require separate adoption before changing this ticket. Finished-directory verification preserves the manifest and generation; the criterion below is corrected to match canonical idempotent preparation. Missing or uncertain claims cannot be repaired by creating an empty claim tree. No implementation or acceptance completion follows.

- Type: Build
- Priority: High
- Estimate: 4 points (confidence 70 percent)
- Labels: Type: Build, Topic: Workspace, Topic: Effects
- Parent: DSR-P2
- Blocked by: DSR-0.6, DSR-1.9
- Blocks: DSR-2.2, DSR-2.3, DSR-2.4, DSR-2.5, DSR-2.7, DSR-2.8, DSR-2.9
- Related: none
- Retires: none
- Informs: A-06, A-21, A-48
- Owner role: Plugin engineer

#### Context

Phase 2 builds the effect executor. The executor needs a prepared run directory, a claims directory outside the tree that the effect identity can write, a manifest, and the state that gives each effect a stable identity. The specification places all of this in the prepare Activity and in the workspace and counter state ([canonical specification](../canonical-documents.md#specification), INV-2, *Workspace*; INV-5, *Effect identity* and *The lineage id*; Interfaces, `AgentState`). The plan lists the same artifacts under milestone M2 ([canonical plan](../canonical-documents.md#plan), M2). The volume class and the effect isolation level come from DSR-0.6. The Phase 1 review (DSR-1.9) must confirm that the engine mechanism holds before this build starts.

#### Problem

No code creates the run directory layout, the Worker owned claims directory, the manifest, or the counters. Without them, the claimed executor cannot refuse a second spawn, and a volume restored from an older snapshot cannot be detected. The prepare step must also be safe to call twice and must never expose a half copied package.

#### Scope

- A `prepare_workspace` Activity that creates the run directory under a hash of the lineage id, copies the skill package under a temporary name, renames it, hashes the finished copy, and writes a manifest with the namespace, the Workflow Id, the lineage id, the start time, the package hash and a `generation` counter.
- Creation of the claims directory `.tca-claims/<hash of the lineage id>/` as a Worker owned directory outside the tree that the effect identity can write.
- A second call on a finished directory that verifies it and returns.
- The `cleanup_workspace` Activity and the janitor contract are not in this ticket. Only the creation side is.
- Lineage id, effect ordinal and effect key state in `AgentState`: the lineage id minted once (the starter supplied value is Phase 3, DSR-3.5), the ordinal advanced at scheduling whatever the outcome, and the key computed once per call from the canonicalization version, lineage id, ordinal, tool name and canonical input, then stored with the pending call.
- The manifest generation and its stored `volume_generation` value. Claims high water state and `contract_version` are outside approved version 1.
- The `AgentState` fields that belong to Phase 2, taken from the one canonical list in the specification.
- The per run `cwd` change. The runner's working directory is a constructor constant used in five places (the constructor mismatch check, the engine option, the session fork copy, the session key derivation and the segment options). The segment input and the effect input gain a `cwd` field, the engine, the session key, the fork copy and the mismatch check use the input value, and the constructor check runs per segment without blocking the event loop.

#### Out of scope

- The claimed executor, its spawn guard and its claim files (DSR-2.2).
- The outcome table (DSR-2.3).
- Janitor removal, `reprepare`, and snapshot restore detection beyond the counter plumbing (Phase 4, DSR-4.2).
- Effect isolation at the decided level (Phase 4, DSR-4.1).
- Fields owned by Phase 3 (`pending_decisions`, `park_seq`, the wait fields).

#### Acceptance criteria

- [ ] Prepare creates the run directory, the manifest and the claims directory, and a second call on a finished directory returns without change. Proof: an integration test against a Temporal dev server that calls the Activity twice and compares the tree and manifest bytes.
- [ ] The hash is taken over the finished copy, and the hash input is the sorted relative paths, normalized modes and file bytes, with symlinks rejected. Proof: a unit test that fails when one byte, one mode bit, or one symlink in the package changes the hash or is accepted ([canonical specification](../canonical-documents.md#specification), INV-7, *Skill packages are code*).
- [ ] A crash between the copy and the rename leaves no directory that a segment would accept. Proof: a fault injection test that stops the Activity after the copy and shows that the next call repairs or rejects the directory.
- [ ] The claims directory exists outside the run directory, is owned by the Worker user, and is not writable by the effect identity. Proof: a permission check in the test rig under the effect identity chosen by DSR-0.6.
- [ ] The manifest `generation` is set on initial preparation and remains unchanged when a finished directory is verified again. The Workflow stores the observed value as `volume_generation` and refuses a lower value. Proof: a Workflow test that compares manifest bytes and stored generation after two idempotent prepares, plus a lower-generation refusal case. An explicit repair that changes generation belongs to DSR-4.2 and must preserve unresolved claims.
- [ ] The effect ordinal is stored in `AgentState` before dispatch and advances whatever the outcome, and a replay of a recorded history yields the same ordinal. Proof: a replay test with a recorded history that includes a failed effect ([canonical specification](../canonical-documents.md#specification), INV-5, *Effect identity*).
- [ ] The effect key is computed once, is stored with the pending call, and is reused by a retry. Proof: a Workflow test that forces a second dispatch of the same pending call and shows an identical stored key and an unchanged computation count.
- [ ] The segment input and the effect input carry `cwd`, and the engine working directory, the session key and the fork copy use the input value, so two runs with different directories in one Worker do not share a session key. Proof: a test that runs two segments with different `cwd` values in one runner and compares the session keys and the engine working directories ([canonical specification](../canonical-documents.md#specification), INV-2, *Workspace*).
- [ ] The mismatch check runs per segment and does not block the event loop. Proof: an event loop lag assertion during the check in a segment test, and a test that the check still detects a mismatched directory.
- [ ] The tests in this ticket need no credentials. Proof: the plugin test suite passes with every `CLAUDE` and `ANTHROPIC` variable cleared ([canonical plan](../canonical-documents.md#plan), *Stack*).
- [ ] The prepared workspace is distinct from conversation history and approval and outcome records. Its manifest identifies the preservation mechanism selected by DSR-0.6 and DSR-0.12, without treating a restored transcript or local Mods store as restored files. Proof: manifest assertions and a test with present conversation state but missing workspace files that refuses or rebuilds only through the approved prepare path.

#### Dependencies and blockers

- Blocked by DSR-0.6 (volume class and effect isolation level) and DSR-1.9 (Phase 1 continue decision).
- DSR-0.2 selects Option R: keep manifest generation and stable claim identity; omit claims high water state and the additional contract version.
- Blocks every other Phase 2 build ticket and the Phase 2 exit review.

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), INV-2, *Workspace*: run directory layout, prepare Activity, manifest and `generation`.
- [canonical specification](../canonical-documents.md#specification), INV-5, *Effect identity* and *The lineage id*: key definition, ordinal rule, lineage id mint.
- [canonical specification](../canonical-documents.md#specification), Interfaces, `AgentState` and *Activities*.
- [canonical plan](../canonical-documents.md#plan), M2 Artifact and Checks.
- Assumption rows A-06, A-21 and A-48 in the specification table.
- Fork `_models.py` for `AgentState`: https://github.com/osamastro7-droid/ai-integrations/blob/69f5497d3d3dec7ad3269c72ff266c2931c9f379/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_models.py
- Fork `_activity.py` for the existing Activity registration: https://github.com/osamastro7-droid/ai-integrations/blob/69f5497d3d3dec7ad3269c72ff266c2931c9f379/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_activity.py

#### Open questions

- Plugin engineer: the estimate is 4 points because the ticket carries workspace, effect identity state and the per run `cwd` change. Split in review if the effect identity state becomes its own ticket.
- Plugin engineer: no official sample repository was inspected for prepare Activity patterns. Any claim that needs one stays open.

### DSR-2.2 Run Bash as a claimed effect with the spawn guard

Status: OPEN

October 9 source reconciliation: [the maintained release-check comparison](../proposals/distributed-recovery/2026-10-08/priority-sweep/coverage.md#october-9-release-check-reconciliation) owns the pinned hook-exception denial, absent-answer/trusted-settings and permission-flag evidence. A wrong nonexecution classification can permit a second physical effect. Source review and independently witnessed counter cases remain pending; protected claims and no-respawn requirements remain authoritative. Status and acceptance criteria are unchanged.

- Type: Build
- Priority: High
- Estimate: 4 points (confidence 65 percent)
- Labels: Type: Build, Topic: Effects
- Parent: DSR-P2
- Blocked by: DSR-2.1
- Blocks: DSR-2.3, DSR-2.6, DSR-2.7, DSR-2.8, DSR-2.9, DSR-3.5
- Related: none
- Retires: A-04, A-05
- Informs: A-17, A-41
- Owner role: Plugin engineer

#### Context

A claimed effect is a Bash call protected by claim guards. The engine defers Bash, the Workflow dispatches it to the effect queue, and the executor spawns the command. An operator Activity reset and a Workflow reset can cause another dispatch, and Workflow code cannot see an Activity reset ([canonical specification](../canonical-documents.md#specification), INV-1, *Claimed effect guard*). The executor refuses another spawn in defined cases. Any uncertain Bash outcome parks the run without a model facing unknown result, as approved in DSR-0.2.

#### Problem

Assumptions A-04 and A-05 are unproven. The claim file mechanism, the preserved heartbeat check and the `attempt` check have no implementation or test. The ordinal claim file is a proposed fix that no reviewer verified.

#### Scope

- The `run_effect` Activity in claimed mode for Bash, with `maximum_attempts` of 1, a 5 minute default Start-To-Close, a 60 second Heartbeat Timeout and WAIT_CANCELLATION_COMPLETED.
- Exclusive creation of the claim files `<key>` and `ord-<ordinal>` with `O_CREAT`, `O_EXCL` and `O_NOFOLLOW` before the spawn record and the spawn, each file storing the `workflow_run_id`, the ordinal, the key and the spawn time.
- Refusal on `EEXIST`, on a preserved heartbeat detail that shows a spawn for the key, and on `attempt` above 1, each raising a non retryable `UnknownOutcome` error.
- Rejection of `run_in_background`, an environment allow list, and an output cap with the full output in a file.
- Treatment of a claim whose stored run id differs from the current run id as a reset or Continue-As-New signal, as [canonical specification](../canonical-documents.md#specification) INV-1 states.

#### Out of scope

- The retained ordered outcome table and the `ExecutorFault` park cause (DSR-2.3).
- Process tree containment, cancellation, shutdown and payload caps (DSR-2.7).
- Isolation at the decided level (Phase 4, DSR-4.1) and the exclusive create test across two hosts (Phase 4, DSR-4.3).
- Operator `redo` and `release_claim` are deferred by DSR-0.2. Recovery for ambiguous Bash remains the open DSR-0.8 decision.

#### Acceptance criteria

- [ ] A Bash call spawns once and returns its capped output. Proof: an integration test on a dev server with a scripted deferred call.
- [ ] A command that ran and then timed out, exhausted its single attempt, or lost its Worker records uncertainty for the operator, parks or stops before the next segment, and never runs twice. Proof: three fault injection tests, each counting spawns and showing no model result or next segment ([canonical plan](../canonical-documents.md#plan), M2 Checks). M3 adds signed recovery; it is not required to observe the M2 stop.
- [ ] An operator Activity reset of a running Bash effect does not run the command again, because the executor refuses on the claim file or the preserved spawn record. Proof: a test that resets the Activity through the server and counts spawns. The test notes that `attempt` returns to 1 after a reset and does not rely on it.
- [ ] A different command decided at an ordinal whose `ord-<ordinal>` file exists after a Workflow reset is refused and parks without a model result. Proof: a test that resets the Workflow, scripts a different command at the same ordinal, and counts spawns. DSR-0.2 retains the ordinal claim file.
- [ ] Each of the two claim files is created before the spawn, and a second exclusive create of either fails with a refusal. Proof: a unit test that creates one file in advance and shows the refusal for each file separately.
- [ ] A claim planted by the effect identity is impossible. Proof: a test under the effect identity that tries to write to the claims directory and fails, because the claims live outside `work/`.
- [ ] A claim failure other than `EEXIST` and a missing claims directory raises `NotStarted` and nothing spawns. Proof: a fault injection test with a read only claims directory.
- [ ] The guarantee is stated as at most one spawn absent a removed claim file, with a partitioned host and a daemonized child listed as residuals. Proof: the executor docstring and the README limits text match [canonical specification](../canonical-documents.md#specification), INV-1, *Claimed effect guard*.

#### Dependencies and blockers

- Blocked by DSR-2.1 (run directory, claims directory, counters).
- DSR-0.2 retains both key and ordinal claim files and drops the claims high water counter.
- Blocks DSR-2.3, DSR-2.6, DSR-2.7, DSR-2.8, DSR-2.9 and DSR-3.5.

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), INV-1, *Claimed effect guard*, *Effect Activities*, *Cancellation and shutdown*.
- [canonical specification](../canonical-documents.md#specification), INV-5, *Claimed mode*.
- Assumption rows A-04 and A-05.
- Retry policy and `maximum_attempts`: https://docs.temporal.io/encyclopedia/retry-policies#default-behavior and https://docs.temporal.io/design-patterns/fixed-count-retries#disabling-retries-entirely
- Activity cancellation types: https://docs.temporal.io/develop/typescript/workflows/cancellation#cancel-an-activity
- Fork `_activity.py`: https://github.com/osamastro7-droid/ai-integrations/blob/69f5497d3d3dec7ad3269c72ff266c2931c9f379/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_activity.py

#### Open questions

- Plugin engineer: no official source states an at most once guarantee for `maximum_attempts` of 1. The guarantee here is the design's own claim and its proof is the test set above.
- Security owner: every claim about claim file integrity is void until DSR-0.6 fixes the isolation level ([canonical specification](../canonical-documents.md#specification), INV-7, *Effect isolation*). Confirm that the tests run under that identity.
- Plugin engineer: the estimate carries low confidence because the operator reset test needs a server level reset and the ordinal file is a proposed fix.

### DSR-2.3 Map every effect outcome by the ordered table and the executor fault

Status: OPEN

October 9 source reconciliation: [the maintained release-check comparison](../proposals/distributed-recovery/2026-10-08/priority-sweep/coverage.md#october-9-release-check-reconciliation) corrects the earlier nonexecution claim. Affirmative evidence is required to classify not started; an absent hook answer can still allow execution. Otherwise governed Bash parks without another spawn or model continuation. A wrong classification can repeat a mutation. Compare the pinned failure mapping with this ticket's ordered outcome table; source adoption and physical proof remain pending. Status and acceptance criteria are unchanged.

- Type: Build
- Priority: High
- Estimate: 3 points (confidence 70 percent)
- Labels: Type: Build, Topic: Effects
- Parent: DSR-P2
- Blocked by: DSR-2.1, DSR-2.2
- Blocks: DSR-2.4, DSR-2.5, DSR-2.9, DSR-3.3
- Related: none
- Retires: A-08, A-10, A-16 (M2 part), A-53, A-54 (executor part)
- Informs: A-24
- Owner role: Plugin engineer

#### Context

The fork turns every Activity error that is not cancellation into a plain "Tool failed" result. That could invite a second Bash command after an uncertain outcome. Approved Option R instead parks uncertain Bash without model continuation. The specification's retained ordered table governs the other outcomes ([canonical specification](../canonical-documents.md#specification), INV-1, *Outcome mapping*), and the plan assigns mapping to Workflow tool dispatch.

**Complete Issue 31 disposition (2026-10-08)**

October 8 full issue sweep: [I31-H2](../proposals/distributed-recovery/2026-10-08/priority-sweep/coverage.md) requires a fault after a physical effect and before External Storage result upload/Activity completion. Proposed oracle: no second physical effect; adopt an independently recorded exact result or park uncertain Bash with no model continuation. The upstream default interruption message with continued model execution is not this mandatory park contract. Original MCP `_meta` propagation does not prove receiver deduplication. Retain stable identity across retry/reset and reject missing/regressed authority. DSR-2.5 remains SUPERSEDED; no keyed-service executor is adopted.

#### Problem

The mapping does not exist in the fork. The wrapper type that stops a tool body from impersonating `NotStarted`, and the `ExecutorFault` park cause, are proposed fixes with no verification. Assumptions A-08 and A-10 are open.

#### Scope

- Workflow side dispatch and ordered outcome mapping for retained classes: success, executor `NotStarted` before a claim, Schedule-To-Start timeout, safe repeatable failure, and uncertain claimed or exceptional Edit outcomes. Ambiguous Bash parks and produces no model result.
- The executor side wrapper that wraps exceptions raised by a tool body and raises `NotStarted` only from executor code before the first claim. Tool bodies cannot impersonate a safe pre claim refusal.
- The proposed wrapper records the inner class name and message for plain Python exceptions and `ApplicationError`. It passes cancellation through unchanged, including `asyncio.CancelledError` and heartbeat based cancellation. Cancellation behavior remains unverified until tested (A-53).
- Segment and effect input, result and state plumbing for `package_hash`, `policy_version` and `engine_version`, with mismatch checks before engine start or claim creation. A mismatch or missing claims directory raises non retryable `ExecutorFault`. The cause is visible to the operator and tells the model nothing (A-54).
- Schedule-To-Start maps to `NOT_RUN` only for a safe repeatable effect. Bash parks without model continuation. The exceptional self containing Edit retains its single attempt uncertainty mapping, not a repeatable guarantee.
- The message wording for safe `NOT_RUN` results and tool errors, and the separate operator cause record for uncertain outcomes. M2 must observe the park or stop before a next segment; DSR-3.3 adds signed recovery in M3.

#### Out of scope

- Operator `redo`, claim release and keyed effects are deferred by DSR-0.2.
- The Edit crash protocol (DSR-2.4).
- Keyed retry policy and the key field (DSR-2.5).
- The additional contract version is deferred; DSR-2.8 is SUPERSEDED. The retained package, policy and engine checks are owned here.

#### Acceptance criteria

- [ ] Each retained ordered outcome row maps as stated for a scripted Activity outcome. Proof: a table driven Workflow test with a case per row and an overlapping case proving precedence ([canonical specification](../canonical-documents.md#specification), INV-1, *Outcome mapping*).
- [ ] Schedule-To-Start reports `NOT_RUN` for a safe repeatable effect, parks Bash without model continuation, and retains the exceptional Edit's unknown mapping, including after reset with `--clear-heartbeat-details`. Proof: dev server tests with an unreachable queue and reset command ([canonical plan](../canonical-documents.md#plan), M2 Checks).
- [ ] An error typed `NotStarted` raised inside a tool body is wrapped and does not map to `NOT_RUN`. Proof: an executor test asserting refusal cannot be impersonated.
- [ ] A plain Python exception whose class is named `NotStarted`, raised in a tool body, is wrapped and does not map to `NOT_RUN`. Proof: a tool body test with a plain class of that name (proposed rule, unverified).
- [ ] A wrapped failure keeps its inner class name and message without changing the retained mode's retry limit. Proof: executor tests reading attempt counts and failure fields.
- [ ] Cancellation passes through the wrapper unchanged and reports cancelled rather than a wrapped failure. Proof: cancellation tests for retained modes, including heartbeat cancellation (A-53).
- [ ] A typed error after a Bash claim records uncertainty, stops before a next segment, and sends no unknown result to the model. Proof: a Bash executor and Workflow test with a post claim failure.
- [ ] A crash after a Bash effect but before outcome publication follows the same park rule on the integration selected by DSR-0.12. Recovery of a pending engine call alone does not authorize another spawn or model continuation. Proof: a fault injection test with one effect marker, intact claim files and zero subsequent model turns.
- [ ] Package hash, policy version and engine version mismatches each raise `ExecutorFault` before a claim or engine start; a missing claims directory also refuses. Proof: parameterized effect and segment tests checking zero spawns or engine starts and no model result (A-16 M2 part).
- [ ] A valid segment returns the three retained version fields and the Workflow stores them. Proof: a Workflow state assertion after a scripted segment result.
- [ ] Every executor refusal reaches an operator visible cause record and stops before another segment. Proof: a Workflow test per fault checking the cause record, no model result and zero subsequent starts (A-54 executor part). DSR-4.2 tests snapshot refusals.
- [ ] Known safe failures return tool errors with `is_error` true. The exceptional Edit retains its explicit unknown result where the specification permits it. Ambiguous Bash sends no tool result. Proof: tests reading resumed session messages and counting segment starts.
- [ ] Recorded histories from the fork and from this ticket replay without non determinism, with the new behavior guarded by `workflow.patched`. Proof: the Replayer over recorded histories ([canonical specification](../canonical-documents.md#specification), INV-3, *Determinism inside the Workflow*).

#### Dependencies and blockers

- Blocked by DSR-2.1 (state fields) and DSR-2.2 (claimed executor).
- DSR-0.2 removes keyed effects, claims high water and the additional contract version. Retained mismatch checks from SUPERSEDED DSR-2.8 belong to this ticket.
- Blocks DSR-2.4, DSR-2.5, DSR-2.9 and DSR-3.3. DSR-3.3 parks on the causes this ticket records.

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), INV-1, *Outcome mapping* and *Effect Activities*.
- [canonical specification](../canonical-documents.md#specification), INV-5, *Mode table*.
- Assumption rows A-08 and A-10.
- Timeouts and retry: https://docs.temporal.io/evaluate/features/timeouts-and-retries#activity-timeouts and https://docs.temporal.io/encyclopedia/retry-policies#default-behavior
- Fork `_workflow.py` for the plain failure mapping: https://github.com/osamastro7-droid/ai-integrations/blob/69f5497d3d3dec7ad3269c72ff266c2931c9f379/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_workflow.py

#### Open questions

- Plugin engineer: the wrapper rules above are proposals. Confirm or replace them before the wrapper is built, and record the result against A-10.
- Plugin engineer: prove runtime row precedence matches the rebaselined specification. DSR-0.3 owns the documented severity and ordering corrections; this ticket owns executor mapping evidence.
- Plugin engineer: the SDK fallback for an unknown outer error type is retryable (brief 20, 2.5). Confirm it with a test, because no official sample was inspected.

### DSR-2.4 Run Write and Edit as repeatable effects

Status: OPEN

October 9 source reconciliation: [the maintained release-check comparison](../proposals/distributed-recovery/2026-10-08/priority-sweep/coverage.md#october-9-release-check-reconciliation) now pins a public native port and successful plugin CI cells. Compare native record replacement, rejection/error shape and full-file exclusion before overlapping implementation. Incorrect records can break subsequent edits or inflate history. This does not select native replay over the existing repeatable protocol or prove workspace/postimage recovery. Status and acceptance criteria are unchanged.

- Type: Build
- Priority: High
- Estimate: 3 points (confidence 70 percent)
- Labels: Type: Build, Topic: Effects
- Parent: DSR-P2
- Blocked by: DSR-2.1, DSR-2.3
- Blocks: DSR-2.6, DSR-2.9
- Related: none
- Retires: A-09, A-59 (native file semantics and outcome consistency part)
- Informs: A-39
- Owner role: Plugin engineer

#### Context

Write and Edit are repeatable effects. The executor treats them as idempotent by content, with one exception for an Edit whose new text contains its old text. The specification gives the protocol: compute the post image hash before the write, send pre and post image hashes in a heartbeat, write by atomic replace, and decide a retry from the current file hash ([canonical specification](../canonical-documents.md#specification), INV-5, *Repeatable mode*).

#### Problem

Heartbeats are throttled and not awaited. A Worker that dies after the write and before the heartbeat reaches the server leaves a retry with no recorded images, and a repeat of a self containing Edit corrupts the file (for example `foobarbar`). The rule for that case is a proposed fix. Review item R5-09 also notes an overlap case where the old text can match again after replacement.

#### Scope

- `run_effect` in repeatable mode for Write and Edit with a 1 minute Start-To-Close, a 30 second Heartbeat Timeout and up to 5 attempts.
- Write semantics: a Write with the same content is a no op, and a path outside `work/`, including the run directory root and `.claude/`, returns an `is_error` result and raises nothing.
- Edit semantics: the unique match and `replace_all` rules, the heartbeat of both hashes before the write, and atomic replace through a temporary file in the same directory and a rename.
- Retry decision: report success when the current hash equals the post image hash, apply again only when it equals the pre image hash, and fail when it matches neither.
- The self containing Edit rule: dispatch with `maximum_attempts` of 1 and map by row 6 of the outcome table.

#### Out of scope

- The differential test against the engine (DSR-2.6).
- The outcome table itself (DSR-2.3).
- Isolation of the effect identity (Phase 4).
- The overlap case in R5-09 beyond a recorded decision in Open questions.

#### Acceptance criteria

- [ ] A Write repeats safely: a repeatable effect that runs twice leaves the same file. Proof: a test that forces a retry and compares file bytes.
- [ ] A Write to the run directory root or to `.claude/` returns an `is_error` result and raises nothing. Proof: two executor tests that assert the result and the absence of an exception ([canonical specification](../canonical-documents.md#specification), Interfaces, *Effect executor contract*).
- [ ] An Edit whose new text contains its old text runs with one attempt and reports unknown when the Worker dies after the write and before the heartbeat. Proof: a crash after write test with a self containing Edit, killing the Worker at the injected point.
- [ ] Every other Edit is applied once after a retry. Proof: a test that kills the Worker after the write for an Edit with disjoint old and new text, then checks one application by file hash.
- [ ] A retry state that matches neither recorded hash is a failure and does not write. Proof: a test that changes the file between attempts.
- [ ] The write is atomic: a crash during the temporary file write leaves the original file unchanged. Proof: a fault injection test that stops between the temporary write and the rename.
- [ ] The overlap case where the old text can match again after replacement has a recorded outcome. Proof: a test or a recorded decision that states the executor result ([canonical specification](../canonical-documents.md#specification), Open issues, and brief 21 R5-09).
- [ ] The Edit rules for unique match and `replace_all` equal the engine's behavior wherever the differential test of DSR-2.6 shows the engine enforces them. Proof: the DSR-2.6 result linked in this ticket.
- [ ] If DSR-0.12 adopts native Read/Edit execution, native read metadata, validation failures and file outcome consistency survive the selected recovery boundary. A crash after mutation but before publishing the result yields a consistent recorded outcome or blocks recovery. Proof: native Read/Edit and crash tests covering the supported path and file types; the prototype's single `note.txt` snapshot is not general filesystem proof. If no native path is adopted, record that candidate rejection and prove the retained repeatable protocol instead.

#### Dependencies and blockers

- Blocked by DSR-2.1 (workspace layout) and DSR-2.3 (outcome mapping for rows 5 and 6).
- Blocks DSR-2.6 and DSR-2.9.

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), INV-5, *Repeatable mode*; INV-1, *Outcome mapping* rows 5 and 6; Interfaces, *Effect executor contract*.
- Assumption row A-09 (the protocol is a proposed fix).
- Heartbeat and idempotency guidance: https://docs.temporal.io/design-patterns/long-running-activity and https://docs.temporal.io/develop/python/best-practices/error-handling#make-activities-idempotent
- Fork `_activity.py`: https://github.com/osamastro7-droid/ai-integrations/blob/69f5497d3d3dec7ad3269c72ff266c2931c9f379/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_activity.py
- Bounded native Read/Edit replay precedent, not production workspace proof: https://github.com/temporalio/ai-integrations/blob/2ab873cc23a1b3224531a5634c1f6d1c8ef0ea1f/python/claude_agent_sdk/README.md

#### Open questions

- Plugin engineer: the overlap case from R5-09 is open. Choose between treating any overlap as a one attempt Edit and a stricter content check.
- Plugin engineer: confirm that the engine enforces a read before edit rule. DSR-2.6 settles it. This ticket reproduces the rule only if the differential test shows it.
- No official sample repository was inspected for atomic replace patterns on a network file system. The claim stays open for Phase 4.

### DSR-2.5 Run keyed author tools with the idempotency key and retry policy

Status: SUPERSEDED

Scope disposition (2026-10-01): DSR-0.2 approved Option R. Keyed effects are not offered in version 1. The historical body below is not active implementation scope. A-11, A-45 and A-47 remain as superseded assumption rows; relationship links remain for phase exit coverage.

- Type: Build
- Priority: High
- Estimate: 4 points (confidence 65 percent)
- Labels: Type: Build, Topic: Effects
- Parent: DSR-P2
- Blocked by: DSR-0.10, DSR-2.1, DSR-2.3
- Blocks: DSR-2.9
- Related: DSR-2.6
- Retires: A-11, A-45, A-47
- Informs: A-06, A-10
- Owner role: Plugin engineer

#### Context

A keyed effect is an author defined tool. The executor adds the effect key to the tool arguments in the reserved field `idempotency_key`, retries stay on, and the retry horizon is bounded by time. The key is enforced by the service that the tool calls, not by Temporal ([canonical specification](../canonical-documents.md#specification), INV-5, *What the key gives and does not give*; INV-1, *Effect Activities*). The retention window of each keyed service comes from DSR-0.10.

#### Problem

The field name is a one way door once external services see keys. The keyed retry policy is a proposed fix. The assumption that the retry horizon stays inside the service retention window is an inference. A tool that wraps a permanent failure in a generic exception retries until the bound.

#### Scope

- Dispatch of an author tool as a keyed effect, with the key delivered in `idempotency_key` and the fork docstring that points to the Activity id corrected.
- The keyed retry policy: SDK defaults for the first interval, backoff and maximum interval, no attempt count, and a `schedule_to_close_timeout` default of 10 minutes that the policy entry can change.
- A policy entry check that rejects a Schedule-To-Close value above the retention window recorded by DSR-0.10.
- A tool entry that sets `maximum_attempts` to 1, treated like a claimed effect by the outcome table.
- Policy schema and timeout rules (proposed and unverified, from review item R6-07): the tool policy schema gains `maximum_attempts` and a list of non retryable error types, both covered by `policy_version`. The policy load requires `schedule_to_close_timeout` to exceed `schedule_to_start` by at least one `start_to_close`, so a queue wait cannot exhaust both limits at once. The ticket states which timeout type maps to which row of the outcome table.
- Key stability tests: identical across attempts and across Continue-As-New, new for a new ordinal after a failure, different under Workflow Id reuse, and the same after a reset.
- The `ToolDefinitiveError` type raised with `non_retryable=True` at the throw site.

#### Out of scope

- The outcome table (DSR-2.3).
- The reset proof of the lineage id (Phase 3, DSR-3.5).
- Keyed `redo` after a park (Phase 3, DSR-3.3).
- Idempotency behavior of a real external service. The tests use a test service that honors the key.

#### Acceptance criteria

- [ ] A keyed tool receives the key in `idempotency_key`, and the key equals the value stored with the pending call. Proof: a tool test that echoes the argument and a Workflow assertion on the stored key (only if kept in version 1, keyed effects).
- [ ] A keyed effect that ran but did not report gives one external effect and reports unknown when the Activity ends after the start. Proof: a test service that counts effects per key and a Worker kill after the call (only if kept in version 1, keyed effects).
- [ ] The key is identical across attempts and across Continue-As-New, changes for a new ordinal after a failure, and differs under Workflow Id reuse. Proof: a Workflow test per case (only if kept in version 1, keyed effects).
- [ ] A keyed effect retries under the default policy inside its Schedule-To-Close bound, stops at once on a `ToolDefinitiveError`, and a keyed tool whose entry sets one attempt maps like a claimed effect. Proof: three tests with a scripted failing tool (only if kept in version 1, keyed effects).
- [ ] A policy entry with a Schedule-To-Close above the recorded retention window of its service is rejected at load. Proof: a policy load test that uses the DSR-0.10 record format (only if kept in version 1, keyed effects).
- [ ] The policy schema holds `maximum_attempts` and the non retryable type list, and a change to either changes `policy_version`. Proof: a unit test that compares digests before and after the change (proposed rule, unverified; only if kept in version 1, keyed effects).
- [ ] A policy entry whose `schedule_to_close_timeout` does not exceed `schedule_to_start` by at least one `start_to_close` is rejected at load. Proof: a policy load test with three values on each side of the limit (proposed rule, unverified; only if kept in version 1, keyed effects).
- [ ] A keyed effect that waits in a queue with no Worker maps by the Schedule-To-Start row and parks, and does not map by the unknown row. Proof: a dev server test with an unreachable effect queue and the default timeouts (only if kept in version 1, keyed effects).
- [ ] The tool author guidance states that a permanent failure must be raised with the reserved type and `non_retryable=True`, and that a generic wrapper makes the failure retryable. Proof: a docstring or README text that cites [canonical specification](../canonical-documents.md#specification), INV-1, *Effect Activities*.
- [ ] The reserved field name is recorded as a one way door in the guidance. Proof: a text check that the decision note names the field and the date of freeze.

#### Dependencies and blockers

- Blocked by DSR-0.10 (retention window record), DSR-2.1 (key and ordinal state) and DSR-2.3 (outcome table).
- Conditional on DSR-0.2: keyed effects. Every criterion above carries `(only if kept in version 1, keyed effects)` so the ticket can shrink or become SUPERSEDED.
- Blocks DSR-2.9. Related to DSR-2.6, which compares engine tools only.

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), INV-1, *Effect Activities* (keyed retry policy, `ToolDefinitiveError`); INV-5, *Effect identity* and *What the key gives and does not give*.
- Assumption rows A-11, A-45 and A-47.
- Idempotency key guidance: https://docs.temporal.io/activity-definition#idempotency
- Retry policy and fixed count retries: https://docs.temporal.io/encyclopedia/retry-policies#default-behavior and https://docs.temporal.io/design-patterns/fixed-count-retries#disabling-retries-entirely
- Fork `_workflow.py` (the `activity_as_tool` shape): https://github.com/osamastro7-droid/ai-integrations/blob/69f5497d3d3dec7ad3269c72ff266c2931c9f379/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_workflow.py

#### Open questions

- Tool author: the key field name `idempotency_key` is a one way door. Confirm it before the first external service sees it.
- Plugin engineer: the default Schedule-To-Close of 10 minutes must change if the load rule above requires a larger value than the Schedule-To-Start of 10 minutes plus one Start-To-Close. Choose the new default and record it.
- Plugin engineer: review item R6-06 asks about a keyed `redo` after a park that outlasts the key retention window. The answer belongs to DSR-3.3 and DSR-0.10.
- A claim about a real external service needs an official sample or a service document. None was inspected.
- Plugin engineer: split in review if the retention check and key stability tests become their own ticket.

### DSR-2.6 Match engine behavior by differential test

Status: OPEN

October 9 source reconciliation: [the maintained release-check comparison](../proposals/distributed-recovery/2026-10-08/priority-sweep/coverage.md#october-9-release-check-reconciliation) owns prospective comparisons for hook failures, trusted settings, override flags, native records, session copies, nested inputs and resume prompts. Wrong assumptions can permit an effect, lose pending identity or alter recovery input. Compare the pinned public port against the selected governed runtime; the wider version report is not local qualification. Status and acceptance criteria are unchanged.

- Type: Verification
- Priority: High
- Estimate: 3 points (confidence 75 percent)
- Labels: Type: Verification, Topic: Effects
- Parent: DSR-P2
- Blocked by: DSR-2.2, DSR-2.4
- Blocks: DSR-2.9
- Related: DSR-2.5
- Retires: A-39
- Informs: none
- Owner role: Plugin engineer

#### Context

The engine defers a built in effect call and never runs it, so the plugin must supply the behavior. The model must see the same tool result that the engine would give. The specification requires a differential test per supported tool, with a relative path case ([canonical specification](../canonical-documents.md#specification), Interfaces, *Effect executor contract*).

**Complete Issue 31 disposition (2026-10-08)**

October 8 full issue sweep: [I31-H3 and route comparison](../proposals/distributed-recovery/2026-10-08/priority-sweep/coverage.md) adds the reported native replay port as a prospective comparator, source-pinned only when public. Compare initial segment, synthetic-result resume, selected original pending recovery and bounded native toolstep separately. Required observations per adopted route: exact hook/callback counts, permitted and denied physical Bash, ask/deny/missing or suppressed hook, exact IDs/inputs/results, native file records and Read/Edit/Write pre/postimages. Include 97196 user-message/ignored-defer and 97358 trailing-notification/result ordering cases. A stream-closure error is not policy enforcement; absent callback is not callback PASS. Preserve synthetic DEFECT and selected original-pending evidence without generalization. Child/parallel positive design is DSR-7.4; this ticket does not silently deliver it.

#### Problem

Nothing yet shows that the executor reproduces the engine's text, error shape and edge rules for Bash, Write and Edit. Bash runs with `work/` as its working directory while the engine uses the run directory, so a relative path means a different place. A mismatch changes how a model retries.

#### Scope

- A test harness that runs the same scripted call twice: once inside the engine with no deferral, and once through the executor, then compares the tool result that the model receives.
- Cases for Bash, Write and Edit that include success, a failed command, a not unique Edit match, `replace_all`, an overwrite, and a read before edit requirement.
- A relative path case that records the difference between the engine working directory and the executor working directory.
- A recorded list of every difference, each marked as accepted with a reason or fixed.

#### Out of scope

- Keyed author tools, which the engine does not run.
- A real model. The test uses the fake Messages API of the plugin test rig.
- Isolation and containment tests (DSR-2.7 and Phase 4).

#### Acceptance criteria

- [ ] For each of Bash, Write and Edit, the executor result and the engine result are identical for the success case. Proof: a differential test run with captured pairs of results ([canonical plan](../canonical-documents.md#plan), M2 Checks, EV-65 V-01).
- [ ] For each tool, the error cases produce the same `is_error` value and the same message class. Proof: captured pairs for a failed command, a missing file and a non unique Edit match.
- [ ] A relative path case runs through both paths, and the recorded difference is stated. Proof: the test output and a short list that names the difference between `work/` and the run directory.
- [ ] A rule that the engine enforces, such as a read before edit requirement, is reproduced in the executor only when the test shows the engine enforces it. Proof: a test that shows the engine behavior and the executor behavior side by side.
- [ ] The test runs on the plugin's minimum engine and on the newest engine, or the gap is stated. Proof: two recorded runs with the version printed by `claude -v` ([canonical plan](../canonical-documents.md#plan), *Stack*).
- [ ] Every difference is recorded as accepted or fixed. Proof: a list in the ticket closing note that has no unclassified entry.

#### Dependencies and blockers

- Blocked by DSR-2.2 (Bash executor) and DSR-2.4 (Write and Edit executor).
- Blocks DSR-2.9.

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), Interfaces, *Effect executor contract*; INV-5, *Repeatable mode*.
- Assumption row A-39 and brief 08 V-01.
- Plan test rig description: [canonical plan](../canonical-documents.md#plan), *Stack*.
- Fork `_runner.py` (engine options and result handling): https://github.com/osamastro7-droid/ai-integrations/blob/69f5497d3d3dec7ad3269c72ff266c2931c9f379/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_runner.py

#### Open questions

- Plugin engineer: the fake Messages API cannot serve the engine's auto mode classifier calls. State whether any case depends on auto mode.
- Plugin engineer: decide whether the newest engine run needs the dependency cooldown override ([canonical plan](../canonical-documents.md#plan), *Stack*).
- The ticket does not assume a real model result. A real model confirmation belongs to Phase 5, DSR-5.8.

### DSR-2.7 Contain process trees, cancellation, shutdown and payload size

Status: OPEN

October 9 source reconciliation: [the maintained release-check comparison](../proposals/distributed-recovery/2026-10-08/priority-sweep/coverage.md#october-9-release-check-reconciliation) records reported full-file toolUseResult exclusion. Compare payload/privacy behavior with existing limits before reuse; unnecessary file capture can expose content or inflate history. Launcher/lock fixes and Worker-kill tests do not prove exact-incarnation descendant death or distributed cleanup. Status and acceptance criteria are unchanged.

- Type: Build
- Priority: High
- Estimate: 4 points (confidence 65 percent)
- Labels: Type: Build, Topic: Effects
- Parent: DSR-P2
- Blocked by: DSR-2.1, DSR-2.2
- Blocks: DSR-2.9
- Related: none
- Retires: A-40, A-41, A-29 (M2 part of each)
- Informs: A-28
- Owner role: Plugin engineer

#### Context

Effects must end cleanly and must stay inside payload limits. Cancellation reaches an Activity only through a heartbeat. A Worker shutdown cancels in flight Activities after the graceful timeout. One payload is limited to 2 MB. The specification sets explicit values for each ([canonical specification](../canonical-documents.md#specification), INV-1, *Cancellation and shutdown* and *Heartbeats and liveness*; INV-3, *Payload size and the transcript*; INV-7, *Effect isolation*).

**Complete Issue 31 disposition (2026-10-08)**

October 8 full issue sweep: [payload and containment proof](../proposals/distributed-recovery/2026-10-08/priority-sweep/coverage.md) requires matching converter/driver identities on all clients/Workers, codec/reference exposure checks, threshold boundaries, upload/retrieve corruption and failure, retained live/reset/replay objects and orphan cleanup. Temporal External Storage payload offload is existing preview prior art, not a CLI SessionStore or workspace snapshot. Inject result upload failure after a physical effect with DSR-2.3 and require no repeat. Source-pin launcher/lock default refusal versus opt-out and fail before effects when required launch/lock/hook is unavailable. Queue separation must be observed, not inferred from a proposal. No driver install, opt-out or new backend is authorized.

#### Problem

None of the containment and cap behavior exists. A daemonized child can outlive the reported outcome. A large Write input lands in history at least twice. A silent engine hangs a segment unless a watchdog ends it.

#### Scope

- Process tree wait: the executor waits for the whole tree before it reports, kills the tree on cancellation, and tracks descendants with a control group, a subreaper, or a PID namespace as a proposal. The mechanism is open ([canonical specification](../canonical-documents.md#specification), INV-7).
- Heartbeats for every effect on a timer, a silence period of none by default for effects, and a segment supervisor that heartbeats on engine output and a 10 second timer with a silence watchdog.
- Cancellation types: TRY_CANCEL for safe repeatable effects, WAIT_CANCELLATION_COMPLETED for claimed effects. Preserve the exceptional Edit's one attempt policy.
- Worker shutdown: an explicit graceful shutdown timeout above the p99 effect time and a SIGTERM handler that calls the Worker shutdown.
- Caps: the 64 KiB output cap with the full output in a file, stderr truncation in failure messages, and a deferred Write above a threshold staged by reference and content hash.

#### Out of scope

- Isolation by user, container or PID namespace (Phase 4, DSR-4.1). This ticket records the residual until then.
- The SIGTERM test inside the Kubernetes grace period (Phase 5, DSR-5.7).
- Event loop lag and process containment measurement under load (Phase 4, DSR-4.4).

#### Acceptance criteria

- [ ] A daemonized child and a shell level background command are contained by the process tree wait, or reported as a stated residual. Proof: two tests, one with a `setsid` child and one with a background command, with the observed result written in the test ([canonical plan](../canonical-documents.md#plan), M2 Checks).
- [ ] Cancellation waits for the in flight effect and then ends. Proof: a Workflow cancel test for a claimed effect that shows the Workflow learns the outcome before it ends.
- [ ] A 3 MB Write and a 5 MB command output stay under the caps, with the full output in a file and the path in the result. Proof: two tests that assert payload size in history and file content (A-29 M2 part).
- [ ] A silent engine is killed by the watchdog and a quiet long effect is not. Proof: a segment test with a silent fake engine and an effect test with a long quiet command.
- [ ] Every effect Activity heartbeats, so a cancellation request reaches it. Proof: a test that cancels a long command and shows the executor stops it at a heartbeat.
- [ ] The Worker graceful shutdown timeout is set explicitly and a SIGTERM calls the Worker shutdown in a local test. Proof: a process level test that sends SIGTERM and shows in flight completion within the timeout.
- [ ] Stderr in a failure message is truncated to a stated size. Proof: a test with a large stderr stream.

#### Dependencies and blockers

- Blocked by DSR-2.1 (workspace) and DSR-2.2 (Bash executor).
- Blocks DSR-2.9.

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), INV-1, *Cancellation and shutdown*, *Heartbeats and liveness*; INV-3, *Payload size and the transcript*; INV-7, *Effect isolation*.
- Assumption rows A-40, A-41 and A-29.
- Shutdown behavior: https://docs.temporal.io/encyclopedia/workers/worker-shutdown#worker-shutdown-behavior
- Cancellation and heartbeat: https://docs.temporal.io/develop/typescript/workflows/cancellation#cancel-an-activity and https://docs.temporal.io/design-patterns/long-running-activity
- Payload limit: https://docs.temporal.io/evaluate/cloud/limits#programming-model-level
- External Storage: https://docs.temporal.io/external-storage
- Fork `_runner.py` (subprocess supervisor): https://github.com/osamastro7-droid/ai-integrations/blob/69f5497d3d3dec7ad3269c72ff266c2931c9f379/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_runner.py

#### Open questions

- Security owner: the containment mechanism (control group, subreaper, PID namespace) depends on the isolation level from DSR-0.6.
- Plugin engineer: the Python Worker shutdown default and the missing SIGTERM handler are relayed claims. Confirm both against the pinned SDK in a local test.
- Plugin engineer: split in review if caps and shutdown become their own ticket.

### DSR-2.8 Refuse version mismatches with a contract version

Status: SUPERSEDED

Scope disposition (2026-10-01): DSR-0.2 defers the additional `contract_version` integer. The historical body below is not active implementation scope. DSR-2.3 owns all retained package, policy and engine mismatch checks and the M2 part of A-16. Relationship links remain for phase exit coverage.

- Type: Build
- Priority: High
- Estimate: 2 points (confidence 75 percent)
- Labels: Type: Build, Topic: Versioning
- Parent: DSR-P2
- Blocked by: DSR-2.1, DSR-2.2
- Blocks: DSR-2.9
- Related: none
- Retires: none
- Informs: A-30, A-50
- Owner role: Plugin engineer

#### Context

A Pinned run whose queue has no Workers on its version sends its Activities to the current version of that queue. An effect could then run on different executor code, silently. The proposed fix puts `package_hash`, `policy_version`, `engine_version` and a `contract_version` integer in the segment and effect inputs, and each executor refuses a mismatch with an `ExecutorFault` error before it creates any claim ([canonical specification](../canonical-documents.md#specification), INV-2, *Versioning*, *Pinned rollout*).

#### Problem

The package, policy and engine versions do not change when only executor code changes, which is why the contract version exists. Nothing carries or checks it yet.

#### Scope

- A `contract_version` integer constant that covers the claim file format and the key canonicalization, carried in the segment input and the effect input, and returned in the segment result.
- Checks in the segment runner and in the effect executor of package hash, policy version, engine version and contract version against the input, each refusing with `ExecutorFault`.
- The refusal happens before any claim file is created.
- The `AgentState` field `contract_version` and its use at a handover. Proposed rule, unverified (review item R6-03): one integer names the claim file format and the key canonicalization, and it stays separate from `canonicalization_version` and from the hook contract version in the build identifier. At a handover the new run carries the stored value, and the executor compares for exact equality. A mismatch raises `ExecutorFault` and parks the run. A supported range with a claims tree migration is not part of version 1.

#### Out of scope

- Worker Deployment rollout and drain guidance (Phase 5, DSR-5.1).
- The park action after `ExecutorFault` (Phase 3, DSR-3.3).
- The outcome mapping of the error (DSR-2.3).

#### Acceptance criteria

- [ ] An effect input with a mismatched package hash, policy version or engine version is refused with `ExecutorFault` before any claim, and zero claim files exist afterward. Proof: three executor tests that list the claims directory after the refusal.
- [ ] An effect input with a mismatched contract version is refused the same way (only if kept in version 1, contract version). Proof: an executor test that lists the claims directory.
- [ ] A segment input with a mismatched contract version is refused before the engine starts (only if kept in version 1, contract version). Proof: a segment test with a counter on engine starts.
- [ ] The segment result carries `package_hash`, `policy_version`, `engine_version` and `contract_version`, and the Workflow stores them. Proof: a Workflow test that reads the stored values ([canonical specification](../canonical-documents.md#specification), INV-2, *Workspace*).
- [ ] At a handover the new run carries the stored `contract_version`, and an executor on a different value refuses and parks the run (proposed rule, unverified; only if kept in version 1, contract version). Proof: a Workflow test that hands over and dispatches to an executor with a changed constant.
- [ ] The assumption row A-16 and the plan retirement row name the contract version beside the other three fields. Proof: a diff of both rows (recorded in DSR-2.9).
- [ ] A changed claim file format or key canonicalization requires a new contract version integer. Proof: a unit test that fails when the format version constant in the code and the `contract_version` constant diverge from a recorded pair.
- [ ] The Workflow tells the model nothing for these refusals. Proof: covered by the DSR-2.3 mapping test, linked from this ticket.

#### Dependencies and blockers

- Blocked by DSR-2.1 (manifest and state) and DSR-2.2 (executor entry point).
- Conditional on DSR-0.2: the contract version. If version 1 drops it, only the three version checks remain and the criteria marked `(only if kept in version 1, contract version)` are removed.
- Blocks DSR-2.9.

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), INV-2, *Versioning* (Pinned rollout and the proposed fix); INV-1, *Outcome mapping* row 2.
- Assumption row A-16 (M2 part).
- Versioning behavior: https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning#choosing-behavior
- Fork `_runner.py` and `_models.py` for the segment input and result: https://github.com/osamastro7-droid/ai-integrations/blob/69f5497d3d3dec7ad3269c72ff266c2931c9f379/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_models.py

#### Open questions

- Plugin engineer: confirm exact equality over a supported range as the version 1 rule, or choose the range and a claims tree migration.
- Plugin engineer: the claim that a Pinned run's Activities move to the current version when the queue has no pinned Workers is relayed from a critic. Confirm it in DSR-5.1.
- No official sample repository was inspected for version carrying in Activity input.

### DSR-2.9 Review Phase 2 evidence and decide continue or redesign

Status: OPEN

- Type: Documentation
- Priority: High
- Estimate: 2 points (confidence 85 percent)
- Labels: Type: Documentation, Topic: Assumptions
- Parent: DSR-P2
- Blocked by: DSR-2.1, DSR-2.2, DSR-2.3, DSR-2.4, DSR-2.5, DSR-2.6, DSR-2.7, DSR-2.8
- Blocks: DSR-3.1
- Related: none
- Retires: none
- Informs: A-04, A-05, A-08, A-09, A-10, A-11, A-16, A-39, A-45, A-47
- Owner role: Plugin engineer

#### Context

Each phase ends with an exit review. The review updates the specification assumption rows and the plan milestone text with the evidence, and records a continue or redesign decision. A contradicted assumption stops the next phase until the design change is recorded (`tickets/README.md`, *Phase gates*). The Phase 2 exit gate lists A-04, A-05, A-08, A-09, A-10, A-11, A-16 (M2 part), A-39, A-45 and A-47 (`tickets/README.md`, *Hierarchy*).

#### Problem

The evidence from the Phase 2 build tickets is spread across tests and notes. The assumption rows still read untested, inferred or proposed fix. The next phase builds the wait loop and parked runs on the effect outcomes, so a wrong Phase 2 result would spread.

#### Scope

- Read the closing evidence of DSR-2.1 to DSR-2.8.
- Update each listed assumption row in the specification with its status and the proving artifact, or with the contradicting evidence and the design change.
- Update the plan milestone M2 text and the retirement table with the evidence.
- Record one decision: continue to Phase 3 or redesign, with the reasons and the owner role.
- Record which guarantees survived the version 1 scope decision (DSR-0.2) and which tickets became SUPERSEDED.

#### Out of scope

- New build work. A failed criterion returns to its ticket.
- Assumption rows that belong to other phases.

#### Acceptance criteria

- [ ] Every retained Phase 2 assumption is verified at source with evidence or contradicted with a recorded design change. A-11, A-45 and A-47 remain superseded by DSR-0.2; A-53 and the executor part of A-54 require test evidence. Proof: a specification diff per gate id.
- [ ] The M2 text in the plan and its retirement table match the evidence. Proof: a diff of the plan with the artifact names that prove each check.
- [ ] A continue or redesign decision is recorded with date, reasons and owner role. Proof: a decision record in the Phase 2 closing note.
- [ ] The record confirms Option R: retain both claim files; exclude keyed effects, claims high water and the additional contract version; verify the three retained mismatch checks in DSR-2.3. Proof: the closing note and recorded supersessions, not deferred implementation evidence.
- [ ] No Phase 3 ticket starts while a contradicted Phase 2 assumption lacks a recorded design change. Proof: the decision record names each open contradiction or states that none exists.
- [ ] The review checks that the full test suite passes without credentials. Proof: a recorded test run output.

#### Dependencies and blockers

- Blocked by every other Phase 2 ticket.
- Blocks DSR-3.1.

#### Source evidence

- `tickets/README.md`, *Phase gates* and *Hierarchy*.
- [canonical plan](../canonical-documents.md#plan), *Assumptions retired by milestone*.
- [canonical specification](../canonical-documents.md#specification), *Assumptions and risks if wrong*.

#### Open questions

- Plugin engineer: confirm retained wrapper and mismatch refusal evidence against Option R; do not reopen deferred keyed defaults or claims high water. A-22 remains Phase 1 and Phase 5 engine compatibility work.
