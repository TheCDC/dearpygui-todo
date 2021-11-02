from datetime import datetime
from typing import Callable, List
from todo_dearpy.services.todo_model import TodoItem, TodoService
from todo_dearpy.ui.base import ComponentBase
import dearpygui.dearpygui as dpg


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
        self.filter_id = dpg.generate_uuid()
        self.value_registry = dpg.add_value_registry()
        self.id_popup_create = dpg.generate_uuid()
        self.id_window = None

    def initialize(self, id_window: int):
        self.id_window = id_window
        now = datetime.now()

        with dpg.window(
            id=self.id_popup_create,
            modal=True,
            show=False,
        ) as modal:
            dpg.add_text("modal")
        with dpg.table(header_row=False):
            dpg.add_table_column(width_stretch=True)
            dpg.add_table_column(width_fixed=True)
            dpg.add_table_column(width_fixed=True)
            dpg.add_table_column(width_fixed=True)
            dpg.add_table_column(width_fixed=True)
            with dpg.table_row():
                tag_add_item = dpg.generate_uuid()
                dpg.add_input_text(
                    label="New Task",
                    tag=tag_add_item,
                )
                dpg.add_date_picker(
                    level=dpg.mvDatePickerLevel_Day,
                    default_value={
                        "year": now.year,
                        "month_day": now.day,
                        "month": now.month,
                    },
                )
                dpg.add_time_picker(
                    default_value={
                        "hour": now.hour,
                        "min": now.minute,
                        "sec": now.second,
                    }
                )
                dpg.add_separator()
                dpg.add_button(
                    label="Add",
                    callback=lambda s, a, u: self.add(
                        s, dpg.get_value(tag_add_item), u
                    ),
                )

        with dpg.group(horizontal=True):
            dpg.add_input_text(
                label="Filter",
                callback=lambda s, a, u: [dpg.set_value(self.filter_id, a), print(a)],
            )
        dpg.add_button(
            label="Create new with popup", callback=self.callback_create_new_popup
        )

        self.tag_table = dpg.generate_uuid()

        with dpg.table(
            tag=self.tag_table,
            policy=dpg.mvTable_SizingFixedFit,
            callback=self.callback_table,
            sortable=True,
        ):
            dpg.add_table_column(
                parent=self.tag_table,
                label="Done",
                width_stretch=False,
                width=0,
                width_fixed=True,
                no_sort=True,
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
                no_sort=True,
            )

        self.refresh_ui()

    def callback_create_new_popup(self, s, a, u):
        dpg.configure_item(self.id_popup_create, show=True)
        pass

    def callback_table(self, sender, sort_specs):

        # sort_specs scenarios:
        #   1. no sorting -> sort_specs == None
        #   2. single sorting -> sort_specs == [[column_id, direction]]
        #   3. multi sorting -> sort_specs == [[column_id, direction], [column_id, direction], ...]
        #
        # notes:
        #   1. direction is ascending if == 1
        #   2. direction is ascending if == -1

        # no sorting case
        if sort_specs is None:
            return

        rows = dpg.get_item_children(sender, 1)

        # create a list that can be sorted based on first cell
        # value, keeping track of row and value used to sort
        sortable_list = []
        for row in rows:
            content_cell = dpg.get_item_children(row, 1)[1]
            content_id = dpg.get_item_children(content_cell, 1)[0]
            v = dpg.get_item_user_data(content_id)
            sortable_list.append([row, v])

        def _sorter(e):
            return e[1][1].name

        sortable_list.sort(key=_sorter, reverse=sort_specs[0][1] < 0)

        # create list of just sorted row ids
        new_order = []
        for pair in sortable_list:
            new_order.append(pair[0])

        dpg.reorder_items(sender, 1, new_order)

    def render_tree(self):
        while len(self.rows) > 0:
            row_to_delete = self.rows[-1]
            dpg.delete_item(row_to_delete)
            del self.rows[-1]
        for index_item, item in enumerate(self.service.items):
            with dpg.table_row(parent=self.tag_table, filter_key=item.name) as row:

                self.rows.append(row)
                # task status
                with dpg.table_cell():
                    with dpg.group():

                        dpg.add_button(
                            label=f"{'[ x ]' if  item.done else '[   ]'}",
                            callback=lambda s, a, u: self.toggle_item(s, a, u),
                            user_data=(index_item, item),
                        )
                # task content
                with dpg.table_cell():
                    with dpg.group(
                        drop_callback=self.drop_item,
                        user_data=(index_item, item),
                        drag_callback=self.drag_item,
                    ) as group_content:
                        dpg.add_text(item.name)
                    with dpg.drag_payload(
                        parent=group_content,
                        drag_data=(index_item, item),
                        drop_data=(index_item, item),
                        user_data=item,
                    ):
                        dpg.add_text(f"being_dragged={group_content}")
                        dpg.add_text(f"index_item {index_item}")
                        dpg.add_text(str(item))
                # Task actions
                with dpg.table_cell():
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label="delete",
                            callback=self.delete_item,
                            user_data=(index_item, item),
                        )
                        dpg.add_button(
                            label="archive",
                        )

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
        index_from, item_from = a
        index_to, item_to = dpg.get_item_user_data(s)
        print(
            s,
            "drop_item",
            item_to,
            "from index",
            a,
            "to index",
            index_to,
            "u=",
            u,
        )
        self.service.move(index_from, index_to)

    def drag_item(self, s, a, u):
        vs = [("sender", s), ("app", a), ("user", u)]
        print("drag_item", *vs, dpg.get_item_user_data(s))
        # print("drag_item", *vs, end="")
        # for v in vs:
        #     try:
        #         print("", v, ":", dpg.get_item_user_data(v), end="")
        #     except:
        #         pass
        # print()
        # pass

    @ComponentBase.callback_requires_refresh
    def add(self, sender, app_data: str, user_data):
        self.service.add(app_data)

    def refresh_ui(self):
        if self.tag_table:
            self.render_tree()
        self.save()

    @ComponentBase.callback_requires_refresh
    def toggle_item(self, s, a, u):
        self.service.toggle(u[0])

    @ComponentBase.callback_requires_refresh
    def delete_item(self, s, a, u):
        self.service.delete(u[0])

    def __iter__(self):

        for index, item in enumerate(self.service.items):
            yield self.render(index, item)
