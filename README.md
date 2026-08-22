# AutoGen Coding Agent

A minimal Streamlit application using AutoGen 0.2. An `AssistantAgent` writes a
self-contained Python solution, and a `UserProxyAgent` executes it through
`code_execution_config`, returns the real output, and continues the conversation
until the coding agent explains the result.

## Run

```bash
cd autogen_coding_agent
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run src/app.py
```

Enter an OpenRouter API key and an OpenRouter model name in the sidebar, then
submit a small coding task. The API key remains in the current Streamlit session
and is passed directly to AutoGen's OpenAI-compatible model client.

## Execution policy

Generated code runs locally in a temporary directory using
`code_execution_config={"use_docker": False, ...}` because Docker is not installed
in the current environment. Review generated code carefully. Configure Docker-backed
execution before exposing this application publicly.
