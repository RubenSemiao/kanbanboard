import tkinter as tk
from tkinter import ttk, messagebox
import json
from ttkthemes import ThemedTk
from tkinter import font, Text, Menu


class Task:
    """
    Represents a task in the Kanban board.
    """
    def __init__(self, title: str, description: str, priority: str = "Medium", deadline: str = None):
        self.title = title
        self.description = description
        self.status = "To Do"
        self.priority = priority
        self.deadline = deadline

    def __str__(self):
        deadline_info = f" (Deadline: {self.deadline})" if self.deadline else ""
        return f"{self.title} - {self.description} [Priority: {self.priority}]{deadline_info}"

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "deadline": self.deadline
        }

    @staticmethod
    def from_dict(data):
        task = Task(data["title"], data["description"], data["priority"], data.get("deadline"))
        task.status = data["status"]
        return task


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

    def to_dict(self):
        return {column_name: [task.to_dict() for task in column.tasks] for column_name, column in self.columns.items()}

    @staticmethod
    def from_dict(data):
        board = Board()
        for column_name, tasks in data.items():
            for task_data in tasks:
                board.columns[column_name].add_task(Task.from_dict(task_data))
        return board


class KanbanApp:
    """
    Main Kanban app.
    """
    def __init__(self):
        self.board = Board()
        self.root = ThemedTk(theme="arc")
        self.root.title("Kanban Board")

        self.root.geometry("900x700")
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.dragged_task = None
        self.dragged_task_widget = None
        self.from_column = None
        self.clone_widget = None

        self.setup_ui()
        self.load_board()  # Load board automatically on startup

    def setup_ui(self):
        """
        Sets up the main UI components.
        """
        # Top Frame for task input
        top_frame = ttk.Frame(self.root)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        top_frame.columnconfigure(1, weight=1)
        top_frame.columnconfigure(3, weight=2)
        top_frame.columnconfigure(5, weight=1)

        ttk.Label(top_frame, text="Title:").grid(row=0, column=0, padx=5, sticky="w")
        self.title_entry = ttk.Entry(top_frame, width=20)
        self.title_entry.grid(row=0, column=1, padx=5, sticky="ew")

        ttk.Label(top_frame, text="Description:").grid(row=0, column=2, padx=5, sticky="w")
        self.description_entry = ttk.Entry(top_frame, width=30)
        self.description_entry.grid(row=0, column=3, padx=5, sticky="ew")

        ttk.Label(top_frame, text="Priority:").grid(row=0, column=4, padx=5, sticky="w")
        self.priority_combobox = ttk.Combobox(top_frame, values=["Low", "Medium", "High"], width=10)
        self.priority_combobox.set("Medium")
        self.priority_combobox.grid(row=0, column=5, padx=5, sticky="w")

        add_task_button = ttk.Button(top_frame, text="Add Task", command=self.add_task)
        add_task_button.grid(row=0, column=6, padx=5, sticky="w")

        save_button = ttk.Button(top_frame, text="Save Board", command=self.save_board)
        save_button.grid(row=0, column=7, padx=5, sticky="w")

        load_button = ttk.Button(top_frame, text="Load Board", command=self.load_board)
        load_button.grid(row=0, column=8, padx=5, sticky="w")

        # Main frame for boards
        self.board_frame = ttk.Frame(self.root)
        self.board_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.board_frame.columnconfigure((0, 1, 2), weight=1)

        self.column_frames = {}
        for i, column_name in enumerate(self.board.columns):
            frame = ttk.Frame(self.board_frame, relief=tk.RIDGE, borderwidth=2)
            frame.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)
            self.column_frames[column_name] = frame

            self.update_column_ui(column_name)

    def update_column_ui(self, column_name: str):
        """
        Updates the UI for a specific column.
        """
        column_frame = self.column_frames[column_name]
        for widget in column_frame.winfo_children():
            widget.destroy()

        ttk.Label(column_frame, text=column_name, font=("Arial", 16, "bold"), foreground="#4A4A4A").pack(pady=10)

        task_container = ttk.Frame(column_frame)
        task_container.pack(fill=tk.BOTH, expand=True)

        for task in self.board.columns[column_name].tasks:
            task_widget = ttk.Frame(task_container, relief=tk.RAISED, padding=5, style="Card.TFrame")
            task_widget.pack(fill=tk.X, padx=5, pady=5)

            task_title = ttk.Label(task_widget, text=task.title, font=("Helvetica", 14, "bold"), foreground="#333333")
            task_title.pack(anchor="w")

            task_description = ttk.Label(task_widget, text=task.description, font=("Helvetica", 10), foreground="#555555")
            task_description.pack(anchor="w", pady=(0, 5))

            priority_color = "#FF0000" if task.priority == "High" else "#b3b300" if task.priority == "Medium" else "#00b300" if task.priority == "Low" else "#008000"
            task_priority = ttk.Label(task_widget, text=f"Priority: {task.priority}", font=("Helvetica", 9, "italic"), foreground=priority_color)
            task_priority.pack(anchor="w")

            if task.deadline:
                task_deadline = ttk.Label(task_widget, text=f"Deadline: {task.deadline}", font=("Helvetica", 9, "italic"), foreground="#777777")
                task_deadline.pack(anchor="w")

            task_widget.bind("<ButtonPress-1>", lambda event, t=task, w=task_widget, c=column_name: self.start_drag(event, t, w, c))
            task_widget.bind("<B1-Motion>", self.drag_motion)
            task_widget.bind("<ButtonRelease-1>", self.drop_task)
            task_widget.bind("<Double-Button-1>", lambda event, t=task: self.edit_task_window(t))
            task_widget.bind("<Button-3>", lambda event, t=task: self.show_context_menu(event, t))



    def start_drag(self, event, task, task_widget, from_column):
        """
        Starts dragging a task.
        """
        self.dragged_task = task
        self.dragged_task_widget = task_widget
        self.from_column = from_column

        # Criar um clone visual para exibir a tarefa durante o arrasto
        self.clone_widget = tk.Label(
            self.root,
            text=task_widget.winfo_children()[0].cget("text"),  # Use the title of the task as clone text
            bg="#e0e0e0",
            relief=tk.RAISED,
            padx=5,
            pady=2,
            font=("Helvetica", 14, "bold")
        )
        self.clone_widget.place(x=event.x_root - self.root.winfo_rootx(), y=event.y_root - self.root.winfo_rooty(), anchor="center")

    def drag_motion(self, event):
        """
        Handles dragging motion by moving the clone widget.
        """
        if self.clone_widget:
            # Sincronizar a posição do clone com o mouse
            self.clone_widget.place(x=event.x_root - self.root.winfo_rootx(), y=event.y_root - self.root.winfo_rooty(), anchor="center")

    def drop_task(self, event):
        """
        Drops a task into the appropriate column and updates the UI.
        """
        to_column = None

        # Detectar qual coluna está sob o cursor
        for column_name, frame in self.column_frames.items():
            if self.is_cursor_in_frame(event, frame):
                to_column = column_name
                break

        if self.dragged_task and to_column:
            # Verificar se a tarefa está sendo movida para uma nova coluna
            if self.from_column != to_column:
                # Atualizar os dados no backend
                self.board.move_task(self.dragged_task.title, self.from_column, to_column)

                # Atualizar a interface gráfica
                self.update_column_ui(self.from_column)
                self.update_column_ui(to_column)

        # Destruir o clone visual
        if self.clone_widget:
            self.clone_widget.destroy()
            self.clone_widget = None

        # Limpar as referências internas
        self.dragged_task = None
        self.dragged_task_widget = None

        # Salvar automaticamente após a alteração
        self.auto_save_board()

    def is_cursor_in_frame(self, event, frame):
        """
        Checks if the cursor is inside the given frame.
        """
        x1, y1, x2, y2 = (frame.winfo_rootx(), frame.winfo_rooty(),
                          frame.winfo_rootx() + frame.winfo_width(),
                          frame.winfo_rooty() + frame.winfo_height())
        return x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2

    def add_task(self):
        """
        Adds a new task to the 'To Do' column.
        """
        title = self.title_entry.get().strip()
        description = self.description_entry.get().strip()
        priority = self.priority_combobox.get()

        if not title:
            messagebox.showerror("Error", "Title is required!")
            return

        new_task = Task(title, description, priority)
        self.board.add_task(new_task)
        self.update_column_ui("To Do")

        self.title_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.priority_combobox.set("Medium")

        # Salvar automaticamente após adicionar a tarefa
        self.auto_save_board()

    def save_board(self):
        """
        Saves the current state of the board to a JSON file.
        """
        try:
            with open("kanban_board.json", "w") as file:
                json.dump(self.board.to_dict(), file, indent=4)
            messagebox.showinfo("Save Board", "Board saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save board: {e}")

    def auto_save_board(self):
        """
        Automatically saves the current state of the board to a JSON file.
        """
        try:
            with open("kanban_board.json", "w") as file:
                json.dump(self.board.to_dict(), file, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to auto-save board: {e}")

    def load_board(self):
        """
        Loads the board state from a JSON file.
        """
        try:
            with open("kanban_board.json", "r") as file:
                data = json.load(file)
                self.board = Board.from_dict(data)
                for column_name in self.board.columns:
                    self.update_column_ui(column_name)
        except FileNotFoundError:
            messagebox.showinfo("Load Board", "No existing board found. A new board will be created.")
            self.board = Board()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load board: {e}")

    def edit_task_window(self, task):
        """
        Opens a window to edit the title, description, and priority of a task.
        """
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Task")
        edit_window.geometry("400x400")

        ttk.Label(edit_window, text="Title:").pack(pady=5)
        title_entry = ttk.Entry(edit_window)
        title_entry.pack(fill=tk.X, padx=10)
        title_entry.insert(0, task.title)

        ttk.Label(edit_window, text="Description:").pack(pady=5)
        description_text = Text(edit_window, wrap=tk.WORD, height=10)
        description_text.pack(fill=tk.BOTH, padx=10, pady=5)
        description_text.insert(1.0, task.description)

        ttk.Label(edit_window, text="Priority:").pack(pady=5)
        priority_combobox = ttk.Combobox(edit_window, values=["Low", "Medium", "High"])
        priority_combobox.pack(padx=10)
        priority_combobox.set(task.priority)

        save_button = ttk.Button(edit_window, text="Save Changes", command=lambda: self.save_task_changes(task, title_entry, description_text, priority_combobox, edit_window))
        save_button.pack(pady=10)

    def save_task_changes(self, task, title_entry, description_text, priority_combobox, window):
        """
        Saves changes made to a task.
        """
        task.title = title_entry.get().strip()
        task.description = description_text.get(1.0, tk.END).strip()
        task.priority = priority_combobox.get().strip()
        window.destroy()
        self.update_column_ui(task.status)

        # Salvar automaticamente após a alteração da tarefa
        self.auto_save_board()

    def show_context_menu(self, event, task):
        """
        Shows a context menu for the task with options to edit, set priority, or remove.
        """
        context_menu = Menu(self.root, tearoff=0)
        context_menu.add_command(label="Edit", command=lambda: self.edit_task_window(task))
        context_menu.add_command(label="Set Priority", command=lambda: self.set_task_priority(task))
        context_menu.add_command(label="Remove", command=lambda: self.remove_task(task))
        context_menu.post(event.x_root, event.y_root)

    def set_task_priority(self, task):
        """
        Opens a dialog to set the priority of a task.
        """
        priority_window = tk.Toplevel(self.root)
        priority_window.title("Set Task Priority")
        priority_window.geometry("300x150")

        ttk.Label(priority_window, text="Select Priority:").pack(pady=10)
        priority_combobox = ttk.Combobox(priority_window, values=["Low", "Medium", "High"])
        priority_combobox.pack(padx=10)
        priority_combobox.set(task.priority)

        set_button = ttk.Button(priority_window, text="Set", command=lambda: self.save_task_priority(task, priority_combobox, priority_window))
        set_button.pack(pady=10)

    def save_task_priority(self, task, priority_combobox, window):
        """
        Saves the new priority for a task.
        """
        task.priority = priority_combobox.get().strip()
        window.destroy()
        self.update_column_ui(task.status)

        # Salvar automaticamente após a alteração da prioridade
        self.auto_save_board()

    def remove_task(self, task):
        """
        Removes a task from the board.
        """
        self.board.columns[task.status].remove_task(task.title)
        self.update_column_ui(task.status)

        # Salvar automaticamente após remover a tarefa
        self.auto_save_board()

    def run(self):
        """
        Runs the Tkinter main loop.
        """
        self.root.mainloop()


if __name__ == "__main__":
    app = KanbanApp()
    app.run()
