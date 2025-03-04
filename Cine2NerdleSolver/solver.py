"""
Solver module for Cine2NerdleSolver.

Provides the Solver class which implements strategies for selecting the next movie in the game
based on genre connections and person frequency.
"""

from Cine2NerdleSolver.database import Database
from Cine2NerdleSolver.models import Movie


class Solver:
    def __init__(self, database: Database, winCondition: str, loseCondition: str,
                 strategy: str, maxMovieSuggestions: int, maxLinks: int):
        """
        Initialize a Solver instance.

        Args:
            database (Database): The movie database instance.
            winCondition (str): The genre that represents the winning condition.
            loseCondition (str): The genre that represents the losing condition.
            strategy (str): The strategy to use for finding the next movie (e.g., "GREEDY").
            maxMovieSuggestions (int): The maximum number of movie suggestions to consider.
            maxLinks (int): The maximum allowed frequency for connections via a person.
        """
        self.database = database
        self.winGenre: str = winCondition
        self.loseGenre: str = loseCondition
        self.usedMovieIDs: set[int] = set()
        self.personFrequency = {}
        self.strategy: str = strategy
        self.maxMovieSuggestions: int = maxMovieSuggestions
        self.maxLinks: int = maxLinks

    def findNextMovies(self, currentMovie: Movie) -> set:
        """
        Determine the next candidate movies from the current movie based on the selected strategy.

        Args:
            currentMovie (Movie): The current movie in the game.

        Returns:
            set: A set of movie IDs representing candidate movies for the next move.
        """
        if self.strategy is None or self.strategy == "GREEDY":
            return self.findNextMovieGreedy(currentMovie)
        raise Exception(f"Strategy {self.strategy} is not defined")

    def findNextMovieGreedy(self, currentMovie: Movie) -> set:
        """
        Find the next movie candidates using a greedy strategy.

        The method first attempts to find movies connected via the winning genre. It then searches
        through other genres, and if necessary, includes movies connected via the losing genre.

        Args:
            currentMovie (Movie): The current movie in the game.

        Returns:
            set: A set of movie IDs that are valid next moves.
        """
        winners = self.database.findConnectedMoviesByGenre(currentMovie, self.winGenre, self.isValid,
                                                           self.maxMovieSuggestions)
        others: set = set()
        for genre in currentMovie.genres:
            if genre in (self.winGenre, self.loseGenre):
                continue
            if len(others) >= self.maxMovieSuggestions:
                break
            candidates = self.database.findConnectedMoviesByGenre(currentMovie, genre, self.isValid,
                                                                  self.maxMovieSuggestions)
            others.update(candidates)
        if len(others) < self.maxMovieSuggestions:
            others.update(self.database.findConnectedMoviesByGenre(currentMovie,
                                                                   self.loseGenre, self.isValid,
                                                                   self.maxMovieSuggestions - len(others)))
            winners.update(others)
        return winners

    def isValid(self, currentMovieID: int, nextMovieID: int) -> bool:
        """
        Check if transitioning from the current movie to the next movie is valid.

        A valid transition means the next movie has not been used yet and at least one connecting person
        has a frequency count below the maximum allowed links.

        Args:
            currentMovieID (int): The ID of the current movie.
            nextMovieID (int): The ID of the potential next movie.

        Returns:
            bool: True if the transition is valid, False otherwise.
        """
        if nextMovieID in self.usedMovieIDs:
            return False
        currentMovie = self.database.movies[currentMovieID]
        nextMovie = self.database.movies[nextMovieID]
        for person in currentMovie.people.intersection(nextMovie.people):
            if self.personFrequency.get(person, 0) < self.maxLinks:
                return True
        return False

    def useMovie(self, currentMovie: Movie, nextMovie: Movie, update_frequency: bool = True) -> None:
        """
        Mark the next movie as used and update the connection frequency between movies.

        Args:
            currentMovie (Movie): The current movie (can be None when starting the game).
            nextMovie (Movie): The movie chosen as the next move.
            update_frequency (bool): Whether to update the frequency count for shared persons.
        """
        self.usedMovieIDs.add(nextMovie.id)
        if not currentMovie:
            return
        if update_frequency:
            for person in currentMovie.people.intersection(nextMovie.people):
                self.personFrequency[person] = self.personFrequency.get(person, 0) + 1

    def flipWinLoseGenres(self) -> None:
        """
        Swap the winning and losing genres.
        """
        tmp = self.winGenre
        self.winGenre = self.loseGenre
        self.loseGenre = tmp
