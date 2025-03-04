from Cine2NerdleSolver.database import Database
from Cine2NerdleSolver.models import Movie
from Cine2NerdleSolver.solver import Solver
from typing import List, Optional, Tuple


def displayMainMenu() -> Optional[int]:
    """
    Display the main menu and prompt the user to enter a choice.

    Returns:
        Optional[int]: The selected menu option as an integer (1-6), or None if input is invalid.
    """
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


def displayGenreSelectionMenu(genres: List[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Display a list of genres and prompt the user to select a winning and a losing genre.

    Args:
        genres (List[str]): A list of available genre names.

    Returns:
        Tuple[Optional[str], Optional[str]]: The selected winning and losing genres.
                                               Returns (None, None) if the selection is invalid.
    """
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


def displayMaxLinks() -> int:
    """
    Prompt the user to input the maximum number of links allowed.

    Returns:
        int: The maximum links as an integer, or infinity if the user enters "infinity".
             Defaults to 3 if the input is invalid.
    """
    maxLinksInput = input("Max links (1, 2, 3, 4, 5 or infinity): ").strip().lower()
    if maxLinksInput == "infinity":
        return float("inf")
    try:
        return int(maxLinksInput)
    except ValueError:
        print("Invalid input for max links. Defaulting to 3.")
        return 3


def selectMovieFromList(moviesWithSelectedName: List[Movie]) -> Optional[Movie]:
    """
    If multiple movies with the same name exist, prompt the user to select one.

    Args:
        moviesWithSelectedName (List[Movie]): A list of Movie objects with the matching name.

    Returns:
        Optional[Movie]: The selected Movie, or None if no valid selection is made.
    """
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


def printCandidateMovies(candidates: List[Movie]) -> None:
    """
    Print a list of candidate movies along with their details.

    Args:
        candidates (List[Movie]): A list of Movie objects to display.
    """
    print("Candidate movies:")
    for index, candidate in enumerate(candidates, start=1):
        genresStr = ", ".join(candidate.genres)
        print(f"{index}) {candidate.name} ({candidate.releaseDate}) - Connection genres: {genresStr}")


def askUserToPickStartingMovie(db: Database) -> Optional[Movie]:
    """
    Prompt the user to enter a starting movie and select it from the database.

    Args:
        db (Database): The movie database instance.

    Returns:
        Optional[Movie]: The selected starting Movie object, or None if not found.
    """
    movieName = input("Starting movie: ").strip()
    possibleMovies = db.findMoviesByName(movieName)
    if not possibleMovies:
        print("No movie was found. Try adding it.")
        selectedMovie = None
    elif len(possibleMovies) == 1:
        selectedMovie = possibleMovies[0]
        print(f"Movie '{selectedMovie.name}' found with release date {selectedMovie.releaseDate}.")
    else:
        selectedMovie = selectMovieFromList(possibleMovies)
        if selectedMovie:
            print(f"Movie '{selectedMovie.name}' selected with release date {selectedMovie.releaseDate}.")
    return selectedMovie


def runGame(db: Database, genres: List[str], solverStrategy: str, maxMovieSuggestions: int) -> None:
    """
    Run the game loop where players select movies based on genre connections.

    Args:
        db (Database): The movie database instance.
        genres (List[str]): A list of available genres.
        solverStrategy (str): The strategy to use for selecting next movies (e.g., "GREEDY").
        maxMovieSuggestions (int): The maximum number of movie suggestions to display.
    """
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

        candidateIDs = solver.findNextMovies(currentMovie)
        if not candidateIDs:
            print("No candidate movies found. Ending game.")
            break

        candidateMovies = sorted([db.movies[cid] for cid in candidateIDs], key=lambda m: m.name)
        printCandidateMovies(candidateMovies)

        choiceInput = input(
            "Enter candidate number or type movie name (or 'skip' to skip, 'escape' for special move): ").strip()
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
            continue
        else:
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


def runRebuildDB(dbInstance: Database, defaultCount: int) -> None:
    """
    Rebuild the movie database by fetching a specified number of movies.

    Args:
        dbInstance (Database): The movie database instance.
        defaultCount (int): The default number of movies to fetch if no input is provided.
    """
    countInput = input("Number of movies to fetch from TMDB (leave blank for default): ").strip()
    movieCount = int(countInput) if countInput else defaultCount
    print("Rebuilding database...")
    dbInstance.rebuild(movieCount)


def runModifyDB(db: Database) -> None:
    """
    Allow the user to add movies to the database by specifying movie titles.

    Args:
        db (Database): The movie database instance.
    """
    movieQuery = input("Movie to add (leave blank to exit): ").strip()
    while movieQuery:
        db.addMoviesByTitle(movieQuery)
        movieQuery = input("Movie to add (leave blank to exit): ").strip()


def runOptions() -> None:
    """
    Display the options menu. Currently a placeholder function.
    """
    print("Placeholder, for now the only strategy is greedy.")


def runHelp() -> None:
    """
    Display help information. Currently a placeholder function.
    """
    print("NA")


def main() -> None:
    """
    Main entry point for the Cine2NerdleSolver application.

    Initializes the database and game parameters, then processes user menu selections.
    """
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
