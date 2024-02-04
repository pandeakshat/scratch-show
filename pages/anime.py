

# Function to fetch anime image
def fetch_anime_image(anime_title):
    base_url = "https://api.jikan.moe/v4"
    search_url = f"{base_url}/anime?q={anime_title}&sfw"
    response = requests.get(search_url)
    data = response.json()

    if data and data['data']:
        first_result = data['data'][0]  # Assuming the first result is the desired one
        image_url = first_result['images']['jpg']['image_url']
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        return img
    return None

import streamlit as st
import pandas as pd
import requests
import os
from PIL import Image
from io import BytesIO

# Function to fetch anime image URL
def fetch_anime_image_url(anime_title):
    base_url = "https://api.jikan.moe/v4"
    search_url = f"{base_url}/anime?q={anime_title}&sfw"
    try:
        response = requests.get(search_url)
        data = response.json()

        if data and data['data']:
            first_result = data['data'][0]  # Assuming the first result is the desired one
            return first_result['images']['jpg']['image_url']
    except Exception as e:
        st.error(f"An error occurred while fetching image URL for '{anime_title}': {e}")
    return None

# Function to add anime to the database
def add_anime_to_csv(anime_name, watch_status, image_url, csv_file):
    df = pd.read_csv(csv_file)
    new_row = pd.DataFrame([[anime_name, watch_status, image_url]], columns=['name', 'watch', 'image_url'])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(csv_file, index=False)

# Function to update watch status
def update_watch_status(anime_name, new_watch_status, csv_file):
    df = pd.read_csv(csv_file)
    df.loc[df['name'] == anime_name, 'watch'] = new_watch_status
    df.to_csv(csv_file, index=False)

def get_image(image_url, is_watched):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    return img.convert('L') if is_watched else img
# Check for CSV file and create if not exists
csv_file = 'anime.csv'
if not os.path.exists(csv_file):
    df = pd.DataFrame(columns=['name', 'watch', 'image_url'])
    df.to_csv(csv_file, index=False)
else:
    df = pd.read_csv(csv_file)

# Streamlit layout
st.title("Anime Display")

# User input to add anime
with st.form("anime_form"):
    new_anime_name = st.text_input("Anime Name")
    new_watch_status = st.selectbox("Watch Status", options=[0, 1])
    submitted = st.form_submit_button("Add Anime")
    if submitted and new_anime_name:
        df = pd.read_csv(csv_file)
        if new_anime_name not in df['name'].values:
            image_url = fetch_anime_image_url(new_anime_name)
            if image_url:
                add_anime_to_csv(new_anime_name, new_watch_status, image_url, csv_file)
                st.success(f"Added '{new_anime_name}' to the database!")
            else:
                st.error("Failed to fetch image URL for the anime.")
        else:
            st.error("Anime already in the database.")

# Display anime images and buttons for updating watch status
df = pd.read_csv(csv_file)  # Reload the csv file to reflect any new additions
for index, row in df.iterrows():
    cols = st.columns([1, 4, 1])
    with cols[1]:
        if row['image_url']:
            img = get_image(row['image_url'], row['watch'] == 1)
            st.image(img, caption=row['name'], width=150)
    with cols[2]:
        if st.button(f"Watched: {bool(row['watch'])}", key=row['name']):
            new_status = 0 if row['watch'] == 1 else 1
            update_watch_status(row['name'], new_status, csv_file)
            st.experimental_rerun()
