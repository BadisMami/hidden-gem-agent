import os
import streamlit as st
import sqlite3
import pandas as pd
import tempfile

from user_skills import get_user_skills
from intelligent_matcher import calculate_match_score
from resume_parser import extract_text

DB_PATH = "database/internship_agent.db"

# Allowlist for load_table - never build SQL from unvalidated input.
ALLOWED_TABLES = {"internships", "alerts", "companies", "users"}


@st.cache_data
def load_table(table_name):

    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"Unknown table: {table_name}")

    conn = sqlite3.connect(DB_PATH)

    query = f"SELECT * FROM {table_name}"

    if table_name == "internships":
        query += " WHERE is_active = 1"

    df = pd.read_sql(
        query,
        conn
    )

    conn.close()

    return df


st.set_page_config(
    page_title="Hidden Gem Internship Intelligence Platform",
    layout="wide"
)

# =====================================
# SIDEBAR
# =====================================

st.sidebar.header(
    "📄 Resume Upload"
)

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

uploaded_file = st.sidebar.file_uploader(
    "Upload Resume (PDF)",
    type=["pdf"]
)

detected_skills = []
raw_text = ""

if uploaded_file is not None:

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as tmp_file:

        tmp_file.write(
            uploaded_file.getbuffer()
        )

        temp_resume_path = tmp_file.name

    try:

        detected_skills = get_user_skills(
            temp_resume_path
        )

        raw_text = extract_text(
            temp_resume_path
        )

    finally:

        os.remove(temp_resume_path)

    st.sidebar.success(
        "Resume Processed"
    )

    st.sidebar.subheader(
        "Detected Skills"
    )

    if detected_skills:

        for skill in detected_skills:

            st.sidebar.write(
                f"✅ {skill}"
            )

    else:

        st.sidebar.warning(
            "No skills detected."
        )

    with st.sidebar.expander(
        "OCR Preview"
    ):

        st.text(
            raw_text[:1000]
        )

# =====================================
# TITLE
# =====================================

st.title(
    "🚀 Hidden Gem Internship Intelligence Platform"
)

# =====================================
# DATA
# =====================================

internships_df = load_table(
    "internships"
)

alerts_df = load_table(
    "alerts"
)

companies_df = load_table(
    "companies"
)

users_df = load_table(
    "users"
)

# =====================================
# METRICS
# =====================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Internships",
    len(internships_df)
)

col2.metric(
    "Alerts",
    len(alerts_df)
)

col3.metric(
    "Companies",
    len(companies_df)
)

col4.metric(
    "Users",
    len(users_df)
)

# =====================================
# TABS
# =====================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Internships",
    "Recommendations",
    "Alerts",
    "Companies",
    "Users"
])

# =====================================
# INTERNSHIPS
# =====================================

with tab1:

    st.header(
        "Internships"
    )

    search_term = st.text_input(
        "🔍 Search company, title, location, or role type"
    )

    internships = internships_df.copy()

    if search_term:

        searchable_columns = [
            "company",
            "title",
            "location",
            "role_type"
        ]

        mask = pd.Series(False, index=internships.index)

        for column in searchable_columns:

            if column in internships.columns:

                mask |= internships[column].astype(str).str.contains(
                    search_term,
                    case=False,
                    na=False
                )

        internships = internships[mask]

    if len(internships) == 0:

        st.info("No internships match your search.")

    else:

        st.dataframe(
            internships,
            width="stretch",
            column_config={
                "application_url": st.column_config.LinkColumn(
                    "Apply",
                    display_text="Apply →"
                )
            }
        )

# =====================================
# RECOMMENDATIONS
# =====================================

with tab2:

    st.header(
        "Personalized Recommendations"
    )

    if uploaded_file is None:

        st.info(
            "Upload a resume to generate recommendations."
        )

    else:

        recommendations = (
            internships_df.copy()
        )

        recommendations[
            "match_score"
        ] = recommendations[
            "title"
        ].apply(
            lambda title: calculate_match_score(
                detected_skills,
                title
            )
        )

        recommendations = recommendations.sort_values(
            by="match_score",
            ascending=False
        )

        recommendations = recommendations[
            recommendations["match_score"] > 0
        ]

        if len(recommendations) == 0:

            st.warning(
                "No matching internships found."
            )

        else:

            st.dataframe(
                recommendations[
                    [
                        "company",
                        "title",
                        "location",
                        "role_type",
                        "match_score",
                        "application_url"
                    ]
                ],
                width="stretch",
                column_config={
                    "application_url": st.column_config.LinkColumn(
                        "Apply",
                        display_text="Apply →"
                    )
                }
            )

# =====================================
# ALERTS
# =====================================

with tab3:

    st.header(
        "Alerts"
    )

    alerts = alerts_df.copy()

    if len(alerts) == 0:

        st.info("No alerts yet. Alerts appear here as new matching internships are discovered.")

    else:

        if "match_score" in alerts.columns:

            alerts = alerts.sort_values(
                by="match_score",
                ascending=False
            )

        st.dataframe(
            alerts,
            width="stretch"
        )

# =====================================
# COMPANIES
# =====================================

with tab4:

    st.header(
        "Companies"
    )

    st.dataframe(
        companies_df,
        width="stretch"
    )

# =====================================
# USERS
# =====================================

with tab5:

    st.header(
        "Users"
    )

    st.dataframe(
        users_df,
        width="stretch"
    )