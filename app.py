# ============================================================
# PART 12 — BUILD THE STREAMLIT UI
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import os
import sqlite3

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# ------------------------------------------------------------
# 1. DATABASE CONNECTION
# ------------------------------------------------------------

def get_database_connection():
    try:
        connection = sqlite3.connect("database/crime.db")
        return connection

    except sqlite3.Error as e:
        st.error(f"❌ Database connection failed: {e}")
        return None


# ------------------------------------------------------------
# 2. LOAD DATA FROM DATABASE
# ------------------------------------------------------------

connection = get_database_connection()

if connection is None:
    st.stop()

try:
    df = pd.read_sql_query(
        "SELECT * FROM crime_records",
        connection
    )

except Exception as e:
    st.error(f"❌ Unable to load data from database: {e}")
    st.stop()

finally:
    connection.close()


# ------------------------------------------------------------
# 3. CHECK WHETHER DATA IS EMPTY
# ------------------------------------------------------------

if df.empty:
    st.warning("⚠️ No data available in the database.")
    st.stop()


# ------------------------------------------------------------
# 4. CHECK REQUIRED COLUMNS
# ------------------------------------------------------------

required_columns = [
    "Country",
    "Year",
    "Attack Type",
    "Target Industry",
    "Financial Loss (in Million $)",
    "Number of Affected Users",
    "Attack Source",
    "Security Vulnerability Type",
    "Defense Mechanism Used",
    "Incident Resolution Time (in Hours)"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        "❌ Required columns are missing: "
        + ", ".join(missing_columns)
    )
    st.stop()


# ------------------------------------------------------------
# 5. CHECK MISSING VALUES
# ------------------------------------------------------------

missing_values = df.isnull().sum().sum()

if missing_values > 0:
    st.warning(
        f"⚠️ Dataset contains {missing_values} missing values."
    )


# ------------------------------------------------------------
# 6. CHECK DUPLICATE RECORDS
# ------------------------------------------------------------

duplicate_records = df.duplicated().sum()

if duplicate_records > 0:
    st.warning(
        f"⚠️ Dataset contains {duplicate_records} duplicate records."
    )


# ------------------------------------------------------------
# 7. CHECK YEAR VALUES
# ------------------------------------------------------------

try:
    min_year = int(df["Year"].min())
    max_year = int(df["Year"].max())

    if min_year > max_year:
        st.error("❌ Invalid year range in the dataset.")
        st.stop()

except Exception as e:
    st.error(f"❌ Year validation failed: {e}")
    st.stop()


# ------------------------------------------------------------
# 8. LOAD MACHINE LEARNING MODEL
# ------------------------------------------------------------

model_path = "models/crime_model.pkl"

if os.path.exists(model_path):

    try:
        ml_model = joblib.load(model_path)

    except Exception as e:
        ml_model = None

        st.warning(
            f"⚠️ Machine learning model could not be loaded: {e}"
        )

else:
    ml_model = None


# ------------------------------------------------------------
# 9. SAFE PREDICTION FUNCTION
# ------------------------------------------------------------

def predict_attack_type(input_data):

    if ml_model is None:
        st.warning(
            "⚠️ Machine learning model is not available. "
            "Please train the model first."
        )
        return None

    try:

        prediction = ml_model.predict(input_data)

        return prediction[0]

    except Exception as e:

        st.error(
            f"❌ Prediction failed: {e}"
        )

        return None


# ------------------------------------------------------------
# 10. SAFE PDF REPORT GENERATION
# ------------------------------------------------------------

def safe_generate_pdf(generate_pdf_function, data, file_path):

    try:

        os.makedirs(
            os.path.dirname(file_path),
            exist_ok=True
        )

        generate_pdf_function(
            data,
            file_path
        )

        return True

    except Exception as e:

        st.error(
            f"❌ PDF report generation failed: {e}"
        )

        return False


# ------------------------------------------------------------
# 11. SAFE FILTER VALIDATION
# ------------------------------------------------------------

def check_filtered_data(filtered_data):

    if filtered_data.empty:

        st.warning(
            "⚠️ No records match the selected filters."
        )

        return False

    return True



# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Internet Crime Analytics Platform",
    page_icon="🔐",
    layout="wide"
)

# ============================================================
# CUSTOM DASHBOARD DESIGN
# ============================================================

