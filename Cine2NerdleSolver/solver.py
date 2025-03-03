# solver.py
from Cine2NerdleSolver.database import Database
from Cine2NerdleSolver.models import Movie


# Todo: Directly modify movie instances for efficiency
# Todo: Make Used_movies store IDs instead of movie objects

class Solver:
    def __init__(self, database: Database, winCondition: str, loseCondition: str,
                 strategy: str, maxMovieSuggestions: int, maxLinks: int):
        self.database = database
        self.winGenre: str = winCondition
        self.loseGenre: str = loseCondition
        self.usedMovieIDs : set[int] = set()
        self.personFrequency = {}
        self.strategy: str= strategy
        self.maxMovieSuggestions:int = maxMovieSuggestions
        self.maxLinks:int = maxLinks

    def findNextMovies(self, currentMovie: Movie):
        # Greedy strategy: Pick whatever / rush win condition
        if self.strategy is None or self.strategy == "GREEDY":
            return self.findNextMovieGreedy(currentMovie)

        raise Exception(f"Strategy {self.strategy} is not defined")

    def findNextMovieGreedy(self, currentMovie: Movie) -> set[int]:
        # 1) Check winning genre first.
        winners = self.database.findConnectedMoviesByGenre(currentMovie, self.winGenre, self.isValid, self.maxMovieSuggestions)
        others : set[int] = set()
        # Consider other genres (excluding winning and opponent)
        for genre in currentMovie.genres:
            if genre in (self.winGenre, self.loseGenre):
                continue
            if len(others) >= self.maxMovieSuggestions:
                break
            candidates = self.database.findConnectedMoviesByGenre(currentMovie, genre, self.isValid, self.maxMovieSuggestions)
            others.update(candidates)

        # Use opponent genre if needed:
        if len(others) < self.maxMovieSuggestions:
            others.update(self.database.findConnectedMoviesByGenre(currentMovie,
                                                                   self.loseGenre, self.isValid, self.maxMovieSuggestions - len(others)))
            winners.update(others)
        return winners


    def isValid(self, currentMovieID: int, nextMovieID: int) -> bool:
        if nextMovieID in self.usedMovieIDs:
            return False
        currentMovie = self.database.movies[currentMovieID]
        nextMovie = self.database.movies[nextMovieID]
        # Return true if any available connection
        for person in currentMovie.people.intersection(nextMovie.people):
            if self.personFrequency.get(person, 0) < self.maxLinks:
                return True
        return False




    def useMovie(self, currentMovie: Movie, nextMovie: Movie, update_frequency=True):
        # Mark nextMovie as used.
        self.usedMovieIDs.add(nextMovie.id)
        if not currentMovie:
            return
        # Update frequency only if allowed.
        if update_frequency:
            for person in currentMovie.people.intersection(nextMovie.people):
                self.personFrequency[person] = self.personFrequency.get(person, 0) + 1

    def flipWinLoseGenres(self):
        tmp = self.winGenre
        self.winGenre = self.loseGenre
        self.loseGenre = tmp
