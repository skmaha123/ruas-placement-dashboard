import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="RUAS Graduate Outcomes Dashboard- Directorate of Training and Placements",
    page_icon="",
    layout="wide"
)

# =====================================================
# STYLING
# =====================================================

st.markdown("""
<style>

.main{
    background:#F5F7FA;
}

.metric-container{
    background:white;
    padding:15px;
    border-radius:12px;
    box-shadow:0px 3px 8px rgba(0,0,0,0.1);
}

[data-testid="stMetric"]{
    background:white;
    padding:15px;
    border-radius:12px;
    border-left:5px solid #003366;
    box-shadow:0px 3px 8px rgba(0,0,0,0.1);
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

col1, col2 = st.columns([1,6])

with col1:
    try:
        st.image("assets/ruas_logo.png", width=100)
    except:
        pass

with col2:
    st.title("🎓 RUAS Graduate Outcomes Intelligence Dashboard")
    st.caption(
        "Placement, Higher Studies, Entrepreneurship & Graduate Outcome Analytics"
    )

# =====================================================
# FILE UPLOAD
# =====================================================

uploaded_file = st.sidebar.file_uploader(
    "Upload Graduate Outcomes Excel",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("Please upload the Graduate Outcomes Excel file.")
    st.stop()

# =====================================================
# LOAD DATA
# =====================================================

df = pd.read_excel(uploaded_file)

df.columns = (
    df.columns
      .astype(str)
      .str.strip()
)

# =====================================================
# FILTERS (ONLY 2)
# =====================================================

st.sidebar.markdown("---")
st.sidebar.subheader("Filters")

years = sorted(df["Year"].unique())

selected_year = st.sidebar.selectbox(
    "Select Year",
    ["All Years"] + list(years)
)

faculties = sorted(df["Faculty"].unique())

selected_faculty = st.sidebar.selectbox(
    "Select Faculty",
    ["All Faculties"] + list(faculties)
)

# =====================================================
# FILTER DATA
# =====================================================

filtered_df = df.copy()

if selected_year != "All Years":
    filtered_df = filtered_df[
        filtered_df["Year"] == selected_year
    ]

if selected_faculty != "All Faculties":
    filtered_df = filtered_df[
        filtered_df["Faculty"] == selected_faculty
    ]

# =====================================================
# KPI CALCULATIONS
# =====================================================

graduates = filtered_df["Graduates"].sum()

placed = filtered_df["Placed"].sum()

higher = filtered_df["Higher Studies"].sum()

entrepreneur = filtered_df["Entrepreneurship"].sum()

others = filtered_df["Others"].sum()

highest_ctc = filtered_df["Highest_CTC"].max()

average_ctc = filtered_df["Average_CTC"].mean()


placement_index = (
    (
        placed +
        higher +
        entrepreneur
    )
    /
    graduates * 100
    if graduates > 0 else 0
)



higher_rate = (
    higher / graduates * 100
    if graduates > 0 else 0
)

# =====================================================
# KPI CARDS
# =====================================================

st.markdown("## Executive KPI Summary")

c1,c2,c3,c4,c5 = st.columns(5)

c4.metric(
    "Higher Studies",
    f"{higher_rate:.1f}%"
)

c5.metric(
    "Entrepreneurs",
    f"{entrepreneur:,}"
)

c5,c6 = st.columns(2)

c5.metric("Highest CTC", f"₹{highest_ctc:,.0f}")
c6.metric("Average CTC", f"₹{average_ctc:,.0f}")

c1.metric(
    "Graduates",
    f"{graduates:,}"
)

c2.metric(
    "Placed",
    f"{placed:,}"
)

c3.metric(
    "Placement %",
    f"{placement_index:.1f}%"
)

# =====================================================
# ROW 1
# =====================================================

col1, col2 = st.columns(2)

# FUNNEL

with col1:

    st.subheader("Graduate Outcomes Funnel")

    fig = go.Figure(
        go.Funnel(
            y=[
                "Graduates",
                "Placed",
                "Higher Studies",
                "Entrepreneurship",
                "Others"
            ],
            x=[
                graduates,
                placed,
                higher,
                entrepreneur,
                others
            ]
        )
    )

    fig.update_layout(height=500)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# DONUT

with col2:

    st.subheader("Outcome Distribution")

    outcome_df = pd.DataFrame({
        "Outcome":[
            "Placed",
            "Higher Studies",
            "Entrepreneurship",
            "Others"
        ],
        "Count":[
            placed,
            higher,
            entrepreneur,
            others
        ]
    })

    fig = px.pie(
        outcome_df,
        names="Outcome",
        values="Count",
        hole=0.6,
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig.update_layout(height=500)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# ROW 2
# =====================================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("Faculty Placement Performance")

    perf_df = filtered_df.copy()
    perf_df["Placement Index"] = (
                                         (
                                                 perf_df["Placed"] +
                                                 perf_df["Higher Studies"] +
                                                 perf_df["Entrepreneurship"]
                                         )
                                         /
                                         perf_df["Graduates"]
                                 ) * 100
    fig = px.bar(
        perf_df,
        x="Faculty",
        y="Placement Index",
        color="Placement Index",
        text_auto=".1f",
        color_continuous_scale="Viridis"
    )
    fig.update_layout(height=550)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    st.subheader("Highest CTC by Faculty")

    fig = px.bar(
        filtered_df,
        x="Faculty",
        y="Highest_CTC",
        color="Highest_CTC",
        text="Highest_CTC",
        color_continuous_scale="Turbo"
    )

    fig.update_traces(
        texttemplate='₹%{y:,.0f}',
        textposition='outside'
    )

    fig.update_layout(height=550)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# ROW 3
# =====================================================

st.subheader("Graduate Outcomes by Faculty")

fig = px.bar(
    filtered_df,
    x="Faculty",
    y=[
        "Placed",
        "Higher Studies",
        "Entrepreneurship",
        "Others"
    ],
    barmode="stack",
    color_discrete_sequence=px.colors.qualitative.Pastel
)

fig.update_layout(height=600)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================================
# ROW 4
# =====================================================

st.subheader("Average CTC by Faculty")

fig = px.bar(
    filtered_df,
    x="Faculty",
    y="Average_CTC",
    color="Average_CTC",
    color_continuous_scale="Blues"
)

fig.update_layout(height=550)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================================
# PLACEMENT INDEX LEADERBOARD
# =====================================================

st.subheader("Placement Index by Faculty")

index_df = filtered_df.copy()

index_df["Placement Index"] = (
    (
        index_df["Placed"]
        + index_df["Higher Studies"]
        + index_df["Entrepreneurship"]
    )
    /
    index_df["Graduates"]
) * 100

fig = px.bar(
    index_df.sort_values(
        "Placement Index",
        ascending=False
    ),
    x="Faculty",
    y="Placement Index",
    color="Placement Index",
    text_auto=".1f",
    color_continuous_scale="RdYlGn"
)

fig.update_layout(height=600)

st.plotly_chart(
    fig,
    use_container_width=True
)



# =====================================================
# HEATMAP
# =====================================================

if selected_year == "All Years":

    st.subheader("Placement Success Heatmap")

    heat_df = df.copy()

    heat_df["Graduate Outcome %"] = (
                                            (
                                                    heat_df["Placed"] +
                                                    heat_df["Higher Studies"] +
                                                    heat_df["Entrepreneurship"]
                                            )
                                            /
                                            heat_df["Graduates"]
                                    ) * 100

    fig = px.density_heatmap(
        heat_df,
        x="Year",
        y="Faculty",
        z="Graduate Outcome %",
        color_continuous_scale="RdYlGn"
    )

    fig.update_layout(height=650)

    st.plotly_chart(
        fig,
        use_container_width=True
    )
# =====================================================
# FORECASTING
# =====================================================

st.markdown("---")
st.subheader("🔮 AI Placement Forecast (2027-2032)")

forecast_df = df.copy()

forecast_df["Outcome_Percentage"] = (
    (
        forecast_df["Placed"] +
        forecast_df["Higher Studies"] +
        forecast_df["Entrepreneurship"]
    )
    /
    forecast_df["Graduates"]
) * 100

faculty_selected = st.selectbox(
    "Faculty for Forecast",
    sorted(df["Faculty"].unique())
)

faculty_data = forecast_df[
    forecast_df["Faculty"] == faculty_selected
].copy()

faculty_data = faculty_data.sort_values(
    "Year"
)

if len(faculty_data) >= 3:

    X = faculty_data[
        [
            "Year",
            "Graduates",
            "Higher Studies",
            "Entrepreneurship"
        ]
    ]

    y = faculty_data["Outcome_Percentage"]

    model = RandomForestRegressor(
        n_estimators=500,
        random_state=42
    )

    model.fit(X, y)

    latest = faculty_data.iloc[-1]

    future_years = []

    current_graduates = latest["Graduates"]
    current_higher = latest["Higher Studies"]
    current_entrepreneur = latest["Entrepreneurship"]

    for yr in range(2027, 2033):

        pred = model.predict([[
            yr,
            current_graduates,
            current_higher,
            current_entrepreneur
        ]])[0]

        pred = min(max(pred, 0), 100)

        future_years.append({
            "Year": yr,
            "Predicted Outcome %": pred,
            "Expected Placed":
                round(
                    current_graduates *
                    pred / 100
                ),
            "Graduates":
                current_graduates
        })

        current_graduates = int(
            current_graduates * 1.02
        )

    pred_df = pd.DataFrame(
        future_years
    )

    col1, col2 = st.columns([2,1])

    with col1:

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=faculty_data["Year"],
                y=faculty_data["Outcome_Percentage"],
                mode="lines+markers",
                name="Historical",
                line=dict(
                    width=4,
                    color="#003366"
                )
            )
        )

        fig.add_trace(
            go.Scatter(
                x=pred_df["Year"],
                y=pred_df["Predicted Outcome %"],
                mode="lines+markers",
                name="Forecast",
                line=dict(
                    width=4,
                    color="green",
                    dash="dash"
                )
            )
        )

        fig.update_layout(
            title=f"{faculty_selected} Forecast",
            template="plotly_white",
            height=500,
            yaxis_title="Graduate Outcome %",
            xaxis_title="Year"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        st.markdown("### Predicted Trend")

        final_percent = pred_df.iloc[-1][
            "Predicted Outcome %"
        ]

        st.metric(
            "2032 Prediction",
            f"{final_percent:.1f}%"
        )

        expected = pred_df.iloc[-1][
            "Expected Placed"
        ]

        st.metric(
            "Expected Outcomes",
            expected
        )

    st.dataframe(
        pred_df,
        use_container_width=True
    )

else:

    st.warning(
        "Not enough historical data for forecasting."
    )
# =====================================================
# EXECUTIVE INSIGHTS
# =====================================================

st.subheader("Executive Insights")

rank_df = filtered_df.copy()

rank_df["Graduate Outcome %"] = (
    rank_df["Placed"]
    /
    rank_df["Graduates"]
) * 100

rank_df = rank_df.sort_values(
    "Graduate Outcome %",
    ascending=False
)

if len(rank_df) > 0:

    best_faculty = rank_df.iloc[0]["Faculty"]

    highest_package_faculty = filtered_df.loc[
        filtered_df["Highest_CTC"].idxmax(),
        "Faculty"
    ]

    st.success(f"""
🏆 Best Placement Faculty: {best_faculty}

💰 Highest Package Faculty: {highest_package_faculty}

📈 Placement Index: {placement_index:.1f}%

🎓 Higher Studies: {higher_rate:.1f}%
""")

# =====================================================
# DATA TABLE
# =====================================================

st.subheader("Detailed Dataset")

st.dataframe(
    filtered_df,
    use_container_width=True
)

# =====================================================
# DOWNLOAD
# =====================================================

csv = filtered_df.to_csv(index=False)

st.download_button(
    "📥 Download Filtered Data",
    csv,
    "graduate_outcomes.csv",
    "text/csv"
)

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.caption(
    "RUAS Graduate Outcomes Intelligence Dashboard"
)