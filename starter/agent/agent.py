"""MLM26 baseline coding agent.

A minimal ReAct-style external agent for Harbor / Terminal-Bench 2.0:

    1. Receive the task instruction from Harbor
    2. Ask the LLM what to do next
    3. Parse the response for one bash command (or TASK_COMPLETE)
    4. Execute it in the task container
    5. Append the output to the conversation and loop

Run it with:

    harbor run -d terminal-bench-sample@2.0 \
        --agent-import-path agent.agent:BaselineAgent

This is a floor, not a ceiling. Read it, understand it, then make it yours:
planning, context management, error recovery, self-critique, retrieval —
that's the competition.
"""

import os

from harbor.agents.base import BaseAgent
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext

from agent.llm import LLMClient
from agent.prompts import NUDGE_MESSAGE, SYSTEM_PROMPT, observation_message
from agent.tools import parse_action, run_shell

# MLM26 per-task budget: <=100 turns (matches the Terminal-Bench default).
MAX_TURNS = int(os.environ.get("AGENT_MAX_TURNS", "100"))
COMMAND_TIMEOUT_SEC = int(os.environ.get("AGENT_COMMAND_TIMEOUT_SEC", "60"))


class BaselineAgent(BaseAgent):
    @staticmethod
    def name() -> str:
        return "mlm26-baseline"

    def version(self) -> str | None:
        return "0.1.0"

    async def setup(self, environment: BaseEnvironment) -> None:
        # External agent: nothing to install inside the container. If you
        # need tools in the environment (ripgrep, jq, ...), install them here
        # via environment.exec — but remember finale tasks may have no
        # network access inside the container.
        pass

    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        llm = LLMClient(model_name=self.model_name)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": instruction},
        ]

        n_input = 0
        n_output = 0
        turns = 0
        finished = False

        for _ in range(MAX_TURNS):
            turns += 1
            text, usage = await llm.chat(messages)
            n_input += usage.get("prompt_tokens", 0)
            n_output += usage.get("completion_tokens", 0)

            # Populate context every turn so a timeout still reports usage.
            context.n_input_tokens = n_input
            context.n_output_tokens = n_output
            context.metadata = {"turns": turns, "finished": finished}

            messages.append({"role": "assistant", "content": text})
            action = parse_action(text)

            if action.kind == "done":
                finished = True
                context.metadata["finished"] = True
                break

            if action.kind == "none":
                messages.append({"role": "user", "content": NUDGE_MESSAGE})
                continue

            self.logger.info("turn %d: %s", turns, action.command[:200])
            observation = await run_shell(
                environment, action.command, timeout_sec=COMMAND_TIMEOUT_SEC
            )
            messages.append(
                {"role": "user", "content": observation_message(observation)}
            )
