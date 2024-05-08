# ToDoApp
A task management app built with Python and Kivy that features both a to-do list and a shopping list. Tasks are dynamically created and stored in two lists: one for currently active tasks and another for tasks scheduled for future dates. Tasks can be set to repeat, automatically generating the next instance based on the selected time interval. All completed tasks and purchased items are stored on a stats screen, which shows their frequency and includes an experience bar to measure progression.

# Project Goals
These were the initial goals of the project set at its inception:
* Create a usable app with a GUI framework.
* Gain comfort exploring GUI documentation and source code.
* Utilize common data structures and algorithms:
  * Linked list
  * Trie (prefix tree)
  * Merge sort
* Learn the basics of SQL databases.
* Gain comfort using GitHub and Git commands.

# Lessons Learned
While the initial goals of the project did not change, the app's implementation needs some revision. In retrospect, I should have spent more time in the pseudocode stage, diagramming and establishing relationships between sections of code to reduce redundancies and the need for refactoring. Additionally, the idea of implementing a linked list in tandem with a dictionary lookup needs revisiting. The initial concept was to use additional memory to enable O(1) access, insertion, and deletion to implement a drag-and-drop feature for task buttons. However, as I developed the app, I realized this feature was not essential, and the function was scrapped. In the future, the linked lists will likely be removed in favor of dynamically updating the SQL database.

While the KivyMD framework was useful, as I learned more about it and wanted greater control over the widget settings, I encountered roadblocks or bugs that limited the code I could implement. If I continue to use this framework in future projects, I'd like to spend time developing my own widgets directly from the Kivy framework to gain more control over aesthetic elements.

# Future Goals
* Redesign the UI to simplify app navigation and make the aesthetics more unique.
* Consider renaming all 'Repeat' elements to 'Future' or another, more accurate descriptor.
* Refactor the TaskDialog widget UI to remove the need for individual screens for current and repeat tasks.
* Replace the linked lists with direct updates to the SQL database.
* Separate the auto-complete function into distinct tries for specific text dialog inputs.
