# Confidential agent runtime: replacement specification plan

Status: DOCUMENT CUTOVER EXECUTED, 2026-10-26. The project owner selected this proposal for execution. The [active package](README.md) owns current specification and review status. The body below preserves the transition proposal as written before execution; statements about files not yet created or a future formal pass describe that earlier checkpoint. Owner decisions and runtime implementation remain pending. Archive in place was selected to preserve fixture imports and historical evidence.

## Decision proposed

Keep this repository as the project home. Write a replacement specification for confidential native agent execution under an external Temporal control plane. Preserve useful requirements and evidence from the existing recovery work, but replace its implementation decomposition and delivery backlog where they no longer fit.

Use one active project directory, `docs/confidential-agent-runtime/`. Keep general sandbox lifecycle contributions in the Sandbox Orchestration Harness. Reuse the upstream Claude Agent SDK and CLI inside the runtime. Treat the ordinary remote SDK integration in upstream PR #169 as optional interoperability, not the foundation or prerequisite for this project's confidential content path.

Do not maintain another active design collection outside this repository. Extract the technical requirements and relevant source evidence into the replacement package. Retire the originating research collection after checking coverage and preserving historical evidence. The replacement package must be understandable without access to an external working folder or private conversation.

This is a replacement specification exercise, not a restart of all engineering. Retain proved results with their exact version, scenario and limitation. Do not transfer an old passing result to a different runtime or mechanism without new evidence.

## Inspected starting point

The local branch is `design-base` at `cad28f3`. It contains uncommitted changes to the existing design, tickets and diagrams, including untracked reset and retention preparation. Preserve these changes before any branch switch, archive move or integration update. No clean checkout or published copy of those changes is assumed.

The current [specification](../../python/claude_agent_sdk/docs/skill-recovery/spec.md), [plan](../../python/claude_agent_sdk/docs/skill-recovery/plan.md) and [ticket set](../../python/claude_agent_sdk/docs/skill-recovery/tickets/README.md) describe governed skill recovery. The [distributed recovery proposal](../../python/claude_agent_sdk/docs/skill-recovery/proposals/distributed-recovery/2026-10-08/README.md) remains conditional. The current specification still requires exact original pending call recovery, separate effect dispatch and durable human decisions. Its code decomposition is built around engine segments and effect Activities.

The inspected upstream integration is https://github.com/temporalio/ai-integrations/pull/169 at `18bc31e5005cbf403ebab38cb51e5cde4aa930a4`. It is an open draft. It places `ClaudeSDKClient` and content callbacks in Workflow code while the CLI runs remotely. A subsequently announced Transport redesign has not reached that source revision.

The inspected lifecycle harness is https://github.com/temporal-community/sandbox-orchestration-harness at `24f09129335f8057750f09f84a45b9c76c99d9c1`. Its current provider contract assumes a Worker inside compute. Explicit external runtime placement is a useful bounded contribution there.

The configured `origin` is a public fork with an older fork parent, not the authoritative upstream integration repository. Do not treat its default branch as a current upstream baseline. Architecture documents prepared for this repository must use technical descriptions and public sources, without private discussion transcripts or unrelated confidential material. Writing a local document is not publication authority.

## Why a replacement specification is needed

| Existing direction | Replacement direction to specify | Required disposition |
|---|---|---|
| Governed skill recovery implemented inside an SDK plugin | Confidential runtime composition across compute, native SDK, policy and outside orchestration | Give the composition its own project contract instead of placing every responsibility in the plugin |
| Workflow dispatches paused built in effects | Native agent owns the loop and ordinary built in execution | Reevaluate the effect control mechanism; preserve the uncertain action safety objective |
| Exact original pending call recovery | Native restoration under an explicit acknowledged progress contract | Decide whether exact pending recovery is still required, conditionally supported, or deliberately replaced |
| SDK, callbacks and policy can execute in a Worker | Confidential content processing stays inside the approved runtime | Outside Workers receive sealed content and approved metadata only |
| Human approvals as a core path | Fixed local policy for confidential tool decisions | Retain only question or output exchanges that satisfy the content release policy |
| Full plugin verification before harness port | Reuse the existing lifecycle controller from the first external runtime experiment | Avoid building a second compute owner or postponing useful controller integration |
| Large cumulative backlog | Small delivery slices with observable outcomes | Map old obligations before replacing tickets; do not carry old estimates forward |

The new design must not silently weaken earlier requirements. In particular, native continuation is not equivalent to exact call recovery, encrypted storage is not operator confidentiality, and a container demonstration is not attested execution. Record each changed guarantee as an explicit decision with its consequence.

## Repository and branch strategy

### Recommended approach

Keep ownership of this fork and the existing checkout. Make the replacement project package independent of the plugin's source tree. Keep production responsibilities modular: project composition here, general lifecycle changes in the harness, and generic SDK integration fixes upstream. This avoids both a second project documentation home and a permanent requirement to maintain a replacement Claude integration.

Do not change the current branch in this planning task. When implementation is selected, first preserve the dirty tree and its untracked evidence. Establish an explicit read only upstream remote for `temporalio/ai-integrations` and fetch reviewed revisions without merging them. Fetching a reference, adopting source, rebasing a branch and changing a runtime dependency are separate operations.

