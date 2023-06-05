import streamlit as st
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import plotly.express as px
import uuid
import streamlit.components.v1 as components
st.set_page_config(page_title="Music Recommendation", layout="wide")

@st.cache_data()
def load_data():
    df = pd.read_csv("data/processed_track_df.csv")
    df['genres'] = df.genres.apply(lambda x: [i[1:-1] for i in str(x)[1:-1].split(", ")])
    exploded_track_df = df.explode("genres")
    return exploded_track_df
    
genre_names = ['Dance Pop', 'Electronic', 'Electropop', 'Hip Hop', 'Jazz', 'K-pop', 'Latin', 'Pop', 'Pop Rap', 'R&B', 'Rock']
audio_feats = ["acousticness", "danceability", "energy", "instrumentalness", "valence", "tempo"]
exploded_track_df = load_data()
def n_neighbors_uri_audio(genre, start_year, end_year, test_feat):
    genre = genre.lower()
    genre_data = exploded_track_df[(exploded_track_df["genres"]==genre) & (exploded_track_df["release_year"]>=start_year) & (exploded_track_df["release_year"]<=end_year)]
    genre_data = genre_data.sort_values(by='popularity', ascending=False)[:500]
    neigh = NearestNeighbors()
    neigh.fit(genre_data[audio_feats].to_numpy())
    n_neighbors = neigh.kneighbors([test_feat], n_neighbors=len(genre_data), return_distance=False)[0]
        
    uris = genre_data.iloc[n_neighbors]["uri"].tolist()
    audios = genre_data.iloc[n_neighbors][audio_feats].to_numpy()
    return uris, audios

    
# Create a login form
def login_page():
    st.title("User Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

# If the user enters a valid username and password, log them in
    if st.button("Login"):
      user_data = pd.read_csv("user_data.csv")
      if username in user_data["Username"].values and password in user_data["Password"].values:
          st.success("Login successful!")
          st.session_state["is_logged_in"] = True
          recommendation_page()
      else:
          st.warning("Invalid username or password.")
            
    st.markdown("Don't have an account? [Create one](?register=true)")

# Create a registration form
def register_page():
    st.write("Enter your details below to create a new account.")
    first_name = st.text_input("First name", key="register_first_name")
    last_name = st.text_input("Last name", key="register_last_name")
    email = st.text_input("Email", key="register_email")
    password = st.text_input("Password", type="password", key="register_password")

# If the user enters all of the required details, create the account
    if st.button("Create Account", key="register_button"):
        if first_name and last_name and email and password:
            user_data = {
                "Username": [first_name],
                "Password": [password]
            }
            df = pd.DataFrame(user_data)
            df.to_csv("user_data.csv", index=False)
            st.success("Account created successfully! Please log in.")
            st.experimental_rerun()
        else:
             st.warning("Please enter all of the required details.")

def recommendation_page():
    title = "Music Recommendation System"
    st.title(title)
        
    st.write("Welcome! Here you can customize what you want to listen to based on genres. And listen to the songs recommended by our system!")
    st.markdown("##")
        
 
    with st.sidebar:
         st.header("***Select genre:***")
         genre = st.radio(
             "",
             genre_names, index=genre_names.index("K-pop"), 
             key=str(uuid.uuid4()))
         with st.container():
             col1, col2, col3 = st.columns([2, 0.5, 2])
             with col1:
                st.markdown("***Customize Features :***")
                start_year, end_year = st.slider(
                    'Select the year range',
                    1990, 2019, (2010, 2019),
                    key=str(uuid.uuid4())
                )
                acousticness = st.slider(
                    'Acousticness',
                    0.0, 1.0, 0.5,
                    key=str(uuid.uuid4())
                )
                danceability = st.slider(
                    'Danceability',
                    0.0, 1.0, 0.5,
                    key=str(uuid.uuid4())
                )
                energy = st.slider(
                    'Energy',
                    0.0, 1.0, 0.5,
                    key=str(uuid.uuid4())
                )
                instrumentalness = st.slider(
                    'Instrumentalness',
                    0.0, 1.0, 0.0,
                    key=str(uuid.uuid4())
                )
                valence = st.slider(
                    'Valence',
                    0.0, 1.0, 0.45,
                    key=str(uuid.uuid4())
                )
                tempo = st.slider(
                    'Tempo',
                    0.0, 244.0, 118.0,
                    key=str(uuid.uuid4())
                )
             with col3:
                st.markdown("***Recommended Songs :***")
                
                tracks_per_page = 5
                
                if "tracks" not in st.session_state:
                    st.session_state["tracks"] = []
                    st.session_state["audios"] = []
                    
                tracks = st.session_state["tracks"]
                audios = st.session_state["audios"]
                
                if len(tracks) == 0:
                # Simulating initial recommendation
                    for i in range(15):
                        tracks.append(f"Song {i+1}")
                        audios.append(np.random.rand(10).tolist())
                        
                if "start_track_i" not in st.session_state:
                    st.session_state["start_track_i"] = 0
                    
                if st.button("Next"):
                    if st.session_state["start_track_i"] + tracks_per_page < len(tracks):
                        st.session_state["start_track_i"] += tracks_per_page
                        
                current_tracks = tracks[st.session_state["start_track_i"]: st.session_state["start_track_i"] + tracks_per_page]
                current_audios = audios[st.session_state["start_track_i"]: st.session_state["start_track_i"] + tracks_per_page]
                
                if st.session_state["start_track_i"] < len(tracks):
                    for i, (track, audio) in enumerate(zip(current_tracks, current_audios)):
                        if i % 2 == 0:
                            with col1:
                                components.html(
                                    track,
                                    height=400,
                                )
                                with st.expander("See more details"):
                                    df = pd.DataFrame(dict(
                                        r=audio[:5],
                                        theta=["feat1", "feat2", "feat3", "feat4", "feat5"]
                                    ))
                                    fig = px.line_polar(df, r='r', theta='theta', line_close=True)
                                    fig.update_layout(height=400, width=340)
                                    st.plotly_chart(fig)
                        else:
                            with col3:
                                components.html(
                                    track,
                                    height=400,
                                )
                                with st.expander("See more details"):
                                    df = pd.DataFrame(dict(
                                        r=audio[:5],
                                        theta=["feat1", "feat2", "feat3", "feat4", "feat5"]
                                    ))
                                    fig = px.line_polar(df, r='r', theta='theta', line_close=True)
                                    fig.update_layout(height=400, width=340)
                                    st.plotly_chart(fig)
                else:
                    st.write("No songs left to recommend")

def main():
    st.session_state.setdefault("is_logged_in", False)

    if not st.session_state["is_logged_in"]:
        if "register" in st.experimental_get_query_params():
            st.session_state["register"] = True
            register_page()
            st.stop()  # Stop the script execution to prevent duplicate widgets error
        else:
            if not st.session_state.get("is_csv_created", False):
                df = pd.DataFrame(columns=["Username", "Password"])
                df.to_csv("user_data.csv", index=False)
                st.session_state["is_csv_created"] = True

            login_page()
            if "register" in st.session_state and st.session_state["register"]:
                register_page()
                st.stop()  # Stop the script execution to prevent duplicate widgets error

        if st.session_state["is_logged_in"]:
            recommendation_page()

    else:
        recommendation_page()

if __name__ == "__main__":
    main()
