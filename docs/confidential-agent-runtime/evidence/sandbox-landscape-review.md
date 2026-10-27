# Sandbox landscape review and phase implications

Date: 2026-10-26. Status: SOURCE RESEARCH AND RECOMMENDATIONS. This review reads the complete rendered [MXC discussion](https://news.ycombinator.com/item?id=50016489), follows the relevant implementation links and compares primary documentation with the active project. It does not change the specification, approve a dependency or qualify a runtime. No third party code was cloned, installed, built or executed. No provider, model, checkpoint or confinement test ran.

## Result

Keep M1 and the first joint demo on their current path. The discussion supplies useful implementation candidates and concrete negative tests for later stages. It supplies no demonstrated replacement for Temporal ownership, accepted native recovery or the selected attested deployment.

The two findings that merit focused follow-up are a documented portable RAM/disk checkpoint route in SmolVM and nono's draft split supervisor protocol. The former could preserve native in-memory execution that transcript restoration loses. The latter addresses authority and credential exposure after guest compromise. These are candidates for a bounded M3 experiment and M2/M4 boundary review, respectively, not reasons to expand the first harness contribution.

## Research scope and limits

The discussion was used for discovery, not product authority. Relevant branches cover containment backends, network enforcement, permission changes, dependency and testing quality, secret handling, VM alternatives and native runtime compatibility. Social commentary, line counts, promotional claims and unsupported exploit allegations do not establish acceptance evidence. No claimed sandbox escape was independently reproduced or adjudicated here.

Primary reads covered MXC's README, current policy schema, lifecycle/API reference, Seatbelt backend, denial diagnostics and telemetry policy; SmolVM's security, mediated egress, credential, checkpoint and limitation documents; Anthropic sandbox-runtime's documented enforcement and defaults; OpenShell's current architecture/policy documentation and its older architecture RFC; and nono's README and draft NEP-0007. Microsandbox, runcontain and sandbox-run received narrower source/document triage. WebAssembly and capability OS suggestions received compatibility triage only, not implementation evaluation.

Atlas discovery used the approved wrapper and returned no exact MXC or SmolVM implementation. Related internal sandbox discussions added no stronger authority than the inspected public sources and existing project requirements. No private discussion or individual attribution is imported into this record.

Repository heads below are inspected source identities, not a claim that their contents are all included in the latest release. Release tags are maturity signals only. No dependency is admitted from a moving branch.

## Prior art

| Candidate and inspected source | Maturity evidence at inspection | Fit and decision |
|---|---|---|
| [MXC](https://github.com/microsoft/mxc/tree/ad54c69452147bd4ca15d027388ad6074903dbff) | MIT; current source commit dated October 26; release v1.0.1 dated October 17; repository contains cross platform build and backend validation workflows, SDK tests and backend negative tests. Tests were not run. | Reference for policy validation and capability reporting; possible later confinement adapter. It is not the selected Temporal lifecycle controller. Its documented Rust, .NET and Node SDK surfaces are not direct Go/Python drop-ins. |
| [Anthropic sandbox-runtime](https://github.com/anthropics/sandbox-runtime/tree/98a4016d27609ed34dd1fb43d23ed6efb6eeeb77) | Apache-2.0; source commit dated October 25; release v0.0.81 dated October 20. | First confinement candidate to examine for native Claude composition, because the project should reuse native enforcement where adequate. Verify exact CLI behavior and all required tool paths; do not assume every requirement is already covered. |
| [SmolVM](https://github.com/smol-machines/smolvm/tree/5521d6bc80dd15161c77b51a28c5a03cc0c2ce39) | Apache-2.0; source commit dated October 26; release v1.32.3 dated October 26; documented fault/limitation cases and an egress test script. | Reference and optional later checkpoint experiment. Local SmolVM and the harness's SmolCloud provider are distinct integration surfaces. M1 does not gain local VM checkpoint capability from a provider name. |
| [OpenShell](https://github.com/NVIDIA/OpenShell/tree/17eda52d454da602fb75416cbca89868102a6dae) | Apache-2.0; source commit dated October 26; release v0.1.5 dated October 20; current public architecture and policy documentation. | Strong supervisor and policy precedent. Evaluate a bounded reuse path before implementing equivalent machinery. Full platform adoption needs an ownership and trust analysis because its gateway already owns lifecycle. |
| [nono](https://github.com/nolabs-ai/nono/tree/11d9e6b8e522a87325134e5399cc458f11e5bba7) | Apache-2.0; source commit dated October 23; release v0.80.0 dated October 13. NEP-0007 is explicitly draft and reports a spike, not generally qualified integration. | Reference or evaluate for command confinement and protected authority. Do not classify the draft remote supervisor design as a shipped recovery guarantee. |
| [Microsandbox](https://github.com/superradcompany/microsandbox/tree/d07acf76e7234fac17dc8e941188731b037ecbbd) | Apache-2.0; source commit dated October 25; release v0.7.11 dated October 24. README explicitly labels the project beta. | Optional VM backend comparison; no demonstrated reason to add a second provider to M1. Performance and secret safety advertising are not qualification evidence. |
| [runcontain](https://github.com/runcontain/runcontain) and [sandbox-run](https://github.com/sandbox-utils/sandbox-run) | Narrow live README triage only; no immutable implementation or release qualification. Runcontain warns against relying on it for untrusted workloads yet. | Reject immediate adoption in this project. The former adds another VM wrapper; the latter requires a dedicated enforcement and dependency audit. Do not use the discussion's historical defect allegations as current proven findings. |

No candidate was selected solely because of language, vendor reputation, source size, download count or test coverage percentage.

## Findings that affect this project

### Backend capability means an enforced contract

MXC's [V1 API](https://github.com/microsoft/mxc/blob/ad54c69452147bd4ca15d027388ad6074903dbff/docs/api-reference/rust/v1/api.md) distinguishes backend discovery from request validation. Discovery is advisory; a reported backend need not have a V1 creation API. Validation does not guarantee later success on a changed host. Its [1.0 policy](https://github.com/microsoft/mxc/blob/ad54c69452147bd4ca15d027388ad6074903dbff/docs/containment-policy/1.0.0/policy.md) restricts persistent lifecycle to specific backends and excludes VM selections available elsewhere in the repository.

Project implication: preserve CR-15 and CNR-2/CNR-4 admission at entry and receiving Activities. For later confinement, bind capability claims to the exact platform, backend, kernel features, policy and version. Keep requested, validated and actually enforced states distinguishable. A generic `network: true` or a provider brand is insufficient. Do not add a large cross platform policy API to M1.

### Network reachability and credential permission are different authorities

The [MXC Seatbelt guide](https://github.com/microsoft/mxc/blob/ad54c69452147bd4ca15d027388ad6074903dbff/docs/backends/seatbelt/seatbelt-backend.md) rejects unsupported destination filters. Its proxy mode fences egress but relies on an external proxy for destination decisions. Anthropic's [runtime README](https://github.com/anthropics/sandbox-runtime/blob/98a4016d27609ed34dd1fb43d23ed6efb6eeeb77/README.md) describes proxy mediation and notes that reads are unrestricted unless configured. A shared OS primitive does not imply identical composed enforcement.

Project implication: later tests must try direct IP, IPv6, alternate DNS, shared destination IPs, proxy variable removal, loopback/control services and cloud metadata. Prove the selected rule semantics rather than inferring them from a DNS allow list. An allowed API endpoint can still accept an unauthorized operation or content disclosure. Endpoint reachability alone cannot replace CR-07/CR-12 authorization and release policy.

SmolVM's [mediated egress](https://github.com/smol-machines/smolvm/blob/5521d6bc80dd15161c77b51a28c5a03cc0c2ce39/docs/mediated-egress.md) denies failed decider connections and requires a fresh mediator binding on restore. Its [credential substitution](https://github.com/smol-machines/smolvm/blob/5521d6bc80dd15161c77b51a28c5a03cc0c2ce39/docs/credential-substitution.md) keeps values outside the guest and scopes injection separately from network access. These mechanisms are platform dependent and are not interchangeable modes.

For the confidential profile, any component inspecting protected plaintext must remain inside the approved trust boundary. Moving a TLS inspecting credential broker to an ordinary outside host would change that boundary even if the agent never sees the credential. Secret non-disclosure to job code is distinct from content non-disclosure to the operator.

### A second isolation boundary is needed inside allocated compute

SmolVM's [security model](https://github.com/smol-machines/smolvm/blob/5521d6bc80dd15161c77b51a28c5a03cc0c2ce39/docs/security-model.md) includes the host account, host OS and hypervisor in its trusted base. Forwarded mounts, sockets and SSH agents deliberately grant authority. A VM alone therefore does not establish this project's mutual confidentiality.

OpenShell's [current architecture](https://docs.nvidia.com/openshell/latest/about/architecture) separates untrusted workload enforcement from a trusted supervisor and describes a protected channel, outer egress fence and readiness checks. It is relevant precedent for the CR-11 boundary. Its gateway also owns lifecycle, so adopting the whole platform would need an explicit ownership composition. The older architecture RFC is not the authority for its current placement.

Nono's [draft NEP-0007](https://github.com/nolabs-ai/nono/blob/11d9e6b8e522a87325134e5399cc458f11e5bba7/neps/0007-remote-supervisor-decisions-over-vsock.md) separates guest enforcement from decisions, credentials and audit authority across vsock. It preserves request identity across reconnect and keeps guest-supplied identity from becoming authority. This is useful partial precedent; its host-side trust placement is not automatically this project's attested content boundary or independent durable Entity contract.

Project implication: compare these actual components before building the M2/M4 supervisor and broker. Require a reuse/reject record for the selected slice. Preserve outside Temporal orchestration, inner content processing, protected independent effect authority and one compute owner as separate responsibilities.

### Portable VM state could reduce native reconstruction, with substantial limits

SmolVM's [incremental checkpoint document](https://github.com/smol-machines/smolvm/blob/5521d6bc80dd15161c77b51a28c5a03cc0c2ce39/docs/incremental-checkpoints.md) describes paused CPU/device/disk capture, retained RAM streaming and publication only after durability. It also describes architecture/device constraints and explicit treatment of host mounts. These are vendor claims to test, not recovery acceptance.

A full process memory image could retain native subagent state that session JSONL omits. That is a meaningful alternative for a future bounded BD-01/BD-04/BD-08 experiment. It is not proof that external connections, model streams, approvals or nonrepeatable effects resume correctly. It does not make external services roll back with the VM. Restoring secrets or authority from old RAM could also conflict with generation fencing and independent authority.

The useful experiment would run the pinned native CLI with an active child, capture accepted state, remove original host/disk access, restore on a permitted compatible host, rebind control/credentials and compare exact action identities, outputs and controlled external effect counters. Include stale-generation and lost-response cases. Avoid host mounts. Inspect RAM/checkpoint storage for required confidentiality and retention. This is later work after a design decision, not new M1 snapshot support or a provider switch.

The documented [SmolVM S3 mount limitations](https://github.com/smol-machines/smolvm/blob/5521d6bc80dd15161c77b51a28c5a03cc0c2ce39/docs/limitations.md) include missing POSIX metadata, non-atomic renames and a flush boundary. A mounted object store cannot be assumed equivalent to a coherent native workspace.

### Policy learning and policy changes must retain authority

MXC's [denial diagnostics](https://github.com/microsoft/mxc/blob/ad54c69452147bd4ca15d027388ad6074903dbff/docs/logging-access-denied.md) distinguish blocked-access recording from permissive audit execution. The latter relaxes containment. OpenShell's [policy documentation](https://docs.nvidia.com/openshell/latest/how-it-works/policies/overview) distinguishes startup filesystem/process rules from mutable network policy.

Project implication: refuse permissive audit/profile overrides for admitted private workloads. Use synthetic data for policy authoring. Denial events may suggest a narrow policy proposal, but must not auto-grant authority. Define whether a policy update affects new connections, existing streams or requires restart; do not claim revocation without that proof. Do not introduce dynamic permissions in M1.

For package and runtime configuration tests, use an untrusted workspace containing `.env`, startup scripts, a malicious executable earlier on `PATH` and user-level tool configuration under `HOME`. Prove these cannot execute before confinement or replace admitted policy. Include inherited file descriptors, control sockets, writable mounts and native Read/subagent paths, not only Bash callbacks. These cases refine CR-01/CR-11/CR-12 without creating a new policy framework requirement.

### Diagnostics and supply chain remain inside the content contract

MXC's [telemetry policy](https://github.com/microsoft/mxc/blob/ad54c69452147bd4ca15d027388ad6074903dbff/docs/telemetry.md) documents consent and administrative constraints. SmolVM's security model discloses release integrity limitations. Neither fact supplies this project's admission proof.

Project implication: pin actual binary/image/package/policy identities, verify required artifacts and reject unsupported fallback. Review telemetry, denial records, crash output, proxy traces and checkpoint caches under CR-13 and retention rules. A candidate's public default is not an accepted project privacy policy. A coverage percentage or an audit log hash does not prove confinement or definitive external outcomes.

## Recommended phase handling

| Phase and owner | Action supported by this research | Keep outside this phase |
|---|---|---|
| M1 / CNR-2 through CNR-6, harness contribution | Keep the reviewed admission, stable identity, one owner, no unsupported fallback and fake conformance tests. Cite MXC validation as corroborating precedent if useful in review. | No MXC dependency, new provider, dynamic policy engine, network mediation framework or snapshot mode. |
| Early M2 demo / runtime composition with native integration input | Keep a clean local runtime, actual skill/helper placement, explicit readiness and close/delete ownership. Record exact native sandbox behavior and the trusted local profile. | No claim of operator confidentiality or full recovery; no platform survey as a prerequisite to the first ordinary demo. |
| Full M2 and M4 / runtime and security owners | Before custom confinement implementation, compare native sandbox-runtime, a bounded nono slice and OpenShell supervisor/isolation components. Test denied reads, sockets, egress bypass, unsafe modes and policy/configuration provenance. | No silent second lifecycle owner, host plaintext inspection or automatic permission widening. |
| M3 / recovery owner | Evaluate portable memory/disk checkpointing as one bounded alternative if native active-child recovery remains unsupported. Review compatibility, authority and confidentiality first. | No inferred exactly once effects, cloud/local API parity, or acceptance based on a successful VM restore alone. |
| M4 / deployment and policy owners | Retain AWS attestation and independent keys. Qualify the selected inner boundary and output policy, including caches and diagnostics. | No substitution of ordinary microVM isolation or credential injection for attestation and release authorization. |

The subsequent documentation update incorporates these recommendations into the [specification](../spec.md#later-stage-implementation-evidence), [plan](../plan.md), existing BD owners and [later milestone criteria](../tickets/later-milestones.md). Candidates remain unselected and all ticket states remain unchanged. The M1 design PASS remains scoped to its reviewed design; this supplemental review does not confer or revoke implementation acceptance. Later mechanism changes require their own scoped review before implementation.

## Effect on the collaboration boundary

The project continues to own the generic harness extension, runtime composition, recovery and confidential adapters. The Claude integration maintainer continues to own native SDK/Transport behavior and upstream examples. Useful joint questions remain exact tool confinement coverage, clean package placement and shutdown semantics. The discussion supplies no basis to make unrelated security platform adoption a prerequisite for PR #169 or its samples.

No public comment, message, dependency change or implementation was made from this review. Any adoption or acceptance change requires its normal scoped decision and verification.
