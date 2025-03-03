from Cine2NerdleSolver.database import Database
from Cine2NerdleSolver.models import Movie
from Cine2NerdleSolver.solver import Solver

## add types if missing. add docstring

def displayMainMenu():
    print("Welcome to Cine2NerdleSolver")
    print("1) Solve")
    print("2) Rebuild DB")
    print("3) Modify DB")
    print("4) Options")
    print("5) Help")
    print("6) Exit")
    inputStr = input("Enter your choice (1..6): ")
    if inputStr.lower() == "help":
        inputStr = "5"
    try:
        return int(inputStr)
    except ValueError:
        print("Invalid input. Please enter a number.")
        return None


def displayGenreSelectionMenu(genres):
    for index, genre in enumerate(genres, start=1):
        print(f"{index}) {genre}")
    try:
        winIndex = int(input("Winning Genre: "))
        loseIndex = int(input("Losing Genre: "))
        winCondition = genres[winIndex - 1]
        loseCondition = genres[loseIndex - 1]
        return winCondition, loseCondition
    except (ValueError, IndexError):
        print("Invalid genre selection.")
        return None, None


def displayMaxLinks():
    maxLinksInput = input("Max links (1, 2, 3, 4, 5 or infinity): ").strip().lower()
    if maxLinksInput == "infinity":
        return float("inf")
    try:
        return int(maxLinksInput)
    except ValueError:
        print("Invalid input for max links. Defaulting to 3.")
        return 3


def selectMovieFromList(moviesWithSelectedName):
    if not moviesWithSelectedName:
        return None
    elif len(moviesWithSelectedName) == 1:
        return moviesWithSelectedName[0]
    else:
        print("Multiple movies found with selected name. Please select the intended one:")
        for index, movie in enumerate(moviesWithSelectedName, start=1):
            print(f"{index}) {movie.name} ({movie.releaseDate})")
        while True:
            try:
                choice = int(input("Enter your choice number (0 to exit): "))
                if 1 <= choice <= len(moviesWithSelectedName):
                    return moviesWithSelectedName[choice - 1]
                elif choice == 0:
                    return None
                else:
                    print("Choice out of range. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")


def printCandidateMovies(candidates):
    print("Candidate movies:")
    for index, candidate in enumerate(candidates, start=1):
        genresStr = ", ".join(candidate.genres)
        print(f"{index}) {candidate.name} ({candidate.releaseDate}) - Connection genres: {genresStr}")


def askUserToPickStartingMovie(db: Database) -> Movie:
    movieName = input("Starting movie: ").strip()
    possibleMovies = db.findMoviesByName(movieName)
    if not possibleMovies:
        print("No movie was found. Try adding it.")
        selectedMovie = None
    # Select the starting movie.
    elif len(possibleMovies) == 1:
        selectedMovie = possibleMovies[0]
        print(f"Movie '{selectedMovie.name}' found with release date {selectedMovie.releaseDate}.")
    else:
        selectedMovie = selectMovieFromList(possibleMovies)
        if selectedMovie:
            print(f"Movie '{selectedMovie.name}' selected with release date {selectedMovie.releaseDate}.")
    return selectedMovie


def runGame(db, genres, solverStrategy, maxMovieSuggestions):
    winCondition, loseCondition = displayGenreSelectionMenu(genres)
    if not winCondition or not loseCondition:
        return

    maxLinks = displayMaxLinks()
    solver = Solver(db, winCondition, loseCondition, solverStrategy, maxMovieSuggestions, maxLinks)

    selectedMovie = askUserToPickStartingMovie(db)
    if not selectedMovie:
        print("Exiting the Game")
        return

    solver.useMovie(None, selectedMovie)
    currentMovie = selectedMovie
    turn = 0

    while True:
        currentPlayer = "Player 1" if turn % 2 == 0 else "Player 2"
        print(f"\n{currentPlayer}'s turn.")
        print(f"Current movie: {currentMovie.name} ({currentMovie.releaseDate})")

        # Get candidate movie IDs and convert them to movie objects
        candidateIDs = solver.findNextMovies(currentMovie)
        if not candidateIDs:
            print("No candidate movies found. Ending game.")
            break

        candidateMovies = sorted([db.movies[cid] for cid in candidateIDs], key=lambda m: m.name)
        printCandidateMovies(candidateMovies)

        choiceInput = input("Enter candidate number or type movie name (or 'skip' to skip, 'escape' for special move): ").strip()
        selectedCandidate = None
        if choiceInput.isdigit():
            choiceNum = int(choiceInput)
            if 1 <= choiceNum <= len(candidateMovies):
                selectedCandidate = candidateMovies[choiceNum - 1]
            else:
                print("Invalid candidate number. Ending game.")
                break
        elif choiceInput.lower() == "skip":
            solver.flipWinLoseGenres()
            turn += 1
            continue
        elif choiceInput.lower() == "escape":
            print("Escape functionality not implemented yet.")
            # Placeholder for escape logic.
            continue
        else:
            # Search by movie name using the user's input.
            matches = db.findMoviesByName(choiceInput)
            if not matches:
                print("No movies found, you need to skip or use escape. We skipped for you.")
                solver.flipWinLoseGenres()
                turn += 1
                continue
            selectedCandidate = selectMovieFromList(matches)
            if not selectedCandidate:
                print("No valid movie selected, skipping turn.")
                solver.flipWinLoseGenres()
                turn += 1
                continue

        updateFrequency = turn >= 4
        solver.useMovie(currentMovie, selectedCandidate, update_frequency=updateFrequency)
        currentMovie = selectedCandidate
        solver.flipWinLoseGenres()
        turn += 1


def runRebuildDB(dbInstance, defaultCount):
    countInput = input("Number of movies to fetch from TMDB (leave blank for default): ").strip()
    movieCount = int(countInput) if countInput else defaultCount
    print("Rebuilding database...")
    dbInstance.rebuild(movieCount)


def runModifyDB(db):
    movieQuery = input("Movie to add (leave blank to exit): ").strip()
    while movieQuery:
        db.addMoviesByTitle(movieQuery)
        movieQuery = input("Movie to add (leave blank to exit): ").strip()


def runOptions():
    print("Placeholder, for now the only strategy is greedy.")


def runHelp():
    print("NA")


def main():
    solverStrategy = "GREEDY"
    maxMovieSuggestions = 3
    defaultCount = 10000
    genres = [
        "Action", "Adventure", "Animation", "Comedy", "Crime",
        "Documentary", "Drama", "Family", "Fantasy", "History",
        "Horror", "Music", "Mystery", "Romance", "Science Fiction",
        "Thriller", "TV Movie", "War", "Western"
    ]

    db = Database("database.joblib")
    try:
        db.loadFromFile()
    except Exception as e:
        print("Could not load from file, rebuilding...")
        db.rebuild(defaultCount)

    while True:
        choice = displayMainMenu()
        if choice is None:
            continue

        if choice == 1:
            runGame(db, genres, solverStrategy, maxMovieSuggestions)
        elif choice == 2:
            runRebuildDB(db, defaultCount)
        elif choice == 3:
            runModifyDB(db)
        elif choice == 4:
            runOptions()
        elif choice == 5:
            runHelp()
        elif choice == 6:
            print("Exiting")
            break
        else:
            print("Invalid option, please try again.")


if __name__ == '__main__':
    main()
