# Standard library imports
import os
from datetime import date, datetime, timedelta

# Third-party imports
import asynckivy
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import SlideTransition
from kivy.utils import platform
from kivymd.app import MDApp

# Local/application-specific imports
from custom_widgets import (
    CompletedWidget,
    ItemButton,
    ItemDialog,
    TaskButton,
    TaskDialog,
)
from data_structures import LinkedList, StatsScreen, Trie
import database


class MainApp(MDApp):
    """
    Main application class for managing task-related UI and data.
    """

    def __init__(self, **kwargs):
        """
        - Initialize the application, setting up internal data structures.
        - Stores a reference so only a single unedited new widget can exist at a time. Allows for quick dismissal of widget's dialog box if no changes are made.
        """

        super().__init__(**kwargs)

        self.screen_position_lookup = {
            "Current": 0,
            "Repeat": 1,
            "List": 2,
            "Stats": 3,
        }
        self.current_task_list = LinkedList("Current Tasks", "Task")
        self.repeat_task_list = LinkedList("Repeat Tasks", "Task")
        self.item_list = LinkedList("Item List", "Item")
        self.stats_screen = StatsScreen()
        self.autocomplete = Trie()
        self.unedited_new_widget = None

    def build(self):
        """
        Configure initial window size and app theme.
        """

        if platform in ("android", "ios"):
            Window.fullscreen = "auto"
        else:
            Window.size = (360, 740)

        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Aliceblue"
        self.color_index = 0

    def on_start(self):
        """
        If a previous database exists, the application is rebuilt to its previous state.
        """

        super().on_start()

        if os.path.exists("main.db"):

            async def set_app():
                connection, cursor = database.initialize_db()
                self.rebuild_current_task_list(cursor)
                self.rebuild_repeat_task_list(cursor)
                self.rebuild_item_list(cursor)
                self.rebuild_stats_screen(cursor)
                self.rebuild_completed_tasks(cursor)
                self.rebuild_purchased_items(cursor)
                self.rebuild_item_locations(cursor)

            asynckivy.start(set_app())
            os.remove("main.db")

        for title in self.stats_screen.completed_tasks.keys():
            self.autocomplete.insert(title)
        for title in self.stats_screen.purchased_items.keys():
            self.autocomplete.insert(title)
        for location in self.stats_screen.locations:
            self.autocomplete.insert(location)

    def rebuild_current_task_list(self, cursor):
        """
        Rebuild the current task list from the database.
        """

        current_rows = database.get_task_list(cursor, "current_task_list")
        current_container = self.root.ids.current_screen_container

        for row in current_rows:
            node = self.current_task_list.add_node_handler()
            node.id_num = row[0]
            node.title = row[1]
            node.first_step = row[2]
            node.second_step = row[3]
            node.third_step = row[4]
            node.start_date = datetime.strptime(row[5], "%Y-%m-%d").date()
            node.repeat_toggle = True if row[6] else False
            node.interval_index = row[7]
            widget = TaskButton(task_node=node)
            widget.ids.task_button_text.text = node.title
            current_container.add_widget(widget)

    def rebuild_repeat_task_list(self, cursor):
        """
        Rebuild the current task list from the database.
        """

        repeat_rows = database.get_task_list(cursor, "repeat_task_list")
        repeat_container = self.root.ids.repeat_screen_container

        for row in repeat_rows:
            node = self.repeat_task_list.add_node_handler()
            node.id_num = row[0]
            node.title = row[1]
            node.first_step = row[2]
            node.second_step = row[3]
            node.third_step = row[4]
            node.start_date = datetime.strptime(row[5], "%Y-%m-%d").date()
            node.repeat_toggle = True if row[6] else False
            node.interval_index = row[7]
            widget = TaskButton(task_node=node)
            widget.ids.task_button_text.text = node.title
            repeat_container.add_widget(widget)

        self.update_current_screen()

    def rebuild_item_list(self, cursor):
        """
        Rebuild the item list from the database.
        """

        item_rows = database.get_item_list(cursor)
        item_container = self.root.ids.list_screen_container

        for row in item_rows:
            node = self.item_list.add_node_handler()
            node.id_num = row[0]
            node.title = row[1]
            node.quantity = row[2]
            node.item_location = row[3]
            node.interval_index = row[4]
            widget = TaskButton(task_node=node)
            widget.ids.task_button_text.text = node.title
            item_container.add_widget(widget)

    def rebuild_stats_screen(self, cursor):
        """
        Rebuild the stats screen with updated data from the database.
        """

        stats_row = database.get_stats_data(cursor)
        self.stats_screen.current_level = stats_row[0][0]
        self.stats_screen.current_xp = stats_row[0][1]
        self.stats_screen.start_level = stats_row[0][2]
        self.stats_screen.next_level = stats_row[0][3]

    def rebuild_completed_tasks(self, cursor):
        """
        Rebuild the list of completed tasks from the database.
        """

        completed_task_rows = database.get_stats_maps(cursor, "completed_tasks")
        for title, count in completed_task_rows:
            self.stats_screen.completed_tasks[title] = count

    def rebuild_purchased_items(self, cursor):
        """
        Rebuild the list of purchased items from the database.
        """

        purchased_item_rows = database.get_stats_maps(cursor, "purchased_items")
        for title, count in purchased_item_rows:
            self.stats_screen.purchased_items[title] = count

    def rebuild_item_locations(self, cursor):
        """
        Rebuild the list of item locations from the database.
        """

        item_locations_rows = database.get_item_locations(cursor)
        for location in item_locations_rows:
            self.stats_screen.locations.add(location)

    def on_stop(self):
        """
        Creates SQL database to store relevant data on application close.
        """

        connection, cursor = database.initialize_db()
        current_list = self.current_task_list.node_lookup.values()
        database.save_task_list(cursor, current_list, "current_task_list")
        repeat_list = self.repeat_task_list.node_lookup.values()
        database.save_task_list(cursor, repeat_list, "repeat_task_list")
        item_list = self.item_list.node_lookup.values()
        database.save_item_list(cursor, item_list)
        stats_screen = self.stats_screen
        database.save_stats_data(cursor, stats_screen)
        completed_tasks = self.stats_screen.completed_tasks
        database.save_stats_maps(cursor, completed_tasks, "completed_tasks")
        purchased_items = self.stats_screen.purchased_items
        database.save_stats_maps(cursor, purchased_items, "purchased_items")
        item_locations = self.stats_screen.locations
        database.save_item_locations(cursor, item_locations)
        database.close_db(connection, cursor)

        return super().on_stop()

    def on_switch_tabs(self, nav_bar, nav_item, item_icon, item_text):
        """
        Handle switching between different tabs in the UI. Default function of MDNavigationBar.
        """

        current_screen = self.root.ids.main_screen_manager.current
        current_pos = self.screen_position_lookup[current_screen]
        target_pos = self.screen_position_lookup[item_text]

        if target_pos > current_pos:
            slide_direction = "left"
        elif target_pos < current_pos:
            slide_direction = "right"
        else:
            return

        self.root.ids.main_screen_manager.transition = SlideTransition(
            direction=slide_direction
        )

        if item_text == "Repeat" or item_text == "List":
            self.sort_and_update_screen(item_text)
        elif item_text == "Current":
            self.update_current_screen()
            self.sort_and_update_screen(item_text)
        elif item_text == "Stats":
            self.update_stats_screen()

        Clock.schedule_once(lambda dt: self.set_current_screen(item_text), 0.2)

    def sort_and_update_screen(self, screen_name):
        """
        Sort tasks or items and update the corresponding screen.
        """

        if screen_name == "Current":
            self.current_task_list.sort_linked_list()
            container = self.root.ids.current_screen_container
            container.clear_widgets()
            current = self.current_task_list.head.next
            while current != self.current_task_list.tail:
                task_widget = TaskButton(task_node=current)
                container.add_widget(task_widget)
                current = current.next
        elif screen_name == "Repeat":
            self.repeat_task_list.sort_linked_list()
            container = self.root.ids.repeat_screen_container
            container.clear_widgets()
            current = self.repeat_task_list.head.next
            while current != self.repeat_task_list.tail:
                task_widget = TaskButton(task_node=current)
                container.add_widget(task_widget)
                current = current.next
        elif screen_name == "List":
            self.item_list.sort_linked_list()
            container = self.root.ids.list_screen_container
            container.clear_widgets()
            current = self.item_list.head.next
            while current != self.item_list.tail:
                item_widget = ItemButton(item_node=current)
                container.add_widget(item_widget)
                current = current.next

    def set_current_screen(self, screen_name):
        """
        Set the current screen based on navigation.
        """

        self.root.ids.main_screen_manager.current = screen_name

    def add_to_active_screen(self, screen_name):
        """
        Add a new task or item to the currently active screen.
        """

        if screen_name == "Current":
            scroll_view = self.root.ids.current_screen_scroll_view
            container = self.root.ids.current_screen_container
            new_task_node = self.current_task_list.add_node_handler()
            new_task_widget = TaskButton(task_node=new_task_node)
        elif screen_name == "Repeat":
            scroll_view = self.root.ids.repeat_screen_scroll_view
            container = self.root.ids.repeat_screen_container
            new_task_node = self.repeat_task_list.add_node_handler()
            new_task_node.start_date += timedelta(days=1)
            new_task_widget = TaskButton(task_node=new_task_node)
        elif screen_name == "List":
            scroll_view = self.root.ids.list_screen_scroll_view
            container = self.root.ids.list_screen_container
            new_item_node = self.item_list.add_node_handler()
            new_task_widget = ItemButton(item_node=new_item_node)

        self.unedited_new_widget = new_task_widget
        Clock.schedule_once(lambda dt: container.add_widget(new_task_widget), 0.2)
        if container.height > scroll_view.height * 0.9:
            scroll_view.scroll_to(new_task_widget)
        if screen_name == "Current" or screen_name == "Repeat":
            self.display_task_details(new_task_widget)
        elif screen_name == "List":
            self.display_item_details(new_task_widget)

    def get_new_widget(self, screen_name):
        """
        Get a new widget based on the current screen context.
        """

        if screen_name == "Current":
            new_node = self.current_task_list.add_node_handler()
            new_widget = TaskButton(task_node=new_node)
        elif screen_name == "Repeat":
            new_node = self.repeat_task_list.add_node_handler()
            new_widget = TaskButton(task_node=new_node)
        elif screen_name == "List":
            new_node = self.item_list.add_node_handler()
            new_widget = ItemButton(item_node=new_node)

        return (new_widget, new_node)

    def display_task_details(self, selected_task):
        """
        Display details of a selected task in a dialog.
        """
        dialog = TaskDialog(selected_task, selected_task.task_node)
        dialog.open()

    def display_item_details(self, selected_item):
        """
        Display details of a selected item in a dialog.
        """

        dialog = ItemDialog(selected_item, selected_item.item_node)
        dialog.open()

    def update_stats_screen(self):
        """
        Update the stats screen with current statistics.
        """
        self.root.ids.start_level.text = str(self.stats_screen.current_level)
        self.root.ids.next_level.text = str(self.stats_screen.current_level + 1)
        xp_needed = self.stats_screen.next_level - self.stats_screen.current_xp
        self.root.ids.xp_to_next_level.text = f"{xp_needed} xp to next level"

        task_container = self.root.ids.completed_tasks_layout
        task_container.clear_widgets()
        self._add_and_sort_widgets(task_container, self.stats_screen.completed_tasks)

        item_container = self.root.ids.purchased_items_layout
        item_container.clear_widgets()
        self._add_and_sort_widgets(item_container, self.stats_screen.purchased_items)

        # Needs to be scheduled after 'set_current_screen' to avoid issues with initial display.
        Clock.schedule_once(
            lambda dt: self.root.ids.progress_bar.fill_progress_bar(), 0.3
        )

    def _add_and_sort_widgets(self, container, widget_map):
        """
        Helper for 'update_stats_screen' to add and sort widgets in a container.
        """

        widget_values = [(count, task) for task, count in widget_map.items()]
        widget_values.sort(key=lambda x: x[0], reverse=True)

        for count, task in widget_values:
            new_widget = CompletedWidget(task, str(count))
            container.add_widget(new_widget)

    def update_current_screen(self):
        """
        Update the current screen for tasks due today.
        """

        repeat_container = self.root.ids.repeat_screen_container
        current_container = self.root.ids.current_screen_container

        for old_button in repeat_container.children:
            if old_button.task_node.start_date <= date.today():
                new_button = self._copy_old_button(old_button)
                self._delete_old_button(old_button, old_button.task_node)
                current_container.add_widget(new_button)

    def _copy_old_button(self, old_button):
        """
        Helper function for 'update_current_screen' to create a new button for a task due today.
        """

        old_task_node = old_button.task_node
        new_task_node = self.current_task_list.add_node_handler()
        new_task_node.title = old_task_node.title
        new_task_node.first_step = old_task_node.first_step
        new_task_node.second_step = old_task_node.second_step
        new_task_node.third_step = old_task_node.third_step
        new_task_node.repeat_toggle = old_task_node.repeat_toggle
        new_task_node.interval_index = old_task_node.interval_index
        new_task_widget = TaskButton(task_node=new_task_node)

        return new_task_widget

    def _delete_old_button(self, old_button, old_node):
        """
        Helper function for 'update_current_screen' to remove an old task button from the repeat screen.
        """

        linked_list = self.repeat_task_list
        container = self.root.ids.repeat_screen_container
        linked_list.delete_node_handler(old_node.id_num)
        container.remove_widget(old_button)

    def cycle_color_schemes(self):
        color_schemes = [
            "Aliceblue",
            "Antiquewhite",
            "Aqua",
            "Aquamarine",
            "Azure",
            "Beige",
            "Bisque",
            "Black",
            "Blanchedalmond",
            "Blue",
            "Blueviolet",
            "Brown",
            "Burlywood",
            "Cadetblue",
            "Chartreuse",
            "Chocolate",
            "Coral",
            "Cornflowerblue",
            "Cornsilk",
            "Crimson",
            "Cyan",
            "Darkblue",
            "Darkcyan",
            "Darkgoldenrod",
            "Darkgray",
            "Darkgrey",
            "Darkgreen",
            "Darkkhaki",
            "Darkmagenta",
            "Darkolivegreen",
            "Darkorange",
            "Darkorchid",
            "Darkred",
            "Darksalmon",
            "Darkseagreen",
            "Darkslateblue",
            "Darkslategray",
            "Darkslategrey",
            "Darkturquoise",
            "Darkviolet",
            "Deeppink",
            "Deepskyblue",
            "Dimgray",
            "Dimgrey",
            "Dodgerblue",
            "Firebrick",
            "Floralwhite",
            "Forestgreen",
            "Fuchsia",
            "Gainsboro",
            "Ghostwhite",
            "Gold",
            "Goldenrod",
            "Gray",
            "Grey",
            "Green",
            "Greenyellow",
            "Honeydew",
            "Hotpink",
            "Indianred",
            "Indigo",
            "Ivory",
            "Khaki",
            "Lavender",
            "Lavenderblush",
            "Lawngreen",
            "Lemonchiffon",
            "Lightblue",
            "Lightcoral",
            "Lightcyan",
            "Lightgoldenrodyellow",
            "Lightgreen",
            "Lightgray",
            "Lightgrey",
            "Lightpink",
            "Lightsalmon",
            "Lightseagreen",
            "Lightskyblue",
            "Lightslategray",
            "Lightslategrey",
            "Lightsteelblue",
            "Lightyellow",
            "Lime",
            "Limegreen",
            "Linen",
            "Magenta",
            "Maroon",
            "Mediumaquamarine",
            "Mediumblue",
            "Mediumorchid",
            "Mediumpurple",
            "Mediumseagreen",
            "Mediumslateblue",
            "Mediumspringgreen",
            "Mediumturquoise",
            "Mediumvioletred",
            "Midnightblue",
            "Mintcream",
            "Mistyrose",
            "Moccasin",
            "Navajowhite",
            "Navy",
            "Oldlace",
            "Olive",
            "Olivedrab",
            "Orange",
            "Orangered",
            "Orchid",
            "Palegoldenrod",
            "Palegreen",
            "Paleturquoise",
            "Palevioletred",
            "Papayawhip",
            "Peachpuff",
            "Peru",
            "Pink",
            "Plum",
            "Powderblue",
            "Purple",
            "Red",
            "Rosybrown",
            "Royalblue",
            "Saddlebrown",
            "Salmon",
            "Sandybrown",
            "Seagreen",
            "Seashell",
            "Sienna",
            "Silver",
            "Skyblue",
            "Slateblue",
            "Slategray",
            "Slategrey",
            "Snow",
            "Springgreen",
            "Steelblue",
            "Tan",
            "Teal",
            "Thistle",
            "Tomato",
            "Turquoise",
            "Violet",
            "Wheat",
            "White",
            "Whitesmoke",
            "Yellow",
            "Yellowgreen",
        ]
        self.color_index = (self.color_index + 1) % 147
        self.theme_cls.primary_palette = color_schemes[self.color_index]


if __name__ == "__main__":
    MainApp().run()
