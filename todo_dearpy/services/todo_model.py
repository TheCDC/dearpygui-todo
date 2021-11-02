from dataclasses import asdict, dataclass
from json.decoder import JSONDecodeError
from typing import List, Type
import json
from pathlib import Path


@dataclass
class TodoItem:
    index: int
    name: str
    done: bool


class TodoService:
    def __init__(self, db_path=None) -> None:
        self.db_path = db_path if db_path else str(Path.home() / "todo_dearpy.db")
        self.__items: List[TodoItem] = []
        try:
            with open(self.db_path, "r") as f:
                self.__items = [TodoItem(**i) for i in json.load(f)]
        except (FileNotFoundError, TypeError):
            self.save()
        except JSONDecodeError:
            self.save()

    def add(self, name: str, done: bool = False):
        idx = 0
        self.__items.insert(idx, TodoItem(idx, name, done))
        self._refresh_indices()

    def delete(self, index: int):
        del self.__items[index]
        self._refresh_indices()

    def _refresh_indices(self):
        for index, i in enumerate(self.items):
            i.index = index

    def toggle(self, index: int):
        self.items[index].done = not self.items[index].done

    def save(self):

        with open(self.db_path, "w") as f:
            json.dump([asdict(i) for i in self.__items], f)

    def get(self, index: int) -> TodoItem:
        return self.items[index]

    @property
    def items(self):
        return self.__items

    def json(self):
        return json.dumps([asdict(i) for i in self.items])

    def move(self, index_from, index_to):
        old = self.__items[:]
        try:
            self.items.insert(index_to, self.items.pop(index_from))
        except (IndexError, TypeError) as e:
            self.__items = old
            raise e
        self._refresh_indices()
