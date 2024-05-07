# Standard library imports
from datetime import date

# Third-party library imports
from kivy.metrics import dp
from kivy.uix.screenmanager import NoTransition
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.pickers import MDModalDatePicker
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.textfield import MDTextField
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle


class TaskButton(MDButton):
    """
    Custom button linked to a specific task node.
    """

    def __init__(self, task_node, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_node = task_node
        self.ids.task_button_text.text = self.task_node.title

    def adjust_pos(self, *args) -> None:
        """
        Center text within the button.
        """

        self._button_text.pos_hint = {"center_x": 0.5, "center_y": 0.5}

    def update_text(self):
        """
        Update the text to reflect the current task title.
        """

        self.ids.task_button_text.text = self.task_node.title


class ItemButton(MDButton):
    """
    Custom button linked to a specific item node.
    """

    def __init__(self, item_node, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_node = item_node
        self.ids.item_button_text.text = self.item_node.title

    def adjust_pos(self, *args) -> None:
        """
        Center text within the button.
        """
        self._button_text.pos_hint = {"center_x": 0.5, "center_y": 0.5}

    def update_text(self):
        """
        Update the text to reflect the current task title.
        """
        self.ids.item_button_text.text = self.item_node.title


class TaskDialog(MDDialog):
    """
    Dialog for editing or viewing details of a task.
    """

    def __init__(self, task_button, task_node, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_app = MDApp.get_running_app()
        self.task_button = task_button
        self.task_node = task_node

        self.ids.task_dialog_screen_manager.transition = NoTransition()
        self.ids.task_dialog_screen_manager.current = (
            self.main_app.root.ids.main_screen_manager.current
        )

        self.load_task_details()

    def load_task_details(self):
        """
        Load details into the dialog from the task node.
        """

        self.ids.task_dialog_title.text = self.task_node.title
        self.ids.first_step.text = self.task_node.first_step
        self.ids.second_step.text = self.task_node.second_step
        self.ids.third_step.text = self.task_node.third_step

        if self.task_node.repeat_toggle:
            self.ids.task_dialog_repeat_button.style = "filled"
        else:
            self.ids.task_dialog_repeat_button.style = "outlined"

        if self.ids.task_dialog_screen_manager.current == "Current":
            self.ids.current_screen_repeat_interval_text.text = (
                self.task_node.interval_text[self.task_node.interval_index]
            )
        elif self.ids.task_dialog_screen_manager.current == "Repeat":
            self.ids.repeat_screen_repeat_interval_text.text = str(
                self.task_node.start_date
            )

    def on_pre_dismiss(self) -> None:
        """
        Deletes current instance if it is an unedited new task.
        """
        if (
            self.ids.task_dialog_title.error
            and self.task_button == self.main_app.unedited_new_widget
        ):
            self.ids.task_dialog_title.error = False
            screen_title = self.main_app.root.ids.main_screen_manager.current
            self.delete_task(screen_title)

    def dismiss(self, *args) -> None:
        """
        Handle dialog dismissal with additional validation checks.
        """

        if self.ids.task_dialog_title.error and not self.main_app.unedited_new_widget:
            self.display_dialog_error()
            return False
        return super().dismiss(*args)

    def on_dismiss(self):
        """
        Updates the task node and button with the new details when dismissed.
        """

        super().on_dismiss()
        self.main_app.unedited_new_widget = None
        self.task_node.title = self.ids.task_dialog_title.text
        self.task_node.first_step = self.ids.first_step.text
        self.task_node.second_step = self.ids.second_step.text
        self.task_node.third_step = self.ids.third_step.text
        self.task_button.update_text()

    def display_dialog_error(self):
        """
        Show an error message if the dialog is dismissed with invalid inputs.
        """

        MDSnackbar(MDSnackbarText(text="Error: A title is mandatory!")).open()

    def delete_task(self, screen_title, skip_dialog=False):
        """
        Delete task with the option to keep/delete rescheduled task if not unedited new task.
        """

        if self.task_button == self.main_app.unedited_new_widget:
            self.main_app.unedited_new_widget = None
        elif (
            self.task_node.repeat_toggle
            and not skip_dialog
            and not screen_title == "Repeat"
        ):
            delete_dialog = DeleteRepeatTaskDialog(self.task_button, self.task_node)
            delete_dialog.open()
            self.dismiss()
            return

        if screen_title == "Current":
            linked_list = self.main_app.current_task_list
            container = self.main_app.root.ids.current_screen_container
        elif screen_title == "Repeat":
            linked_list = self.main_app.repeat_task_list
            container = self.main_app.root.ids.repeat_screen_container

        linked_list.delete_node_handler(self.task_node.id_num)
        container.remove_widget(self.task_button)

        self.dismiss()

    def repeat_button_toggle(self, repeat_button):
        """
        Toggle the repeat state of the task and update the button style.
        """

        self.task_node.repeat_toggle = not self.task_node.repeat_toggle
        repeat_button.style = "filled" if self.task_node.repeat_toggle else "outlined"

    def cycle_interval(self, button_text):
        """
        Cycle through predefined intervals for repeating tasks.
        """

        self.task_node.interval_index = (self.task_node.interval_index + 1) % 4
        button_text.text = self.task_node.interval_text[self.task_node.interval_index]

    def open_date_picker(self):
        """
        Open date picker with only a select range of dates available. Current date is focused.
        """

        desired_year = self.task_node.start_date.year
        desired_month = self.task_node.start_date.month
        desired_day = self.task_node.start_date.day
        button = self.ids.repeat_screen_repeat_interval_text
        min_date = date.today()
        max_date = date(
            year=date.today().year + 1, month=date.today().month, day=date.today().day
        )

        date_dialog = FutureDatePicker(
            button=button,
            task_node=self.task_node,
            year=desired_year,
            month=desired_month,
            day=desired_day,
            min_date=min_date,
            max_date=max_date,
        )

        date_dialog.open()

    def complete_task(self):
        """
        Completes task and updates stats screen. Schedules future task if repeat is toggled.
        """

        if self.ids.task_dialog_title.error:
            self.display_dialog_error()
            return

        task_text = self.ids.task_dialog_title.text
        self.main_app.stats_screen.completed_task_handler(task_text)
        self.main_app.autocomplete.insert(task_text)
        self.dismiss()

        if not self.task_node.repeat_toggle:
            self.delete_task("Current")
            return

        container = self.main_app.root.ids.repeat_screen_container
        new_task_node = self.main_app.repeat_task_list.add_node_handler()
        self.task_node.clone_self(new_task_node)
        new_task_node.advance_start_date()
        new_task_widget = TaskButton(task_node=new_task_node)
        container.add_widget(new_task_widget)

        self.delete_task("Current", True)


class DialogTextField(MDTextField):
    """
    A custom text field for dialogues with several restrictions.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_app = MDApp.get_running_app()

    def insert_text(self, substring, from_undo=False):
        """
        Delete selection if one exists. Insert lowercase text into field if it fits within the designated width. Function are from Kivy source code.
        """

        self.delete_selection()
        current_width = self._get_text_width(
            self._lines[0], self.tab_width, self._label_cached
        )
        substring_width = self._get_text_width(
            substring, self.tab_width, self._label_cached
        )
        if current_width + substring_width >= dp(243):
            substring = ""
        substring = substring.lower()

        super().insert_text(substring, from_undo=from_undo)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """
        Handle key down events, specifically intercepting the tab key.
        """

        if keycode[1] == "tab":
            return True

        return super().keyboard_on_key_down(window, keycode, text, modifiers)


class DialogTextFieldAutocomplete(MDTextField):
    """
    A custom text field for dialogues with several restrictions and autocomplete capabilities.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_app = MDApp.get_running_app()

    def insert_text(self, substring, from_undo=False):
        """
        Delete selection if one exists. Insert lowercase text into field if it fits within the designated width. Adds suffix if applicable. Function are from Kivy source code.
        """

        self.delete_selection()
        current_width = self._get_text_width(
            self._lines[0], self.tab_width, self._label_cached
        )
        substring_width = self._get_text_width(
            substring, self.tab_width, self._label_cached
        )
        if current_width + substring_width >= dp(243):
            substring = ""
        substring = substring.lower()

        super().insert_text(substring, from_undo=from_undo)

        suffix = self.main_app.autocomplete.get_suffix(self.text)
        if suffix:
            index = self.cursor_index()
            end_index = index + len(suffix)
            self.text = self.text[:index] + suffix
            self.select_text(index, end_index)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """
        Handle key down events, specifically intercepting the tab key.
        """

        if keycode[1] == "tab":
            return True

        return super().keyboard_on_key_down(window, keycode, text, modifiers)


class DialogNumberField(MDTextField):
    """
    A custom text field that only accepts numerical input including a single decimal point.
    It restricts input to digits and a single decimal, and ensures the text fits within a defined width.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the dialog number field with a flag to track the presence of a decimal point.
        """

        super().__init__(*args, **kwargs)
        self.has_decimal = False

    def insert_text(self, substring, from_undo=False):
        """
        Insert text into the field, only allowing numeric characters and a single decimal point.
        Ensures that the text does not exceed the maximum allowed width.
        """

        if not (substring.isdigit() or (substring == "." and not self.has_decimal)):
            substring = ""

        if substring == ".":
            self.has_decimal = True

        current_width = self._get_text_width(
            self._lines[0], self.tab_width, self._label_cached
        )
        substring_width = self._get_text_width(
            substring, self.tab_width, self._label_cached
        )
        if current_width + substring_width >= dp(123):
            substring = ""

        super().insert_text(substring, from_undo=from_undo)

    def do_backspace(self, from_undo=False, mode="bkspc"):
        """
        Handles the backspace operation, adjusting the decimal point tracking flag as necessary.
        """

        super().do_backspace(from_undo=from_undo, mode=mode)
        self.has_decimal = "." in self.text


class DialogButtonSmall(MDButton):
    """
    Small button to control primary dialog functions.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def adjust_pos(self, *args) -> None:
        self._button_text.pos_hint = {"center_x": 0.5, "center_y": 0.5}

    def adjust_width(self, *args) -> None:
        self.width = dp(95)


class DialogButtonLarge(MDButton):
    """
    Large button to control primary dialog functions.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def adjust_pos(self, *args) -> None:
        self._button_text.pos_hint = {"center_x": 0.5, "center_y": 0.5}

    def adjust_width(self, *args) -> None:
        self.width = dp(274)


class FutureDatePicker(MDModalDatePicker):
    """
    Dialog that allows user to select specific date for task. Two unneeded buttons were removed from the default MDModalDatePicker class.
    """

    def __init__(
        self,
        button,
        task_node,
        year=None,
        month=None,
        day=None,
        firstweekday=0,
        **kwargs,
    ):
        super().__init__(year, month, day, firstweekday, **kwargs)
        self.button = button
        self.task_node = task_node
        self.mark_today = False

        parent = self.children[4]
        on_edit_button = parent.children[0]
        parent.remove_widget(on_edit_button)

        parent = self.children[2]
        select_year_button = parent.children[3]
        parent.remove_widget(select_year_button)

    def on_ok(self, *args):
        """
        Updates button and task node with currently selected date
        """

        self.task_node.start_date = self.get_date()[0]
        self.button.text = str(self.task_node.start_date)
        self.dismiss()

    def on_cancel(self, *args):
        self.dismiss()


class DeleteRepeatTaskDialog(MDDialog):
    """
    Dialog that launches when a task set to repeat is being deleted.
    """

    def __init__(self, task_button, task_node, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_app = MDApp.get_running_app()
        self.task_button = task_button
        self.task_node = task_node
        self.screen_name = self.main_app.root.ids.main_screen_manager.current

    def schedule_repeat_task(self):
        """
        Schedules next occurrence of task when user presses 'Keep.'
        """

        container = self.main_app.root.ids.repeat_screen_container
        new_task_node = self.main_app.repeat_task_list.add_node_handler()
        self.task_node.clone_self(new_task_node)
        new_task_node.advance_start_date()
        new_task_widget = TaskButton(task_node=new_task_node)
        container.add_widget(new_task_widget)

        self.delete_selected_task()

    def delete_selected_task(self):
        """
        Deletes selected task from display and data structure.
        """

        if self.task_button == self.main_app.unedited_new_widget:
            self.main_app.unedited_new_widget = None

        linked_list = self.main_app.current_task_list
        container = self.main_app.root.ids.current_screen_container
        linked_list.delete_node_handler(self.task_button.task_node.id_num)
        container.remove_widget(self.task_button)

        self.dismiss()


class ItemDialog(MDDialog):
    """
    A dialog for displaying and editing the details of an item node.
    """

    def __init__(self, item_button, item_node, *args, **kwargs):
        """
        Initialize the dialog with item details.
        """

        super().__init__(*args, **kwargs)
        self.main_app = MDApp.get_running_app()
        self.item_button = item_button
        self.item_node = item_node

        self.load_task_details()

    def load_task_details(self):
        """
        Load and display the details of the item from the item node.
        """

        self.ids.item_dialog_title.text = self.item_node.title
        self.ids.item_dialog_location.text = self.item_node.item_location
        self.ids.item_dialog_quantity.text = (
            str(self.item_node.quantity) if self.item_node.quantity else ""
        )

        self.ids.item_dialog_units_text.text = self.item_node.interval_text[
            self.item_node.interval_index
        ]

    def on_pre_dismiss(self) -> None:
        """
        Handle the dialog's pre-dismiss event, including the deletion of a task if necessary.
        """

        if (
            self.ids.item_dialog_title.error
            and self.item_button == self.main_app.unedited_new_widget
        ):
            self.ids.item_dialog_title.error = False
            self.delete_task()

    def on_dismiss(self):
        """
        Handle the dialog's dismiss event, updating the item node with new data.
        """

        self.main_app.unedited_new_widget = None

        self.item_node.title = self.ids.item_dialog_title.text
        self.item_node.item_location = self.ids.item_dialog_location.text
        self.item_node.quantity = (
            int(self.ids.item_dialog_quantity.text)
            if self.ids.item_dialog_quantity.text
            else None
        )

        self.item_button.update_text()

        super().on_dismiss()

    def dismiss(self, *args) -> None:
        """
        Attempt to dismiss the dialog and display an error if there are validation issues.
        """

        if self.ids.item_dialog_title.error and not self.main_app.unedited_new_widget:
            self.display_dialog_error()
            return False

        return super().dismiss(*args)

    def display_dialog_error(self):
        """
        Display a snackbar with an error message when there are dialog validation errors.
        """

        MDSnackbar(MDSnackbarText(text="Error: Task details are incorrect!")).open()

    def delete_task(self):
        """
        Delete the current task and remove its widget from the list.
        """

        if self.item_button == self.main_app.unedited_new_widget:
            self.main_app.unedited_new_widget = None

        linked_list = self.main_app.item_list
        container = self.main_app.root.ids.list_screen_container

        linked_list.delete_node_handler(self.item_node.id_num)
        container.remove_widget(self.item_button)

        self.dismiss()

    def complete_task(self):
        """
        Mark the task as completed, update stats, and handle auto-complete entries.
        """

        title_text = self.ids.item_dialog_title.text
        location_text = self.ids.item_dialog_location.text
        self.main_app.stats_screen.purchased_item_handler(title_text, location_text)
        self.main_app.autocomplete.insert(title_text)
        self.main_app.autocomplete.insert(location_text)

        self.delete_task()

    def cycle_unit(self, unit_text):
        """
        Cycle through the intervals and update the interval button's display text.
        """

        self.item_node.interval_index = (self.item_node.interval_index + 1) % 6
        unit_text.text = self.item_node.interval_text[self.item_node.interval_index]
        unit_text.pos_hint = {"center_x": 0.5, "center_y": 0.5}


class CompletedWidget(MDBoxLayout):
    """
    Widget that is added dynamically to the scroll view containers on the stats screen.
    """

    def __init__(self, task_name, task_count, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_name = task_name
        self.task_count = task_count

        self.ids.completed_task_name.text = self.task_name
        self.ids.completed_task_count.text = self.task_count


class ProgressBarWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_app = MDApp.get_running_app()

    def fill_progress_bar(self):
        self.canvas.clear()

        progress_percentage = (
            self.main_app.stats_screen.current_xp
            - self.main_app.stats_screen.start_level
        ) / (
            self.main_app.stats_screen.next_level
            - self.main_app.stats_screen.start_level
        )

        progress_width = progress_percentage * (self.width - dp(4))
        progress_height = self.height - dp(4)
        progress_pos = self.x + dp(2), self.y + dp(2)

        self.canvas.add(Color(self.main_app.theme_cls.onSurfaceColor))
        self.canvas.add(
            RoundedRectangle(
                size=(progress_width, progress_height),
                pos=progress_pos,
                radius=[dp(3), dp(0), dp(0), dp(3)],
            ),
        )
