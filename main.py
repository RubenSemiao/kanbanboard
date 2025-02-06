import tkinter as tk
from tkinter import ttk, messagebox, font, Text, Menu
import json
from ttkthemes import ThemedTk
from tkcalendar import DateEntry # Biblioteca para calendário
from datetime import datetime # Biblioteca para data e hora
from plyer import notification # Biblioteca para notificações

class Task:
    """
    Represents a task in the Kanban board.
    """
    def __init__(self, title: str, description: str, priority: str = "Médio", deadline: str = None):
        self.title = title
        self.description = description
        self.status = "Para fazer"
        self.priority = priority
        self.deadline = deadline

    def __str__(self):
        deadline_info = f" (Deadline: {self.deadline})" if self.deadline else ""
        return f"{self.title} - {self.description} [Priority: {self.priority}]{deadline_info}"

    def to_dict(self):
        return {
            "Titulo": self.title,
            "Descrição": self.description,
            "Estado": self.status,
            "Prioridade": self.priority,
            "deadline": datetime.strptime(self.deadline, "%m/%d/%y").strftime("%m/%d/%y") if self.deadline else None
        }

    @staticmethod
    def from_dict(data):
        return Task(data["Titulo"], data["Descrição"], data["Prioridade"], data.get("deadline"))
    
    def get_deadline_date(self):
        """
        Converte a string 'deadline' para um objeto datetime.date.
        Retorna None se a conversão falhar.
        """
        if not self.deadline:
            return None
        try:
            return datetime.strptime(self.deadline, "%m/%d/%y").date()  # ✅ Corrige o erro de conversão
        except ValueError:
            print(f"⚠️ Erro ao processar a data da tarefa '{self.title}': {self.deadline}")
            return None

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
            "Para fazer": Column("Para fazer"),
            "Em Progresso": Column("Em Progresso"),
            "Completo": Column("Completo"),
            "Arquivado": Column("Arquivado")
        }

    def add_task(self, task: Task):
        self.columns["Para fazer"].add_task(task)

    def move_task(self, task_title: str, from_column: str, to_column: str) -> bool:
        if from_column in self.columns and to_column in self.columns:
            task_to_move = self.columns[from_column].remove_task(task_title)
            if task_to_move:
                task_to_move.status = to_column
                self.columns[to_column].add_task(task_to_move)
                return True
        return False

        print(f"Erro: Uma das colunas '{from_column}' ou '{to_column}' não existe.")
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

class TaskAlert: # Nova tarefa para alerta de prazo
    """
    Represents a task alert.
    """
    def __init__(self, board, days_before_alert=10): # Adiciona um novo parâmetro para definir os dias antes do alerta
        self.board = board
        self.days_before_alert = days_before_alert
    
    def load_tasks_from_json(self):
        """
        Lê o JSON e retorna uma lista de tarefas que possuem deadline.
        """
        try:
            with open("kanban_board.json", "r") as file:
                data = json.load(file)
                tasks_with_deadline = []

                for column_tasks in data.values():  # Itera diretamente sobre os valores do JSON
                    for task_data in column_tasks:
                        task = Task.from_dict(task_data)
                        if task.deadline:  # Só adiciona tarefas com prazo
                            tasks_with_deadline.append(task)

                return tasks_with_deadline  # ✅ Retorna apenas as tarefas relevantes
        except FileNotFoundError:
            print("⚠️ Arquivo JSON não encontrado.")
            return []
        except Exception as e:
            print(f"❌ Erro ao carregar tarefas do JSON: {e}")
            return []

    def check_deadlines(self):
        """
        Percorre todas as tarefas do quadro e verifica se alguma está próxima do prazo definido.
        """
        today = datetime.today().date()  # ✅ Converte para 'date' corretamente
        tasks_with_deadline = self.load_tasks_from_json()  # ✅ Carrega direto do JSON

        for task in tasks_with_deadline:
            deadline_date = task.get_deadline_date()  # ✅ Método que converte a string

            if deadline_date:
                days_remaining = (deadline_date - today).days

                print(f"🔍 Verificando: {task.title} (Prazo: {task.deadline}, Restam: {days_remaining} dias)")

                if 0 <= days_remaining <= self.days_before_alert:
                    print(f"🚨 ALERTA: '{task.title}' está prestes a vencer!")
                    self.show_alert(task.title, days_remaining)

    def show_alert(self, task_title, days_remaining):
        """
        Exibe um alerta informando quantos dias faltam para o prazo da tarefa.
        """
        message = f"A tarefa '{task_title}' está prestes a vencer! Faltam {days_remaining} dia(s)."

        print(f"🔔 Tentando exibir notificação: {task_title} ({days_remaining} dias restantes)")

        # Notificação nativa do Windows
        try:
            notification.notify(
                title="Alerta de Prazo",
                message=message,
                app_name="Kanban Board",
                timeout=10  # Duração da notificação em segundos
            )
            print("✅ Notificação enviada com sucesso.")
        except Exception as e:
            print(f"❌ Erro ao exibir notificação: {e}")
            messagebox.showwarning("Alerta de Prazo", message)
        
