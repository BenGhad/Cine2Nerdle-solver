import csv
from Cine2NerdleSolver.database import database
from Cine2NerdleSolver.solver import Cine2NerdleSolver


def main():
    print("Welcome to Cine2NerdleSolver")

    # Create a database instance and rebuild if needed.
    db_instance = database()
    count = 20000
    if input("Rebuild DB? (y/N): ").lower() == "y":
        db_instance.buildDB(count)

    # Load the database.
    loaded = db_instance.loadData("Cine2NerdleSolver/databases.joblib")
    if loaded is None:
        print("Failed to load database")
        return
    db = loaded

    # Ask for maximum links.
    max_links_input = input("Max links (1, 2, 3, 4, 5 or infinity): ").strip().lower()
    if max_links_input == "infinity":
        max_lintks = None
    else:
        try:
            max_links = int(max_links_input)
        except ValueError:
            print("Invalid input for max links. Defaulting to 3.")
            max_links = 3

    # Ask for genre choices.
    genres = [
        "Action", "Adventure", "Animation", "Comedy", "Crime",
        "Documentary", "Drama", "Family", "Fantasy", "History",
        "Horror", "Music", "Mystery", "Romance", "Science Fiction",
        "Thriller", "TV Movie", "War", "Western"
    ]
    for i, g in enumerate(genres):
        print(f"{i + 1}) {g}")
    winIndex = int(input("Winning Genre: "))
    loseIndex = int(input("Losing Genre: "))
    winCondition = genres[winIndex - 1]
    loseCondition = genres[loseIndex - 1]

    solver = Cine2NerdleSolver(db, winCondition, loseCondition)

    # Ask for the starting movie.
    movieStr = input("Starting movie: ").strip()
    possibleMovies = [m for m in db.movies if m.name.lower() == movieStr.lower()]
    if not possibleMovies:
        print("No movie was found. Exiting.")
        return
    elif len(possibleMovies) == 1:
        movie = possibleMovies[0]
        print(f"Movie '{movie.name}' found with release date {movie.release_date}.")
    else:
        print("Multiple movies found with that name. Please select the intended one:")
        for i, m in enumerate(possibleMovies):
            print(f"{i + 1}) {m.name} ({m.release_date})")
        while True:
            try:
                choice = int(input("Enter your choice (number): "))
                if 1 <= choice <= len(possibleMovies):
                    movie = possibleMovies[choice - 1]
                    break
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

        # Build candidate list from current movie's connections.
        candidate_indices = {}
        for genre, indices in movie.movies.items():
            for idx in indices:
                candidate_movie = db.movies[idx]
                if solver.isValid(movie, candidate_movie):
                    candidate_indices.setdefault(idx, set()).add(genre)
        if not candidate_indices:
            print("No valid candidate movies found.")
            continue  # try again

        # Order candidates: winning genre first, then others, then opponent genre.
        winning_candidates = []
        other_candidates = []
        opponent_candidates = []
        for idx, genres_set in candidate_indices.items():
            if solver.winning_genre in genres_set:
                winning_candidates.append(idx)
            elif solver.opponent_genre in genres_set:
                opponent_candidates.append(idx)
            else:
                other_candidates.append(idx)
        ordered_candidates = winning_candidates + other_candidates + opponent_candidates

        # Limit candidate list if max_links is set.
        if max_links is not None:
            ordered_candidates = ordered_candidates[:max_links]

        # Print the winning genre candidate list with numbers.
        print("Candidate movies:")
        for i, idx in enumerate(ordered_candidates, start=1):
            cand = db.movies[idx]
            genres_str = ", ".join(candidate_indices[idx])
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
                print("Invalid candidate number. Game over.")
                break
        # POWER UP HANDLING:
        elif choice_input == "skip":  # Skip -> Someone skips their turn
            solver.flipGenre()
            turns += 1
            continue
        else:
            # Look for a movie by name.
            matches = [m for m in db.movies if m.name.lower() == choice_input.lower()]

            if len(matches) == 0:
                choice_input = input("invalid input, skipped movie: ")
                if choice_input == "skip":
                    solver.flipGenre()
                    turns += 1
                    continue
                matches = [m for m in db.movies if m.name.lower() == choice_input.lower()]
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
                    print("skipping...")
                    solver.flipGenre()
                    turns += 1
                    continue

        if selected_movie is None:
            print("No valid movie selected. Game over.")
            break

        # Determine the candidate used for connection.
        candidate_movie = None
        for idx in ordered_candidates:
            cand = db.movies[idx]
            if cand.name.lower() == selected_movie.name.lower() and cand.release_date == selected_movie.release_date:
                candidate_movie = cand
                break
        if candidate_movie is None:
            candidate_movie = selected_movie

        # Update move.
        # For the first 3 turns, we do NOT update person frequency.
        update_freq = turns >= 3
        solver.add(candidate_movie, selected_movie, update_frequency=update_freq)
        movie = selected_movie
        solver.flipGenre()
        turns += 1

    print("Game over. Thanks for playing!")


if __name__ == '__main__':
    main()
