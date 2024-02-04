import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import os

# Function to fetch TV show image URL (using OMDB API)
def fetch_tv_show_image_url(tv_show_title, api_key):
    url = f"http://www.omdbapi.com/?t={tv_show_title}&type=series&apikey={api_key}"
    try:
        response = requests.get(url)
        data = response.json()

        if 'Poster' in data and data['Poster'] != 'N/A':
            return data['Poster']
    except Exception as e:
        st.error(f"An error occurred while fetching image URL for '{tv_show_title}': {e}")
    return None

# Function to add TV show to the database
def add_tv_show_to_csv(tv_show_name, watch_status, image_url, csv_file):
    df = pd.read_csv(csv_file)
    new_row = pd.DataFrame([[tv_show_name, watch_status, image_url]], columns=['name', 'watch', 'image_url'])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(csv_file, index=False)

# Function to update watch status
def update_watch_status(tv_show_name, new_watch_status, csv_file):
    df = pd.read_csv(csv_file)
    df.loc[df['name'] == tv_show_name, 'watch'] = new_watch_status
    df.to_csv(csv_file, index=False)

# Function to get image in greyscale if watched
def get_image(image_url, is_watched):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    return img.convert('L') if is_watched else img

# Check for CSV file and create if not exists
csv_file = 'tv_shows.csv'
if not os.path.exists(csv_file):
    df = pd.DataFrame(columns=['name', 'watch', 'image_url'])
    df.to_csv(csv_file, index=False)
else:
    df = pd.read_csv(csv_file)

# Streamlit layout
st.title("TV Show Display")

# Load your OMDB API key
# api_key = st.secrets["omdb_api_key"]
api_key='f500e5a8'
# User input to add TV shows
with st.form("tv_show_form"):
    new_tv_show_name = st.text_input("TV Show Name")
    new_watch_status = st.selectbox("Watch Status", options=[0, 1])
    submitted = st.form_submit_button("Add TV Show")
    if submitted and new_tv_show_name:
        df = pd.read_csv(csv_file)
        if new_tv_show_name not in df['name'].values:
            image_url = fetch_tv_show_image_url(new_tv_show_name, api_key)
            if image_url:
                add_tv_show_to_csv(new_tv_show_name, new_watch_status, image_url, csv_file)
                st.success(f"Added '{new_tv_show_name}' to the database!")
            else:
                st.error("Failed to fetch image URL for the TV show.")
        else:
            st.error("TV Show already in the database.")

# Display TV show images and buttons for updating watch status
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
