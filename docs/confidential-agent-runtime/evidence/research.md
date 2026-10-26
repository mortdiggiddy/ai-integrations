# Consolidated runtime and recovery research

Status: prepared evidence synthesis, 2026-10-26. Product observations are scoped to the cited source revisions. Proposed contracts and proving cases remain unimplemented.

## Upstream update during the formal pass

PR #169 advanced to [revision 2c722ff59250d3427ba5e43ea9713ecef959ee71](https://github.com/temporalio/ai-integrations/tree/2c722ff59250d3427ba5e43ea9713ecef959ee71/python/claude_agent_sdk) during the formal specification pass on October 26. This is P08 in the source catalog. P01 remains the historical cutover revision; the P01 findings below must not be presented as the current interface or unchanged defects.

The current optional seam is `TransportActivities` with `launch`, `write_stdin`, `watch_output` and `stop`. The invented Sandbox interface is removed. Default `subprocess_activities()` runs the CLI on the launch Worker's host and requires same host routing. This is a Temporal counterpart of the upstream subprocess transport, not the upstream `SubprocessCLITransport` instance itself. SDK and content callbacks still execute in Workflow code, so the confidential project boundary remains distinct.

The current close operation invokes the supplied CLI stop Activity; it does not inherently delete a VM. The README removed the earlier broad automatic sandbox recovery claim. The new launch script reserves its stdin directory atomically, closing the earlier two launchers passing the PID check window. Preserve those earlier findings as historical, not current defects. An interrupted reservation before process or PID publication remains a reconciliation test to qualify. Full native session and workspace replacement recovery remains a project acceptance obligation.

P08 locks SDK 0.2.163 and Temporal 1.34.0, with SDK bounds `>=0.2.163,<0.2.166`. The retained project checkout instead locks SDK 0.2.154 and Temporal 1.33.0. Source fetch is not dependency adoption. This pass fetched P08 to a review ref and left the working branch and application source unchanged.

