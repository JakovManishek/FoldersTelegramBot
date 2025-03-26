import sqlite3
from typing import Union, List, Tuple, Optional, Dict
from pathlib import Path

# Константы для работы с базой данных
DB_DIR = Path(__file__).parent.parent / "database"
DB_PATH = DB_DIR / "database.db"


def cycle_BFS(vertices_id: List[int], path_id: List[int]) -> bool:
    """
    Проверяет наличие циклов в графе с помощью обхода в ширину (BFS).
    
    Args:
        vertices_id: Список идентификаторов вершин для проверки
        path_id: Список идентификаторов вершин в текущем пути
        
    Returns:
        bool: False если найден цикл, иначе True
    """
    if not vertices_id:
        return True
    
    next_vertices_id: List[int] = []
    for vertex_id in vertices_id:
        if vertex_id in path_id:
            return False
        
        next_vertices = get_value_db("Folders", "next_vertices", vertex_id).split(";")
        next_vertices = [] if next_vertices[-1] == "" else next_vertices

        next_vertices_id += [
            int(ids.split(":")[-1]) 
            for ids in next_vertices 
            if ids.split(":")[0] == "F"
        ]

    return cycle_BFS(next_vertices_id, path_id)


def delete_DFS(
    vertex_type: str, 
    vertex_id: int, 
    chat_id: int, 
    fl_cnt: Optional[bool] = True
) -> Dict[str, List[int]]:
    """
    Рекурсивно удаляет вершины графа с помощью обхода в глубину (DFS).
    
    Args:
        vertex_type: Тип вершины ('F' - папка, 'D' - файл)
        vertex_id: Идентификатор вершины
        chat_id: Идентификатор чата пользователя
        fl_cnt: Флаг для управления подсчетом пользователей
        
    Returns:
        Словарь с идентификаторами удаляемых элементов:
        {
            "F": [список id папок],
            "D": [список id файлов],
            "change_cnt": [список id для изменения счетчика]
        }
    """
    delete_id: Dict[str, List[int]] = {"F": [], "D": [], "change_cnt": []}
    
    if vertex_type == "D":
        delete_id["D"].append(vertex_id)
        return delete_id

    autor_id = get_value_db("Folders", "autor_id", vertex_id)
    cnt = get_value_db("Folders", "count_of_users", vertex_id)

    if cnt > 1:
        delete_id["change_cnt"].append(vertex_id)
        fl_cnt = False
        
    if not fl_cnt:
        return delete_id
    
    delete_id["F"].append(vertex_id)

    next_vertices = get_value_db("Folders", "next_vertices", vertex_id).split(";")
    next_vertices = [] if next_vertices[-1] == "" else next_vertices

    for elem in next_vertices:
        type_, id_ = elem.split(":")[0], int(elem.split(":")[-1])
        result = delete_DFS(type_, id_, chat_id, fl_cnt)
        delete_id["F"] += result["F"]
        delete_id["D"] += result["D"]
        delete_id["change_cnt"] += result["change_cnt"]

    return delete_id


def change_cnt_DFS(
    vertex_type: str, 
    vertex_id: int, 
    change: Optional[int] = 1
) -> None:
    """
    Рекурсивно изменяет счетчик пользователей для папок.
    
    Args:
        vertex_type: Тип вершины ('F' - папка, 'D' - файл)
        vertex_id: Идентификатор вершины
        change: Величина изменения счетчика
    """
    if vertex_type == "D":
        return

    cnt = get_value_db("Folders", "count_of_users", vertex_id)
    set_value_db("Folders", "count_of_users", vertex_id, cnt + change)
    
    next_vertices = get_value_db("Folders", "next_vertices", vertex_id).split(";")
    next_vertices = [] if next_vertices[-1] == "" else next_vertices

    for elem in next_vertices:
        type_, id_ = elem.split(":")[0], int(elem.split(":")[-1])
        change_cnt_DFS(type_, id_, change)


