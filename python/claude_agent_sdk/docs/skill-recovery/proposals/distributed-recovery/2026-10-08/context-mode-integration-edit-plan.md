# Context Mode reuse findings and documentation execution handoff

Status: PREPARED AND VERIFIED FOR DOCUMENTATION (2026-10-11). The proposed architecture remains CONDITIONAL. This document records research findings and instructions for future documentation edits. It does not approve a dependency, fork, tool, deployment, protocol or runtime experiment. DSR-0.6 remains OPEN. DSR-2.1 remains OPEN and blocked by the applicable DSR-0.6 choices.

## Purpose and execution boundary

Use this document as the input when the operator asks an agent to execute the documentation adjustments. Read the complete document before editing. Execute only the applicable actions in the documentation ledger. A request to execute this document authorizes those documentation actions; it does not select the alternatives, approve the optional integration, authorize implementation, or authorize commits and pushes.

The output of that later task is a coherent documentation diff, an action receipt, unresolved choices and one next action. Do not implement DSR-2.1, build an executor, use `execute-design`, install or upgrade dependencies, build or pull images, run models, inspect credentials, provision infrastructure, terminate a provider resource, contact an external party, commit, or push without separate applicable authorization. Do not interpret a qualification recipe as permission to run it.

This document owns the integration findings and future edit ledger. The existing [research note](context-execution-research.md) owns the maintained technical comparison. The [configuration recommendation](dsr-0.6-configuration.md) owns the proposed first portable qualification stack. The [canonical documents register](../../../canonical-documents.md) identifies the contract owners. Transfer accepted research clarifications to the research owner through the ledger; do not maintain a second specification here.

## Recommendation

Reuse Context Mode's separation of complete artifacts, derived retrieval indexes and small model inputs. Reference its capability descriptors, adapter packaging, scoped instructions and diagnostics. First compare a fixed processor with immutable inputs and retained exact output. Keep this optional work separate from the portable recovery decision.

Do not fork the complete package now. Do not enable its arbitrary execution tools or copy its central routing skill unchanged. A narrowly scoped external component with a thin adapter is a later option after license, dependency, policy and compatibility selection. A small maintained fork is justified only when the required approved interface cannot be separated through a component or upstream extension. An independently authored implementation of the narrow principles is another alternative; copied source or instructions cannot be called an independent implementation.

The immediate decision remains whether the proposed AWS/S3, protected Temporal Entity authority and externally terminated dedicated Linux EC2 instance is the first portable qualification target. The cold checkpoint direction and original disk unavailable outcome are already approved directions. Product configuration, applicable protocol adoption, owners and finite execution allowance remain unresolved. Optional Context Mode processing does not become a new blocker to DSR-2.1 when it remains deferred.

## Authority and preserved dispositions

Use the current paragraphs and status rows, not earlier narrative, to determine ticket dispositions. Read the Phase 1 independent verification checkpoint dated 2026-10-07 and its approved exit in [canonical evidence](../../../evidence.md). Phase 1 is complete at its bounded dispositions. Preserve DSR-1.6, DSR-1.7 and DSR-1.9 as DONE at their recorded bounded scope. Do not repeat their experiments.

Preserve the mandatory Claude SDK entrypoint, acceptance of a segment before external effects, the exact original pending call and result, unknown Bash parking before any next model segment, independent authoritative cleanup before replacement and denial of unsupported native child recovery. An Entity or Child Workflow does not supply a physical process boundary. Activity timeout, cancellation, storage availability, lease expiry and force deletion do not prove that the old execution cannot continue.

Canonical governed v1 still has its shared volume/file claim contract and restricted tool set. The distributed candidate remains CONDITIONAL and not adopted. A proposed portable protocol needs an explicit approved rebaseline before its requirements replace that contract. External MCP/custom script tools are not admitted because another package supports them. Internal processing of already retained artifacts and admission of a Claude visible tool are separate choices.

Keep DSR-0.6 as the workspace/isolation decision owner, DSR-0.11 as the retention/session store owner and DSR-7.4 as the native child/parallel extension decision owner. Do not reopen completed DSR-0.3 or DSR-0.12 to record new adoption work. Do not revive superseded DSR-2.5, DSR-2.8 or DSR-3.8. Preserve raw archives, historical FAIL/DEFECT records, publication and preservation manifests, frozen review snapshots and consumed reservations.

## Source pin and worktree baseline

Prepared against branch `design-base`, HEAD `4553c340ed4ba8477de09af4888bd00008db8e41`, with 14 existing pending files preserved. The working tree, including those pending files, is the preparation baseline. It is not the same tree as the published HEAD alone. No existing file was edited to create this handoff.

All paths in the next table are relative to `python/claude_agent_sdk/docs/skill-recovery/`. The digests are freshness checks, not instructions to restore old contents. If HEAD, bytes, heading, status or source pin has changed, inspect the current change and reconcile the affected action. Never overwrite new work with the captured baseline.

| Owner path | Observed SHA256 |
|---|---|
| `spec.md` | `cf70b8ad00b04e83406340edd0b5c6215b1a8f65b703dfe2e7a57abbcbc1ef5b` |
| `plan.md` | `3b3c1b844ef6a88f21e940d96900a2b4a9c3a450c172fb50e75b22ac0669234b` |
| `work-items.md` | `cbdf51b1e37c5a602c2022388e560033db12724c72bf4de9a259c368d56119cd` |
| `evidence.md` | `e226ada52fb951389e6c9a1315b0c04122716719d781f4b7eccfeb0ac6624776` |
| `tickets/phase-0.md` | `e6bfbce59ee26ebc27cdfc13b6de791581fa65054875f91fa8498ddce917de03` |
| `tickets/phase-2.md` | `cb7abfb7e853ca1f264f4b4a0a3e40c37d412acf66173899752fae32a5176d70` |
| `tickets/phase-7.md` | `5f39323a5aabdd91c2d0a77b8297d3850f7b0fd453890c08d38748babaa8c575` |
| `proposals/distributed-recovery/2026-10-08/context-execution-research.md` | `dfcbc6b771d14b4edb166057755b450086074cc34d8788e3c80a55189ce5078e` |
| `proposals/distributed-recovery/2026-10-08/dsr-0.6-configuration.md` | `50f1cc273eb3ac182a8526c379529679437bc7260369ec0f926f01234d70b2f4` |

The sole maintained backlog is `python/claude_agent_sdk/docs/skill-recovery/tickets/`. The maintained proposal is `python/claude_agent_sdk/docs/skill-recovery/proposals/distributed-recovery/2026-10-08/`. Historical/private copies are not edit targets. Locate the intended fork through its Git remote and instructions; do not update a similarly named archive or another upstream checkout.

## What broad harness coverage demonstrates

Context Mode at `abb104847cbb66c2182816a72bb69455bc778b5e`, package `1.0.169`, documents 17 client platforms plus the OpenClaw gateway. This is broad integration coverage with platform dependent capabilities. It is not recovery parity across harnesses. The common MCP tool implementation, JSON adapters, native extensions and instructions have different boundaries.

