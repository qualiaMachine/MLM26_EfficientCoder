# Context Management and History Compaction — Design

> **This is the target architecture, not an implementation request.** Do not implement it in one
> pass. Work happens one phase at a time — see `roadmap.md` for phase order/status and `phases/`
> for the per-phase contracts. Section numbers below are stable cross-reference targets (there is
> intentionally no §4). Changes to this design must be logged in `decisions.md`.

## 1. Feature summary

Implement a context-management system for the coding agent that prevents execution history from growing without bounds while preserving the information required to complete a task correctly.

The system must separate the complete execution record from the smaller working context sent to the language model. It will retain a lossless raw history for auditing and evaluation, while dynamically constructing each model request from:

1. Permanent system instructions
2. The original task and its constraints
3. A structured compacted task state
4. A recent window of exact action–observation events
5. The current unresolved failure, preserved with sufficient exact detail
6. Older evidence retrieved when it is specifically relevant

The primary objective is to substantially reduce repeated input tokens without causing the agent to forget architectural decisions, implementation details, unresolved bugs, user constraints, failed approaches, or remaining acceptance criteria.

The full execution history is the audit log. It must not automatically be the model’s working context.

---

## 2. Problem statement

The current agent repeatedly sends its full conversation and terminal history to the model. As a task grows, every additional model call includes all previous assistant messages and command results.

This causes:

* Rapid growth in input-token consumption
* Repeated transmission of irrelevant or redundant terminal output
* Attention pollution from resolved errors and old investigations
* Increasing latency and cost
* Difficulty distinguishing current facts from outdated observations
* Repeated exploration and verification
* Poor awareness of completed versus remaining work
* A greater chance of exhausting the model’s context window

Much of this history is not useful in its raw form. Examples include:

* Assistant narration preceding a command
* Repeated file reads
* Successful installation progress
* Long build logs
* Duplicate commands
* Errors that have already been resolved
* Complete source-file dumps that remain accessible in the container

However, blindly deleting old messages or tool results is unsafe. Raw interactions may contain important consequences such as:

* An architectural choice and its rationale
* A dependency version selected for compatibility
* A file or symbol that was modified
* An unresolved error
* A failed approach that should not be repeated
* A test that passed before a later code modification
* A task constraint that must remain satisfied

The feature must therefore discard redundant representations of the past while retaining their durable consequences.

---

## 3. Goals

The context-management system must:

* Reduce the number of history tokens resent on every model call.
* Preserve the complete raw execution history outside the active context.
* Preserve the original task and all user-provided constraints.
* Track acceptance criteria and their current verification status.
* Preserve architectural decisions and their rationales.
* Preserve important implementation details, including affected files and symbols.
* Preserve environment and dependency changes.
* Preserve unresolved bugs with exact operational evidence.
* Preserve failed approaches so that the agent does not repeat them.
* Preserve verification results and invalidate them when later changes make them stale.
* Keep recent interactions available without lossy summarization.
* Keep the latest relevant failure as exactly as practical.
* Allow older raw evidence to be recovered if compaction omitted or generalized a necessary detail.
* Use deterministic reduction wherever possible.
* Use LLM-based compaction only where semantic interpretation is required.
* Measure whether compaction improves token usage without lowering task-completion reliability.

The system should optimize for:

$$
\text{high completion rate} + \text{low token usage} + \text{low turn count}
$$

Token reduction alone is not success if the agent forgets requirements or completes a task incorrectly.

---

## 5. Core architectural principle

The agent must maintain two distinct representations of execution:

### Raw history

A complete, append-only record of everything that happened.

It exists for:

* Debugging
* Evaluation
* Harbor result metadata
* Reconstructing state
* Auditing compaction behavior
* Recovering information omitted from active context
* Comparing compacted and non-compacted runs

### Active context

A deliberately selected and bounded set of messages sent to the model on the next turn.

It exists only to provide the information the model needs to choose its next action correctly.

The relationship should be:

```text
Raw execution events
        ↓
Context manager
        ├── Permanent instructions
        ├── Original task
        ├── Structured task state
        ├── Recent exact events
        ├── Exact current failure
        └── Retrieved older evidence
        ↓
Bounded working context
        ↓
Language model
```

The critical invariant is:

```python
active_messages != raw_history
```

Raw history must not be mutated or destroyed when active context is compacted.

---

## 6. Event model

Store execution history as structured events instead of treating the transcript as the only source of truth.

A possible base event model is:

```python
@dataclass
class Event:
    id: int
    turn: int
    event_type: str
    timestamp: str
    token_count: int | None
    tags: dict[str, list[str] | str]
```

Assistant action events should retain both the raw and canonical forms:

```python
@dataclass
class AssistantActionEvent(Event):
    raw_response: str
    action_kind: Literal["shell", "complete", "invalid"]
    command: str | None
    canonical_content: str
```

Observation events should contain:

