import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import os

# Function to fetch movie image URL (using OMDB API as an example)
def fetch_movie_image_url(movie_title, api_key):
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={api_key}"
    try:
        response = requests.get(url)
        data = response.json()

        if 'Poster' in data and data['Poster'] != 'N/A':
            return data['Poster']
    except Exception as e:
        st.error(f"An error occurred while fetching image URL for '{movie_title}': {e}")
    return None

# Function to add movie to the database
def add_movie_to_csv(movie_name, watch_status, image_url, csv_file):
    df = pd.read_csv(csv_file)
    new_row = pd.DataFrame([[movie_name, watch_status, image_url]], columns=['name', 'watch', 'image_url'])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(csv_file, index=False)

# Function to update watch status
def update_watch_status(movie_name, new_watch_status, csv_file):
    df = pd.read_csv(csv_file)
    df.loc[df['name'] == movie_name, 'watch'] = new_watch_status
    df.to_csv(csv_file, index=False)

# Function to get image in greyscale if watched
def get_image(image_url, is_watched):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    return img.convert('L') if is_watched else img

# Check for CSV file and create if not exists
csv_file = 'movies.csv'
if not os.path.exists(csv_file):
    df = pd.DataFrame(columns=['name', 'watch', 'image_url'])
    df.to_csv(csv_file, index=False)
else:
    df = pd.read_csv(csv_file)

# Streamlit layout
st.title("Movie Display")

# Load your OMDB API key
try:
    api_key = st.secrets["omdb_api_key"]
    st.write("API Key found")
except:
    api_key='f500e5a8'
# User input to add movies
with st.form("movie_form"):
    new_movie_name = st.text_input("Movie Name")
    new_watch_status = st.selectbox("Watch Status", options=[0, 1])
    submitted = st.form_submit_button("Add Movie")
    if submitted and new_movie_name:
        df = pd.read_csv(csv_file)
        if new_movie_name not in df['name'].values:
            image_url = fetch_movie_image_url(new_movie_name, api_key)
            if image_url:
                add_movie_to_csv(new_movie_name, new_watch_status, image_url, csv_file)
                st.success(f"Added '{new_movie_name}' to the database!")
            else:
                st.error("Failed to fetch image URL for the movie.")
        else:
            st.error("Movie already in the database.")

# Display movie images and buttons for updating watch status
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
