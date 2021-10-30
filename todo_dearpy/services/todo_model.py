from dataclasses import asdict, dataclass
from json.decoder import JSONDecodeError
from typing import List
import json
from pathlib import Path


@dataclass
class TodoItem:
    name: str
    done: bool


class TodoService:
    def __init__(self, db_path=None) -> None:
        self.db_path = db_path if db_path else str(Path.home() / "todo_dearpy.db")
        self.__items: List[TodoItem] = []
        try:
            with open(self.db_path, "r") as f:
                self.__items = [TodoItem(**i) for i in json.load(f)]
        except FileNotFoundError:
            self.save()
        except JSONDecodeError:
            self.save()

    def add(self, name: str, done: bool = False):
        self.__items.append(TodoItem(name, done))

    def delete(self, index: int):
        del self.__items[index]

    def toggle(self, index: int):
        self.items[index].done = not self.items[index].done

    def save(self):

        with open(self.db_path, "w") as f:
            json.dump([asdict(i) for i in self.__items], f)

    def get(self, index: int):
        return self.items[index]

    @property
    def items(self):
        return self.__items

    def json(self):
        return json.dumps([asdict(i) for i in self.items])
