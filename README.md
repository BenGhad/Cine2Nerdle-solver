# Cine2NerdleSolver

[Cine2Nerdle](https://www.cinenerdle2.app/battle) is a movie-connection game where two players take turns linking movies by their shared cast and crew. Although it looks simple, perfect play entails graph theory, combinatorial complexity, and clever heuristics to even enter the realm of possibility. This program attempts to fix that.

---

## Section 1: Technical Side

### Game Mechanics & Complexity

- **How It Works:**  
  Players take turns connecting movies by selecting those that share cast/crew members with the current movie. Each movie can only be used once, and shared personnel (e.g., actors, directors) have a usage limit to prevent overreliance. The objective is to reach a target winning condition based on genre or force your opponent into a position where they can no longer make a valid move.

- **Theoretical Interest:**  
  - **Complexity:** A brute-force approach would require exploring N! combinations, but if you ignore order (treating sequences like ABCDE and BCDAE as equivalent), the state space can be reduced to 2^n.  
  - **PSPACE-Completeness:** Perfect play in this game is theoretically PSPACE-complete(See [Generalized Geography](https://en.wikipedia.org/wiki/Generalized_geography))
  - **Greedy Heuristic:** As a practical alternative, a simple greedy heuristic is employed. Under the given constraints, this heuristic can be proven to be near-optimal even though it doesn’t explore the full complexity of the state space.

### Tech Stack & Design

- **Programming Language:** Python  
- **Data Fetching:** TMDB API is used to retrieve detailed movie information, including genres and credits.  
- **Serialization:** Joblib is used to efficiently save and load the movie database mappings.  
- **Data Models:**  
  - **Movie:** Stores details like ID, title, release date, genres, and associated cast/crew.  
  - **Person:** Represents actors, directors, and other crew members with unique IDs and names.  

- **Database Structure:**  
  Instead of storing a monolithic database, the program saves three core mappings for quick load times:
  - **Movie Mapping:** A dictionary mapping movie IDs to `Movie` objects.
  - **Person-Movie Mapping:** A mapping from person IDs to sets of movie IDs they appear in.
  - **Person-Genre Mapping:** A mapping from (person ID, genre) pairs to sets of movie IDs.
  
  This modular approach allows for creating a new database instance each time while only loading the essential structures, thus optimizing the save/load process.

### To-Dos & Future Enhancements

- **Database Optimization:**  
  - Streamline the connection between the database and main game logic to handle stale data and identity mismatches.  
  - Update the database instance in place to quickly remove invalid connections.

- **Solver Improvements:**  
  - Enhance the solver with deeper lookahead and improved heuristics
  - Experiment with alternative strategies beyond the current greedy method.

- **Feature Expansion:**  
  - Add support for different game modes, lifelines, bans-.  
  - Refine the crew linking definitions as per updated API data.

---

## Section 2: Usage

To get started with Cine2NerdleSolver:

1. **Run the Game:**  
   Simply execute the main module:
   ```bash
   python main.py