```python
@dataclass
class ObservationEvent(Event):
    command: str
    exit_code: int
    stdout_preview: str
    stderr_preview: str
    full_output_path: str | None
    original_character_count: int
    truncated: bool
    started_at: str | None
    duration_seconds: float | None
```

Additional tags may include:

```python
{
    "command_type": "test",
    "status": "failed",
    "files": ["src/example.py"],
    "symbols": ["parse_config"],
    "tests": ["test_invalid_config"],
    "error_types": ["ValueError"],
}
```

These tags can later support deterministic filtering and retrieval without embeddings.

---

## 7. Canonicalization

Canonicalization converts a model response into one standard, minimal representation of the action that actually occurred.

For example, these raw responses:

`````text
I need to inspect the configuration before deciding what to change.

```bash
cat setup.py
```
`````

and:

`````text
I will now examine setup.py.

```bash
cat setup.py
```
`````

should both become:

`````text
```bash
cat setup.py
```
`````

The raw response remains in the audit history. Only the canonical action is eligible for inclusion in active context.

A basic deterministic function may be:

```python
def canonicalize_action(action: Action) -> str:
    if action.kind == "shell":
        return f"```bash\n{action.command}\n```"

    if action.kind == "complete":
        return "TASK_COMPLETE"

    return ""
```

Canonicalization is not conversation summarization. It operates on one response and records exactly what action occurred in a standard form.

For the initial implementation:

* Canonicalize assistant messages deterministically.
* Do not use an LLM to canonicalize commands.
* Preserve raw responses separately.
* Treat parsing failures as explicit events rather than silently dropping them.

---

## 8. Tool-output management

Large tool outputs must not remain indefinitely in active context.

For every command, retain:

* Exact command
* Exit code
* Original output size
* A bounded preview
* A path to the full output when available
* Whether truncation occurred
* Relevant error content for failures

The complete command output should be written to a file inside the task container when it exceeds the configured active-output limit.

A compact observation may resemble:

```text
Command:
python setup.py build_ext --inplace

Exit code:
1

Output size:
47,382 characters

Full output:
/tmp/agent-outputs/turn-018.log

Relevant output:
...
ModuleNotFoundError: No module named 'setuptools'
```

The output-selection strategy should be sensitive to the command result:

### Successful commands

Usually retain:

* Exit code
* A small output sample
* The durable result
* The full-output path, if offloaded

Successful package-installation progress, download bars, and routine warnings usually do not deserve active-context space.

### Failed commands

Retain more exact information:

* Exit code
* Final relevant error block
* Exception type and message
* Final useful stack frames
* Referenced files and line numbers
* Compiler invocation immediately preceding a compiler error
* Full-output path

### Read-only commands

After their findings enter structured state, commands such as `cat`, `sed`, `rg`, `ls`, and `find` can usually be evicted from active context.

### State-changing commands

Their durable effects must be preserved before their raw interactions are removed.

A successful exit code alone is not proof of the intended consequence. When possible, the effect should be based on later inspection or verification.

---

## 9. Tool-call retention policy

Do not blindly clear every tool call and result.

Classify tool interactions into three broad categories:

| Interaction                                              | Treatment                               |
| -------------------------------------------------------- | --------------------------------------- |
| Recent action or current failure                         | Preserve exactly or nearly exactly      |
| Action that changed repository or environment state      | Convert into durable structured state   |
| Read-only, routine, duplicate, or superseded interaction | Remove after preserving useful findings |

Examples:

### Read-only inspection

Raw interaction:

```bash
cat setup.py
```

Durable finding:

```text
setup.py creates Cython extensions only when Cython and NumPy are importable. Build isolation may otherwise produce a package without compiled extensions.
```

The command and full file output may then be removed from active context.

### Repository modification

Raw interaction:

```bash
sed -i 's/np.int/np.int64/g' ccomplexity.pyx
```

Durable state:

```text
Implementation change:
- File: pyknotid/spacecurves/ccomplexity.pyx
- Change: Replaced runtime uses of np.int with np.int64.
- Reason: NumPy 2.x removed the np.int alias.
- Verification: Pending rebuild and tests.
```

### Environment modification

Raw interaction:

```bash
pip install planarity==0.6
```

Durable state:

```text
Environment change:
- Installed planarity 0.6.
- Reason: The project expects the older pos/start/end interface.
- Verification: Relevant failing test must be rerun.
```

### Current failure

Preserve:

```text
Command:
pytest tests/test_spacecurve.py

Exit code:
1

Failing test:
test_reconstructed_space_curve

Exact error:
KeyError: 'pos'

Suspected cause:
The installed planarity version exposes an incompatible node-attribute API.
```

Once resolved, compress this to a cause-and-resolution record.

---

## 10. Structured task state

The agent must maintain a compact, persistent representation of the task’s operational state.

A suggested schema is:

```python
@dataclass
class EvidenceReference:
    event_ids: list[int]
    command: str | None
    output_path: str | None
    file_paths: list[str]
    note: str | None
```