def is_user_in_table(chat_id: int) -> bool:
    """
    Проверяет наличие пользователя в таблице Users.
    
    Args:
        chat_id: Идентификатор чата пользователя
        
    Returns:
        bool: True если пользователь существует, иначе False
    """
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM Users WHERE chat_id = ?', (chat_id,))
        return cur.fetchone() is not None


def get_value_db(table: str, column: str, id: int) -> str | int:
    """
    Получает значение из указанной таблицы по ID.
    
    Args:
        table: Название таблицы ('Users', 'Folders', 'Files')
        column: Название столбца
        id: ID записи (chat_id для Users, id для других таблиц)
        
    Returns:
        Значение из базы данных (str или int)
    """
    match table:
        case "Users":
            with sqlite3.connect(DB_PATH) as con:
                cur = con.cursor()
                # Для таблицы Users используем chat_id как ключ
                cur.execute(
                    f"SELECT {column} FROM Users WHERE chat_id = ?", 
                    (id,)
                )
            
        case "Folders":
            with sqlite3.connect(DB_PATH) as con:
                cur = con.cursor()
                # Для таблицы Folders используем id как ключ
                cur.execute(
                    f"SELECT {column} FROM Folders WHERE id = ?", 
                    (id,)
                )
            
        case "Files":
            with sqlite3.connect(DB_PATH) as con:
                cur = con.cursor()
                # Для таблицы Files используем id как ключ
                cur.execute(
                    f"SELECT {column} FROM Files WHERE id = ?", 
                    (id,)
                )

    # Возвращаем первое значение из результата запроса
    return cur.fetchone()[0]
        

def set_value_db(table: str, column: str, id: int, new_value: str | int) -> None:
    """
    Обновляет значение в указанной таблице.
    
    Args:
        table: Название таблицы ('Users', 'Folders', 'Files')
        column: Название столбца  
        id: ID записи (chat_id для Users, id для других таблиц)
        new_value: Новое значение
    """
    match table:
        case "Users":
            with sqlite3.connect(DB_PATH) as con:
                cur = con.cursor()
                # Обновление записи в таблице Users
                cur.execute(
                    f"UPDATE Users SET {column} = ? WHERE chat_id = ?",
                    (new_value, id)
                )
            
        case "Folders":
            with sqlite3.connect(DB_PATH) as con:
                cur = con.cursor()
                # Обновление записи в таблице Folders
                cur.execute(
                    f"UPDATE Folders SET {column} = ? WHERE id = ?",
                    (new_value, id)
                )
            
        case "Files":
            with sqlite3.connect(DB_PATH) as con:
                cur = con.cursor()
                # Обновление записи в таблице Files
                cur.execute(
                    f"UPDATE Files SET {column} = ? WHERE id = ?",
                    (new_value, id)
                )


def get_full_parameters(folder_id: int) -> List[Union[str, int]]:
    """
    Получает все параметры папки по её ID.
    
    Args:
        folder_id: Идентификатор папки
        
    Returns:
        Список параметров папки: [name, autor_id, private_mode, next_vertices, head_text]
    """
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute(
            "SELECT name, autor_id, private_mode, next_vertices, head_text "
            "FROM Folders WHERE id = ?", 
            (folder_id,)
        )
        return cur.fetchone()


def create_user(chat_id: int, chat_type: str, name: str) -> int:
    """
    Создает нового пользователя и корневую папку для него.
    
    Args:
        chat_id: Идентификатор чата пользователя
        chat_type: Тип чата ('private' или другой)
        name: Имя пользователя/папки
        
    Returns:
        int: ID созданной корневой папки
    """
    private_mode = 1 if chat_type == "private" else 0

    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO Folders (name, autor_id, private_mode) "
            "VALUES (?, ?, ?)", 
            (name, chat_id, private_mode)
        )
        folder_id = cur.lastrowid
        
        cur.execute(
            "INSERT INTO Users (chat_id, path) VALUES (?, ?)", 
            (chat_id, f"U:{folder_id}")
        )

    return folder_id


