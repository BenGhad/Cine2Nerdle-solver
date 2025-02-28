from dataclasses import dataclass # classes just store data, dataclass for boilerplate
from typing import Set, List, Dict


@dataclass(frozen=True)
class Person:
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
    name: str
    release_date: str
    genres: List[str]
    people: Set[Person]
    movies: Dict[str, Set[int]]