```python
@dataclass
class AcceptanceCriterion:
    description: str
    status: Literal["pending", "passed", "failed", "stale"]
    evidence: EvidenceReference | None
```

```python
@dataclass
class ArchitecturalDecision:
    decision: str
    rationale: str
    alternatives_rejected: list[str]
    evidence: EvidenceReference | None
```

```python
@dataclass
class ImplementationChange:
    file: str
    symbols: list[str]
    change: str
    reason: str
    verification_status: Literal[
        "unverified",
        "partially_verified",
        "verified",
        "stale",
    ]
    evidence: EvidenceReference | None
```

```python
@dataclass
class BugState:
    symptom: str
    exact_error: str | None
    failing_command: str | None
    affected_files: list[str]
    suspected_cause: str | None
    attempted_resolutions: list[str]
    status: Literal["unresolved", "resolved"]
    resolution: str | None
    evidence: EvidenceReference | None
```

```python
@dataclass
class TestResult:
    command: str
    scope: str
    status: Literal["passed", "failed", "stale"]
    summary: str
    evidence: EvidenceReference | None
```

```python
@dataclass
class TaskState:
    objective: str
    constraints: list[str]
    acceptance_criteria: list[AcceptanceCriterion]
    architectural_decisions: list[ArchitecturalDecision]
    implementation_changes: list[ImplementationChange]
    environment_facts: list[str]
    environment_changes: list[str]
    verified_facts: list[str]
    unresolved_bugs: list[BugState]
    resolved_bugs: list[BugState]
    failed_approaches: list[str]
    test_results: list[TestResult]
    current_error: str | None
    current_blocker: str | None
    next_step: str | None
    verification_may_be_stale: bool
    compacted_through_event_id: int
```

The exact code structure may change, but the semantic fields should remain represented.

---

## 11. Information that must survive compaction

The following information must not be discarded:

* Original task objective
* Explicit and implied user constraints
* Acceptance criteria
* Required output format
* Architectural decisions
* Rationale for architectural decisions
* Rejected alternatives when repeating them would waste time
* Modified files
* Modified symbols or relevant locations
* Nature and purpose of each meaningful implementation change
* Dependency and environment changes
* Exact versions, paths, values, and commands when operationally important
* Important repository and environment discoveries
* Current unresolved bugs
* Exact current error
* Failing command
* Failing test or build target
* Suspected cause, clearly marked as a hypothesis
* Failed approaches and why they failed
* Tests already run
* Whether tests passed, failed, or became stale
* Evidence supporting passed acceptance criteria
* Outstanding work
* Current blocker
* Most appropriate next step

If uncertainty exists about whether a detail is operationally important, the compactor should initially favor retention.

---

## 12. Information that can usually be discarded or reduced

The following content is usually safe to remove from active context after preserving any durable consequence:

* Assistant narration such as “I will inspect the repository”
* Duplicate commands with identical findings
* Repeated reads of unchanged files
* Routine successful `pwd`, `ls`, and directory listings
* Download and installation progress
* Full source-file contents that remain accessible in the container
* Long successful build output
* Long logs after the relevant error or finding is preserved
* Resolved error traces after cause and resolution are recorded
* Repeated verification output for the same unchanged state
* Tool-call formatting after the action’s effect is represented
* Exploratory hypotheses disproven by later evidence
* Superseded plans
* Conversational filler

Information should be removed because it is redundant or recoverable, not merely because it is old.

---

## 13. Recent exact window

The model must receive a recent uncompressed or minimally processed history window.

The purpose of the recent window is to preserve local continuity and prevent fresh errors, commands, and reasoning-relevant observations from being degraded by summarization.

The initial version may preserve a fixed number of recent action–observation pairs, such as the last six turns. The preferred mature implementation should select recent events by token budget rather than by turn count.

Example:

```python
def select_recent_events(events, token_budget, count_tokens):
    selected = []
    used = 0

    for event in reversed(events):
        cost = count_tokens(event.to_active_message())

        if selected and used + cost > token_budget:
            break

        selected.append(event)
        used += cost

    return list(reversed(selected))
```

Requirements:

* Never split an assistant action from its corresponding observation.
* Prefer complete action–observation pairs.
* Preserve the latest unresolved failure even if it slightly exceeds the normal recent-history budget.
* Do not include events already represented in compacted state unless they belong to the recent window or are explicitly retrieved.
* Ensure the recent window cannot grow without bounds.

---

## 14. Compaction trigger

Compaction must occur before the active context approaches the model’s hard limit.

Before every request, calculate:

```python
available_input_tokens = (
    model_context_limit
    - max_completion_tokens
    - safety_margin_tokens
)
```

Estimate the active-message token count before sending the request.

Use configurable soft and hard thresholds. A possible starting point is:

```python
SOFT_LIMIT_RATIO = 0.60
HARD_LIMIT_RATIO = 0.80
```

At the soft threshold:

* Canonicalize eligible assistant messages.
* Offload large outputs.
* Split history into compactable older events and a recent exact window.
* Update structured task state with newly evicted events.
* Rebuild active context.

