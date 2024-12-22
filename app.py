import requests
import random
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash

# Load environment variables
load_dotenv()

# Jikan API Base URL
JIKAN_URL = os.getenv("JIKAN_URL")

# Average anime episode duration (in minutes)
AVERAGE_EPISODE_DURATION = 24

# Available genres for selection
GENRES = [
    'Action', 'Adventure', 'Cars', 'Comedy', 'Dementia',
    'Demons', 'Mystery', 'Drama', 'Ecchi', 'Fantasy',
    'Game', 'Hentai', 'Historical', 'Horror', 'Kids',
    'Magic', 'Martial Arts', 'Mecha', 'Music', 'Parody',
    'Samurai', 'Romance', 'School', 'Sci-Fi', 'Shoujo',
    'Shoujo Ai', 'Shounen', 'Shounen Ai', 'Space', 'Sports',
    'Super Power', 'Vampire', 'Yaoi', 'Yuri', 'Harem',
    'Slice of Life', 'Supernatural', 'Military', 'Police',
    'Psychological', 'Thriller', 'Seinen', 'Josei'
]

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

@app.route('/')
def index():
    """Render the main page with genre options."""
    return render_template('index.html', genres=GENRES)

@app.route('/suggest', methods=['POST'])
def suggest_anime():
    """Suggest anime based on user input."""
    genre_name = request.form['genre']
    try:
        min_time = float(request.form['min_time'])
        max_time = float(request.form['max_time'])

        genre_dict = {genre.lower(): i + 1 for i, genre in enumerate(GENRES)}
        genre_id = genre_dict.get(genre_name.lower())
        if not genre_id:
            flash("Invalid genre selected.")
            return redirect(url_for('index'))

        min_time_minutes = min_time * 60
        max_time_minutes = max_time * 60

        # Fetch data from Jikan API
        response = requests.get(f"{JIKAN_URL}/anime?genres={genre_id}")
        anime_list = response.json().get('data', [])

        # Filter results based on the user's time constraints
        filtered_anime = [
            anime for anime in anime_list
            if anime.get('episodes') and min_time_minutes <= anime['episodes'] * AVERAGE_EPISODE_DURATION <= max_time_minutes
        ]

        if not filtered_anime:
            flash(f"No anime found in '{genre_name}' within {min_time}-{max_time} hours.")
            return redirect(url_for('index'))

        # Randomize and select up to 3 recommendations
        random.shuffle(filtered_anime)
        recommendations = []
        for anime in filtered_anime[:3]:
            total_time_minutes = anime['episodes'] * AVERAGE_EPISODE_DURATION
            total_time_hours = total_time_minutes / 60
            recommendations.append({
                'title': anime['title'],
                'episodes': anime['episodes'],
                'total_time': f"{total_time_hours:.2f} hours",
                'url': anime['url']
            })

        return render_template('suggestions.html', recommendations=recommendations)

    except ValueError:
        flash("Please enter valid numbers for time.")
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
