import json
import streamlit as st

from agents.bug_hunter import BugHunterJuror
from agents.code_quality import CodeQualityJuror
from agents.complexity import ComplexityJuror
from agents.correctness import CorrectnessJuror
from agents.edge_cases import EdgeCaseJuror
from agents.problem_classifier import ProblemClassifier
from orchestrator.judge import JudgeAgent
from verifiers.python_runner import PythonExecutionRunner
from verifiers.registry import get_verifier


def build_judge() -> JudgeAgent:
    jurors = [
        CorrectnessJuror("Juror A", "Correctness"),
        ComplexityJuror("Juror B", "Complexity"),
        EdgeCaseJuror("Juror C", "Edge Cases"),
        CodeQualityJuror("Juror D", "Code Quality"),
        BugHunterJuror("Juror E", "Bug Hunting"),
    ]
    return JudgeAgent(jurors)


def render_opinion_card(opinion):
    st.markdown(f"### {opinion['juror_name']} — {opinion['specialty']}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Verdict", opinion["verdict"].upper())
    c2.metric("Confidence", f"{opinion['confidence']}%")
    c3.metric("Score", opinion["score"])

    st.markdown("**Key points**")
    for item in opinion["key_points"]:
        st.write(f"- {item}")

    st.markdown("**Risks**")
    for item in opinion["risks"]:
        st.write(f"- {item}")

    if opinion.get("agreements"):
        st.markdown("**Agreements**")
        for item in opinion["agreements"]:
            st.write(f"- {item}")

    if opinion.get("disagreements"):
        st.markdown("**Disagreements**")
        for item in opinion["disagreements"]:
            st.write(f"- {item}")


def main():
    st.set_page_config(page_title="CodeJury", layout="wide")
    st.title("⚖️ CodeJury")
    st.caption(
        "A jury-style multi-agent code review system with classifier, verifiers, "
        "runtime checks, deliberation, and weighted voting."
    )

    with st.sidebar:
        rounds = st.slider("Deliberation rounds", 1, 3, 2)
        st.info(
            "Correctness + Edge Cases use Ollama when available; "
            "fallback logic is used otherwise."
        )

        if st.button("Clear session"):
            st.session_state.pop("last_result", None)
            st.rerun()

        if "last_result" in st.session_state:
            st.markdown("**Juror weights**")
            st.write("- Correctness: 0.30")
            st.write("- Edge Cases: 0.25")
            st.write("- Bug Hunting: 0.20")
            st.write("- Complexity: 0.15")
            st.write("- Code Quality: 0.10")

    problem = st.text_area(
        "Problem statement",
        value="",
        height=120,
        placeholder="Paste the problem statement here...",
    )
    code = st.text_area(
        "Candidate code",
        value="",
        height=280,
        placeholder="Paste the candidate code here...",
    )

    col1, col2 = st.columns(2)
    run = col1.button("Run jury review", type="primary")
    export = col2.button("Export JSON")

    if run:
        if not problem.strip():
            st.error("Please enter a problem statement.")
            return
        if not code.strip():
            st.error("Please enter candidate code.")
            return

        try:
            classifier = ProblemClassifier()
            classification = classifier.classify(problem, code)
            category = classification["category"]

            verifier = get_verifier(category)
            verifier_report = verifier.verify(problem, code)

            runner = PythonExecutionRunner()
            execution_report = runner.execute(category, code)

            judge = build_judge()
            result = judge.deliberate(
                problem=problem,
                code=code,
                category=category,
                verifier_report=verifier_report,
                execution_report=execution_report,
                rounds=rounds,
            )

            result["classification"] = classification
            st.session_state["last_result"] = result

        except Exception as e:
            st.error(f"Failed to run jury review: {e}")

    if "last_result" in st.session_state:
        result = st.session_state["last_result"]
        final_verdict = result["final_verdict"]
        classification = result["classification"]
        verifier_report = result["verifier_report"]
        execution_report = result["execution_report"]

        st.subheader("Classification")
        st.write(f"**Detected category:** `{classification['category']}`")
        st.write(f"**Confidence:** {classification['confidence']}")
        st.write(f"**Tags:** {', '.join(classification['tags'])}")

        st.subheader("Verifier + Runtime Checks")
        v1, v2 = st.columns(2)

        with v1:
            st.markdown("**Verifier Report**")
            st.write(f"Verdict: **{verifier_report['verdict'].upper()}**")
            for item in verifier_report["findings"]:
                st.write(f"- {item}")
            for item in verifier_report["hard_failures"]:
                st.write(f"- {item}")

        with v2:
            st.markdown("**Execution Report**")
            st.write(f"Supported: **{execution_report['supported']}**")
            st.write(f"Verdict: **{execution_report['verdict'].upper()}**")
            st.write(f"Passed: **{execution_report['passed']} / {execution_report['total']}**")
            for item in execution_report["findings"]:
                st.write(f"- {item}")

        st.subheader("Final Verdict")
        a, b = st.columns(2)
        a.metric("Outcome", final_verdict["outcome"].upper())
        b.metric("Confidence", f"{final_verdict['confidence']}%")
        st.write(final_verdict["summary"])

        v1, v2, v3 = st.columns(3)
        v1.metric("Weighted Accept", final_verdict["vote_tally"]["accept"])
        v2.metric("Weighted Revise", final_verdict["vote_tally"]["revise"])
        v3.metric("Weighted Reject", final_verdict["vote_tally"]["reject"])

        st.caption(
            f"Raw votes — Accept: {final_verdict['raw_vote_counts']['accept']}, "
            f"Revise: {final_verdict['raw_vote_counts']['revise']}, "
            f"Reject: {final_verdict['raw_vote_counts']['reject']}"
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**Majority reasons**")
            for item in final_verdict["majority_reasons"]:
                st.write(f"- {item}")

        with c2:
            st.markdown("**Minority reasons**")
            for item in final_verdict["minority_reasons"]:
                st.write(f"- {item}")

        with c3:
            st.markdown("**Recommended improvements**")
            for item in final_verdict["improvements"]:
                st.write(f"- {item}")

        st.subheader("Deliberation History")
        for round_data in result["history"]:
            with st.expander(
                f"Round {round_data['round']}",
                expanded=(round_data["round"] == 1),
            ):
                for opinion in round_data["opinions"]:
                    render_opinion_card(opinion)
                    st.divider()

    if export and "last_result" in st.session_state:
        st.download_button(
            label="Download deliberation JSON",
            data=json.dumps(st.session_state["last_result"], indent=2),
            file_name="codejury_result.json",
            mime="application/json",
        )


if __name__ == "__main__":
    main()