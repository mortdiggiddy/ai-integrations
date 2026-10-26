# Confidential native agent runtime on Temporal

This fork is the project home for confidential native agent execution with outside Temporal orchestration. The [active project package](docs/confidential-agent-runtime/README.md) owns the prepared specification, plan, decisions, obligation mapping and evidence.

The selected direction keeps the native Claude SDK and CLI inside the approved runtime. Outside Workers carry sealed service operations and approved metadata. The Sandbox Orchestration Harness owns compute lifecycle. General SDK and lifecycle contributions remain separate from this project's content policy, keys and recovery adapters.

## Project status

The document cutover and formal `spec-driven-temporal` pass are complete. The [independent design review](docs/confidential-agent-runtime/verification-report.md) returned CONDITIONAL with no material core or remedy findings. This is not a qualified runtime or a production release. Open owner decisions remain explicit, including the recovery guarantee, external effect authority and preventive spending policy.

- [Specification](docs/confidential-agent-runtime/spec.md): requirements and acceptance boundaries.
- [Plan](docs/confidential-agent-runtime/plan.md): small delivery slices and activation gates.
- [Decisions](docs/confidential-agent-runtime/decisions.md): unresolved owner choices.
- [Obligation map](docs/confidential-agent-runtime/obligation-map.md): disposition of earlier requirements, assumptions and tickets.
- [Evidence](docs/confidential-agent-runtime/evidence/README.md): extracted research, source pins and qualification limits.

The earlier governed skill recovery effort is [archived in place](python/claude_agent_sdk/docs/skill-recovery/ARCHIVED.md). Its source, fixtures, experiment results and historical ticket states remain available at their original paths. They do not define the active architecture or prove the replacement runtime.

## Upstream integration collection

This fork retains the upstream repository layout and the other integrations. The catalog and development conventions below describe that collection, not completed skill recovery features or a release of this fork's changes.

Plugins that connect AI agent frameworks and SDKs to [Temporal](https://temporal.io) durable
execution. Each plugin is its own package with its own dependencies, tests, version and release
cadence, laid out as `<language>/<integration>/`.

| Plugin | Package | Root API | Maturity |
|---|---|---|---|
| [`python/claude_agent_sdk`](python/claude_agent_sdk) | [`temporalio-claude-agent-sdk`](https://pypi.org/project/temporalio-claude-agent-sdk/) | `temporalio.claude_agent_sdk` | Experimental |
| [`python/mcp`](python/mcp) | [`temporalio-mcp`](https://pypi.org/project/temporalio-mcp/) | `temporalio.mcp` | Experimental |
| [`python/openai_agents`](python/openai_agents) | [`temporalio-openai-agents`](https://pypi.org/project/temporalio-openai-agents/) | `temporalio.openai_agents` | GA |

More plugins are migrating here from the SDK repositories; see the target table in
[`AGENTS.md`](AGENTS.md).

## Install

```
$ uv add temporalio-claude-agent-sdk
$ uv add temporalio-mcp
$ uv add temporalio-openai-agents
```

## Develop

```
$ cd python/openai_agents
$ make sync    # non-editable install into .venv (see AGENTS.md for why)
$ make lint
$ make test    # provider calls use deterministic local models and transports
```

`make help` lists every target. Conventions, CI design, release process and migration procedure
are in [`AGENTS.md`](AGENTS.md); contributor workflow is in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

[MIT](LICENSE). Each plugin directory carries an identical copy so every published package ships the license text.
