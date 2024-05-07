from datetime import date, timedelta


class TaskNode:
    """
    Data structure to maintain the buttons and dialogs on the Current and Repeat screens.
    """

    def __init__(self, id_num: int, previous=None, nxt=None):
        self.id_num = id_num
        self.previous = previous
        self.next = nxt

        self.title = ""
        self.first_step = ""
        self.second_step = ""
        self.third_step = ""
        self.start_date = date.today()
        self.repeat_toggle = False
        self.interval_index = 0
        self.interval_text = ["a day", "a week", "a month", "a year"]

    def clone_self(self, clone):
        """
        Copies all of the current nodes data to a select clone.
        """

        clone.title = self.title
        clone.first_step = self.first_step
        clone.second_step = self.second_step
        clone.third_step = self.third_step
        clone.start_date = self.start_date
        clone.repeat_toggle = self.repeat_toggle
        clone.interval_index = self.interval_index
        clone.interval_text = self.interval_text

    def advance_start_date(self):
        """
        Used to advance a task's date based on the current interval selected.
        """

        if self.interval_index == 0:
            self.start_date += timedelta(days=1)
        elif self.interval_index == 1:
            self.start_date += timedelta(weeks=1)
        elif self.interval_index == 2:
            self.start_date += timedelta(weeks=4)
        else:
            self.start_date += timedelta(weeks=52)


class ItemNode:
    """
    Data structure to maintain the buttons and dialogs on the Item screen.
    """

    def __init__(self, id_num: int, previous=None, nxt=None) -> None:
        self.id_num = id_num
        self.previous = previous
        self.next = nxt
        self.title = ""
        self.quantity = None
        self.item_location = ""
        self.item_price = ""
        self.interval_index = 0
        self.interval_text = [
            "units",
            "ounces",
            "pounds",
            "milligrams",
            "grams",
            "kilograms",
        ]


class LinkedList:
    """
    Data structure to maintain both TaskNode and ItemNode classes. Maintains both a doubly-linked list and a dictionary for O(1) access, insertion, and deletion.
    """

    def __init__(self, list_name: str, list_type: str):
        self.list_name = list_name
        self.list_type = list_type
        self.node_lookup = {}
        self.current_id = 1

        if self.list_type == "Task":
            self.head = TaskNode(-1)
            self.tail = TaskNode(-1)
        elif self.list_type == "Item":
            self.head = ItemNode(-1)
            self.tail = ItemNode(-1)

        self.head.next = self.tail
        self.tail.previous = self.head

    def add_node_handler(self):
        """
        Creates a new node and adds it to the tail of the list.
        """

        if self.list_type == "Task":
            new_task = TaskNode(self.current_id, self.tail.previous, self.tail)
        elif self.list_type == "Item":
            new_task = ItemNode(self.current_id, self.tail.previous, self.tail)

        self.node_lookup[self.current_id] = new_task
        self.current_id += 1

        new_task.previous.next = new_task
        new_task.next.previous = new_task

        return new_task

    def delete_node_handler(self, task_id: int):
        """
        Deletes task from linked list and node_lookup.
        """

        if task_id not in self.node_lookup:
            print("Error: delete_task")
            return

        old_task = self.node_lookup[task_id]
        old_task.previous.next = old_task.next
        old_task.next.previous = old_task.previous

        del old_task
        del self.node_lookup[task_id]

    def remove_node_handler(self, task_id: int):
        """
        Not currently in use. Made in anticipation of a drag-and-drop feature yet to be implemented.
        """

        if task_id not in self.node_lookup:
            print("Error: delete_task")
            return

        old_task = self.node_lookup[task_id]
        old_task.previous.next = old_task.next
        old_task.next.previous = old_task.previous

    def insert_node_handler(self, task_id: int, previous_id: int, next_id: int):
        """
        Not currently in use. Made in anticipation of a drag-and-drop feature yet to be implemented.
        """

        previous_task = self.node_lookup[previous_id]
        task = self.node_lookup[task_id]
        next_task = self.node_lookup[next_id]

        task.previous, task.next = previous_task, next_task
        previous_task.next = next_task.previous = task

    def sort_linked_list(self):
        """
        Merge sort linked lists with the help of several helper functions.
        """

        if self.head.next == self.tail:
            return

        bald_head = self._strip_nodes()
        new_head = self._merge_sort(bald_head)
        new_tail = self._get_tail(new_head)

        new_head.previous, self.head.next = self.head, new_head
        new_tail.next, self.tail.previous = self.tail, new_tail

    def _strip_nodes(self):
        """
        Strips all nodes from the 'head' and 'tail' constants.
        """

        bald_head = self.head.next
        self.head.next = self.tail
        self.tail.previous = self.head

        bald_tail = self._get_tail(bald_head)
        bald_tail.next = None

        return bald_head

    def _merge_sort(self, head):
        """
        Initiates merge sort on stripped linked list.
        """

        if not head or not head.next:
            return head

        middle_node = self._get_middle(head)
        next_node = middle_node.next
        middle_node.next = None

        left_list = self._merge_sort(head)
        right_list = self._merge_sort(next_node)

        return self._merge(left_list, right_list)

    def _merge(self, head_a, head_b):
        """
        Merges list back together based on 'start_date' or 'location' depending on the list.
        """

        if not head_a:
            return head_b
        if not head_b:
            return head_a

        if self.list_type == "Task":
            if head_a.start_date <= head_b.start_date:
                output = head_a
                output.next = self._merge(head_a.next, head_b)
            else:
                output = head_b
                output.next = self._merge(head_a, head_b.next)
        elif self.list_type == "Item":
            if head_a.item_location.lower() <= head_b.item_location.lower():
                output = head_a
                output.next = self._merge(head_a.next, head_b)
            else:
                output = head_b
                output.next = self._merge(head_a, head_b.next)

        return output

    def _get_middle(self, head):
        """
        Finds middle node to evenly split portion of list.
        """

        if not head:
            return head

        slow, fast = head, head.next
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next

        return slow

    def _get_tail(self, node):
        """
        Finds the tail of the current section of the linked list
        """

        while node and node.next and node.next != self.tail:
            node = node.next

        return node


