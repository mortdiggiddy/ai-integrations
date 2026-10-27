# Later delivery milestones

### CNR-10 Run native skills inside the managed runtime

Status: OPEN

- Type: Epic
- Priority: Medium
- Estimate: none
- Labels: none
- Parent: none
- Blocked by: CNR-1
- Blocks: CNR-20
- Related: none
- Owner role: Runtime composition owner; native SDK integration maintainer consulted
- Requirements: M2; CR-01 through CR-07, CR-11 through CR-13; applicable AC-01, AC-02, AC-04, AC-08 and AC-09 at local scope

#### Context

M1 provides generic external placement. The [M2 plan](../plan.md#m2-native-supervisor-and-sealed-content-path) places the native SDK and CLI inside a managed runtime with a defined supervisor boundary.

#### Problem

External compute placement does not prove native skill execution, package placement, content handling or correct separation of connection close and compute deletion.

#### Scope

Retain the full M2 outcome as a milestone. After M1, detail and review the smallest native skill demo slice first, using the approved synthetic local Docker profile. Keep later content boundary work visible until full M2 acceptance.

#### Out of scope

This container authorizes no implementation by itself. Host loss recovery belongs to CNR-20 and attested deployment belongs to CNR-30. Ordinary remote Transport interoperability remains optional and is not the confidential architecture by default.

#### Acceptance criteria

- [ ] Before implementation, the bounded demo design records the cross language/service binding, exact SDK/CLI/integration pins, readiness meaning, package placement and shutdown ownership. Relevant M2 decision gates receive scoped review. Source: M2 plan and BD-06/BD-07.
- [ ] The first demo runs one representative native skill with supporting files in a clean local runtime. Native request/result evidence proves actual loading and helper execution; missing or mismatched packages refuse before execution. Its report states that this trusted local demo is only an M2 subset. Source: M2 plan and U1.
- [ ] Reconnect retains resource identity; connection close, CLI shutdown and compute deletion follow their separate contracts. No Temporal Worker or Namespace credential is bootstrapped inside the runtime. Source: M2 plan and H2/U1.
- [ ] Full M2 acceptance additionally proves sealed operations, caller/job/generation binding and selected acknowledgment meanings. Synthetic canary checks inspect outside payloads, history, failures, logs, telemetry and observers for content exposure and cross job access. Source: M2 plan and runtime protocol.
- [ ] Scoped `verify-change` covers the implemented M2 slice and states which full M2 criteria remain open. Ordinary containers do not establish host operator confidentiality. Source: M2 plan.
- [ ] Before full M2/M4 custom confinement implementation, a bounded comparison records reuse or rejection of the relevant native sandbox-runtime, nono and OpenShell components, exact pins and lifecycle/trust fit under BD-07. This does not block the early trusted local skill demo. Source: M2 plan and supplemental sandbox research.
- [ ] Full M2 confinement tests prove the admitted profile rejects native/child read bypass, unsafe startup/configuration inputs, inherited control descriptors/sockets, direct egress bypass and permissive audit/override modes. Policy update tests state whether existing connections require restart or explicit closure. Source: CR-01/CR-11/CR-12 and supplemental sandbox research.

#### Dependencies and blockers

CNR-1 supplies the generic lifecycle seam. The native SDK integration maintainer must confirm the joint seam before a shared demo is represented as agreed. Local trusted profile approval carries forward; exact M2 mechanisms still require review.

#### Source evidence

[M2 plan](../plan.md#m2-native-supervisor-and-sealed-content-path); [decision register](../decisions.md); [runtime protocol](../runtime-protocol.md); [U1 and H2](../ticket-evidence.md#inspected-sources); [supplemental sandbox sources and proof mapping](../ticket-evidence.md#supplemental-later-stage-evidence).

#### Open questions

Select the smallest Go harness to Python runtime binding without assuming a Python harness SDK or new Nexus service. Confirm who prepares the demo adapter and exact package delivery path. Do not estimate this entire milestone before decomposition.

### CNR-20 Restore accepted native state after runtime loss

Status: OPEN

- Type: Epic
- Priority: Medium
- Estimate: none
- Labels: none
- Parent: none
- Blocked by: CNR-10
- Blocks: CNR-30
- Related: none
- Owner role: Recovery composition owner
- Requirements: M3; CR-06 through CR-10, CR-16; AC-04 through AC-07 and applicable AC-11

#### Context

The [M3 plan](../plan.md#m3-coherent-replacement-recovery) requires recovery of one accepted native session/workspace state without the original host or disk.

#### Problem

Best effort transcript mirroring, surviving files or a watcher retry do not prove coherent replacement recovery or safe treatment of uncertain effects.

#### Scope

Retain accepted state capture, independent authority, definitive outcomes, selected state restoration and generation takeover as one milestone. Detail its implementation only after the native mechanism is reviewed against exact supported behavior.

#### Out of scope

This container does not approve a recovery algorithm, waive positive child/parallel requirements, permit arbitrary Bash replay or qualify confidential deployment.

#### Acceptance criteria

- [ ] Reviewed native mechanisms satisfy BD-01, BD-02, BD-04 and applicable BD-07/BD-09 gates before dependent code is treated as implementation ready. Per-tool projection uses real supported schema and consumption behavior. Source: M3 plan and native recovery protocol.
- [ ] A fault test destroys the original runtime and disables its host/disk access. A replacement restores the selected accepted session, workspace and required sidecars, with matching identities and controlled effect counters. Source: M3 plan.
- [ ] Lost replies, stale producers, missing/corrupt accepted bytes and mutation before result acceptance have explicit tests. Unknown outcomes stop without repeating uncertain actions or inventing definitive output. Source: M3 plan and native recovery protocol.
- [ ] Positive child and parallel recovery requirements receive proof or an explicit owner disposition before broader recovery is claimed. Parking an active-child crash is not positive recovery. Source: BD-08 and the retained obligation map.
- [ ] Scoped implementation verification reports the supported workload and recovery limits and preserves required state/keys across rollback and retention. Source: M3 plan and BD-09.
- [ ] The recovery mechanism decision records evaluation or justified rejection of portable RAM/disk capture against the native active-child gap. If selected, admitted fault tests cover compatible replacement without original host/disk, accepted identity, an active child, lost external response, stale generations and credential/control rebinding; restore success alone is insufficient. Source: M3 plan, BD-01/BD-04/BD-08 and supplemental sandbox research.

#### Dependencies and blockers

CNR-10 supplies the native composition. Exact active-child resume remains unresolved. This gap blocks its guarantee, not M1 delivery or the first bounded native skill demo.

#### Source evidence

[M3 plan](../plan.md#m3-coherent-replacement-recovery); [native recovery protocol](../native-recovery-protocol.md); [decision register](../decisions.md); [obligation map](../obligation-map.md); [supplemental checkpoint source and proof mapping](../ticket-evidence.md#supplemental-later-stage-evidence).

#### Open questions

Resolve the supported active-child recovery mechanism and coherent writer boundary before decomposing affected implementation work. No full milestone estimate is assigned.

### CNR-30 Qualify an attested confidential deployment

Status: OPEN

- Type: Epic
- Priority: Medium
- Estimate: none
- Labels: none
- Parent: none
- Blocked by: CNR-20
- Blocks: none
- Related: none
- Owner role: Deployment and security owners with job policy owners
- Requirements: M4; all applicable CR and AC rows, including CR-17 and CR-18

#### Context

The [M4 plan](../plan.md#m4-confidential-activation-and-bounded-operational-qualification) retains AWS EC2 NitroTPM, a mutually approved Attestable AMI and independently administered KMS policies. The cloud provider remains trusted.

#### Problem

Local execution, encrypted payloads and a capability flag do not establish mutual confidentiality, attested key release or bounded production operation.

#### Scope

Retain the selected image and key binding, administration and command isolation, authorized output, protected restoration, preventive spending, telemetry, retention and version transition qualification. Include broader service exit obligations from the plan.

#### Out of scope

No cloud allocation, paid inference, production activation, provider substitution or business report field policy is approved by this milestone container.

#### Acceptance criteria

- [ ] Deployment and job owners approve exact image measurements, independent key policies, recipient/model disclosure and real job release policy before private input or key admission. Source: M4 plan and BD-05/BD-06.
- [ ] Qualification denies keys for wrong image/job/stale identity and proves the selected administration, tool confinement, authorized output and restoration boundaries. State cloud provider and model provider trust explicitly. Source: M4 plan and runtime protocol.
- [ ] Preventive spending has actual admission proof; retention preserves all live, parked, reset and replay references. Cleanup and version/reset/Continue-As-New tests use the supported deployment boundary. Source: M4 plan and BD-03/BD-09.
- [ ] Broader native feature, processing and second harness obligations are proved or explicitly retired by their owner, with the obligation map updated. They are not silently dropped from the service exit. Source: broader service exit and BD-08.
- [ ] Final implementation and deployment evidence supports only the selected profile and declared guarantee. Failed attestation, unauthorized disclosure or accepted state loss keeps that profile disabled. Source: M4 plan.
- [ ] The reviewed deployment data flow identifies every protected plaintext processor, including credential/TLS brokers, and proves its placement inside the approved content boundary. Negative checks cover selected backend enforcement, unsafe mode fallback and content in diagnostics, telemetry and checkpoint caches. Source: CR-04/CR-05/CR-11/CR-13, M4 plan and supplemental sandbox research.

#### Dependencies and blockers

CNR-20 supplies qualified recovery. Actual final policy and deployment bindings remain gates. Narrow adapter preparation can be planned earlier only where it does not assume an unresolved decision; full milestone acceptance still requires the preceding outcomes.

#### Source evidence

[M4 plan and broader service exit](../plan.md#m4-confidential-activation-and-bounded-operational-qualification); [decision register](../decisions.md); [runtime protocol](../runtime-protocol.md); [specification](../spec.md); [supplemental trust and confinement evidence](../ticket-evidence.md#supplemental-later-stage-evidence).

#### Open questions

Select exact qualified deployment bindings and actual job policies at their activation gates. No full milestone estimate or activation date is assigned.
