"""
Database module for Cine2NerdleSolver.

Provides the Database class which manages movie data, including fetching movies from TMDB API,
storing movie details, and maintaining mappings between movies and persons.
"""

import requests
import joblib
from Cine2NerdleSolver.models import Movie, Person
from Cine2NerdleSolver.config import API_KEY
from typing import Dict, Set, Tuple, List, Callable


class Database:
    def __init__(self, dbFileName: str):
        """
        Initialize a new Database instance.

        Args:
            dbFileName (str): The filename used to store the database.
        """
        # Mapping of movieID -> Movie
        self.movies: Dict[int, Movie] = {}
        # Mapping of personID -> set of movieIDs the person is in
        self.personMovies: Dict[int, Set[int]] = {}
        # Mapping of (personID, genre) -> set of movieIDs
        self.personGenreMovies: Dict[Tuple[int, str], Set[int]] = {}
        self.dbFileName = dbFileName

    def rebuild(self, count: int) -> None:
        """
        Rebuild the database by fetching a specified number of movies and saving to file.

        Args:
            count (int): The number of movies to fetch from the API.
        """
        self.fetchMovies(count)
        self.saveToFile()

    def addMovie(self, movie: Movie) -> None:
        """
        Add a movie to the database if it is not already present.
        Also updates the mappings for persons and their associated genres.

        Args:
            movie (Movie): The Movie object to add.
        """
        if movie.id in self.movies:
            return
        self.movies[movie.id] = movie
        for person in movie.people:
            self.personMovies.setdefault(person.id, set()).add(movie.id)
            for genre in movie.genres:
                key = (person.id, genre)
                self.personGenreMovies.setdefault(key, set()).add(movie.id)

    def fetchMovies(self, count: int) -> None:
        """
        Fetch movies from TMDB API until the specified count is reached.

        Args:
            count (int): The number of movies to fetch.
        """
        movieCount = 0
        page = 1
        while movieCount < count:
            topRatedUrl = (
                f"https://api.themoviedb.org/3/movie/top_rated?"
                f"api_key={API_KEY}&language=en-US&page={page}"
            )
            response = requests.get(topRatedUrl)
            if response.status_code != 200:
                print(f"Request failed on page {page} with status code {response.status_code}")
                break
            data = response.json()
            results = data.get("results", [])
            if not results:
                break
            for result in results:
                if movieCount >= count:
                    break
                movieID = result.get("id")
                movie = self.fetchMovie(movieID)
                if movie is None:
                    continue
                self.addMovie(movie)
                movieCount += 1
            print(f"processed page {page} . Total movies so far: {len(self.movies)} ")
            page += 1

    def saveToFile(self) -> None:
        """
        Save the current database state to a file using joblib.
        """
        db = {
            "movies": self.movies,
            "personMovies": self.personMovies,
            "personGenreMovies": self.personGenreMovies
        }
        joblib.dump(db, self.dbFileName)

    def loadFromFile(self) -> None:
        """
        Load the database state from a file using joblib.
        """
        db = joblib.load(self.dbFileName)
        self.movies = db["movies"]
        self.personMovies = db["personMovies"]
        self.personGenreMovies = db["personGenreMovies"]

    def addMoviesByTitle(self, movieTitle: str) -> None:
        """
        Search for movies by title using the TMDB API and add them to the database if not already present.

        Args:
            movieTitle (str): The title of the movie to search for.
        """
        movieURL = (
            f"https://api.themoviedb.org/3/search/movie?query={movieTitle}&api_key={API_KEY}"
        )

        response = requests.get(movieURL)
        if response.status_code != 200:
            print(f"Request failed with status code {response.status_code}")
            return
        data = response.json()
        results = data.get("results", [])
        if not results:
            print("No results found")
            return

        for result in results:
            movieID = result.get("id")
            movie = self.fetchMovie(movieID)
            if movie is None:
                continue
            if movie.id in self.movies:
                print(f"Movie '{movie.name}' ({movie.releaseDate}) already exists in the database. Skipping.")
                continue

            self.addMovie(movie)
            print(f"Movie '{movie.name}' ({movie.releaseDate}) added to the database.")

    def fetchMovie(self, movie_id: int) -> Movie:
        """
        Fetch detailed information for a movie from TMDB API, including genres and credits.

        Args:
            movie_id (int): The ID of the movie to fetch.

        Returns:
            Movie: A Movie object with detailed information, or None if the request fails.
        """
        details_url = (
            f"https://api.themoviedb.org/3/movie/{movie_id}?"
            f"api_key={API_KEY}&language=en-US"
        )
        detailsResponse = requests.get(details_url)
        if detailsResponse.status_code != 200:
            print(f"Request failed with status code {detailsResponse.status_code}")
            return None
        details = detailsResponse.json()
        title = details.get("title")
        release_date = details.get("release_date")
        genres = [genre.get("name") for genre in details.get("genres")]
        creditsURL = (
            f"https://api.themoviedb.org/3/movie/{movie_id}/credits?"
            f"api_key={API_KEY}"
        )
        creditsResponse = requests.get(creditsURL)
        if creditsResponse.status_code != 200:
            print(f"Request failed with status code {creditsResponse.status_code}")
            return None
        credits = creditsResponse.json()
        people = set()
        cast = credits.get("cast", [])
        crew = credits.get("crew", [])
        people.update([Person(name=m.get("name"), id=m.get("id"))
                       for m in cast[:10] if m.get("id") is not None])
        people.update([Person(name=m.get("name"), id=m.get("id"))
                       for m in crew[:5] if m.get("id") is not None])

        movie = Movie(
            id=movie_id,
            name=title,
            releaseDate=release_date,
            genres=genres,
            people=people,
        )
        return movie

    def findMoviesByName(self, movie_name: str) -> List[Movie]:
        """
        Find movies in the database that match the given name (case-insensitive).

        Args:
            movie_name (str): The name of the movie to search for.

        Returns:
            List[Movie]: A list of Movie objects whose names match the search term.
        """
        return [movie for movie in self.movies.values() if movie.name.lower() == movie_name.lower()]

    def findConnectedMoviesByGenre(self, movie: Movie, genre: str, isValid: Callable[[int, int], bool],
                                   maxMovieSuggestions: int) -> set:
        """
        Find movies connected to the given movie that share at least one person and belong to a specified genre.

        Args:
            movie (Movie): The current movie.
            genre (str): The genre to filter connected movies.
            isValid (Callable[[int, int], bool]): A function to validate if a connection between two movies is allowed.
            maxMovieSuggestions (int): The maximum number of movie suggestions.

        Returns:
            set: A set of movie IDs that are connected to the given movie based on the specified criteria.
        """
        candidateIDs = set()
        for person in movie.people:
            key = (person.id, genre)
            movieIDs = self.personGenreMovies.get(key, set())
            for ID in movieIDs:
                if ID != movie.id and isValid(movie.id, ID):
                    candidateIDs.add(ID)
        return candidateIDs
