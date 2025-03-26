import sqlite3
from pathlib import Path


def create_db(db_path: str = 'database.db') -> bool:
    """
    Создает базу данных SQLite с необходимыми таблицами.
    
    Args:
        db_path: Путь к файлу базы данных (по умолчанию 'database.db')
        
    Returns:
        bool: True если создание прошло успешно, иначе False
        
    Raises:
        sqlite3.Error: В случае ошибок работы с базой данных
    """
    try:
        # Создаем директорию для базы данных, если её нет
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(db_path) as con:
            cur = con.cursor()
            
            # Создание таблицы Users
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Users (
                    chat_id INTEGER PRIMARY KEY,
                    messages_id TEXT NOT NULL DEFAULT "",
                    pages TEXT NOT NULL DEFAULT "1",
                    delete_mode INTEGER NOT NULL DEFAULT 0,
                    path TEXT NOT NULL DEFAULT ""
                )
            """)
            
            # Создание таблицы Folders
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Folders (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL DEFAULT "None",
                    autor_id INTEGER,
                    private_mode INTEGER NOT NULL,
                    count_of_users INTEGER NOT NULL DEFAULT 1,
                    next_vertices TEXT NOT NULL DEFAULT "",
                    head_text TEXT NOT NULL DEFAULT ""
                )
            """)
            
            # Создание таблицы Files
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Files (
                    id INTEGER PRIMARY KEY,
                    file_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    file_type TEXT NOT NULL
                )
            """)
            
            # Создание индексов для улучшения производительности
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_folders_autor_id 
                ON Folders(autor_id)
            """)
            
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_path 
                ON Users(path)
            """)
            
            con.commit()
            
        print(f"База данных успешно создана: {db_path}")
        return True
        
    except sqlite3.Error as ex:
        print(f"Ошибка при создании базы данных: {ex}")
        return False
    except Exception as ex:
        print(f"Неожиданная ошибка: {ex}")
        return False


if __name__ == "__main__":
    # Создаем базу данных в поддиректории 'database'
    DB_DIR = Path(__file__).parent / "database"
    DB_PATH = str(DB_DIR / "database.db")
    
    if create_db(DB_PATH):
        print("Инициализация базы данных завершена успешно")
    else:
        print("Ошибка инициализации базы данных")