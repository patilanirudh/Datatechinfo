import os
import requests
import pandas as pd

# Load anime dataset
anime_df = pd.read_csv("data/anime.csv")

# Folder to store images
image_folder = "images/"
os.makedirs(image_folder, exist_ok=True)

# Base URL for Jikan API
BASE_URL = "https://api.jikan.moe/v4/anime"

# Function to download images
def download_anime_images():
    for index, row in anime_df.iterrows():
        anime_id = row["MAL_ID"]  # Adjust column name based on dataset
        anime_title = row["Name"]
        img_path = os.path.join(image_folder, f"{anime_id}.jpg")

        # Skip if the image already exists
        if os.path.exists(img_path):
            print(f"Skipping (Already Exists): {anime_title}")
            continue

        try:
            response = requests.get(f"{BASE_URL}/{anime_id}")
            data = response.json()
            image_url = data["data"]["images"]["jpg"]["image_url"]

            img_data = requests.get(image_url).content

            with open(img_path, "wb") as img_file:
                img_file.write(img_data)

            print(f"Downloaded: {anime_title}")

        except Exception as e:
            print(f"Failed: {anime_title} - {e}")

# Run image download function
download_anime_images()