At the hard threshold:

* Force compaction before another model request.
* Remove low-value resolved output.
* Reduce previews further where recoverable.
* Preserve the current failure and incomplete criteria.
* Validate that the rebuilt context fits within the allowable input budget.

The exact thresholds must be configurable and evaluated empirically.

Compaction is an investment: it incurs an additional model call when semantic compaction is used. It should happen early enough to benefit later turns but not so often that compaction costs exceed its savings.

---

## 15. Compaction cursor

The system must track which events have already been incorporated into compacted state.

```python
task_state.compacted_through_event_id
```

Only events after this cursor and before the recent-window boundary should be compacted.

After a successful state update:

```python
task_state.compacted_through_event_id = last_compacted_event.id
```

This prevents:

* Reprocessing the same events
* Duplicate state entries
* Repeated compaction-model costs
* Gradual distortion caused by repeatedly summarizing identical evidence

Raw events must remain available even after the cursor advances.

---

## 16. Hybrid deterministic and LLM-based compaction

Compaction should use deterministic processing first and semantic LLM processing second.

### Deterministic responsibilities

Use code for:

* Parsing assistant actions
* Canonicalizing commands
* Recording exit codes
* Recording command-output paths
* Identifying output sizes
* Deduplicating identical commands and observations
* Extracting common file paths
* Recognizing common test commands
* Tracking modified files where commands make this observable
* Retaining current failures
* Selecting the recent window
* Enforcing token budgets
* Updating the compaction cursor
* Applying basic invalidation rules
* Preserving exact structured evidence
* Removing routine successful output
* Detecting repeated actions

### LLM responsibilities

Use an LLM when events require semantic interpretation, such as:

* Identifying an architectural decision
* Explaining why an implementation choice was made
* Distinguishing an unresolved issue from a resolved one
* Extracting important findings from exploratory work
* Updating implementation summaries
* Determining which failed approaches should not be repeated
* Producing a concise next-step description
* Merging new evidence into existing structured state

The compaction model must update an explicit schema rather than produce an unrestricted prose summary.

---

## 17. Compaction prompt requirements

The compaction prompt should prioritize recall of durable, decision-relevant information rather than maximum compression.

Suggested prompt:

```text
Update the persistent task state using the supplied execution events.

Your primary goal is to preserve the information required for the coding
agent to continue and complete the task correctly. Omitting an important
fact is worse than retaining a mildly redundant fact.

Preserve:
- the task objective, constraints, and acceptance criteria;
- architectural decisions and their rationales;
- rejected alternatives when repeating them would waste time;
- every meaningfully modified file and symbol;
- the nature and reason for each implementation change;
- environment and dependency facts or changes;
- unresolved bugs and exact relevant errors;
- failing commands, tests, file paths, symbols, and versions;
- failed approaches that should not be repeated;
- test and verification results;
- evidence supporting completion claims;
- remaining work, blockers, and the next step.

Rules:
- Do not claim that a criterion passed without evidence.
- Do not mark a bug resolved unless a later event demonstrates resolution.
- Do not invent motivations, causes, modifications, or verification.
- Clearly distinguish confirmed facts from suspected causes.
- Do not discard an unresolved error.
- Do not treat earlier verification as current after a relevant later change.
- Preserve exact values, paths, versions, commands, errors, and symbols when
  they are operationally important.
- Retain evidence references to the raw events whenever possible.
- Merge new facts into the previous state without duplicating existing facts.
- Prefer the latest supported fact when events conflict.
- If uncertain whether a detail may matter later, preserve it.

You may discard:
- conversational narration;
- duplicated information;
- routine successful command output;
- full source-file contents that remain accessible;
- verbose logs after preserving their relevant findings;
- resolved error details after recording the cause and resolution;
- superseded hypotheses clearly disproven by later evidence.

Return only data conforming to the required schema.
```

The compactor should receive:

* Original task
* Acceptance criteria
* Previous structured state
* Newly evicted events
* Evidence identifiers and output paths
* The required structured-output schema

It should not need the entire raw history on every compaction call.

---

## 18. Compaction validation

Do not assume a syntactically valid compaction result is semantically safe.

After compaction, validate:

* All original constraints remain present.
* Every acceptance criterion remains represented.
* Every unresolved bug from the previous state remains unresolved unless new evidence proves resolution.
* Modified files are not silently removed.
* Current failing command and error are retained.
* Passed criteria include evidence.
* The compaction cursor only moves forward.
* New state does not refer to nonexistent event IDs.
* A hypothesis is not presented as a verified fact.
* No criterion changes from failed or pending to passed without new evidence.
* State size remains within its configured token budget.
* The rebuilt active context fits the model’s input budget.

If validation fails:

* Reject the compacted update.
* Preserve the previous valid state.
* Record the compaction failure in telemetry.
* Retry with a stricter repair prompt or fall back to deterministic truncation.
* Never discard raw events because a compaction attempt failed.

---

## 19. Stale-state invalidation

