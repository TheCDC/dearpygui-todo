from typing import Callable, List
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
                num_items=10,
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
        self.rows = []

    def initialize(self):
        with dpg.group(horizontal=True):
            tag_add_item = dpg.generate_uuid()
            dpg.add_button(
                label="Add",
                callback=lambda s, a, u: self.add(s, dpg.get_value(tag_add_item), u),
            )
            dpg.add_input_text(
                label="New Task",
                tag=tag_add_item,
            )

        self.tag_table = dpg.generate_uuid()

        with dpg.table(tag=self.tag_table):
            dpg.add_table_column(
                parent=self.tag_table,
                label="",
                # width_stretch=True,
                width=32,
                width_fixed=True,
            )
            dpg.add_table_column(
                parent=self.tag_table,
                label="Done",
                width_stretch=False,
                width=0,
                width_fixed=True,
            )
            dpg.add_table_column(
                parent=self.tag_table, label="Content", width_stretch=True
            )
            dpg.add_table_column(
                parent=self.tag_table,
                label="Actions",
                width_stretch=False,
                width=0,
                width_fixed=True,
            )

        self.refresh_ui()

    def render_tree(self):
        while len(self.rows) > 0:
            row_to_delete = self.rows[-1]
            dpg.delete_item(row_to_delete)
            del self.rows[-1]

        for index_item, item in enumerate(self.service.items):
            with dpg.table_row(parent=self.tag_table) as row:
                self.rows.append(row)
                with dpg.table_cell():
                    with dpg.group(
                        drop_callback=self.drop_item,
                        user_data=index_item,
                        drag_callback=self.drag_item,
                    ) as group_drag:
                        h = 16
                        w = 16
                        with dpg.drawlist(width=w, height=h):
                            # dpg.draw_quad((0, 0), (0, h), (w, h), (w, 0))
                            dpg.draw_line((0, h * 2 / 8), (w, h * 2 / 8))
                            dpg.draw_line((0, h * 4 / 8), (w, h * 4 / 8))
                            dpg.draw_line((0, h * 6 / 8), (w, h * 6 / 8))
                        with dpg.drag_payload(
                            parent=group_drag,
                            drag_data=index_item,
                            drop_data=index_item,
                            user_data=index_item,
                        ):
                            dpg.add_text(index_item)
                            dpg.add_text(
                                self.service.get(index_item),
                                # user_data=index_item,
                            )

                dpg.add_button(
                    label=f"{'[ x ]' if  item.done else '[   ]'}",
                    callback=lambda s, a, u: self.toggle_item(s, a, u),
                    user_data=index_item,
                )
                dpg.add_text(item.name)
                with dpg.table_cell():
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label="delete",
                            callback=self.delete_item,
                            user_data=index_item,
                        )
                        dpg.add_button(label="archive")

    def _get_tag(self, index):
        return

    def save(self, *args):
        self.service.save()

    def encode_index(self, index: int, s: str):
        return f"{index} {s}"

    def decode_index(self, s: str):
        return int(s.split()[0])

    @ComponentBase.callback_requires_refresh
    def drop_item(self, s, a, u):
        index_from = a
        index_to = dpg.get_item_user_data(s)
        print(
            "drop_item",
            "from",
            a,
            "to",
            dpg.get_item_user_data(s),
        )
        self.service.move(index_from, index_to)

    def drag_item(self, s, a, u):
        vs = [s, a, u]
        print(*vs, end="")
        for v in vs:
            try:
                print("", v, ":", dpg.get_item_user_data(v), end="")
            except:
                pass
        print()
        pass

    @ComponentBase.callback_requires_refresh
    def add(self, sender, app_data: str, user_data):
        self.service.add(app_data)

    def refresh_ui(self):
        if self.tag_table:
            self.render_tree()
        self.save()

    @ComponentBase.callback_requires_refresh
    def toggle_item(self, s, a, u):
        self.service.toggle(u)

    @ComponentBase.callback_requires_refresh
    def delete_item(self, s, a, u):
        self.service.delete(u)

    def __iter__(self):

        for index, item in enumerate(self.service.items):
            yield self.render(index, item)
