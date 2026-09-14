import streamlit as st
import sqlite3
import pandas as pd
import tempfile

from user_skills import get_user_skills
from intelligent_matcher import calculate_match_score
from resume_parser import extract_text

DB_PATH = "database/internship_agent.db"


@st.cache_data
def load_table(table_name):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        f"SELECT * FROM {table_name}",
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

    detected_skills = get_user_skills(
        temp_resume_path
    )

    raw_text = extract_text(
        temp_resume_path
    )

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
        "🔍 Search internships"
    )

    internships = internships_df.copy()

    if search_term:

        internships = internships[
            internships["title"]
            .str.contains(
                search_term,
                case=False,
                na=False
            )
        ]

    st.dataframe(
        internships,
        width="stretch"
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
                        "match_score"
                    ]
                ],
                width="stretch"
            )

# =====================================
# ALERTS
# =====================================

with tab3:

    st.header(
        "Alerts"
    )

    alerts = alerts_df.copy()

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