Structured state can become misleading when later changes invalidate earlier evidence.

Add at least basic invalidation rules.

Examples:

* Source-code modification → related test results become `stale`.
* Dependency change → import, build, and test verification may become `stale`.
* Reinstallation → package-location and import verification become `pending` or `stale`.
* Build-configuration modification → compiled-artifact verification becomes `stale`.
* Generated-file regeneration → verification based on the old generated file becomes `stale`.
* Test-only modification → passing that modified test does not independently verify production behavior.
* Environment reset → environment-dependent evidence becomes `stale`.

The first version may use a conservative rule:

```python
if action_may_modify_repository_or_environment(command):
    task_state.verification_may_be_stale = True
```

Before the agent may emit `TASK_COMPLETE`, it must run final verification appropriate to all acceptance criteria whenever this flag is set.

The mature version can invalidate only affected tests or criteria based on file and command metadata.

---

## 20. Current-failure preservation

The most recent unresolved failure is often the most important part of the context.

Preserve, where available:

* Exact command
* Exit code
* Failing test or target
* Exception or compiler-error type
* Exact error message
* Final useful stack frames
* Referenced files and line numbers
* Relevant surrounding lines
* Immediately preceding compiler invocation
* Output-file path
* Suspected cause, labeled as unconfirmed
* Attempts already made

Do not reduce:

```text
ModuleNotFoundError: No module named 'setuptools'
```

to:

```text
The build failed because of a dependency issue.
```

When the issue is resolved, replace the large exact failure in active state with:

* Original symptom
* Confirmed cause
* Resolution
* Verification evidence

The complete original error remains available in raw history and the offloaded log.

---

## 21. Evidence and recovery

Each important compacted fact should retain a pointer to its evidence where practical.

Evidence may include:

* Event IDs
* Turn numbers
* Commands
* Full-output paths
* Repository file paths
* Test names
* Relevant symbols

Example:

```json
{
  "decision": "Use planarity 0.6 instead of adapting the project to 1.0",
  "rationale": "The requested package version expects the older node API.",
  "evidence": {
    "event_ids": [41, 42, 45, 46],
    "command": "pytest tests/test_spacecurve.py",
    "output_path": "/tmp/agent-outputs/turn-023.log",
    "file_paths": ["pyknotid/spacecurves/spacecurve.py"]
  }
}
```

Evidence references reduce summary drift and allow targeted recovery from raw history.

If the model later needs exact source or log content, it should reread the source file or inspect the referenced log rather than keeping the entire content permanently in its context.

The guiding rule is:

> Preserve findings and pointers; reread exact recoverable content when needed.

---

## 22. Retrieval of older evidence

The initial implementation should use metadata retrieval rather than embeddings.

Retrieve older events using:

* File path
* Symbol
* Command type
* Test name
* Error type
* Dependency name
* Modification status
* Event type
* Acceptance-criterion identifier

Example:

```python
def retrieve_events(query, events, token_budget):
    candidates = [
        event for event in events
        if metadata_matches(query, event.tags)
    ]

    ranked = rank_by_recency_and_exact_match(candidates)
    return fit_within_token_budget(ranked, token_budget)
```

Retrieved evidence should only be added when relevant to the current action or unresolved issue.

Embedding-based retrieval may be evaluated later if metadata and keyword retrieval fail to recover necessary semantic details.

---

## 23. Active-context construction

Each model request should be rebuilt from authoritative components rather than continuously appending to one unbounded `messages` list.

Suggested order:

```text
1. System prompt
2. Original task instruction
3. Current structured task state
4. Progress and remaining acceptance criteria
5. Retrieved older evidence, if any
6. Recent exact action–observation window
7. Exact current unresolved failure, if not already present
8. Turn and token-budget feedback
```

Possible implementation:

```python
def build_active_context(
    system_prompt,
    instruction,
    task_state,
    raw_events,
    retrieval_query,
    budgets,
):
    recent_events = select_recent_events(
        raw_events,
        token_budget=budgets.recent_events,
    )

    retrieved_events = retrieve_relevant_events(
        query=retrieval_query,
        events=raw_events,
        exclude_ids={event.id for event in recent_events},
        token_budget=budgets.retrieved_evidence,
    )

    messages = compose_messages(
        system_prompt=system_prompt,
        instruction=instruction,
        task_state=task_state,
        retrieved_events=retrieved_events,
        recent_events=recent_events,
    )

    return enforce_total_budget(messages, budgets)
```

Structured state should appear before the recent event window so that recent evidence can naturally supersede or refine the older compacted state.

---

## 24. Context budgeting

Every component must have a configurable token budget.

For a model with a 64K context and an 8K completion allowance, an initial allocation could resemble:

| Component                | Initial budget |
| ------------------------ | -------------: |
| System instructions      |           1–2K |
| Original task            |       Up to 4K |
| Structured task state    |           2–6K |
| Recent exact events      |          8–12K |
| Retrieved older evidence |           2–4K |
| Safety margin            |           4–8K |
| Completion allowance     |             8K |