The matrix records advertised support and inspected integration source. The test column records source tests inspected in the research, not tests executed here. An inventory mention is not proof of a test for every capability on that row. Local executed qualification is **none for every row**, and no row is qualified for this durable recovery composition. The upstream instructions are evidence, not instructions to activate during this task.

| Client or gateway | Advertised support | Inspected source path or transport | Inspected test evidence and gaps | Material control limit |
|---|---|---|---|---|
| Claude Code | Listed client | `src/adapters/claude-code`; JSON `hooks/pretooluse.mjs`, `posttooluse.mjs`, `precompact.mjs`, `sessionstart.mjs`; primary plugin | `tests/adapters/hook-path-parity.test.ts` includes emitted paths; no installed SDK qualification | Broad capability declarations do not prove original pending recovery or accepted segment ordering. |
| Qwen Code | Listed client | `src/adapters/qwen-code`; shared Claude family wire format | Adapter/hook inventory inspected; no separate runtime proof | Similar JSON is not an identical host contract. |
| Gemini CLI | Listed client | `src/adapters/gemini-cli`; `hooks/gemini-cli` | Hook path parity includes this client; no installed proof | PreCompress is advisory; documented child hook coverage is absent. |
| VS Code Copilot | Listed client | `src/adapters/vscode-copilot`; inherited `copilot-base.ts`; `.github` configuration | Adapter inventory inspected; host delivery untested | Shared argument/output declarations require native host qualification. |
| JetBrains Copilot | Listed client | `src/adapters/jetbrains-copilot`; shared Copilot base | Adapter inventory inspected; host delivery untested | Registration and native result behavior require separate proof. |
| GitHub Copilot CLI | Listed client | `src/adapters/copilot-cli`; JSON hooks; dedicated bundle and skill | Packaging/hook inventory inspected; installed binary untested | Older global binaries can leave hooks inert and calls allowed; documentation says output modification is unavailable. |
| Cursor | Listed client | `src/adapters/cursor`; JSON hooks and rules | Adapter inventory inspected; disputed events untested | Source declares SessionStart; documentation describes rejected/buggy SessionStart. `failClosed: false`; no output modification. |
| OpenCode | Listed client | `src/adapters/opencode/plugin.ts`; native tools and callbacks | Adapter/session inventory inspected; actual delivery untested | Experimental compaction/system transformation; Bash output UI caveat; native tool names are not always MCP names. |
| KiloCode | Listed client | OpenCode plugin route with Kilo identity/configuration | Shared route inspected; no independent all-capability qualification | Shared implementation does not prove separate host behavior. |
| OpenClaw | Listed gateway | `src/adapters/openclaw/plugin.ts`; native tools, callbacks and context engine | Gateway/analytics inventory inspected; host untested | Gateway is not an ordinary MCP client; no output rewriting; optional external analytics path. |
| Codex CLI | Listed client | `src/adapters/codex`; JSON hooks and TOML MCP configuration | `tests/adapters/codex-external-mcp-routing.test.ts` checks matchers/configuration | Argument/output modification disabled; PreToolUse soft context dropped; event/version delivery untested. |
| Kimi Code | Listed client | `src/adapters/kimi`; JSON hooks and response formatters | Adapter source inspected; contradictory capabilities untested | Documentation claims argument/ask/context support. Source disables argument/output/session injection; PreToolUse emits deny only, while later formatters emit additional context. |
| Antigravity IDE | Listed client | `src/adapters/antigravity`; MCP plus instructions | Packaging/adapter inventory inspected; no hook proof | No JSON hook capabilities declared; instructions cannot enforce effects. |
| Antigravity CLI (`agy`) | Listed client | `src/adapters/antigravity-cli`; limited JSON hooks and plugin bundle | Packaging/adapter inventory inspected; cited runtime untested | No argument/output/session/compaction capability; Stop documented as best effort and unverified for cited `agy 1.0.6`. |
| Kiro | Listed client | `src/adapters/kiro`; JSON hooks and `agentSpawn` | Hook path parity includes this client; host untested | Source uses `agentSpawn` as session start; documentation understates it. No argument/output modification or compaction. |
| Zed | Listed client | `src/adapters/zed`; MCP plus instructions | Packaging/adapter inventory inspected; no hook proof | No JSON hook capabilities declared. |
| Pi | Listed client | `src/adapters/pi/index.ts` plus native `extension.ts` | `pi-bridge-parent-death.test.ts`, `pi-mcp-bridge-env-scrub.test.ts` provide local cases | Standard HookAdapter is all false, but native callbacks exist. Routing failure permits passthrough; local parent death is not remote host death. |
| OMP / Oh My Pi | Listed client | `src/adapters/omp/index.ts` plus native `plugin.ts`; `package.json` `omp.extensions` | Adapter/packaging source inspected; actual delivery untested | Adapter comments say native hooks are unwired, but plugin registers callbacks and MCP. Do not call it globally hookless. |

Read `src/adapters/types.ts` for `PlatformCapabilities`, normalized events and `HookAdapter`, and `src/adapters/client-map.ts` for MCP client names. Capability flags are a useful test inventory. They are not observed enforcement. Source declarations and published documentation conflict for Cursor, Kimi and parts of the native Pi/OMP routes; resolve them only against a selected installed host/version and negative tests.

`tests/adapters/hook-path-parity.test.ts` covers emitted paths for Claude Code, Gemini CLI and Kiro and explicitly excludes other dispatcher platforms. `tests/integration/seed-parity-coverage.test.ts` checks analytics event fields against a seed schema with mocked fetch. Neither proves recovery parity. No third party test was run during this review.

## Components and principles to reuse

| Component or principle | Proposed reuse | Required adaptation or rejection boundary |
|---|---|---|
| Complete artifact separated from model excerpt | Reuse the principle in preparation | Retain full result and exact accepted projection. Recovery uses that stored projection, not a new search. |
| `src/store.ts` chunking, SQLite FTS5, BM25 and trigram search | Evaluate a narrow component after selection | Index is derived and disposable. Bind immutable artifact identity, authorized namespace/session and processor version. Database recreation is not recovery of accepted data. |
| File ingestion instead of large tool parameters | Reuse the principle | Replace mutable host paths with authenticated immutable artifact references for portable work. A path is not content identity or authorization. |
| Fixed processor and explicit output | Preferred optional qualification | Fixed processor/version/query and immutable bytes; allow bounded scratch/index/output writes only. Deny live workspace mutation, network and background descendants. |
| Capability descriptors and per-platform formatters | Reference compatibility design | Record declared, inspected and executed capability separately. Refuse unsupported promised controls or declare the exact reduced guarantee. |
| Normalized events/tool names | Reference or small adapter | Retain native raw identity, error/status and provenance beside normalized records. Normalization does not mint execution authority or a recoverable original call. |
| Per-platform instruction delivery | Reference packaging | Author a scoped skill only for approved processing. Do not overwrite project/global instructions or route unapproved execution. |
| Registration, callback and tool diagnostics | Reference diagnostic design | Test callback coverage and harmless deny behavior. Missing required protection must prevent dispatch or model continuation independently. |
| Project/session isolation cases | Reference tests | Use durable authorization and namespace/session/artifact identities. Local path hashes are insufficient. |
| Context byte accounting | Reference measurement | Measure model input, Temporal payload and Worker memory separately. Disable external telemetry by default. |
| `src/session/snapshot.ts` and local session events | Convenience reference only | Do not use as authoritative conversation/workspace pair, original pending record or dispatch authority. |
| General `ctx_execute`, `ctx_execute_file` and batch execution | Reject general governed v1 adoption | Ordinary process execution can hide writes/network effects inside one outer tool and leave unknown continuing work. |
| Upgrade, purge, dependency healing and install helpers | Exclude from the reuse runtime | They can change pins, host configuration or retained data. No runtime self-upgrade or destructive purge. |

