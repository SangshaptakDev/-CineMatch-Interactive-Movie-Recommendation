import streamlit as st
import pandas as pd
import sqlite3
import joblib
from scipy import sparse
from sklearn.metrics.pairwise import linear_kernel
import os

# --- Load Data ---
def load_data():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "movies.sqlite"))
    print(f"Database path: {db_path}")  # Print to verify the path
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM movies", conn)
    conn.close()
    return df

df = load_data()

# --- Apply filters ---
def apply_filters(df, lang_filter, genre_filter, min_rating, min_year, max_year):
    filtered_df = df.copy()

    if genre_filter:
        filtered_df = filtered_df[filtered_df["Genre"].isin(genre_filter)]
    
    if lang_filter:
        filtered_df = filtered_df[filtered_df["Language"].isin(lang_filter)]

    filtered_df["Rating(10)"] = pd.to_numeric(filtered_df["Rating(10)"], errors='coerce')
    filtered_df = filtered_df[filtered_df["Rating(10)"] >= min_rating]

    filtered_df = filtered_df[(filtered_df["Year"] >= min_year) & (filtered_df["Year"] <= max_year)]
    
    return filtered_df

# --- Recommender Function ---
def get_recommendations(title, genre, n=10):
    # Get movies from the same genre
    recommendations = df[df["Genre"] == genre]
    recommendations = recommendations[recommendations["Movie Name"] != title]  # Remove the selected movie
    return recommendations[["Movie Name", "Rating(10)", "Genre", "Language"]].head(n)

# --- Set Background Image and Opacity ---
BACKGROUND_IMAGE_URL = "https://satyajitray.org/wp-content/uploads/2020/01/Hirak-Rajar-Deshe-NemaiGhosh-1024x677.jpg"
OPACITY = 0.85  # Set opacity value directly in the code

# Apply background with opacity
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{BACKGROUND_IMAGE_URL}");
        background-size: cover;
        opacity: {OPACITY};
        height: 100%;
    }}
    </style>
    """, unsafe_allow_html=True
)

st.title("🎬 CineMatch: Movie Recommender Engine")

# --- Sidebar Filters ---
with st.sidebar:
    st.header("🔍 Filter Movies")
    genre_filter = st.multiselect("Select Genre(s):", options=sorted(df["Genre"].dropna().unique()))
    lang_filter = st.multiselect("Select Language(s):", options=sorted(df["Language"].dropna().unique()))
    min_rating = st.slider("Minimum Rating", 0.0, 10.0, 5.0)
    min_year = st.slider("Year of Release Range:", 1913, 2024, (1913, 2024))
    max_year = min_year[1]
    
    # Apply filters to the data
    filtered_df = apply_filters(df, lang_filter, genre_filter, min_rating, min_year[0], max_year)
    st.write(f"🎯 Filtered Movies: {len(filtered_df)}")

# --- Page Navigation ---
page = st.selectbox("Select Page", ["Filtered Movies", "Recommendations"])

if page == "Filtered Movies":
    st.subheader("Filtered Movies:")
    if len(filtered_df) > 0:
        st.dataframe(filtered_df[["Movie Name", "Rating(10)", "Genre", "Language"]], use_container_width=True)
    else:
        st.write("No movies found based on selected filters.")

elif page == "Recommendations":
    st.subheader("🎥 Pick a Movie You Like:")
    if len(filtered_df) > 0:
        movie_list = filtered_df["Movie Name"].drop_duplicates().sort_values().tolist()
        selected_movie = st.selectbox("Choose a movie you like:", movie_list)

        if st.button("✨ Recommend"):
            # Get recommendations based on genre
            genre = filtered_df[filtered_df["Movie Name"] == selected_movie]["Genre"].iloc[0]
            recommendations = get_recommendations(selected_movie, genre)

            if recommendations.empty:
                st.warning("No recommendations found for this movie.")
            else:
                st.success(f"Top {len(recommendations)} recommendations for '{selected_movie}':")
                st.dataframe(recommendations.reset_index(drop=True), use_container_width=True)
    else:
        st.write("No movies found based on selected filters.")
