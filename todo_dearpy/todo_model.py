from dataclasses import dataclass
from typing import List


@dataclass
class TodoItem:
    name: str
    done: bool


class TodoService:
    def __init__(self) -> None:
        self.__items: List[TodoItem] = []

    def add(self, name: str, done: bool):
        self.__items.append(TodoItem(name, done))

    def delete(self, index: int):
        self.__items.remove(index)

    def toggle(self, index: int):
        self.items[index].done = not self.items[index].done

    @property
    def items(self):
        return self.__items
