# Phase 4 tickets

### DSR-4.1 Isolate effects at the decided level

Status: OPEN

Interface requirements (2026-10-12): Apply the [canonical policy/execution interfaces](../spec.md#selected-component-boundaries-2026-10-12): deny worker access to controller, authority, keys, unauthorized store readers and unapproved egress. Local containers/VMs and selected EC2 remain separately qualified profiles. Future microVM/confidential admission requires explicit threat boundary, measurement/freshness/key release/revocation and external-model disclosure policy; ordinary isolation or attestation alone does not prove confidentiality, rollback safety or old-execution death.

Selected isolation qualification (2026-10-11): dedicated Linux EC2 guest with unprivileged container/cgroup execution and external controller is the selected target. Qualify package/claim/authority, credentials/metadata-service/runtime-socket denial, permitted egress and detached descendants. Q-1/Q-7 also deny processor live writes/network/startup telemetry/healing and require no forbidden outbound requests. Trusted-host protection does not establish confidential execution; exact policies/pins and named Security/deployment holders remain OPEN.

- Type: Build
- Priority: Medium
- Estimate: 5 points (confidence 50 percent)
- Labels: Type: Build, Topic: Effects, Topic: Workspace, Status: Blocked on decision
- Parent: DSR-P4
- Blocked by: DSR-0.6, DSR-3.7
- Blocks: DSR-4.4, DSR-4.5
- Related: DSR-4.3
- Retires: A-17
- Informs: A-41
- Owner role: Plugin engineer

#### Context

The specification requires isolation for any use beyond a private demo. Effects run as a separate unprivileged operating system user, or inside a container or a PID namespace with a restricted `/proc`. Only `work/` in the run directory is writable by the effect identity. The run directory and `.claude/` belong to the Worker user.

DSR-0.6 decides the isolation level and names the security owner. Until that decision exists, the specification says every confinement claim about `.claude/`, about claim file integrity and about the Worker launch environment is void. The at most one spawn guarantee for claimed effects is void as well.

Phase 2 built the executor and the run directory layout. This ticket makes the executor honor the decided level.

#### Problem

A command that runs as the Worker user can read the Worker launch environment through `/proc/PID/environ`. It can write the read only package copy and plant project settings that pre approve tools. It can leave a daemonized child that a process group kill misses. A recorded local test in the pack showed the environment read with an empty child environment.

The design cannot claim confinement until a test shows the decided level closes each path.

#### Scope

- Run every effect at the isolation level that DSR-0.6 records.
- Prove on Linux that the effect identity writes only `work/`, cannot replace `.claude/` or the run directory, cannot read the Worker launch environment, and leaves no running child.
- Prove that the protection for a project settings allow rule comes from the Worker owned `.claude/` tree and not from the preventive backstop.
- Replace the specification's interim statement about the private demo with the decided level and its recorded residuals.

#### Out of scope

- The choice of level and the security owner. DSR-0.6 owns it.
- A microVM product (non goal N4).
- Network file system behavior. DSR-4.3 owns it.
- Measurements under load. DSR-4.4 owns them.
- Path checks for Write and Edit. DSR-2.4 owns them.

#### Acceptance criteria

- [ ] A Bash effect under the effect identity cannot write any file under `.claude/`. The attempt returns a permission error and the package hash of the run is unchanged afterward. Proof: an integration test output and the passing per segment hash check that follows it.
- [ ] A Bash effect cannot rename or replace `.claude/` or the run directory, and cannot create a file at the run directory root. Only `work/` accepts writes. Proof: an integration test that asserts an error for each attempt.
- [ ] A Bash effect cannot read the Worker launch environment. A marker value set in the Worker environment does not appear in the effect output when the effect reads `/proc/<Worker pid>/environ`. Proof: an integration test with the marker.
- [ ] After the executor reports an outcome, no descendant of the effect runs, including a child that called `setsid`. Proof: a test that lists the processes of the effect identity or namespace after the report and finds none. Any process class that the decided level cannot reach appears as a residual in the limits text.
- [ ] A Bash effect that writes a project settings allow rule under `.claude/` fails to write it. Proof: a test that shows the denied write, which shows that protection rests on the Worker owned tree.
- [ ] No effect process starts as the Worker user when the decided level is configured. A test that removes the effect identity or the level prerequisite shows that no effect process starts as the Worker user. Proof: the test output. The outcome mapping for this refusal is an open question below.
- [ ] The effect identity cannot create, change or delete a claim file or the claims directory, because both live outside `work/`. Proof: an integration test for a claimed Bash effect that attempts each action.
- [ ] The specification text and the limits text state the decided level, its security owner role and its residuals, and no confinement claim remains void. Proof: the reviewed diff recorded in DSR-4.5.


- [ ] Q-1/Q-7 deny processor startup/executor/telemetry/healing surfaces and live workspace/network access; confined SDK/effect descendants cannot escape the exact guest. Protected provider/Temporal/key credentials and sockets are inaccessible to effects. Proof: synthetic marker/egress/descendant negatives and selected-instance terminal witness; no credential inspection.

#### Dependencies and blockers

- Blocked by DSR-0.6, which decides the level and the security owner.
- Blocked by DSR-3.7, the Phase 3 exit review.
- Blocks DSR-4.4, which measures process containment under load on top of this isolation.
- Blocks DSR-4.5.
- DSR-0.2 retains claimed Bash and both claim guards in approved Option R. The claim file criterion and the spawn guard checks remain required; DSR-0.6 still decides the isolation level.

#### Source evidence

- Specification, INV-7, *Effect isolation* paragraph and *Credentials and the effect environment* paragraph.
- Specification, INV-2, *Workspace* paragraph, for the run directory ownership layout.
- Specification, INV-1, *Fail closed contract* paragraph, for the project settings allow rule case.
- Assumptions A-17 and A-41, and open issue OI-6.
- Fork engine options at the pinned commit: https://github.com/osamastro7-droid/ai-integrations/blob/69f5497d3d3dec7ad3269c72ff266c2931c9f379/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_runner.py#L869-L947

#### Open questions

- Security owner: which isolation level does DSR-0.6 record, and is a non Linux host supported?
- Plugin engineer: what outcome does the executor report when the effect identity or the level prerequisite is missing at run time? The specification names `ExecutorFault` for state faults only. A proposal is an `ExecutorFault` park, which needs a recorded design change.
- The estimate is 5 points because the work changes with the level. Split this ticket in review if the level is a container or a PID namespace.

### DSR-4.2 Remove run directories safely and detect a restored snapshot

Status: OPEN

Interface requirements (2026-10-12): Use the [canonical checkpoint/key retention interface](../spec.md#selected-component-boundaries-2026-10-12) for version-specific authorized cleanup. Preserve accepted objects, projections, keys and independent authority; unknown retention refuses deletion. Disposable worker/index cleanup cannot delete the sole readable accepted copy or revoke unresolved authority. Test stale references/configuration and denied cross-resource deletion for each admitted backend.

Selected preservation/cleanup requirement (2026-10-11): Q-13 refuses routine destruction while required result/postimage/projection remains sole-readable locally or publication is unresolved. Retain referenced artifacts, accepted projection, exact S3 versions, keys, local claims and independent authority through every supported recovery window; indexes are disposable cache. Urgent containment or genuine host loss records park/data loss. Namespace expiry, not-found, lease or generation alone never authorizes deletion/recreation.

- Type: Build
- Priority: Medium
- Estimate: 5 points (confidence 55 percent)
- Labels: Type: Build, Topic: Workspace
- Parent: DSR-P4
- Blocked by: DSR-3.7, DSR-0.11
- Blocks: DSR-4.5
- Related: DSR-4.3
- Retires: A-21, A-37, A-51, A-54 (workspace part)
- Informs: A-27
- Owner role: Plugin engineer

#### Context

The external janitor requires established namespace/lineage identity, safe lifecycle and complete retained references before routine deletion. Closure/not-found and grace alone are insufficient. It refuses unresolved publication or deletion of sole-readable required result/postimage/projection. Live, idle and parked runs remain preserved; no lease or modification time establishes authority.

Retain local guards, accepted object versions, keys and independent authority across the complete approved recovery/reset/replay horizon. Namespace retention alone is insufficient. Validate namespace, Workflow/lineage identity, accepted pair and live references; unknown identity or references refuse deletion.

The manifest `generation` counts prepare and `reprepare` calls, and the Workflow stores it as `volume_generation`. Approved Option R drops the claims high water counter. Generation checks can detect a snapshot older than a recorded prepare, but do not prove detection of a mid run snapshot that removes later claims or file edits.

#### Problem

A janitor that deletes the files of a live run, or a restored volume that diverges without notice, causes silent data loss. Both are High severity in A-21. A reused Workflow Id or a wrong namespace can also make the janitor delete a live run (A-51). The sixth critique found that the counters have no rebaseline after `reprepare`, that a lost effect result leaves the Workflow value behind, and that the counter covers claimed effects only.

#### Scope

- The janitor, with identity/status/lifecycle checks, sole-readable publication refusal and reference/key/authority retention across the complete approved horizon.
- The manifest check on every segment and the `reprepare` step, to the extent that DSR-2.1 did not already build them. If DSR-2.1 built part of this, this ticket proves it and builds the remainder.
- Manifest generation checks, the operator visible refusal and park that follow a stale value, and a defined baseline after a legitimate `reprepare`.

#### Out of scope

- Physical accepted-pair restore and exact-incarnation termination qualification. DSR-4.3 owns it.
- Isolation of effects. DSR-4.1 owns it.
- The choice of the retention value. The deployment owner sets it (OI-10).
- Complete mid run snapshot detection for claim files or Write and Edit file state. Approved Option R retains manifest generation checks, not the claims high water mechanism.

#### Acceptance criteria

- [ ] Closed-run cleanup after the grace period additionally requires sole-readable publication, reference-retention and exact-incarnation lifecycle checks; Workflow closure alone is insufficient. Proof: dev-server status and unresolved-publication/old-execution negatives.
- [ ] The janitor never removes the directory of a live idle run or of a live parked run that waits for days. Proof: a test that leaves a run idle past the grace period with an old modification time and shows the directory intact.
- [ ] The janitor removes nothing when Temporal is unreachable or returns any answer other than closed or not found. Proof: a test with a failing status call.
- [ ] Cleanup retains claims, objects, keys and independent authority through the complete approved recovery/reset/replay horizon and refuses unknown or unresolved references. Namespace expiry alone does not authorize removal. Proof: finite-policy and live/reference/expiry negatives.
- [ ] A run whose Workflow Id was reused keeps its own directory. A described run whose lineage id differs from the manifest is not treated as the same run. Proof: a test for each case.
- [ ] A janitor pointed at a wrong namespace never deletes the directory of a live run. Proof: a test where the wrong namespace reports not found for a live run and the directory remains.
- [ ] A missing manifest refuses; reprepare resumes only after validating the exact accepted pair, intact independent authority and required old-incarnation cleanup. Missing accepted bytes fail rather than becoming new state. Proof: authorized restoration positive and missing/mismatched-state negatives.
- [ ] A volume restored from a snapshot taken before the last prepare reports a lower `volume_generation`. The run parks with the cause named and the model receives no message about it. Proof: a test with a restored volume.
- [ ] After a legitimate `reprepare`, the next claimed effect is not refused as stale. The specification states how `reprepare` and `resume` set the stored `volume_generation`, and a test shows the next effect running. Proof: the specification text and the test output.
- [ ] The limits text states that restore detection is best effort and names the file state that it does not cover. Proof: the reviewed text recorded in DSR-4.5.


- [ ] Q-13 refuses routine cleanup of sole-readable required result/postimage/projection and preserves live/reset/replay artifacts, keys and authority. Index deletion is safe only when authenticated full artifacts and exact accepted projection survive. Proof: sealing/upload failure, unknown status/retention, restored-cache and reference reachability negatives.

#### Dependencies and blockers

- Blocked by DSR-3.7, the Phase 3 exit review.
- Blocks DSR-4.5.
- Related to DSR-4.3, which qualifies accepted-pair restoration and independent execution termination.
- DSR-0.2 retains both claim guards and manifest generation but drops claims high water detection. Mid run snapshot restore remains an explicit limitation, not a verified guarantee.

#### Source evidence

- Specification, INV-2, *Workspace* paragraph, for the janitor, the manifest and the generation check.
- Specification, INV-7, *Retention* paragraph.
- Specification, INV-1, *Claimed effect guard* paragraph, for the claims directory and the `ExecutorFault` park.
- Assumptions A-21, A-37, A-51 and A-54, and open issue OI-21.
- Review of revision 6, finding R6-02, for the rebaseline gap, the lost result anchor and the claimed effect scope.
- Namespace retention: https://docs.temporal.io/evaluate/cloud/limits#default-retention-period
- Workflow Id reuse policy: https://docs.temporal.io/workflow-execution/workflowid-runid#workflow-id-reuse-policy

#### Open questions

- Plugin engineer: how does legitimate `reprepare` update `volume_generation` without authorizing claim loss or treating uncertain Bash as resolved? Record and test the generation baseline rule.
- Operator: what retention value does the deployment use? The specification assumes 7 days and says the deployment owner must confirm it.
- Plugin engineer: the claims high water feature is deferred. State clearly that manifest generation alone does not detect every mid run snapshot restore.
- The estimate is 5 points. Split the janitor from the generation checks in review if the rebaseline design grows.

### DSR-4.3 Prove accepted checkpoint restoration and independent execution termination

Status: OPEN

Interface requirements (2026-10-12): Run common [canonical lifecycle/checkpoint cases](../spec.md#selected-component-boundaries-2026-10-12) plus actual AWS storage/host-loss/partition/termination proof. Moto and local container/VM tests provide only their declared development evidence. Managed reattachment, microVM clones, confidential providers and alternate stores need independent publication, freshness and terminal-incarnation proof before claiming parity.

Selected portable proof (2026-10-11): the operator approved the S3/Entity/EC2 protocol rebaseline. This ticket now owns Q-10 surviving-host control, Q-11 accepted-pair H2 restore without H1 disk and Q-12 live-partition denial until independently confirmed exact-incarnation termination. Each is a separate physical proof; mocks, directory appearance and safety parking do not establish accepted-data durability.

- Type: Verification
- Priority: Medium
- Estimate: 4 points (confidence 55 percent)
- Labels: Type: Verification, Topic: Workspace
- Parent: DSR-P4
- Blocked by: DSR-3.7
- Blocks: DSR-4.5
- Related: DSR-4.1, DSR-4.2
- Retires: A-27, A-48, A-59 (replacement Worker workspace part)
- Informs: A-21
- Owner role: Plugin engineer

#### Context

The selected contract requires exact accepted S3 pair restoration on a compatible EC2 guest after independent old-incarnation termination. Local POSIX and protected claims remain defense. Surviving-host replacement, original-disk-unavailable restore and live control partition are separate qualification cases; none is demonstrated by documentation.

DSR-0.6 owns exact configuration, responsible holders and qualification prerequisites for the approved target. Protected independent Entity authority must survive outer reset/restored preclaim files. The retained local exclusive-create guard is additional defense; declaring an untested limit cannot complete portable durability acceptance.

**Complete Issue 31 disposition (2026-10-08)**

October 8 full issue sweep: [I31-H4/H5](../proposals/distributed-recovery/2026-10-08/priority-sweep/coverage.md) retains this ticket's canonical shared-volume scope. Cold object, sandbox snapshot and microVM lanes need explicit BD-6 adopted scope before their evidence can close it. Prepared extension tests include crash before Docker exit snapshot, two-writer stale overwrite, refused E2B pause, nontransactional mount refusal, stale authenticated confidential bundle and independent old-host power/provider fencing. Matching accepted trajectory/workspace bytes and whole-tree termination are separate required proofs. Timeout, lease expiry, API deletion or volume detach alone is insufficient.

#### Problem

Mixed or missing accepted state can lose acknowledged work. Restored or regressed authority can repeat Bash, and premature replacement can race a still-live old execution. Exact accepted-pair validation, independent admission and terminal-incarnation proof resolve separate hazards.

#### Scope

- Prove Q-10 surviving-host replacement as a control, preserving exact native files/records and whole descendant cleanup.
- Prove Q-11 H2 restore of the accepted conversation/workspace/result pair with all H1 disk access denied, exact object versions/digests and native metadata.
- Prove Q-12 live control partition with old effect egress still active: H2 dispatch is denied until an independent controller reconciles exact terminal incarnation.
- Test conditional publication/head ACK loss, stale/mixed pairs, preclaim restoration, independent authority loss and unresolved postimage cleanup with the existing owners.
- Record independently witnessed physical counters and each case's failure boundary. Mocks do not qualify provider/storage semantics.

#### Out of scope

- Infrastructure execution without separate exact configuration, named owners and finite allowance.
- Production density, region-loss guarantees and live-memory restoration.
- Treating another provider, shared filesystem or volume detach as equivalent proof.
- Completing native child/parallel recovery from serial tests; DSR-7.4 owns the positive requirement.

#### Acceptance criteria

- [ ] Q-10 restores exact generated files, package, manifest, native pending/result records and approvals on a replacement after independently verified whole-execution cleanup. Proof: surviving-host hashes/identity and descendant witness.
- [ ] Q-11 restores the exact accepted pair on H2 without any H1 disk access, preserving hidden files, deletions, executable bits and admitted link/ownership metadata. Missing acknowledged bytes is FAIL. Proof: independently witnessed restore and corrupted/missing/mixed-pair negatives.
- [ ] Q-12 keeps old effect egress alive during control partition while readable S3 fails to admit H2. Lost termination reply reconciles account/region/instance/launch identity and authoritative terminated status before replacement. Proof: physical canary/effect counters and zero replacement before the witness.
- [ ] Duplicate/lost publication and admission replies reconcile original identity/bytes; preclaim rollback, authority recreation/regression and changed ordinal cannot schedule another physical effect. Proof: independent counters and exact status/result or park.
- [ ] Result/postimage/projection gaps and sole-readable cleanup failures park with no repeated effect or next model segment. Proof: publication-fault and cleanup-refusal records under DSR-2.3/4.2.
- [ ] Accepted native metadata and exact raw/accepted result identity survive replacement; unsupported paths/devices/metadata refuse before SDK startup. Proof: DSR-2.4/2.6 conformance vectors on the selected stack.
- [ ] An absent/stale terminal identity, timeout, cancellation, shutting-down or API disappearance never admits replacement. Earlier remote requests remain exact-outcome reconciliation or park. Proof: each negative and late-request witness.
- [ ] Every failed/unexecuted case retains its disposition and assumption gate; a safety park or declared limit is not portable durability PASS. Proof: DSR-4.5 reviewed evidence and unchanged historical failures.

#### Dependencies and blockers

- Blocked by DSR-3.7, the Phase 3 exit review.
- Blocks DSR-4.5.
- Related to DSR-4.1 and DSR-4.2, which own isolation and retained state lifecycle.
- DSR-0.2 retains claimed Bash and both local guards in approved Option R. DSR-0.6 prerequisites remain open; selected independent authority and physical qualification supplement those guards without closing acceptance.

#### Source evidence

- Canonical specification, *Package and filesystem boundary*, for exact accepted-pair validation and cold restoration.
- Canonical specification, *Effect identity, execution and outcomes* and *Timeouts and process lifetime*, for independent admission, retained local guards and exact-incarnation termination.
- Historical specification alternative A10 records the rejected volume ledger; it does not supply selected portable authority.
- Assumptions A-27 and A-48, and open issue OI-2.
- Review of revision 5, finding R5-08, for the atomicity assumption.
- SDK sessions do not preserve the filesystem: https://code.claude.com/docs/en/agent-sdk/sessions

#### Open questions

- Deployment/storage and Security owners: record exact S3 policy/key/region and EC2/AMI/kernel/container/controller identities and finite rig allowance before execution.
- Integration owner: pin accepted receipt schema and native adapter/API revision before proof.
- Retention owner: approve authority/object/key survival and administration denial; no numeric policy is inferred.

### DSR-4.4 Measure event loop lag, step cost and process containment

Status: OPEN

October 9 source reconciliation: [the maintained release-check comparison](../proposals/distributed-recovery/2026-10-08/priority-sweep/coverage.md#october-9-release-check-reconciliation) owns corrected matched-run timing evidence. Reported native port savings are about 0.1 seconds per step; incorrect savings distort capacity decisions. Matched local measurement remains pending, and no warm optimization or latency target is adopted. Status and acceptance criteria are unchanged.

- Type: Verification
- Priority: Medium
- Estimate: 4 points (confidence 55 percent)
- Labels: Type: Verification, Topic: Engine, Topic: Effects
- Parent: DSR-P4
- Blocked by: DSR-3.7, DSR-4.1
- Blocks: DSR-4.5
- Related: none
- Retires: A-28 (M4 part), A-41 (M4 part), A-43
- Informs: A-17
- Owner role: Plugin engineer

#### Context

The design assumes that the async segment Activity does not block the event loop. The fork code declares the Activity with `async def`, and no source tests the assumption (OI-20). The fork README reports 0.7 to 0.9 seconds and up to about 270 MB per segment, measured with an instant local model. The pack did not reproduce those figures. OI-8 asks for a measurement with real model latency.

The specification also says the executor waits for the whole process tree, and that a daemonized child and a partitioned host remain residuals. Slot sizing on the segment queue is a design decision that depends on measured memory.

**Complete Issue 31 disposition (2026-10-08)**

October 8 full issue sweep: [I31-H1](../proposals/distributed-recovery/2026-10-08/priority-sweep/coverage.md) adds cold/warm/hybrid/native replay comparators to measurement preparation. Upstream warm eligibility is same Worker/checkpoint and only original result within warm_seconds; callbacks, in-process MCP, max_turns and max_budget_usd exclude its reported lane. Compare instant-model overhead separately from real-model median/p95 and record starts, slots, memory and raw samples. Force cold fallback after retry/reset/host change/timeout/input change and verify policy/cleanup equivalence. Warm reuse does not reduce the separately launched native toolstep by itself. Optimization implementation remains out of scope; BD-4 sets objectives and BD-6 selects any follow-up. Reporter timings do not close this ticket.

#### Problem

If the event loop blocks under load, heartbeats arrive late and Heartbeat Timeouts fire without a real fault. If the real step cost is higher than the README figures, slot sizing and latency budgets are wrong for shell heavy skills. If a child survives an effect under load, the model is told an effect ended while it still acts.

#### Scope

- An event loop lag test under load on one Worker.
- A measurement report of seconds and memory per segment and per effect with real model latency, on the rig, for a representative skill.
- A process containment check at the configured slot count.
- A recommended `max_concurrent_activities` for the segment queue, derived from the measured memory.

#### Out of scope

- Optimizing step cost, batching effects, or asking for multi call defer. The report decides OI-8 and a later ticket acts on it.
- Changing the slot supplier type.
- Cross host behavior. DSR-4.3 owns it.
- Metric emission from Workflow code. DSR-5.7 owns it.

#### Acceptance criteria

- [ ] The lag test runs the configured number of concurrent segment and effect Activities on one Worker and records the maximum event loop lag and the count of Heartbeat Timeouts. The report states the threshold it used and why. The assumption is recorded as supported, or recorded as corrected with a design change. Proof: the captured test output and the recorded row text.
- [ ] The measurement report gives the median and the 95th percentile of seconds and of peak memory per segment and per effect, over a stated number of steps, with real model latency. It compares them with the README figures. Proof: the report as a recorded artifact with the raw samples.
- [ ] The report records the decision on OI-8 (keep reads in the engine, batch effects, or ask for multi call defer) with the owner role, and the limits text states the per step cost. Proof: the decision record and the limits text.
- [ ] The report derives a recommended `max_concurrent_activities` for the segment queue from the measured peak memory and states the formula it used. Proof: the report section.
- [ ] At the configured slot count, effects that start a daemonized child with `setsid` and a shell level background command leave no running process after the executor reports, or the report lists the exact residual. Proof: a rig test output that lists the process table after each report.
- [ ] A measurement run that reaches the budget cap stops, and the report labels any partial result as partial. Proof: the run record with the cap and the spend.

#### Dependencies and blockers

- Blocked by DSR-3.7, the Phase 3 exit review.
- Blocked by DSR-4.1, because the containment check needs the decided isolation.
- Blocks DSR-4.5.
- Uses the monitored real model test harness from DSR-1.1 with a separately approved exact measurement scenario and allowance. DSR-0.4 remains the final acceptance budget decision; strict preventive enforcement stays at DSR-5.8. The [canonical separation checkpoint](../canonical-documents.md), *Approved experiment authorization separation*, governs this distinction.
- DSR-0.2 retains Bash as a claimed effect in approved Option R. The containment criterion remains required at the isolation level that DSR-0.6 decides, with any unproven containment listed as a residual.

#### Source evidence

- Specification, INV-3, *Sandbox and imports* paragraph, for the event loop assumption.
- Specification, INV-2, *Sizing* paragraph, for the slot sizing decision.
- Specification, INV-7, *Effect isolation* paragraph, for the process tree wait.
- Assumptions A-28, A-41 and A-43, and open issues OI-8 and OI-20.
- Fork README figures at the pinned commit: https://github.com/osamastro7-droid/ai-integrations/blob/69f5497d3d3dec7ad3269c72ff266c2931c9f379/python/claude_agent_sdk/README.md#L93-L97
- Sync and async Activities in the Python SDK: https://docs.temporal.io/develop/python/best-practices/python-sdk-sync-vs-async
- Worker performance tuning: https://docs.temporal.io/develop/worker-performance/runtime-tuning

#### Open questions

- Plugin engineer: what number of concurrent Activities counts as load for the lag test? A proposal is the configured slot count of the segment queue.
- Budget owner: approve the exact measurement scenario, allowance and residual monitoring/accounting risks before execution; this ticket grants no model authorization. DSR-0.4 still owns the independent final acceptance allocation.
- Plugin engineer: which skill is representative? The measurement needs a skill with many shell commands, and the pack names none.

### DSR-4.5 Review Phase 4 evidence and decide continue or redesign

Status: OPEN

- Type: Documentation
- Priority: Medium
- Estimate: 2 points (confidence 80 percent)
- Labels: Type: Documentation, Topic: Assumptions
- Parent: DSR-P4
- Blocked by: DSR-4.1, DSR-4.2, DSR-4.3, DSR-4.4
- Blocks: DSR-5.1, DSR-5.2, DSR-5.3, DSR-5.4, DSR-5.5, DSR-5.6, DSR-5.7, DSR-5.8
- Related: none
- Retires: none
- Informs: A-17, A-21, A-27, A-28, A-37, A-41, A-43, A-48, A-51
- Owner role: Plugin engineer

#### Context

A phase ends with an exit review. The review updates the specification's assumption rows and the plan's milestone text with the evidence, and it records a continue or redesign decision. A contradicted assumption stops the next phase until the design change is recorded.

Phase 4 settles A-17, A-21, A-27, A-37, A-43, A-48 and A-51, and supplies the workspace part of A-54. It also supplies the M4 parts of A-28 and A-41. Other phase portions remain open until their evidence exists.

#### Problem

Without a recorded review, evidence stays in test output and the specification rows keep their old status. A later reader cannot tell which assumption the evidence settled.

#### Scope

- Update each Phase 4 row in the specification table with its new status and the name of the proving artifact.
- Update the plan's M4 milestone text and the retirement table row for each affected id.
- Record the continue or redesign decision for Phase 5.

#### Out of scope

- New measurements or new tests. The four earlier tickets own the evidence.
- Rows that Phase 5 settles.

#### Acceptance criteria

- [ ] Each of A-17, A-21, A-27, A-37, A-43, A-48 and A-51 carries a status in the specification table of verified at source with the proving artifact named, or contradicted with the design change recorded. Proof: the edited specification rows.
- [ ] A-28 and A-41 record M4 evidence, and A-54 records workspace refusal visibility without overstating executor proof. Each states any remaining open part. Proof: the edited rows.
- [ ] A row for a declared untested limit says so in its status text and names the README limits text. Proof: the edited rows.
- [ ] The plan's M4 milestone text and its retirement table match the specification by assumption id and check text. Proof: a side by side listing of the ids in both documents.
- [ ] After the edits, the evidence gate passes for the specification and for the plan. Proof: the captured output of the evidence script for each document, ending with `RESULT: PASS`.
- [ ] A decision record states continue or redesign for Phase 5, with the owner role and the date. A contradicted assumption names the design change that must exist before DSR-5.1 to DSR-5.8 start. Proof: the decision record.

#### Dependencies and blockers

- Blocked by every other Phase 4 ticket: DSR-4.1, DSR-4.2, DSR-4.3 and DSR-4.4.
- Blocks DSR-5.1 to DSR-5.8.

#### Source evidence

- Specification, section *Assumptions and risks if wrong*.
- Plan, sections *Assumptions retired by milestone* and *Milestones*, M4.
- Ticket set index, section *Phase gates*.

#### Open questions

- Operator: who confirms a redesign decision if the Plugin engineer and the Security owner disagree? The pack names no escalation role.

Current adapter admission: [the typed contracts](../spec.md#project-owned-adapter-record-and-operation-contracts) and [approved local configuration](../proposals/distributed-recovery/2026-10-08/dsr-0.6-configuration.md#approved-local-configuration-2026-10-14) own the selected interfaces, container-first sequence, PKI/reader/key policy, component admission and qualification limits. The decision ticket owns its status. Physical and component qualifications remain unexecuted; DSR-2.1 remains blocked while other prerequisites are incomplete.