st.markdown("""
<style>

    /* Main page */
    .main {
        padding-top: 1rem;
    }

    /* KPI Card */
    .kpi-card {
        background-color: #1f2937;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #374151;
        text-align: center;
        min-height: 140px;
        margin-bottom: 20px;
    }

    .kpi-icon {
        font-size: 30px;
        margin-bottom: 5px;
    }

    .kpi-title {
        font-size: 15px;
        color: #d1d5db;
        margin-bottom: 8px;
    }

    .kpi-value {
        font-size: 28px;
        font-weight: bold;
        color: white;
    }

    /* Section headings */
    .section-title {
        font-size: 22px;
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 15px;
    }

    /* Information box */
    .info-box {
        background-color: #172554;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #3b82f6;
        margin-bottom: 20px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD DATA FROM SQLITE DATABASE
# ============================================================

connection = get_database_connection()

df = pd.read_sql_query(
    "SELECT * FROM crime_records",
    connection
)

connection.close()


# ============================================================
# LOAD MACHINE LEARNING MODEL
# ============================================================

model_path = "models/crime_model.pkl"

if os.path.exists(model_path):

    ml_model = joblib.load(model_path)

else:

    ml_model = None

# ============================================================
# PDF REPORT GENERATION FUNCTION
# ============================================================

def generate_pdf_report(df, file_path):

    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        PageBreak
    )
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.units import inch

    # ---------------------------------------------------------
    # BASIC STATISTICS
    # ---------------------------------------------------------

    total_incidents = len(df)

    total_countries = df["Country"].nunique()

    total_attack_types = df["Attack Type"].nunique()

    total_industries = df["Target Industry"].nunique()

    total_affected_users = df["Number of Affected Users"].sum()

    total_financial_loss = df["Financial Loss (in Million $)"].sum()

    average_resolution_time = (
        df["Incident Resolution Time (in Hours)"].mean()
    )

    total_attack_sources = df["Attack Source"].nunique()

    total_vulnerabilities = df[
        "Security Vulnerability Type"
    ].nunique()

    total_defense_mechanisms = df[
        "Defense Mechanism Used"
    ].nunique()

    start_year = int(df["Year"].min())
    end_year = int(df["Year"].max())


    # ---------------------------------------------------------
    # DOCUMENT SETUP
    # ---------------------------------------------------------

    document = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=20
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading1"],
        fontSize=15,
        leading=20,
        spaceBefore=12,
        spaceAfter=10
    )

    subheading_style = ParagraphStyle(
        "SubHeadingStyle",
        parent=styles["Heading2"],
        fontSize=12,
        leading=16,
        spaceBefore=8,
        spaceAfter=6
    )

    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["BodyText"],
        fontSize=9,
        leading=14,
        spaceAfter=8
    )


    story = []


    # ---------------------------------------------------------
    # TITLE
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "INTERNET CRIME ANALYTICS PLATFORM",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Cybersecurity Incident Analysis Report",
            subheading_style
        )
    )

    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            f"Analysis Period: {start_year} - {end_year}",
            normal_style
        )
    )

    story.append(Spacer(1, 20))


    # ---------------------------------------------------------
    # 1. PROJECT SUMMARY
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "1. Project Summary",
            heading_style
        )
    )

    summary_text = (
        "The Internet Crime Analytics Platform is a data analytics "
        "system developed to analyze cybersecurity incidents and "
        "identify important patterns and trends. The platform "
        "examines attack types, affected countries, target industries, "
        "attack sources, security vulnerabilities, financial losses, "
        "affected users, defense mechanisms, and incident resolution "
        "time. The analysis helps provide a clear understanding of "
        "cybersecurity incidents and supports data-driven decision making."
    )

    story.append(
        Paragraph(
            summary_text,
            normal_style
        )
    )


    # ---------------------------------------------------------
    # 2. DATASET OVERVIEW
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "2. Dataset Overview",
            heading_style
        )
    )

    dataset_table = [
        ["Parameter", "Value"],
        ["Total Records", f"{total_incidents:,}"],
        ["Analysis Period", f"{start_year} - {end_year}"],
        ["Countries Covered", str(total_countries)],
        ["Attack Types", str(total_attack_types)],
        ["Target Industries", str(total_industries)],
        ["Attack Sources", str(total_attack_sources)],
        ["Vulnerability Types", str(total_vulnerabilities)],
        ["Defense Mechanisms", str(total_defense_mechanisms)]
    ]

    table = Table(
        dataset_table,
        colWidths=[3.0 * inch, 2.5 * inch]
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
        ])
    )

    story.append(table)


    # ---------------------------------------------------------
    # 3. OVERALL INCIDENT OVERVIEW
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "3. Overall Cybersecurity Incident Overview",
            heading_style
        )
    )

    overview_table = [
        ["Metric", "Value"],
        ["Total Incidents", f"{total_incidents:,}"],
        ["Total Affected Users", f"{total_affected_users:,}"],
        [
            "Total Financial Loss",
            f"${total_financial_loss:,.2f} Million"
        ],
        [
            "Average Resolution Time",
            f"{average_resolution_time:,.2f} Hours"
        ],
        ["Countries Affected", str(total_countries)],
        ["Attack Types Identified", str(total_attack_types)]
    ]

    table = Table(
        overview_table,
        colWidths=[3.0 * inch, 2.5 * inch]
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
        ])
    )

    story.append(table)


    # ---------------------------------------------------------
    # 4. COUNTRY-WISE ANALYSIS
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "4. Country-wise Incident Analysis",
            heading_style
        )
    )

    country_counts = (
        df["Country"]
        .value_counts()
        .reset_index()
    )

    country_counts.columns = [
        "Country",
        "Incidents"
    ]

    country_financial = (
        df.groupby("Country")[
            "Financial Loss (in Million $)"
        ]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    country_users = (
        df.groupby("Country")[
            "Number of Affected Users"
        ]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    top_country = country_counts.iloc[0]["Country"]
    top_country_incidents = country_counts.iloc[0]["Incidents"]

    lowest_country = country_counts.iloc[-1]["Country"]
    lowest_country_incidents = country_counts.iloc[-1]["Incidents"]

    story.append(
        Paragraph(
            f"The country with the highest number of reported incidents "
            f"is <b>{top_country}</b>, with {top_country_incidents:,} incidents.",
            normal_style
        )
    )

    story.append(
        Paragraph(
            f"The country with the lowest number of reported incidents "
            f"is <b>{lowest_country}</b>, with {lowest_country_incidents:,} incidents.",
            normal_style
        )
    )

    story.append(
        Paragraph(
            "Top Countries by Incident Count",
            subheading_style
        )
    )

    country_table_data = [
        ["Rank", "Country", "Incidents"]
    ]

    for i, row in country_counts.head(10).iterrows():
        country_table_data.append([
            str(i + 1),
            str(row["Country"]),
            f"{int(row['Incidents']):,}"
        ])

    table = Table(
        country_table_data,
        colWidths=[0.7 * inch, 3.0 * inch, 1.5 * inch]
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (0, 0), (0, -1), "CENTER")
        ])
    )

    story.append(table)

    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            "Top Countries by Financial Loss",
            subheading_style
        )
    )

    country_loss_table = [
        ["Country", "Financial Loss ($ Million)"]
    ]

    for country, loss in country_financial.items():
        country_loss_table.append([
            str(country),
            f"{loss:,.2f}"
        ])

    table = Table(
        country_loss_table,
        colWidths=[3.5 * inch, 2.0 * inch]
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8)
        ])
    )

    story.append(table)


    # ---------------------------------------------------------
    # 5. ATTACK TYPE ANALYSIS
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "5. Attack Type Analysis",
            heading_style
        )
    )

    attack_counts = (
        df["Attack Type"]
        .value_counts()
        .reset_index()
    )

    attack_counts.columns = [
        "Attack Type",
        "Incidents"
    ]

    attack_loss = (
        df.groupby("Attack Type")[
            "Financial Loss (in Million $)"
        ]
        .sum()
        .sort_values(ascending=False)
    )

    attack_users = (
        df.groupby("Attack Type")[
            "Number of Affected Users"
        ]
        .sum()
        .sort_values(ascending=False)
    )

    attack_resolution = (
        df.groupby("Attack Type")[
            "Incident Resolution Time (in Hours)"
        ]
        .mean()
        .sort_values(ascending=False)
    )

    most_common_attack = attack_counts.iloc[0]["Attack Type"]

    highest_loss_attack = attack_loss.index[0]

    highest_users_attack = attack_users.index[0]

    longest_resolution_attack = attack_resolution.index[0]

    story.append(
        Paragraph(
            f"The most common attack type is "
            f"<b>{most_common_attack}</b>.",
            normal_style
        )
    )

    story.append(
        Paragraph(
            f"The attack type associated with the highest total "
            f"financial loss is <b>{highest_loss_attack}</b>.",
            normal_style
        )
    )

    story.append(
        Paragraph(
            f"The attack type affecting the highest number of users "
            f"is <b>{highest_users_attack}</b>.",
            normal_style
        )
    )

    story.append(
        Paragraph(
            f"The attack type with the longest average resolution "
            f"time is <b>{longest_resolution_attack}</b>.",
            normal_style
        )
    )

    attack_table_data = [
        [
            "Attack Type",
            "Incidents",
            "Financial Loss",
            "Affected Users",
            "Avg Resolution"
        ]
    ]

    for attack in attack_counts["Attack Type"]:

        incidents = len(
            df[df["Attack Type"] == attack]
        )

        loss = df.loc[
            df["Attack Type"] == attack,
            "Financial Loss (in Million $)"
        ].sum()

        users = df.loc[
            df["Attack Type"] == attack,
            "Number of Affected Users"
        ].sum()

        resolution = df.loc[
            df["Attack Type"] == attack,
            "Incident Resolution Time (in Hours)"
        ].mean()

        attack_table_data.append([
            str(attack),
            f"{incidents:,}",
            f"{loss:,.2f}",
            f"{users:,}",
            f"{resolution:,.2f}"
        ])

    table = Table(
        attack_table_data,
        colWidths=[
            1.5 * inch,
            0.8 * inch,
            1.1 * inch,
            1.1 * inch,
            1.0 * inch
        ],
        repeatRows=1
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
        ])
    )

    story.append(table)


    # ---------------------------------------------------------
    # 6. TARGET INDUSTRY ANALYSIS
    # ---------------------------------------------------------

    story.append(
    Paragraph(
        "6. Target Industry Analysis",
        heading_style
    )
    )

    industry_counts = (
        df["Target Industry"]
        .value_counts()
    )

    top_industry = industry_counts.index[0]

    story.append(
        Paragraph(
            f"The most targeted industry is "
            f"<b>{top_industry}</b>, with "
            f"{industry_counts.iloc[0]:,} incidents.",
            normal_style
        )
    )

    industry_table_data = [
        ["Target Industry", "Incidents"]
    ]

    for industry, count in industry_counts.head(10).items():
        industry_table_data.append([
            str(industry),
            f"{count:,}"
        ])

    table = Table(
        industry_table_data,
        colWidths=[4.0 * inch, 1.5 * inch]
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8)
        ])
    )

    story.append(table)


    # ---------------------------------------------------------
    # 7. ATTACK SOURCE ANALYSIS
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "7. Attack Source Analysis",
            heading_style
        )
    )

    source_counts = (
        df["Attack Source"]
        .value_counts()
    )

    top_source = source_counts.index[0]

    story.append(
        Paragraph(
            f"The most frequently recorded attack source is "
            f"<b>{top_source}</b>, accounting for "
            f"{source_counts.iloc[0]:,} incidents.",
            normal_style
        )
    )

    source_table = [
        ["Attack Source", "Incidents"]
    ]

    for source, count in source_counts.items():
        source_table.append([
            str(source),
            f"{count:,}"
        ])

    table = Table(
        source_table,
        colWidths=[4.0 * inch, 1.5 * inch]
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8)
        ])
    )

    story.append(table)


    # ---------------------------------------------------------
    # 8. SECURITY VULNERABILITY ANALYSIS
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "8. Security Vulnerability Analysis",
            heading_style
        )
    )

    vulnerability_counts = (
        df["Security Vulnerability Type"]
        .value_counts()
    )

    top_vulnerability = vulnerability_counts.index[0]

    story.append(
        Paragraph(
            f"The most frequently identified security vulnerability "
            f"type is <b>{top_vulnerability}</b>, with "
            f"{vulnerability_counts.iloc[0]:,} incidents.",
            normal_style
        )
    )

    vulnerability_table = [
        ["Security Vulnerability Type", "Incidents"]
    ]

    for vulnerability, count in vulnerability_counts.items():
        vulnerability_table.append([
            str(vulnerability),
            f"{count:,}"
        ])

    table = Table(
        vulnerability_table,
        colWidths=[4.0 * inch, 1.5 * inch]
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8)
        ])
    )

    story.append(table)


    # ---------------------------------------------------------
    # 9. DEFENSE MECHANISM ANALYSIS
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "9. Defense Mechanism Analysis",
            heading_style
        )
    )

    defense_counts = (
        df["Defense Mechanism Used"]
        .value_counts()
    )

    top_defense = defense_counts.index[0]

    story.append(
        Paragraph(
            f"The most frequently recorded defense mechanism is "
            f"<b>{top_defense}</b>, associated with "
            f"{defense_counts.iloc[0]:,} incidents.",
            normal_style
        )
    )

    defense_table = [
        ["Defense Mechanism", "Incidents"]
    ]

    for defense, count in defense_counts.items():
        defense_table.append([
            str(defense),
            f"{count:,}"
        ])

    table = Table(
        defense_table,
        colWidths=[4.0 * inch, 1.5 * inch]
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8)
        ])
    )

    story.append(table)


    # ---------------------------------------------------------
    # 10. INCIDENT RESOLUTION ANALYSIS
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "10. Incident Resolution Analysis",
            heading_style
        )
    )

    max_resolution = df[
        "Incident Resolution Time (in Hours)"
    ].max()

    min_resolution = df[
        "Incident Resolution Time (in Hours)"
    ].min()

    story.append(
        Paragraph(
            f"The average incident resolution time is "
            f"<b>{average_resolution_time:,.2f} hours</b>.",
            normal_style
        )
    )

    story.append(
        Paragraph(
            f"The shortest recorded resolution time is "
            f"<b>{min_resolution:,.2f} hours</b>, while the longest "
            f"recorded resolution time is "
            f"<b>{max_resolution:,.2f} hours</b>.",
            normal_style
        )
    )


    # ---------------------------------------------------------
    # 11. MAJOR FINDINGS
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "11. Major Findings & Insights",
            heading_style
        )
    )

    findings = [
        f"The dataset contains {total_incidents:,} cybersecurity incidents.",
        f"The incidents cover {total_countries} countries.",
        f"{most_common_attack} is the most frequently observed attack type.",
        f"{top_country} recorded the highest number of incidents.",
        f"{top_industry} is the most targeted industry.",
        f"{top_source} is the most frequently recorded attack source.",
        f"{top_vulnerability} is the most frequently identified vulnerability.",
        f"{top_defense} is the most frequently recorded defense mechanism.",
        f"The total estimated financial loss is ${total_financial_loss:,.2f} million.",
        f"The total number of affected users is {total_affected_users:,}.",
        f"The average incident resolution time is {average_resolution_time:,.2f} hours."
    ]

    for finding in findings:

        story.append(
            Paragraph(
                "• " + finding,
                normal_style
            )
        )


    # ---------------------------------------------------------
    # 12. MACHINE LEARNING RESULTS
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "12. Machine Learning Results",
            heading_style
        )
    )

    import os

    model_path = "models/crime_model.pkl"

    if os.path.exists(model_path):

        story.append(
            Paragraph(
                "A machine learning model has been trained and saved "
                "for attack type prediction. The model is integrated "
                "with the Internet Crime Analytics Platform and can be "
                "used to predict the possible attack type based on "
                "selected incident characteristics.",
                normal_style
            )
        )

        ml_table = [
            ["Machine Learning Component", "Details"],
            ["Model Status", "Trained model available"],
            ["Model File", "crime_model.pkl"],
            ["Prediction Target", "Attack Type"],
            ["Purpose", "Cybersecurity Attack Type Prediction"]
        ]

        table = Table(
            ml_table,
            colWidths=[3.0 * inch, 2.5 * inch]
        )

        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8)
            ])
        )

        story.append(table)

    else:

        story.append(
            Paragraph(
                "Machine learning model file was not found. "
                "The prediction module can be enabled after training "
                "and saving the machine learning model.",
                normal_style
            )
        )


    # ---------------------------------------------------------
    # 13. CONCLUSION
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "13. Conclusion",
            heading_style
        )
    )

    conclusion_text = (
        "The Internet Crime Analytics Platform provides a structured "
        "approach for analyzing cybersecurity incidents using data "
        "analytics techniques. The analysis identifies important "
        "patterns related to countries, attack types, target industries, "
        "attack sources, vulnerabilities, defense mechanisms, financial "
        "losses, affected users, and incident resolution time. These "
        "insights can help organizations better understand cybersecurity "
        "risks and support data-driven security planning."
    )

    story.append(
        Paragraph(
            conclusion_text,
            normal_style
        )
    )


    # ---------------------------------------------------------
    # 14. RECOMMENDATIONS & FUTURE SCOPE
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "14. Recommendations & Future Scope",
            heading_style
        )
    )

    recommendations = [
        "Expand the dataset by including more countries and recent cybersecurity incidents.",
        "Integrate real-time cybersecurity incident data for continuous monitoring.",
        "Improve machine learning models using additional relevant features.",
        "Add advanced prediction and classification techniques.",
        "Develop more detailed geographical and industry-level analysis.",
    ]

    for recommendation in recommendations:

        story.append(
            Paragraph(
                "• " + recommendation,
                normal_style
            )
        )


    # ---------------------------------------------------------
    # FOOTER
    # ---------------------------------------------------------

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "Internet Crime Analytics Platform | MSc Data Analytics Project",
            ParagraphStyle(
                "Footer",
                parent=normal_style,
                alignment=TA_CENTER,
                fontSize=8
            )
        )
    )


    # ---------------------------------------------------------
    # BUILD PDF
    # ---------------------------------------------------------

    document.build(story)
# ============================================================
# APPLICATION TITLE
# ============================================================

st.title("🔐 Internet Crime Analytics Platform")

st.write(
    "An interactive platform for analyzing global cybersecurity incidents."
)


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "🏠 Dashboard",
        "📊 Crime Analysis",
        "📈 Crime Trends",
        "🔎 Data Explorer",
        "🤖 Prediction",
        "📄 Reports"
    ]
)


# ============================================================
# PART 13 — DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.header("🏠 Dashboard")

    st.write(
        "Interactive overview of global cybersecurity incidents "
        "from 2015 to 2024."
    )


    # ========================================================
    # DASHBOARD FILTERS
    # ========================================================

    st.subheader("🎛️ Dashboard Filters")

    filter_col1, filter_col2 = st.columns(2)


    # Year filter
    with filter_col1:

        min_year = int(df["Year"].min())
        max_year = int(df["Year"].max())

        selected_years = st.slider(
            "Select Year Range",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year)
        )


    # Country filter
    with filter_col2:

        country_options = sorted(
            df["Country"].unique().tolist()
        )

        selected_countries = st.multiselect(
            "Select Countries",
            country_options,
            default=country_options
        )


    # ========================================================
    # APPLY DASHBOARD FILTERS
    # ========================================================

    dashboard_df = df[
        (df["Year"] >= selected_years[0]) &
        (df["Year"] <= selected_years[1])
    ]


    if selected_countries:

        dashboard_df = dashboard_df[
            dashboard_df["Country"].isin(selected_countries)
        ]


    # ========================================================
    # KPI CALCULATIONS
    # ========================================================

    total_incidents = len(dashboard_df)

    total_countries = dashboard_df["Country"].nunique()

    total_affected_users = dashboard_df[
        "Number of Affected Users"
    ].sum()

    total_financial_loss = dashboard_df[
        "Financial Loss (in Million $)"
    ].sum()

    total_attack_types = dashboard_df[
        "Attack Type"
    ].nunique()

    average_resolution_time = dashboard_df[
        "Incident Resolution Time (in Hours)"
    ].mean()


    # ========================================================
    # KPI CARDS — ROW 1
    # ========================================================

    st.markdown(
        '<div class="section-title">📌 Key Performance Indicators</div>',
        unsafe_allow_html=True
    )


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">🚨</div>
                <div class="kpi-title">Total Incidents</div>
                <div class="kpi-value">{total_incidents:,}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with col2:

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">🌍</div>
                <div class="kpi-title">Countries Affected</div>
                <div class="kpi-value">{total_countries:,}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with col3:

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">👥</div>
                <div class="kpi-title">Affected Users</div>
                <div class="kpi-value">{total_affected_users:,}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with col4:

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">💰</div>
                <div class="kpi-title">Financial Loss ($ Million)</div>
                <div class="kpi-value">{total_financial_loss:,.2f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # KPI CARDS — ROW 2
    # ========================================================

    col5, col6, col7, col8 = st.columns(4)


    with col5:

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">🛡️</div>
                <div class="kpi-title">Attack Types</div>
                <div class="kpi-value">{total_attack_types}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with col6:

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">⏱️</div>
                <div class="kpi-title">Avg. Resolution Time</div>
                <div class="kpi-value">{average_resolution_time:.2f} hrs</div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with col7:

        if len(dashboard_df) > 0:

            most_common_attack = (
                dashboard_df["Attack Type"]
                .value_counts()
                .idxmax()
            )

        else:

            most_common_attack = "N/A"


        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">⚠️</div>
                <div class="kpi-title">Most Common Attack</div>
                <div class="kpi-value">{most_common_attack}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with col8:

        if len(dashboard_df) > 0:

            highest_loss_attack = (
                dashboard_df.groupby("Attack Type")[
                    "Financial Loss (in Million $)"
                ]
                .sum()
                .idxmax()
            )

        else:

            highest_loss_attack = "N/A"


        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">💸</div>
                <div class="kpi-title">Highest Loss Attack</div>
                <div class="kpi-value">{highest_loss_attack}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # CHART 1 — ATTACK TYPE
    # ========================================================

    chart_col1, chart_col2 = st.columns(2)


    with chart_col1:

        st.subheader("📊 Incidents by Attack Type")


        attack_counts = (
            dashboard_df["Attack Type"]
            .value_counts()
            .reset_index()
        )


        attack_counts.columns = [
            "Attack Type",
            "Number of Incidents"
        ]


        fig1 = px.bar(
            attack_counts,
            x="Attack Type",
            y="Number of Incidents",
            title="Cyber Incidents by Attack Type",
            text="Number of Incidents"
        )


        fig1.update_layout(
            hovermode="x unified",
            margin=dict(l=20, r=20, t=60, b=20)
        )


        st.plotly_chart(
            fig1,
            use_container_width=True
        )


    # ========================================================
    # CHART 2 — YEARLY TREND
    # ========================================================

    with chart_col2:

        st.subheader("📈 Year-wise Incident Trend")


        year_counts = (
            dashboard_df
            .groupby("Year")
            .size()
            .reset_index(
                name="Number of Incidents"
            )
        )


        fig2 = px.line(
            year_counts,
            x="Year",
            y="Number of Incidents",
            markers=True,
            title="Cyber Incidents Over the Years"
        )


        fig2.update_layout(
            hovermode="x unified",
            margin=dict(l=20, r=20, t=60, b=20)
        )


        st.plotly_chart(
            fig2,
            use_container_width=True
        )


    # ========================================================
    # CHART 3 — FINANCIAL LOSS
    # ========================================================

    chart_col3, chart_col4 = st.columns(2)


    with chart_col3:

        st.subheader("💰 Financial Loss by Attack Type")


        financial_by_attack = (
            dashboard_df
            .groupby("Attack Type")[
                "Financial Loss (in Million $)"
            ]
            .sum()
            .reset_index()
        )


        fig3 = px.bar(
            financial_by_attack,
            x="Attack Type",
            y="Financial Loss (in Million $)",
            title="Financial Loss by Attack Type",
            text="Financial Loss (in Million $)"
        )


        fig3.update_layout(
            hovermode="x unified",
            margin=dict(l=20, r=20, t=60, b=20)
        )


        st.plotly_chart(
            fig3,
            use_container_width=True
        )


    # ========================================================
    # CHART 4 — COUNTRY
    # ========================================================

    with chart_col4:

        st.subheader("🌍 Incidents by Country")


        country_counts = (
            dashboard_df["Country"]
            .value_counts()
            .reset_index()
        )


        country_counts.columns = [
            "Country",
            "Number of Incidents"
        ]


        fig4 = px.bar(
            country_counts,
            x="Country",
            y="Number of Incidents",
            title="Cyber Incidents by Country",
            text="Number of Incidents"
        )


        fig4.update_layout(
            hovermode="x unified",
            margin=dict(l=20, r=20, t=60, b=20)
        )


        st.plotly_chart(
            fig4,
            use_container_width=True
        )


    # ========================================================
    # INFORMATION BOX
    # ========================================================

    st.markdown(
        f"""
        <div class="info-box">
            <b>📌 Dashboard Summary</b><br>
            The dashboard currently displays 
            <b>{total_incidents:,}</b> cybersecurity incidents
            across <b>{total_countries}</b> countries for the selected
            period from <b>{selected_years[0]}</b> to
            <b>{selected_years[1]}</b>.
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# PART 14 — DATA EXPLORER
# ============================================================

elif page == "🔎 Data Explorer":

    st.header("🔎 Data Explorer")

    st.write(
        "Explore and filter cybersecurity incident records "
        "from the dataset."
    )


    # --------------------------------------------------------
    # YEAR FILTER
    # --------------------------------------------------------

    year_options = ["All"] + sorted(
        df["Year"].unique().tolist()
    )


    selected_year = st.selectbox(
        "Select Year",
        year_options
    )


    # --------------------------------------------------------
    # COUNTRY FILTER
    # --------------------------------------------------------

    country_options = ["All"] + sorted(
        df["Country"].unique().tolist()
    )


    selected_country = st.selectbox(
        "Select Country",
        country_options
    )


    # --------------------------------------------------------
    # ATTACK TYPE FILTER
    # --------------------------------------------------------

    attack_options = ["All"] + sorted(
        df["Attack Type"].unique().tolist()
    )


    selected_attack = st.selectbox(
        "Select Attack Type",
        attack_options
    )


    # --------------------------------------------------------
    # TARGET INDUSTRY FILTER
    # --------------------------------------------------------

    industry_options = ["All"] + sorted(
        df["Target Industry"].unique().tolist()
    )


    selected_industry = st.selectbox(
        "Select Target Industry",
        industry_options
    )


    # --------------------------------------------------------
    # APPLY FILTERS
    # --------------------------------------------------------

    filtered_df = df.copy()


    if selected_year != "All":

        filtered_df = filtered_df[
            filtered_df["Year"] == selected_year
        ]


    if selected_country != "All":

        filtered_df = filtered_df[
            filtered_df["Country"] == selected_country
        ]


    if selected_attack != "All":

        filtered_df = filtered_df[
            filtered_df["Attack Type"] == selected_attack
        ]


    if selected_industry != "All":

        filtered_df = filtered_df[
            filtered_df["Target Industry"] == selected_industry
        ]


    # --------------------------------------------------------
    # DISPLAY FILTERED DATA
    # --------------------------------------------------------

    st.subheader("📋 Filtered Records")


    st.write(
        f"Showing {len(filtered_df)} records."
    )


    st.dataframe(
        filtered_df,
        use_container_width=True
    )


    # --------------------------------------------------------
    # DOWNLOAD FILTERED DATA
    # --------------------------------------------------------

    csv_data = filtered_df.to_csv(
        index=False
    ).encode("utf-8")


    st.download_button(
        label="⬇️ Download CSV",
        data=csv_data,
        file_name="filtered_internet_crime_data.csv",
        mime="text/csv"
    )


# ============================================================
# PART 15 — CRIME ANALYSIS
# ============================================================

elif page == "📊 Crime Analysis":

    st.header("📊 Crime Analysis")

    st.write(
        "Detailed analysis of cybersecurity incidents based "
        "on attack type, country, industry, financial loss, "
        "and affected users."
    )


    # --------------------------------------------------------
    # ATTACK TYPE ANALYSIS
    # --------------------------------------------------------

    attack_counts = (
        df["Attack Type"]
        .value_counts()
    )


    most_common_attack = (
        attack_counts.idxmax()
    )


    most_common_count = (
        attack_counts.max()
    )


    least_common_attack = (
        attack_counts.idxmin()
    )


    least_common_count = (
        attack_counts.min()
    )


    # --------------------------------------------------------
    # FINANCIAL LOSS ANALYSIS
    # --------------------------------------------------------

    financial_by_attack = (
        df.groupby("Attack Type")[
            "Financial Loss (in Million $)"
        ]
        .sum()
        .sort_values(ascending=False)
    )


    highest_loss_attack = (
        financial_by_attack.idxmax()
    )


    highest_loss_value = (
        financial_by_attack.max()
    )


    # --------------------------------------------------------
    # ANALYSIS CARDS
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Most Common Attack",
            most_common_attack
        )

        st.write(
            f"Incidents: {most_common_count}"
        )


    with col2:

        st.metric(
            "Least Common Attack",
            least_common_attack
        )

        st.write(
            f"Incidents: {least_common_count}"
        )


    with col3:

        st.metric(
            "Highest Financial Loss",
            highest_loss_attack
        )

        st.write(
            f"Loss: ${highest_loss_value:.2f} Million"
        )


    # --------------------------------------------------------
    # CHART 1 — ATTACK TYPE DISTRIBUTION
    # --------------------------------------------------------

    st.subheader("📊 Attack Type Distribution")


    attack_distribution = (
        df["Attack Type"]
        .value_counts()
        .reset_index()
    )


    attack_distribution.columns = [
        "Attack Type",
        "Number of Incidents"
    ]


    fig1 = px.bar(
        attack_distribution,
        x="Attack Type",
        y="Number of Incidents",
        title="Cybersecurity Incidents by Attack Type",
        text="Number of Incidents"
    )


    st.plotly_chart(
        fig1,
        use_container_width=True
    )


    # --------------------------------------------------------
    # CHART 2 — FINANCIAL LOSS
    # --------------------------------------------------------

    st.subheader("💰 Financial Loss by Attack Type")


    financial_chart = (
        df.groupby("Attack Type")[
            "Financial Loss (in Million $)"
        ]
        .sum()
        .reset_index()
    )


    fig2 = px.bar(
        financial_chart,
        x="Attack Type",
        y="Financial Loss (in Million $)",
        title="Total Financial Loss by Attack Type",
        text="Financial Loss (in Million $)"
    )


    st.plotly_chart(
        fig2,
        use_container_width=True
    )


    # --------------------------------------------------------
    # CHART 3 — AFFECTED USERS
    # --------------------------------------------------------

    st.subheader("👥 Affected Users by Attack Type")


    users_by_attack = (
        df.groupby("Attack Type")[
            "Number of Affected Users"
        ]
        .sum()
        .reset_index()
    )


    fig3 = px.bar(
        users_by_attack,
        x="Attack Type",
        y="Number of Affected Users",
        title="Total Affected Users by Attack Type",
        text="Number of Affected Users"
    )


    st.plotly_chart(
        fig3,
        use_container_width=True
    )


    # --------------------------------------------------------
    # CHART 4 — COUNTRY DISTRIBUTION
    # --------------------------------------------------------

    st.subheader("🌍 Incident Distribution by Country")


    country_distribution = (
        df["Country"]
        .value_counts()
        .reset_index()
    )


    country_distribution.columns = [
        "Country",
        "Number of Incidents"
    ]


    fig4 = px.bar(
        country_distribution,
        x="Country",
        y="Number of Incidents",
        title="Cybersecurity Incidents by Country",
        text="Number of Incidents"
    )


    st.plotly_chart(
        fig4,
        use_container_width=True
    )


    # --------------------------------------------------------
    # CHART 5 — TARGET INDUSTRY
    # --------------------------------------------------------

    st.subheader("🏢 Target Industry Distribution")


    industry_distribution = (
        df["Target Industry"]
        .value_counts()
        .reset_index()
    )


    industry_distribution.columns = [
        "Target Industry",
        "Number of Incidents"
    ]


    fig5 = px.bar(
        industry_distribution,
        x="Target Industry",
        y="Number of Incidents",
        title="Cybersecurity Incidents by Target Industry",
        text="Number of Incidents"
    )


    st.plotly_chart(
        fig5,
        use_container_width=True
    )