The package has `skills/context-mode/SKILL.md`, references `anti-patterns.md`, `patterns-javascript.md`, `patterns-python.md`, `patterns-shell.md`, and utility skills under `skills/ctx-{doctor,index,insight,purge,search,stats,upgrade}/SKILL.md`. Dedicated bundles include `configs/copilot-cli/skills/context-mode/SKILL.md` and `configs/antigravity-cli/skills/context-mode/SKILL.md`. Harness instructions are separate under `configs/`.

The central skill routes most reads, tests, builds and service calls through Context Mode. It permits direct file mutations, Git writes, package installation and process control. Those routing choices are not permission decisions for this project. Browser and parallel guidance exceed the current admitted tool and child scope. The anti-pattern reference also allows ordinary Bash for short output and refers to a model summarization call, which differs from the central routing rule. Do not copy this inconsistent package as an accepted durable Skill.

Generic external MCP routing in `hooks/core/routing.mjs` supplies periodic guidance and does not deny or modify that call. It cannot guarantee that every raw response stays out of model context. `hooks/platform-bridge.mjs` can forward events to a configured external endpoint using configured credentials. A selected reuse profile must omit or disable that path and test zero outbound requests. The research inspected source, not credential files.

## Dependency, upstream change and fork decision

| Route | Benefit | Cost or risk | Disposition |
|---|---|---|---|
| Locally authored contracts based on principles | No package activation or code copying; preserves present boundaries | Processor and recovery composition still need their own tests | Recommended now for documentation preparation. |
| Pinned external component plus thin adapter | Reuses retrieval implementation and integration experience | Node/dependency footprint, startup effects and license fit; stable restricted API may be absent | Evaluate only after a lane is selected. |
| Proposed upstream extension | General improvements remain maintained upstream | Acceptance/timing uncertain; requires separately authorized external contact | Prepare suggestions; do not send them now. |
| Minimal maintained fork | Can remove unsafe startup/executor surfaces and expose a needed interface | Divergence, security updates, builds, ownership and license obligations | Only if approved requirements cannot use a narrower route. |
| Independently authored narrow implementation | Avoids unsuitable dependency/license coupling | More owned implementation and tests | Alternative; no source or instruction copying implied. |

Possible upstream improvements are accurate native extension capability documentation, deterministic immutable input APIs, fixed processor entrypoints, explicit raw/accepted result separation and diagnostics that detect missing callbacks. These are recommendations for discussion, not claims that upstream agreed to implement them.

Context Mode uses Elastic License 2.0, not MIT. The inspected tree provides no separate permissive exception for Markdown skills, bundled instructions, assets or code. Resolve intended plugin distribution, example publication and any hosted offering with the designated license owner before copying selected files or offering substantial functionality as a service. Preserve applicable license/notices and modification notices if reuse is approved. This is an unresolved fit check, not a claim that all integration is prohibited.

Before approving a fork, identify exact selected files, forbidden runtime surfaces, maintained divergence, update owner, source pin, reproducible build and meaningful tests. Sketch the narrow API seam first. If it suffices, do not fork. Neither a fork nor an adapter is a physical security boundary by itself.

## Retained data and native result projection

Three state classes need separate ownership: the exact authoritative conversation/outcome, retained complete artifacts with the accepted projection, and the derived retrieval index. A configured persistent SQLite database can still be a cache. Its local persistence and multiwriter design do not establish cross-host authority or checkpoint pairing.

A selected projection receipt must bind original call identity, raw definitive result, native error/status/metadata, the exact accepted model representation, processor/schema/version and digests. Define which native fields remain unchanged before acceptance. Never use a new `$.tool.call` identity, later retrieval order, a rewritten accepted prefix or a summary as restoration of the original result. Rebuilding an index is permitted only from retained authenticated artifacts and does not alter the stored accepted projection.

Mods `session.append` can change transcript/model content before storage. It is not UI-only filtering, a segment commit barrier, arbitrary native result injection or durable cross-process suspension. Core's opaque tool `ref` is process-local. A Mod callback waiting on Temporal does not establish the required acceptance ordering. Required guards can disappear after crashes or safe mode; independent prevention must cover absence/unload, not just a caught callback exception.

If an output exclusion guarantee is selected, a missing projection Mod must block the next model request through an independent control. Full raw fallback is allowed only when no such exclusion guarantee is offered. Count physical effects and unintended model payload exposure separately. Stub tests must assert callbacks ran and intended denials occurred; a successful test exit can coexist with a skipped hook.

Public Mods declarations and newer live documentation have different version identities. Preserve historical activation FAIL for its exact installed runtime and preserve separate original pending PASS evidence. Do not infer a new minimum version or installed success from current documentation. Complete response escrow, positive child recovery, multiple pending native calls and confidential execution remain unqualified optional lanes under their existing owners.

## Temporal execution choices and failure boundaries

| Choice | Useful property | Boundary and disposition |
|---|---|---|
| Fixed processor Activity | External computation against immutable inputs with recorded output | Preferred optional comparison. No live mutation/network; exact accepted output retained. |
| Restricted Code Mode component | Suspends at explicit registered host functions for per-operation coordination | Strong further reference from the pinned harness. Keep mandatory Claude SDK loop; adapter and custom tool admission remain unqualified. |
| Whole `ctx_execute` Activity | One recorded outer operation | Does not expose each internal effect. One attempt does not prove nonexecution. Unknown outcome parks; no automatic retry or background adoption. |
| Identified remote job, submit and poll | Existing job can be reconciled without rerunning computation | Require atomic logical key admission and lookup after lost reply, plus retained exact outcome. Returned provider ID alone is insufficient. |
| Async Activity completion | Releases the Activity Worker while an identified job runs | Token expiry does not kill the job or authorize resubmission. Result delivery authority and job lifetime are separate. |
| Child or Entity Workflow lifecycle | Durable logical ownership and multistage reconciliation | Closure, cancellation, reset or a stale message is not OS death. Native Claude child recovery is a different capability. |

The harness Monty component still uses pooled subprocesses for pure computation. Its replay boundary is explicit capabilities and recorded host outcomes, not the absence of processes. `run_tool` does not make every host function an Activity automatically. Runner, tool registration, approval/event contracts, VFS and optional interpreter dependencies are ambient requirements. A source test is not a standalone Claude SDK adapter proof.

