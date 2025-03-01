# solver.py
from Cine2NerdleSolver.models import Movie


# Todo: Directly modify movie instances for efficiency
# Todo: Make Used_movies store IDs instead of movie objects

class Cine2NerdleSolver:
    def __init__(self, database, winning_genre, opponent_genre, strategy, candidateSize, maxLinks):
        self.database = database
        self.winning_genre = winning_genre
        self.opponent_genre = opponent_genre
        self.used_movies = set()
        self.person_frequency = {}
        self.strategy = strategy
        self.candidateSize = candidateSize
        self.maxLinks = maxLinks

    def findNextMovies(self, currentMovie: Movie):
        # print("Available connection genres for current movie:", list(currentMovie.movies.keys()))

        # Greedy sol: Pick whatever / rush win condition
        if self.strategy is None or self.strategy == "GREEDY":
            # 1) Check winning genre first.
            winners = self.findMovies(self.winning_genre, currentMovie)

            # 2) Look at all other genres.
            others = []
            for genre in currentMovie.movies:
                if genre == self.winning_genre or genre == self.opponent_genre:
                   continue
                others.append(self.findMovies(genre, currentMovie))
            # 3) Check losing genre if and only if no other options
            if len(others) < self.candidateSize:
                others.append(self.findMovies(self.opponent_genre, currentMovie))
            winners.append(others)

            return winners




    def isValid(self, A: Movie, B: Movie):
        # Check if B is used
        if B.name + "|" + B.release_date in self.used_movies:
            return False
        # Return true if any available connection:
        for personA in A.people:
            for personB in B.people:
                if personA.name == personB.name and personA.id == personB.id and self.person_frequency.get(personA, 0) < self.maxLinks:
                    return True
        # None found
        return False

    def findMovies(self, genre: str, currentMovie: Movie):
        candidates = []
        if currentMovie.movies.get(genre) is None:
            return candidates
        count = 0
        for i in currentMovie.movies.get(genre):
            if count == self.candidateSize: break
            candidate = self.database.movies[i]
            if self.isValid(currentMovie, candidate):
                candidates.append(candidate)
            count += 1
        return candidates


    def add(self, A: Movie, B: Movie, update_frequency=True):
        # Mark Movie B as used.
        self.used_movies.add(B.name + "|" + B.release_date)
        # Update frequency only if allowed.
        if update_frequency:
            for person in A.people.intersection(B.people):
                self.person_frequency[person] = self.person_frequency.get(person, 0) + 1

    def flipGenre(self):
        tmp = self.winning_genre
        self.winning_genre = self.opponent_genre
        self.opponent_genre = tmp