Use short contribution branches based on the repository that will accept each change. A generic integration fix may be based on an exact PR #169 revision if it actually changes that implementation. A lifecycle contribution belongs on a branch of the harness. The project specification and private runtime prototype do not need to inherit all of PR #169.

Once the relevant integration merges upstream, move affected contribution branches to a supported upstream baseline. Keep local compatibility patches small and identifiable. Do not repeatedly merge the entire draft branch into the project merely to stay current. Review updates at implementation boundaries and record the adopted SDK, CLI, integration and harness revisions.

### Alternatives considered

| Option | Decision | Reason |
|---|---|---|
| Replace the existing design in this fork | Recommend | Retains evidence and ownership while providing one active project home |
| Base the complete project on upstream PR #169 | Reject as the default | Its outside SDK topology does not satisfy the selected content boundary; the private local SDK route does not require it |
| Follow PR #169 on a separate integration branch | Use when needed | Appropriate for a focused upstream fix or ordinary deployment adapter |
| Continuously merge the draft into the project branch | Reject | Couples unrelated project work to changing protocol and lifecycle assumptions |
| Create a separate runtime repository immediately | Defer | A separate application repository may become appropriate at packaging or ownership handoff; it is not necessary to settle this specification or prove the first runtime |

The long term boundary is a small application or service composed from upstream components, not an indefinitely divergent SDK fork. Decide the eventual packaging and repository extraction when the prototype reveals actual application code and ownership needs. If extraction occurs, transfer the active project package with it and leave one redirect, rather than maintaining two specifications.

## Replacement architecture to specify

| Component | Intended responsibility | Excluded responsibility |
|---|---|---|
| Outside Temporal Workflow and Activities | Job lifecycle, authorized sealed operations, accepted recovery references and approved status | Parsing confidential agent prompts, outputs or tool arguments |
| Sandbox lifecycle controller | Create, reconcile, inspect, replace and remove compute | Owning the Claude agent loop or content policy |
| Runtime supervisor | Own local SDK lifecycle, authenticate inputs, enforce policy and coordinate protected persistence | Holding Namespace credentials or acting as an unrestricted remote shell |
| Native SDK and CLI | Native agent behavior and supported session continuation | Guaranteeing arbitrary external effects occur exactly once |
| Recovery adapter | Publish and restore a matching selected session and workspace state | Inferring accepted state from unrelated latest pointers or diagnostic telemetry |
| Trust and key adapter | Verify approved runtime identity and release scoped keys | Treating an ordinary container or generic provider capability flag as attestation |

For the first native route, the SDK and CLI communicate locally through the normal `SubprocessCLITransport`. The controller launches the runtime supervisor. A small sealed service protocol connects outside orchestration to that supervisor. Its exact operations, authentication, generation binding and acknowledgment meanings are specification work, not settled API names.

Separate the supervisor from untrusted generated commands. The specification must explain which process can read keys, use credentials, access control sockets, write policy and make outbound requests. Co location inside one VM is not sufficient isolation.

One controller owns compute. A connection retry must not create a second runtime. Communication close, CLI stop, runtime replacement and compute deletion must have distinct documented meanings. Define ownership across cancellation, reset and Continue-As-New rather than inheriting accidental behavior from a transport context manager.

## Requirements to extract and decisions to make

The replacement specification should contain a short requirement set that distinguishes the final outcome from prototype limitations:

- Native skill loading and agent behavior remain supported on the selected SDK and CLI versions.
- Outside orchestration cannot inspect confidential content. Service storage holds encrypted content and approved metadata only.
- The runtime contains no Temporal Worker or Namespace credential in the external mode.
- Client code, protected skill material and released outputs follow an explicit access policy. State which parties may observe each class.
- Preserve the mutual trust requirement that neither party can decrypt protected material alone. Specify the approval and key release arrangement without assuming that ordinary storage encryption meets it.
- Approved image identity and key release establish the final trust boundary. Protection from the cloud provider is a separate optional threat requirement, not implied by every attested runtime.
- State the model provider's permitted access to plaintext prompts. Confidential execution of the agent does not itself hide inference inputs from that provider.
- Recovery works on a replacement host with the original host and disk unavailable. Define the exact progress boundary, possible loss, repeat behavior and failure disposition.
- Session files, workspace, required sidecars and pending operations restore from one accepted state. Concurrent tools and background writes must fit the capture boundary.
- Unknown external mutations do not become an automatic retry. Select supported idempotency, reconciliation or stopped outcomes.
- Stale runtime generations cannot publish accepted progress or control the current runtime.
- Policy, input authentication, telemetry and output release are enforced inside the content trust boundary where needed.
- Paid experiments retain explicit authorization and a finite allowance. Reconcile the earlier strict preventive budgeting requirement rather than quietly deleting it or making it block all credential free development.

The most important owner decisions for specification authoring are these:

