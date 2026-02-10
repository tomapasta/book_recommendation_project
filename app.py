import streamlit as st
import pandas as pd

# --------------------
# App setup
# --------------------
st.set_page_config(page_title="Book Mood Recommender", layout="wide")
st.title("📚 Book Lovers App")

@st.cache_data
def load_data():
    return pd.read_csv("data/processed/df_final_scored_with_descriptions.csv")

df = load_data()

# ====================
# SIDEBAR — Filters
# ====================
st.sidebar.header("Customize your search")

MOODS = {
    "📖 Easy Reading": "score_easy",
    "🚶 On the go": "score_on_the_go",
    "🌙 Relaxing Bedtime Stories": "score_bedtime",
    "🏖️ Beach Day": "score_beach",
    "🧠 Make me Smarter": "score_educational",
    "⚡ Adrenaline Rush": "score_adrenaline",
}

selected_mood_label = st.sidebar.selectbox(
    "Choose your mood",
    options=list(MOODS.keys())
)

selected_mood_col = MOODS[selected_mood_label]

STRICTNESS_OPTIONS = {
    "Balanced": "balanced",
    "Best match only": "best_only",
    "Broad / flexible": "broad",
}

selected_strictness_label = st.sidebar.radio(
    "Strictness",
    options=list(STRICTNESS_OPTIONS.keys())
)
selected_strictness = STRICTNESS_OPTIONS[selected_strictness_label]

max_pages = st.sidebar.slider(
    "Maximum pages",
    min_value=50,
    max_value=int(df["pages"].dropna().max()),
    value=500,
    step=25,
)

min_rating = st.sidebar.slider(
    "Minimum rating",
    min_value=0.0,
    max_value=5.0,
    value=3.5,
    step=0.1,
)

# ====================
# BUILD df_view (THIS WAS MISSING)
# ====================
df_view = df.copy()

# practical filters
df_view = df_view[
    (df_view["pages"].fillna(10_000) <= max_pages) &
    (df_view["rating"].fillna(0) >= min_rating)
]

# mood logic
if selected_strictness == "balanced":
    df_view = df_view.sort_values(selected_mood_col, ascending=False)

elif selected_strictness == "best_only":
    df_view = df_view[
        df_view["top_mood"] == selected_mood_col
    ].sort_values(
        ["top_mood_score", "rating_count"],
        ascending=[False, False]
    )

elif selected_strictness == "broad":
    broad_col = f"{selected_mood_col}_broad"
    df_view = df_view.sort_values(broad_col, ascending=False)

# limit results early
df_view = df_view.head(10)

# ====================
# RESULTS AREA — EXPANDERS
# ====================
st.markdown("---")
st.title("Your Book Matches")

if df_view.empty:
    st.info(
        "No books match those exact filters. "
        "Try increasing the Max Page Count or lowering the Minimum Rating."
    )
else:
    st.write(f"Found **{len(df_view)}** books matching your criteria.")

    # sort visually by rating
    for _, row in df_view.sort_values("rating", ascending=False).iterrows():
        with st.expander(f"{row['title']} — ⭐ {row['rating']:.2f}"):
            st.write(f"**Author:** {row['author']}")
            st.write(f"**Length:** {int(row['pages'])} pages")

            st.markdown("**Description:**")
            if pd.notna(row["description"]) and row["description"].strip():
                st.write(row["description"])
            else:
                st.write("No description available for this title.")

            st.divider()