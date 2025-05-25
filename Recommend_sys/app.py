import streamlit as st
import pandas as pd
from recommender import get_hybrid_recommendations

# Set up Streamlit page
st.set_page_config(page_title="Anime Recommender", layout="wide")

st.title("🎥 Anime Recommender")

# Search bar
search_query = st.text_input("Enter anime name:")

if search_query:
    st.subheader(f"🔍 Recommendations for: *{search_query}*")

    recommendations = get_hybrid_recommendations(search_query)

    if recommendations.empty:
        st.error("No recommendations found. Please try a different anime.")
    else:
        cols = st.columns(5)
        for i, (index, row) in enumerate(recommendations.iterrows()):
            with cols[i % 5]:
                if row["image_path"]:
                    st.image(row["image_path"], width=150, caption=row["name"])
                else:
                    st.markdown(f"**{row['name']}**")
                    st.caption("No image available.")
                st.caption(row["genre"])
