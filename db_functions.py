import sqlite3


def cycle_BFS(vertices_id: list[int], path_id: list[int]) -> bool:

    if not vertices_id:
        return True
    
    next_vertices_id: list[int] = []
    for id in vertices_id:

        if id in path_id:
            return False
        
        next_vertices = get_value_db("Folders", "next_vertices", id).split(";")
        next_vertices = [] if next_vertices[-1] == "" else next_vertices

        next_vertices_id += [int(ids.split(":")[-1]) for ids in next_vertices if ids.split(":")[0] == "F"]

    return cycle_BFS(next_vertices_id, path_id)


def delete_DFS(vertex_type: str, vertex_id: int, chat_id: int, fl_cnt: bool | None = True) -> dict[str, list[int]]:

    delete_id: dict[str, list[int]] = {"F": [], "D": [], "change_cnt": []}
    
    if vertex_type == "D":
        delete_id["D"].append(vertex_id)
        return delete_id

    autor_id = get_value_db("Folders", "autor_id", vertex_id)
    cnt = get_value_db("Folders", "count_of_users", vertex_id)

    print("9: ", cnt, autor_id, chat_id, delete_id, vertex_id)
    if cnt > 1:
        delete_id["change_cnt"].append(vertex_id)
        fl_cnt = False
        
    if not fl_cnt:
        return delete_id
    
    delete_id["F"].append(vertex_id)
    print("4:", delete_id)

    next_vertices = get_value_db("Folders", "next_vertices", vertex_id).split(";")
    next_vertices = [] if next_vertices[-1] == "" else next_vertices

    for type, id in [[elem.split(":")[0], int(elem.split(":")[-1])] for elem in next_vertices]:

        result = delete_DFS(type, id, chat_id, fl_cnt)
        delete_id["F"] += result["F"]
        delete_id["D"] += result["D"]
        delete_id["change_cnt"] += result["change_cnt"]

    return delete_id


def change_cnt_DFS(vertex_type: str, vertex_id: int, change: int | None = 1) -> dict[str, list[int]]:
    
    if vertex_type == "D":
        return

    cnt = get_value_db("Folders", "count_of_users", vertex_id)
    set_value_db("Folders", "count_of_users", vertex_id, cnt + change)
    
    next_vertices = get_value_db("Folders", "next_vertices", vertex_id).split(";")
    next_vertices = [] if next_vertices[-1] == "" else next_vertices

    for type, id in [[elem.split(":")[0], int(elem.split(":")[-1])] for elem in next_vertices]:

        change_cnt_DFS(type, id, change)




def is_user_in_table(chat_id: int) -> bool:    # Проверка на наличе пользователя в таблице
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM Users WHERE chat_id = ?', (chat_id,))

        if cur.fetchone() is None:
            return False
        return True
    




def get_value_db(table: str, column: str, id: int) -> str | int:
    
    match table:
        case "Users":
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute(f"SELECT {column} FROM Users WHERE chat_id = ?", (id,))
            
        case "Folders":
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute(f"SELECT {column} FROM Folders WHERE id = ?", (id,))
            
        case "Files":
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute(f"SELECT {column} FROM Files WHERE id = ?", (id,))

    return cur.fetchone()[0]
        

def set_value_db(table: str, column: str, id: int, new_value: str | int) -> None:

    match table:
        case "Users":
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute(f"UPDATE Users SET {column} = ? WHERE chat_id = ?", (new_value, id))
            
        case "Folders":
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute(f"UPDATE Folders SET {column} = ? WHERE id = ?", (new_value, id))
            
        case "Files":
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute(f"UPDATE Files SET {column} = ? WHERE id = ?", (new_value, id))


def get_full_parameters(folder_id: int) -> list[str | int]:
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute(f"SELECT name, autor_id, private_mode, next_vertices, head_text FROM Folders WHERE id = ?", (folder_id,))
    
    return cur.fetchone()




def create_user(chat_id: int, chat_type: str, name: str) -> int:    # Шаг 1

    private_mode = 1 if chat_type == "private" else 0

    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute("INSERT INTO Folders (name, autor_id, private_mode) VALUES (?, ?, ?)", (name, chat_id, private_mode))

        cur.execute("INSERT INTO Users (chat_id, path) VALUES (?, ?)", (chat_id, f"U:{cur.lastrowid}"))

        last_row_id = cur.lastrowid

    return last_row_id
            

def create(chat_id: int, lvl: str, name: str, private_mode: int | None = None, file_id: str | None = None, file_type: str | None = None) -> int:    # Шаг 2

    vertex_id = int(get_value_db("Users", "path", chat_id).split("\\")[-1].split(":")[-1])

    next_vertices = get_value_db("Folders", "next_vertices", vertex_id).split(";")
    next_vertices = [] if next_vertices[0] == "" else next_vertices

    if lvl == "fold":
        cnt_users = get_value_db("Folders", "count_of_users", vertex_id)
    else:
        cnt_users = None
    print("8: ", cnt_users, vertex_id)

    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        if lvl == "fold":
            cur.execute("INSERT INTO Folders (private_mode, name, autor_id, count_of_users) VALUES (?, ?, ?, ?)", (private_mode, name, chat_id, cnt_users))
        else:
            cur.execute("INSERT INTO Files (file_id, name, file_type) VALUES (?, ?, ?)", (file_id, name, file_type))
        last_row_id = cur.lastrowid
    
        
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        set_value_db("Folders", "next_vertices", vertex_id, ";".join([*next_vertices, f"{'F' if lvl == 'fold' else 'D'}:{last_row_id}"]))
    
    return last_row_id


def add_folder(chat_id: int, new_vertex_type: str, new_vertex_id: int) -> None:    # Шаг 3.1

    vertex_type, vertex_id = get_value_db("Users", "path", chat_id).split("\\")[-1].split(":")
    vertex_id = int(vertex_id)

    path_id = [int(ids.split(":")[-1]) for ids in get_value_db("Users", "path", chat_id).split("\\")]
    
    
    if not cycle_BFS([new_vertex_id], path_id):
        raise KeyError("You cannot add the same folder to a folder")

    next_vertices = get_value_db("Folders", "next_vertices", vertex_id).split(";")
    next_vertices = [] if next_vertices[0] == "" else next_vertices

    set_value_db("Folders", "next_vertices", vertex_id, ";".join([*next_vertices, f"F:{new_vertex_id}"]))
    print("7:", new_vertex_type, new_vertex_id)
    change_cnt_DFS(new_vertex_type, new_vertex_id, 1)

    
def delete(chat_id: int, vertex: str) -> None:    # Шаг 3.2
    vertex_type, vertex_id = vertex.split(":")
    delete_id = delete_DFS(vertex_type, int(vertex_id), chat_id)
    
    id = get_value_db("Users", "path", chat_id).split("\\")[-1].split(":")[-1]
    next_vertices = get_value_db("Folders", "next_vertices", id).split(";")
    next_vertices = [] if next_vertices[0] == "" else next_vertices
    print("6:", delete_id, next_vertices, vertex_type, vertex_id, id)
    next_vertices.remove(vertex)
    set_value_db("Folders", "next_vertices", id, ";".join(next_vertices))

    
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()

        cur.executemany('DELETE FROM Folders WHERE id = ?', [(id,) for id in delete_id["F"]])
        cur.executemany('DELETE FROM Files WHERE id = ?', [(id,) for id in delete_id["D"]])

    with sqlite3.connect('database.db') as con:
        cur = con.cursor()

        for id in delete_id["change_cnt"]:
            change_cnt_DFS("F", id, -1)
