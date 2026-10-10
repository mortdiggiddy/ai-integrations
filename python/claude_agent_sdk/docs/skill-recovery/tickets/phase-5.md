# Phase 5 tickets

### DSR-5.1 Document and test Worker Deployment rollout and drain

Status: OPEN

- Type: Build
- Priority: Medium
- Estimate: 5 points (confidence 55 percent)
- Labels: Type: Build, Topic: Versioning, Status: Blocked on decision
- Parent: DSR-P5
- Blocked by: DSR-0.9, DSR-4.5
- Blocks: DSR-5.6, DSR-5.8, DSR-5.9
- Related: DSR-5.5
- Retires: A-30, A-50, A-16 (M5 part), A-29 (M5 part)
- Informs: none
- Owner role: Plugin engineer

#### Context

The specification sets Pinned as the default Worker Versioning behavior. A run also hands over by Continue-As-New when the target Deployment Version changed, observed at the periodic wake of any wait, and the new run opts in to upgrade explicitly. One Deployment Version covers the `agent`, `segment` and `effect` queues, with at least two Workers per queue per retained version.

The build identifier includes the SDK wheel version, the engine version, the hook contract version and the plugin version, and engine self update is disabled in the image. The specification adds a proposed rollout rule: roll out Workers for all three queues before any Workflow moves, and drain a version only when the server reports no run pinned to it and the operator confirmed that every waiting run upgraded at its handover.

Upgrade on Continue-As-New is a Public Preview feature, and a community report describes a reversion to Pinned after the handover. DSR-0.9 names who registers the Search Attributes and who owns the rollout order.

#### Problem

If the rollout order slips or an old version drains early, a pinned run can send an effect to the current version of its queue, which runs different executor code without any error. If Worker Versioning is not deployed, the Pinned default and the drain rules do nothing. If upgrade on Continue-As-New does not work on the pinned SDK version, old Workers must stay up indefinitely.

#### Scope

- Rollout and drain guidance as a runbook inside the plugin documentation, with the rollout owner role from DSR-0.9.
- Tests on the pinned SDK version for the Pinned default, the upgrade at handover, the version check that catches removed effect Workers, and the build identifier.
- A visible consequence when Worker Versioning is not deployed.

#### Out of scope

- Registering Search Attributes. DSR-0.9 names the owner and DSR-3.4 built the start check.
- The daily newest engine job. DSR-5.6 owns it.
- Patch retirement. DSR-5.5 owns it.
- Running a Kubernetes Worker Controller for the customer.

#### Acceptance criteria

- [ ] A run started as Pinned on version 1 hands over by Continue-As-New with an explicit upgrade opt in, and the new run executes on version 2. The new run is not reverted to Pinned. Proof: a test on the pinned `temporalio` SDK version against a dev server with Worker Versioning. If the test fails, the fallback to patching is recorded as a design change.
- [ ] A Pinned run keeps its Workflow Tasks on its version while version 2 is current. Proof: a test that shows the Workflow Task Worker version.
- [ ] After the effect Workers of the pinned version are removed from a run that is still pinned, the executor version check refuses the effect with an `ExecutorFault` before any claim, the run parks, and no effect runs on different code. Proof: a test with the removal step.
- [ ] A rehearsal on a dev server rolls out version 2 on all three queues before any Workflow moves, and a run continues across the rollout without a refusal. Proof: the rehearsal record.
- [ ] The runbook states the drain rule. A version is drained on a queue only when the server reports no run pinned to it and the operator confirmed that every waiting run upgraded at its handover. A rehearsal drains version 1 after the last run left it, and the record names the evidence source for no run pinned. Proof: the rehearsal record and the runbook text.
- [ ] When Worker Versioning is not enabled, a start time warning or a README statement says that the Pinned default and the drain rules have no effect and that patching is then the only gate. Proof: a test of the warning or the reviewed README text.
- [ ] A change to any one of the SDK wheel version, the engine version, the hook contract version or the plugin version changes the build identifier. Proof: a unit test for each of the four inputs.
- [ ] The `temporalio` SDK version is pinned because External Storage is in public preview, and the pin is recorded in the build identifier and the README. This settles the M5 part of A-29. Proof: the dependency file and the README text.
- [ ] The runbook states that signed approval enforcement holds only for Workflows built on the plugin base class and registered with the interceptor. Proof: the reviewed runbook text.

#### Dependencies and blockers

- Blocked by DSR-0.9, which names the rollout order owner.
- Blocked by DSR-4.5, the Phase 4 exit review.
- Blocks DSR-5.6, DSR-5.8 and DSR-5.9.
- DSR-0.2 retains upgrade on Continue-As-New in approved Option R. The first criterion remains required, and the pinned SDK behavior still needs proof. A fallback to patching requires a recorded design change.

#### Source evidence