class ui:
    def setup_ui(self):
        """
        Sets up the main UI components.
        """
        # 
        top_frame = ttk.Frame(self.root)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

        button_frame = ttk.Frame(top_frame)
        button_frame.grid(row=1, column=0, sticky="ew", columnspan=10, pady=10)

        button_frame.columnconfigure((0, 1, 2), weight=1)

        buttons = [
            ("Adicionar tarefa", self.add_task),
            ("Carregar quadro", self.load_board)
        ]

        for i, (text, command) in enumerate(buttons):
            ttk.Button(button_frame, text=text, command=command).grid(row=0, column=i, padx=5, pady=5)

        # Mostrar data e hora
        current_date = datetime.now().strftime("%d/%m/%Y")
        ttk.Label(top_frame, text=f"Data: \n{current_date}", font=("Arial", 12, "bold"), foreground="#4A4A4A").grid(row=1, column=10, padx=10, sticky="e")
        
        
        # Frame para os quadros
        self.board_frame = ttk.Frame(self.root)
        self.board_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.board_frame.columnconfigure((0, 1, 2, 3), weight=1)

        self.column_frames = {}

        for column_name in self.board.columns:
            frame = ttk.Frame(self.board_frame, relief=tk.RIDGE, borderwidth=0)
            frame.column_name = column_name  # Define explicitamente a propriedade column_name
            self.column_frames[column_name] = frame


        for i, (column_name, frame) in enumerate(self.column_frames.items()):
            frame.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)
            for column_name, frame in self.column_frames.items():
                frame.column_name = column_name  # Atribui o nome da coluna ao frame          
            
                self.update_column_ui(column_name)

        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(5, weight=1)
         
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
            task_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            title_label = ttk.Label(task_widget, text=task.title, font=("Helvetica", 14, "bold"), foreground="#333333")
            title_label.pack(anchor="w")
            
            desc_label = ttk.Label(task_widget, text=task.description, font=("Helvetica", 10), foreground="#555555", wraplength=250, justify="left")
            desc_label.pack(anchor="w", pady=(0, 5))

            for label in [title_label, desc_label]:
                label.bind("<ButtonPress-1>", lambda event, t=task, w=task_widget, c=column_name: self.start_drag(event, t, w, c))
                label.bind("<B1-Motion>", self.drag_motion)
                label.bind("<ButtonRelease-1>", self.drop_task)

          
            priority_color = "#FF0000" if task.priority == "Alta" else "#b3b300" if task.priority == "Médio" else "#FFEA00" if task.priority == "Baixo" else "#008000"
            ttk.Label(task_widget, text=f"Prioridade: {task.priority}", font=("Helvetica", 9, "italic"), foreground=priority_color).pack(anchor="w")

            if task.deadline:
                ttk.Label(task_widget, text=f"Deadline: {task.deadline}", font=("Helvetica", 9, "italic"), foreground="#777777").pack(anchor="w")

            task_widget.bind("<ButtonPress-1>", lambda event, t=task, w=task_widget, c=column_name: self.start_drag(event, t, w, c))
            task_widget.bind("<B1-Motion>", self.drag_motion)
            task_widget.bind("<ButtonRelease-1>", self.drop_task)
            task_widget.bind("<Double-Button-1>", lambda event, t=task: self.edit_task_window(t))
            task_widget.bind("<Button-3>", lambda event, t=task: self.show_context_menu(event, t))
            

    def add_task(self):
        """
        Adds a new task to the 'Para fazer' column.
        """
        
        def newWindow():
            """
            Cria uma nova janela para entrada de dados da tarefa.
            """
            window = tk.Toplevel(self.root)  # Cria uma nova janela secundária
            window.title("Nova Tarefa")
            window.geometry("500x500")

            ttk.Label(window, text="Título:").pack(pady=5)
            title_entry = ttk.Entry(window)
            title_entry.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)

            ttk.Label(window, text="Descrição:").pack(pady=5)
            description_text = Text(window, wrap=tk.WORD, height=5)
            description_text.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)

            ttk.Label(window, text="Prioridade:").pack(pady=5)
            priority_combobox = ttk.Combobox(window, values=["Baixo", "Médio", "Alta"], width=10)
            priority_combobox.set("Médio")
            priority_combobox.pack(pady=5)

            ttk.Label(window, text="Deadline:").pack(pady=5)
            deadline = DateEntry(window, width=20, background="blue", foreground="white", borderwidth=2)
            deadline.pack(pady=15)

            def save_task():
                """
                Salva a nova tarefa ao quadro.
                """
                title = title_entry.get().strip()
                description = description_text.get("1.0", tk.END).strip()
                priority = priority_combobox.get()
                deadline_date = deadline.get()

                if not title:
                    messagebox.showinfo("Campo em falta", "O título não foi introduzido.")
                    return

                new_task = Task(title, description, priority, deadline_date)
                self.board.add_task(new_task)
                self.update_column_ui("Para fazer")
                self.auto_save_board()

                # Fecha a janela após salvar a tarefa
                window.destroy()

            # Botão para salvar a tarefa
            ttk.Button(window, text="Salvar Tarefa", command=save_task).pack(pady=20)

        newWindow()

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
        edit_window.title("Editar Tarefa")
        edit_window.geometry("500x500")

        ttk.Label(edit_window, text="Título:").pack(pady=5)
        title_entry = ttk.Entry(edit_window)
        title_entry.pack(fill=tk.X, padx=10)
        title_entry.insert(0, task.title)

        ttk.Label(edit_window, text="Descrição:").pack(pady=5)
        description_text = Text(edit_window, wrap=tk.WORD, height=10)
        description_text.pack(fill=tk.BOTH, padx=10, pady=5)
        description_text.insert(1.0, task.description)

        ttk.Label(edit_window, text="Prioridade:").pack(pady=5)
        priority_combobox = ttk.Combobox(edit_window, values=["Baixo", "Médio", "Alta"])
        priority_combobox.pack(padx=10)
        priority_combobox.set(task.priority)

        ttk.Label(edit_window, text="Deadline:").pack(pady=5)
        deadline = DateEntry(edit_window, width=20, background="blue", foreground="white", borderwidth=2)
        deadline.pack(pady=15)

        save_button = ttk.Button(edit_window, text="Salvar Alterações", command=lambda: self.save_task_changes(task, title_entry, description_text, priority_combobox, deadline, edit_window))
        save_button.pack(pady=10)

    def save_task_changes(self, task, title_entry, description_text, priority_combobox, deadline, window):
        """
        Saves changes made to a task.
        """
        task.title = title_entry.get().strip()
        task.description = description_text.get(1.0, tk.END).strip()
        task.priority = priority_combobox.get().strip()
        task.deadline = deadline.get()
        window.destroy()
        self.update_column_ui(task.status)

        # Salvar automaticamente após a alteração da tarefa e reler o quadro
        self.auto_save_board()
        self.load_board()
        self.schedule_alerts()

    def set_task_priority(self, task):
        """
        Opens a dialog to set the priority of a task.
        """
        priority_window = tk.Toplevel(self.root)
        priority_window.title("Definir Prioridade da Tarefa")
        priority_window.geometry("300x150")

        ttk.Label(priority_window, text="Selecionar prioridade:").pack(pady=10)
        priority_combobox = ttk.Combobox(priority_window, values=["Baixa", "Médio", "Alta"])
        priority_combobox.pack(padx=10)
        priority_combobox.set(task.priority)

        set_button = ttk.Button(priority_window, text="Definir", command=lambda: self.save_task_priority(task, priority_combobox, priority_window))
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
        self.load_board()
    
    def set_task_deadline(self, task):
        """
        Edita a janela para definir o prazo da tarefa.
        """
        deadline_window = tk.Toplevel(self.root)
        deadline_window.title("Definir Prazo da Tarefa")
        deadline_window.geometry("300x150")

        ttk.Label(deadline_window, text="Selecionar prazo:").pack(pady=10)
        deadline = DateEntry(deadline_window, width=20, background="blue", foreground="white", borderwidth=2)
        deadline.pack(padx=10)

        set_button = ttk.Button(deadline_window, text="Definir", command=lambda: self.save_task_deadline(task, deadline, deadline_window))
        set_button.pack(pady=10)
    
    def save_task_deadline(self, task, deadline, window):
        """
        Salva o novo prazo para uma tarefa.
        """
        task.deadline = deadline.get()
        window.destroy()
        self.update_column_ui(task.status)

        # Salvar automaticamente após a alteração do prazo
        self.auto_save_board()
        self.load_board()

    def remove_task(self, task):
        """
        Removes a task from the board.
        """
        self.board.columns[task.status].remove_task(task.title)
        self.update_column_ui(task.status)

        # Salvar automaticamente após remover a tarefa
        self.auto_save_board()
    
    def show_context_menu(self, event, task):
        """
        Shows a context menu for the task with options to edit, set priority, or remove.
        """
        context_menu = Menu(self.root, tearoff=0)
        context_menu.add_command(label="Editar", command=lambda: self.edit_task_window(task))
        context_menu.add_command(label="Definir Prioridade", command=lambda: self.set_task_priority(task))
        context_menu.add_command(label="Remover", command=lambda: self.remove_task(task))
        context_menu.add_command(label="Definir Prazo", command=lambda: self.set_task_deadline(task))
        context_menu.post(event.x_root, event.y_root)

    def run(self):
        """
        Runs the Tkinter main loop.
        """
        self.root.mainloop()

