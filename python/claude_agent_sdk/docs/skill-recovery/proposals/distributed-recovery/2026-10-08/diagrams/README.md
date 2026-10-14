# Distributed recovery proposal diagrams

These views illustrate the conditional proposal. They do not establish runtime support or close ticket acceptance criteria. The candidate specification and plan own the design; older diagram revisions remain historical outside this export.

| View | SVG | Interactive HTML |
|---|---|---|
| Durable session and independent effect authority | [SVG](durable-session.svg) | [HTML](durable-session.html) |
| Workspace recovery and publication | [SVG](workspace-alternatives.svg) | [HTML](workspace-alternatives.html) |
| Termination and replacement barrier | [SVG](recovery-barrier.svg) | [HTML](recovery-barrier.html) |
| Effect succeeds before result publication fails | [SVG](result-publication-fault.svg) | [HTML](result-publication-fault.html) |

JSON specifications and portable delivery receipts accompany every view. Each original HTML delivery passed nine showcase checks with zero errors and warnings. Specification and HTML bytes are unchanged by export. SVGs passed XML parsing and retain embedded dark theme styles. Visual review was skipped because no capable browser or SVG rasterizer was available. This remains a limitation after migration.

## Complete architecture review views

The [architecture review pack](../architecture-review.md) contains Mermaid views for component/trust boundaries, payload encryption/offload, native checkpoint publication, effect outcomes, replacement barriers, harness/VFS correlation, Nexus policy, key/retention, confidential execution and positive child/parallel requirements. These are evaluation inputs, not qualified deployments. The earlier SVG/HTML exports above retain their historical scope.

## Skill package and engine attachment views

These views explain the [mandatory SDK execution path](../../../../spec.md#sdk-entrypoint-and-session-control), [project adapter contracts](../../../../spec.md#project-owned-adapter-record-and-operation-contracts) and [approved local configuration](../dsr-0.6-configuration.md#approved-local-configuration-2026-10-14). The canonical specification owns the contracts, the configuration owns the finite profile choices, and the [maintained tickets](../../../../tickets/README.md) own implementation and acceptance. These views add no contract or status authority.

| View | SVG | Use |
|---|---|---|
| Existing skill package, native Claude execution and Temporal coordination | [SVG](skill-execution-binding.svg) | Read first for the caller, service, package admission, runner, native engine and candidate Mods layer |
| Engine attachment to project contracts | [SVG](engine-adapter-boundaries.svg) | Read next for accepted state, dispatch, storage, execution control, readers/keys, artifact processing and transport |
| Recovery proof sequence | [SVG](recovery-proof-sequence.svg) | Compare the initial local container proof with the required later host-loss and partition proof |

An admitted skill retains its instructions, scripts and references. Native skill loading does not require Mods. The project runner binds package admission, workspace, tools and runtime policy to the SDK. TypeScript Mods are a separate candidate hook layer inside SDK-launched Claude Code; they do not own durable authority. Package compatibility, script dependencies and permissions must be admitted. These views do not promise that every existing skill runs unchanged.

The engine attachment view is a typed operation map, not a physical deployment topology. Trusted adapters mediate the operations; job code does not receive controller privileges or unrestricted key access. The views are not the complete acceptance inventory. Selected native projection, restricted Code Mode/harness integration and positive child/parallel qualification remain required at their existing ticket owners.

Independent source review on 2026-10-14 passed the three SVGs for scoped semantic fidelity. All three passed XML parsing. Candidate validation, delivery and strict checks passed, but full finalization did not pass because browser checks were skipped. No rendered visual review occurred. A Windows process launch failure from the review environment prevented the permitted browser routes; no software was installed to repair it. Browser rendering, clipping, routing and interactive behavior remain unverified.

The separate architecture review pack still needs three corrections: route the overview's direct SDK effect path through the governed intent/Entity boundary; separate or label the reader-to-operation route as read only; and distinguish the selected reader broker from its unimplemented qualification. These SVGs do not fix those Mermaid sources or establish runtime admission. Preserve historical diagrams and the dated handoff when correcting the maintained pack.
