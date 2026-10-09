# Phase 4 tickets

### DSR-4.1 Isolate effects at the decided level

Status: OPEN

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

The specification describes a janitor that runs outside the Workflow. It removes `work/` and `.claude/` of a run only when Temporal reports the Workflow closed or not found, after a grace period. It uses no lease file and no modification time, because an idle human wait or a park runs no segment and leaves the directory untouched for days.

The janitor removes the claims directory only after the namespace retention ends, because a reset can reopen a closed run. The manifest holds the namespace, the Workflow Id, the lineage id, the start time and the package hash. The janitor requires the lineage id of a described run to match the manifest.

The manifest `generation` counts prepare and `reprepare` calls, and the Workflow stores it as `volume_generation`. Approved Option R drops the claims high water counter. Generation checks can detect a snapshot older than a recorded prepare, but do not prove detection of a mid run snapshot that removes later claims or file edits.

#### Problem

A janitor that deletes the files of a live run, or a restored volume that diverges without notice, causes silent data loss. Both are High severity in A-21. A reused Workflow Id or a wrong namespace can also make the janitor delete a live run (A-51). The sixth critique found that the counters have no rebaseline after `reprepare`, that a lost effect result leaves the Workflow value behind, and that the counter covers claimed effects only.

#### Scope

- The janitor, with the status based rule, the grace period, the lineage match and the retention rule for claims.
- The manifest check on every segment and the `reprepare` step, to the extent that DSR-2.1 did not already build them. If DSR-2.1 built part of this, this ticket proves it and builds the remainder.
- Manifest generation checks, the operator visible refusal and park that follow a stale value, and a defined baseline after a legitimate `reprepare`.

#### Out of scope

- Behavior on a network file system. DSR-4.3 owns it.
- Isolation of effects. DSR-4.1 owns it.
- The choice of the retention value. The deployment owner sets it (OI-10).
- Complete mid run snapshot detection for claim files or Write and Edit file state. Approved Option R retains manifest generation checks, not the claims high water mechanism.

#### Acceptance criteria

- [ ] The janitor removes `work/` and `.claude/` of a run whose Workflow was terminated, timed out or cancelled, after the grace period. Proof: a test against a dev server with a short grace period.
- [ ] The janitor never removes the directory of a live idle run or of a live parked run that waits for days. Proof: a test that leaves a run idle past the grace period with an old modification time and shows the directory intact.
- [ ] The janitor removes nothing when Temporal is unreachable or returns any answer other than closed or not found. Proof: a test with a failing status call.
- [ ] The janitor keeps the claims directory until the namespace retention ends and then removes it. Proof: a test with a short retention value, and the written statement of how the janitor reads the value.
- [ ] A run whose Workflow Id was reused keeps its own directory. A described run whose lineage id differs from the manifest is not treated as the same run. Proof: a test for each case.
- [ ] A janitor pointed at a wrong namespace never deletes the directory of a live run. Proof: a test where the wrong namespace reports not found for a live run and the directory remains.
- [ ] A segment fails when the manifest is missing, and `reprepare` repairs the directory so the next segment starts. Proof: a test that shows the failure, the repair and the next segment.
- [ ] A volume restored from a snapshot taken before the last prepare reports a lower `volume_generation`. The run parks with the cause named and the model receives no message about it. Proof: a test with a restored volume.
- [ ] After a legitimate `reprepare`, the next claimed effect is not refused as stale. The specification states how `reprepare` and `resume` set the stored `volume_generation`, and a test shows the next effect running. Proof: the specification text and the test output.
- [ ] The limits text states that restore detection is best effort and names the file state that it does not cover. Proof: the reviewed text recorded in DSR-4.5.

#### Dependencies and blockers

- Blocked by DSR-3.7, the Phase 3 exit review.
- Blocks DSR-4.5.
- Related to DSR-4.3, which tests the same volume on two hosts.
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

### DSR-4.3 Prove shared volume behavior on two containers over a network file system

Status: OPEN

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

Version 1 needs one shared volume that every segment and effect Worker mounts at the same absolute path. The volume must give POSIX semantics, close to open consistency and one user and group mapping on every host. Cross host behavior is untested, and the specification calls it a limit until a two container rig exists.

DSR-0.6 decides the volume class and whether the rig is built or the untested limit is declared. The claim file guard uses an exclusive create (`O_CREAT | O_EXCL | O_NOFOLLOW`). The first design rejected a ledger on the volume because it needed this same property.

**Complete Issue 31 disposition (2026-10-08)**