# ============================================================
# PART 16 — CRIME TRENDS
# ============================================================

elif page == "📈 Crime Trends":

    st.header("📈 Crime Trends")

    st.write(
        "Analyze yearly trends in cybersecurity incidents, "
        "financial losses, and affected users."
    )


    # --------------------------------------------------------
    # YEAR-WISE INCIDENTS
    # --------------------------------------------------------

    yearly_incidents = (
        df.groupby("Year")
        .size()
        .reset_index(
            name="Number of Incidents"
        )
    )


    # --------------------------------------------------------
    # CHART 1 — INCIDENT TREND
    # --------------------------------------------------------

    st.subheader(
        "📈 Year-wise Cybersecurity Incidents"
    )


    fig1 = px.line(
        yearly_incidents,
        x="Year",
        y="Number of Incidents",
        markers=True,
        title="Cybersecurity Incidents Over the Years"
    )


    st.plotly_chart(
        fig1,
        use_container_width=True
    )


    # --------------------------------------------------------
    # HIGHEST INCIDENT YEAR
    # --------------------------------------------------------

    highest_incident_year = (
        yearly_incidents.loc[
            yearly_incidents["Number of Incidents"].idxmax(),
            "Year"
        ]
    )


    highest_incident_count = (
        yearly_incidents[
            "Number of Incidents"
        ].max()
    )


    st.info(
        f"📌 The year with the highest number of incidents "
        f"was {highest_incident_year}, with "
        f"{highest_incident_count} incidents."
    )


    # --------------------------------------------------------
    # YEAR-WISE FINANCIAL LOSS
    # --------------------------------------------------------

    yearly_financial_loss = (
        df.groupby("Year")[
            "Financial Loss (in Million $)"
        ]
        .sum()
        .reset_index()
    )


    # --------------------------------------------------------
    # CHART 2 — FINANCIAL LOSS TREND
    # --------------------------------------------------------

    st.subheader(
        "💰 Year-wise Financial Loss"
    )


    fig2 = px.line(
        yearly_financial_loss,
        x="Year",
        y="Financial Loss (in Million $)",
        markers=True,
        title="Financial Loss Over the Years"
    )


    st.plotly_chart(
        fig2,
        use_container_width=True
    )


    # --------------------------------------------------------
    # YEAR-WISE AFFECTED USERS
    # --------------------------------------------------------

    yearly_affected_users = (
        df.groupby("Year")[
            "Number of Affected Users"
        ]
        .sum()
        .reset_index()
    )


    # --------------------------------------------------------
    # CHART 3 — AFFECTED USERS TREND
    # --------------------------------------------------------

    st.subheader(
        "👥 Year-wise Affected Users"
    )


    fig3 = px.line(
        yearly_affected_users,
        x="Year",
        y="Number of Affected Users",
        markers=True,
        title="Affected Users Over the Years"
    )


    st.plotly_chart(
        fig3,
        use_container_width=True
    )


    # --------------------------------------------------------
    # YEAR-WISE SUMMARY
    # --------------------------------------------------------

    st.subheader(
        "📋 Year-wise Summary"
    )


    yearly_summary = (
        yearly_incidents
        .merge(
            yearly_financial_loss,
            on="Year"
        )
        .merge(
            yearly_affected_users,
            on="Year"
        )
    )


    st.dataframe(
        yearly_summary,
        use_container_width=True
    )


