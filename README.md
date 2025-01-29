# **Kanban Board**

## **Descrição**

Este projeto implementa uma aplicação simples de **Kanban Board** para gerenciamento de tarefas utilizando **Python** e **Tkinter**. A aplicação permite que os usuários organizem tarefas em colunas (*To Do*, *In Progress*, *Done*) de forma interativa, simulando um fluxo típico de trabalho ágil.

A aplicação foi projetada com foco na modularidade e escalabilidade, seguindo boas práticas de programação orientada a objetos (POO). 

---

## **Funcionalidades**

1. **Adicionar Tarefas**:
   - Permite criar uma nova tarefa com título e descrição.
   - A tarefa é automaticamente adicionada à coluna *To Do*.

2. **Mover Tarefas**:
   - Move tarefas entre as colunas:
     - *To Do* → *In Progress*.
     - *In Progress* → *Done*.

3. **Visualizar Tarefas**:
   - Exibe as tarefas organizadas em colunas.
   - Atualiza dinamicamente a interface quando tarefas são adicionadas ou movidas.

4. **Interface Gráfica**:
   - Usa **Tkinter** para criar uma interface interativa.
   - Organiza as colunas lado a lado para simular um quadro Kanban.

---

## **Estrutura do Projeto**

### **1. Classe `Task`**
Representa uma tarefa individual no quadro Kanban.

- **Atributos**:
  - `title` (str): O título da tarefa.
  - `description` (str): Uma breve descrição da tarefa.
  - `status` (str): O status atual da tarefa (*To Do*, *In Progress*, *Done*).
  - `assigned_user` (str): Nome do usuário responsável pela tarefa (opcional).

- **Métodos**:
  - `__init__(title, description, assigned_user=None)`: Inicializa a tarefa com título, descrição e status padrão (*To Do*).
  - `__str__()`: Retorna uma string representando a tarefa.

---

### **2. Classe `Column`**
Representa uma coluna no quadro Kanban, armazenando tarefas relacionadas.

- **Atributos**:
  - `name` (str): O nome da coluna (e.g., *To Do*).
  - `tasks` (list): Lista de objetos `Task` na coluna.

- **Métodos**:
  - `__init__(name)`: Inicializa a coluna com um nome e uma lista vazia de tarefas.
  - `add_task(task)`: Adiciona uma tarefa à coluna.
  - `remove_task(task_title)`: Remove uma tarefa pelo título e retorna o objeto removido.

---

### **3. Classe `Board`**
Gerencia o quadro Kanban completo, com colunas e a lógica de movimentação de tarefas.

- **Atributos**:
  - `columns` (dict): Dicionário de colunas, onde a chave é o nome da coluna (e.g., *To Do*) e o valor é um objeto `Column`.

- **Métodos**:
  - `__init__()`: Inicializa o quadro com três colunas padrão: *To Do*, *In Progress* e *Done*.
  - `add_task(task)`: Adiciona uma nova tarefa à coluna *To Do*.
  - `move_task(task_title, from_column, to_column)`: Move uma tarefa entre colunas.

---

### **4. Classe `KanbanApp`**
Interface gráfica da aplicação, conectando o backend (lógica do quadro Kanban) ao Tkinter.

- **Atributos**:
  - `board` (Board): O quadro Kanban gerenciado pela aplicação.
  - `root` (Tk): Janela principal do Tkinter.
  - `column_frames` (dict): Mapeia os nomes das colunas aos seus frames na interface gráfica.

- **Métodos**:
  - `__init__()`: Inicializa o quadro Kanban e configura a interface gráfica.
  - `setup_ui()`: Configura a interface gráfica com campos de entrada, botões e colunas.
  - `update_column_ui(column_name)`: Atualiza dinamicamente a interface de uma coluna específica.
  - `add_task()`: Lê os dados do usuário e adiciona uma nova tarefa ao quadro.
  - `move_task(task_title, from_column, to_column)`: Move uma tarefa entre colunas e atualiza a interface.
  - `run()`: Inicia o loop principal do Tkinter.

---

## **Fluxo de Funcionamento**

1. O usuário inicia a aplicação e visualiza o quadro com três colunas: *To Do*, *In Progress* e *Done*.
2. O usuário insere uma tarefa preenchendo os campos de título e descrição e clica no botão "Add Task".
3. A tarefa é adicionada automaticamente à coluna *To Do*.
4. O usuário pode mover as tarefas entre as colunas clicando nos botões correspondentes.
5. O quadro é atualizado dinamicamente à medida que as tarefas são adicionadas ou movidas.

---

## **Extensibilidade**

O projeto foi estruturado para facilitar a adição de novas funcionalidades sem alterar significativamente o código existente. Algumas possibilidades incluem:

- **Persistência de Dados**:
  - Adicionar suporte para salvar e carregar o estado do quadro (e.g., em JSON ou banco de dados).

- **Múltiplos Quadros**:
  - Criar uma classe `KanbanManager` para gerenciar diferentes quadros Kanban.

- **Interface Gráfica Melhorada**:
  - Substituir o Tkinter por uma biblioteca moderna como PyQt ou criar uma interface web.

- **Novas Funcionalidades**:
  - Adicionar prazos, prioridades e etiquetas às tarefas.
  - Implementar suporte a múltiplos usuários para colaboração.

---

## **Como Executar**

1. Certifique-se de ter o Python instalado (versão 3.6 ou superior).
2. Instale a biblioteca **Tkinter** (normalmente já incluída com o Python).
3. Execute o arquivo principal do projeto:
   ```bash
   python kanban_app.py
