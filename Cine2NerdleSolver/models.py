# models.py
from dataclasses import dataclass
from typing import Set, List

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
    id: int
    name: str
    releaseDate: str
    genres: List[str]
    people: Set[Person]
