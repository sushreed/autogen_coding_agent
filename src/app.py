import streamlit as st

try:
    from src.workflow import generate_streamlit_app, publish_streamlit_app, run_coding_agent
except ModuleNotFoundError as exc:
    if exc.name != "src":
        raise
    from workflow import generate_streamlit_app, publish_streamlit_app, run_coding_agent


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
      <p>Describe a Python task or a Streamlit application. AutoGen writes the
      source, and CodePilot lets you execute it locally.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

build_mode = st.radio(
    "Build type",
    ["Python task", "Streamlit app"],
    horizontal=True,
    help="Python tasks run immediately. Streamlit apps are generated for review before launch.",
)

steps = st.columns(3)
if build_mode == "Streamlit app":
    step_content = [
        ("01 · PROMPT", "Describe", "Explain the Streamlit experience you want to create."),
        ("02 · BUILD", "Generate", "The coding agent creates a complete Streamlit script."),
        ("03 · LAUNCH", "Run", "Review the source, then launch the generated app locally."),
    ]
else:
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
if build_mode == "Streamlit app":
    examples = {
        "Choose an example…": "",
        "Personal budget dashboard": (
            "Build a personal budget dashboard with editable income and expense inputs, "
            "summary metrics, and a category chart."
        ),
        "Quiz app": (
            "Build a five-question Python quiz with a score, progress indicator, and restart button."
        ),
        "Unit converter": (
            "Build a polished unit converter for length, temperature, and weight."
        ),
    }
else:
    examples = {
        "Choose an example…": "",
        "Fibonacci explorer": "Print the first 15 Fibonacci numbers and their sum.",
        "Prime number check": "Find every prime number between 1 and 100 and print the count.",
        "Text frequency": "Count the frequency of each word in 'agents write code and agents verify code'.",
        "Monte Carlo π": "Estimate pi with a deterministic Monte Carlo simulation using seed 42.",
    }
selected_example = st.selectbox("Quick start", list(examples), label_visibility="collapsed")

task_key = "streamlit_task" if build_mode == "Streamlit app" else "coding_task"
example_key = f"last_example_{task_key}"
if task_key not in st.session_state:
    st.session_state[task_key] = ""
if examples[selected_example] and st.session_state.get(example_key) != selected_example:
    st.session_state[task_key] = examples[selected_example]
    st.session_state[example_key] = selected_example

task = st.text_area(
    "Coding task",
    key=task_key,
    height=180,
    label_visibility="collapsed",
    placeholder=(
        "Example: Build a habit tracker with daily checkboxes and progress metrics."
        if build_mode == "Streamlit app"
        else "Example: Calculate the first 15 Fibonacci numbers and print their sum."
    ),
)

run_column, hint_column = st.columns([1, 2])
with run_column:
    run_clicked = st.button(
        "✨ Generate app" if build_mode == "Streamlit app" else "⚡ Write & run",
        type="primary",
        use_container_width=True,
    )
with hint_column:
    if build_mode == "Streamlit app":
        st.caption("Generated code is shown for review and only runs when you launch it.")
    else:
        st.caption("Best for small, self-contained Python tasks using the standard library.")

if run_clicked:
    if not api_key.strip():
        st.error("Add an OpenRouter API key in the sidebar.")
    elif not task.strip():
        st.error("Describe a coding task first.")
    elif build_mode == "Streamlit app":
        progress = st.progress(20, text="Asking AutoGen to build the Streamlit app…")
        try:
            generated = generate_streamlit_app(
                task=task.strip(),
                api_key=api_key.strip(),
                model=model.strip(),
            )
        except Exception as exc:
            progress.empty()
            st.error(f"CodePilot could not generate the Streamlit app: {exc}")
        else:
            progress.progress(100, text="Streamlit source generated")
            progress.empty()
            st.session_state.generated_streamlit_code = generated.code
            st.session_state.generated_streamlit_response = generated.response
            st.session_state.run_generated_streamlit_app = False
            st.session_state.pop("github_publish_result", None)
            st.success("App generated. Review its source below, then launch it when ready.")
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

if build_mode == "Streamlit app" and st.session_state.get("generated_streamlit_code"):
    st.markdown("### Generated Streamlit application")
    st.code(st.session_state.generated_streamlit_code, language="python", line_numbers=True)
    st.warning(
        "Launching executes AI-generated code on this computer. Review the source before running it."
    )
    launch_clicked = st.button(
        "▶ Run Streamlit app",
        type="primary",
        use_container_width=True,
    )
    if launch_clicked:
        st.session_state.run_generated_streamlit_app = True

    if st.session_state.get("run_generated_streamlit_app"):
        st.divider()
        st.markdown("### App preview")
        try:
            generated_namespace = {"__name__": "__main__"}
            exec(
                compile(
                    st.session_state.generated_streamlit_code,
                    "generated_streamlit_app.py",
                    "exec",
                ),
                generated_namespace,
            )
        except Exception as exc:
            st.error(f"The generated app stopped with an error: {exc}")

    with st.expander("Publish generated app to GitHub", expanded=False):
        st.caption(
            "The token is used only for this request and must have permission to write "
            "repository contents. The selected branch must already exist."
        )
        with st.form("github_publish_form"):
            github_token = st.text_input("GitHub token", type="password")
            github_repository = st.text_input(
                "Repository",
                placeholder="owner/repository or https://github.com/owner/repository",
            )
            repository_column, path_column = st.columns(2)
            with repository_column:
                github_branch = st.text_input("Branch", value="main")
            with path_column:
                github_file_path = st.text_input("File path", value="generated_app/app.py")
            github_commit_message = st.text_input(
                "Commit message",
                value="Add generated Streamlit app",
            )
            publish_clicked = st.form_submit_button(
                "Push to GitHub",
                type="primary",
                use_container_width=True,
            )

        if publish_clicked:
            try:
                publish_result = publish_streamlit_app(
                    code=st.session_state.generated_streamlit_code,
                    repository=github_repository,
                    branch=github_branch,
                    file_path=github_file_path,
                    commit_message=github_commit_message,
                    token=github_token,
                )
            except Exception as exc:
                st.error(f"Could not push the generated app: {exc}")
            else:
                st.session_state.github_publish_result = publish_result
                st.success(f"Pushed successfully in commit {publish_result.commit_sha[:7]}.")

        publish_result = st.session_state.get("github_publish_result")
        if publish_result:
            link_column, commit_column = st.columns(2)
            with link_column:
                st.link_button("View generated file ↗", publish_result.file_url, use_container_width=True)
            with commit_column:
                st.link_button("View commit ↗", publish_result.commit_url, use_container_width=True)
