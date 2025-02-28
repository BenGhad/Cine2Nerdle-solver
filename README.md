Game Rules: https://www.cinenerdle2.app/how-to-play/battle/battle-2
 


In Cine2Nerdle you and your opponent take turns linking movies together by their cast/crew members until one of you wins.

There are 2 ways to win:

- You meet the Win Condition requirement of your Battle Kit (ex. play 7 horror movies)

- Your opponent fails to link a movie before their turn ends (25s per turn)

You can play a movie that has any shared actors, directors, writers, cinematographers and/or composers with the previous movie. However...
- You cannot play a movie that has already been played this game.
- A link can only be used a maximum of three times per game. If Emma Stone was used three different times as a link, you would no longer be able to link to a movie using Emma Stone.

This is just graph theory, there's probably a div1 codeforces problem here


This project is split into an offline database of TMDB's top 5000, and the actual game player itself. 

**1: Database**

An instance of Database contains a list of 5000 movie instances

**1.1 Person**

A Person has the following fields:

    name – A string representing the person’s full name.
    dateOfBirth (DOB) – A string or date object representing the person’s date of birth, used to distinguish individuals who share the same name.

**1.2 Movie**

A Movie object has the following fields:

    genres – A list of strings. Each string is a genre label (e.g., "Action", "Comedy"). A single movie can have multiple genres.
    name – A string representing the movie’s title.
    yearOfRelease – An integer representing the movie’s release year, used to distinguish movies with the same title.
    People - a list of people involved in the movie(actors, directors, etc)
    An instance of Genre-to-Movies GTM
**1.3 Genre-To-Movies**
There are 19 movie genres in TMDB. Each instance of GTM is linked to a specific Movie _M_, and 
maps each genre _gg_ to a list of movies that

    Have gg in their genres list.
    Share at least one actor or crew member with M (Representing a connection).
    Appear within the top 5000 movies in the database.
Formally: genreMovieMap: Map<String, List<Movie>>, where each key is a genre name and each value is the list of movies 
that satisfy the criteria

**2: The Game**

The game is played between two opponents; each has a target winning genre. 
The objective for each player is to navigate (via shared cast/crew) from one movie to another until 
one of the following conditions is met:

    A player has used enough movies of their winning genre (Generally 7).
    The opponent fails to choose a valid connecting movie in time (25-second turn timer per move).
**2.1 Data Structures**

- A set of movies that have **already been used** in the chain. No movie can appear twice
- A mapping from **Person** p to an integer indicating how many times they have been used in a connection. 
- The Winning Genres for both players

**2.2 Valid Connection**

A connection (A -> B) between two movies A and B is valid if and only if

- There is at least ONE shared Person p between A and B such that p has a frequency less than 3
  - For example, if A and B share two people, and one of those people has a frequency of 2, while the other has a frequency of 3, the connection is still valid (because the person with frequency 2 can still be “used”).
  - If all shared people have a frequency ≥ 3, the connection is not valid.
- B is not in the set of used movies

**2.3A Selection Logic**

On a player's turn, given the movie M:

- Search in M.GTM and find any movie that can form a valid connection with M and is in the player's winningGenre
  - if none are found, iterate through every other genre until a valid connection is found. 
  - The opponent's winning genre is checked last
- Once a valid movie N is found: 
  - add N to the set of used movies.
  - Identify all shared people between M and N and increment their frequency counts in the personFrequencyMap
  - Return N as the chosen movie

**To-Do:**

PROGRAMMING:

- Clean up database-to-main. connection with stale data and identity fraud (medium T-shirt -> Python makes me miserable)
- Modify database instance in place for faster times(small T-shirt -> delete invalid connections)
- Improve solver logic for better play(XXL T-Shirt)
  - Perfect play is physically impossible unless we solve PSPACE complete
  - Hardcode "lines", which requires a LOT of manual input
  - Some form of heuristic recognition
  - AI isn't exactly out of reach 
    - Movie-Actor graph isn't as interconnected as worst-case assumes, there's 
    a lot of connected components 
      - Movie A is interconnected with a lot of movies(Group A) but only 1 movie in there associates with Marvel movies(group B)
      - Which means ML could be computationally feasible if we only look ahead 1-2 turns and only consider win conditions 
    - An LLM might be worth experimenting with, although probably not
- Make seperate databases depending on computing power (Small T-shirt)
- Update crew linking definition (Medium T-shirt -> undocumented API)
  - 'Director', 'Novel', 'Book', 'Short Story', 'Writer', 'Teleplay', 'Screenplay', 'Original Music Composer' and 'Director of Photography'.

CONCEPTUALLY:

- Modify database to align with Cine2Nerdle instead of TMDB(Large T-shirt -> undocumented API)
  - eg the Action Comedy genre is not on TMDB, and it doesn't mean action movies that are comedies
- Add actors as a win condition (Large T-shirt -> secondary database)
- Add support for items/lifelines/bans/kits (medium T-shirt -> restructure existing code)
- Distinguish top 5k movies (small T-shirt -> add a count)
- Some form of autocomplete/guessing (Large T-shirt -> nuff said)
- Some form of auto-interact with the game (XXXL T-shirt -> Entirely different project)
  - C WASM JS browser extension 
  - Screen/Page parse + macro 
- Different playstyles 
  - (Near)Perfect Play: See Technical
  - Anti-human: Ignore genre, only play obscure films to flag opponent (Medium T-shirt -> database restructuring)
  - Greedy(current implementation): Pick whatever works, prioritizing winCon (Medium T-shirt -> Bugfixing)
  - Trapper: A mix of Anti-human & Greedy, Go for win-cons, but if a "line" exists, setup the trap (XL T-shirt -> See reddit)
  
**2.3B Logic Analysis**

This is a greedy heuristic - it always plays a movie in the winning genre, then falls back on others. 

This method is
generally fine, but falls apart in perfect play. It fails to consider:
- A move that delays immediate progress but blocks off strong connections for the opponent
- Resource management - how does a movie impact future valid movies? 

Cine2Nerdle is combinatorial game with a very complex state.
The minimax algorithm would always play perfectly,but would be 
computationally infeasible(O(n!)) 

There is theoretically a DP solution(O(2^n)),  but the dependency on freq counts and a massive statespace suggests that
perfect play falls into PSPACE-Complete. 

That is, we wouldn't even be able to store states.
If a movie was 1 atom, we'd need more than 100 planet earths to store the states for 100 movies


**2.4 Winning Condition**

A player wins if:
- They have selected enough movies of their winning Genre
- Their opponent cannot produce a valid connecting movie on time
