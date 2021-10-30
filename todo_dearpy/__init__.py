from typing import Callable
import dearpygui.dearpygui as dpg
from dataclasses import dataclass

from todo_dearpy.todo_model import TodoService, TodoItem
import random

from todo_dearpy.ui.base import ComponentBase


class Listbox_TodoManager(ComponentBase):
    def _wrap_pre_post(self, method, args, kwargs):
        res = method(*args, **kwargs)
        self.refresh_ui()
        return res

    def __init__(
        self, payload=None, render_format: Callable[[int, TodoItem], str] = None
    ) -> None:
        payload = payload if payload else []
        self.render_format = (
            render_format
            if render_format
            else lambda index, item: f"[{'x' if item.done else ' '}] {str(item)}"
        )
        self.service = TodoService()
        self.ui_element_id = None

    def initialize(self):
        self.ui_element_id = dpg.add_listbox(
            list(self),
            label="Todos",
            num_items=32,
            user_data="yeet",
            callback=self.clicked
            # callback=lambda a, b, c, *args, **kwargs: (
            #     print(a, b, c, args, kwargs, self.clicked),
            #     # self.clicked(*args, **kwargs),
            # ),
        )
        self.button1_id = dpg.add_button(
            label="test", callback=lambda *args: print(self.service.json())
        )

        self.button2_id = dpg.add_button(
            label="save",
            callback=lambda *args, **kwargs: print(args, kwargs, self.save()),
        )
        self.button3_id = dpg.add_button(
            label="add new",
            callback=lambda: self.add(None, str(random.randint(1, 1000)), None),
        )

    def save(self, *args):
        self.service.save()

    def encode_index(self, index: int, s: str):
        return f"{index} {s}"

    def decode_index(self, s: str):
        return int(s.split()[0])

    @ComponentBase.callback_requires_refresh
    def clicked(self, sender, app_data: str, user_data):
        onscreen_string = app_data
        index = self.decode_index(onscreen_string)
        self.service.toggle(index)

    @ComponentBase.callback_requires_refresh
    def add(self, sender, app_data: str, user_data):
        self.service.add(app_data)

    def refresh_ui(self):
        if self.ui_element_id:
            dpg.configure_item(self.ui_element_id, items=list(self))

    def __iter__(self):

        for index, item in enumerate(self.service.items):
            yield self.encode_index(index, self.render_format(index, item))


fruits = (
    "Apple",
    "Banana",
    "Cherry",
    "Kiwi",
    "Mango",
    "Orange",
    "Pineapple",
    "Strawberry",
    "Watermelon",
)
dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()


def button_callback(sender, app_data, user_data):
    print(f"sender is: {sender}")
    print(f"app_data is: {app_data}")
    print(f"user_data is: {user_data}")


def log(sender, app_data, user_data):
    print(f"sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")


lbtdm = Listbox_TodoManager(
    None,
    render_format=lambda index, item: f"{'YEET' if item.done else 'NAW'} {item.name}",
)

with dpg.value_registry():
    bool_value = dpg.add_bool_value(default_value=True)
    string_value = dpg.add_string_value(default_value="Default string")
with dpg.window(label="Tutorial", width=300, height=400) as w1:
    lbtdm.initialize()
dpg.set_primary_window(w1, True)
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