| Decision | Recommended starting position | Consequence if not selected |
|---|---|---|
| Engine and content placement | Native SDK plus CLI inside runtime | Any outside content processor must be included in the trusted base explicitly |
| Recovery guarantee | State native continuation limits, then test one replacement case | Exact original pending call recovery remains an unresolved obligation if still required |
| External actions in first prototype | Local filesystem workload and a controlled synthetic effect counter | Do not claim safety for arbitrary production mutations |
| Human interaction | Fixed local tool policy; explicitly permitted sealed questions and outputs | Earlier durable approval behavior cannot be assumed compatible with mutual confidentiality |
| Initial deployment | One local provider, with a later selected attested deployment | Local proof cannot establish attestation or cloud durability |
| Integrity scope | Preserve the documented distinction between stale generation handling and malicious operator rollback protection | A stronger integrity promise needs its own threat decision and evidence |
| Optional upstream interoperability | Add only for a concrete use case | No mandatory dependency on the changing remote Transport seam |

These are proposed positions, not approved answers. A source conversion must retain other applicable old obligations or list their explicit retirement. Do not infer that a requirement disappeared because its old implementation was abandoned.

## One active package and an explicit archival cutover

The intended active package is:

```text
docs/confidential-agent-runtime/
  rebaseline-plan.md
  spec.md
  plan.md
  decisions.md
  evidence/
  tickets/
```

Only `rebaseline-plan.md` is created by this task. The later authoring workflow can add its required evidence metadata in this directory. Do not create a second candidate specification elsewhere. The plan owns sequence, decisions owns unresolved owner choices, evidence owns observations, and tickets own work acceptance. Keep technical requirements in the specification rather than copying them into every file.

Perform the archival cutover when the replacement package and requirement mapping are ready:

1. Preserve the complete current tracked and untracked state before moving anything. Retain earlier runtime failures, reservations, approvals and immutable source pins.
2. Extract relevant technical requirements and inspectable evidence from the separate research collection. Separate stakeholder requirements, adopted decisions, proposals and source observations. Do not import private transcripts or environment specific paths into public project documents.
3. Map every old requirement and open DSR obligation to retained, replaced, explicitly retired, or deferred with a stated activation condition. Give each item one new owner. Keep DONE results at their historical scope.
4. Archive the existing recovery document tree together so its internal relative links and evidence remain intact. A candidate destination is `docs/archive/skill-recovery-v1/`; inspect incoming links, scripts and recorded commands before selecting the final move. Use redirect stubs only where needed for old entry points.
5. Update navigation and planning checks in the same cutover. Historical validation findings remain historical. A checker that assumes the old active paths must not silently assess the new package with the old contract.
6. Make the replacement package the sole active source for the new architecture. Mark old open work superseded or deferred through the mapping without changing historical DONE or failure evidence. Retire the separate research collection from active maintenance after coverage is checked.

The cutover must be atomic at the documentation contract level: no interval should advertise two specifications as current. Before cutover, this file is a transition proposal; the old specification still describes its old governed recovery scope. After cutover, archive notices must state the replacement location and the scope of historical claims.

## New delivery backlog shape

Create a new ticket series only after the replacement specification settles the changed guarantees. Do not reuse DSR identifiers or copy old estimates. The proposed first delivery units are:

| Delivery unit | Result | Exit evidence |
|---|---|---|
| Project cutover | One specification, decision list and obligation mapping | All old open obligations have a disposition; active navigation has one owner |
| Generic external runtime support | Explicit mode and narrow capability preflight in the harness | Existing defaults work; unsupported combinations allocate nothing; no Worker or Namespace credential in the example |
| Native runtime supervisor | One inside SDK/CLI runtime and sealed outside operations | Synthetic confidential content stays out of outside Worker payloads, logs, failures and telemetry; one lifecycle owner |
| Replacement recovery | One coherent native session and workspace restored without original host access | Conversation, files, generation and controlled effect counters match the declared recovery contract; uncertain outcomes stop |
| Confidential activation | One qualified approved image, key path and isolation profile | Attestation, key release, restricted administration, content policy and protected restoration meet the final trust requirements |

These units describe outcomes, not approved tickets or estimates. Each should produce a reviewable result. Use one provider and one representative native skill before adding provider breadth. Use credential free checks where they answer the question. Introduce model calls or cloud resources only for acceptance that needs them.

Autonomous runtime examples should initially disable command based idle suspension. Runtime aware idle behavior is a separate capability unless the selected provider already supplies it. Optional remote SDK adapters, Nexus, a Python harness SDK, universal process streaming and a replay engine are not prerequisites for this path.

## Next action after this plan

Agree the project and branch strategy and settle the owner decisions that affect the final guarantees. Then author the replacement specification and its minimal implementation plan in the active package, using the retained evidence rather than repeating the research program. Reconcile and archive the old backlog in that same specification cutover.

Stop investigation when a decision has enough source evidence to write a testable contract. Open new research only for a concrete unsupported assumption or failed acceptance case. Do not make the first useful external runtime contribution wait for every confidential deployment detail, and do not call that contribution completion of the confidential product.

No branch switch, upstream merge, archive move, ticket replacement, implementation, model call, cloud allocation, commit or publication is performed by this planning document.