def create(
    chat_id: int, 
    lvl: str, 
    name: str, 
    private_mode: Optional[int] = None,
    file_id: Optional[str] = None,
    file_type: Optional[str] = None
) -> int:
    """
    Создает новую папку или файл в текущей директории пользователя.
    
    Args:
        chat_id: Идентификатор чата пользователя
        lvl: Тип создаваемого объекта ('fold' - папка, иначе - файл)
        name: Имя создаваемого объекта
        private_mode: Режим приватности (только для папок)
        file_id: ID файла (только для файлов)
        file_type: Тип файла (только для файлов)
        
    Returns:
        int: ID созданного объекта
    """
    vertex_id = int(get_value_db("Users", "path", chat_id).split("\\")[-1].split(":")[-1])

    next_vertices = get_value_db("Folders", "next_vertices", vertex_id).split(";")
    next_vertices = [] if next_vertices[0] == "" else next_vertices

    cnt_users = get_value_db("Folders", "count_of_users", vertex_id) if lvl == "fold" else None

    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        if lvl == "fold":
            cur.execute(
                "INSERT INTO Folders (private_mode, name, autor_id, count_of_users) "
                "VALUES (?, ?, ?, ?)", 
                (private_mode, name, chat_id, cnt_users)
            )
        else:
            cur.execute(
                "INSERT INTO Files (file_id, name, file_type) VALUES (?, ?, ?)", 
                (file_id, name, file_type)
            )
        last_row_id = cur.lastrowid
    
    set_value_db(
        "Folders", 
        "next_vertices", 
        vertex_id, 
        ";".join([*next_vertices, f"{'F' if lvl == 'fold' else 'D'}:{last_row_id}"])
    )
    
    return last_row_id


def add_folder(chat_id: int, new_vertex_type: str, new_vertex_id: int) -> None:
    """
    Добавляет существующую папку в текущую директорию пользователя.
    
    Args:
        chat_id: Идентификатор чата пользователя
        new_vertex_type: Тип добавляемой вершины
        new_vertex_id: ID добавляемой вершины
        
    Raises:
        KeyError: При попытке добавить папку, которая создаст цикл
    """
    vertex_type, vertex_id = get_value_db("Users", "path", chat_id).split("\\")[-1].split(":")
    vertex_id = int(vertex_id)

    path_id = [
        int(ids.split(":")[-1]) 
        for ids in get_value_db("Users", "path", chat_id).split("\\")
    ]
    
    if not cycle_BFS([new_vertex_id], path_id):
        raise KeyError("You cannot add the same folder to a folder")

    next_vertices = get_value_db("Folders", "next_vertices", vertex_id).split(";")
    next_vertices = [] if next_vertices[0] == "" else next_vertices

    set_value_db(
        "Folders", 
        "next_vertices", 
        vertex_id, 
        ";".join([*next_vertices, f"F:{new_vertex_id}"])
    )
    change_cnt_DFS(new_vertex_type, new_vertex_id, 1)

    
def delete(chat_id: int, vertex: str) -> None:
    """
    Удаляет папку или файл из текущей директории пользователя.
    
    Args:
        chat_id: Идентификатор чата пользователя
        vertex: Строка с типом и ID удаляемого объекта (формат "тип:id")
    """
    vertex_type, vertex_id = vertex.split(":")
    delete_id = delete_DFS(vertex_type, int(vertex_id), chat_id)
    
    id_ = get_value_db("Users", "path", chat_id).split("\\")[-1].split(":")[-1]
    next_vertices = get_value_db("Folders", "next_vertices", id_).split(";")
    next_vertices = [] if next_vertices[0] == "" else next_vertices
    
    next_vertices.remove(vertex)
    set_value_db("Folders", "next_vertices", id_, ";".join(next_vertices))

    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.executemany(
            'DELETE FROM Folders WHERE id = ?', 
            [(id,) for id in delete_id["F"]]
        )
        cur.executemany(
            'DELETE FROM Files WHERE id = ?', 
            [(id,) for id in delete_id["D"]]
        )

    for id_ in delete_id["change_cnt"]:
        change_cnt_DFS("F", id_, -1)