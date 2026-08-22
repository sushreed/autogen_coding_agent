import tempfile
from dataclasses import dataclass

from autogen import AssistantAgent, UserProxyAgent


@dataclass
class CodingResult:
    answer: str
    transcript: list[dict[str, str]]


def run_coding_agent(*, task: str, api_key: str, model: str) -> CodingResult:
    """Generate and execute Python with AutoGen 0.2's UserProxyAgent."""

    llm_config = {
        "config_list": [
            {
                "model": model,
                "api_key": api_key,
                "base_url": "https://openrouter.ai/api/v1",
            }
        ],
        "temperature": 0,
        "timeout": 120,
    }

    with tempfile.TemporaryDirectory(prefix="autogen-coder-") as work_dir:
        coding_agent = AssistantAgent(
            name="coding_agent",
            llm_config=llm_config,
            system_message=(
                "You are a practical Python coding agent. Solve the task with a small, "
                "self-contained Python program in one fenced python code block. Use only "
                "the Python standard library. Do not access files, environment variables, "
                "the network, operating-system commands, input(), or any interactive prompt. "
                "Use fixed example values when the task does not provide inputs. Do not write "
                "TERMINATE in the message containing code. After the executor returns real "
                "output, explain the verified result briefly and then end with TERMINATE."
            ),
        )
        executor = UserProxyAgent(
            name="code_executor",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3,
            is_termination_msg=lambda message: (
                "TERMINATE" in (message.get("content") or "")
                and "```" not in (message.get("content") or "")
            ),
            code_execution_config={
                "work_dir": work_dir,
                "use_docker": False,
                "last_n_messages": 2,
            },
            llm_config=False,
        )

        chat_result = executor.initiate_chat(
            coding_agent,
            message=task,
            max_turns=4,
            summary_method="last_msg",
        )

    transcript = [
        {
            "source": message.get("name") or message.get("role", "agent"),
            "content": message.get("content") or "",
        }
        for message in chat_result.chat_history
        if message.get("content")
    ]
    answer = chat_result.summary or (
        transcript[-1]["content"] if transcript else "The agent returned no answer."
    )
    return CodingResult(answer=answer, transcript=transcript)
