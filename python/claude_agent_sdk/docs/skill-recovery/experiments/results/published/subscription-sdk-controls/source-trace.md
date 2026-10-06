# Pinned CLI and SDK continuation trace

Date: 2026-10-02. Method: read only static inspection of the existing CLI binary and experimental SDK source. No model call, login mount, credential read, dependency sync or completed experiment rerun occurred. The CLI SHA256 was verified as `15e2d05148f801b5774032faad87e624ecd172e9903288bda448b892eb58fa07`, matching CLI `2.1.274` in the retained image. Byte offsets below are zero based positions in that binary's embedded minified JavaScript, not public source line numbers or supported API promises. Independent source investigation supplied this trace.

## Observed result

The unchanged [failed stream](../subscription-sdk-query/stream.jsonl) contains three generated continuation UserMessages and a final error with four reported turns. One host admission supplied one original prompt. Aggregate usage is 2,100 input/256 output tokens, of which 244 output tokens are thinking. Two AssistantMessage blocks share the first provider message ID and its usage; summing each emitted block would double count that request. The final usage is the recorded aggregate. Exactly four provider requests is not independently established by four CLI turns or four distinct provider message IDs: auxiliary calls, internal retry handling and provider admission are not independently recorded.

## Pinned source interpretation

| Binary byte offset | Source fragment or named branch | Finding |
|---|---|---|
| 204186724 | `var xc=3;` | Output-limit recovery has a separate fixed three-attempt allowance. |
| 204195173 | `function xS(h){return h?.type==="assistant"&&h.apiError==="max_output_tokens"}` | Recognizes output-limit errors. |
| 204248493 | `if(MS(so,Pn),tt!==void 0&&(xS(tt)||cl)){let fo=cl?Pt:Pt+1;if(fo<=xc){` | Recovery branch precedes the later tool recursion turn check. |
| near 204249016 | `maxOutputTokensRecoveryCount:fo` and `turnCount:ni`, followed by recovery `continue` | Advances the recovery counter while retaining the internal turn counter. This is consistent with the observed three continuations despite `max_turns=1`. |
| 204259907 | `_d=ni+1,Sd=Me&&_d>Me?Me:void 0` | Later tool followup branch computes the maximum-turn guard. |
| near 204262770 | `max_turns_reached` | This guard is reached after the earlier recovery branch, which can continue first. |
| 197359638 | `function uot()` reads `CLAUDE_CODE_MAX_RETRIES` | API retry selection is separate from output-limit recovery. Zero API retries does not disable this continuation loop. |
| 191283897 | `h_t` continuation prompt | Matches the generated messages in the archived stream. |
| 199357707 and terminal API error path after recovery | `qve`, `StopFailure` | The hook runs after recovery exhaustion for this path. It cannot prevent the first continuation; its outputs are ignored. |

No configurable count or skip flag was found in this specific output-limit branch. A `tengu_truncated_response_recovery` feature gate controls a different branch and does not disable `xS(tt)` recovery. This is a bounded pinned-source search conclusion, not proof that every hidden setting or future version behaves identically. Do not alter the binary or invent a private flag for the next proof.

## Earlier observation and shutdown

At byte 197441753, `max_tokens` handling creates an output error and subsequently yields the raw `message_delta` stream event before returning to query recovery. The print adapter near byte 211492000 forwards stream events when partial output is enabled. In SDK source `3ac4b25733d1302c89d0dadd13cab268e64d1213`, `src/claude_agent_sdk/_internal/transport/subprocess_cli.py` adds `--include-partial-messages`, and `src/claude_agent_sdk/_internal/message_parser.py` preserves the raw event in `StreamEvent`. Setting `include_partial_messages=True` therefore provides a candidate earlier observable `event.delta.stop_reason=max_tokens` signal. The original invocation did not enable this option. A mocked raw event is not a measured live stop.

The public [Python reference](https://code.claude.com/docs/en/agent-sdk/python) distinguishes `ClaudeSDKClient.interrupt()` from `query()`, which exposes no interrupt method. The pinned client interrupt sends a control request; it is not a provider admission fence. Pinned transport `close()` waits up to five seconds for graceful EOF shutdown, then five after TERM and five after KILL. Async generator loop exit alone does not synchronously close all nested generators. Internal client `process_query()` explicitly closes its inner generator in `finally`, but the public `query()` wrapper itself uses an async loop without explicitly closing that client iterator. Closing the outer query generator is best effort cleanup, not independent proof that all nested transport state closed. Host container removal remains the immediate containment authority.

For an immediate host reaction, issue owned container force-removal on the first parsed stop trigger before reading another record; do not wait for cooperative interrupt/disconnect. A separate deadline must also cover blocked reads and cleanup failures. CLI stdout production, SDK message delivery and host receipt are asynchronous. None supplies an acknowledged pre-request gate. Even earlier streaming detection and successful removal cannot guarantee zero next requests, cancel work already admitted by the provider, reverse token consumption or verify subscription/extra billing. Missing final accounting remains unknown and reserved. This trace motivates the [new proposal](../../subscription-control-proposal.md), not preventive currency/token/aggregate acceptance.
