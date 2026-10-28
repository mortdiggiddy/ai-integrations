# Confidential native agent runtime

Status: ACTIVE PROJECT HOME, 2026-10-27. M1 uses provider configuration and existing `Start` after maintainer clarification supplied by the operator. The combined CNR-2 compatibility and CNR-3 concrete provider contribution passed fresh independent verification and the lead rerun; their tickets own the exact revision and evidence. The earlier mode/interface review remains historical. CNR-4 lifecycle policy, the generic demo and complete M1 acceptance remain pending. Later native recovery and trusted deployment requirements retain their own stages and approval scope.

## Document owners

| Document | Responsibility |
|---|---|
| [Specification](spec.md) | Stable requirements, acceptance boundaries and the proposed content and lifecycle architecture |
| [Plan](plan.md) | Delivery order, dependencies, activation and stopping conditions |
| [Decisions](decisions.md) | Approval carryover, native design work and genuine remaining owner choices |
| [Runtime protocol](runtime-protocol.md) | Proposed sealed operations, capture, budget admission, key release and handoff contracts |
| [Native recovery protocol](native-recovery-protocol.md) | Proposed original-call authority, exact outcomes and prelaunch restoration, with explicit native capability gaps |
| [Obligation map](obligation-map.md) and [machine record](obligation-map.json) | Disposition of historical requirements, assumptions, decisions, qualification cases and tickets |
| [Evidence](evidence/README.md) | Sanitized research extraction, primary source pins and actual proof limits |
| [Verification report](verification-report.md) and [manifest](verification-manifest.json) | Formal evidence gate results, independent findings and review limits |
| [Transition proposal](rebaseline-plan.md) | Historical basis for this cutover; subsequent status is owned here |
| [Local backlog](tickets/README.md) | M1 implementation tickets and gated later milestone outcomes |
| [Collaboration handoff](collaboration-handoff.md) | Proposed ownership boundary, shared interface checks and the first demo sequence |

This is the only active project design package. The [older recovery tree](../../python/claude_agent_sdk/docs/skill-recovery/ARCHIVED.md) is archived in place. Its source, fixtures, experiments and historical states remain inspectable, but its open work is not the active implementation backlog for this architecture.

## What is selected and what is pending

The project home and cutover are selected. The prepared direction uses native SDK and CLI execution inside an approved runtime, an outside Temporal control plane handling sealed content, and one sandbox lifecycle owner. Ordinary remote SDK interoperability is optional. These boundaries do not prove the supervisor protocol, coherent native recovery, confinement, attestation or key release.

Exact original pending call recovery, protected independent Entity authority and strict preventive budgeting remain required. The approved synthetic local provider, key/read roles and retention policy carry forward within their recorded scope. The runtime and native recovery protocols supply later-stage guidance; bounded main-agent and safety contracts were independently reviewed, while implementation and qualification remain pending. Per-tool projection requires actual schema and native consumption checks. Active-child resume remains unresolved, and parking does not fulfill positive recovery.

The final provider direction remains AWS EC2 NitroTPM, a mutually approved Attestable AMI and independently administered KMS policies, with inherited cloud provider trust. Google Confidential Space remains an alternative. Exact image measurements, key policies and isolation require qualification; recipient disclosure, model provider access and uncertain Bash actions retain their applicable gates. Historical approvals do not close new runtime acceptance rows.

## Next work

The [cutover validation record](cutover-validation.json) records source preservation, complete coverage, independent review and proving limits. Run `python3 docs/confidential-agent-runtime/check_documents.py` from the repository root to check document links, source identities, ticket preservation and obligation coverage. This is a document integrity check, not formal specification or runtime validation.

The [M1 plan](plan.md#m1-explicit-external-runtime-support) records the existing interface direction. The [local backlog](tickets/README.md) owns delivery order and exact acceptance state: CNR-2 supplies verified compatibility and CNR-3 supplies concrete provider admission. CNR-4 native lifecycle policy follows, then the generic demo and M1 acceptance. Later phases remain unestimated milestone containers. Maintainer acceptance gates upstream merge. Future confidential business policies do not block this generic contribution. The review ledger preserves earlier verdicts for their actual scope. Do not resume the archived DSR queue or issue a broad replacement backlog by default.

The first useful implementation target is a configured native process through existing harness lifecycle interfaces, with only demonstrated missing validation and provider changes. This documentation update does not implement the revision or change the published PR. The native skill demo, replacement recovery and confidential activation retain their separate decision and verification gates.