class TrieNode:
    def __init__(self):
        self.children: dict = {}
        self.is_end_of_word: bool = False


class Trie:
    """
    Prefix tree used to generate autocomplete for select text fields.
    """

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        """
        Inserts a word into the trie, converting it to lowercase to ensure case insensitivity.
        """

        current = self.root
        for char in word.lower():
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]
        current.is_end_of_word = True

    def get_suffix(self, prefix: str) -> str:
        """
        Returns the first lexicographical suffix that completes the first found prefix in the trie.
        """

        current = self.root
        for char in prefix:
            if char not in current.children:
                return ""  # Early exit if prefix not found
            current = current.children[char]

        suffix = ""
        while current and not current.is_end_of_word:
            char, current = self.find_first_child(current)
            suffix += char
        return suffix

    def find_first_child(self, node: TrieNode) -> tuple:
        """
        Finds the first child of a given node in lexicographical order.
        """

        if not node.children:
            return ("", None)
        first_char = min(node.children.keys())
        return (first_char, node.children[first_char])


class StatsScreen:
    """
    Maintains data relevant to the Stats screen.
    """

    def __init__(self) -> None:
        self.current_level = 1
        self.current_xp = 0
        self.start_level = 0
        self.next_level = 100

        self.completed_tasks = {}
        self.purchased_items = {}
        self.locations = set()

    def completed_task_handler(self, task):
        """
        Records completed task and adjusts current_xp accordingly.
        """

        self.completed_tasks[task] = self.completed_tasks.get(task, 0) + 1
        xp = 10 + min(10, self.completed_tasks[task])
        self.add_xp(xp)

    def purchased_item_handler(self, item, item_location):
        """
        Records purchased item and adjusts current_xp accordingly.
        """

        self.purchased_items[item] = self.purchased_items.get(item, 0) + 1
        self.locations.add(item_location)
        xp = 10 + min(10, self.purchased_items[item])
        self.add_xp(xp)

    def add_xp(self, xp):
        """
        Adds xp to total and adjusts current_level and next_level accordingly.
        """

        self.current_xp += xp
        if self.current_xp >= self.next_level:
            self.start_level = self.next_level
            self.next_level += 100 + (self.current_level * 10)
            self.current_level += 1
