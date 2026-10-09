# Phase 3 tickets

### DSR-3.1 Carry waits and state across Continue-As-New

Status: OPEN

- Type: Build
- Priority: High
- Estimate: 5 points (confidence 60 percent)
- Labels: Type: Build, Topic: Approvals, Topic: Engine
- Parent: DSR-P3
- Blocked by: DSR-2.9
- Blocks: DSR-3.2, DSR-3.3, DSR-3.4, DSR-3.6, DSR-3.7
- Related: none
- Retires: A-42, A-29 (M3 part)
- Informs: A-20
- Owner role: Plugin engineer

#### Context

A human wait can last days. The fork keeps its waiting calls only in memory and reaches a handover only after a tool call returns. The specification replaces that with a timer bounded wait loop, a wake interval of 6 hours, absolute deadlines, a two phase check that consumes a recorded answer before it checks the handover triggers, and an entry branch that re enters a carried wait ([canonical specification](../canonical-documents.md#specification), INV-4, *The wait state machine* and *What travels across Continue-As-New*). The plan names the same artifacts in milestone M3 ([canonical plan](../canonical-documents.md#plan), M3).

#### Problem

Without this loop, a question pending at a handover is lost, an answer and a handover in one Workflow Task can drop the answer, and a wait aged from its original registration can trigger a handover on every wake. The carried state also approaches the 2 MB payload limit if it is not bounded.

#### Scope

- A loop of timer bounded `wait_condition` calls, each timer `min(wake interval, deadline - now)` with a 1 second floor, covering every pending decision kind.
- The two phase pass: consume any recorded answer into the pending result, then check the Continue-As-New triggers (server suggestion, handover size estimate, target Deployment Version change, wait age, periodic wake).
- The handover that carries the paused call (id, name, input, key, ordinal), the absolute deadline and the question payload, and the `_loop` entry branch that re enters a carried wait without a new segment against a session that ends at an unanswered `tool_use`.
- The stamp `wait_started_in_run` set at each run's wait entry, the `registered_at` audit value kept but never used for age, and a handover cooldown of one wake interval.
- Draining of handlers before Continue-As-New with `workflow.all_handlers_finished`.
- The `AgentState` fields from the canonical list that this loop needs, including the bounded `answered_decision_ids` (256) and the state size assertion.
- A question answer path for the Workflow side only. The Update handler and its token are DSR-3.2.

#### Out of scope

- Signed tokens and the interceptor (DSR-3.2).
- Parked runs and the retained signed resume actions (DSR-3.3).
- Search Attributes and discovery (DSR-3.4).
- Update behavior at the boundary and under concurrency as a verification result (DSR-3.6).
- Versioning options at handover beyond passing them through (Phase 5).

#### Acceptance criteria

- [ ] A question stays pending across a Worker crash and across 30 Continue-As-New handovers, and is answered once. Proof: a dev server test forced by the `limited` fixture or a small `continue_as_new_after_events` value with a short wake interval ([canonical plan](../canonical-documents.md#plan), M3 Checks).
- [ ] The carried state stays under a stated size after 30 handovers. Proof: a size assertion on the serialized `AgentState` in the same test, tied to the 2 MB payload limit (A-29 M3 part).
- [ ] An answer and a Continue-As-New trigger in one Workflow Task do not lose the answer. Proof: a Workflow test that records the answer in the same activation as a scripted suggestion and shows the answer in the next run.
- [ ] A recorded answer wins over a timeout in the same activation, and a decision at or after the deadline is not accepted. Proof: two Workflow tests at the deadline boundary ([canonical specification](../canonical-documents.md#specification), INV-1, *Human waits*).
- [ ] A wait with a deadline shorter than the wake interval expires on time. Proof: a time skipping test with a deadline of half the interval.
- [ ] A wait started in one run is not aged from its original registration after a handover, and a handover does not repeat on every wake. Proof: a test that counts handovers over five wakes (A-42).
- [ ] An approval and a Continue-As-New trigger in one activation do not lose the approval, and a `resume` accepted before a handover is applied by the new run. Proof: two Workflow tests that record the unapplied action field before the handover.
- [ ] A Workflow cancellation takes priority over a recorded decision. Proof: a test that cancels with a recorded answer present.
- [ ] The loop never starts a segment against a session that ends at an unanswered `tool_use`. Proof: a test that hands over during a wait and counts segment starts in the new run.
- [ ] New behavior is guarded by `workflow.patched`, and recorded histories from the fork and from Phase 2 replay. Proof: the Replayer over recorded histories ([canonical specification](../canonical-documents.md#specification), INV-3, *Determinism inside the Workflow*).

#### Dependencies and blockers

- Blocked by DSR-2.9 (Phase 2 continue decision).
- DSR-0.2 removes redo authority, not the exceptional Edit's retained uncertainty handling. Carry the parked cause, pending call and any uncertainty bookkeeping required by the specification's canonical state list. Ambiguous Bash never permits model continuation, and no carried field authorizes claim release or redo.
- Blocks DSR-3.2, DSR-3.3, DSR-3.4, DSR-3.6 and DSR-3.7.

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), INV-4, *The wait state machine*, *What travels across Continue-As-New*, *Update volume*; INV-2, *Versioning* (the wait age fields).
- Assumption rows A-29 and A-42 (A-42 is a proposed fix).
- Continue-As-New guidance: https://docs.temporal.io/develop/python/workflows/continue-as-new
- Approval with timeout pattern: https://docs.temporal.io/design-patterns/approval#basic-approval-with-timeout
- Event limits: https://docs.temporal.io/evaluate/cloud/limits#programming-model-level
- Fork `_workflow.py` (`_loop`, the handover and `AgentState`): https://github.com/osamastro7-droid/ai-integrations/blob/69f5497d3d3dec7ad3269c72ff266c2931c9f379/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_workflow.py

#### Open questions

- Plugin engineer: the default wake interval, handover size, wait age and cooldown are configuration values that M3 must measure. Record the measured values.
- Plugin engineer: review item R5-13 asks whether the daily wait age handover should be opt in. Decide in version 1.
- Plugin engineer: this ticket stays one ticket at 5 points and is flagged for split review. A split into the wait loop and the carried state is recommended if the estimate grows. The id DSR-3.1 does not change.
- The claim that a Signal wakes a waiting Workflow Task for a version change is relayed. Confirm in DSR-5.1.
- No official sample repository was inspected for a timer bounded wait.

### DSR-3.2 Verify signed tokens in an interceptor

Status: OPEN

- Type: Build
- Priority: High
- Estimate: 4 points (confidence 65 percent)
- Labels: Type: Build, Topic: Approvals
- Parent: DSR-P3
- Blocked by: DSR-0.7, DSR-3.1
- Blocks: DSR-3.3, DSR-3.6, DSR-3.7
- Related: none
- Retires: A-12, A-13, A-14, A-15 (M3 part), A-56 (M3 part)
- Informs: A-20, A-33
- Owner role: Security owner

#### Context

No documented mechanism lets an Update validator read an authenticated caller identity. The design puts one authenticated gateway in front of the Update API and attaches a signed token to each answer, approval and `resume` ([canonical specification](../canonical-documents.md#specification), INV-7, *Approver identity*). The handler base class declares the names and the plugin installed inbound interceptor is the one place that rejects an unsigned `decide` Signal or approval Update. The gateway owner comes from DSR-0.7.

#### Problem

The token definitions, the interceptor, the base class and the sandbox change that verification needs are proposed fixes with no verification. A user Workflow that declares its own handlers can replace a handler body, and a Signal handler that raises stalls the run. Assumptions A-12, A-13, A-14 and A-15 are open.

#### Scope

- The token: audience (Workflow Id and lineage id), purpose (`answer`, `approve`, `resume`), subject (decision id or park id), digests of the question payload and the decision payload over canonical JSON, expiry, nonce, key id and token version.
- Public key verification in an Update validator, with the sandbox change that the verification package needs, and the rule that the Workflow judges expiry with `workflow.now()`.
- Rejection of repeats with the carried answered ids, rejection of an unknown token version and of a version below the run input minimum, and a per park id for `resume`.
- The `answer_question` and `resume` Updates with validators and no answer Signal, with the decision id as the client side Update id.
- The Workflow base class that declares the Update handlers, validators and Queries, and the inbound interceptor that rejects a `decide` Signal or an approval Update without a valid token when `tool_policy` is set. A missing or invalid token on a Signal is dropped and logged, and never raises.
- A cross language digest test against a gateway written in another language.
- Interceptor replay safety and threat model (proposed and unverified, from review item R6-05): the interceptor accept or drop logic is replay relevant code, so it falls under the same `workflow.patched` and recorded history replay policy as the Workflow class. The documented threat model is an external caller and a trusted Workflow author. A Signal flood from an unauthenticated sender is bounded by the gateway credential rule, and the interceptor does not bound it.

#### Out of scope

- The gateway itself and its deployment (decided in DSR-0.7).
- Key rotation for a waiting run. Version 1 states termination of the affected runs as the response to a compromised key.
- Parked run actions (DSR-3.3).
- Codec coverage of Update payloads (Phase 5, DSR-5.2).

#### Acceptance criteria

- [ ] An unsigned, forged, expired, cross question, substituted decision and replayed `resume` token is rejected. Proof: six validator tests, each asserting rejection before the Update is recorded in history ([canonical plan](../canonical-documents.md#plan), M3 Checks).
- [ ] A forged Update sent directly to the frontend is rejected. Proof: a dev server test that sends an Update with the client API and an unsigned or wrongly signed token (A-12, A-14).
- [ ] Signature verification runs in the sandbox without failing a Workflow Task. Proof: a Workflow test that runs the validator on a valid and an invalid token and shows no task failure (A-12).
- [ ] A token below the minimum version is rejected, a second answer and a replayed token are rejected, and the carried answered ids survive a handover. Proof: three tests, the last across a forced handover (A-13).
- [ ] A `resume` token replayed after a Workflow reset is rejected through the per park id. Proof: a reset test with a captured token.
- [ ] An unsigned `decide` Signal and an approval Update with no token are rejected by the interceptor even when a subclass replaces the handler body, and the run does not stall. Proof: a test with an overriding subclass and a check that the next Workflow Task completes (A-15 M3 part).
- [ ] A direct `decide` Signal without a token is dropped, logged and does not stall the run when `tool_policy` is set. Proof: a test that counts log lines and Workflow Task failures.
- [ ] The canonical JSON digest agrees with a gateway written in another language. Proof: a digest vector file used by two language tests.
- [ ] The interceptor is replay safe: a history recorded with the interceptor installed replays without non determinism, and a change to a token rule, the expiry rule or the minimum version handling is guarded by `workflow.patched`. Proof: a Replayer run over a recorded history, and a replay test that changes one rule and shows the guard keeps the old result (proposed rule, unverified).
- [ ] The documented threat model states an external caller and a trusted Workflow author, and states that a Signal flood is bounded by the gateway credential rule. Proof: a README text check that names both statements (proposed rule, unverified).
- [ ] The tests state which assumption about the identity of the caller they rely on. Proof: a note in the ticket closing record that names the evidence for A-14.

#### Dependencies and blockers

- Blocked by DSR-0.7 (gateway owner) and DSR-3.1 (the wait loop that records answers).
- Blocks DSR-3.3, DSR-3.6 and DSR-3.7.
- The token field set is a one way door once gateways sign it. Freeze the field set before DSR-3.3 builds on it.

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), INV-7, *Approver identity*; INV-2, *Versioning* (handler ownership); INV-4, *Update volume*; Interfaces, *Workflow messages*.
- Assumption rows A-12, A-13, A-14 and A-15.
- Message passing: https://docs.temporal.io/encyclopedia/workflow-message-passing and https://docs.temporal.io/develop/python/workflows/message-passing#updates
- Python sandbox limits: https://docs.temporal.io/develop/python/best-practices/python-sdk-sandbox
- Fork `_workflow.py` (the `decide` Signal, `validate_decision` and the Update machinery): https://github.com/osamastro7-droid/ai-integrations/blob/69f5497d3d3dec7ad3269c72ff266c2931c9f379/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_workflow.py

#### Open questions

- Security owner: the key set source, key id policy and the minimum version bump process need a record.
- Gateway owner: confirm that only the gateway credentials may send Updates. A-14 stays an inference until this is confirmed.
- Plugin engineer: the claim that the Python SDK checks only the decorator on an override is read by a critic and relayed. Confirm it in a test.
- Plugin engineer: the claim that a non failure exception in a Signal handler stalls the run is relayed. Confirm it in a test.
- Plugin engineer: the third party verification package is outside the sandbox passthrough set. The change affects every user Worker. Confirm the owner of that change.
- Security owner: the estimate is 4 points with low confidence because the interceptor design is untested on the pinned SDK.

### DSR-3.3 Park runs and apply the retry, checkpoint resume and abort actions

Status: OPEN

- Type: Build
- Priority: High
- Estimate: 4 points (confidence 65 percent)
- Labels: Type: Build, Topic: Approvals, Topic: Effects
- Parent: DSR-P3
- Blocked by: DSR-0.8, DSR-2.3, DSR-3.1, DSR-3.2
- Blocks: DSR-3.5, DSR-3.7, DSR-3.8
- Related: none
- Retires: A-24 (M3 part)
- Informs: A-08, A-10, A-16
- Owner role: Plugin engineer

#### Context

A run parks on a persistent fault, exposes a Query and waits for a signed `resume` Update bound to a park sequence number. The retained actions are `retry`, `resume_from_checkpoint` and `abort` for causes where they are safe. DSR-0.2 defers `redo`; DSR-0.8 must decide the ambiguous Bash procedure. Until that decision, no action may clear claims, repeat Bash or return an unknown outcome to the model. A `reprepare` step is not another action ([canonical specification](../canonical-documents.md#specification), INV-1, *Parked runs*). Cause records come from DSR-2.3.

#### Problem

The parked phase and the park causes have no implementation, and the classification of credential and quota errors is untested. A run that fails after its retries must wait for an operator and must not lose a paid session.

#### Scope

- The parked phase with a park sequence number and a per park id, the Query for the parked state, and the park causes: exhausted segment retries, contract violation, credential or quota error, first Schedule-To-Start timeout on an effect queue, and `ExecutorFault`.
- Credential and quota errors marked non retryable at the segment Activity, and a segment Schedule-To-Close bound of 1 hour with the fork's 10 minute Start-To-Close.
- `retry` and `resume_from_checkpoint` for supported safe causes, returning the phase to running and delivering a recorded safe `NOT_RUN` when applicable. Neither action may imply that ambiguous Bash is safe. DSR-0.8 remains OPEN for that cause.
- `abort`, which ends the Workflow with a stated aborted result and calls cleanup.
- The `reprepare` step that lays out the run directory and the claims directory again.

#### Out of scope

- Token verification (DSR-3.2).
- `redo`, `release_claim` and redo authority over uncertainty bookkeeping are deferred by DSR-0.2; DSR-3.8 is SUPERSEDED. Retained exceptional Edit uncertainty fields follow the specification's canonical state list.
- Reset detection proof (DSR-3.5).
- The janitor and snapshot restore detection beyond parking on a lower counter (Phase 4).
- The paid retry rate measurement (Phase 5, DSR-5.7).

#### Acceptance criteria

- [ ] A run parks after exhausted segment retries, a contract violation, a quota error, an effect queue timeout and an executor fault, and names the cause in the Query. Proof: five Workflow tests with scripted failures ([canonical plan](../canonical-documents.md#plan), M3 Checks).
- [ ] A credential or quota error does not retry at the segment Activity and parks the run, and a transient rate limit error retries inside the Schedule-To-Close bound. Proof: two tests with scripted provider errors (A-24 M3 part).
- [ ] For a supported safe cause, `retry` starts a new segment attempt with the same input and returns the phase to running. Proof: a test with a signed `resume` token and a count of segment starts.
- [ ] For a supported safe cause, `resume_from_checkpoint` starts a segment at the last checkpoint. Proof: a test comparing the session checkpoint used. Ambiguous Bash remains governed by the open DSR-0.8 decision.
- [ ] For a safe cause, supported resume actions deliver the recorded `NOT_RUN` when applicable. An ambiguous Bash park never delivers a model facing `OUTCOME_UNKNOWN`, clears a claim or starts a segment while DSR-0.8 is unresolved. Proof: positive safe cause tests and rejection tests for ambiguous Bash actions.
- [ ] `abort` ends the Workflow with a stated aborted result and calls cleanup. Proof: a test that checks the result and the cleanup call.
- [ ] A `resume` token with a stale park id or sequence number is rejected. Proof: a test that replays a token after a second park.
- [ ] A parked run waits for days across handovers without failing, and the Query returns the parked state after each handover. Proof: a time skipping test with 20 wakes while parked.

#### Dependencies and blockers

- Blocked by DSR-0.8 (reset policy), DSR-2.3 (outcome mapping and park causes), DSR-3.1 (wait loop) and DSR-3.2 (tokens).
- Blocks DSR-3.5 and DSR-3.7. The DSR-3.8 link remains historical phase coverage for a SUPERSEDED ticket, not redo authorization.

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), INV-1, *Parked runs*, *Outcome mapping*, *Segment Activity*; INV-5, *The lineage id*.
- Assumption A-24 for retained park and segment behavior. A-23 is superseded provenance for deferred redo, not active proving work.
- Retry policy and non retryable types: https://docs.temporal.io/encyclopedia/retry-policies#default-behavior
- Saga pattern guidance: https://docs.temporal.io/design-patterns/saga-pattern#best-practices
- Fork `_workflow.py` and `_runner.py` for the failure path: https://github.com/osamastro7-droid/ai-integrations/blob/69f5497d3d3dec7ad3269c72ff266c2931c9f379/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_workflow.py

#### Open questions

- Plugin engineer: review item R6-02 notes that the snapshot counter covers claimed effects only and has no rebaseline after `reprepare`. Decide the rebaseline rule (for example, the `resume` action confirms a new baseline) before parking on a lower counter.
- The credential and quota error classification depends on provider error types that were not inspected. Mark as an open question for the Plugin engineer.

### DSR-3.4 Check Search Attributes at start and discover pending decisions with live output off

Status: OPEN

- Type: Build
- Priority: High
- Estimate: 3 points (confidence 70 percent)
- Labels: Type: Build, Topic: Approvals
- Parent: DSR-P3
- Blocked by: DSR-0.9, DSR-3.1
- Blocks: DSR-3.7
- Related: none
- Retires: A-32, A-33
- Informs: A-16, A-30, A-50
- Owner role: Plugin engineer

#### Context

Live output is off by default, so a question event cannot be the only way that an approver learns of a pending decision. The gateway discovers a pending decision through a Query and through the `AgentPhase` Search Attribute. An upsert of an unregistered Search Attribute stalls the Workflow Task, so the plugin sets all of its attributes at start and refuses a namespace that lacks them ([canonical specification](../canonical-documents.md#specification), Interfaces, *Events*; INV-6, *Logs, traces and visibility*). The registrant and the rollout order come from DSR-0.9.

#### Problem

The start check, the attribute set at start and the discovery path are proposed fixes. The stall claim comes from a public issue that a critic relayed. Without the start check a run can stop silently on an `AgentPhase` upsert.

#### Scope

- The Search Attributes `AgentPhase` (running, waiting_human, parked, completed), `PendingHumanInput`, `OldestPendingAt`, `PackageHash`, `PolicyVersion` and `EngineVersion`, set when the Workflow starts and updated at phase changes.
- A plugin start check that reads the operator service listing of registered attributes and refuses a start with a stated error when any are missing.
- A Query that returns pending decisions, the last effect outcomes and the parked state.
- The events `question_needed`, `effect_started` and `effect_ended` for viewers, carrying the key and mode and never the raw tool input.
- Discovery of a pending decision with live output off through the Query and the Search Attribute, and the alert source `OldestPendingAt` for the half timeout notice.
- A rule that no tool input, output, workspace path, question text or answer text appears in a Search Attribute.

#### Out of scope

- Registering the attributes in each namespace (decided and owned by DSR-0.9).
- The gateway software.
- The deadline attribute for the half timeout alert beyond a recorded decision (review item R5-13).
- Metrics and dashboards (Phase 5).

#### Acceptance criteria

- [ ] A start against a namespace without the registered attributes is refused by the plugin with a stated error that names each missing attribute. Proof: a dev server test on a namespace with no custom attributes ([canonical plan](../canonical-documents.md#plan), M3 Checks).
- [ ] The plugin sets all of its attributes at start, and a run never stalls a Workflow Task on an upsert. Proof: a dev server test with the attributes registered and a check of zero Workflow Task failures after 20 phase changes.
- [ ] With live output off, a gateway client discovers a pending decision through the Query and through a visibility query on `AgentPhase` equal to waiting_human. Proof: a test that starts a run, waits for the question, and finds it through both paths.
- [ ] `OldestPendingAt` holds the registration time of the oldest pending decision and clears when none remains. Proof: a Workflow test that reads the attribute before and after an answer.
- [ ] No Search Attribute value contains tool input, output, a workspace path, question text or answer text. Proof: a test that runs a scripted skill with sensitive strings and scans every attribute value.
- [ ] Events carry the key and mode and never the raw tool input. Proof: a test that scans the event payloads for the scripted input string.
- [ ] A stalled upsert claim is checked against the pinned SDK. Proof: a recorded test result that shows whether an unregistered upsert stalls the Workflow Task (A-32).

#### Dependencies and blockers

- Blocked by DSR-0.9 (who registers the attributes) and DSR-3.1 (the wait loop that sets the phase).
- Blocks DSR-3.7.

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), Interfaces, *Events*; INV-6, *Logs, traces and visibility*; INV-7, *Search Attributes*.
- Assumption rows A-32 and A-33.
- Search Attributes: https://docs.temporal.io/search-attribute
- Fork `_events.py`: https://github.com/osamastro7-droid/ai-integrations/blob/69f5497d3d3dec7ad3269c72ff266c2931c9f379/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_events.py

#### Open questions

- Gateway owner: confirm that the gateway polls the Query and the visibility listing, and set the poll interval.
- Plugin engineer: review item R5-13 asks for a uniqueness rule for a starter supplied lineage id and a deadline attribute. Decide whether either is in version 1.
- Plugin engineer: the operator service listing call name and its permission need a check against the pinned SDK. No official sample repository was inspected.

### DSR-3.5 Prove reset behavior for the lineage id and claim files

Status: OPEN

- Type: Verification
- Priority: High
- Estimate: 3 points (confidence 65 percent)
- Labels: Type: Verification, Topic: Effects, Topic: Workspace
- Parent: DSR-P3
- Blocked by: DSR-0.8, DSR-2.2, DSR-3.3
- Blocks: DSR-3.7
- Related: none
- Retires: A-06, A-07
- Informs: A-05, A-13, A-23
- Owner role: Plugin engineer

#### Context

A Workflow reset must keep the lineage id and run directory. A reset to the first Workflow Task may reseed `workflow.uuid4()` before its first call, so the starter mints the lineage id and passes it in the run input ([canonical specification](../canonical-documents.md#specification), INV-5, *The lineage id*). After a reset, an existing Bash claim refuses a second spawn and parks the run without a model result. Keyed service effects are excluded by DSR-0.2.

#### Problem

The seed claim comes from the Rust core and Python SDK by reading, not by running. The starter minted id is a proposed fix. A wrong lineage id after reset gives fresh claim identities and a fresh directory, allowing a completed Bash effect to run again.

#### Scope

- A reset test at a later Workflow Task that shows the lineage id, the run directory name, the effect key and the claim file refusal after the reset.
- A reset test to the first Workflow Task, with a starter supplied lineage id and without one, that compares the ids.
- The starter side: accept `lineage_id` in the run input, and use `workflow.uuid4()` only as the fallback.
- Detection of a reset by comparing the claim's `workflow_run_id` with the current run id, and the operator procedure that DSR-0.8 must record. No redo path is included.
- A `resume` token replay after a reset, linked to DSR-3.2.

#### Out of scope

- The runbook text itself (DSR-0.8 and Phase 5 documentation).
- Reset of a closed run beyond the patch retirement view (Phase 5, DSR-5.5).
- Volume restore from a snapshot (Phase 4).

#### Acceptance criteria

- [ ] A reset to a later Workflow Task keeps the lineage id and the run directory. Proof: a dev server test that resets after two effects and compares the stored id and the directory name (A-06 M3 part).
- [ ] After that reset, an existing claim refuses the Bash effect, parks without a model result and spawns nothing. Proof: a reset test counting spawns and subsequent segment starts.
- [ ] A reset to the first Workflow Task keeps the lineage id when the starter supplies it. Proof: a test that resets to the first task and compares the ids (A-07).
- [ ] A reset to the first Workflow Task without a starter supplied id is recorded as changing the id or not, with the observed result. Proof: the same test with the id omitted, and a recorded result that confirms or contradicts the inference.
- [ ] A claim whose stored run id differs from the current run id is recognized as written by an earlier run of the same lineage. Proof: a test that reads the refusal reason after a reset (only if kept in version 1, ordinal claim file, for the divergent command case).
- [ ] A different Bash command at the same ordinal after reset is refused and parks without model continuation. Proof: a test linked to the retained ordinal claim guard in DSR-2.2.
- [ ] A Workflow Id reuse gives a different lineage id from the first run. Proof: a test with the reuse policy that allows a duplicate.
- [ ] The result states whether a starter supplied id can collide between two starts. Proof: a recorded decision or a uniqueness test (review item R5-13).

#### Dependencies and blockers

- Blocked by DSR-0.8 (reset policy), DSR-2.2 (claimed executor and both claim files) and DSR-3.3 (the parked path).
- DSR-0.2 retains ordinal claim guards and removes keyed effects and redo. The operator reset procedure is not selected by this rebaseline.
- Blocks DSR-3.7.

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), INV-5, *The lineage id*; INV-1, *Claimed effect guard*.
- Assumption rows A-06 and A-07. Rust core and Python SDK seed behavior is cited in the specification as EV-115 and EV-116 and was read, not run.
- Workflow Id reuse: https://docs.temporal.io/workflow-execution/workflowid-runid#workflow-id-reuse-policy
- Fork `_workflow.py` (session id minted with `workflow.uuid4()`): https://github.com/osamastro7-droid/ai-integrations/blob/69f5497d3d3dec7ad3269c72ff266c2931c9f379/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_workflow.py

#### Open questions

- Plugin engineer: the API comment that a reset preserves `original_execution_run_id` is read at the API source and not re read in this pack. Confirm it by test.
- Security owner: confirm who may reset a Workflow, because a reset is an operator action that needs the workspace restored.
- No official sample repository was inspected for reset testing with the SDK test environment. Mark as open for the Plugin engineer.

### DSR-3.6 Prove Update behavior at the Continue-As-New boundary and under concurrency

Status: OPEN

- Type: Verification
- Priority: High
- Estimate: 3 points (confidence 65 percent)
- Labels: Type: Verification, Topic: Approvals
- Parent: DSR-P3
- Blocked by: DSR-3.1, DSR-3.2
- Blocks: DSR-3.7
- Related: none
- Retires: A-20
- Informs: A-13, A-42
- Owner role: Plugin engineer

#### Context

Update ids are scoped to one run, so the same id can be accepted again after Continue-As-New. The server documents that an Update can reach both the old and the new run when its completion and a Continue-As-New land in one Workflow Task. The design carries recent answered decision ids and uses the decision id as the client side Update id ([canonical specification](../canonical-documents.md#specification), INV-4, *Update volume*). Handlers must drain before Continue-As-New.

#### Problem

The behavior at the boundary is relayed and untested. An approval or answer can be lost or accepted twice with no signal to the approver. Assumption A-20 is open and the severity is High.

#### Scope

- A test of an Update sent at the Continue-As-New boundary, with the result documented as delivered to the new run or rejected visibly.
- A test of two concurrent answers for one decision in one Workflow Task, accepting exactly one.
- A test that the carried answered ids stop a double acceptance after a handover.
- A test of the gateway retry after `RESOURCE_EXHAUSTED` with the question id as the Update id.
- The documented client behavior that results, for the gateway owner.

#### Out of scope

- The subscriber load test with live output on (Phase 5, DSR-5.3).
- Token rejection cases (DSR-3.2).
- Any change to the server behavior.

#### Acceptance criteria

- [ ] An Update sent at the boundary is either applied by the new run or rejected with a visible error, and the test documents which. Proof: a dev server test that sends the Update while the Workflow hands over and records the client result and the history of both runs ([canonical plan](../canonical-documents.md#plan), M3 Checks).
- [ ] Two concurrent answers for one decision in one Workflow Task accept exactly one, and the other receives a stated rejection. Proof: a test that sends both through the validator in one activation and reads both client results.
- [ ] The carried answered ids survive a handover and reject a repeat in the new run. Proof: a test that answers, hands over, and sends the same id again (A-20).
- [ ] The same Update id after Continue-As-New is rejected through the carried ids and not accepted twice. Proof: a test with the same client Update id before and after a forced handover.
- [ ] A gateway retry after `RESOURCE_EXHAUSTED` with the same Update id is safe. Proof: a test that exhausts the in flight limit, retries, and counts accepted answers.
- [ ] The result lists the client rules that follow (retry on error, same Update id, check the Query after a handover). Proof: a short note in the ticket closing record that names each rule and its test.

#### Dependencies and blockers

- Blocked by DSR-3.1 (the handover and carried ids) and DSR-3.2 (the validators).
- Blocks DSR-3.7.

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), INV-4, *Update volume* and *Continue-As-New*; INV-7, *Approver identity*.
- Assumption row A-20.
- Update handling and limits: https://docs.temporal.io/develop/python/workflows/message-passing#send-update-from-client and https://docs.temporal.io/evaluate/cloud/limits#programming-model-level
- Continue-As-New and handler drain: https://docs.temporal.io/develop/python/workflows/continue-as-new
- Fork `_workflow.py`: https://github.com/osamastro7-droid/ai-integrations/blob/69f5497d3d3dec7ad3269c72ff266c2931c9f379/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_workflow.py

#### Open questions

- Plugin engineer: the claim that an Update can reach both the old and the new run is relayed from a review brief and is not read from the server documentation in this pack. The test may show a different result. Record the observed result.
- Gateway owner: confirm the client retry policy that the test results require.
- Plugin engineer: the dev server may not reproduce the same race as a production server. State the limit of the test.

### DSR-3.7 Review Phase 3 evidence and decide continue or redesign

Status: OPEN

- Type: Documentation
- Priority: High
- Estimate: 2 points (confidence 85 percent)
- Labels: Type: Documentation, Topic: Assumptions
- Parent: DSR-P3
- Blocked by: DSR-3.1, DSR-3.2, DSR-3.3, DSR-3.4, DSR-3.5, DSR-3.6, DSR-3.8
- Blocks: DSR-4.1, DSR-4.2, DSR-4.3, DSR-4.4
- Related: none
- Retires: none
- Informs: A-06, A-07, A-12, A-13, A-14, A-15, A-20, A-23, A-24, A-32, A-33, A-42
- Owner role: Plugin engineer

#### Context

Each phase ends with an exit review. The review updates the specification assumption rows and the plan milestone text with the evidence, and records a continue or redesign decision. A contradicted assumption stops the next phase until the design change is recorded (`tickets/README.md`, *Phase gates*). The Phase 3 exit gate lists A-06, A-07, A-12, A-13, A-14, A-15, A-20, A-23, A-24, A-32, A-33 and A-42 (`tickets/README.md`, *Hierarchy*).

#### Problem

The evidence from the Phase 3 tickets is spread across tests and notes. Many of the listed rows are proposed fixes or untested. Phase 4 builds isolation and workspace lifecycle on the claims, tokens and parked runs from this phase, so a wrong Phase 3 result would spread.

#### Scope

- Read the closing evidence of DSR-3.1 to DSR-3.6 and DSR-3.8.
- Update each listed assumption row in the specification with its status and the proving artifact, or with the contradicting evidence and the design change.
- Update the plan milestone M3 text and the retirement table with the evidence.
- Record one decision: continue to Phase 4 or redesign, with the reasons and the owner role.
- Confirm the approved DSR-0.2 disposition: both key and ordinal claim files are retained; redo, keyed effects, claims high water and the additional contract version are excluded. Confirm DSR-3.8's SUPERSEDED record rather than reopening its scope.
- Record the one real model run of the answers shape (A-25) as done or moved, if it is part of Phase 3 evidence.

#### Out of scope

- New build work. A failed criterion returns to its ticket.
- Assumption rows that belong to later phases.

#### Acceptance criteria

- [ ] Every retained Phase 3 assumption is verified at source with evidence or contradicted with a recorded design change. A-23 remains superseded by DSR-0.2, and A-56 has its M3 replay evidence. Proof: a specification diff per gate id.
- [ ] The M3 text in the plan and its retirement table match the evidence. Proof: a diff of the plan with the artifact names that prove each check.
- [ ] A continue or redesign decision is recorded with date, reasons and owner role. Proof: a decision record in the Phase 3 closing note.
- [ ] The closing note confirms Option R, the retained ordinal claim guard and the four superseded tickets. It does not claim deferred work was implemented. Proof: the note and scope decision links.
- [ ] No Phase 4 ticket starts while a contradicted Phase 3 assumption lacks a recorded design change. Proof: the decision record names each open contradiction or states that none exists.
- [ ] The review checks that the full test suite passes without credentials and that recorded histories replay. Proof: a recorded test run and a Replayer result.

#### Dependencies and blockers

- Blocked by every other Phase 3 ticket, including DSR-3.8.
- Blocks DSR-4.1, DSR-4.2, DSR-4.3 and DSR-4.4.

#### Source evidence

- `tickets/README.md`, *Phase gates* and *Hierarchy*.
- [canonical plan](../canonical-documents.md#plan), *Assumptions retired by milestone*.
- [canonical specification](../canonical-documents.md#specification), *Assumptions and risks if wrong*.

#### Open questions

- Plugin engineer: the open review items that touch Phase 3 and are not scoped into a ticket (R6-02 snapshot counter rebaseline, R6-08 assumption value mismatches, R6-10 state size) need an owner. Decide at this review which are in version 1.
- Plugin engineer: confirm whether the real model check of the answers shape (A-25) is run in Phase 3 or recorded as moved. No ticket in the README table owns it.

### DSR-3.8 Run redo to repeat or redispatch an unknown outcome on purpose

Status: SUPERSEDED

Scope disposition (2026-10-01): DSR-0.2 defers redo, claim release and keyed redispatch. A-23 remains superseded. The historical body below is not active implementation scope, and its links remain for phase exit coverage. DSR-0.8 still owns the unresolved ambiguous Bash operator procedure.

- Type: Build
- Priority: High
- Estimate: 4 points (confidence 60 percent)
- Labels: Type: Build, Topic: Effects, Topic: Approvals
- Parent: DSR-P3
- Blocked by: DSR-0.8, DSR-3.3
- Blocks: DSR-3.7
- Related: DSR-3.5
- Retires: A-23
- Informs: A-08, A-45
- Owner role: Plugin engineer

#### Context

A parked run can hold an effect whose outcome is unknown. The `redo` action lets an operator repeat that effect on purpose. For a claimed effect, `redo` runs a `release_claim` Activity on the segment queue, because the Worker owns the claims tree and the effect queue may be the queue that is down. The Workflow then dispatches the same call as a new effect at the next ordinal with a new key. For a keyed effect there is no claim to release, so `redo` redispatches the call under its stored key and ordinal ([canonical specification](../canonical-documents.md#specification), INV-1, *Parked runs*). The reset policy and the `redo` decision come from DSR-0.8. The parked phase comes from DSR-3.3.

#### Problem

The `redo` mechanism, `release_claim`, and the split of `pending_unknown` and `unknown_audit` are proposed fixes with no verification. A wrong `redo` repeats an external effect. A keyed `redo` after a park that outlasts the key retention window of the service executes twice under a label that says it is safe (review item R6-06).

#### Scope

- The `pending_unknown` list (each parked unknown outcome not yet delivered, with its paused call, key and ordinal) and the bounded `unknown_audit` list (64 entries, oldest dropped) that receives an entry once the model has received its outcome.
- The `release_claim` Activity on the segment queue, which removes `ord-<ordinal>` and `<key>` and is idempotent.
- `redo` for a claimed effect: release the claims, dispatch the same call at the next ordinal with a new key, return that outcome to the model in place of the unknown outcome, and set the phase to running.
- `redo` for a keyed effect: redispatch under the stored key and ordinal.
- Validator rejection of an ordinal not in `pending_unknown` and of one whose outcome the model already received.
- Keyed `redo` retention rule (proposed and unverified, from review item R6-06): the park time is recorded with the `pending_unknown` entry, and the validator rejects a keyed `redo` that is older than the declared retention window of that tool, leaving the model to decide with a new ordinal and key. The window comes from the record made by DSR-0.10.
- The audit record is the `resume` Update and the new effect, which history already holds.

#### Out of scope

- The parked phase, `retry`, `resume_from_checkpoint` and `abort` (DSR-3.3).
- Token verification (DSR-3.2).
- Reset detection proof (DSR-3.5).
- Content rules for audit entries to reduce handover bytes (review item R6-10). The ticket stores ordinal, key, tool name and an input digest in the audit list as a proposal.

#### Acceptance criteria

- [ ] `redo` runs `release_claim` on the segment queue for a claimed effect, dispatches the call at a new ordinal with a new key, and returns the new outcome in place of the unknown outcome (only if kept in version 1, redo). Proof: a test that counts claim files, spawns and the tool result that the model receives.
- [ ] `redo` for a claimed effect works when the effect queue is down (only if kept in version 1, redo). Proof: a test that stops every effect Worker, runs `release_claim` on the segment queue, and shows that the claim files are gone and the dispatch waits on the effect queue without failing the run.
- [ ] `release_claim` is idempotent (only if kept in version 1, redo). Proof: a test that calls it twice and compares the claims directory.
- [ ] `redo` for a keyed effect redispatches under the stored key and ordinal and produces one external effect (only if kept in version 1, redo and keyed effects). Proof: a test service that counts effects per key.
- [ ] A keyed `redo` older than the declared retention window of its tool is rejected by the validator, and a younger one is accepted (only if kept in version 1, redo and keyed effects; proposed rule, unverified). Proof: two validator tests with the park time on each side of the window.
- [ ] `redo` rejects an ordinal not in `pending_unknown` and one whose outcome the model already received (only if kept in version 1, redo). Proof: two validator tests.
- [ ] An entry moves from `pending_unknown` to `unknown_audit` when the model receives its outcome, and the audit list drops its oldest entry at 64 (only if kept in version 1, redo). Proof: a Workflow test with 65 delivered outcomes and a size assertion on the carried state.
- [ ] A `redo` accepted just before a handover is applied by the new run exactly once (only if kept in version 1, redo). Proof: a test that forces a handover between acceptance and application.
- [ ] The `redo` action needs a valid signed `resume` token bound to the park id and the ordinal. Proof: a rejection test for a token with another ordinal.

#### Dependencies and blockers

- Blocked by DSR-0.8 (reset policy and `redo` decision) and DSR-3.3 (parked phase and the `resume` Update).
- Conditional on DSR-0.2: `redo`. If version 1 drops it, this ticket becomes SUPERSEDED and A-23 is reassigned. Keyed redispatch is also conditional on keyed effects, and the retention rule is also conditional on DSR-0.10.
- Blocks DSR-3.7. Related to DSR-3.5, which checks the operator behavior after a reset.

#### Source evidence

- [canonical specification](../canonical-documents.md#specification), INV-1, *Parked runs*; INV-5, *The lineage id*; Interfaces, *Activities*.
- Assumption rows A-23 (a proposed fix) and A-45. Review item R6-06 in the sixth design critique.
- Idempotency key guidance: https://docs.temporal.io/activity-definition#idempotency
- Fork `_workflow.py` for the dispatch path: https://github.com/osamastro7-droid/ai-integrations/blob/69f5497d3d3dec7ad3269c72ff266c2931c9f379/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_workflow.py

#### Open questions

- Security owner: confirm that `redo` needs no stronger authorization than the `resume` token.
- Plugin engineer: confirm that a rejected keyed `redo` leaves the unknown outcome for `retry` to deliver, and that the model then decides.
- Tool author: confirm the retention window of each keyed tool, because the retention rule depends on it.
- Plugin engineer: the severity of A-23 should be rated High if the keyed duplicate branch is real (review item R6-08). Confirm in DSR-3.7.