# ============================================================
# PART 19 — PREDICTION PAGE
# ============================================================

elif page == "🤖 Prediction":

    st.header("🤖 Attack Type Prediction")

    st.write(
        "Use the trained machine learning model to predict "
        "the possible attack type of a cybersecurity incident."
    )

    if ml_model is None:

        st.error(
            "Machine learning model not found. "
            "Please train and save the model first."
        )

    else:

        

        st.subheader("📝 Enter Incident Details")

        col1, col2 = st.columns(2)

        with col1:

            selected_country = st.selectbox(
                "🌍 Country",
                sorted(df["Country"].unique().tolist())
            )

        with col2:

            selected_year = st.selectbox(
                "📅 Year",
                sorted(df["Year"].unique().tolist())
            )

        with col1:

            selected_industry = st.selectbox(
                "🏢 Target Industry",
                sorted(df["Target Industry"].unique().tolist())
            )

        with col2:

            selected_source = st.selectbox(
                "🎯 Attack Source",
                sorted(df["Attack Source"].unique().tolist())
            )

        selected_vulnerability = st.selectbox(
            "🔐 Security Vulnerability Type",
            sorted(
                df["Security Vulnerability Type"]
                .unique()
                .tolist()
            )
        )

        st.write("")

        predict_button = st.button(
            "🔮 Predict Attack Type",
            use_container_width=True
        )

        if predict_button:

            input_data = pd.DataFrame({
                "Country": [selected_country],
                "Year": [selected_year],
                "Target Industry": [selected_industry],
                "Attack Source": [selected_source],
                "Security Vulnerability Type": [
                    selected_vulnerability
                ]
            })

            prediction = ml_model.predict(input_data)

            predicted_attack = prediction[0]

            st.subheader("🎯 Prediction Result")

            st.success(
                f"Predicted Attack Type: {predicted_attack}"
            )

