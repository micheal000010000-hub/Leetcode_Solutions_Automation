import glob
import os
from datetime import datetime

import pandas as pd
import streamlit as st

from config import LEETCODE_REPO_PATH, OLLAMA_GENERATE_URL, OLLAMA_MODEL, PROMPT_VERSION
from services.generation_service import generate_solution_post_with_metadata
from services.metrics_service import (
    estimate_edit_distance,
    export_runs_to_excel,
    fetch_metrics_summary,
    fetch_recent_runs,
    get_metrics_paths,
    update_run_feedback,
)
from services.repo_service import add_solution, push_changes
from services.system_service import check_ollama_health, get_project_runtime_snapshot
from ui.activity import add_activity_event, get_activity_dataframe, init_activity_state
from ui.constants import LANGUAGE_EXTENSION_MAP


def _process_single_queue_item(item: dict) -> dict:
    """Process one queue item in a worker thread. Safe to call from ThreadPoolExecutor."""
    try:
        extension = LANGUAGE_EXTENSION_MAP[item["language"]]
        filename = f"{item['problem_number']}_{item['problem_name'].replace(' ', '_')}.{extension}"

        if item.get("save_to_repo"):
            add_solution(
                problem_number=item["problem_number"],
                problem_name=item["problem_name"],
                difficulty=item["difficulty"],
                link=item["link"],
                solution_code=item["solution_code"],
                filename=filename,
            )

        result = generate_solution_post_with_metadata(
            problem_number=item["problem_number"],
            problem_name=item["problem_name"],
            difficulty=item["difficulty"],
            link=item["link"],
            code=item["solution_code"],
            language=item["language"],
            include_repo_link=item.get("include_repo_link", True),
        )

        output_path = _save_generated_markdown(
            item["problem_number"], item["problem_name"], result["text"]
        )
        return {**item, "status": "done", "result": result, "output_path": output_path}
    except Exception as exc:
        return {**item, "status": "error", "error": str(exc)}


def render_sidebar_guide() -> None:
    st.sidebar.markdown("## Quick Guide")
    st.sidebar.markdown(
        """
1. Open `Generate` and submit problem details.
2. Review output and optional feedback.
3. Track run quality in `Metrics`.
4. Use `Activity` to inspect system health and events.
5. Push with `Git` once satisfied.
        """
    )
    st.sidebar.markdown("### Current Model")
    st.sidebar.markdown(f"`{OLLAMA_MODEL}`")


def _save_generated_markdown(problem_number: str, problem_name: str, content: str) -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "copy_paste_solution")
    os.makedirs(output_dir, exist_ok=True)

    safe_problem_name = (problem_name or "unknown").replace(" ", "_")
    file_name = f"structured_solution_{problem_number}_{safe_problem_name}.md"
    path = os.path.join(output_dir, file_name)

    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)

    return path