These are starting values, not permanent requirements.

When content exceeds its component budget, reduction priority should be:

1. Remove duplicate narration.
2. Remove routine successful output.
3. Replace recoverable file contents with paths and findings.
4. Reduce resolved-bug detail.
5. Reduce old verification-output detail while keeping status and evidence.
6. Reduce retrieved evidence.
7. Reduce recent successful observations.
8. Preserve unresolved failures and incomplete acceptance criteria as the highest priority.

Never silently truncate the original task or permanent system constraints.

---

## 25. Turn and progress feedback

Expose progress and remaining budget to the coding model on each turn.

Example:

```text
Turn: 18/30

Completed:
- Repository cloned
- Build dependencies installed
- NumPy compatibility patches applied

Remaining:
- Rebuild extensions
- Install package
- Run README example
- Run required tests

Current blocker:
Build fails because setuptools is unavailable.

Context:
12,430 / 40,000 available input tokens
```

At a configurable turn threshold, inject a targeted recovery instruction:

```text
You are approaching the turn budget. Stop nonessential exploratory work.
Identify the shortest safe path to the unmet acceptance criteria. Batch
related checks where appropriate and avoid repeating completed work.
```

A large emergency maximum-turn ceiling may remain, but a smaller warning threshold should shape behavior before the limit is reached.

---

## 26. No-progress detection

Track behavior that suggests the agent is not advancing the task.

Possible signals:

* Repeating the same command without new justification
* Reopening an unchanged file multiple times
* Repeating a verification that already passed without an invalidating change
* Three or more consecutive read-only actions without a new recorded finding
* Consecutive actions that do not update state or acceptance criteria
* Returning to a previously rejected approach
* Reinstalling an already confirmed dependency
* Repeatedly inspecting the same error without testing a new hypothesis

When detected, inject a targeted message describing the specific pattern.

Example:

```text
No-progress warning:
The last three actions reread files without producing a new finding or
changing task state. Use the existing evidence to choose an implementation
or verification action. Do not repeat a previous command unless you explain
what changed and what new evidence it should produce.
```

Avoid using only a generic nudge because it does not tell the model which behavior must change.

---

## 27. Completion guard

The agent must not emit `TASK_COMPLETE` solely because the compacted summary sounds positive.

Before completion:

* Every acceptance criterion must be `passed`.
* Each passed criterion must have current evidence.
* No required criterion may be `pending`, `failed`, or `stale`.
* No unresolved blocker may remain.
* Verification must have occurred after the latest relevant code, dependency, build, or environment change.
* Required compiled artifacts, imports, commands, snippets, or tests must be checked directly.
* Any explicit exclusions from the task must be respected.
* The final verification command and result must be recorded.

If state is inconsistent, the completion attempt should be rejected and the agent should receive a precise explanation of what remains unverified.

---

## 28. Main run-loop integration

A simplified integrated flow may resemble:

```python
async def run(instruction, environment, context):
    raw_events = []
    task_state = initialize_task_state(instruction)
    next_event_id = 0

    for turn in range(1, AGENT_MAX_TURNS + 1):
        apply_pending_invalidations(task_state, raw_events)

        active_messages = build_active_context(
            system_prompt=SYSTEM_PROMPT,
            instruction=instruction,
            task_state=task_state,
            raw_events=raw_events,
            retrieval_query=derive_retrieval_query(task_state),
            budgets=CONTEXT_BUDGETS,
        )

        if should_compact(active_messages):
            compactable, recent = split_compactable_events(
                raw_events=raw_events,
                compacted_through=task_state.compacted_through_event_id,
                recent_token_budget=CONTEXT_BUDGETS.recent_events,
            )

            if compactable:
                candidate_state = await update_compact_state(
                    instruction=instruction,
                    previous_state=task_state,
                    events=compactable,
                )

                validate_compact_state(
                    previous_state=task_state,
                    candidate_state=candidate_state,
                    instruction=instruction,
                    events=compactable,
                )

                task_state = candidate_state
                task_state.compacted_through_event_id = compactable[-1].id

                active_messages = build_active_context(
                    system_prompt=SYSTEM_PROMPT,
                    instruction=instruction,
                    task_state=task_state,
                    raw_events=raw_events,
                    retrieval_query=derive_retrieval_query(task_state),
                    budgets=CONTEXT_BUDGETS,
                )

        enforce_input_limit(active_messages)

        response = await llm.chat(active_messages)
        action = parse_action(response)

        action_event = make_action_event(
            id=next_event_id,
            turn=turn,
            raw_response=response,
            action=action,
        )
        next_event_id += 1
        raw_events.append(action_event)

        if action.kind == "complete":
            validate_completion(task_state)

            update_run_metadata(
                context=context,
                raw_events=raw_events,
                task_state=task_state,
            )
            return

        observation = await run_shell_with_output_capture(
            command=action.command,
            environment=environment,
            turn=turn,
        )

        observation_event = make_observation_event(
            id=next_event_id,
            turn=turn,
            action=action,
            observation=observation,
        )
        next_event_id += 1
        raw_events.append(observation_event)

        task_state = deterministically_update_state(
            task_state=task_state,
            action_event=action_event,
            observation_event=observation_event,
        )

        apply_invalidation_rules(
            task_state=task_state,
            action_event=action_event,
            observation_event=observation_event,
        )

        update_run_metadata(
            context=context,
            raw_events=raw_events,
            task_state=task_state,
        )

    raise TurnLimitExceeded(task_state=task_state)
```