Current source anchors: [transport API](https://github.com/temporalio/ai-integrations/blob/2c722ff59250d3427ba5e43ea9713ecef959ee71/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_transport.py#L105), [close](https://github.com/temporalio/ai-integrations/blob/2c722ff59250d3427ba5e43ea9713ecef959ee71/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_transport.py#L296), [launch reservation](https://github.com/temporalio/ai-integrations/blob/2c722ff59250d3427ba5e43ea9713ecef959ee71/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/scripts/launch.sh#L13) and [same host placement](https://github.com/temporalio/ai-integrations/blob/2c722ff59250d3427ba5e43ea9713ecef959ee71/python/claude_agent_sdk/README.md#L98). This is source analysis, not executed failure injection.

## Source baseline

| ID | Source and identity | What it supports |
|---|---|---|
| P01 | [Integration PR #169](https://github.com/temporalio/ai-integrations/pull/169), open draft at `18bc31e5005cbf403ebab38cb51e5cde4aa930a4`, rechecked October 26 | Current ordinary remote SDK topology and source findings below |
| P02 | [Claude Python SDK](https://github.com/anthropics/claude-agent-sdk-python/tree/1ef6d8c71bb0e44a6b33fe61497864f21e17fdb7), version 0.2.163 locked by P01 | Custom Transport restore behavior and mirror setup |
| P03 | [Sandbox Orchestration Harness](https://github.com/temporal-community/sandbox-orchestration-harness/tree/24f09129335f8057750f09f84a45b9c76c99d9c1) | Lifecycle controller, provider contract, ownership and idle behavior |
| P04 | [SDK mirror batcher](https://github.com/anthropics/claude-agent-sdk-python/blob/f7529348747235da34af3ed202251228ff31db08/src/claude_agent_sdk/_internal/transcript_mirror_batcher.py), version 0.2.165 inspected by the earlier recovery comparison | Historical implementation evidence that eager mirroring is not a synchronous execution barrier; not the P01 dependency pin |
| P05 | [Integration PR #103 source](https://github.com/temporalio/ai-integrations/tree/2f1c9b561384fab2e7b415dde91eb0b5900ea42f/python/claude_agent_sdk) | Historical native continuation and registered tool repair precedent |
| P06 | [Mods prototype](https://github.com/temporalio/ai-integrations/tree/9b968eb01e271bbf6d5e4d5cefbd6986871ed90d/python/claude_agent_sdk) | Historical native step interception and recorded result substitution |
| P07 | [Native parallel prototype](https://github.com/temporalio/ai-integrations/tree/fd9fe9c2e67adb287d20bfa3d1c3ab673b4d07a6/python/claude_agent_sdk) | Historical accepted batches, native result carriers and foreground child identities |

P05 through P07 are alternative prototypes, not a combined release. Historical test counts, author validation reports and branch names are not acceptance evidence for this composition. P01 and P03 are MIT source with tests, but no production readiness claim follows from that license or test presence.

## Trust requirements retained from the design history

The two parties supply different protected inputs: client code and a protected skill package. The operator administers outside orchestration. The final service must enforce the selected visibility and release rules even though neither party can inspect the other's confidential content.

| Topic | Retained requirement or decision | Remaining qualification |
|---|---|---|
| Stored content | Temporal storage and object storage hold encrypted content and permitted metadata only | Inspect payloads, failures, references, object names and diagnostics |
| Operator secrecy | Operator administrators cannot inspect client code, conversation or workspace plaintext | Keep plaintext processing inside the approved runtime and remove administrative bypasses |
| Skill secrecy | The client cannot inspect the skill package or recover it through released content | Validate output and question schemas; arbitrary natural language has no blanket nonleakage proof |
| Mutual key control | Neither party can decrypt protected job content alone | Qualify both approval and key release paths; the proposed wrapping scheme is not proved by this research |
| Approved execution | The runtime must prove its approved image and configuration before protected key release | Validate evidence, recipient, audience, freshness, debug state and job registration |
| External placement | The runtime holds no Namespace credential and runs no Temporal Worker in the target mode | Inspect image, environment, process and connection behavior |
| Model access | The model provider ordinarily receives plaintext inference inputs | Record the permitted trust assumption; confidential inference is a separate future profile |
| Infrastructure access | Protecting against the cloud hypervisor is distinct from excluding the workload operator | Select hardware protection only for the stronger declared threat model |

An approved attested image and a hardware confidential VM are not interchangeable claims. The earlier research identified AWS EC2 instance attestation and Google Confidential Space as candidates. It did not qualify either deployment end to end, compare current prices, prove asymmetric key behavior, or demonstrate the chosen tool isolation mechanism on the selected image. Reference [EC2 attestation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/nitrotpm-attestation.html), [KMS attestation conditions](https://docs.aws.amazon.com/kms/latest/developerguide/conditions-attestation.html), and [Confidential Space overview](https://docs.cloud.google.com/confidential-computing/confidential-space/docs/confidential-space-overview) before selecting a concrete profile.

The image must own environment, command arguments, logging, telemetry export, endpoint configuration and egress policy. Outside launch overrides must not expose content or change trusted policy. No operator remote shell, debugger, arbitrary file reader or plaintext provider snapshot is part of the final confidential profile. This restricts administrative access; it does not require removing the Bash functionality a native skill needs inside its confined execution environment.

Untrusted generated commands must be isolated from supervisor keys, storage credentials, repository credentials and gateway control access. A destination allowlist alone does not stop content leakage to an allowed destination. The proposed gVisor arrangement and native Bash sandbox are alternative isolation candidates, not qualified dependencies. [Secure deployment guidance](https://code.claude.com/docs/en/agent-sdk/secure-deployment) supports treating permissions and operating system isolation as separate controls.

The earlier direction selected fixed tool policy inside the runtime instead of human tool approvals in confidential mode. Showing tool arguments to either party can expose the other's content. Questions are released output: client fact questions may use a restricted typed schema through the output gate; skill method decisions need packaged defaults; mixed questions need an explicit fallback. The exact question schema remains open. Ordinary nonconfidential approvals remain a separate supported use case if selected.

Client prompts and answers need authenticated sealing, sequence checks and job binding before use. The client must not receive the job content key merely to submit a prompt. A gateway holds Namespace credentials outside the runtime and permits named operations for the registered job and generation only. Image attestation alone does not authorize a job. The gateway must not expose arbitrary Workflow start, reset, cancel, terminate or Signal capabilities to untrusted tools.

Temporal's codec documentation says plaintext exists in the executing Clients and Workers. Therefore an outside codec cannot hide content already processed by an outside Worker. A blind outside control plane requires sealing before that content crosses the runtime boundary. [Payload Codec](https://docs.temporal.io/payload-codec) and [data encryption](https://docs.temporal.io/evaluate/features/data-encryption) ground that distinction. Failures, Search Attributes, IDs, logs and telemetry need their own content policy; ciphertext payload bodies alone are insufficient.

## Native execution and the ordinary integration boundary

P01 keeps the native CLI loop, tools, skills, plugins and subagents. It places `ClaudeSDKClient`, approvals, hooks and SDK tools in Workflow code. `_transport.py` parses outgoing JSON at line 153 and incoming JSON at line 206. This topology assumes a trusted Worker. It does not satisfy the retained operator secrecy requirement merely because the remote CLI is inside a confidential VM.

For the target profile, SDK, CLI and content callbacks can communicate locally inside the approved runtime using `SubprocessCLITransport`. Outside orchestration exchanges sealed service operations. This is a proposed composition to qualify, not a supplied P01 deployment mode. It avoids making an ordinary remote SDK adapter a prerequisite for the confidential prototype.

The source findings worth retaining from P01 are these:

1. **Launch identity gap.** [`launch.sh:8`](https://github.com/temporalio/ai-integrations/blob/18bc31e5005cbf403ebab38cb51e5cde4aa930a4/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/scripts/launch.sh#L8) checks for a PID file, starts a process, then records its PID. Rename prevents a partial PID read, not overlapping launches or a lost launch result before PID publication. The inspected retry test is sequential for launch. Concurrent launch and lost reply tests are pending.
2. **Recovery scope gap.** [`watch_output`](https://github.com/temporalio/ai-integrations/blob/18bc31e5005cbf403ebab38cb51e5cde4aa930a4/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_activities.py#L72) reconstructs a wrapper and follows existing output. It does not start replacement compute or establish a new native resume transition. The retained PID and boot handling does not supply a complete replacement protocol. Lost watcher coverage with a surviving CLI is useful but narrower than host destruction.
3. **Custom Transport store qualification.** P02 [`client.py:117`](https://github.com/anthropics/claude-agent-sdk-python/blob/1ef6d8c71bb0e44a6b33fe61497864f21e17fdb7/src/claude_agent_sdk/client.py#L117) skips SessionStore materialization when a custom Transport is supplied, while [`client.py:226`](https://github.com/anthropics/claude-agent-sdk-python/blob/1ef6d8c71bb0e44a6b33fe61497864f21e17fdb7/src/claude_agent_sdk/client.py#L226) still installs the mirror. Setting the option does not restore remote files automatically. An adapter called from Workflow code must also respect Workflow execution constraints.
4. **Ownership question.** P01 close reaches `sandbox.terminate()`. A borrowed runtime needs explicit communication close, CLI stop and compute removal meanings. Removing the extra Sandbox abstraction does not automatically settle them.

These are pinned source observations and failure reasoning, not reproduced production incidents. The announced Transport redesign is intent until a changed source revision exists. P01 already discloses history growth, payload size, concurrent session access and additional reset/resume tests as draft work. Do not present those disclosures as newly discovered omissions.

## Recovery representations and their limits

Native SessionStore mirrors transcript entries. It can include discovered subagent transcripts when the required subkey interface is implemented. It is not process memory, a complete workspace capture or a durable external effect ledger. The [session storage guide](https://code.claude.com/docs/en/agent-sdk/session-storage) and P04 distinguish asynchronous mirroring from an execution barrier. Eager flush frequency does not make every dependent action wait for durable append. Append failures, timeout and late landing writes need explicit reconciliation.

Interrupted turn continuation can cause another model request. That is a recovery behavior and cost tradeoff, not a correctness failure by itself. It is not proof that every missing tool runs before another request or that an acknowledged original result survives. Graceful SIGTERM, abrupt process loss and host loss are different cases. See [environment variables](https://code.claude.com/docs/en/env-vars) and [programmatic execution](https://code.claude.com/docs/en/headless).

P05 provides partial hybrid precedent: it loads native entries, identifies dangling registered Workflow tools, retrieves their recorded results and repairs the transcript before CLI startup. That treatment does not apply automatically to arbitrary Bash. At the inspected source, it disables native features required by this project, and its lease wrapper documents a check then append takeover race. It is component prior art, not a complete replacement engine.

P06 substitutes recorded native model and tool results, but uses checkpoint Signals and replay Queries rather than a proved accepted workspace contract. It streams model chunks before complete model persistence. A missing checkpoint is not always permission for new work: committed prefix loss or mismatched identity must refuse. Native read caches, working directory behavior, compaction, nested agents and edit prerequisites need exact runtime tests. The earlier Mods first recommendation is superseded as the default integration route, not proof that the prototype has no useful component.

P07 records complete native assistant batches and preserves original result carriers and foreground child identities. Its shared filesystem assumption and runtime qualification remain material limits. Native accepted batches, strict recorded step replay and native continuation are separate modes. Do not combine their guarantees into one durable flag or require all three to finish the first native prototype.

The old exact original pending call guarantee, protected independent dispatch authority and strict preventive spending requirements are not retired by choosing native continuation. Their disposition belongs to explicit owner decisions. The prototype must state the limits it proves while those final contract choices remain open.

## One coherent recovery state

Retain the publication principle: encrypt immutable content, upload it completely, then accept a reference that binds the session representation, workspace version, pinned inputs, generation and predecessor. Reconcile an uncertain acknowledgment using the same identity. An uploaded object, best effort transcript tail, stdout offset or independent latest pointer is not sufficient authority to restore a state.

P01's [`test_chat.py:207`](https://github.com/temporalio/ai-integrations/blob/18bc31e5005cbf403ebab38cb51e5cde4aa930a4/python/claude_agent_sdk/tests/integration/test_chat.py#L207) waits for transcript appearance after stdout. This supports testing the acknowledgment interval; it does not measure loss or prove every transcript write unsafe. The final recovery contract must say what acknowledged progress survives and what unaccepted work can repeat.

Capture the filesystem rather than infer changed bytes from Bash commands. Preserve required hidden files, deletion, rename, mode and link behavior, plus native session sidecars and configuration. Fetch immutable base repository and skill package by commit and digest where appropriate. Exclude credentials, host mounts and nonportable process state. Rebuild dependencies from the pinned image or lockfiles. Restoring files does not restore active sockets, shells or arbitrary process memory.

Capture must account for all writers. A post tool hook can observe another tool's partial write or a detached child. Options include session wide serialization through acceptance, a quiescent whole batch boundary, or separately specified isolated workspaces and merge. Disabling a background flag alone does not contain a detached process. Restore the selected accepted workspace on every start, including the same host, so unaccepted local writes do not contaminate a resumed session.

Scope uploads by job and generation, reject stale publication and conflicting duplicate content, and retain accepted referenced objects and keys across waits and recovery. Late uploads are unaccepted garbage, not a new head. Cleanup must not remove a live recovery dependency just because an old Workflow run closed. Retention, crypto erasure, custody and garbage collection remain explicit policy work; no numeric value is approved by this synthesis.

Unknown external mutations cannot be repaired by transcript restoration or workspace rollback. A command may commit a remote action before its result is saved. Use destination enforced idempotency, authoritative outcome lookup or a stopped uncertain state. A pre execution refusal means the action did not run; uncertainty must not be relabeled refusal. [Activity idempotency](https://docs.temporal.io/activity-definition#idempotency) supports this boundary. Logical generation checks do not physically stop old processes or revoke uncontrolled destination credentials.

Preserve honest authoritative history as the freshness assumption for ordinary crash recovery. A MAC authenticates an old record but does not by itself prove freshness. The inherited confidentiality threat scope excludes malicious operator rollback integrity; stronger protection is an open threat decision, not an automatic requirement for an independent antirollback service.

Continue-As-New changes the Workflow run and requires explicit application state transfer. It does not compact the model's semantic context. Retain the accepted recovery reference, identity, generation, deduplication and necessary storage/key access, and resolve old handlers and watchers according to the selected lifetime contract. [Continue-As-New](https://docs.temporal.io/develop/python/workflows/continue-as-new) is mechanism evidence, not proof of this composition.

## Lifecycle and capability conclusions

Reuse the existing harness controller, not just its provider interface followed by a second controller. P03 already separates owning and attached references. Its provider `Start` contract assumes an internal Worker; an explicit external runtime mode removes that ambiguity. Reject unsupported requested combinations before provisioning and preserve existing provider defaults.

Provider running, communication ready, authenticated runtime ready, attestation accepted and recovery accepted are different observations. Stable create identities and reconciliation after unknown replies are necessary for the selected one owner outcome. A heartbeat timeout, communication disconnect or cancellation request does not establish physical teardown. Use explicit terminal observation and an ownership scoped orphan reconciler where the lifecycle contract requires it. Exact contracts remain design work.

P03 idle handling starts around `ExecuteCommand`. An autonomous agent can continue after a setup command returns or never call that API. Initially use `NoIdleTimeout` rather than claim runtime aware idleness. Optional touch, lease and cost policies can follow a real need. A provider snapshot may be filesystem only, not process memory; confidential mode must not silently fall back to a snapshot that exposes keys or plaintext.

Harness PR #4 is Worker and Task Queue separation preparation, not a delivered Python SDK. PR #5 is an optional Nexus service boundary, not the confidential content gateway. PR #6 is merged in P03 and supplies useful resource adoption and readiness precedent. The older main pin and open PR #6 status in the imported October 16 notes are historical. PR #1 supplies retry identity tests. These sources justify focused reuse, not merging every open branch or implementing the full older roadmap.

## Observability and measured cost

Use the [Agent SDK observability guide](https://code.claude.com/docs/en/agent-sdk/observability) for the local CLI instrumentation route. The broader platform announcement does not make trace propagation across a custom remote Transport automatic. Collector access and exported content remain part of the trust policy. Keep telemetry credentials out of recorded launch options. Buffered telemetry can be lost on abrupt death and is not recovery authority.

A five minute duration does not predict action rate. Measure Activity executions, protocol messages, Signals or Updates, polling, heartbeats, history bytes, encrypted storage writes, model requests and actual effects for the selected implementation. Old Mods arithmetic and price examples are historical illustrations, not a current cost estimate or a service budget. No benchmark was run for this migration.

## Coverage and deferred scope

| Imported topic | Current owner | Disposition |
|---|---|---|
| Trust, keys, plaintext placement, input and output classes | Replacement specification and owner decisions | Retain requirements; implementation remains unqualified |
| Native recovery choices, source findings, workspace consistency and effects | Replacement specification, obligation map and this evidence | Retain safety objectives; changed exact guarantees remain open |
| Controller reuse, placement and capability admission | Replacement plan | First bounded contribution; broad controller hardening follows demonstrated need |
| Runtime and gateway pseudocode | Historical evidence | Unrun sketch; do not copy assumed helpers as production APIs |
| Second harness qualification | Broader service exit criteria | Retain as deferred until the first runtime contract is proved; not a first prototype prerequisite |
| Multiple cloud providers, confidential inference, universal streaming, Nexus and Python client breadth | Future extension decisions | Deferred capability qualification, no implicit support claim |
| Durable Workspace and TemporalZFS | Historical prior art | Reference concepts only; no new server or filesystem product dependency |
| Earlier A1 deployment and Mods first sequence | Historical alternatives | Preserve rationale and version evidence; not the selected target decomposition |
| Archived source snapshots, diagram assets and verification bookkeeping | Historical provenance | No new requirement or runtime qualification inferred |

The decisive next evidence is one native skill with local file mutation, controller loss separately from runtime loss, original host removal, coherent restoration, stale generation refusal and independent effect/request counters. Add wrong image, wrong job, debug configuration, key release and content canary tests before confidential activation. Use one provider first. Do not expand this evidence consolidation into another market survey or treat a container test as mutual confidentiality.
