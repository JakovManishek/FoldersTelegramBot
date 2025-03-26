"""
Текстовые сообщения для Telegram бота Folders.

Все текстовые константы и шаблоны сообщений для взаимодействия с пользователем.
"""

# Сообщения пагинации
FIRST_PAGE_ANSWER = "Вы находитесь на первой странице."
LAST_PAGE_ANSWER = "Вы находитесь на последней странице."


def now_page_answer(page: int, cnt: int) -> str:
    """Генерирует сообщение о текущей странице."""
    return f"Вы находитесь на {page} из {cnt} страниц."


# Сообщения об ошибках
LONG_NAME_ERROR = (
    "Слишком длинное название. Пожалуйста, используйте не более 50 символов в имени папки."
)
PRIVATE_FOLDER_ERROR = "Эта папка приватная. Ее нельзя добавить."
LINK_IS_NOT_VALID_ERROR = "Ссылка на папку не действительна."
DOUBLICATE_FOLDER_ERROR = "Нельзя добавить в папку ту же самую папку."
INCORRECTLY_PRIVATE_CHOSEN_ERROR = (
    "Пожалуйста, выберите один из вариантов из списка ниже:"
)
INCORRECTLY_TEXT_ERROR = (
    "Неизвестная команда.\nНажмите /help, чтобы ознакомиться с ботом."
)
INCORRECTLY_MEDIA_ERROR = "Неправильные входные данные. Пришлите медиа."
TECHNICAL_JOB_TEXT = "Бот не работает. Происходят технические работы."

# Тексты для клавиатур
HEAD_TEXT_KB = (
    "Нажмите кнопку \"Очистить текст\", если хотите вернуть текст папки к изначальному."
)
CHOOSE_PRIVATE_KB = "Выберите режим приватности:"
MEDIA_GROUP_KB = (
    "Нажмите кнопку \"Завершить добавление\", если загрузились все файлы."
)

# Основные текстовые сообщения
ADD_VERTEX_TEXT = (
    "Пришлите медиа (оно добавится в эту папку).\n\n"
    "Если хотите добавить папку - пришлите название новой папки "
    "или ссылку на уже существующую папку:"
)

COMPLETE_HEAD_TEXT = "Текст добавлен."
CHOOSE_NAME_TEXT = "Выберите приватность папки:"
ADD_HEAD_TEXT = (
    "Напишите текст (например, описание папки или заметка). "
    "Он будет отображаться под названием папки."
)


def folder_is_create_text(private: str, folder_name: str) -> str:
    """Генерирует сообщение о создании папки."""
    return f"Создана {private} папка с именем: {folder_name}."


ADD_GROUP_FOLDER_TEXT = (
    "Добавление \"Папки группы\" по ссылке.\n\n"
    "Добавленная папка является полностью публичной, "
    "т.е. все ее могут редактировать (возможность создания папок с одним редактором "
    "будет добавлена в следующих обновлениях).\n\n"
    "Изменять эту и все папки в ней могут все пользователи. Чтобы другим пользователям "
    "изменять эту папку - им нужно по ссылке добавить папку к себе "
    "(в личные сообщения с ботом)."
)

# Команды бота
NEW_CHAT_MESSAGE = (
    "Добро пожаловать в Бот Folders!\n"
    "Чтобы ознакомиться с <b>Инструкцией пользования ботом</b> нажмите: /help"
)

HELP_INSTRUCTION = """
<b>Инструкция пользования ботом Folder:</b>

Данный бот реализует метод хранения <b><i>медиа (файлы, фото, видео)</i></b> и <b><i>текстовых заметок</i></b> по папкам.

<b>Пользователь может создать папку в одном из двух режимов:</b>
   <b><i>1. Публичная папка</i></b> – Любой пользователь может добавить эту папку к себе по ссылке. Никто кроме создателя этой папки не может изменять содержимое папки. Создатель не может редактировать имя этой папки.
   <b><i>2. Приватная папка</i></b> – Никто кроме создателя папки не может получить доступ к ней. Создатель может изменять содержимое папки, а также редактировать имя этой папки.

<b>Взаимодействие с ботом:</b>
   <b><i>• Создать папку</i></b> – Пользователь создает папку, указывая название папки и режим приватности. <i>Названия приватных папок не могут повторяться!</i>
   <b><i>• Добавить папку</i></b> – Пользователь добавляет Публичную папку к себе по ссылке. <i>Пользователь не может никак ее изменять!</i>
   <b><i>• Удалить папку</i></b> – Удаление папки у пользователя без дальнейшего ее восстановления, если папка приватная. Если папка публичная, то ее можно будет восстановить по ссылке, если эта папка есть у хотя бы одного пользователя, иначе папка так же стирается без восстановления.
   <b><i>• Переименовать папку</i></b> – Переименовать можно только приватную папку. <i>Названия приватных папок не могут повторяться!</i>
   <b><i>• Изменить текстовую заметку в папке</i></b> – Текстовое пояснение к папке, расположенное перед файлами.
   <b><i>• Добавить файл</i></b> – Пользователь добавляет файл в папку. <i>Названия файлов не могут повторяться в одной папке!</i>
   <b><i>• Удалить файл</i></b> – Удаление файла из папки.

<b>Команды, доступные пользователю:</b>
   /start – Начало работы с ботом. Команда очищает историю чата (за последние два дня) и показывает пользователю все его папки по страницам.
   /help – Подробная инструкция пользования ботом.
"""

