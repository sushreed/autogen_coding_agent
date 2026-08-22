import streamlit as st

from workflow import run_coding_agent


st.set_page_config(
    page_title="CodePilot · AutoGen",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 15% 5%, rgba(124, 58, 237, .18), transparent 28rem),
            radial-gradient(circle at 90% 15%, rgba(14, 165, 233, .14), transparent 25rem),
            #090d18;
    }
    [data-testid="stSidebar"] {
        background: rgba(12, 17, 31, .92);
        border-right: 1px solid rgba(148, 163, 184, .16);
    }
    .hero {
        padding: 2.3rem 2.5rem;
        border: 1px solid rgba(148, 163, 184, .18);
        border-radius: 24px;
        background: linear-gradient(135deg, rgba(124, 58, 237, .20), rgba(14, 165, 233, .09));
        box-shadow: 0 24px 70px rgba(0, 0, 0, .24);
        margin-bottom: 1.4rem;
    }
    .eyebrow {
        color: #a78bfa;
        font-size: .78rem;
        font-weight: 800;
        letter-spacing: .16em;
        text-transform: uppercase;
    }
    .hero h1 {
        color: #f8fafc;
        font-size: clamp(2.15rem, 5vw, 4rem);
        letter-spacing: -.055em;
        margin: .35rem 0 .65rem;
    }
    .hero p { color: #bac6d8; font-size: 1.08rem; max-width: 720px; margin: 0; }
    .step-card {
        min-height: 112px;
        padding: 1.05rem 1.15rem;
        border: 1px solid rgba(148, 163, 184, .16);
        border-radius: 17px;
        background: rgba(15, 23, 42, .72);
    }
    .step-number { color: #38bdf8; font-size: .76rem; font-weight: 800; }
    .step-title { color: #f1f5f9; font-weight: 750; margin: .28rem 0; }
    .step-copy { color: #94a3b8; font-size: .88rem; line-height: 1.45; }
    div.stButton > button[kind="primary"] {
        min-height: 3.15rem;
        border: 0;
        border-radius: 14px;
        font-weight: 800;
        background: linear-gradient(90deg, #7c3aed, #0284c7);
        box-shadow: 0 10px 30px rgba(124, 58, 237, .28);
    }
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stTextInput"] input {
        border-radius: 13px;
        border-color: rgba(148, 163, 184, .22);
        background: rgba(15, 23, 42, .80);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="hero">
      <div class="eyebrow">AutoGen powered · real execution</div>
      <h1>CodePilot ⚡</h1>
      <p>Describe a small programming challenge. One focused agent writes the
      solution, a UserProxyAgent runs it, and CodePilot explains the verified result.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

steps = st.columns(3)
step_content = [
    ("01 · PROMPT", "Describe", "Tell CodePilot what Python should calculate or demonstrate."),
    ("02 · BUILD", "Generate", "The coding agent creates a compact standard-library solution."),
    ("03 · VERIFY", "Execute", "UserProxyAgent runs the code and returns its actual output."),
]
for column, (number, title, copy) in zip(steps, step_content):
    with column:
        st.markdown(
            f'<div class="step-card"><div class="step-number">{number}</div>'
            f'<div class="step-title">{title}</div><div class="step-copy">{copy}</div></div>',
            unsafe_allow_html=True,
        )

with st.sidebar:
    st.markdown("## ⚙️ OpenRouter")
    st.caption("Your credential stays in this browser session and is never written to disk.")
    api_key = st.text_input(
        "API key",
        type="password",
        placeholder="Paste your OpenRouter key",
    )
    model = st.text_input("Model", value="openai/gpt-4o-mini")

st.markdown("### What should CodePilot build?")
examples = {
    "Choose an example…": "",
    "Fibonacci explorer": "Print the first 15 Fibonacci numbers and their sum.",
    "Prime number check": "Find every prime number between 1 and 100 and print the count.",
    "Text frequency": "Count the frequency of each word in 'agents write code and agents verify code'.",
    "Monte Carlo π": "Estimate pi with a deterministic Monte Carlo simulation using seed 42.",
}
selected_example = st.selectbox("Quick start", list(examples), label_visibility="collapsed")

if "coding_task" not in st.session_state:
    st.session_state.coding_task = ""
if examples[selected_example] and st.session_state.get("last_example") != selected_example:
    st.session_state.coding_task = examples[selected_example]
    st.session_state.last_example = selected_example

task = st.text_area(
    "Coding task",
    key="coding_task",
    height=180,
    label_visibility="collapsed",
    placeholder="Example: Calculate the first 15 Fibonacci numbers and print their sum.",
)

run_column, hint_column = st.columns([1, 2])
with run_column:
    run_clicked = st.button("⚡ Write & run", type="primary", use_container_width=True)
with hint_column:
    st.caption("Best for small, self-contained Python tasks using the standard library.")

if run_clicked:
    if not api_key.strip():
        st.error("Add an OpenRouter API key in the sidebar.")
    elif not task.strip():
        st.error("Describe a coding task first.")
    else:
        progress = st.progress(10, text="Sending the task to the coding agent…")
        try:
            progress.progress(35, text="Writing the Python solution…")
            result = run_coding_agent(
                task=task.strip(),
                api_key=api_key.strip(),
                model=model.strip(),
            )
            progress.progress(100, text="Execution verified")
        except Exception as exc:
            progress.empty()
            st.error(f"CodePilot could not finish the task: {exc}")
        else:
            progress.empty()
            st.success("Execution complete — the answer below includes the verified output.")
            answer_tab, transcript_tab = st.tabs(["✨ Result", "🧭 Agent trace"])
            with answer_tab:
                st.markdown(result.answer)
            with transcript_tab:
                for index, message in enumerate(result.transcript, start=1):
                    source = message["source"].replace("_", " ").title()
                    with st.expander(
                        f"{index:02d} · {source}",
                        expanded=index == len(result.transcript),
                    ):
                        st.markdown(message["content"])
