import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Function to fetch movies from a given URL
def fetch_movies(url, headers):
    try:
        # Make a GET request to the webpage
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error if the request failed
        # Parse the webpage content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")
        return soup
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None

# Function to extract movie data (names and ratings) from the parsed HTML
def extract_movie_data(soup):
    movie_data = []

    if soup:
        # Find all movie names and ratings
        movie_names = soup.find_all('a', class_='ipc-title-link-wrapper')
        movie_ratings = soup.find_all('span', class_='sc-b189961a-1 kcRAsW')

        # Iterate over movie names and ratings
        for name, rating in zip(movie_names, movie_ratings):
            movie_name = name.text.strip()  # Clean up the movie name text

            # Use regex to find the rating in the text
            rating_match = re.search(r'\d+\.\d+', rating.text)
            if rating_match:
                movie_rating_str = rating_match.group()
                try:
                    # Convert the rating to a float
                    movie_rating = float(movie_rating_str)
                    # Add the movie name and rating to the movie data list
                    movie_data.append((movie_name, movie_rating))
                except ValueError:
                    print(f"Could not convert rating '{movie_rating_str}' for movie '{movie_name}' to a float.")
            else:
                print(f"Could not find a valid rating for movie '{movie_name}'.")

    return movie_data

# Function to save the extracted movie data to a CSV file
def save_to_csv(movies, filename="movies.csv"):
    # Create a DataFrame and save it as a CSV file
    df = pd.DataFrame(movies, columns=["Title", "Rating"])
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

# Function to load movie data from a CSV file
def load_movies(filename="movies.csv"):
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(filename)
        return df
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None

# Function to suggest movies by genre and minimum rating
def suggest_movies_by_genre(df, genre, min_rating=0):
    # Filter the movies based on the genre and minimum rating
    filtered_movies = df[df["Title"].str.contains(genre, case=False, na=False)]
    sorted_movies = filtered_movies[filtered_movies["Rating"] >= min_rating].sort_values(by="Rating", ascending=False)

    # Print the sorted list of movies
    if not sorted_movies.empty:
        print(f"\nMovies found for genre '{genre}' with rating >= {min_rating}:")
        print(sorted_movies.to_string(index=False))
    else:
        print(f"No movies found for the given genre '{genre}' with rating >= {min_rating}.")

# Main program
url = "https://www.imdb.com/chart/moviemeter"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Fetch and extract movies from the URL
soup = fetch_movies(url, headers)
movies = extract_movie_data(soup)

if movies:
    save_to_csv(movies)  # Save the movies to a CSV file
    df_movies = load_movies()  # Load the movies from the CSV file
    if df_movies is not None:
        # Get user input for genre and minimum rating
        genre = input("Enter a genre to get movie suggestions: ").strip()
        try:
            min_rating = float(input("Enter the minimum rating (e.g., 7.5): ").strip())
            suggest_movies_by_genre(df_movies, genre, min_rating)  # Suggest movies based on input
        except ValueError:
            print("Please enter a valid number for the rating.")
else:
    print("No movies were found or an error occurred.")
