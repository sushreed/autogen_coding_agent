import re
import tempfile
from dataclasses import dataclass

from autogen import AssistantAgent, UserProxyAgent


@dataclass
class CodingResult:
    answer: str
    transcript: list[dict[str, str]]


@dataclass
class StreamlitAppResult:
    code: str
    response: str


def _llm_config(*, api_key: str, model: str) -> dict:
    return {
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


def run_coding_agent(*, task: str, api_key: str, model: str) -> CodingResult:
    """Generate and execute Python with AutoGen 0.2's UserProxyAgent."""

    llm_config = _llm_config(api_key=api_key, model=model)

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


def generate_streamlit_app(*, task: str, api_key: str, model: str) -> StreamlitAppResult:
    """Ask AutoGen for one self-contained Streamlit application."""

    coding_agent = AssistantAgent(
        name="streamlit_coding_agent",
        llm_config=_llm_config(api_key=api_key, model=model),
        system_message=(
            "You build small, polished Streamlit applications. Return exactly one complete "
            "Python file in a fenced python code block, followed by a short explanation. "
            "The file must run with `streamlit run app.py`. Use only Python's standard "
            "library and Streamlit. Do not access environment variables, secrets, the "
            "network, subprocesses, operating-system commands, or files outside the app. "
            "Do not use input() or include shell commands. Use fixed sample data when the "
            "request does not provide data."
        ),
    )
    reply = coding_agent.generate_reply(
        messages=[{"role": "user", "content": task}],
        sender=None,
    )
    response = reply.get("content", "") if isinstance(reply, dict) else str(reply or "")
    match = re.search(r"```(?:python|py)?\s*\n(.*?)```", response, flags=re.DOTALL | re.IGNORECASE)
    if not match:
        raise ValueError("The coding agent did not return a fenced Python application.")

    code = match.group(1).strip() + "\n"
    compile(code, "generated_streamlit_app.py", "exec")
    if not re.search(r"(^|\n)\s*(?:import\s+streamlit|from\s+streamlit)", code):
        raise ValueError("The generated code is not a Streamlit application.")
    return StreamlitAppResult(code=code, response=response)