- Specification, INV-2, *Versioning* paragraph, including the *Handler ownership* and *Pinned rollout* passages.
- Assumptions A-16, A-30 and A-50, and open issue OI-7.
- Worker Versioning behaviors: https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning#choosing-behavior
- Worker Controller for Kubernetes: https://docs.temporal.io/production-deployment/worker-deployments/kubernetes-controller
- Task queue separation: https://docs.temporal.io/best-practices/worker#separate-task-queues-logically
- DSR-0.2, Option R, for retained package, policy and engine checks without the additional contract version.

#### Open questions

- Plugin engineer: does the pinned SDK version implement upgrade on Continue-As-New as the documentation describes? No source in the pack confirms it.
- Plugin engineer: a plugin or executor change may not change any of the three retained fields. State the resulting limitation and prove rollout safety without claiming an additional contract version check.
- Operator: who confirms in a real deployment that every waiting run upgraded before a drain?
- The pack did not inspect an official sample repository for Worker Versioning. A claim about a sample pattern would need one.
- The estimate is 5 points. Split documentation from the tests in review if the preview feature needs a fallback.

### DSR-5.2 Prove codec coverage of Update payloads

Status: OPEN

- Type: Verification
- Priority: Medium
- Estimate: 2 points (confidence 70 percent)
- Labels: Type: Verification, Topic: Approvals
- Parent: DSR-P5
- Blocked by: DSR-4.5
- Blocks: DSR-5.9
- Related: none
- Retires: A-31
- Informs: none
- Owner role: Security owner

#### Context

The default Data Converter does not encrypt, so payloads sit in clear text in history, the Web UI and the CLI unless a Payload Codec is installed. The documentation lists Signal inputs and other data as encryptable. It does not list Update arguments or results. The design assumes that Update arguments pass through the codec like Signals.

The approval, answer and `resume` Updates carry signed tokens, decisions and free text answers. The specification also requires an encoded failure converter, because subprocess stderr would otherwise sit in clear text in failure messages.

#### Problem

If Update payloads bypass the codec, approval decisions, tokens and answers are readable in history. No test in the pack inspects a stored Update payload.

#### Scope

- A test with a real encrypting Payload Codec on the Client and on the Worker.
- Inspection of stored history events for the three Update kinds, for failure messages and for Search Attributes.

#### Out of scope

- Choosing the codec product or the Codec Server design.
- Key management for the codec.
- The signed token scheme. DSR-3.2 built it.

#### Acceptance criteria

- [ ] With an encrypting Payload Codec on the Client and on the Worker, the stored history event for each of the answer, approval and `resume` Updates holds its arguments in encoded form, and a marker string placed in the arguments does not appear in plain text. Proof: a test that reads the history and asserts the absence of the marker.
- [ ] The stored Update result for each of the three Updates holds no plain text marker. Proof: the same test for the result payload.
- [ ] The same run completes. The validator verifies the token and records the answer while the arguments pass through the codec. Proof: the test run outcome.
- [ ] With the encoded failure converter on, a marker placed in subprocess stderr does not appear in plain text in a stored failure event. Proof: a test that reads the failure event.
- [ ] No Search Attribute value of the run holds tool input, tool output, a workspace file path, question text or answer text. Proof: a test that lists the attribute values of a run after a question and an effect.
- [ ] If an Update argument or result appears in plain text, the test fails, the row for A-31 records the contradiction, and the design change is recorded. A proposal is to encrypt the token and answer fields in the application. Proof: the recorded design change.

#### Dependencies and blockers

- Blocked by DSR-4.5, the Phase 4 exit review.
- Blocks DSR-5.9.

#### Source evidence

- Specification, INV-7, *Encryption*, *Failures* and *Search Attributes* paragraphs.
- Assumption A-31 and open issue OI-5.
- Data encryption: https://docs.temporal.io/evaluate/features/data-encryption
- Failure converter: https://docs.temporal.io/failure-converter
- Search Attributes: https://docs.temporal.io/search-attribute

#### Open questions

- Security owner: which codec does the deployment use for the test? A test codec proves coverage of the path and does not prove the production codec.
- The pack did not inspect an official sample for a codec test. A claim about sample shape would need one.

### DSR-5.3 Prove approvals under subscriber load with live output on

Status: OPEN

- Type: Verification
- Priority: Medium
- Estimate: 3 points (confidence 60 percent)
- Labels: Type: Verification, Topic: Approvals
- Parent: DSR-P5
- Blocked by: DSR-4.5
- Blocks: DSR-5.9
- Related: none
- Retires: A-34
- Informs: none
- Owner role: Gateway owner

#### Context

Live output is off by default. When it is on, the fork publishes assistant text through Workflow Streams as batched Signals, and subscriber long polls are Updates. A Workflow allows 10 Updates in flight and 2,000 in total per execution. The fork's own test shows that 12 parked subscribers exhaust the in flight limit and make an approval fail with `RESOURCE_EXHAUSTED`.

The specification keeps coarse lifecycle events in history, sends high rate output out of band or with a raised batch interval, and puts one shared subscriber service in front of viewers. The approval gateway retries an Update that fails with `RESOURCE_EXHAUSTED`. That retry is safe because the decision id is the Update id.

