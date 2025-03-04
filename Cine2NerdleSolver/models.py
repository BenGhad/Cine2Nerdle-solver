"""
Models module for Cine2NerdleSolver.

Defines the data models used in the application, including Person and Movie.
"""

from dataclasses import dataclass
from typing import Set, List


@dataclass(frozen=True)
class Person:
    """
    Represents a person (actor or crew member) involved in a movie.

    Attributes:
        id (int): The unique identifier for the person.
        name (str): The name of the person.
    """
    id: int
    name: str

    def __eq__(self, other):
        if not isinstance(other, Person):
            return NotImplemented
        return self.id == other.id and self.name == other.name

    def __hash__(self):
        return hash((self.id, self.name))


@dataclass
class Movie:
    """
    Represents a movie with details such as title, release date, genres, and associated people.

    Attributes:
        id (int): The unique identifier for the movie.
        name (str): The title of the movie.
        releaseDate (str): The release date of the movie.
        genres (List[str]): A list of genres the movie belongs to.
        people (Set[Person]): A set of Person objects associated with the movie.
    """
    id: int
    name: str
    releaseDate: str
    genres: List[str]
    people: Set[Person]