October 8 full issue sweep: [I31-H4/H5](../proposals/distributed-recovery/2026-10-08/priority-sweep/coverage.md) retains this ticket's canonical shared-volume scope. Cold object, sandbox snapshot and microVM lanes need explicit BD-6 adopted scope before their evidence can close it. Prepared extension tests include crash before Docker exit snapshot, two-writer stale overwrite, refused E2B pause, nontransactional mount refusal, stale authenticated confidential bundle and independent old-host power/provider fencing. Matching accepted trajectory/workspace bytes and whole-tree termination are separate required proofs. Timeout, lease expiry, API deletion or volume detach alone is insufficient.

#### Problem

If an exclusive create is not atomic and visible across hosts, two hosts can both create a claim file and both spawn the command. The at most one spawn guarantee then fails without any error. Stale or missing files on a second host also cause divergent steps.

#### Scope

- A rig of two containers that run the one image of the plugin, each with the segment and effect roles, on a real network file system of the class that DSR-0.6 records.
- Tests for tree visibility, close to open behavior, user and group mapping, concurrent exclusive create and the per run exclusive lock.
- A recorded pass or fail result for each test.

#### Out of scope

- Production tuning or performance of the file system.
- The choice of the volume class. DSR-0.6 owns it.
- Janitor and snapshot behavior. DSR-4.2 owns it.
- A microVM or object storage strategy.

#### Acceptance criteria

- [ ] A tree written by a prepare Activity on container A is visible with a matching package hash to a segment that starts afterward on container B. Proof: a rig test that compares the hash on both containers.
- [ ] A file written by an effect on container A in `work/` is visible to a Read call in the engine on container B after the effect reports. Proof: a rig test that records the read result.
- [ ] After container A and its local session directory disappear, container B restores the generated files, package and manifest through the approved workspace preservation mechanism and restores conversation state separately. A surviving transcript alone does not satisfy this case. Proof: a replacement Worker test with file hashes, matching manifest, session checkpoint and recorded approval and outcome identity; missing or conflicting state refuses continuation. Any adopted native path includes the crash boundary from DSR-2.4.
- [ ] Both containers map the same user and group to the same owner on every file in the tree. Proof: a rig test that lists numeric owners from both sides.
- [ ] Two containers that issue an exclusive create for the same claim file name at the same time give exactly one success and one `EEXIST` result, repeated over a stated number of rounds. Proof: a rig test log with the round count and the result of each side.
- [ ] A claim file created by container A is seen by container B at its next attempt, so container B refuses to spawn. Proof: a rig test that shows the refusal on container B.
- [ ] The per run exclusive lock serializes two effects of one run that start on different containers, or the test records that lock semantics on this file system do not hold and names the consequence. Proof: a rig test result and its recorded interpretation.
- [ ] A failed test records the contradiction, and a design change is recorded for the affected assumption. A proposal is to restrict claimed effects to one host. Proof: the recorded design change that DSR-4.5 reads.
- [ ] If the rig cannot be built, the README limits text lists the untested cross host behavior, and the rows A-27 and A-48 keep a status that says the limit is declared. Proof: the limits text and the row status. DSR-6.1 and DSR-6.2 decide whether a declared limit settles the row.

#### Dependencies and blockers

- Blocked by DSR-3.7, the Phase 3 exit review.
- Blocks DSR-4.5.
- Related to DSR-4.1 and DSR-4.2, which share the volume layout.
- DSR-0.2 retains claimed Bash and both claim guards in approved Option R. The claim file criteria remain required; DSR-0.6 still decides the volume class and rig availability.

#### Source evidence

- Specification, INV-2, *Workspace* paragraph, for the volume requirements and the untested limit.
- Specification, INV-1, *Claimed effect guard* paragraph, for the exclusive create of the claim files.
- Specification, Alternatives considered, A10, for the rejected ledger.
- Assumptions A-27 and A-48, and open issue OI-2.
- Review of revision 5, finding R5-08, for the atomicity assumption.
- SDK sessions do not preserve the filesystem: https://code.claude.com/docs/en/agent-sdk/sessions

#### Open questions

- Operator: which network file system class does DSR-0.6 name, and who provides the rig hosts?
- Operator: does a declared untested limit settle A-27 and A-48 for PASS? The ticket set index defines a settled row as verified at source or changed by a recorded design change. A declared limit meets neither text. DSR-6.1 and DSR-6.2 need an answer.
- Plugin engineer: Option R drops claims high water. This volume rig must still prove both retained claim guards and must not claim complete snapshot restore detection.

### DSR-4.4 Measure event loop lag, step cost and process containment

Status: OPEN

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