#### Problem

An approval that fails under subscriber load stalls a run until the decision expires. The count of Signal batches in a 10 minute segment is a derived estimate of about 300, and OI-20 asks for a measurement.

#### Scope

- An acceptance test with live output on, more than ten concurrent subscribers, a 10 minute segment and then an approval.
- A measured count of Signal batches and Update totals for the run.
- The retry behavior of a test gateway client.

#### Out of scope

- Building the production gateway. The Gateway owner builds it.
- The shared subscriber service.
- Live output off. DSR-3.4 covered discovery with live output off.

#### Acceptance criteria

- [ ] With live output on and more than ten concurrent subscribers during a 10 minute segment, an approval Update either succeeds at once or fails with `RESOURCE_EXHAUSTED`, and the gateway client retry then succeeds. Proof: a test log with the subscriber count, the number of retries and the accepted decision.
- [ ] The approval is accepted exactly once, because the decision id is the Update id. A duplicate send after success does not create a second acceptance. Proof: the same test with a duplicate send.
- [ ] The test records the number of Signal batches and the history event count for the 10 minute segment. It compares the batch count with the derived figure of about 300 and states whether the figure holds. Proof: the recorded measurement.
- [ ] At the end of the run the total Update count stays below 2,000, and the report states the margin. Proof: the recorded count.
- [ ] If the retry bound passes and the approval still fails, the test reports the failure, the row for A-34 records the contradiction, and a design change is recorded. Proof: the test result and the recorded change.

#### Dependencies and blockers

- Blocked by DSR-4.5, the Phase 4 exit review.
- Blocks DSR-5.9.
- DSR-0.2 retains approvals and the existing opt in live output behavior in approved Option R. Every criterion remains required for the test with live output enabled; live output remains off by default.

#### Source evidence

- Specification, INV-4, *Live output and the Update budget* and *Update volume* paragraphs.
- Assumption A-34 and open issue OI-20.
- Event and Update limits: https://docs.temporal.io/evaluate/cloud/limits#programming-model-level
- Update semantics: https://docs.temporal.io/develop/python/workflows/message-passing#send-update-from-client

#### Open questions

- Gateway owner: what retry bound does the gateway use? The specification names the retry and no bound.
- Plugin engineer: how does the test create subscribers? The fork test that parks 12 subscribers is the starting shape, and the pack did not read an official sample for Workflow Streams.

### DSR-5.4 Prove session store conformance

Status: OPEN

