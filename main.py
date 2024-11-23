import tkinter as tk
from tkinter import messagebox


class Task:
    """
    Represents a task in the Kanban board.
    """
    def __init__(self, title: str, description: str, assigned_user: str = None):
        self.title = title
        self.description = description
        self.status = "To Do"  # Default status for all tasks
        self.assigned_user = assigned_user

    def __str__(self):
        return f"{self.title} - {self.description}"


class Column:
    """
    Represents a column in the Kanban board.
    """
    def __init__(self, name: str):
        self.name = name
        self.tasks = []

    def add_task(self, task: Task):
        self.tasks.append(task)

    def remove_task(self, task_title: str) -> Task:
        for task in self.tasks:
            if task.title == task_title:
                self.tasks.remove(task)
                return task
        return None


class Board:
    """
    Represents the Kanban board.
    """
    def __init__(self):
        self.columns = {
            "To Do": Column("To Do"),
            "In Progress": Column("In Progress"),
            "Done": Column("Done")
        }

    def add_task(self, task: Task):
        self.columns["To Do"].add_task(task)

    def move_task(self, task_title: str, from_column: str, to_column: str) -> bool:
        if from_column in self.columns and to_column in self.columns:
            task_to_move = self.columns[from_column].remove_task(task_title)
            if task_to_move:
                task_to_move.status = to_column
                self.columns[to_column].add_task(task_to_move)
                return True
        return False


class KanbanApp:
    """
    Main application with Tkinter UI.
    """
    def __init__(self):
        self.board = Board()
        self.root = tk.Tk()
        self.root.title("Kanban Board")

        self.setup_ui()

    def setup_ui(self):
        """
        Sets up the main UI components.
        """
        # Top frame for task addition
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(top_frame, text="Title:").pack(side=tk.LEFT)
        self.title_entry = tk.Entry(top_frame, width=20)
        self.title_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(top_frame, text="Description:").pack(side=tk.LEFT)
        self.description_entry = tk.Entry(top_frame, width=30)
        self.description_entry.pack(side=tk.LEFT, padx=5)

        add_task_button = tk.Button(top_frame, text="Add Task", command=self.add_task)
        add_task_button.pack(side=tk.LEFT, padx=5)

        # Board frame for Kanban columns
        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.column_frames = {}
        for column_name in self.board.columns:
            frame = tk.Frame(self.board_frame, relief=tk.RAISED, borderwidth=2)
            frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.column_frames[column_name] = frame
            self.update_column_ui(column_name)

    def update_column_ui(self, column_name: str):
        """
        Updates the UI for a specific column.
        """
        column_frame = self.column_frames[column_name]
        for widget in column_frame.winfo_children():
            widget.destroy()  # Clear existing widgets

        # Column title
        tk.Label(column_frame, text=column_name, font=("Arial", 14, "bold")).pack(pady=5)

        # Task list
        for task in self.board.columns[column_name].tasks:
            task_frame = tk.Frame(column_frame, relief=tk.SUNKEN, borderwidth=1)
            task_frame.pack(fill=tk.X, padx=5, pady=2)

            tk.Label(task_frame, text=str(task)).pack(side=tk.LEFT, padx=5)
            if column_name != "Done":
                next_column = "In Progress" if column_name == "To Do" else "Done"
                move_button = tk.Button(task_frame, text=f"Move to {next_column}",
                                        command=lambda t=task.title, c=column_name, n=next_column: self.move_task(t, c, n))
                move_button.pack(side=tk.RIGHT, padx=5)

    def add_task(self):
        """
        Adds a new task to the 'To Do' column.
        """
        title = self.title_entry.get().strip()
        description = self.description_entry.get().strip()

        if not title:
            messagebox.showerror("Error", "Title is required!")
            return

        new_task = Task(title, description)
        self.board.add_task(new_task)
        self.update_column_ui("To Do")

        # Clear inputs
        self.title_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)

    def move_task(self, task_title: str, from_column: str, to_column: str):
        """
        Moves a task between columns and updates the UI.
        """
        if self.board.move_task(task_title, from_column, to_column):
            self.update_column_ui(from_column)
            self.update_column_ui(to_column)
        else:
            messagebox.showerror("Error", f"Failed to move task '{task_title}'.")

    def run(self):
        """
        Runs the Tkinter main loop.
        """
        self.root.mainloop()


# To run the application (uncomment below line when running in a local Python environment)
app = KanbanApp()
app.run()