def render_generate_tab() -> None:
    st.subheader("Generate Solution Post")
    st.info(
        "Start here: fill details, generate markdown, then optionally save feedback to improve your prompt strategy."
    )

    llm_health = check_ollama_health(timeout_seconds=2)
    if llm_health.get("reachable") == "True":
        if llm_health.get("model_loaded") == "True":
            st.success(f"Local LLM status: Connected. Model available: `{OLLAMA_MODEL}`")
        else:
            st.warning(
                f"Local LLM status: Connected, but configured model `{OLLAMA_MODEL}` was not found in loaded tags."
            )
    else:
        st.error(f"Local LLM status: Not reachable. {llm_health.get('message', '')}")

    with st.form("generate_form", clear_on_submit=True):
        left, right = st.columns(2)

        with left:
            problem_number = st.text_input("Problem Number", placeholder="e.g. 506")
            problem_name = st.text_input("Problem Name", placeholder="Relative Ranks")
            difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"])
            link = st.text_input("Problem Link", placeholder="https://leetcode.com/problems/...")

        with right:
            language = st.selectbox("Language", list(LANGUAGE_EXTENSION_MAP.keys()))
            save_to_repo = st.checkbox("Save solution file and update README", value=True)
            include_repo_link = st.checkbox("Append repository link in generated post", value=True)

        solution_code = st.text_area(
            "Solution Code",
            height=280,
            placeholder="Paste your solution here...",
        )

        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            submitted = st.form_submit_button("Generate Structured Post", width="stretch")
        with btn_col2:
            add_to_queue = st.form_submit_button("+ Add to Queue", type="secondary", width="stretch")

    if submitted:
        if not all([problem_number.strip(), problem_name.strip(), link.strip(), solution_code.strip()]):
            st.error("Problem number, name, link, and code are required.")
            add_activity_event(
                action="Generate blocked",
                status="warning",
                details="Missing required input fields",
                category="generation",
            )
            return

        progress = st.progress(5, text="Preparing generation workflow...")
        status_log_placeholder = st.empty()
        status_lines = []

        def update_status(percent: int, message: str) -> None:
            progress.progress(percent, text=message)
            status_lines.append(f"- {message}")
            status_log_placeholder.markdown("#### Status\n" + "\n".join(status_lines))

        update_status(15, "Inputs validated.")

        extension = LANGUAGE_EXTENSION_MAP[language]
        filename = f"{problem_number}_{problem_name.replace(' ', '_')}.{extension}"

        add_activity_event(
            action="Generation started",
            status="info",
            details=f"{problem_number} - {problem_name}",
            category="generation",
        )
        update_status(25, "Generation task started.")

        try:
            if save_to_repo:
                update_status(40, "Saving solution to local repository...")
                add_solution(
                    problem_number=problem_number,
                    problem_name=problem_name,
                    difficulty=difficulty,
                    link=link,
                    solution_code=solution_code,
                    filename=filename,
                )
                add_activity_event(
                    action="Solution saved in repo",
                    status="success",
                    details=f"{difficulty}/{filename}",
                    category="repository",
                )
                update_status(50, "Solution saved in repository.")
            else:
                update_status(40, "Skipping repository save step.")

            update_status(62, f"Calling local LLM endpoint: {OLLAMA_GENERATE_URL}")

            result = generate_solution_post_with_metadata(
                problem_number=problem_number,
                problem_name=problem_name,
                difficulty=difficulty,
                link=link,
                code=solution_code,
                language=language,
                include_repo_link=include_repo_link,
            )
            if result["error_type"]:
                update_status(
                    78,
                    f"Local LLM call finished with warning: {result['error_type']}",
                )
            else:
                http_status = result.get("http_status")
                update_status(
                    78,
                    f"Local LLM call completed successfully (HTTP {http_status if http_status else 'n/a'}).",
                )

            output_text = result["text"]
            update_status(90, "Saving generated markdown output...")
            output_path = _save_generated_markdown(problem_number, problem_name, output_text)

            st.session_state["last_run"] = {
                "run_id": result["run_id"],
                "output_text": output_text,
                "output_path": output_path,
                "problem_number": problem_number,
                "problem_name": problem_name,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            if result["error_type"]:
                st.warning(output_text)
                add_activity_event(
                    action="Generation finished with warning",
                    status="warning",
                    details=result["error_type"],
                    category="generation",
                )
                update_status(100, "Generation completed with warning.")
            else:
                st.success(f"Generated successfully. Saved at: {output_path}")
                add_activity_event(
                    action="Generation succeeded",
                    status="success",
                    details=f"run_id={result['run_id'][:8]}",
                    category="generation",
                )
                update_status(100, "Generation completed.")

            st.markdown("### Generated Markdown")
            st.code(output_text, language="markdown")

        except Exception as exc:
            progress.progress(100, text="Generation failed.")
            status_lines.append(f"- Generation failed: {str(exc)}")
            status_log_placeholder.markdown("#### Status\n" + "\n".join(status_lines))
            st.error(f"Failed: {str(exc)}")
            add_activity_event(
                action="Generation failed",
                status="error",
                details=str(exc),
                category="generation",
            )

    # --- Add to Queue handler ---
    if add_to_queue:
        if not all([problem_number.strip(), problem_name.strip(), link.strip(), solution_code.strip()]):
            st.error("Problem number, name, link, and code are required to add to queue.")
        else:
            if "solution_queue" not in st.session_state:
                st.session_state["solution_queue"] = []
            st.session_state["solution_queue"].append({
                "problem_number": problem_number.strip(),
                "problem_name": problem_name.strip(),
                "difficulty": difficulty,
                "link": link.strip(),
                "language": language,
                "solution_code": solution_code.strip(),
                "save_to_repo": save_to_repo,
                "include_repo_link": include_repo_link,
                "status": "pending",
                "result": None,
            })
            st.session_state["auto_process_queue_now"] = True
            st.success(f"Added #{problem_number.strip()} — {problem_name.strip()} to queue ({len(st.session_state['solution_queue'])} total).")
            add_activity_event(
                action="Added to queue",
                status="info",
                details=f"{problem_number.strip()} - {problem_name.strip()}",
                category="generation",
            )

    # --- Batch Queue UI ---
    queue = st.session_state.get("solution_queue", [])
    if queue:
        st.markdown("---")
        st.markdown("### Batch Queue")

        queue_rows = [
            {
                "#": i + 1,
                "Problem": f"{item['problem_number']} — {item['problem_name']}",
                "Difficulty": item["difficulty"],
                "Language": item["language"],
                "Status": item["status"],
            }
            for i, item in enumerate(queue)
        ]
        st.dataframe(pd.DataFrame(queue_rows), width="stretch")

        pending_count = sum(1 for item in queue if item["status"] == "pending")
        done_count = sum(1 for item in queue if item["status"] == "done")
        error_count = sum(1 for item in queue if item["status"] == "error")
        st.caption(f"{pending_count} pending · {done_count} done · {error_count} error")

        q_col1, q_col2 = st.columns(2)
        with q_col1:
            process_queue = st.button(
                f"Process All ({pending_count} pending)",
                type="primary",
                disabled=pending_count == 0,
                key="process_queue_btn",
            )
        with q_col2:
            clear_queue = st.button("Clear Queue", key="clear_queue_btn")

        auto_process_queue = st.session_state.pop("auto_process_queue_now", False)

        if clear_queue:
            st.session_state["solution_queue"] = []
            st.rerun()

        if process_queue or (auto_process_queue and pending_count > 0):
            pending_entries = [
                (idx, item) for idx, item in enumerate(queue) if item["status"] == "pending"
            ]
            batch_progress = st.progress(0, text=f"Processing 0 / {len(pending_entries)}...")
            results: list = []

            for completed_count, (queue_index, item) in enumerate(pending_entries, start=1):
                result = _process_single_queue_item(item)
                queue[queue_index] = result
                results.append(result)

                pct = int((completed_count / len(pending_entries)) * 100)
                batch_progress.progress(
                    pct,
                    text=f"Processing {completed_count} / {len(pending_entries)}...",
                )

            st.session_state["solution_queue"] = queue

            success_count = sum(1 for r in results if r["status"] == "done")
            fail_count = sum(1 for r in results if r["status"] == "error")
            st.success(f"Queue processed: {success_count} succeeded, {fail_count} failed.")
            for r in results:
                if r["status"] == "done":
                    add_activity_event(
                        action="Batch generation succeeded",
                        status="success",
                        details=f"{r['problem_number']} - {r['problem_name']}",
                        category="generation",
                    )
                else:
                    add_activity_event(
                        action="Batch generation failed",
                        status="error",
                        details=f"{r['problem_number']} - {r.get('error', '')}",
                        category="generation",
                    )
            st.rerun()

    last_run = st.session_state.get("last_run")
    if last_run:
        st.markdown("### Feedback Metrics")
        st.caption("Attach acceptance and manual edit distance to the last generated run.")

        feedback_choice = st.radio(
            "Accepted for posting?",
            options=["Not set", "Yes", "No"],
            horizontal=True,
            key="feedback_choice",
        )
        edited_text = st.text_area(
            "Optional edited final version",
            value=last_run["output_text"],
            height=220,
            key="edited_text",
        )

        if st.button("Save Feedback", type="secondary"):
            accepted_map = {"Not set": None, "Yes": 1, "No": 0}
            accepted_value = accepted_map[feedback_choice]
            edit_distance = estimate_edit_distance(last_run["output_text"], edited_text)
            update_run_feedback(
                run_id=last_run["run_id"],
                accepted_for_posting=accepted_value,
                manual_edit_distance=edit_distance,
            )
            st.success(
                f"Feedback saved for run {last_run['run_id'][:8]}... Estimated edit distance: {edit_distance}"
            )
            add_activity_event(
                action="Feedback saved",
                status="success",
                details=f"run_id={last_run['run_id'][:8]}, edit_distance={edit_distance}",
                category="feedback",
            )


def render_queue_tab() -> None:
    st.subheader("Queue and Run Status")
    st.caption("Run history summary with pass/fail state.")

    runs = fetch_recent_runs(limit=200)
    if not runs:
        st.info("No runs available yet.")
        return

    df = pd.DataFrame(runs)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["status"] = df["error_type"].apply(lambda x: "Success" if str(x).strip() == "" else "Failed")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Recent Jobs", len(df))
    c2.metric("Success", int((df["status"] == "Success").sum()))
    c3.metric("Failed", int((df["status"] == "Failed").sum()))
    c4.metric("Unique Problems", int(df["problem_number"].nunique()))

    status_filter = st.multiselect(
        "Filter by Status",
        options=["Success", "Failed"],
        default=["Success", "Failed"],
    )
    filtered = df[df["status"].isin(status_filter)]

    display_columns = [
        "timestamp",
        "status",
        "problem_number",
        "problem_name",
        "difficulty",
        "problem_link",
        "language",
        "model",
        "prompt_version",
        "prompt_strategy",
        "prompt_hash",
        "error_type",
        "http_status",
        "total_duration_ms",
        "tokens_per_sec",
        "output_input_ratio",
        "completeness_score",
    ]
    existing_columns = [col for col in display_columns if col in filtered.columns]
    st.dataframe(
        filtered[existing_columns].sort_values("timestamp", ascending=False),
        width="stretch",
    )


def render_metrics_tab() -> None:
    st.subheader("Metrics Dashboard")

    summary = fetch_metrics_summary()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Runs", summary["total_runs"])
    c2.metric("Success Runs", summary["success_runs"])
    c3.metric("Failed Runs", summary["failed_runs"])
    c4.metric("Timeout Runs", summary["timeout_runs"])

    c5, c6, c7 = st.columns(3)
    c5.metric("Avg Tokens/Sec", summary["avg_tokens_per_sec"])
    c6.metric("Avg Duration (ms)", summary["avg_total_duration_ms"])
    c7.metric("Avg Completeness", summary["avg_completeness_score"])

    runs = fetch_recent_runs(limit=1000)
    if not runs:
        st.info("No run metrics available yet.")
        return

    df = pd.DataFrame(runs)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.sort_values("timestamp")

    st.markdown("### Throughput Trend")
    throughput_df = df[["timestamp", "tokens_per_sec"]].dropna()
    if not throughput_df.empty:
        st.line_chart(throughput_df.set_index("timestamp"))

    st.markdown("### Completeness Trend")
    completeness_df = df[["timestamp", "completeness_score"]].dropna()
    if not completeness_df.empty:
        st.area_chart(completeness_df.set_index("timestamp"))

    st.markdown("### Prompt Version Comparison")
    prompt_group_columns = [col for col in ["prompt_version", "prompt_strategy", "model", "prompt_hash"] if col in df.columns]
    if not prompt_group_columns:
        prompt_group_columns = ["prompt_version"]

    prompt_summary = (
        df.groupby(prompt_group_columns, dropna=False)
        .agg(
            runs=("run_id", "count"),
            avg_completeness=("completeness_score", "mean"),
            avg_format=("format_score", "mean"),
            avg_tokens_per_sec=("tokens_per_sec", "mean"),
            avg_output_input_ratio=("output_input_ratio", "mean"),
        )
        .reset_index()
        .sort_values("runs", ascending=False)
    )
    st.dataframe(prompt_summary, width="stretch")

    st.markdown("### Latest Runs")
    st.dataframe(df.sort_values("timestamp", ascending=False), width="stretch")

    if st.button("Export SQLite Metrics to Excel"):
        result = export_runs_to_excel()
        if result["status"] == "ok":
            st.success(f"Exported to: {result['path']}")
            add_activity_event(
                action="Excel export",
                status="success",
                details=result["path"],
                category="metrics",
            )
        elif result["status"] == "permission_error":
            st.warning(f"⚠️ {result['message']}")
            add_activity_event(
                action="Excel export",
                status="warning",
                details=result["message"],
                category="metrics",
            )
        else:
            st.error(f"Export failed: {result['message']}")
            add_activity_event(
                action="Excel export",
                status="error",
                details=result["message"],
                category="metrics",
            )


def render_activity_tab() -> None:
    st.subheader("Activity and Health")
    st.caption("Understand what the app is doing in real time.")

    init_activity_state()

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.markdown("### System Health")
        if st.button("Refresh Health Snapshot"):
            add_activity_event(
                action="Health refresh requested",
                status="info",
                details="Manual health check",
                category="system",
            )

        ollama = check_ollama_health()
        snapshot = get_project_runtime_snapshot()

        health_rows = pd.DataFrame(
            [
                {"check": "Ollama reachable", "value": ollama["reachable"]},
                {"check": "Configured model available", "value": ollama["model_loaded"]},
                {"check": "Metrics DB exists", "value": snapshot["metrics_db_exists"]},
                {"check": "Metrics Excel exists", "value": snapshot["excel_exists"]},
                {"check": "Copy folder exists", "value": snapshot["copy_folder_exists"]},
            ]
        )
        st.dataframe(health_rows, width="stretch")

        st.markdown("### Health Details")
        st.code(
            "\n".join(
                [
                    f"OLLAMA_ENDPOINT={OLLAMA_GENERATE_URL}",
                    f"OLLAMA_MESSAGE={ollama['message']}",
                    f"OLLAMA_MODELS={ollama['models']}",
                    f"METRICS_DB={snapshot['metrics_db_path']}",
                    f"METRICS_EXCEL={snapshot['excel_path']}",
                ]
            ),
            language="bash",
        )

    with col_right:
        st.markdown("### Event Stream")
        events_df = get_activity_dataframe()
        if events_df.empty:
            st.info("No events captured yet. Run a generation or export to populate this view.")
        else:
            category_filter = st.multiselect(
                "Category Filter",
                options=sorted(events_df["category"].unique().tolist()),
                default=sorted(events_df["category"].unique().tolist()),
            )
            filtered = events_df[events_df["category"].isin(category_filter)]
            st.dataframe(filtered, width="stretch")


def render_git_tab() -> None:
    st.subheader("Git Push")
    st.caption("Runs git add, date-based commit, and force push.")

    if st.button("Push Changes to GitHub", type="primary"):
        add_activity_event(
            action="Git push started",
            status="info",
            details="git add, commit, push -f",
            category="git",
        )
        result = push_changes()
        if result.get("ok", "False") == "True":
            st.success(f"Push completed. Commit message: {result['commit_message']}")
            add_activity_event(
                action="Git push succeeded",
                status="success",
                details=result["commit_message"],
                category="git",
            )
        else:
            st.warning("Push workflow reported issues. Inspect output below.")
            add_activity_event(
                action="Git push warning",
                status="warning",
                details=result.get("push_output", ""),
                category="git",
            )

        st.code(result.get("add_output", ""), language="bash")
        st.code(result.get("commit_output", ""), language="bash")
        st.code(result.get("push_output", ""), language="bash")


def render_settings_tab() -> None:
    st.subheader("Settings and Paths")
    paths = get_metrics_paths()

    st.code(
        "\n".join(
            [
                f"LEETCODE_REPO_PATH={LEETCODE_REPO_PATH}",
                f"OLLAMA_GENERATE_URL={OLLAMA_GENERATE_URL}",
                f"OLLAMA_MODEL={OLLAMA_MODEL}",
                f"PROMPT_VERSION={PROMPT_VERSION}",
                f"METRICS_DB={paths['db_path']}",
                f"METRICS_EXCEL={paths['excel_path']}",
            ]
        ),
        language="bash",
    )


def render_copy_solutions_tab() -> None:
    st.subheader("Copy Paste Solutions")
    st.caption("Browse every generated markdown solution and copy it with one click.")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    copy_dir = os.path.join(base_dir, "copy_paste_solution")

    if not os.path.isdir(copy_dir):
        st.info("No copy_paste_solution folder found yet. Generate a solution first.")
        return

    # Show most recently generated markdown files first for faster lookup in the selector.
    files = sorted(
        glob.glob(os.path.join(copy_dir, "*.md")),
        key=os.path.getmtime,
        reverse=True,
    )
    if not files:
        st.info("No generated solutions found yet. Use Generate or the Queue to create some.")
        return

    file_names = [os.path.basename(f) for f in files]

    if "copy_solutions_index" not in st.session_state:
        st.session_state["copy_solutions_index"] = 0

    idx = max(0, min(st.session_state["copy_solutions_index"], len(files) - 1))
    st.session_state["copy_solutions_index"] = idx

    # Jump selector
    selected_name = st.selectbox(
        "Jump to solution",
        options=file_names,
        index=idx,
        key="copy_solutions_selector",
    )
    if selected_name != file_names[idx]:
        st.session_state["copy_solutions_index"] = file_names.index(selected_name)
        st.rerun()

    # Navigation row
    nav_prev, nav_counter, nav_next = st.columns([1, 3, 1])
    with nav_prev:
        if st.button("← Prev", disabled=idx == 0, width="stretch"):
            st.session_state["copy_solutions_index"] -= 1
            st.rerun()
    with nav_counter:
        st.markdown(
            f"<p style='text-align:center;padding-top:6px;font-weight:600'>{idx + 1} / {len(files)}</p>",
            unsafe_allow_html=True,
        )
    with nav_next:
        if st.button("Next →", disabled=idx == len(files) - 1, width="stretch"):
            st.session_state["copy_solutions_index"] += 1
            st.rerun()

    current_file = files[st.session_state["copy_solutions_index"]]
    with open(current_file, "r", encoding="utf-8") as fh:
        content = fh.read()

    st.caption(f"File: `{os.path.basename(current_file)}`")
    st.code(content, language="markdown")  # built-in copy button in top-right corner


def render_about_tab() -> None:
    st.subheader("About LeetCode AutoSync")
    st.markdown(
        """
LeetCode AutoSync solves the repetitive parts of interview practice so you can focus on problem solving.

### Problem We Are Solving
- Writing a solution is only part of the workflow.
- After solving, you still need to organize files, update README entries, generate explanation posts, and track quality over time.
- Doing this manually every day is slow, error-prone, and hard to keep consistent.

### How This App Helps
- Adds and organizes solutions in your repo by difficulty.
- Generates structured markdown explanation posts using your local LLM.
- Tracks run quality, speed, and formatting metrics.
- Stores feedback so prompt quality can improve over time.
- Provides health checks, activity history, and Git push workflow in one place.

### Intended Outcome
You spend more time learning algorithms and less time managing repetitive tooling steps.
        """
    )