The exact interfaces may differ from the existing agent, but the separation of responsibilities should remain.

---

## 29. Telemetry

Record context-management metrics for every turn.

Suggested fields:

```python
{
    "turn": turn,
    "raw_history_tokens": raw_history_tokens,
    "sent_input_tokens": sent_input_tokens,
    "system_prompt_tokens": system_prompt_tokens,
    "task_tokens": task_tokens,
    "state_tokens": state_tokens,
    "recent_history_tokens": recent_tokens,
    "retrieved_evidence_tokens": retrieved_tokens,
    "completion_tokens": completion_tokens,
    "observation_original_chars": original_chars,
    "observation_sent_chars": preview_chars,
    "output_offloaded": output_offloaded,
    "compaction_performed": compaction_performed,
    "compaction_input_tokens": compaction_input_tokens,
    "compaction_output_tokens": compaction_output_tokens,
    "compacted_event_count": compacted_event_count,
    "compacted_through_event_id": compacted_through,
    "state_validation_passed": state_validation_passed,
    "no_progress_warning": warning_type,
}
```

Task-level metrics should include:

* Task completion rate
* Benchmark reward
* Input tokens per completed task
* Total tokens including compaction calls
* Turns per completed task
* Maximum active-context size
* Number of compactions
* Number of compaction failures
* Percentage of tool output offloaded
* Number of raw-evidence rereads
* Repeated-command count
* Premature-completion attempts
* Forgotten-constraint failures
* Stale-evidence failures
* Missing-detail failures caused by compaction
* Total latency
* Cost per successful task

---

## 30. Evaluation strategy

Evaluate context strategies on the same Terminal-Bench tasks and model configuration.

Recommended variants:

| Variant | Context strategy                                                |
| ------- | --------------------------------------------------------------- |
| A       | Full raw history baseline                                       |
| B       | Original task plus recent rolling window                        |
| C       | Structured LLM compaction plus recent window                    |
| D       | Structured compaction, canonicalization, and output offloading  |
| E       | Hybrid deterministic state updates plus LLM semantic compaction |

Keep other variables fixed where possible:

* Model
* Prompt
* Maximum turns
* Environment
* Temperature
* Completion-token allowance
* Task selection
* Tool interface

Compare:

* Completion and reward
* Total input and output tokens
* Compaction tokens
* Number of turns
* Latency
* Repeated work
* Forgotten constraints
* Premature completion
* Stale verification
* Incorrectly summarized errors
* Need to reread raw evidence

Simple rolling truncation must be treated as a serious baseline. Structured compaction should earn its added complexity through measurably better completion reliability, lower token usage, or fewer turns.

---

## 31. Feature rollout plan

### Phase 1: Establish architecture and measurement

Implement:

* Append-only raw event history
* Separately generated active context
* Token counting before each model request
* Per-turn context telemetry
* Canonical assistant actions
* A fixed or token-bounded recent history window

Exit criteria:

* Raw history remains complete.
* The model no longer receives the entire raw transcript.
* Existing tasks still execute correctly.
* Token usage can be measured by context component.

### Phase 2: Reversible output reduction

Implement:

* Large-output capture inside the task container
* Bounded success and failure previews
* Full-output paths
* Failure-aware preview selection
* Deterministic observation metadata

Exit criteria:

* Large outputs no longer dominate active context.
* Full output remains recoverable.
* Current errors remain sufficiently detailed for diagnosis.

### Phase 3: Structured task state

Implement:

* Objective and constraints
* Acceptance criteria
* Architectural decisions
* Implementation changes
* Environment changes
* Unresolved and resolved bugs
* Failed approaches
* Test results
* Blocker and next step
* Evidence references

Exit criteria:

* Important progress can be understood without replaying the full transcript.
* Completion status is linked to acceptance criteria.
* State updates cannot silently remove unresolved work.

### Phase 4: Structured semantic compaction

Implement:

* Soft and hard compaction thresholds
* Compaction cursor
* Schema-constrained compaction prompt
* Previous-state-plus-new-events updating
* State validation
* Failure fallback
* Active-context rebuilding after compaction

Exit criteria:

* Old history is removed from active context after being incorporated.
* Compaction processes each event once.
* Constraints, changes, and unresolved bugs survive compaction tests.

### Phase 5: Invalidation and completion safety

Implement:

* Conservative invalidation rules
* `stale` verification status
* Final-verification requirement
* Completion guard
* Current-failure preservation

