# database.py
import requests
import joblib
from Cine2NerdleSolver.models import Movie, Person
from Cine2NerdleSolver.config import API_KEY
from typing import Dict, Set, Tuple, List
from typing import Callable


class Database:
    def __init__(self, dbFileName: str):
        # Mapping of movieID -> Movie
        self.movies: Dict[int, Movie] = {}
        # Mapping of personID -> set of movieIDs the person is in
        self.personMovies: Dict[int, Set[int]] = {}
        # Mapping of (personID, genre) -> set of movieIDs
        self.personGenreMovies: Dict[Tuple[int, str], Set[int]] = {}
        self.dbFileName = dbFileName

    def rebuild(self, count: int):
        self.fetchMovies(count)
        self.saveToFile()

    def addMovie(self, movie: Movie):
        if movie.id in self.movies:
            return
        self.movies[movie.id] = movie
        # Update person -> movies mapping and person+genre mapping
        for person in movie.people:
            self.personMovies.setdefault(person.id, set()).add(movie.id)
            for genre in movie.genres:
                key = (person.id, genre)
                self.personGenreMovies.setdefault(key, set()).add(movie.id)

    def fetchMovies(self, count: int):
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
                break  # no more movies(which shouldn't happen since we never look past the first 5000)
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

    def saveToFile(self):
        db = {"movies": self.movies, "personMovies": self.personMovies, "personGenreMovies": self.personGenreMovies}
        joblib.dump(db, self.dbFileName)


    def loadFromFile(self):
        db = joblib.load(self.dbFileName)
        self.movies = db["movies"]
        self.personMovies = db["personMovies"]
        self.personGenreMovies = db["personGenreMovies"]


    def addMoviesByTitle(self, movieTitle: str):
        # Manually add whatever buildDB missed out on
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

    def fetchMovie(self, movie_id: int):
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
        # Extract Genres
        genres = [genre.get("name") for genre in details.get("genres")]
        # Extract actors:
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
        # Take up to 10 cast members that have a valid id
        people.update([Person(name=m.get("name"), id=m.get("id"))
                       for m in cast[:10] if m.get("id") is not None])
        # Take up to 5 crew members that have a valid id
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
        """Return a list of movies whose names match."""
        return [movie for movie in self.movies.values() if movie.name.lower() == movie_name.lower()]

    def findConnectedMoviesByGenre(self, movie: Movie, genre: str, isValid: Callable[[int, int], bool], maxMovieSuggestions: int) -> set[int]:
        """
        Returns Movies that share at least one person with the given movie
        and include the specified genre.
        """
        candidateIDs = set()
        for person in movie.people:
            key = (person.id, genre)
            movieIDs = self.personGenreMovies.get(key, set())
            for ID in movieIDs:
                if ID != movie.id and isValid(movie.id, ID):
                    candidateIDs.add(ID)
        # candidates = [self.movies[m_id] for m_id in candidateIDs if m_id in self.movies]
        return candidateIDs