October 9 source reconciliation: [the maintained release-check comparison](../proposals/distributed-recovery/2026-10-08/priority-sweep/coverage.md#october-9-release-check-reconciliation) records native tool recording into a session copy. Compare source-session immutability and exact pending/result records under replacement and lost acknowledgement. Recording into the wrong session can turn a deferred call into an interrupted call. Reported conversation recovery does not supply workspace restoration or local store conformance. Status and acceptance criteria are unchanged.

- Type: Verification
- Priority: Medium
- Estimate: 3 points (confidence 65 percent)
- Labels: Type: Verification, Topic: Engine
- Parent: DSR-P5
- Blocked by: DSR-4.5, DSR-0.11
- Blocks: DSR-5.9
- Related: none
- Retires: A-38
- Informs: none
- Owner role: Security owner

#### Context

The transcript holds prompts, model output and every tool input and result. External Storage does not cover it. The shipped session store is meant for tests and one machine, and it writes plaintext. The specification requires a production store that every Worker can reach, that encrypts at rest and that deduplicates entries by `uuid`. The conformance suite requirement is this design's own choice, because the plugin does not state it.

The fork reads the session back after every segment to compute the checkpoint, so a store that loses writes stalls the run with retries.

**Complete Issue 31 disposition (2026-10-08)**

October 8 full issue sweep: [conversation conformance](../proposals/distributed-recovery/2026-10-08/priority-sweep/coverage.md) clarifies that External Storage does not automatically cover CLI transcript files. If an adopted lane represents exact conversation as accepted Activity payloads, it can use payload offload; it still needs the selected original pending adapter and conflict/conditional-append conformance. Canonical v1's shared store remains authoritative until adoption. Test exact opaque JSON/UUID identity, lost/partial append, mismatched head, replacement with no old local disk, encryption and retained live/reset references. Conversation conformance cannot close workspace or old-execution termination proof.

#### Problem

If the store is not shared, a Worker that resumes a session cannot read it. If it is not encrypted, the full transcript sits in clear text. If it does not deduplicate, a retried segment writes duplicate entries.

#### Scope

- A conformance test suite that a production session store must pass.
- A run of the suite against the production store that the Security owner names.

#### Out of scope

- Choosing or building the production store.
- Transcript retention policy.
- The Payload Codec. DSR-5.2 owns it.

#### Acceptance criteria

- [ ] An entry that Worker A writes is read by Worker B in the same test, where the two Workers are separate processes with no shared local state. Proof: a conformance test output.
- [ ] The bytes at rest in the backing storage contain no plain text marker taken from a transcript entry. Proof: a test that scans the stored objects for the marker.
- [ ] Writing the same entry `uuid` twice gives one entry on read. Proof: a conformance test output.
- [ ] A store that drops a write makes the segment fail and retry inside the Schedule-To-Close bound, and no wrong checkpoint commits. Proof: a test with a fault injecting store.
- [ ] The integration selected by DSR-0.12 restores its session and exact pending call on a replacement Worker without local disk from the first Worker. Lost, partial or mismatched stored state refuses continuation. Conversation conformance does not count as filesystem restoration or durable approval publication. Proof: store fault and replacement process tests, with DSR-4.3 linked for workspace recovery and the recorded workflow state checked independently.
- [ ] The limits text states that the shipped store writes plain text and names the conformance suite as the production bar. Proof: the reviewed text recorded in DSR-5.9.

#### Dependencies and blockers

- Blocked by DSR-4.5, the Phase 4 exit review.
- Blocks DSR-5.9.

#### Source evidence

- Specification, INV-7, *The session store* paragraph.
- Specification, INV-5, *State ownership* paragraph, for the lost write behavior.
- Assumption A-38.
- Session storage interface: https://code.claude.com/docs/en/agent-sdk/session-storage
- Session mirroring and separate filesystem boundary: https://code.claude.com/docs/en/agent-sdk/sessions
- Fork test fixtures at the pinned commit: https://github.com/osamastro7-droid/ai-integrations/blob/69f5497d3d3dec7ad3269c72ff266c2931c9f379/python/claude_agent_sdk/tests/conftest.py#L23-L134

#### Open questions

- Security owner: which production store does the suite run against? DSR-0.6 records the security owner and no store.
- Security owner: which encryption property does the test accept as proof, for example server side encryption of the backing storage? The specification says only encrypted at rest.

### DSR-5.5 Rehearse patch retirement

Status: OPEN

- Type: Verification
- Priority: Medium
- Estimate: 3 points (confidence 60 percent)
- Labels: Type: Verification, Topic: Versioning
- Parent: DSR-P5
- Blocked by: DSR-4.5
- Blocks: DSR-5.9
- Related: DSR-5.1
- Retires: A-46, A-56 (M5 part)
- Informs: none
- Owner role: Plugin engineer

#### Context

The plugin ships Workflow code as a library, so a change to the Workflow class changes what replays for every open run of every user. Every new Workflow behavior is guarded by `workflow.patched` from the first release. CI keeps recorded histories from every released plugin version.

The specification proposes a retirement procedure built from the documented three step lifecycle: deploy `patched` with both paths, then deploy `deprecate_patch` in the same position with the old path removed, then remove the `deprecate_patch` call. The design uses the strictest bar. A step proceeds only when no run that could still be replayed carries the marker, meaning no open run and no closed run that a Query or a Reset could replay within retention. That a Reset of a closed run replays the marker is an inference.

**Complete Issue 31 disposition (2026-10-08)**

October 8 full issue sweep: [golden-history disposition](../proposals/distributed-recovery/2026-10-08/priority-sweep/coverage.md) requires evaluating existing PR33 golden histories and drift controls before authoring replacements. Pin corpus source/dependency/storage-route identities and run compatible historical replay with deliberately incompatible command/schema/identity negatives. Add missing governed receipt/approval/reset cases without repeating completed model experiments. Replay is not a filesystem/physical-effect failover test. Preserve original raw FAIL dispositions and immutable publication manifests.

#### Problem

If a marker is removed too early, a Query or a Reset of a closed run fails with a nondeterminism error. A reported incident shows that failure when `deprecate_patch` was removed while an open run still held the original marker.

#### Scope

- A dry run of the three step procedure on a real guard of the plugin or on a test guard with the same shape.
- A Replayer run over recent open and closed histories before each deploy, including histories with the installed inbound interceptor and a changed token rule protected by a patch (A-56 M5 part).
- A negative control and a Reset test that settle the inference.

#### Out of scope

- Retiring a guard in a released version. The rehearsal produces the procedure only.
- Patching for users who run no Worker Versioning. The sixth critique left this open.
- Worker Deployment rollout. DSR-5.1 owns it.

#### Acceptance criteria

- [ ] The rehearsal record shows the three steps in order, with a Replayer pass over recent open and closed histories before each deploy. The history set includes at least one open run that recorded the original marker and one closed run inside retention. Proof: the rehearsal record with the Replayer output for each step.
- [ ] A negative control replays a history that recorded the original marker against code with the marker removed, which skips the deprecation step. The replay fails with a nondeterminism error. Proof: a test output that shows the failure.
- [ ] A Reset of a closed run that recorded the marker, or a Replayer run as its stand in, is run against the code of each stage. The result confirms or contradicts the inference in A-46. Proof: the captured output. A contradiction leads to a recorded design change in the specification.
- [ ] A runbook states the bar: a step proceeds only when no replayable run carries the marker, and it states how an operator finds the runs that qualify. Proof: the reviewed runbook text.
- [ ] A recorded history from an earlier plugin version replays without nondeterminism against the current code. Proof: the replay test output.

#### Dependencies and blockers

- Blocked by DSR-4.5, the Phase 4 exit review.
- Blocks DSR-5.9.
- Related to DSR-5.1, which covers rollout of the Workers that carry each step.

#### Source evidence

- Specification, INV-2, *Patch retirement* paragraph.
- Specification, INV-3, *Determinism inside the Workflow* paragraph.
- Assumption A-46.
- Patching and retirement: https://docs.temporal.io/develop/python/workflows/versioning#patching

#### Open questions

- Plugin engineer: do the plugin patch ids need a namespace so that they cannot collide with ids in a user Workflow? The sixth critique proposed it and the specification did not adopt it.
- The pack did not inspect an official sample for patch retirement. A claim about a sample pattern would need one.

### DSR-5.6 Run the daily newest engine job and the engine upgrade resume test

Status: OPEN

October 9 source reconciliation: [the maintained release-check comparison](../proposals/distributed-recovery/2026-10-08/priority-sweep/coverage.md#october-9-release-check-reconciliation) pins the tested public fork, four successful plugin cells and separate reported version coverage. Review Windows HTTP refusal, stack-dependent nested-input tests and resume-prompt protection before promotion; platform assumptions can hide failures. The tooling failure cause remains attributed, PR 33 has an older head, and approved dependencies/runtime are unchanged. Status and acceptance criteria are unchanged.

Approved budget separation checkpoint (2026-10-03): see [canonical pointer](../canonical-documents.md), *Approved experiment authorization separation*. Earlier budget gate wording in historical checkpoints is superseded for Phase 1 monitored experiments only. No live run is authorized and strict preventive budgeting remains required at DSR-5.8 final acceptance.

- Type: Build
- Priority: Medium
- Estimate: 4 points (confidence 55 percent)
- Labels: Type: Build, Topic: Engine
- Parent: DSR-P5
- Blocked by: DSR-4.5, DSR-5.1
- Blocks: DSR-5.9
- Related: none
- Retires: A-01 (M5 part), A-22 (M5 part)
- Informs: A-30
- Owner role: Plugin engineer

#### Context

The resume mechanism depends on engine behavior that the official documentation read for this pack does not describe. The plan sets a daily job against the newest engine and gates Deployment Version promotion on it. The plugin refuses an engine older than its minimum. The project sets a two week dependency cooldown, so a newer wheel needs an explicit override. The plugin tests clear every `CLAUDE` and `ANTHROPIC` environment variable, so the Phase 1 test helper that reads an engine path from one explicit variable is the base.

The deferral experiments from the spike are permanent tests after Phase 1. A session written by engine N must resume on engine N+1 at a Continue-As-New boundary.

**Complete Issue 31 disposition (2026-10-08)**

October 8 full issue sweep: [version/platform and permission routes](../proposals/distributed-recovery/2026-10-08/priority-sweep/coverage.md) includes explicit permission mode and the historical SDK .160 through .163 Windows-wheel gap. Require package/binary/source provenance, supported OS markers, minimum and selected upper runtime lanes, upgrade resume and four-route hook/callback/effect observations. Linux upper proof cannot qualify Windows or every resume path. Newest is not a silent registry upgrade and the minimum is not raised to avoid unavailable artifacts. Report a missing package as an environment limit; no installation is authorized.

#### Problem

A newer engine can stop honoring `defer` or the synthetic result. Without a daily check, the plugin finds out when a run parks or when an effect runs unrecorded.

#### Scope

- A scheduled job that runs the deferral tests and the backstop tests on the newest engine.
- A promotion step that reads the job result.
- The engine N to N+1 session resume test.

#### Out of scope

- The Phase 1 test helper and the deferral tests. They already exist.
- Choosing the scheduling system. Open question below.
- Engine behavior with a real model. DSR-5.8 covers one run.

#### Acceptance criteria

- [ ] The job runs every day against the newest published engine with an explicit override of the dependency cooldown. It runs the deferral tests for built in Write and Bash with a synthetic result, and the backstop tests, which must fail when the backstop is removed. Proof: two consecutive scheduled run records.
- [ ] A forced failure, produced with an engine that does not honor `defer`, makes the job report failure to the owner role and makes the contract check park a test run with the engine version in the message. Proof: a negative control run record.
- [ ] The promotion step reads the latest job result, and a failing result blocks the promotion of a Deployment Version. Proof: a rehearsal that shows a blocked promotion and an allowed promotion.
- [ ] A session written by the minimum engine resumes on a newer engine at a Continue-As-New boundary. The run continues, the transcript is intact, and tool results are retained. Proof: a test that records the `claude -v` output of both engines.
- [ ] The row for A-01 records the daily job result on the newest engine as the M5 evidence. The row for A-22 records the resume test. Proof: the edited rows in DSR-5.9.

#### Dependencies and blockers

- Blocked by DSR-4.5, the Phase 4 exit review.
- Blocked by DSR-5.1, because promotion gating uses the Deployment Version rules.
- Blocks DSR-5.9.

#### Source evidence

- Specification, INV-2, *Versioning* paragraph, for the build identifier and the engine N to N+1 test.
- Specification, Scenarios, S6, for the park on a contract violation.
- Plan, Constraints, *Engine and documentation risk* paragraph.
- Assumptions A-01 and A-22, and open issues OI-1 and OI-3.
- Minimum engine check in the fork at the pinned commit: https://github.com/osamastro7-droid/ai-integrations/blob/69f5497d3d3dec7ad3269c72ff266c2931c9f379/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_runner.py#L229-L247
- Hooks reference: https://code.claude.com/docs/en/agent-sdk/hooks

#### Open questions

- Operator: where does the job run? The repository conventions say no workflow file per plugin, so the job may live outside the repository.
- Plugin engineer: what is the promotion gate rule, for example the last result must pass within 24 hours? The plan names the gate and no rule. The rule above is a proposal.
- The daily job is a plan decision and not a fact from a source.

### DSR-5.7 Prove shutdown, metrics and paid retry rate

Status: OPEN

Approved budget separation checkpoint (2026-10-03): see [canonical pointer](../canonical-documents.md), *Approved experiment authorization separation*. Earlier budget gate wording in historical checkpoints is superseded for Phase 1 monitored experiments only. No live run is authorized and strict preventive budgeting remains required at DSR-5.8 final acceptance.

- Type: Verification
- Priority: Medium
- Estimate: 4 points (confidence 55 percent)
- Labels: Type: Verification, Topic: Effects
- Parent: DSR-P5
- Blocked by: DSR-4.5
- Blocks: DSR-5.8, DSR-5.9
- Related: none
- Retires: A-40 (M5 part), A-28 (M5 part), A-24 (M5 part)
- Informs: none
- Owner role: Plugin engineer

#### Context

The Python Worker reference states a default of zero for the graceful shutdown timeout, and the SDK installs no SIGTERM handler. The design sets the timeout above the p99 effect time, installs a SIGTERM handler that calls the Worker shutdown, and sets the Kubernetes grace period above the timeout.

The design emits counters (contract violations, unknown outcomes and the human wait age) from Workflow code through the Python SDK metric facility. The specification marks replay safe emission as an assumption to verify before service level work starts. The service level for paid retries is fewer than 1 in 100 segments with an attempt above one, because each retry can cost a model call.

#### Problem

A deploy without graceful shutdown cancels in flight effects and creates unknown outcomes. Wrong counters give blind alerts. A paid retry rate above target costs money without notice.

#### Scope

- A SIGTERM test of a Worker with an in flight effect.
- A metric emission test, including replay.
- A measurement of the paid retry rate against the service level, with fault injection.

#### Out of scope

- Dashboards and alert configuration.
- Cloud metrics.
- The shutdown test for the segment engine process group in Phase 2. DSR-2.7 built the containment.

#### Acceptance criteria

- [ ] A SIGTERM to a Worker with an in flight effect starts graceful shutdown. The effect completes inside the graceful shutdown timeout and the Worker exits inside the Kubernetes grace period. Proof: a test that records the signal time, the effect end time and the exit time.
- [ ] An effect longer than the graceful shutdown timeout is cancelled and its process tree is killed on a reachable host. An uncertain claimed Bash outcome parks without model result and does not run again. Proof: claimed case test output showing the cause and no further segment, with partitioned host survival named as a residual.
- [ ] The Python SDK metric facility emits the contract violation counter, the unknown outcome counter and the human wait age from Workflow code. A replay of a recorded history does not increment a counter again. Proof: a captured metric scrape from a live run and from a replay.
- [ ] The measured rate of segments with an attempt above one is below 1 in 100 over a stated sample, or the report records the rate and the recorded tuning. Proof: the measurement table with the sample size and the attempt counts.
- [ ] Fault injection shows that a credential or quota error parks the run with no paid retry, and that a rate limit error retries inside the 1 hour Schedule-To-Close bound. Proof: a test output for each error class.

#### Dependencies and blockers

- Blocked by DSR-4.5, the Phase 4 exit review.
- Blocks DSR-5.8, because the acceptance run uses the shutdown settings and the counters.
- Blocks DSR-5.9.

#### Source evidence

- Specification, INV-1, *Cancellation and shutdown* paragraph and *Segment Activity* paragraph.
- Specification, INV-6, *Metrics the design commits to* paragraph and the service level table.
- Assumptions A-24, A-28 and A-40.
- Worker shutdown: https://docs.temporal.io/encyclopedia/workers/worker-shutdown#worker-shutdown-behavior
- SDK metrics: https://docs.temporal.io/references/sdk-metrics
- Retry policies: https://docs.temporal.io/encyclopedia/retry-policies#default-behavior

#### Open questions

- Plugin engineer: what workload produces the retry rate sample? A synthetic fault workload gives a rate that reflects the injected faults. A production sample needs live runs and a budget.
- The shutdown default of zero and the missing SIGTERM handler are relayed claims, and the test is the first direct check.

### DSR-5.8 Prove strict budgeting and real model application acceptance

Status: OPEN

Approved budget separation checkpoint (2026-10-03): see [canonical pointer](../canonical-documents.md), *Approved experiment authorization separation*. Earlier budget gate wording in historical checkpoints is superseded for Phase 1 monitored experiments only. No live run is authorized and strict preventive budgeting remains required at DSR-5.8 final acceptance.

- Type: Verification
- Priority: Medium
- Estimate: 3 points (confidence 50 percent)
- Labels: Type: Verification, Topic: Engine
- Parent: DSR-P5
- Blocked by: DSR-0.4, DSR-4.5, DSR-5.1, DSR-5.7
- Blocks: DSR-5.9
- Related: none
- Retires: A-02 (M5 part)
- Informs: A-01, A-24
- Owner role: Budget owner

#### Context

Every empirical result in the pack came from a fake model. The spike and the fork tests script the model's calls. They prove engine mechanics and do not show how a real model behaves at a deferral boundary. OI-16 is a hard gate before any customer facing claim. The plan sets one manual acceptance run against a real model under a budget cap with a named owner.

DSR-0.4 must complete final budget ownership, authentication, billing and Phase 5 allocation decisions. DSR-1.1 supplies monitored experiment controls; its Phase 1 evidence does not prove strict preventive budgeting. DSR-1.3 and DSR-1.4 produced the short checks in Phase 1.

#### Problem

If a real model loses a deferred call or reacts badly to a denial after a pause, the first sign is a customer facing run. A-02 covers two deferred calls in one message, the paused call marker, the denial after a pause, and reads before and after a deferral.

#### Scope

- Establish the strict preventive request/token/currency and cumulative accounting boundary, then one separately authorized manual demo skill acceptance run on the hardened plugin under its Phase 5 allocation.
- Observations for each behavior in A-02, and a check that history holds every effect.

#### Out of scope

- A statistical evaluation of the model.
- The answer shape check. DSR-1.6 owns A-25.
- Running more than one acceptance scenario.

#### Acceptance criteria

- [ ] Before every provider request, including internal continuations, retries and resumes, the supported enforcement route admits the maximum request envelope against exact model, cumulative input/output and currency limits. Proof: provider request receipts and deliberately insufficient envelope refusal controls; reactive SDK/host stopping cannot pass this criterion.
- [ ] Complete verified usage/cost deltas reconcile all segments/retries/overlapping processes without resetting logical test or phase totals. Missing accounting or owner loss retains unresolved reservations and prevents unaccounted continuation; stale receipts refuse. Proof: accounting/fault/replacement records on the supported topology.
- [ ] Independent Phase 5 allocation, supported credential route and billing disposition are approved before the acceptance run. Deliberately low allowance produces a nonpassing preventive refusal and verified cleanup. Proof: DSR-0.4 decision and full request/accounting/host records.

- [ ] The run completes under the cap that the budget owner set, and the recorded spend is at or below it. If the cap is reached, the run stops safely and the record says so. Proof: the run record with the cap, the spend and the end state.
- [ ] A step of the run offers two effect calls in one message, and neither is lost. Proof: the history events for both calls or the recorded denial with the model's next action.
- [ ] The recorded observations cover the paused call marker, the denial after a pause with the model's next action, a read before a deferred call that survives, and a read after one that is denied. Each is marked as matching the fake model result or as different. Proof: the run record with one line per behavior.
- [ ] Every effect in the run appears in history with its key and mode as `effect_started` and `effect_ended` events that carry no raw tool input, and no effect ran inside the engine. Proof: the history export and a check that the files of an unrecorded effect do not exist.
- [ ] One effect in the run is gated by an approval with a signed token from a test gateway, and the run continues after the approval. Proof: the history events for the Update and the effect.
- [ ] A behavior that differs from the fake model result leads to a recorded design change, and A-02 records the change. Proof: the recorded change.
- [ ] The stored run record holds no credential. Proof: a scan of the record for the credential values.
- [ ] This same bounded acceptance scenario uses an application authored Temporal Workflow with the documented plugin registration, policy and security configuration, running the validated skill package without a replacement agent loop. Proof: the example source, configuration and complete run history. Missing required registration or security configuration refuses execution before an effect; a negative configuration test proves the refusal. This proves the documented contract, not compatibility with every Workflow or the Phase 7 harness adapter.

#### Dependencies and blockers

- Blocked by DSR-0.4 for complete final budget/authentication/allocation decisions; no Phase 1 monitored exception satisfies this dependency.
- Blocked by DSR-4.5, the Phase 4 exit review.
- Blocked by DSR-5.1, which provides the deployment rules the run uses.
- Blocked by DSR-5.7, which provides the shutdown settings and counters the run uses.
- Blocks DSR-5.9.
- DSR-0.2 retains signed approvals and claimed Bash in approved Option R. The approval criterion and each Bash step remain required, under the budget and credential decisions in DSR-0.4.

#### Source evidence

- [Canonical budget separation decision](../canonical-documents.md), *Approved experiment authorization separation*, owns the approved acceptance allocation and preserved strict enforcement contract.

- Specification, Open issues, OI-16 and OI-3.
- Specification, INV-3, *Mixed calls* paragraph, for the paused call marker and the denial.
- Plan, Milestones, M5, for the acceptance run.
- Assumptions A-01, A-02 and A-24.
- Hooks reference: https://code.claude.com/docs/en/agent-sdk/hooks
- Approved reusable Workflow goal and separate harness adapter boundary, not runtime proof: https://github.com/mortdiggiddy/ai-integrations/blob/2acc081998407f9c88fdba349103f5392dab2d73/README.md

#### Open questions

- Budget owner: what cap applies, and which credentials does the run use? DSR-0.4 records both.
- Operator: is one run enough to accept A-02? The plan asks for one run, and A-02 is reversible, so a later run can reopen it.
- Plugin engineer: which skill is the demo? The pack names none.

### DSR-5.9 Review Phase 5 evidence and decide continue or redesign

Status: OPEN

Approved budget separation checkpoint (2026-10-03): see [canonical pointer](../canonical-documents.md), *Approved experiment authorization separation*. Earlier budget gate wording in historical checkpoints is superseded for Phase 1 monitored experiments only. No live run is authorized and strict preventive budgeting remains required at DSR-5.8 final acceptance.

- Type: Documentation
- Priority: Medium
- Estimate: 2 points (confidence 80 percent)
- Labels: Type: Documentation, Topic: Assumptions
- Parent: DSR-P5
- Blocked by: DSR-5.1, DSR-5.2, DSR-5.3, DSR-5.4, DSR-5.5, DSR-5.6, DSR-5.7, DSR-5.8
- Blocks: DSR-6.1, DSR-6.2
- Related: none
- Retires: none
- Informs: A-02, A-16, A-22, A-24, A-28, A-29, A-30, A-31, A-34, A-38, A-40, A-46, A-50
- Owner role: Plugin engineer

#### Context

The Phase 5 exit gate needs A-16, A-22, A-29, A-30, A-31, A-34, A-38, A-40, A-46 and A-50 settled, plus the real model acceptance run for A-02. The review also records the M5 part of A-01, A-24 and A-28. The review updates the specification rows and the plan text with the evidence and records a continue or redesign decision for Phase 6.

#### Problem

Phase 6 records the evidence for every row. If Phase 5 leaves rows with old status text, Phase 6 must rediscover which test settled which row.

#### Scope

- Update each Phase 5 row in the specification table with its new status and proving artifact.
- Update the plan's M5 text and its retirement table.
- Record the decision for Phase 6.

#### Out of scope

- New tests. The eight earlier tickets own the evidence.
- The full table reconciliation. DSR-6.1 owns it.

#### Acceptance criteria

- [ ] Each of A-16, A-22, A-30, A-31, A-34, A-38, A-40, A-46 and A-50 carries a status of verified at source with the proving artifact named, or contradicted with the design change recorded. Proof: the edited specification rows.
- [ ] The row for A-02 records the acceptance run result, and the rows for A-01, A-24 and A-28 record their M5 evidence. Proof: the edited rows.
- [ ] The row for A-29 records the SDK version that the plugin pins and the test result at that version, and says which earlier ticket supplied the M2 and M3 parts. Proof: the edited row and the dependency pin in the plugin project file.
- [ ] The plan's M5 text and its retirement table match the specification by assumption id and check text. Proof: a side by side listing of the ids.
- [ ] After the edits, the evidence gate passes for the specification and for the plan. Proof: the captured output of the evidence script for each document, ending with `RESULT: PASS`.
- [ ] A decision record states continue or redesign for Phase 6, with the owner role and the date. A contradicted assumption names the design change that must exist before DSR-6.1 starts. Proof: the decision record.

#### Dependencies and blockers

- Blocked by every other Phase 5 ticket: DSR-5.1 to DSR-5.8.
- Blocks DSR-6.1.

#### Source evidence

- Specification, section *Assumptions and risks if wrong*.
- Plan, sections *Assumptions retired by milestone* and *Milestones*, M5.
- Ticket set index, section *Phase gates*.

#### Open questions

- Plugin engineer: no Phase 5 ticket lists A-29 under Retires, although the plan assigns its M5 part to pinning the SDK version. This review records the pin as a stopgap. The lead should confirm the owner of that part.