Exit criteria:

* The agent cannot complete using verification made stale by later changes.
* Required criteria must have current evidence.

### Phase 6: Progress control

Implement:

* Turn-budget feedback
* Completed and remaining work display
* No-progress detection
* Targeted recovery instructions
* Repeated-command detection

Exit criteria:

* Unproductive loops are detected and surfaced.
* Long tasks show lower repeated-action counts.

### Phase 7: Retrieval and optimization

Implement:

* Event tagging
* Metadata and keyword retrieval
* Targeted evidence reinsertion
* Tuned component budgets
* Optional embedding-retrieval experiment only if justified by results

Exit criteria:

* Older exact evidence can be recovered when needed.
* Retrieval improves outcomes enough to justify its complexity.

---

## 32. Testing requirements

### Unit tests

Test:

* Action canonicalization
* Token counting
* Recent-window selection
* Preservation of action–observation pairs
* Output offloading
* Failure preview extraction
* Compaction-boundary calculation
* Cursor advancement
* Duplicate-event handling
* Schema validation
* State merge behavior
* Evidence-reference validation
* Invalidation rules
* Completion guard
* No-progress signals

### Compaction-preservation tests

Create synthetic histories containing:

* Architectural decisions
* Several modified files
* Conflicting hypotheses
* Resolved and unresolved bugs
* Failed approaches
* Passing and failing tests
* A later code edit that invalidates earlier passing tests
* Verbose redundant output
* An important constraint mentioned only once

Assert that compaction:

* Preserves all required durable information
* Removes redundant narration and logs
* Keeps unresolved bugs unresolved
* Does not invent changes
* Does not mark unsupported criteria as passed
* Marks affected verification stale
* Retains evidence pointers
* Produces a smaller active representation

### Integration tests

Run complete agent tasks where:

* No compaction is needed
* One compaction occurs
* Multiple compactions occur
* A compaction call fails
* Tool output is extremely large
* The most important error appears in the middle of a log
* The agent modifies code after tests pass
* The agent needs an older detail that was compacted
* The agent attempts premature completion

### Regression tests

Maintain tasks that previously exposed:

* Token explosion
* Repeated exploration
* Forgotten constraints
* Lost error details
* Stale test evidence
* Incorrect early completion

---

## 33. Safety and reliability invariants

The implementation must maintain these invariants:

1. Raw history is append-only and recoverable.
2. Active context is rebuilt deliberately and remains bounded.
3. Original task instructions are never removed by compaction.
4. Unresolved bugs cannot disappear without evidence of resolution.
5. Acceptance criteria cannot become passed without evidence.
6. Later relevant changes invalidate earlier verification.
7. The latest unresolved failure remains available in actionable detail.
8. Offloaded tool output remains accessible from its recorded path.
9. The compaction cursor never moves backward.
10. The same events are not repeatedly compacted.
11. A failed compaction cannot destroy the previous valid state.
12. LLM-produced state is validated before becoming authoritative.
13. Hypotheses remain distinguishable from confirmed facts.
14. `TASK_COMPLETE` requires current verification of all required criteria.
15. Token reduction must never rely on permanently deleting the audit record.

---

## 34. Initial configuration

All thresholds should be configurable rather than hard-coded.

Possible starting configuration:

```python
CONTEXT_CONFIG = {
    "soft_limit_ratio": 0.60,
    "hard_limit_ratio": 0.80,
    "recent_history_token_budget": 8_000,
    "retrieval_token_budget": 3_000,
    "task_state_token_budget": 4_000,
    "safety_margin_tokens": 6_000,
    "max_completion_tokens": 8_000,
    "observation_inline_character_limit": 6_000,
    "failure_preview_character_limit": 5_000,
    "success_preview_character_limit": 2_000,
    "turn_budget_warning": 20,
    "maximum_turns": 100,
    "output_directory": "/tmp/agent-outputs",
}
```

These values must be tuned using benchmark data and the actual context size of the hosted model.

---

## 35. Definition of done

The feature is complete when:

* The agent keeps a full raw execution record without sending all of it on every turn.
* Each model request is built from bounded, intentional context components.
* Assistant actions are canonicalized.
* Large command outputs are offloaded and recoverable.
* Recent action–observation pairs remain available.
* Older events are compacted into validated structured state.
* Architectural decisions, implementation details, unresolved bugs, constraints, failed approaches, and verification evidence survive compaction.
* The current error is preserved with actionable exact detail.
* Compaction uses a cursor and does not repeatedly process the same events.
* Stale verification is detected after relevant changes.
* Completion is blocked until all criteria have current evidence.
* Context and compaction telemetry are recorded.
* Benchmark comparisons show significant token reduction without an unacceptable decline in task-completion rate.
* The system has been compared against a simpler rolling-window baseline.
* Compaction failures degrade safely without destroying execution history or task state.

The final design should aggressively remove redundant conversational and execution noise while conservatively retaining facts that influence implementation, debugging, verification, or completion.
