# Local Enterprise login preparation

This container prepares operator authentication for bounded local real model proof. It supplies no production login integration, recovery store or effect executor. The launcher has no model execution command. Budget decisions, harness enforcement and separate model execution authorization remain required.

## Authentication boundary

Anthropic's [Agent SDK subscription notice](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan) states in its June 15 update that the announced credit changes are paused and SDK usage still draws from subscription usage limits. The historical credit table below that update is not current policy. The [CLI reference](https://code.claude.com/docs/en/cli-reference) documents `claude auth login` and `claude auth status`. Account entitlement, organization policy and compatibility with the pinned CLI still require an actual operator login. Login success alone does not prove a model request or recovery.

The selected local proof route is an operator Enterprise Claude login, performed inside the container. Do not copy host credentials or use `setup-token`. The named Docker volume `claude-recovery-proof-login` retains the container home and login state after a container exits. It is private local state, not an evidence artifact. Login uses normal bridge networking; offline checks and status use no networking. This is process/filesystem separation for a local test, not a production security proof or a network egress allowlist.

The container runs as UID 1000 with dropped capabilities, no additional privileges, a read only image and bounded writable temporary directories. It mounts neither the Docker socket, the host home nor the repository. The launcher passes no host environment values. The base image and installed package tree are copied as existing artifacts, not installed or updated during the build. The image contains the SDK and pinned CLI; the login volume is only attached for login/status.

## Preparation

Use an existing full base image SHA-256 identity, the existing Python 3.13.15 runtime directory, the verified experimental environment's installed `site-packages`, and the unchanged bundled CLI. The launcher copies these into a temporary build context and removes that exact context after the build. It tags the existing base locally because Dockerfile `FROM` does not accept a raw local image ID. It runs no package resolver. Image tags are local conveniences, not provenance; record the resulting image ID before using it.

```sh
python3 login_container.py build --base <existing-full-image-id> --runtime <python-runtime-directory> --packages <verified-site-packages-directory> --cli <pinned-cli>
python3 login_container.py check
```

The check verifies nonroot execution, Python/SDK versions, CLI hash, SDK recovery and plugin imports. It prints CLI version and login command help without networking or credential mounts. It performs zero model calls. Version strings and successful imports do not replace SDK source/wheel provenance verification.

## Operator login

From an interactive terminal, run the following commands using the launcher's actual path:

```sh
python3 login_container.py login
python3 login_container.py status
```

Complete the browser authorization for the intended Enterprise organization. If the container cannot open a browser, open the displayed login URL yourself and follow the CLI prompts. Keep authorization URLs and codes out of evidence and chat. Status prints only login state, authentication method and provider; raw account identifiers and command output are withheld.

The next harness stage must enforce a fixed model and bounded request/turn/time limits without automatic retry or extra usage fallback. Subscription usage does not by itself prove USD/token cap enforcement. Any proposed substitute for the existing API spend acceptance needs an explicit recorded decision. Original budget and real model criteria remain open until fulfilled or explicitly rebaselined; this setup closes none of them.

The login volume is retained until the operator chooses to log out and remove it. Do not automatically delete login state or alter the operator's normal host login. No model test runs as part of build, check, login or status.

## Proposed first connectivity check

[connectivity_plan.py](connectivity_plan.py) prints the proposed command and limits without executing it. It selects exact model `claude-haiku-4-5-20251001`, listed in the current [official model overview](https://platform.claude.com/docs/en/models/overview). The prompt asks only for `CONNECTIVITY_OK`; the proposal uses one turn, no tools/skills/MCP, no persisted session, a 64 output token setting, a USD 0.05 CLI budget setting and a zero API retry setting. The pinned binary contains the retry control and advertises the relevant tool/model/output settings; the [official CLI reference](https://code.claude.com/docs/en/cli-reference) documents turn and budget semantics. Binary inspection is not a runtime enforcement proof.

The execution procedure, if approved, must enforce a 60 second outer timeout, kill/remove the named test container on timeout or failure, retain complete output and stop without retry or fallback. The proposed command alone does not enforce that outer timeout. Login state remains retained. Any extra usage/quota/model refusal stops the check; no billing settings are changed. The operator must explicitly approve this single subscription connectivity check as a bounded exception to the original API budget gate. It does not replace USD/input-token/phase cap proof or permit a recovery experiment batch. No model call is authorized merely by printing the plan.

The operator approved this single test on 2026-10-02. [connectivity_run.py](connectivity_run.py) implements the execution procedure with a unique container name, one process launch, timeout/teardown and complete stdout/stderr/plan/report writes to a new private system temporary directory. It is a model execution command and must not be included in offline checks or rerun without execution authorization. The [result](../evidence.md#subscription-cli-connectivity-2026-10-02) passed connectivity only; authorization covered this invocation, not a subsequent batch or replacement of the original budget criteria.
