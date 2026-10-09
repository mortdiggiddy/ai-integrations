# Pinned Mods declarations capture

Retrieved 2026-10-08 by HTTPS read only. Source: https://raw.githubusercontent.com/anthropics/claude-code/52c76441cae91f6891e4712306bffb057ff6fec5/mods/types/claude-code.d.ts

Full response SHA-256: `8ae1244d19d4b393261605fe72d517b66be0d7e1c214c378cdec5107e8b0b46c`; bytes: 507444; lines: 13186.

Selected source-code excerpts; original line numbers are retained. This is the 2.1.277 generated contract, not an installed 2.1.287 contract. No runtime probe was executed.

```typescript
1: // Written by Claude Code 2.1.277.
2: // Claude Code function hooks: the plugin API's TypeScript declarations.
3: //
4: // EARLY ACCESS: this surface may change between releases without notice.
5: // Written by `/plugin-types`; regenerate with that command after an update
6: // rather than editing. The first line names the Claude Code version that
7: // wrote it. TypeScript 5.4 or newer reads it. `claude plugin validate <dir>`
8: // is the other half: it reads a plugin's manifest and its hooks module's
9: // source the way the engine will and reports what the module hooks and
10: // calls and everything the engine would refuse, before any session loads it.
875:   /**
876:    * The handler `on(...).catch(handler)` takes for a hook of type `F`: the
877:    * hook's `($, e, next)`, run afresh when it throws, misreturns or overruns.
878:    *
879:    * `next` carries `error` and `called` (Caught) and is replay-safe; a return
880:    * within the grace is the hook's result, `undefined` the hook absent. On a
881:    * streaming event the handler is a generator too, continuing the stream.
882:    */
883:   export type CatchHandler<F> = F extends ($: infer D, e: infer E, next: infer N) => infer R ? [R] extends [AsyncGenerator<unknown, unknown, unknown>] ? ($: D, e: E, next: N & Caught) => R : ($: D, e: E, next: N & Caught) => R | undefined | Promise<Awaited<R> | undefined> : never;
884:
885:   /**
886:    * What `next` carries into a `.catch` handler and nowhere else: why the
887:    * hook failed, and whether it had called `next` before it did.
888:    *
889:    * There `next` is replay-safe: when `called`, `next(e)` resolves to what the
890:    * hook's last call settled to, nothing beneath running again, the argument
891:    * unread; when not, it runs the hooks beneath once and a later call replays.
892:    */
893:   export type Caught = {
894:       /**
895:        * Why the hook failed (HookFailure); undefined on an ordinary hook's
896:        * `next`, so its presence says a handler is running.
897:        */
898:       readonly error: HookFailure;
899:       /**
900:        * True when the failed hook had called `next()` or `next.to()` at least
901:        * once, settled or in flight; the handler runs once that call settled.
902:        */
903:       readonly called: boolean;
904:   };
2853:       /**
2854:        * This plugin's own key-value store, kept between sessions and hot
2855:        * reloads; values are JSON data.
2856:        *
2857:        * A JSON file of the plugin's own under the user's Claude Code
2858:        * configuration directory.
2859:        */
2860:       store: {
2861:           /**
2862:            * Returns the value under `key`, or `undefined` when unset.
2863:            *
2864:            * @example
2865:            * const count = Number((await $.store.get("count")) ?? 0) + 1
2866:            */
2867:           get: (key: string) => Promise<unknown>;
2868:           /**
2869:            * Sets `key` to `value`, which must be JSON data.
2870:            *
2871:            * `get` reads back `JSON.parse(JSON.stringify(value))`: a Date is its ISO
2872:            * string, an `undefined` field is dropped, a Map or Set is `{}`. Rejects
2873:            * a function, a cycle, or a store over 4 MiB of JSON text in all.
2874:            */
2875:           set: (key: string, value: unknown) => Promise<void>;
2876:           /**
2877:            * Removes `key` from the store.
2878:            */
2879:           delete: (key: string) => Promise<void>;
2880:           /**
2881:            * Returns every key set, in insertion order.
2882:            */
2883:           keys: () => Promise<string[]>;
2884:       };
3235:   /**
3236:    * The events the engine raises at its call sites, and `engine.create`; the
3237:    * classic settings hooks' events are ClassicEventOf.
3238:    *
3239:    * At every one, a hook that fails (throws, overruns its budget: HookBudget,
3240:    * answers a wrong shape) is skipped: the hooks beneath and core run in its
3241:    * place, or its last `next` result stands; the failure is reported by name.
3242:    */
3243:   export type EngineEventOf = {
3244:       /**
3245:        * Fires when the engine is about to run a tool. `next(e)` runs the hooks
3246:        * beneath, then core (the permission prompt, the tool itself).
3247:        *
3248:        * Return `{ deny: reason }` to refuse or `{ result }` to answer yourself; a
3249:        * hook that returns while its `next` is pending aborts what runs beneath.
3250:        * The managed-settings hooks run first: their deny is the call's result.
3251:        */
3252:       'tool.call': ToolCallInput;
3253:       /**
3254:        * Fires when the engine decides whether a tool call may run, after the
3255:        * `tool.call` and PreToolUse hooks and before the mode settles an ask.
3256:        *
3257:        * `next(e)` resolves to the engine's verdict (rules, mode, the tool's own
3258:        * check, PreToolUse's decision); return any `{ decision }`. `$.tool.check`
3259:        * runs the same chain and executes nothing.
3260:        *
3261:        * @example
3262:        * on("tool.check", { tool: "Read" }, () => ({ decision: "allow" }))
3263:        */
3264:       'tool.check': ToolCheckInput;
3540:       /**
3541:        * Fires once per process for each loaded plugin, before the first prompt,
3542:        * then once per fresh load of one (never `/clear`); `next(e)` is `{ cwd }`.
3543:        *
3544:        * Observe. The first is awaited: a `$.tool.register` is listed by turn one.
3545:        * A later one runs its hooks alone: an enable, a worker respawn, or a reload
3546:        * (changed modules only; all if one hooks `engine.create`/`plugin.register`).
3547:        *
3548:        * @example
3549:        * on("session.start", ($, e, next) => $.tool.register(t).then(() => next(e)))
3550:        */
3551:       'session.start': SessionStartInput;
3564:       /**
3565:        * Fires when the conversation is about to be compacted (`/compact`, the
3566:        * threshold, a plugin, or ahead of time); `next(e)` resolves `{ messages }`.
3567:        *
3568:        * Rewrite `instructions` or `messages` on the way down, the messages on
3569:        * the way up, or answer `{ messages }` of your own; `{ skip: reason }`
3570:        * leaves the conversation as it is. `trigger` passes on as received.
3571:        *
3572:        * @example
3573:        * on("session.compact", { trigger: "precompute" }, () => ({ skip: "off" }))
3574:        */
3575:       'session.compact': SessionCompactInput;
3605:       /**
3606:        * Fires once when the session ends (exit, /clear, resume, logout, signal, a
3607:        * `-p` run done), after its SessionEnd settings hooks; `e.reason` says which.
3608:        *
3609:        * `e.resume.id` is `--resume`'s id; `next(e)` runs the engine's end step for
3610:        * the plugins (at an exit the attached clients leave): `{ sessionId }`. The
3611:        * SessionEnd bound afresh, 1.5 s by default; a `kill -9` raises nothing.
3612:        *
3613:        * @example
3614:        * on("session.end", async ($, e, next) => (await keep(e.resume), next(e)))
3615:        */
3616:       'session.end': SessionEndInput;
3629:       /**
3630:        * Fires when a model turn begins, before its first model call; `next(e)`
3631:        * resolves to `{ turnId }`. Observe: a different return changes nothing.
3632:        */
3633:       'turn.start': TurnStartInput;
3634:       /**
3635:        * Fires when the engine is about to send a model request of a turn, main's
3636:        * or a subagent's (`e.agentId`); `next(e)` resolves to the whole response.
3637:        *
3638:        * `next({ ...e, model })` or `effort` sends another; the turn, the index and
3639:        * the message count are pinned. An answer without `next` sends no request.
3640:        * It streams (StreamNext): the hook's budget counts its own code alone.
3641:        */
3642:       'turn.step': TurnStepInput;
3643:       /**
3644:        * Fires when a model turn has ended, at the point its duration is reported;
3645:        * `next(e)` resolves to `{ text }`, the answer. `e.reason` says why.
3646:        *
3647:        * Return `{ text }` with a different text to show it beneath the answer (a
3648:        * synopsis, a TL;DR line); the transcript's record is never rewritten. A
3649:        * hook that fails leaves the answer as it was.
3650:        */
3651:       'turn.complete': TurnCompleteInput;
4217:   /**
4218:    * The time bounds every hook runs under, in milliseconds: the engine's own
4219:    * constants are typed by these members, and `next.budget` reads the live one.
4220:    *
4221:    * Each bounds the hook's OWN time: the clock stops while a `next(e)` call or
4222:    * any `$` call of the hook's is in flight (a `$.clock` wait excepted), so a
4223:    * slow chain beneath or a minute-long `$.model.complete` costs it nothing.
4224:    *
4225:    * @example
4226:    * await $.model.complete(ask) // a minute; next.budget.remainingMs unmoved
4227:    */
4228:   export type HookBudget = {
4229:       /**
4230:        * A hook's budget per dispatch, from its call to its return; past it the
4231:        * hook is absent (its `.catch` asked, else `next(e)` run on its behalf).
4232:        *
4233:        * A streaming hook's (`turn.step`, an async generator) spans its whole
4234:        * run and counts only while its own code runs: never at a `yield`, never
4235:        * while it reads the stream beneath. Not per chunk: the sum of its work.
4236:        */
4237:       readonly ms: 10_000;
4238:       /**
4239:        * A `.catch` handler's grace: a fresh budget from the moment it is called,
4240:        * on the same clock (its `next` replay and its `$` calls are free).
4241:        *
4242:        * Past it the hook is absent as if it had no handler; `next.error.budget`
4243:        * and `next.budget.ms` both read it there. `engine.create` has no budget.
4244:        */
4245:       readonly catchMs: 1_000;
4246:       /**
4247:        * How long a hook may keep running after `next.signal` aborted (the person
4248:        * interrupted, a hook above settled first, its own budget ran out).
4249:        *
4250:        * Past it the hook is reported as lingering; the dispatch had already gone
4251:        * on without it when the signal aborted.
4252:        */
4253:       readonly lingerMs: 5_000;
4254:   };
9465:   /**
9466:    * The hook a streaming event takes: `async function* ($, e, next) {}`,
9467:    * yielding the event's chunks and returning its result.
9468:    *
9469:    * `return yield* next(e)` passes; `for await (const c of next(e)) yield
9470:    * f(c)` transforms; yielding without `next` answers alone. A chunk yielded
9471:    * stays: a hook that fails mid-stream is left, the rest from beneath it.
9472:    *
9473:    * @example on('turn.step', async function* ($, e, next) {
9474:    *   const r = yield* next(e); return { ...r } })
9475:    */
9476:   export type StreamHook<N extends StreamingEventName> = ($: EngineInterface, e: Frozen<Args<N>>, next: StreamNext<N>) => StreamHookBody<Chunk<N>, EventResult<N>>;
9477:
9478:   /**
9479:    * What a hook on a streaming event evaluates to: the async generator an
9480:    * `async function*` makes, yielding `C` and returning `R` or nothing.
9481:    *
9482:    * Returning nothing lets its last `next(e)`'s result stand. A plain
9483:    * function is a type error here even when it returns `next(e)`: the hook
9484:    * is the generator, not a function that hands one back.
9485:    */
9486:   export type StreamHookBody<C, R> = AsyncGenerator<C, R | void> & {
9487:       /**
9488:        * Absent on a generator; present on `next(e)`, which is not a hook body.
9489:        */
9490:       readonly result?: never;
9491:   };
9492:
9493:   /**
9494:    * The events that stream: their hooks are async generators, `next(e)` is
9495:    * the stream of everything beneath, and the result is what it returns.
9496:    *
9497:    * `turn.step` alone: the model's response arrives in pieces, and a hook
9498:    * that saw it whole could not change what had already been shown.
9499:    */
9500:   export type StreamingEventName = 'turn.step';
9501:
9502:   /**
9503:    * The rest of the chain as a hook on a streaming event receives it: Next,
9504:    * except that `next(e)` is the stream beneath (HookStream), not a promise.
9505:    *
9506:    * Each call opens a fresh stream; for `turn.step` each is a model request,
9507:    * so a hook that calls it twice makes two. Not calling it yields the hook's
9508:    * own chunks and returns its own result, and nothing beneath runs.
9790:    * The input of `tool.call`: the tool, the id of this call, the tool's
9791:    * arguments beside them (`e.command` for Bash), and `agentId` in a subagent.
9792:    *
9793:    * A union discriminated by `tool`: after `if (e.tool === "Bash")`, `e.command`
9794:    * is a string and a rewrite is checked against Bash's schema. `tool`,
9795:    * `tool_use_id` and `agentId` are reserved: a rewrite of any is refused.
9796:    */
9797:   export type ToolCallInput = ToolCallEnvelope & AgentLoop;
9822:   /**
9823:    * What a `tool.call` hook returns and what `next(e)` and `$.tool.call(input)`
9824:    * resolve to: the tool's result (`{ result, context? }`) or `{ deny }`.
9825:    *
9826:    * From core the result is `{ ref, result, text }` or, when the tool reported
9827:    * an error, `{ ref, result, text, isError }`; `ref` names core's messages.
9828:    *
9829:    * @template Name the tool the call went to, typing `result` per built-in
9830:    *   tool (BuiltinToolResults) once `e.tool` is narrowed; else `unknown`
9831:    */
9832:   export type ToolCallResult<Name extends string = string> = {
9833:       /**
9834:        * Refuses the call: the model receives the text as an error result.
9835:        * Absent when the call was answered.
9836:        */
9837:       deny: string;
9838:       result?: undefined;
9839:       context?: undefined;
9840:       ref?: undefined;
9841:       text?: undefined;
9842:       isError?: undefined;
9843:   } | {
9844:       /**
9845:        * The tool's output: from core the tool's record, typed per built-in
9846:        * tool once `e.tool` and `isError` are narrowed; from a hook, its own.
9847:        *
9848:        * Core validates a hook's answer against the tool's output schema when
9849:        * it has one, maps it for the model with the tool's own mapper, and
9850:        * records it in the transcript as the tool's result. Absent on a deny.
9851:        */
9852:       result: ToolResultOf<Name>;
9853:       /**
9854:        * What the model reads after the tool's result and the user never
9855:        * sees. From core, none.
9856:        *
9857:        * One reminder, as a PostToolUse hook's is, after the managed tier's
9858:        * review; none on a plugin's own `$.tool.call`. Kept whole from `next`,
9859:        * none empty, any length: past 100,000 (200,000 together) head + path.
9860:        */
9861:       context?: readonly string[];
9862:       /**
9863:        * Set by core on what `next(e)` resolves to: names the messages core
9864:        * produced for the call (they stay on the host side).
9865:        *
9866:        * A hook that returns the object it got makes core use them verbatim.
9867:        * Absent on a hook's own `{ result }` and on a deny.
9868:        */
9869:       ref?: number;
9870:       /**
9871:        * Set by core: the result as the model reads it (text blocks joined),
9872:        * present whatever the tool, where `result`'s shape varies per tool.
9873:        *
9874:        * Absent on a hook's own `{ result }`.
9875:        */
9876:       text?: string;
9877:       isError?: undefined;
9878:       deny?: undefined;
9879:   } | {
9880:       /**
9881:        * Set by core, present only when the tool reported an error (it threw,
9882:        * was interrupted, or answered an error): `text` is what the model read.
9883:        */
9884:       isError: true;
9885:       /**
9886:        * What the transcript stored for the errored call: the error text, or
9887:        * undefined when nothing was stored; never the tool's typed record.
9888:        */
9889:       result: unknown;
9890:       /**
9891:        * The error as the model reads it.
9892:        */
9893:       text?: string;
9894:       /**
9895:        * As on an answered result: names the messages core produced.
9896:        */
9897:       ref?: number;
9898:       /**
9899:        * As on an answered result.
9900:        */
9901:       context?: readonly string[];
9902:       deny?: undefined;
9903:   };
10419:   /**
10420:    * The input of `turn.step`: one model request inside a turn, at the moment
10421:    * the engine is about to send it; the bottom of the chain sends it.
10422:    *
10423:    * The transcript is not on it: `messageCount` says how many messages the
10424:    * request carries, and `$.session.messages()` reads them. A hook rewrites
10425:    * `model` or `effort` going down; the rest is pinned.
10426:    */
10427:   export type TurnStepInput = {
10428:       /**
10429:        * The turn this step belongs to (`turn.start`'s id; inside a subagent's
10430:        * loop, the id the run's `turn.complete` will carry). Pinned.
10431:        */
10432:       turnId: string;
10433:       /**
10434:        * The step's position in the turn, from 0. Pinned.
10435:        */
10436:       index: number;
10437:       /**
10438:        * Which model the request names, as the engine resolved it for this step
10439:        * (the session's, a fallback's). `next({ ...e, model })` names another.
10440:        */
10441:       model: string;
10442:       /**
10443:        * How hard the request asks the model to think: the session's setting or
10444:        * the model's default, absent for a model without effort; rewritable.
10445:        */
10446:       effort?: 'low' | 'medium' | 'high' | 'xhigh' | 'max' | number;
10447:       /**
10448:        * How many messages the request carries (the conversation so far, the
10449:        * turn's tool results included). Pinned: the messages are the engine's.
10450:        */
10451:       messageCount: number;
10452:       /**
10453:        * The loop the request is made in: a subagent's id, the `id`
10454:        * `$.agent.list()` gives it and its `tool.call`s carry; absent on main.
10455:        *
10456:        * Pinned: a different value is refused, one left out is kept. A subagent
10457:        * a hook spawned through `$.agent.spawn` steps past that hook, as its tool
10458:        * calls do; every other hook sees its steps.
10459:        */
10460:       agentId?: string;
10461:   };
10480:   /**
10481:    * What a `turn.step` hook returns and what `next(e)` resolves to: the
10482:    * model's response to the step's request, once its blocks are all in.
10483:    *
10484:    * From the bottom, the response the engine streamed; a hook's own value
10485:    * changes what the hooks above it read, never what the engine streamed.
10486:    */
10487:   export type TurnStepResult = {
10488:       /**
10489:        * The turn this step belongs to, as received.
10490:        */
10491:       turnId: string;
10492:       /**
10493:        * The step's position in the turn, as received.
10494:        */
10495:       index: number;
10496:       /**
10497:        * The visible text of the response ("" when it only called tools, only
10498:        * thought, or no request was made).
10499:        */
10500:       answer: string;
10501:       /**
10502:        * The tool calls the response made, in order; empty for a text-only step.
10503:        */
10504:       toolUses: readonly TurnStepToolUse[];
10505:       /**
10506:        * Why the model stopped; null when no response arrived (the request
10507:        * failed or was interrupted before a message, or no request was made).
10508:        */
10509:       stopReason: TurnStopReason;
10510:       /**
10511:        * What the request cost as the API reported it, and the model that
10512:        * answered; null when no response arrived or it carried no usage.
10513:        */
10514:       usage: TurnUsage | null;
10515:   };
10557:   /**
10558:    * The model begins a tool call in block `index`: the tool's name and the
10559:    * call's id; its arguments follow as `input` chunks of the same index.
10560:    *
10561:    * A block whose `tool` chunk never comes out of the chain is no tool call:
10562:    * the engine records none and runs none.
10563:    */
10564:   export type TurnStepToolChunk = ChunkRef & {
10565:       kind: 'tool';
10566:       index: number;
10567:       /**
10568:        * The call's `tool_use_id`.
10569:        */
10570:       id: string;
10571:       /**
10572:        * The tool's name (`Read`, `Bash`, `mcp__server__tool`).
10573:        */
10574:       name: string;
10575:   };
```
