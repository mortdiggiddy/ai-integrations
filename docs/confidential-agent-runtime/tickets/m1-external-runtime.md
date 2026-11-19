# M1 external runtime delivery

### CNR-1 Deliver external runtime orchestration

Status: OPEN

- Type: Epic
- Priority: High
- Estimate: none
- Labels: none
- Parent: none
- Blocked by: CNR-6
- Blocks: CNR-10
- Related: none
- Owner role: Harness contribution owner
- Requirements: CR-03, CR-06, CR-15; applicable AC-03 and AC-04

#### Context

The [M1 plan](../plan.md#m1-explicit-external-runtime-support) uses the existing Go harness. The earlier mode/interface design review passed; the revised configuration based mechanism requires scoped review and implementation verification.

#### Problem

The maintainer confirmed that the existing provider interface supports compute without an inside Temporal Worker. Native process launch should use provider configuration and the existing lifecycle owner.

#### Scope

Deliver CNR-2 through CNR-6 as additive harness changes, one existing provider extension and a reproducible generic example.

#### Out of scope

Native Claude integration, recovery snapshots, suspend/resume, attestation, paid inference and live cloud qualification belong to later work or separately authorized checks.

#### Acceptance criteria

- [ ] CNR-2 through CNR-6 meet their criteria with resolvable evidence at the exact reviewed revision.
- [ ] The M1 review package contains the runnable example, legacy replay result, fake provider conformance results and independent implementation verdict.
- [ ] The proposed upstream contribution states the admitted fresh start profile and the remaining provider and security limits. Maintainer acceptance remains a separate merge gate.

#### Dependencies and blockers

CNR-6 owns M1 acceptance. No later confidential policy decision blocks this generic contribution.

#### Source evidence

[M1 contract and evidence mapping](../ticket-evidence.md#m1-evidence-and-acceptance-map); [M1 design review](../verification-report.md).

#### Open questions

Maintainers may request different additive API names. Record any material semantic change before implementation proceeds under a changed contract.

### CNR-2 Launch an explicit external runtime without changing legacy execution

Status: DONE (2026-10-27)

- Type: Feature
- Priority: High
- Estimate: 4 points (confidence 80 percent)
- Labels: Type: Feature, Topic: External runtime
- Parent: CNR-1
- Blocked by: none
- Blocks: CNR-3, CNR-4
- Related: none
- Owner role: Harness contribution owner
- Requirements: CR-03, CR-06, CR-15; applicable AC-03 and AC-04

#### Context

The harness uses `Provider.Start(ctx, taskQueueName)`. The maintainer clarified through the operator on 2026-10-27 that the Worker bootstrap comment is historical and provider configuration is the preferred way to select a host without a Worker. This replaces the earlier separate mode/start interface selection.

#### Problem

A configured native process must not receive unintended Worker bootstrap or change existing configurations. Retries must retain resource identity and configuration; old histories must retain their command selection.

#### Scope

Revise the launch contribution to use provider configuration and the existing start Activity and controller. Remove the separate mode/start interface requirement. Prove stable input, resource identity and legacy compatibility with recording fake providers and fresh histories. Provider admission belongs to CNR-3; initial and later lifecycle policy belongs to CNR-4. Keep earlier verification evidence as historical and run a fresh full verification pass for this revised scope.

#### Out of scope

Actual SmolCloud native configuration, allocation/adoption admission and configuration specific restore refusal are CNR-3. Initial idle/snapshot admission, later operations and attached references are CNR-4. This compatibility contribution does not claim those policies are enforced or the complete native process feature is ready. No new controller, Python harness SDK or Nexus service is required.

#### Acceptance criteria

- [x] Recording provider tests prove unchanged configurations use existing `Start` with the original queue, defaults and command selection. Retained legacy parent and controller histories replay without a nondeterminism error. Source: M1 plan and H1/H2/T2.
- [x] A native process configuration uses the same `Start` interface without requiring an inside Worker. A retry test proves identical stable start identity and configuration on both attempts; no second launch identity is required unless existing identity is insufficient. Source: M1 plan and T1.
- [x] Unknown providers and invalid configuration rejected by the configured provider constructor produce zero start/allocation calls through existing SDK/controller and direct receiving Activity routes. Valid unchanged configurations require no new optional interface or capability lookup. Do not add global rejection of unknown configuration keys. Source: M1 plan and H1/H2.
- [x] Tests show existing default and explicit `NoIdleTimeout` options and initial snapshot selection retain their original interpretation and routing. Fake native execution explicitly selects `NoIdleTimeout`. Native configuration specific idle/snapshot/restore admission remains required under CNR-3/CNR-4 and is not claimed by these compatibility tests. Source: M1 plan and H1/H2/T2.
- [x] Existing serialized inputs and registrations remain compatible. Fresh history and retained state show the selected provider configuration and stable resource identity through the existing start path. No parallel external Activity family is added merely for placement. Any historical command change requires a separate activation/versioning plan. Source: M1 plan and T2/G1.

#### Dependencies and blockers

Start against harness revision H0. Inspect the changed registration and caller paths before editing. Record the selected source revision and any relevant upstream delta in the contribution.

#### Source evidence

[M1 plan](../plan.md#m1-explicit-external-runtime-support); [H0, H1, H2, T1, T2 and G1](../ticket-evidence.md#inspected-sources).

[BD-10](../decisions.md#decision-and-design-register) records the replay scope for configuration keys that a policy resolver reads.

**Merged contribution:** [PR #7](https://github.com/temporal-community/sandbox-orchestration-harness/pull/7) is merged at `d8a7d5b8b3782e26ff803678b097eed548c8c8ac`, with final head `26df2abc0ad3eb86efbb6259a70a3cfab1e79005`. Both hosted SDK test runs, Go analysis and CodeQL pass for that head. The [current contribution evidence](../ticket-evidence.md#current-contribution-evidence) supplies exact check links. Maintainer acceptance applies to that merged scope; CNR-4 completion and full M1 acceptance remain separate. Earlier independent verification remains evidence for its named revision.

**Prior compatibility-only implementation acceptance evidence:**

Verified and published revision: `9addcda9e6cf7dd03bb194dbec37c138e2a7ab82`, base `24f09129335f8057750f09f84a45b9c76c99d9c1`, [PR #7](https://github.com/temporal-community/sandbox-orchestration-harness/pull/7). The operator requested one combined commit. It replaces the two draft commits and has the identical tree `a8794c1d81313c2f89b8c4f32d247f6c6ddbb7b8` as independently verified source revision `028bd08d69ea592972d352908b06881215479c2c`. Canonical per commit verification passed again on the replacement. Upstream still matched the reviewed baseline before publication. The executable provider/SDK/controller paths match that baseline; only the provider contract comment changes in production source. The revised contribution removes the earlier separate mode/interfaces and Activity family. The committed tree matches source snapshot SHA256 `81974bdad209e2bc8707c66a1f278e37bfa656d222620ef4cac17b57c5863cab`, computed over the compact sorted path-to-SHA256 map of all 72 tracked files.

- Existing start and retry proof: `TestExistingStartRetriesPreserveProviderConfiguration` and `TestLocalNativeProcessHistory` run a bounded local process through a fake provider, retain queue/configuration across actual Activity attempts and observe one fake resource. No inside Worker polls the resource queue. [Conformance tests](https://github.com/temporal-community/sandbox-orchestration-harness/blob/9addcda9e6cf7dd03bb194dbec37c138e2a7ab82/sdk/provider_start_test.go) and [fresh history tests](https://github.com/temporal-community/sandbox-orchestration-harness/blob/9addcda9e6cf7dd03bb194dbec37c138e2a7ab82/sdk/provider_start_history_test.go).
- Refusal and compatibility proof: direct Activity and public SDK invalid provider/configuration matrices produce zero start/allocation calls; opaque provider fields remain valid. `TestExistingSandboxWireShapes`, `TestExistingSandboxRegistrationContract`, option forwarding and snapshot routing tests pass. Both retained legacy histories and four fresh parent/controller histories replay.
- Fresh independent contract, mutation and structural invariant reviews pass. The final matrix detects 42 distinct relevant faults, with no unresolved survivor. A default timer mutation exposed a test gap; corrected assertions now reject both the six minute timer and any timer under `NoIdleTimeout`. Unrelated controls preserve all 695 materialized wire bytes. Six focused compiler probes reject broken interface/record contracts with intended diagnostics.
- Lead rerun and canonical per commit verification pass on the exact revision: 33 top level tests and 53 passing results including subtests, two expected skips for live cloud execution and fixture regeneration, vet, all 12 Makefile binary targets and the database example build. Focused race verification passes eight top level tests and 26 results including subtests, with no skips. Builds use the documented temporary replacement for the baseline's unavailable SDK pseudo version; tracked dependency files remain unchanged.

Local CNR-2 acceptance is complete. GitHub CodeQL and its Go analysis passed on source revision `028bd08d69ea592972d352908b06881215479c2c`, completed at 2026-10-28T00:00:35Z. Fresh CodeQL is running on the published combined commit; the earlier CI result does not qualify that revision. Maintainer acceptance remains separate. CNR-3/CNR-4 still own concrete provider admission and initial/later lifecycle policy. Full native process acceptance still needs both plus the demo. No cloud allocation, paid inference, recovery, attestation or confidential deployment was performed.

**Earlier implementation evidence, superseded mechanism:**

The maintainer's clarification and the operator's direction on 2026-10-27 replaced the mode/interface mechanism with provider configuration through existing `Start`. The ticket was reopened for that revision. The following evidence remains valid for the earlier implementation only; the completed revised acceptance is recorded above and does not transfer the earlier verdict.

The operator subsequently approved the minimal division on 2026-10-27: CNR-2 proves existing start and compatibility; CNR-3 owns concrete provider admission; CNR-4 owns initial and later lifecycle policy. Existing `Start` receives no controller idle option, so its direct calls validate the provider information they actually receive. CNR-4 must inspect actual idle/snapshot choices at controller initialization. Complete native process acceptance still requires CNR-3/CNR-4 and the CNR-5 demo; no guarantee is removed by this reassignment.

Implementation: `temporal-community/sandbox-orchestration-harness`, branch `external-runtime-launch`, commit `b9b5675810895efdaa030d4db7d67a4491bf0339`, base `24f09129335f8057750f09f84a45b9c76c99d9c1`. Upstream matched H0 before editing and before the PR attempt. The committed source matches reviewed snapshot SHA256 `90cd3e948bcf9a5ea9a622302856c7d5fc885c11fb4bd6088b8d2e50206be86c`, computed over the sorted path-to-SHA256 map for the 16 changed files using compact JSON.

Draft PR: https://github.com/temporal-community/sandbox-orchestration-harness/pull/7, published under the operator's later PR request after SAML SSO reauthorization. The published revision is the earlier implementation commit. Per commit verification passed, including the SDK suite, retained and fresh histories, vet and all example builds. At publication, GitHub CodeQL was running; this note does not assert its current result. Maintainer feedback now requires the configuration based revision. This documentation update does not change the PR or its code.

The five superseded criteria are retained here as the exact acceptance basis for that proof:

- Recording provider tests prove omitted and zero mode use legacy `Start` with the original queue and command selection. A retained legacy history replays without a nondeterminism error. Source: M1 plan and H1/H2/T2.
- An explicit external request reaches only the optional external start interface with nonempty, retained `SandboxID` and `LaunchIdentity`. A retry test shows identical identity and configuration on both attempts. Source: M1 plan and T1.
- Unsupported or unknown modes, absent optional interfaces, failed capability lookup and unsupported requested capabilities produce zero allocation calls. Tests cover both SDK/controller entry and direct receiving Activity input. Source: M1 plan and H1/H2.
- The first external profile requires explicit `NoIdleTimeout` and refuses snapshot, restore, suspend/resume and unsupported idle policies before dispatch. Tests prove external failure never falls back to legacy `Start`. Source: M1 plan and H1/H2.
- New external Activity names and explicit inputs preserve the old serialized input interpretation and registrations. Tests inspect retained controller mode/profile/configuration and fresh external history. Any historical command change requires a separate activation/versioning plan. Source: M1 plan and T2/G1.

- Legacy proof: `TestSDKPlacementSelection`, `TestLegacyStartKeepsQueueWithoutCapabilities`, `TestLegacyInputSerializationUnchanged` and `TestRetainedLegacyReplay` pass. The retained parent and controller histories were captured from unchanged H0 production source. Their fixture SHA256 values are `04af535e512909d0dc1ef31558d6461f05bba13615383f20145ea6333fc9a2a4` and `7cef88826f8dcfba7950d6d5bcaf9e74f59c41620fa94922d40c18acdab33d3e`.
- External proof: `TestFreshExternalHistory`, `TestControllerRetainsExternalAdmissionAndRetry` and the controller/direct Activity refusal matrices pass. Tests cover retained configuration, retry identity after a lost reply, each disabled initial policy, missing interfaces, failed capability lookup, no fallback and conflicting initialization. `TestAcceptedExternalHandlerInterleaving` also checks handlers without a second validator call.
- Independent `verify-change --mutation-sensitive` with structural invariants: PASS. Three isolated initial contexts reviewed the contract, mutation sensitivity and structural invariants. The final mutation matrix has 55 killed faults, two equivalent validator checks confirmed by a second reader and one passing unrelated provider control. No relevant survivor remains.
- Lead rerun: `GOWORK=off HARNESS_LOCAL_TEST=1 go test -json -count=1 ./...` passes 45 top level tests and 94 results including subtests, with two expected skips for live cloud testing and fixture regeneration. Vet, all 12 existing Makefile binary targets and the database example build pass. The existing example modules reference an unavailable SDK pseudo version; builds use a temporary workspace replacement to the local SDK, with tracked module files unchanged. The placement unit test retains an enabled ten second detector allowance for SDK binary checksum setup; production defaults and all acceptance assertions are unchanged.

Scope remains CNR-2. Actual provider provisioning/adoption is CNR-3. Later operation and attachment enforcement is CNR-4. The generic demo and complete M1 acceptance remain open. No live allocation, paid inference, recovery, attestation or confidential deployment was performed.

#### Open questions

Prove the existing contract and identify only demonstrated missing checks in scope. Concrete provider and lifecycle policy mechanisms remain owned by CNR-3/CNR-4 rather than added to this compatibility contribution.

### CNR-3 Provision an external SmolCloud runtime with stable ownership

Status: DONE (2026-10-27)

- Type: Feature
- Priority: High
- Estimate: 3 points (confidence 80 percent)
- Labels: Type: Feature, Topic: External runtime
- Parent: CNR-1
- Blocked by: CNR-2
- Blocks: CNR-5
- Related: none
- Owner role: Harness provider contribution owner
- Requirements: CR-03, CR-06, CR-15; applicable AC-03 and AC-04

#### Context

The existing SmolCloud provider uses queue derived names, Worker bootstrap environment and create/adopt helpers. Its recovered start can resume a paused machine.

#### Problem

External execution must not inherit Worker credentials or adopt a conflicting legacy, changed or restoration dependent resource.

#### Scope

Use the existing provider `Start` with the selected native process configuration. Reuse creation, adoption and cleanup where ownership, stable identity, configuration and network checks remain enforced. Add only the provider configuration changes required for that behavior. Keep unchanged configuration requests compatible.

#### Out of scope

Other provider implementations, a new reconciliation framework, snapshot recovery and live cloud qualification are excluded.

#### Acceptance criteria

- [x] Fake HTTP request tests show native process configuration uses existing `Start` and omits `TEMPORAL_TASK_QUEUE` and Worker/Namespace credential bootstrap. Missing, unknown or unsupported selected configuration and forbidden restoration refuse before allocation, including direct provider calls. Provider credentials remain on the outside Activity Worker. Unchanged configuration requests retain existing behavior. Source: M1 plan and H3.
- [x] Creation/adoption binds harness ownership, stable identity and selected nonsecret image/configuration. Tests inspect exact requests across retries and reject incompatible resources. Reuse existing naming and metadata where sufficient; a separate domain or identity field requires demonstrated need. Source: M1 plan and H3/T1.
- [x] A simulated lost create reply followed by a retry returns the original matching external resource. Same name legacy resources, changed image/configuration, wrong network policy and multiple matches are refused without modifying or deleting conflicting resources. Source: M1 plan and H3/T1.
- [x] An unexpectedly paused external resource refuses rather than using the legacy resume helper. Tests also prove owned creation failure cleanup and retained legacy adoption behavior. Source: M1 plan and H3.
- [x] All acceptance tests use a fake provider endpoint. The contribution labels the live example path as unqualified until a separately authorized live check runs. Source: M1 plan.

#### Dependencies and blockers

CNR-2 proves the existing start contract and stable retry inputs. This ticket supplies concrete configuration and provider admission; it cannot verify controller idle options absent from provider input. CNR-4 owns actual initialization/lifecycle options. Native feature acceptance waits for both and the demo.

#### Source evidence

[M1 provider contract](../plan.md#first-actual-provider-and-example); [H3 and T1](../ticket-evidence.md#inspected-sources).

[BD-11](../decisions.md#decision-and-design-register) records the `int32` bound for CPU and memory values.

**Current implementation acceptance (2026-10-28):** [Combined commit `28e521cc7b067c2902e38442386fd131ec6667a0`](https://github.com/temporal-community/sandbox-orchestration-harness/commit/28e521cc7b067c2902e38442386fd131ec6667a0), base `24f09129335f8057750f09f84a45b9c76c99d9c1`, retains one commit in [draft PR #7](https://github.com/temporal-community/sandbox-orchestration-harness/pull/7). Fresh full contract, mutation and activated structural invariant reviews pass. Mutation review found two disk validation test gaps; three new zero/negative/overflow assertions now detect both weakened guards. Final disposition: 147 of 152 Go/provider/public faults killed, three equivalent, one unreachable and one invalid mutation; eight additional CI guard faults killed, with no relevant survivor. Eleven compiler negative probes and exact baseline wire comparisons pass. The lead exact-commit rerun passes 111 results, with only live cloud and fixture capture skipped, plus vet and all example builds. Both retained histories and four fresh histories replay. [Hosted PR SDK tests](https://github.com/temporal-community/sandbox-orchestration-harness/actions/runs/40733050664), [push SDK tests](https://github.com/temporal-community/sandbox-orchestration-harness/actions/runs/40733041473), [CodeQL Go analysis](https://github.com/temporal-community/sandbox-orchestration-harness/actions/runs/40733043794/job/122974175082) and the CodeQL check pass on this revision. The GitHub hosted runner uses a local headless Temporal CLI server, fake HTTP and local subprocesses; no AWS resources or Docker are needed. Maintainer acceptance remains separate. CNR-4, the generic demo and full M1 acceptance remain open.

**Earlier implementation acceptance:** [Combined commit `2a6c1db1bdc2d16ae34da428ca8a8cfaed6b21a7`](https://github.com/temporal-community/sandbox-orchestration-harness/commit/2a6c1db1bdc2d16ae34da428ca8a8cfaed6b21a7), base `24f09129335f8057750f09f84a45b9c76c99d9c1`, in [existing draft PR #7](https://github.com/temporal-community/sandbox-orchestration-harness/pull/7). This includes CNR-2 compatibility and CNR-3 provider behavior in one commit. Maintainer acceptance remains separate.

- Configuration and request proof: `TestNativeProcessConfigurationAdmission`, `TestSmolCloudNativeDirectActivityAdmission` and `TestSmolCloudNativeExistingActivityRetry` exercise `workload=native-process` through existing interfaces. Native CPU/memory values must fit the API int32 wire domain; legacy and disk parsing retain their existing host integer domain. Requests contain no Worker/Namespace bootstrap or provider credential in guest data. Native restoration refuses before HTTP.
- Binding and retry proof: `TestNativeProcessRequestAndLostCreateReply` and `TestNativeProcessAdoptionRefusals` cover byte-identical retries, original resource adoption, exact name/ownership/configuration/network checks and untouched conflicts. The existing name and ownership label remain; one digest label binds the full queue and admitted nonsecret configuration. Exact digest assertions cover image/resources/allowlists and order-only equivalence.
- Failure proof: `TestNativeProcessOwnedCreateCleanup`, `TestNativeProcessCreateRequiresIdentity` and `TestNativeProcessPausedDuringReadiness` cover partial decode with a known ID, missing-ID refusal, owned failure cleanup and paused refusal at both adoption observations. Legacy adoption/resume tests pass. Cleanup observations prove the tested DELETE requests, not universal process death.
- Combined verification: fresh independent contract, mutation and activated structural invariant reviews pass. The final matrix detects 132 faults, with three independently confirmed equivalent guards and no unresolved relevant survivor. Eleven compiler probes reject invalid interface/record contracts. All eleven materialized public wire records exactly match compiled upstream output and fixed literals.
- Lead exact-commit checks pass: `GOWORK=off HARNESS_LOCAL_TEST=1 SMOL_CLOUD_LIVE=0 go test -json -count=1 ./...` executes 41 top level tests and 108 passing results including subtests, with only live cloud execution and fixture regeneration skipped. Both retained histories and four fresh histories replay. Vet, all twelve Makefile binary targets and the database build pass with the documented temporary local SDK replacement. Focused race detection passes 17 top level tests and 84 results, with no skips or race reports.

Local CNR-2/CNR-3 acceptance is complete. [CodeQL Go analysis](https://github.com/temporal-community/sandbox-orchestration-harness/actions/runs/40616745937/job/122580906082) and the CodeQL check pass for exact pushed revision `2a6c1db1bdc2d16ae34da428ca8a8cfaed6b21a7`, completed on 2026-10-28 UTC. CNR-4 actual initial idle/snapshot choices, later operations and attachments, the generic demo and full M1 acceptance remain OPEN. Live SmolCloud execution, account capacity, recovery, attestation and confidential deployment remain unqualified. No cloud allocation or paid inference occurred.

#### Open questions

If the actual provider API cannot enforce the selected ownership/configuration binding, record the limit and return to scoped design review. Do not weaken adoption checks to complete the example.

### CNR-4 Preserve external policy across commands and attached references

Status: DONE (2026-11-18, corrected initialization ownership and fresh whole-contribution verification; maintainer acceptance pending)

- Type: Feature
- Priority: High
- Estimate: 3 points (confidence 80 percent)
- Labels: Type: Feature, Topic: External runtime
- Parent: CNR-1
- Blocked by: CNR-2
- Blocks: CNR-5
- Related: none
- Owner role: Harness lifecycle contribution owner
- Requirements: CR-06, CR-15; applicable AC-03 and AC-04

#### Context

The existing SDK distinguishes owned and attached sandbox references. M1 uses provider configuration and existing lifecycle boundaries to preserve the selected native process policy.

#### Problem

Creation checks alone do not prevent later commands, attachments or direct Activity calls from bypassing the admitted profile.

#### Scope

Enforce actual initial idle/snapshot policy, selected configuration, allowed operations and resource binding at existing SDK/controller, receiving Activity and provider boundaries. Add checks only where existing enforcement is insufficient. Preserve one resource owner and unchanged configuration behavior; do not add a parallel external operation family merely for placement.

#### Out of scope

New snapshot, suspend/resume or restore support, replacement recovery and runtime idle detection are excluded.

#### Acceptance criteria

- [x] Tests prove an attached reference routes to the same resource without resetting its configuration or acquiring ownership. Closing an attachment does not delete compute. Source: M1 plan and H2.
- [x] SDK/controller initialization rejects omitted/default or unsupported idle policy and initial snapshot/restore for the selected fresh native configuration before allocation. Require actual `NoIdleTimeout`; a declaration in provider config alone does not prove the controller selected it. Direct receiving calls validate the configuration and identity information available there, without claiming to inspect absent controller fields. Source: M1 plan and H1/H2.
- [x] Unsupported execute, snapshot, restore, suspend/resume and idle requests produce zero forbidden provider calls after startup and through attachments. Source: M1 plan and H1/H2.
- [x] Direct receiving Activity/provider tests reject missing or conflicting required configuration/resource binding independently of the SDK route. Retries retain the selected context. Existing input signatures remain compatible. Source: M1 plan and H2/T1.
- [x] Owner completion/cancellation tests exercise the existing stop/cleanup path; attached callers cannot become a second cleanup owner. Report provider teardown observations accurately rather than claiming proof of all process death. Source: M1 plan and H2/G1.
- [x] Legacy command and attachment tests retain their original routing without a new capability prerequisite. Source: M1 plan and H2/T2.

#### Customer decisions

Coverage: complete

#### Dependencies and blockers

CNR-2 supplies the revised configuration and identity contract through existing inputs. This work can proceed beside CNR-3 after that revision is reviewed and verified.

#### Source evidence

[M1 contract](../plan.md#source-contract-and-extension-surface); [H1, H2, T1, T2 and G1](../ticket-evidence.md#inspected-sources).

- Customer decision review: zero. Reviewed: all CNR-4 sections, active criteria, dependencies, prior implementation decisions, source evidence and current local verification. No held update file exists. Result: this generic controller correction requires engineering work, not a customer action, fact, choice or approval. Maintainer acceptance and publication remain separate.
- Current qualification: revision `549bd175eeba39f33fe606c49a91cd5f67c55f74` closes the inherited overlapping initialization failure. New controllers claim the pinned SDK's native Workflow mutex before policy changes or awaited Start work; validator and receiving handler reject competing initialization. Same Update ID retries preserve the original result. `TestLocalConcurrentInitializationOwnership/{same,changed,invalid,legacy}/{stop,cancel}` proves all eight held-create interleavings retain original configuration/status, one create, one matching Stop/DELETE and replay. The direct handler test and isolated validator bypass prove independent receiving enforcement; removing the claim in the isolated copy fails the regression. Three fresh roles and the final lead suite, gate, vet and builds accept the corrected 101 file source map in the [combined M1 acceptance record](../evidence/m1-implementation-acceptance.md). The version marker preserves old histories; older pending initialization must finish before deployment and marked active controllers require a verified rollback transition. The operator authorizes this correction, whole verification and publication on 2026-11-18. Maintainer acceptance remains separate.

#### Open questions

Record any existing attachment or cancellation path that cannot preserve the selected profile before changing it. Such a source impact requires a bounded correction, not a second lifecycle controller.

**Implementation decision, 2026-11-17:** The operator authorizes completion after review against merged main `d8a7d5b8b3782e26ff803678b097eed548c8c8ac`. Preserve version 1 references and explicit attachment `RequestStop` delegation to the same owner. Ordinary attachment completion/cancellation must not create a cleanup owner or delete compute. The earlier version 2 refusal is an unadopted candidate, not an acceptance requirement. Fresh SmolCloud status carries optional typed resource context, with provider/configuration/instance checks at the receiving boundaries and metadata reconciliation before supported command/stop effects. Legacy status omits that context. A caller that erases every profile marker cannot be distinguished from a legacy caller using local input alone; labels and references are trusted reconciliation data, not authentication.

**Cancellation and activation:** The same owner uses the pinned SDK's `WithWaitForCancellation` and disconnected `AllHandlersFinished` drain to retain a terminal initialization result before cleanup. The `wait-for-fresh-start-cancellation` `GetVersion` gate preserves historical command selection. Tests distinguish successful initialization, failed initialization, recovered adoption and lost replies. Cleanup uses only a known matching instance. Stricter fresh status validation requires compatible receiving Workers before new starts. Existing fresh executions with unbound status must finish on compatible code or receive a separately verified transition; this ticket authorizes no automatic migration. Baseline/default executions retain their existing path. The contribution records the cutover and rollback prerequisites because old Workers can ignore new context and unknown start results can prevent cleanup.

Merged [PR #7](https://github.com/temporal-community/sandbox-orchestration-harness/pull/7), final head `26df2abc0ad3eb86efbb6259a70a3cfab1e79005`, supplies independent bootstrap/lifecycle/branchability settings and applicable initial/later fresh lifecycle admission. Fresh lifecycle permits supported commands. The CNR-4 contribution builds on merged main rather than the historical candidate `0cff218` and preserves those settings and the original fixture bytes.

**Local acceptance, 2026-11-17:** Implementation revision `133786bb5e805495532db85ef08bc2075e2bf005` completes this ticket on merged baseline `d8a7d5b8b3782e26ff803678b097eed548c8c8ac`. `TestLocalAttachmentOwnershipHistory` proves all eight fresh/legacy owner shutdown routes and harmless ordinary attachment completion/cancellation. Initial admission and later operation matrices prove zero forbidden calls. `TestResourceBindingLocalContract`, direct receiving Activity/provider matrices and lost-reply adoption tests prove independent binding checks and retention. `TestLocalPendingStartCancellationCleanup` proves late success cleanup and canceled/uncanceled initialization failure. Retained legacy and both fresh controller histories replay; all ten merged baseline fixtures remain byte identical. Version 1 references, legacy wire data, registrations, default configuration and supported commands retain their contracts.

Fresh contract, mutation and activated structural reviews accept all six criteria. The lead rerun passes 287 test/subtest results with three expected live/capture skips, the exact automatic CI required-test script, vet, all 12 Makefile example targets and the database example build. The single commit passes the same checks in a separate checkout. Mutation evidence records 97 unique current killed faults, four equivalent clauses and five invalid candidates retained against unchanged production sources; no relevant survivor remains. Retained acceptance report SHA256: `bc8c909b00fc4ad765caf0e7a925746e7c900823c70dafffbd44dd7c05560f24`. This is local acceptance, not maintainer acceptance or full M1 acceptance.

[Draft PR #13](https://github.com/temporal-community/sandbox-orchestration-harness/pull/13) contains the exact implementation revision above. Its [PR SDK tests](https://github.com/temporal-community/sandbox-orchestration-harness/actions/runs/44189142854), [push SDK tests](https://github.com/temporal-community/sandbox-orchestration-harness/actions/runs/44189088202), [Go analysis](https://github.com/temporal-community/sandbox-orchestration-harness/actions/runs/44189133829/job/134413533800) and [CodeQL](https://github.com/temporal-community/sandbox-orchestration-harness/runs/134415565869) pass for that revision. The PR retains the existing reviewer and draft status. Merged PR #7 remains unchanged.

Activation is limited to fresh native executions. Earlier experimental native histories require a separate activation/versioning decision before migration. Retained baseline histories must replay unchanged. No migration or live provider run is authorized by this reconciliation. CNR-5 owns the generic process demo and CNR-6 owns full M1 acceptance.

### CNR-5 Demonstrate a controller owned external process

Status: DONE (2026-11-18, local implementation acceptance; contribution revision 549bd175eeba39f33fe606c49a91cd5f67c55f74)

- Type: Task
- Priority: High
- Estimate: 2 points (confidence 85 percent)
- Labels: Type: Task, Topic: External runtime
- Parent: CNR-1
- Blocked by: CNR-3, CNR-4
- Blocks: CNR-6
- Related: none
- Owner role: Harness example contribution owner
- Requirements: CR-03, CR-06, CR-15; applicable AC-03 and AC-04

#### Context

The first useful demonstration is a generic native process managed by the existing harness. It does not require the Claude integration.

#### Problem

Reviewers need a reproducible example of external placement, capability refusal and compute ownership before evaluating the later native agent composition.

#### Scope

Add one harmless bounded process example through provider configuration and existing `Start`, a fake provider conformance test and instructions for an optional real SmolCloud run. Use explicit `NoIdleTimeout`; no separate execution mode is required.

#### Out of scope

No LLM call, model credential, new cloud allocation, live run, skill execution, host recovery or confidentiality claim is part of this ticket's default proof.

#### Acceptance criteria

- [x] A documented local fake provider command runs the example and proves one resource owner, process completion and explicit cleanup. A second run exercises cancellation and cleanup. Source: M1 plan and H2/G1.
- [x] Captured launch configuration contains no in-resource Temporal Worker bootstrap or Namespace credential. The real example's image entrypoint runs only the bounded native process. Source: M1 plan and H1/H3.
- [x] A deliberately unsupported profile fails before allocation and produces an actionable error. The example does not treat command completion as autonomous runtime idleness. Source: M1 plan.
- [x] A reviewer can find exact prerequisites, commands, expected results and limits without private records. Optional real execution is labeled separately and not reported as tested by fake conformance. Source: M1 plan.
- [x] The example and collaboration handoff identify the next early M2 skill demo without making that later integration an M1 acceptance dependency. Source: M1/M2 plan.

#### Customer decisions

Coverage: complete

#### Dependencies and blockers

CNR-3 and CNR-4 supply actual provider behavior and lifecycle enforcement. Fake conformance is the default acceptance route; no live provider credential is required for it.

#### Source evidence

[M1 example and acceptance contract](../plan.md#focused-acceptance-and-compatibility); [collaboration handoff](../collaboration-handoff.md); [H1, H2, H3 and G1](../ticket-evidence.md#inspected-sources).

- Customer decision review: zero. Reviewed: all CNR-5 sections, CNR-3/CNR-4 dependencies, CNR-6 boundary, M1 plan, collaboration handoff and available local ticket history. No held update file exists. Result: this generic local example requires no customer action, fact, choice or approval. Live execution and later integration retain separate authorization.
- Reviewed implementation: branch `external-runtime-demo`, revision `549bd175eeba39f33fe606c49a91cd5f67c55f74`, based on verified PR #13 head `133786bb5e805495532db85ef08bc2075e2bf005`. The corrected combined 101 file inventory has SHA256 `3808089139e9dc1cd7de6f0ec8265306467b8870a044cfebf4ccef7c56f1320d`, computed over compact sorted JSON from repository relative paths to file SHA256 values. CNR-4 owns the controller correction; dependency files and existing fixtures match the base. The combined acceptance record owns current verification and publication qualification.
- Completion and cancellation: `sdk/external_process_example_test.go`, SHA256 `e733779d77430a7974b820894f0a3f4a7ce619f32e0aa7a1e7534d40ad34f6a3`, supplies `TestLocalExternalProcessExample/completion` and `/cancellation`. Each runs the real SmolCloud provider against a loopback fake API, observes one controller/create/DELETE/Stop Activity and confirms local process reaping before fallback cleanup. Cancellation interrupts a running process. An isolated DELETE acknowledgement without process stop fails with `cancellation did not interrupt the process`.
- Launch and refusal: the same test captures `env:{}`, rejects Temporal bootstrap keys and synthetic Namespace/provider credentials in launch data, and uses explicit `NoIdleTimeout`. `/unsupported-profile` rejects fresh lifecycle with branching using `fresh lifecycle requires branchable=false`, with zero HTTP requests and no process. Controller history contains no idle timer. `examples/external-process/Dockerfile`, SHA256 `b70d8025adcad6ddf04af66e26552c640eb20fe65ee8ff8b4d836451b296b525`, contains the same bounded `printf process-output; exec sleep 2` entrypoint.
- Reproduction: `examples/external-process/README.md`, SHA256 `f551262a1cb1d31a76f938f57e999c5a8dc73c496dbdfa0b7183c2126fba98d0`, contains prerequisites, the local server command, three exact case commands, expected results, cleanup and optional real execution limits. Each documented case command passes independently. The example and collaboration handoff identify the separate early M2 local Docker/Connector skill demo.
- Final lead checks: from `sdk`, `GOWORK=off HARNESS_LOCAL_TEST=1 SMOL_CLOUD_LIVE=0 HARNESS_HISTORY_CAPTURE= go test -json -count=1 -timeout=5m ./...` passes 301 test/subtest results with three expected live/capture skips. The exact CI required-name gate and `go vet ./...` pass. All 12 `make bins` targets and the database example build pass with an isolated workspace using the same local SDK. Focused race checks pass. CI guard counterexamples reject absent, skipped and wrong-package demo and initialization results. The canonical per-commit verifier repeats the full suite, gate, vet and builds on the actual committed checkout.
- Fresh verification: independent contract, adversarial containment and activated structural invariant reviews accept all five example criteria and the corrected whole M1 implementation with no unresolved material finding. Current report identities and all 26 criteria are retained in the [combined M1 acceptance record](../evidence/m1-implementation-acceptance.md). Five compiler probes reject invalid record/interface contracts. Verification uses local Temporal, fake HTTP and local processes only. Real image boot, provider readiness/observation and cloud teardown remain unqualified. CNR-6 completes local M1 acceptance; maintainer approval is separate.

#### Open questions

None for local acceptance. Optional real execution requires separate authorization and qualification of short entrypoint readiness, image publication and a provider supported process observer. No model access is required by this example.

### CNR-6 Verify M1 and prepare the upstream review handoff

Status: DONE (2026-11-18, whole M1 implementation and local review package accepted; maintainer acceptance pending)

- Type: Task
- Priority: High
- Estimate: 2 points (confidence 85 percent)
- Labels: Type: Task, Topic: External runtime
- Parent: CNR-1
- Blocked by: CNR-5
- Blocks: CNR-1
- Related: none
- Owner role: Contribution owner with independent implementation reviewers
- Requirements: CR-03, CR-06, CR-15; applicable AC-03 and AC-04

#### Context

The revised M1 mechanism requires scoped design review before implementation. Implementation acceptance then needs evidence from the actual changed harness revision; earlier mode/interface verification does not satisfy this gate.

#### Problem

A design PASS, source links or fake example alone cannot prove complete compatibility, admission enforcement and ownership behavior.

#### Scope

Run scoped `verify-change` after implementation, including the target repository's required checks. Prepare a concise draft contribution description, example instructions and collaboration handoff. Keep fixes with the behavior they repair.

#### Out of scope

Publishing a PR or message, paid execution, live provider qualification and upstream merge are separate actions. No M2 through M4 guarantee is accepted here.

#### Acceptance criteria

- [x] Independent implementation verification maps every CNR-2 through CNR-5 criterion to exact revision evidence and reports no unresolved material defect for the selected M1 scope. Source: M1 verification contract.
- [x] A lead rerun confirms applicable target CI commands, legacy history replay, fresh external histories, fake provider retry/adoption cases, direct Activity refusal, attachment isolation and completion/cancellation cleanup. Source: M1 plan, T1/T2 and G1.
- [x] A clean example run and negative configuration run reproduce CNR-5 results. Retain actionable evidence without requiring private raw diagnostics to review the contribution. Source: M1 plan.
- [x] The draft upstream description states the problem, additive behavior, compatibility, proof and limits. The collaboration handoff separates harness ownership from the native SDK/Transport work and lists unresolved joint seam questions. Source: M1 plan.
- [x] The M1 exit record distinguishes implementation acceptance, pending maintainer acceptance and unexecuted live checks. It identifies the bounded early M2 design/ticket handoff instead of expanding all later work. Source: M1/M2 plan.

#### Customer decisions

Coverage: complete

#### Dependencies and blockers

CNR-5 transitively requires every other M1 work ticket. Maintainer review gates upstream merge, not preparation of this local review package.

#### Source evidence

[M1 acceptance and compatibility](../plan.md#focused-acceptance-and-compatibility); [M1 design review](../verification-report.md); [T1, T2 and G1](../ticket-evidence.md#inspected-sources).

- Customer decision review: zero. Reviewed: all CNR-6 sections, active CNR-2 through CNR-5 criteria, dependencies, current review reports and the local plan/handoff. No held update file exists. Result: the generic local implementation review needs no customer action, fact, choice or approval. Operator authority for a controller correction, publication and maintainer acceptance remain separate.

The [current M1 implementation acceptance record](../evidence/m1-implementation-acceptance.md) binds revision `549bd175eeba39f33fe606c49a91cd5f67c55f74` and the 101 file source map to all 21 active implementation criteria and five package criteria. Three fresh roles accept the whole implementation; the lead independently repeats 301 passing results, three expected skips, the CI event gate, vet and all example builds. Three documented example commands pass independently. [PR #14](https://github.com/temporal-community/sandbox-orchestration-harness/pull/14) publishes the correction and demo together on PR #13. Its description states behavior, compatibility, proof and limits. The collaboration handoff states compute/process ownership and unresolved early M2 seams. Both [PR SDK CI](https://github.com/temporal-community/sandbox-orchestration-harness/actions/runs/44370319316) and [push SDK CI](https://github.com/temporal-community/sandbox-orchestration-harness/actions/runs/44370261128) pass on that exact head. Local M1 acceptance is complete; maintainer approval, upstream merge and live qualification remain separate.

#### Open questions

None for local acceptance. The operator authorizes correction, full verification and publication on 2026-11-18. Maintainer approval, upstream merge and unexecuted live qualification remain separate.
