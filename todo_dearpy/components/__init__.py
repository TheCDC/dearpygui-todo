from typing import Callable
import random
from todo_dearpy.services.todo_model import TodoItem, TodoService
from todo_dearpy.ui.base import ComponentBase
import dearpygui.dearpygui as dpg


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
        with dpg.value_registry():
            self.string_value = dpg.add_string_value(default_value="Default string")
        with dpg.handler_registry():
            m_drag = dpg.add_mouse_drag_handler(button=dpg.mvMouseButton_Left)
        with dpg.group(
            horizontal=False,
        ):
            with dpg.group(horizontal=True):
                textbox_tag = dpg.generate_uuid()
                dpg.add_button(
                    label="add",
                    user_data=textbox_tag,
                    callback=lambda s, a, u: [
                        self.add(s, dpg.get_value(u), u),
                        dpg.set_value(u, ""),
                    ],
                )
                textbox = dpg.add_input_text(label="New Todo", tag=textbox_tag)
        with dpg.group(
            horizontal=True,
        ):
            self.ui_element_id = dpg.add_listbox(
                list(self),
                num_items=32,
                callback=self.clicked,
                drag_callback=lambda s, a, u: print("drag", s, a, u),
                drop_callback=lambda s, a, u: print("drop", s, a, u),
                tracked=True,
                payload_type="string",
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
        dpg.set_value(self.ui_element_id, self.render(index, self.service.get(index)))

    @ComponentBase.callback_requires_refresh
    def add(self, sender, app_data: str, user_data):
        self.service.add(app_data)

    def refresh_ui(self):
        if self.ui_element_id:
            dpg.configure_item(self.ui_element_id, items=list(self))

    def render(self, index, item):
        return self.encode_index(index, self.render_format(index, item))

    def __iter__(self):

        for index, item in enumerate(self.service.items):
            yield self.render(index, item)


class Table_TodoManager(ComponentBase):
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
        with dpg.table(callback=lambda s, a, u: print(s, a, u)):
            dpg.add_table_column()
            dpg.add_table_column()
            dpg.add_table_column()
            for item in self.service.items:
                with dpg.table_row():
                    dpg.add_button(label=f"{item.done}")
                    dpg.add_text(item.name)
                    dpg.add_button(label="x")

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
        dpg.set_value(self.ui_element_id, self.render(index, self.service.get(index)))

    @ComponentBase.callback_requires_refresh
    def add(self, sender, app_data: str, user_data):
        self.service.add(app_data)

    def refresh_ui(self):
        if self.ui_element_id:
            dpg.configure_item(self.ui_element_id, items=list(self))

    def render(self, index, item):
        return self.encode_index(index, self.render_format(index, item))

    def __iter__(self):

        for index, item in enumerate(self.service.items):
            yield self.render(index, item)