# ============================================================
# PART 22 — REPORTS PAGE
# ============================================================

elif page == "📄 Reports":

    st.header("📄 Analytics Report")

    st.write(
        "Generate a report PDF containing "
        "cybersecurity incident analysis, country-wise statistics, "
        "attack analysis, industry analysis, major findings, "
        "machine learning information, conclusion and future scope."
    )

    st.markdown("---")

    # Report contents
    st.subheader("📋 Report Contents")

    report_contents = [
        "Project Summary",
        "Dataset Overview",
        "Overall Cybersecurity Incident Overview",
        "Country-wise Incident Analysis",
        "Attack Type Analysis",
        "Target Industry Analysis",
        "Attack Source Analysis",
        "Security Vulnerability Analysis",
        "Defense Mechanism Analysis",
        "Incident Resolution Analysis",
        "Major Findings & Insights",
        "Machine Learning Results",
        "Conclusion",
        "Recommendations & Future Scope"
    ]

    for i, item in enumerate(report_contents, start=1):

        st.write(f"**{i}.** {item}")

    st.markdown("---")

    # Report button
    if st.button(
        "📄 Generate Professional PDF Report",
        use_container_width=True
    ):

        os.makedirs("reports", exist_ok=True)

        report_path = (
            "reports/Internet_Crime_Analytics_Report.pdf"
        )

        try:

            generate_pdf_report(
                df,
                report_path
            )

            st.info(
                "The report contains country-wise analysis, "
                "attack analysis, industry analysis, financial loss, "
                "affected users, vulnerabilities, defense mechanisms, "
                "major findings, ML information, conclusion and future scope."
            )

            with open(report_path, "rb") as pdf_file:

                pdf_data = pdf_file.read()

            st.download_button(
                label="⬇️ Download Professional PDF Report",
                data=pdf_data,
                file_name="Internet_Crime_Analytics_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        except Exception as e:

            st.error(
                f"❌ Error while generating report: {e}"
            )