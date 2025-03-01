from Cine2NerdleSolver.database import database
from Cine2NerdleSolver.solver import Cine2NerdleSolver


def main():
    while True:
        # Default Settings # Todo: cache/save settings
        strategy = "GREEDY"
        candidateSize = 5
        count = 20000

        # Initializations:
        genres = [
            "Action", "Adventure", "Animation", "Comedy", "Crime",
            "Documentary", "Drama", "Family", "Fantasy", "History",
            "Horror", "Music", "Mystery", "Romance", "Science Fiction",
            "Thriller", "TV Movie", "War", "Western"
        ]
        db_instance = database()
        loaded = db_instance.loadData("Cine2NerdleSolver/databases.joblib")
        if loaded is None:
            print("Failed to load database")
            return
        db = loaded

        # Menu
        print("Welcome to Cine2NerdleSolver")
        print("1) Solve")
        print("2) Rebuild DB")
        print("3) Modify DB")
        print("4) Options")
        print("5) Help")
        print("6) Exit")
        inpStr = input("Enter your choice: ")
        if inpStr.lower() == "help": inpStr = "5"
        inp = int(inpStr)

        # Solver
        if inp == 1:
            # Game state initialization
            for i, g in enumerate(genres):
                print(f"{i + 1}) {g}")
            winIndex = int(input("Winning Genre: "))
            loseIndex = int(input("Losing Genre: "))
            winCondition = genres[winIndex - 1]
            loseCondition = genres[loseIndex - 1]

            # Get Links
            max_links_input = input("Max links (1, 2, 3, 4, 5 or infinity): ").strip().lower()
            if max_links_input == "infinity":
                max_links = None
            else:
                try:
                    max_links = int(max_links_input)
                except ValueError:
                    print("Invalid input for max links. Defaulting to 3.")
                    max_links = 3

            solver = Cine2NerdleSolver(db, winCondition, loseCondition, strategy, candidateSize, max_links)

            # Get start
            movieStr = input("Starting movie: ").strip()
            possibleMovies = [m for m in db.movies if m.name.lower() == movieStr.lower()]  # TODO: Better search for QOL
            if not possibleMovies or len(possibleMovies) == 0:  # TODO: Add movie DURING the game
                print("No movie was found. Try adding it ")
                break
            elif len(possibleMovies) == 1:
                movie = possibleMovies[0]
                print(f"Movie '{movie.name}' found with release date {movie.release_date}.")
            else:
                print("Multiple movies found with that name. Please select the intended one:")
                for i, m in enumerate(possibleMovies):
                    print(f"{i + 1}) {m.name} ({m.release_date})")
                while True:
                    try:
                        choice = int(input("Enter your choice (number, 0 if exiting): "))
                        if 1 <= choice <= len(possibleMovies):
                            movie = possibleMovies[choice - 1]
                            break
                        elif choice == 0:
                            print("Exiting...")
                            return  # Todo: double break
                        else:
                            print("Choice out of range. Please try again.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")
                print(f"Movie '{movie.name}' selected with release date {movie.release_date}.")

                solver.used_movies.add(movie.name + "|" + movie.release_date)

                # Game loop.
                turns = 0
                while True:
                    current_player = "Player 1" if turns % 2 == 0 else "Player 2"
                    print(f"\n{current_player}'s turn.")
                    print(f"Current movie: {movie.name} ({movie.release_date})")

                    # Todo: Modify database mid-game for the purpose of speed(delete used movies) & refresh after

                    # Output candidates
                    ordered_candidates = solver.findNextMovies(movie)
                    print("Candidate movies:")
                    for i, cand in enumerate(ordered_candidates, start=1):
                        genres_str = ""
                        for genre in cand.genres:
                            genres_str += genre + ", "
                        print(f"{i}) {cand.name} ({cand.release_date}) - Connection genres: {genres_str}")

                    # TODO: In case of blocks, print the non-winning genre candidate list
                    # Get user's choice: either a number or a movie name.
                    choice_input = input("Enter candidate number or type movie name: ").strip()
                    selected_movie = None
                    if choice_input.isdigit():
                        choice_num = int(choice_input)
                        if 1 <= choice_num <= len(ordered_candidates):
                            selected_movie = db.movies[ordered_candidates[choice_num - 1]]
                        else:
                            print("Invalid candidate number. Game over") #TODO: Re-ask
                            break
                    # POWER UP HANDLING:
                    elif choice_input == "skip":  # Skip -> Someone skips their turn
                        solver.flipGenre()
                        turns += 1
                        continue
                    elif choice_input == "escape":
                        # Todo: Implement escape here(pick non-win con movie)
                        print("placeholder rizz")
                    else:
                        # Look for a movie by name.
                        matches = [m for m in db.movies if m.name.lower() == choice_input.lower()]

                        # Todo: Better power up handling
                        if len(matches) == 0:
                            choice_input = input("No movies found, you need to skip/use an escape: ")
                            if choice_input == "skip":
                                solver.flipGenre()
                                turns += 1
                                continue
                        if len(matches) == 1:
                            selected_movie = matches[0]
                        else:
                            print("Multiple movies found. Please select the intended one:")
                            for i, m in enumerate(matches):
                                print(f"{i + 1}) {m.name} ({m.release_date})")
                            choice = int(input("Enter your choice (number): "))
                            if 1 <= choice <= len(matches):
                                selected_movie = matches[choice - 1]
                            else:
                                print("unknown input, time to skip ig")
                                solver.flipGenre()
                                turns += 1
                                continue

                    # Update move.
                    # For the first 3 turns, we do NOT update person frequency.
                    update_freq = turns >= 3
                    solver.add(movie, selected_movie, update_frequency=update_freq)
                    movie = selected_movie
                    solver.flipGenre()
                    turns += 1

        # Rebuilder
        elif inp == 2:
            countStr = input("Number of movies(leave blank for default): ")
            if countStr != "":
                count = int(countStr)
            print("Rebuilding database...")
            db_instance.buildDB(count)

            # Load the database.
            loaded = db_instance.loadData("Cine2NerdleSolver/databases.joblib")
            if loaded is None:
                print("Failed to load database")
                return
            db = loaded
            print("Rebuilt and Reloaded Database")
        # Modifier for now it's just add
        elif inp == 3:
            movieStr = input("Movie to add(leave blank to exit): ")
            while movieStr != "":
                db.addMovie(movieStr)
                movieStr = input("Movie to add(leave blank to exit): ")
        # Options, for now it's just strategy
        elif inp == 4:
            print("Placeholder, for now the only strategy is greedy")
        # Quick rundown of how the user can use the program
        elif inp == 5:
            print("NA")

        elif inp == 6:
            print("Exiting")
            break


if __name__ == '__main__':
    main()