OpenAI sandbox and Go sandbox lifecycle patterns provide source references for session state and provider adapters. Their default command retries, stop acknowledgements, provider resume behavior and payload snapshots do not satisfy our whole execution termination and exact original call contract. Do not inherit those defaults. An immutable draft with separately accepted publication is a proposed further option, not an implemented transaction and not reversal of an escaped external request.

| Failure | Allowed evidence | Remaining obligation |
|---|---|---|
| Surviving host, replaced container | Qualified local supervisor cleanup and preserved host files/claims | Exact accepted bytes and whole old execution/descendant cleanup. Container replacement alone is insufficient. |
| Permanent host/disk loss | Already accepted external pair and retained authority/outcomes | Restore on H2 with no H1 disk access. Missing accepted bytes are FAIL; unknown prior effects park. A postimage cannot be captured after real loss. |
| Network partition | Independent authority can reject stale publication; external controller can obtain terminal incarnation evidence | Old host can still act. No replacement effect dispatch before authoritative whole execution death. Already issued remote requests require reconciliation or park. |

Storage availability supplies bytes, Activity timeout supplies scheduling information, and lease expiry supplies a logical deadline. None proves physical exclusion. Routine destructive cleanup must preserve required sole-readable bytes before termination. Urgent containment or genuine host loss can leave a parked effect and data loss; record that boundary instead of fabricating recovery.

## Material uncertainties and smallest future qualifications

These recipes are not executed evidence. Use installed model-free seams where possible. Provider, installed-host and native SDK tests require their own selected scope and authorization. Do not repeat completed Phase 1 experiments.

| ID | Uncertainty and risk if wrong | Smallest qualification and required oracle | Existing owner |
|---|---|---|---|
| Q-1 | A nominal processor changes workspace or external systems | One fixed synthetic immutable input; allow bounded scratch/output writes; deny live workspace, network and detached descendants; assert zero forbidden effects/egress | DSR-4.1, DSR-2.7 |
| Q-2 | Index rebuilding silently changes accepted model input | Delete index; restore immutable artifacts on H2; compare source hashes and retrieval outputs; recover the stored accepted projection unchanged | DSR-0.11, DSR-5.4 |
| Q-3 | Wrong identity/status or missing native bookkeeping advances a pending call | One success and one error original pending fixture with metadata; lose publication reply; fresh Worker restores same raw/accepted receipt and call identity; later selected native differential proof | DSR-2.6 |
| Q-4 | Missing projection hook exposes excluded output | Large synthetic result; record intended next-model bytes; remove/skip hook; assert callback coverage and independent refusal, zero unintended exposure | DSR-2.6, DSR-2.7 |
| Q-5 | Source adapter flags are mistaken for host enforcement | One callback and harmless denied effect per selected installed runtime, then absent/unloaded callback negative; check actual delivered result | DSR-2.6, DSR-5.6 |
| Q-6 | Artifact labels or paths allow cross-session exposure | Two authorized sessions with identical labels and different immutable artifacts; attempt cross-scope lookup; require denial and no leaked bytes | DSR-0.11, DSR-5.4 |
| Q-7 | Component import starts executor, telemetry, healer or config mutation | Inspect dependency/startup graph; after execution authorization invoke only selected API with offline fakes; assert no outbound/config/install surfaces | DSR-0.6, DSR-4.1 |
| Q-8 | Outer Activity retry repeats hidden inner mutation | One witnessed harmless mutation, lost completion, independent invocation count; require park and zero next model starts or second spawn | DSR-2.2, DSR-2.3 |
| Q-9 | Remote submit reply loss duplicates jobs or loses completed output | Fake provider atomically accepts logical key and supports lookup; lose submit and result replies; reconcile one job with exact retained stdout/exit/artifacts | DSR-2.3, DSR-0.10 if selected keyed service scope applies |
| Q-10 | Local replacement retains transcript but loses file/claim or descendant consistency | Replace container on surviving host; check exact bytes/claims and whole old execution cleanup witness | DSR-4.3 |
| Q-11 | Local-only state is mistaken for portable recovery | Publish one tiny accepted pair; deny all H1 disk access; restore on H2; validate identity before scripted continuation; missing accepted bytes FAIL | DSR-4.3, DSR-5.4 |
| Q-12 | Two partitioned live executions act concurrently | Keep old canary/effect egress alive while control is unavailable; readable store must not admit H2; lose termination reply, reconcile exact terminal incarnation; assert no replacement before witness | DSR-4.1, DSR-4.3 |
| Q-13 | Unresolved local postimage is destroyed during planned cleanup | Fail sealing/publication after harmless effect; request routine cleanup; require refusal while required bytes remain only local | DSR-4.2 |
| Q-14 | Logical authority can be reset into an empty reusable permission | Concurrent duplicate and lost Update reply; outer reset/preclaim restore; attempt authority reset/recreation; require denial or park, one physical invocation | DSR-0.8, DSR-3.5 |
| Q-15 | Unnecessary fork creates unowned maintenance or improper copying | Read-only adapter seam sketch and exact selected file/license/service review with designated owners | DSR-0.6 selection; no runtime proof claimed |

Q-9 does not revive superseded keyed author tools or introduce a new keyed service by implication. A provider keyed submission interface requires selected scope and retention. Q-10, Q-11 and Q-12 are different proof cases; none substitutes for the others.

## Six owner decisions: applicable now and deferred

