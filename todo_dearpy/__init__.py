from typing import Callable
import dearpygui.dearpygui as dpg
from dataclasses import dataclass
from todo_dearpy.components import Listbox_TodoManager, Table_TodoManager

from todo_dearpy.services.todo_model import TodoService, TodoItem
import random

from todo_dearpy.ui.base import ComponentBase


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
    render_format=lambda index, item: f"{'[ x ]' if item.done else '[   ]'} {item.name}",
)

table_todos = Table_TodoManager()

with dpg.value_registry():
    bool_value = dpg.add_bool_value(default_value=True)
    string_value = dpg.add_string_value(default_value="Default string")
with dpg.window(label="Tutorial") as w1:
    with dpg.group(horizontal=False):
        lbtdm.initialize()
        table_todos.initialize()
dpg.set_primary_window(w1, True)
dpg.create_viewport(
    title="Custom Title",
)
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
