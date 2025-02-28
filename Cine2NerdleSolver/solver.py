# solver.py
from Cine2NerdleSolver.models import Movie


# Todo: Directly modify movie instances for efficiency
# Todo: Make Used_movies store IDs instead of movie objects

class Cine2NerdleSolver:
    def __init__(self, database, winning_genre, opponent_genre):
        self.database = database
        self.winning_genre = winning_genre
        self.opponent_genre = opponent_genre
        self.used_movies = set()
        self.person_frequency = {}

    def findNextMovie(self, currentMovie: Movie):
        print("Available connection genres for current movie:", list(currentMovie.movies.keys()))

        # Greedy sol: Pick whatever / rush win condition

        # 1) Check winning genre first.
        winning_index = self.findMovie(self.winning_genre, currentMovie)

        if winning_index is not None:
            print("Found candidate in winning genre:", self.database.movies[winning_index].name)
            return self.database.movies[winning_index]

        # 2) Look at all other genres.
        for genre in currentMovie.movies:
            if genre == self.winning_genre or genre == self.opponent_genre:
                continue
            candidate_index = self.findMovie(genre, currentMovie)
            if candidate_index is not None:
                print("Found candidate in genre", genre, ":", self.database.movies[candidate_index].name)
                return self.database.movies[candidate_index]

        # 3) Look at opponent genre last.
        opponent_index = self.findMovie(self.opponent_genre, currentMovie)
        if opponent_index is not None:
            print("Found candidate in opponent genre:", self.database.movies[opponent_index].name)
            return self.database.movies[opponent_index]

        print("No valid candidate found.")
        return None

    def isValid(self, A: Movie, B: Movie):
        # Check if B is used
        if B.name + "|" + B.release_date in self.used_movies:
            return False
        # Return true if any available connection:
        for personA in A.people:
            for personB in B.people:
                if personA.name == personB.name and personA.id == personB.id and self.person_frequency.get(personA, 0) < 3:
                    return True
        # None found
        return False

    def findMovie(self, genre: str, currentMovie: Movie):
        if currentMovie.movies.get(genre) is None:
            return None
        for i in currentMovie.movies.get(genre):
            movie = self.database.movies[i]
            if self.isValid(currentMovie, movie):
                return i
        return None

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