The [configuration owner](dsr-0.6-configuration.md#six-owner-decisions-and-blockers) contains the full decision split. This summary tells the future edit agent which choices it cannot infer. Keep all six candidate rows Open until applicable answers and evidence are actually recorded.

| Decision | Must be settled for dependent portable work | Can remain deferred |
|---|---|---|
| BD-1 | First failure envelope; accepted-data loss FAIL; unknown effects/partition park without independent death; exact finite recovery limits before execution | Region failure and live-memory/PTY/daemon continuity |
| BD-2 | Select or replace AWS/S3/protected Entity/EC2 qualification target; storage, integration, Security and deployment owners; required configuration | Production density/autoscaling and alternate-provider matrix |
| BD-3 | Finite retained object/key/authority survival; reset/recreation/rollback prohibition and supported outer reset; retirement window | Production backup/migration and retention tuning if not offered in the rig |
| BD-4 | Exact one-session/one-pending/harmless-effect workspace, byte, time and run allowance before executing the rig | Production throughput, latency SLO and large-workspace optimization |
| BD-5 | Trusted host/provider boundary; encryption, key survival, readers and credential separation | Confidential execution only when protection against host/provider is not required |
| BD-6 | Applicable portable protocol and canonical rebaseline; integration interface ownership and pinned revision | Context processing, Mods projection, full response escrow, native child and multiple pending calls |

If optional processing is selected, also settle its exact admission boundary, result/projection guarantee, retained receipt representation, dependency/license route and owner. If a required output exclusion guarantee is selected, independent missing-hook prevention is mandatory. These choices are not prerequisites when that lane remains deferred. No fork choice can answer the physical termination or portable authority questions.

## Documentation ledger: Class A preparation

Class A is the default scope for a later request to execute this document. These actions add research and navigation only. They leave statuses, dependencies and acceptance checkboxes unchanged. Each action has an idempotent completion condition. If the current owner already states the intended fact, record SKIPPED with its exact section; do not append another copy.

| Action | Target and exact existing heading | Instruction | Acceptance and expected state |
|---|---|---|---|
| A1 | `proposals/distributed-recovery/2026-10-08/context-execution-research.md`, `Context Mode findings` and `Source ledger and discovery receipts` | Add the package/component and 18-row coverage findings with the pin, license and inspected/not-executed distinctions. Record Cursor/Kimi and native Pi/OMP contradictions; cite exact source paths. Keep the full comparison in this owner. | No claim of runtime parity; no package admission. Existing research is expanded once. |
| A2 | Same file, `Execution alternatives` and `Recommendation and owner impact` | Reconcile principles-first reuse, fixed immutable processor, exact stored projection, narrow component/upstream/fork decision and separate portable blocker. Replace incomplete advice rather than adding conflicting recommendations. | Context remains optional; DSR-0.6 stack unchanged; no new executor or full fork recommendation. |
| A3 | `evidence.md`, new dated preparation checkpoint near current preparation records | Record four-role preparation, final bounded review receipt and actual local documentation checks. Reference A1 research owner and this handoff. Preserve source inspection, documentation verification and pending runtime qualification. | No assumption retirement, acceptance completion or architecture approval. Do not write PENDING as PASS. |
| A4 | `plan.md`, `Direction and adoption boundary` or `Preparation` | Add or refine one concise research reference only if the current reference omits its useful boundary. Say processing/projection remain optional and do not block portable work by default. | Prefer no change if sufficient. Do not edit `M1 assumption dispositions`. |
| A5 | `tickets/phase-0.md`, `DSR-0.6 Decide the workspace volume class and the effect isolation level`, `Approved checkpoint architecture direction (2026-10-10)` | Inspect the existing additive research paragraph dated 2026-10-11. Replace only incomplete or contradictory wording with the research reference and optional/deferred boundary. | Prefer no change if already correct; status OPEN, existing block on DSR-2.1 and unchecked criteria retained. |
| A6 | Proposal `README.md`, `Maintained documents` | Refine existing research navigation only if needed to find this preparation and its ledger. Do not introduce another technical contract owner. | Navigation only; proposal still CONDITIONAL and not adopted. |

Do not change canonical `spec.md` for Class A. Its exclusions already prohibit unsupported arbitrary execution and unsafe recovery. Do not edit `canonical-documents.md`, `work-items.md`, ticket `README.md` or `status-map.md` merely to mention a package. Change them only if an actual navigation/work-path fact becomes false, and record that narrow reason. Add no fresh ticket or assumption ID in Class A.

## Documentation ledger: Class B selected protocol and optional integration

Class B is conditional. First reuse existing applicable explicit approvals recorded by the operator or authorized owner. Do not infer new choices from a generic request to execute this document. Execute only the actions those approvals cover, and record which choice authorizes each action. A selection permits documentation preparation; it does not prove acceptance criteria. Preserve current completion states until the owning proof actually passes.

Separate **B-P portable protocol rebaseline** from **B-C optional context integration**. B-P follows the existing approved direction and applicable DSR-0.6 adoption choices. B-C requires explicit artifact/projection/tool admission selection and can remain deferred. Do not attach all B-C work as a dependency of DSR-2.1 merely because it appears in this document.

| Action and owner | Target with exact heading | Selected documentation change | Gate and expected disposition |
|---|---|---|---|
| B-P1, DSR-0.6/0.8/0.11 | `tickets/phase-0.md`, the respective decision headings | Record selected stack/roles/failure envelope, protected authority and retention/reset boundary in current decision notes. Distinguish target selection, complete protocol adoption and rig allowance. | Applicable approval required; no unchecked criterion closes from a recommendation. |
| B-P2, canonical spec | `spec.md`, `Package and filesystem boundary`, `Effect identity, execution and outcomes`, `Timeouts and process lifetime`, `Deployment security, lifecycle and service targets` | Apply selected cold pair/restore, independent authority, result/postimage and terminal-incarnation contract from configuration change map. Remove incompatible shared-volume-only requirements within approved rebaseline. Preserve local guard defense and no redispatch after uncertainty. | Full selected protocol approval; material design review required. |
| B-P3, assumptions | `spec.md`, `Assumptions and risks if wrong` | Reconcile applicable A-17/A-21/A-27/A-37/A-38/A-48/A-59 without deleting/reusing IDs. Record proposed/revised or superseded dispositions and actual proof gate. | Do not alter approved M1 scope by implication; reconcile plan status mirrors if affected. |
| B-P4, implementation owners | `tickets/phase-2.md`, DSR-2.1 through DSR-2.4, DSR-2.6 and DSR-2.7 | Rebaseline approved restore/publish schema, independent admission, exact outcome/postimage, unknown parking, metadata and containment under existing owners. Preserve sequential original pending behavior. | DSR-2.1 remains blocked until applicable DSR-0.6 approval; no implementation. |
| B-P5, lifecycle owners | `tickets/phase-3.md`, DSR-3.3/3.5; `tickets/phase-4.md`, DSR-4.1/4.2/4.3 | Reconcile reset, cleanup/retention, surviving-host replacement, original disk loss and live partition tests. DSR-4.3 currently says `Prove shared volume behavior on two containers over a network file system`; change outcome and references only in the approved route. | Do not close old shared-volume acceptance with an unadopted different rig. |
| B-P6, plan/work mirrors | `plan.md`, `Effects and prepared workspace`, `Workspace and process recovery`, `Hardening and reusable Workflow acceptance`; `work-items.md`, applicable owner headings | Carry selected implementation/evidence order and blocker references. Work-items remain a concise mirror of owning tickets. | Same selected rebaseline; status/dependency map agrees. |
| B-C1, DSR-0.6/0.11 | `tickets/phase-0.md`, respective `Scope`, `Acceptance criteria`, `Dependencies and blockers` | Record internal processor versus custom tool admission, authoritative result/artifact/projection versus disposable index, retention/key/read authorization and license/owner selection. | Explicit optional selection; existing decision ownership retained. |
| B-C2, canonical scope | `spec.md`, `Supported tools and guarantees`, `Recovery state and integration choice`, `Baseline orchestration and interception`, `Package and filesystem boundary`, `Interfaces and later adapter` | State selected seam, unchanged raw/native fields and optional guarantees. An internal processor need not admit a general MCP tool. Do not widen other engines or native child/parallel support. | Explicit scope/projection/policy adoption; unselected exclusions retained. |
| B-C3, DSR-2.1/2.3 | `tickets/phase-2.md`, `Prepare the per run workspace, claims directory, manifest, counters and effect identity state`; `Map every effect outcome by the ordered table and the executor fault` | Add selected artifact/projection/version identities and lost publication cases to approved manifest/outcome criteria. Rebuilding an index cannot recover accepted bytes or imply NOT_RUN. | Optional selection plus portable prerequisite if applicable. |
| B-C4, DSR-2.2/2.4 | Same file, `Run Bash as a claimed effect with the spawn guard`; `Run Write and Edit as repeatable effects` | For selected opaque execution/native transformation only: retain one attempt, guarded identity and native bookkeeping. Never classify arbitrary script writes as repeatable native Write/Edit. | Tool/outcome selection required; Q-8/fidelity proof pending. |
| B-C5, DSR-2.6 | Same file, `Match engine behavior by differential test` | Own raw/accepted result, original identity/status/metadata, absence/unload and replacement recovery tests Q-3/Q-4/Q-5. Specify exact accepted representation before acceptance. | Fidelity owner; source inspection does not replace native proof. |
| B-C6, DSR-2.7 | Same file, `Contain process trees, cancellation, shutdown and payload size` | Add selected descendants, partial/background negatives and separate model input, history payload and Worker memory limits. | Runtime selected; Q-1/Q-4/Q-7 unexecuted until authorized. |
| B-C7, DSR-3.3/3.5 | `tickets/phase-3.md`, `Park runs and apply the retry, checkpoint resume and abort actions`; `Prove reset behavior for the lineage id and claim files` | Missing definitive result or required projection parks. Restored index/snapshot cannot replace authority or permit checkpoint resume. | Selected integration only; logical identity/reset contract retained. |
| B-C8, DSR-4.1/4.2 | `tickets/phase-4.md`, `Isolate effects at the decided level`; `Remove run directories safely and detect a restored snapshot` | Qualify processor capability denial; indexes are cache. Preserve referenced full artifacts/projections and sole-readable cleanup rule. | Selected integration; Q-1/Q-7/Q-13 pending. |
| B-C9, DSR-5.4/5.6 | `tickets/phase-5.md`, `Prove session store conformance`; `Run the daily newest engine job and the engine upgrade resume test` | Add retained record/projection authorization and lost acknowledgement; bind selected package/runtime/type identities. | No Docs-only version floor; Q-2/Q-3/Q-5/Q-6 pending. |
| B-C10, later harness | `tickets/phase-7.md`, `DSR-7.2 Port the integration to the agent harness`, `DSR-7.3 Name the owner of the effect ordinal and key for the harness port` | Reference selected Code Mode component; name runner/VFS/tool/event dependencies and single identity owner. Preserve post-PASS/upstream/glue gate and dependencies. | Adapter adoption required; broader harness changes need explicit boundary revision. |
| B-C11, native extensions | Same file, `DSR-7.4 Select a testable durable child and parallel tool design` | Add reuse reference if useful. Preserve positive child/batch identity, correlation, conflict, partial failure and descendant proof. | Denial/serial proof cannot close positive outcomes. |
| B-C12, mirrors | `plan.md`, applicable preparation headings and `Upstream and harness adapter`; `work-items.md`, `Prepared workspace and effect identity`, `Ordered outcomes and refusals`, `Tool behavior fidelity`, `Process and payload bounds`, `Session storage conformance`, `Harness adapter` | Update concise selected references to owning tickets. Keep optional work separate and no duplicate specification. | Selected lane only; no M1 re-opening or automatic blocker. |

DSR-2.9, DSR-4.5, DSR-5.9 and DSR-6.1 through DSR-6.4 keep their phase/assumption/independent PASS gates. Reconcile references when selected scope changes proof inputs. Do not advance status or inherit a candidate verdict for changed claims.

## Candidate package and transitive consistency

The maintained candidate consists of exactly four files: `candidate/spec.md`, `candidate/plan.md`, `candidate/evidence.json` and `candidate/plan-evidence.json`. Markdown Evidence sections are inside the spec and plan. There is no `candidate/evidence.md` or `candidate/plan-evidence.md` edit target.

For a selected correction, place requirements under candidate `Interfaces` / `Optional Mods capability lanes` and applicable existing constitution/assumption rows. Place qualification under candidate plan `Milestones` and `Verification handoff`. Preserve A-71 through A-73 for applicable Mods conditions, A-70 for confidential execution and A-74 for complete response escrow. Clarify existing processing/state rows only when their actual scope covers the condition; do not force an unrelated assumption to absorb it.

Do not change frozen captures or historical verdicts. Material maintained candidate changes require a new `verify-design` result. Do not claim that an earlier verdict covers changed claims. Class A can leave the candidate untouched.

`check_planning.py` enforces 59 canonical assumption IDs, fourteen bounded M1 dispositions, fifteen candidate assumptions A-60 through A-74, six Open BD decisions and EV-1 through EV-46 in both candidate Evidence tables and JSON manifests. All existing IDs and equivalent Markdown/JSON fields must stay aligned.

Class A must not expand those inventories. If a selected change needs a new assumption/evidence row or an Answered BD state, report checker/test transitive impact before applying it. Reuse owner prose when sufficient. If broader scope is approved, update meaningful checker expectations and tests for the authorized transition, preserving stable old IDs and negative protections. Never remove assertions or mark decisions Open again merely to obtain green. This handoff does not authorize checker source/test edits under default documentation-only execution.

## Source ledger and evidence classification

Repository pins identify inspected source, not selected installed runtimes. Live Docs need a fresh check against emitted types before runtime selection. The research owner has full source receipts, discovery queries and rejected alternatives; reuse it before repeating searches.

| Source | Exact source or maintained owner | Role and limit |
|---|---|---|
| C-1 | https://github.com/mksglu/context-mode/tree/abb104847cbb66c2182816a72bb69455bc778b5e | Source behavior, package `1.0.169`, Node at least `22.5`; no execution qualification |
| C-2 | https://github.com/mksglu/context-mode/blob/abb104847cbb66c2182816a72bb69455bc778b5e/LICENSE | Elastic License 2.0; owner/license fit unresolved |
| C-3 | C-1 `src/adapters/types.ts`, `client-map.ts`, individual adapters; `docs/platform-support.md`, `README.md` | Capability/integration claims and source/document contradictions |
| C-4 | C-1 `skills/context-mode/SKILL.md`, `skills/context-mode/references/`, `skills/ctx-*/SKILL.md`, `configs/` | Packaging/routing evidence, not an accepted durable Skill |
| C-5 | C-1 `src/executor.ts`, `src/server.ts`, `src/store.ts`, `src/session/snapshot.ts`, `hooks/core/routing.mjs`, `hooks/platform-bridge.mjs` | Process/cache/guidance/optional analytics limits |
| C-6 | C-1 `tests/adapters/`, `tests/integration/` and package test inventory | Test definitions inspected, not run; no complete platform proof |
| T-1 | https://docs.temporal.io/activity-execution and https://temporal.io/blog/idempotency-and-durable-execution | Attempts/cancellation/atomic receiver idempotency; no physical exactly-once guarantee |
| T-2 | https://docs.temporal.io/child-workflows and https://docs.temporal.io/design-patterns/entity-workflow | Logical ownership precedent, not OS containment or native child recovery |
| T-3 | https://docs.temporal.io/develop/python/activities/asynchronous-activity | Async delivery, not job death |
| H-1 | https://github.com/temporal-community/temporal-agent-harness/tree/30b0c7f0affb0629cac4c846d0cb88589571e484 and https://github.com/temporal-community/temporal-agent-harness/pull/19 | MIT, package `0.6.0`, Experimental / Pre-Alpha; restricted component reference |
| H-2 | https://github.com/temporalio/ai-integrations/tree/7d2197d42c86be1f20f53b766e142f151f2ff873/python/openai_agents | MIT owner; sandbox Pre-release within GA parent; not Claude materializer |
| H-3 | https://github.com/temporal-community/sandbox-orchestration-harness/tree/a3d2194e600f9b9018efbc43d8edc1d3082c0d74 | MIT lifecycle reference; ACK/retry/autoresume limits |
| H-4 | https://github.com/temporalio/samples-python/tree/b0e4d843ed49a647b5fcd1e18453ab1d048ba857 | MIT mechanism samples, not portable pair/death proof |
| M-1 | https://github.com/anthropics/claude-code/blob/3deb873687379f0c199a69fdaccc65f0865f7a29/mods/types/claude-code.d.ts | Early access CLI `2.1.277`; SHA256 `e1c060069af2d494fc884e03f136ed0b3ddaa0eb5341e72e3acd712e5f637c49` |
| M-2 | https://code.claude.com/docs/en/plugins/mods/reference and https://code.claude.com/docs/en/plugins/mods/events | Live 2026-10-11 observations, not installed activation |
| M-3 | https://code.claude.com/docs/en/plugins/mods/admin , https://code.claude.com/docs/en/plugins/mods/api , https://code.claude.com/docs/en/plugins/mods/test and https://code.claude.com/docs/en/plugins/mods/troubleshoot | Failure/capability/stub evidence; runtime tests not run |
| R-1 | [Research](context-execution-research.md), `Source ledger and discovery receipts` | Full 16-source comparison, blogs, tool receipts and historical distinction |
| R-2 | [Mods synthesis](mods-synthesis.md), [storage synthesis](storage-loop/synthesis.md), [Issue 31 coverage](priority-sweep/coverage.md) | Qualification limits and complete discussion outcomes |
| R-3 | [Configuration](dsr-0.6-configuration.md) and [preparation](dsr-0.6-preparation.md) | Proposed stack/change map/ordered acceptance; pending owner choices |

C-1 assertions are `current_behavior` at the inspected pin; host capabilities are `conditional` where runtime delivery is absent or contradictory. T-1 through T-3 are `product_constraint`/mechanism precedent. SDK/order/parking/cleanup rules are `requirement_or_decision`. Processing, adapters and stack details are `proposed_design` or `recommendation`. License fit/runtime selection are `open_decision` or `assumption`. Q rows are proof obligations, not confirmed evidence.

Fixed artifact Activities and restricted host calls have partial precedent. This review found no sanctioned complete composition of original Claude pending recovery, immutable portable workspace pair, protected authority and independent physical termination. This is pending project qualification, not a missing Temporal primitive or a demonstrated production pattern.

## Future agent execution procedure

1. Read Git status, HEAD/remotes, repository/ancestor instructions and this document. Preserve pending files. Resolve owning fork and scope. Discover scoped skills/configuration without activating untrusted hooks/plugins.
2. Read canonical owners, current tickets and maintained proposal. Recheck digests/headings, pins and approvals. Reconcile changed baselines; never reset/checkout/restore old bytes.
3. Produce a ledger with action ID, exact target, current equivalent text, applicable authorization, intended diff and expected state. Use APPLIED, SKIPPED (already satisfied), DEFERRED (unselected) or BLOCKED (exact missing approval/evidence).
4. Apply Class A by default through visible edits. Merge into owning paragraphs; do not add duplicate authority or assumption/evidence IDs merely to place research.
5. Apply Class B only with applicable explicit approval. Keep B-P independent from unselected B-C. Execution of this document does not select all alternatives.
6. Check selected ticket/work-item/plan mirrors and candidate four-file consistency. Disclose checker transitive scope and hold it pending approval. Never weaken gates or rewrite history to hide drift.
7. Run installed documentation/conventions checks with synchronization disabled. Missing tooling is pending verification, not installation permission. Review exact diff for statuses, history, unsupported claims and portable paths.
8. Use `verify-design` for material design changes; record exact target/digest/scope and open choices. Documentation verification does not qualify a provider/runtime/platform matrix.
9. Report action receipts, changed files, deferred scope, actual checks and one next action. Do not commit or push from this document alone.

Resolve `REPO_ROOT` from the selected checkout for these commands. It is task configuration, not a system option. Use absolute resolved paths. Do not invoke `make sync`, bare `uv run` or `--frozen`.

```bash
python3 "$REPO_ROOT/python/claude_agent_sdk/docs/skill-recovery/check_planning.py"
env UV_NO_SYNC=1 UV_OFFLINE=1 UV_NO_EDITABLE=1 uv run --project "$REPO_ROOT/scripts" --locked python "$REPO_ROOT/scripts/ci/check_conventions.py"
git -C "$REPO_ROOT" diff --check
git -C "$REPO_ROOT" status --short
git -C "$REPO_ROOT" diff --stat
```

Planning checks current owners, fixed inventories, status boundaries, references and preservation/diagram receipts. It does not prove runtime behavior or live URL freshness. Conventions prove repository shape. No full suite rerun or hosted CI is claimed by these commands.

## Sequential review record and lead reconciliation

The user selected four sequential roles with full conversation/prior research context: reuse/parity reviewer, contract/adversarial reviewer, writer and final verifier. Each reports to the lead. These are separate agents with shared context, not blind reviews. The writer reconciles both reviews; the final verifier checks this artifact; the lead owns corrections and final receipt.

The reuse reviewer identified artifact/retrieval, adapter and diagnostic reuse, but no qualified parity. It recorded Elastic licensing, routing skill drift, advisory MCP routing, optional analytics and native Pi/OMP paths. The contract reviewer required exact accepted projections, independent prevention, preserved Phase 1, optional gates and synchronized candidate/checker inventories. Both required bounded qualifications, not architecture approval. Each recorded one successful Temporal Docs call and one Atlas wrapper query, with no third party execution or edits.

The lead corrected target errors before writing: research heading `Context Mode findings`, DSR-7.2 title `Port the integration to the agent harness`, and four candidate files with embedded Evidence tables rather than standalone Evidence Markdown. This ledger uses actual headings/inventory. A reviewer suggestion is not authoritative by itself.

Writer receipt: created this file through a visible patch. No ticket, canonical spec/plan, index, runtime, checker, test or historical artifact changed. Preserved 14 existing pending files. Reused owner source and both reviewer reports. Writer successful Temporal Docs calls: zero. No new external search, live model, installation, credential read, provider execution, external contact, commit or push.

Final verification receipt (2026-10-11): PASS for bounded documentation preparation. The fourth agent found no material factual or contract defect. Architecture and runtime qualification remain CONDITIONAL because the named choices and proof gates remain open. The lead applied one approval wording clarification in Class B; the final verifier read it and confirmed that it resolves the finding. No runtime, ticket or architecture approval follows.

The verifier checked the full draft, exact owner headings and titles, all nine recorded owner digests, pinned primary adapters/skill/license, preserved statuses and qualification boundaries. Planning passed with 1,229 local references. Synchronization-disabled repository conventions passed. Explicit checks covered new-file whitespace as well as the tracked diff; the Unicode check found no prohibited dashes. The lead compared 42 existing owning Markdown/JSON files against the starting hashes: all were unchanged. Git status contained the original 14 pending files plus only this new handoff. No index, existing ticket/spec/plan or historical artifact changed.

Fresh source access has a bounded tooling limitation. The verifier's combined Atlas query failed because the query script contained an unresolved merge marker. Its lookup alternative failed because prepared query dependencies were unavailable. The permitted read wrapper successfully read `code/sdk-python/temporalio/activity.py`, exit 0. Earlier lead and reviewer query receipts remain valid. No Atlas repair or installation was attempted. The verifier made one successful Temporal Docs call; together with one call by the lead and each reviewer, this pass has four calls. The writer made zero.

The design manifest gate passed, exit 0, with `status: complete`. That status describes the declaration gate only. The automated proof check returned exit 0 with `proof-of-load: disclosed`; all four applied rows were `not-proven`. It did not resolve the Codex and agent transcripts, and it does not check the cited external precedent URLs. The manifest declaration is the only automated enforcement for those rows in this run; visible reads, returned tool results and agent receipts supply the manual record. Do not present this as machine-proven skill loading or runtime qualification.

The following gate disclosures and proof warnings are retained unchanged:

disclosure: The Temporal design review was installed and applied (discovered as `temporal-workflow-design-critic`, invoked by context_contract_review) and returned findings cited at Retained data and native result projection, Temporal execution choices and failure boundaries, Candidate package and transitive consistency.

disclosure: Temporal product and SDK behavior claims were grounded through Temporal Docs (4 successful connector calls across lead, context_reuse_review, context_contract_review, context_handoff_verify).

disclosure: Composed Temporal mechanisms were classified against precedent by lead: Fixed artifact processor with retained exact accepted projection is partial precedent (source https://docs.temporal.io/activity-execution); Restricted interpreter with registered host calls in the Claude SDK path is partial precedent (source https://github.com/temporal-community/temporal-agent-harness/tree/30b0c7f0affb0629cac4c846d0cb88589571e484); Identified external job with atomic submission and retained outcome is partial precedent (source https://temporal.io/blog/idempotency-and-durable-execution); Protected independent Entity dispatch authority across reset and restoration is partial precedent (source https://docs.temporal.io/design-patterns/entity-workflow); Exact accepted conversation workspace pair with independent physical termination is no precedent found (source https://docs.temporal.io/activity-execution).

disclosure: The Temporal developer skill was installed and applied (discovered as `temporal:temporal-developer`, invoked by lead) and returned findings cited at Authority and preserved dispositions, Temporal execution choices and failure boundaries.

warning: temporal-design-review is unproven (no transcript supplied for role context_contract_review; pass --role-transcript context_contract_review=<path>); the manifest declaration is the only enforcement for it

warning: temporal-docs-grounding is unproven (0 of 4 declared calls observed; lead: harness codex but the session transcript could not be resolved (unavailable); pass --transcript; context_reuse_review: no transcript supplied for role context_reuse_review; pass --role-transcript context_reuse_review=<path>; context_contract_review: no transcript supplied for role context_contract_review; pass --role-transcript context_contract_review=<path>; context_handoff_verify: no transcript supplied for role context_handoff_verify; pass --role-transcript context_handoff_verify=<path>); the manifest declaration is the only enforcement for it

warning: pattern-precedent is unproven (no atlas:// source to resolve; Temporal Docs and external sources are not checked); the manifest declaration is the only enforcement for it

warning: temporal-developer is unproven (harness codex but the session transcript could not be resolved (unavailable); pass --transcript); the manifest declaration is the only enforcement for it

### Embedded design review manifest

This is run bookkeeping inside the requested single document. The same manifest was gated from session scratch; no JSON sidecar was added to the repository. The draft identity refers to the reviewed body before the bounded approval clarification and this receipt. The final verifier separately checked that clarification. The source and design verdict remain conditional.

```json
{
  "schema_version": 1,
  "verdict": "CONDITIONAL",
  "target_identities": [
    "design-base HEAD 4553c340ed4ba8477de09af4888bd00008db8e41 plus preserved preparation worktree",
    "Context Mode source abb104847cbb66c2182816a72bb69455bc778b5e",
    "Handoff draft SHA256 545b1b4dc3f1edaaff60cc0e5e4be8f998857a3cd3ea38c88877bc8e8ee555c1 before approval wording correction"
  ],
  "reviewers": [
    {
      "reviewer": "temporal-design-review",
      "applicability": "applicable",
      "applicability_basis": "Activity effects, exact recovery state, ownership, cancellation and retention claims in a documentation handoff",
      "outcome": "applied",
      "discovered_as": "temporal-workflow-design-critic",
      "invoked_by": "context_contract_review",
      "finding_refs": [
        "Retained data and native result projection",
        "Temporal execution choices and failure boundaries",
        "Candidate package and transitive consistency"
      ]
    },
    {
      "reviewer": "temporal-docs-grounding",
      "applicability": "applicable",
      "applicability_basis": "Temporal execution and cancellation constraints support the edit plan",
      "outcome": "applied",
      "call_count": 4,
      "roles": [
        "lead",
        "context_reuse_review",
        "context_contract_review",
        "context_handoff_verify"
      ]
    },
    {
      "reviewer": "pattern-precedent",
      "applicability": "applicable",
      "applicability_basis": "Proposed artifact processing, host calls, remote jobs and authority compose Temporal mechanisms",
      "outcome": "applied",
      "invoked_by": "lead",
      "classifications": [
        {
          "mechanism": "Fixed artifact processor with retained exact accepted projection",
          "classification": "partial",
          "source": "https://docs.temporal.io/activity-execution"
        },
        {
          "mechanism": "Restricted interpreter with registered host calls in the Claude SDK path",
          "classification": "partial",
          "source": "https://github.com/temporal-community/temporal-agent-harness/tree/30b0c7f0affb0629cac4c846d0cb88589571e484"
        },
        {
          "mechanism": "Identified external job with atomic submission and retained outcome",
          "classification": "partial",
          "source": "https://temporal.io/blog/idempotency-and-durable-execution"
        },
        {
          "mechanism": "Protected independent Entity dispatch authority across reset and restoration",
          "classification": "partial",
          "source": "https://docs.temporal.io/design-patterns/entity-workflow"
        },
        {
          "mechanism": "Exact accepted conversation workspace pair with independent physical termination",
          "classification": "none_found",
          "source": "https://docs.temporal.io/activity-execution"
        }
      ]
    },
    {
      "reviewer": "temporal-developer",
      "applicability": "applicable",
      "applicability_basis": "Deterministic orchestration versus external Activity execution and original call identity",
      "outcome": "applied",
      "discovered_as": "temporal:temporal-developer",
      "invoked_by": "lead",
      "finding_refs": [
        "Authority and preserved dispositions",
        "Temporal execution choices and failure boundaries"
      ]
    }
  ]
}
```

Documentation preparation is complete for this handoff. The single next operator action remains selection or replacement of the first portable qualification stack. Context processing and a fork can remain deferred. A later documentation execution must use the action ledger and preserve all stated gates.