class KanbanApp(ui, TaskAlert):
    """
    Main Kanban app.
    """
    def __init__(self):
        self.board = Board()
        self.root = ThemedTk(theme="arc")
        self.root.title("Kanban Board")

        self.root.geometry("1200x800")
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.dragged_task = None
        self.dragged_task_widget = None
        self.from_column = None
        self.clone_widget = None
        self.alert_system = TaskAlert(self.board)

        ui.setup_ui(self)
        ui.load_board(self)  # Load board automatically on startup
        self.schedule_alerts()

    def schedule_alerts(self):
        """
        Schedules task alerts to check for upcoming deadlines.
        """
        print("Checking deadlines...")
        try:
            self.alert_system.check_deadlines()
            print("check_deadlines executed successfully.")
        except Exception as e:
            print(f"Error in check_deadlines: {e}")
        self.root.after(60000, self.schedule_alerts)
    
    def start_drag(self, event, task, task_widget, from_column):
            """
            Inicia o arrasto da tarefa e armazena a referência.
            """

            self.dragged_task = task
            self.dragged_task_widget = event.widget
            self.from_column = from_column  # ✅ Armazena a coluna original

            # Criar um clone da tarefa visualmente
            self.clone_widget = tk.Toplevel(self.root)
            self.clone_widget.overrideredirect(True)  # Remove bordas da janela
            
            # Criar um Frame dentro do clone para parecer uma tarefa real
            clone_frame = ttk.Frame(self.clone_widget, relief=tk.RAISED, padding=5, borderwidth=2)
            clone_frame.pack(fill=tk.BOTH, expand=True)
        
            # Título da tarefa
            ttk.Label(clone_frame, text=task.title, font=("Helvetica", 14, "bold"), foreground="#333333").pack(anchor="w")
        
            # Descrição da tarefa (sem cortes)
            desc_label = ttk.Label(clone_frame, text=task.description, font=("Helvetica", 10), foreground="#555555", wraplength=250, justify="left")
            desc_label.pack(anchor="w", pady=(0, 5))
        
            # Cor da prioridade
            priority_color = "#FF0000" if task.priority == "Alta" else "#b3b300" if task.priority == "Médio" else "#FFEA00" if task.priority == "Baixo" else "#008000"
            ttk.Label(clone_frame, text=f"Prioridade: {task.priority}", font=("Helvetica", 9, "italic"), foreground=priority_color).pack(anchor="w")
        
            if task.deadline:
                ttk.Label(clone_frame, text=f"Deadline: {task.deadline}", font=("Helvetica", 9, "italic"), foreground="#777777").pack(anchor="w")
        
            # Atualizar layout antes de definir a geometria
            self.clone_widget.update_idletasks()
        
            # Definir tamanho dinâmico com base no conteúdo
            width = clone_frame.winfo_reqwidth()
            height = clone_frame.winfo_reqheight()
            self.clone_widget.geometry(f"{width}x{height}+{event.x_root}+{event.y_root}")
        
            # Ligar eventos para mover o clone com o rato
            self.clone_widget.bind("<B1-Motion>", self.drag_motion)

    def drag_motion(self, event):
            """
            Destaca a coluna ao passar sobre ela.
            """
            if self.clone_widget:
            # Sincronizar a posição do clone com o mouse
                width = self.clone_widget.winfo_width()
                height = self.clone_widget.winfo_height()
                self.clone_widget.geometry(f"{width}x{height}+{event.x_root}+{event.y_root}")

    def drop_task(self, event):
        """
        Drops a task into the appropriate column and updates the UI.
        """
        # Detectar qual coluna está sob o cursor
        for column_name, frame in self.column_frames.items():
            if self.is_cursor_in_frame(event, frame):
                to_column = column_name
                break

        if self.dragged_task and to_column:
            # Verificar se a tarefa está sendo movida para uma nova coluna
            if self.from_column and self.from_column != to_column:
                self.board.move_task(self.dragged_task.title, self.from_column, to_column)
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

if __name__ == "__main__":
    app = KanbanApp()
    app.run()
