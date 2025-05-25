import os
import pandas as pd
import numpy as np

anime_df = pd.read_csv("anime_with_images.csv").drop_duplicates(subset=["anime_id"])
ratings_df = pd.read_csv("rating_with_images.csv").drop_duplicates(subset=["user_id", "anime_id"])

IMAGE_FOLDER = "images"

def get_anime_image(anime_id):
    """Returns image path if it exists, else None."""
    image_path = os.path.join(IMAGE_FOLDER, f"{anime_id}.jpg")
    return image_path if os.path.exists(image_path) else None

def get_popular_anime(top_n=5):
    """Returns top N popular anime by average rating."""
    top_anime_ids = ratings_df.groupby("anime_id")["rating"].mean().sort_values(ascending=False).head(top_n).index
    top_anime = anime_df[anime_df["anime_id"].isin(top_anime_ids)][["anime_id", "name", "genre"]]
    top_anime["image_path"] = top_anime["anime_id"].apply(get_anime_image)
    return top_anime

def get_hybrid_recommendations(anime_title, top_n=5):
    """Combines collaborative filtering and popularity-based recommendations."""
    collaborative_df = get_collaborative_recommendations(anime_title, top_n=top_n)

    if len(collaborative_df) >= top_n:
        return collaborative_df.head(top_n)

    # Fill remaining slots with popular anime not already recommended
    needed = top_n - len(collaborative_df)
    popular_df = get_popular_anime(top_n=top_n * 2)  # Get more to avoid duplicates
    if not collaborative_df.empty:
        popular_df = popular_df[~popular_df["anime_id"].isin(collaborative_df["anime_id"])]

    hybrid_df = pd.concat([collaborative_df, popular_df.head(needed)], ignore_index=True)
    return hybrid_df

def get_collaborative_recommendations(anime_title, top_n=5):
    if anime_title not in anime_df["name"].values:
        return pd.DataFrame(columns=["anime_id", "name", "genre", "image_path"])

    anime_id = anime_df.loc[anime_df["name"] == anime_title, "anime_id"].values[0]

    if anime_id not in ratings_df["anime_id"].unique():
        return pd.DataFrame(columns=["anime_id", "name", "genre", "image_path"])

    try:
        user_item_matrix = ratings_df.pivot_table(
            index="user_id", columns="anime_id", values="rating", aggfunc="mean"
        )

        anime_counts = ratings_df["anime_id"].value_counts()
        valid_anime_ids = anime_counts[anime_counts >= 10].index
        user_item_matrix = user_item_matrix[valid_anime_ids]

        if anime_id not in user_item_matrix:
            return pd.DataFrame(columns=["anime_id", "name", "genre", "image_path"])

        user_item_matrix = user_item_matrix.subtract(user_item_matrix.mean(axis=1), axis=0)
        target_ratings = user_item_matrix[anime_id].dropna()

        if len(target_ratings) < 2:
            return pd.DataFrame(columns=["anime_id", "name", "genre", "image_path"])

        similarities = {}
        for other_anime_id in user_item_matrix.columns:
            if other_anime_id == anime_id:
                continue

            other_ratings = user_item_matrix[other_anime_id].dropna()
            common_users = target_ratings.index.intersection(other_ratings.index)

            if len(common_users) >= 2:
                with np.errstate(divide='ignore', invalid='ignore'):
                    corr = np.corrcoef(
                        target_ratings.loc[common_users],
                        other_ratings.loc[common_users]
                    )[0, 1]

                if not np.isnan(corr) and corr != 0:
                    similarities[other_anime_id] = corr

        if not similarities:
            return pd.DataFrame(columns=["anime_id", "name", "genre", "image_path"])

        top_similar = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:top_n]
        top_ids = [anime_id for anime_id, _ in top_similar]

        recommended_anime = anime_df[anime_df["anime_id"].isin(top_ids)][["anime_id", "name", "genre"]]
        recommended_anime["image_path"] = recommended_anime["anime_id"].apply(get_anime_image)

        return recommended_anime

    except Exception as e:
        print(f"Error in collaborative filtering: {e}")
        return pd.DataFrame(columns=["anime_id", "name", "genre", "image_path"])