ADD_GROUP_FOLDER = "Отправьте название папки"
ADD_GROUP_LINK = "Отправьте ссылку на папку"

MADE_BY_TEXT = """
FoldersTelegramBot Version 2.0

Designed and created by @Jakov_Manishek.
Сreated based on the library aiogram 3+.

Git проекта: <code>https://github.com/JakovManishek/FoldersTelegramBot</code>

Следующие обновления: Уменьшение спама. Общее исправление ошибок.
"""

# Основные текстовые шаблоны
def name_fold_text(folder_name: str, private_mode: int, vertex_type: str) -> str:
    """Генерирует текст с информацией о папке."""
    if vertex_type != "U":
        privacy = "приватная" if private_mode == 1 else "публичная"
        return f"Открыта <b>{privacy}</b> папка:\n{folder_name}."
    return f"Открыта папка:\n{folder_name}."


def link_fold_text(folder_link: str) -> str:
    """Генерирует текст со ссылкой на папку."""
    return f"Ссылка на папку:\n<code>{folder_link}</code>."


EMPTY_TEXT = "Тут пока пусто."
NOT_EMPTY_TEXT = "Снизу расположены папки и медиа."
PUBLIC_LOCATED_VERTICES = (
    "Чтобы <b>Добавить</b> папку или медиа - нажмите на кнопку \"<b>Добавить</b>\"."
)
PRIVATE_LOCATED_VERTICES = (
    "Это приватная папка. Изменять ее содержимое может только создатель."
)
DELETE_VERTICES = "Чтобы <b>Удалить</b> папку или медиа - нажмите на папку/медиа."


def dif_head_text(head_text: str, private_mode: int, is_empty: bool) -> str:
    """Генерирует основной текст для папки с учетом ее состояния."""
    if head_text:
        return head_text

    head_ans = EMPTY_TEXT if is_empty else NOT_EMPTY_TEXT
    addition = PRIVATE_LOCATED_VERTICES if private_mode else PUBLIC_LOCATED_VERTICES
    return f"{head_ans} {addition}"


def start_text(
    chat_type: str,
    folder_link: str,
    folder_name: str,
    vertex_type: str,
    private_mode: int,
    delete_mode: bool,
    is_empty: bool,
    head_text: str = "",
) -> str:
    """
    Генерирует стартовое сообщение для папки.
    
    Args:
        chat_type: Тип чата ('private' или другой)
        folder_link: Ссылка на папку
        folder_name: Название папки
        vertex_type: Тип вершины ('U' - пользователь, иначе - папка)
        private_mode: Режим приватности (0/1)
        delete_mode: Флаг режима удаления
        is_empty: Флаг пустой папки
        head_text: Дополнительный текст папки
        
    Returns:
        Сформированное текстовое сообщение
    """
    if vertex_type == "U" and chat_type == "private":
        answer_text = ""
    else:
        answer_text = f"{name_fold_text(folder_name, private_mode, vertex_type)}\n\n"
    
    if delete_mode:
        return answer_text + DELETE_VERTICES
    
    if vertex_type == "U" and chat_type == "private":
        base_text = f"{head_text}\n\n{EMPTY_TEXT if is_empty else NOT_EMPTY_TEXT}"
        return f"{base_text} {PUBLIC_LOCATED_VERTICES}"
    
    if vertex_type == "U":
        answer_text += f"{link_fold_text(folder_link)}\n\n"
        if head_text:
            answer_text += f"{head_text}\n\n{EMPTY_TEXT if is_empty else NOT_EMPTY_TEXT}"
        else:
            answer_text += EMPTY_TEXT if is_empty else NOT_EMPTY_TEXT
    else:
        answer_text += f"{link_fold_text(folder_link)}\n\n"
        answer_text += dif_head_text(head_text, private_mode, is_empty)

    return answer_text