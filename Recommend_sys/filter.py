import pandas as pd
import os

# Load CSVs
anime_df = pd.read_csv('data/anime.csv')
rating_df = pd.read_csv('data/rating.csv')

# Get list of image filenames in 'images/' folder
image_files = os.listdir('images')
# Extract anime IDs from image filenames by removing '.jpg' and converting to int
image_ids = [int(filename.split('.')[0]) for filename in image_files if filename.endswith('.jpg')]

# Filter anime and rating dataframes where anime_id exists in image_ids
anime_filtered = anime_df[anime_df['anime_id'].isin(image_ids)]
rating_filtered = rating_df[rating_df['anime_id'].isin(image_ids)]

# Save or use filtered data
anime_filtered.to_csv('anime_with_images.csv', index=False)
rating_filtered.to_csv('rating_with_images.csv', index=False)
