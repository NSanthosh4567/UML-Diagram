
import html
import json

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from analyzer import (
    analyze_code,
    generate_mermaid,
    export_data,
)
from ml_model import train_model, predict_relationship


st.set_page_config(
    page_title="UMLGen AI",
    page_icon="🧠",
    layout="wide",
)

st.markdown("""
<style>
.block-container {
    padding-top: 1.8rem;
    max-width: 1450px;
}
.hero {
    padding: 28px;
    border-radius: 18px;
    background: linear-gradient(120deg, #172554, #4338ca);
    color: white;
    margin-bottom: 22px;
}
.hero h1 {
    font-size: 2.2rem;
    margin: 0;
}
.hero p {
    opacity: 0.9;
}
</style>
<div class="hero">
  <h1>🧠 UMLGen AI</h1>
  <p>Intelligent source code analysis and UML generation</p>
</div>
""", unsafe_allow_html=True)


with st.sidebar:
    st.title("UMLGen AI")
    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "UML Generator",
            "ML Insights",
            "About",
        ],
    )


if "analysis" not in st.session_state:
    st.session_state.analysis = None


if page == "Dashboard":
    st.header("Project Dashboard")

    a, b, c = st.columns(3)
    a.metric("Engine", "Python AST")
    b.metric("ML Framework", "scikit-learn")
    c.metric("Status", "Ready")

    st.write(
        "Upload Python source code to inspect its structure "
        "and generate UML class diagrams."
    )

    st.info("Choose UML Generator from the sidebar to begin.")


elif page == "UML Generator":
    st.header("Source Code → UML")

    uploaded = st.file_uploader(
        "Upload a Python file",
        type=["py"],
    )

    source = st.text_area(
        "Or paste your Python code",
        height=240,
        placeholder=(
            "class User:\n"
            "    def login(self):\n"
            "        pass"
        ),
    )

    if st.button("Analyze and Generate UML", type="primary"):
        try:
            if uploaded is not None:
                if uploaded.size > 2 * 1024 * 1024:
                    st.error("File size must be below 2 MB.")
                    st.stop()

                source = uploaded.getvalue().decode("utf-8")

            if not source.strip():
                st.warning("Upload a file or enter source code.")
                st.stop()

            classes, relationships = analyze_code(source)
            diagram = generate_mermaid(classes, relationships)

            model = train_model()
            predictions = []

            for rel in relationships:
                result = predict_relationship(
                    model, rel.evidence
                )

                predictions.append({
                    "Source": rel.source,
                    "Target": rel.target,
                    "AST relationship": rel.kind,
                    "ML prediction": result["prediction"],
                    "Confidence": round(
                        result["confidence"], 3
                    ),
                })

            st.session_state.analysis = {
                "classes": classes,
                "relationships": relationships,
                "diagram": diagram,
                "predictions": predictions,
            }

        except UnicodeDecodeError:
            st.error("The uploaded file must be UTF-8 text.")
        except SyntaxError as error:
            st.error(f"Python syntax error: {error}")
        except Exception as error:
            st.error(f"Analysis failed: {error}")


    result = st.session_state.analysis

    if result is not None:
        classes = result["classes"]
        relationships = result["relationships"]

        a, b, c = st.columns(3)
        a.metric("Classes", len(classes))
        b.metric("Relationships", len(relationships))
        c.metric(
            "Methods",
            sum(len(item.methods) for item in classes),
        )

        diagram_tab, inventory_tab, ml_tab = st.tabs([
            "UML Diagram",
            "Class Inventory",
            "ML Analysis",
        ])

        with diagram_tab:
            st.subheader("Generated Class Diagram")

            # Mermaid renders the diagram in the browser.
            safe_diagram = html.escape(result["diagram"])

            components.html(
                f"""
                <pre class="mermaid">
                {safe_diagram}
                </pre>
                <script type="module">
                    import mermaid from
                    'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';

                    mermaid.initialize({{
                        startOnLoad: true,
                        securityLevel: 'strict',
                        theme: 'default'
                    }});
                </script>
                """,
                height=550,
                scrolling=True,
            )

            st.download_button(
                "Download Mermaid UML",
                data=result["diagram"],
                file_name="uml_diagram.mmd",
                mime="text/plain",
            )

        with inventory_tab:
            if classes:
                st.dataframe(
                    pd.DataFrame([
                        {
                            "Class": item.name,
                            "Bases": ", ".join(item.bases),
                            "Attributes": ", ".join(item.attributes),
                            "Methods": ", ".join(item.methods),
                        }
                        for item in classes
                    ]),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.warning("No classes found.")

            if relationships:
                st.subheader("Detected Relationships")
                st.dataframe(
                    pd.DataFrame([
                        {
                            "Source": rel.source,
                            "Target": rel.target,
                            "Type": rel.kind,
                        }
                        for rel in relationships
                    ]),
                    use_container_width=True,
                    hide_index=True,
                )

        with ml_tab:
            st.warning(
                "Demo model: trained on synthetic examples. "
                "Confidence is not validated model accuracy."
            )

            if result["predictions"]:
                st.dataframe(
                    pd.DataFrame(result["predictions"]),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.write("No relationships to classify.")

        report = export_data(classes, relationships)
        report["ml_predictions"] = result["predictions"]

        st.download_button(
            "Download JSON Report",
            data=json.dumps(report, indent=2),
            file_name="umlgen_report.json",
            mime="application/json",
        )


elif page == "ML Insights":
    st.header("Machine Learning Insights")

    st.write(
        "UMLGen AI uses TF-IDF and logistic regression "
        "to classify textual evidence about relationships."
    )

    st.code(
        "Pipeline([\n"
        "    ('tfidf', TfidfVectorizer()),\n"
        "    ('classifier', LogisticRegression())\n"
        "])",
        language="python",
    )

    st.warning(
        "The initial training set is illustrative. "
        "Build a labeled dataset and evaluate held-out "
        "projects before making accuracy claims."
    )


elif page == "About":
    st.header("About UMLGen AI")

    st.write(
        "An AI-assisted developer tool that analyzes Python "
        "source code and generates UML class diagrams."
    )

    st.markdown("""
    **Technologies**

    - Python and AST
    - scikit-learn
    - Streamlit
    - Mermaid
    - pandas
    """)
