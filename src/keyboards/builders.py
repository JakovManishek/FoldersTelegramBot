from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup
)
import database.сore as core
import texts.messages as messages
from math import ceil


def inline_start_kb(
    chat_id: int,
    autor_id: int,
    chat_type: str,
    vertex_type: str,
    private_mode: int,
    delete_mode: bool,
    next_vertices: list[str]
) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для навигации по папкам и файлам.
    
    Args:
        chat_id: ID чата пользователя
        autor_id: ID автора текущей папки
        chat_type: Тип чата ('private' или другой)
        vertex_type: Тип текущей вершины ('U' - пользователь, 'F' - папка, 'D' - файл)
        private_mode: Режим приватности (0/1)
        delete_mode: Флаг режима удаления
        next_vertices: Список дочерних элементов в формате ["тип:id", ...]
        
    Returns:
        InlineKeyboardMarkup: Объект клавиатуры для Telegram бота
    """
    # Получаем информацию о текущей странице
    pages = [
        int(page) 
        for page in core.get_value_db("Users", "pages", chat_id).split("\\")
    ]
    cnt_page = ceil(len(next_vertices) / 10)  # Общее количество страниц
    page = pages[-1]  # Текущая страница

    kb = []  # Будущая клавиатура

    # Обработка случая, когда нет элементов
    if cnt_page == 0:
        # Кнопки для пустой папки
        if (chat_type == "private" and 
            ((private_mode == 1 and autor_id == chat_id) or private_mode == 0)):
            kb += [
                [InlineKeyboardButton(
                    text="Изменить текст папки", 
                    callback_data="head"
                )],
                [InlineKeyboardButton(
                    text="Добавить", 
                    callback_data="add"
                )]
            ]

        # Кнопка "Назад" для всех кроме корневой папки
        if vertex_type != "U":
            kb += [
                [InlineKeyboardButton(
                    text="Назад", 
                    callback_data="back"
                )]
            ]

        return InlineKeyboardMarkup(inline_keyboard=kb)

    # Корректировка номера страницы, если он некорректен
    if page < 1:
        pages[-1] = 1
        core.set_value_db(
            "Users", 
            "pages", 
            chat_id, 
            "\\".join(str(p) for p in pages)
        )
        page = 1

    # Вычисляем диапазон элементов для текущей страницы
    start = (page - 1) * 10
    stop = min(len(next_vertices), start + 10)

    # Дополнительная проверка на выход за границы
    while start >= stop:
        pages[-1] -= 1
        core.set_value_db(
            "Users", 
            "pages", 
            chat_id, 
            "\\".join(str(p) for p in pages)
        )
        page -= 1
        start = (page - 1) * 10
        stop = min(len(next_vertices), start + 10)

    # Добавляем кнопки для элементов текущей страницы
    for ind in range(start, stop):
        try:
            vert_type, vert_id = next_vertices[ind].split(":")
            vert_id = int(vert_id)
            
            # Получаем имя папки/файла
            table = "Folders" if vert_type == "F" else "Files"
            name = core.get_value_db(table, "name", vert_id)
            
            kb.append([
                InlineKeyboardButton(
                    text=name,
                    callback_data=next_vertices[ind]
                )
            ])
        except Exception:
            continue  # Пропускаем некорректные элементы

    # Добавляем пагинацию
    kb += [
        [
            InlineKeyboardButton(text="<<", callback_data="pagina_back"),
            InlineKeyboardButton(text=f"{page}/{cnt_page}", callback_data="pagina_view"),
            InlineKeyboardButton(text=">>", callback_data="pagina_next")
        ]
    ]

    # Добавляем дополнительные кнопки в зависимости от режима
    if not delete_mode:
        if (chat_type == "private" and 
            ((private_mode == 1 and autor_id == chat_id) or private_mode == 0)):
            kb += [
                [
                    InlineKeyboardButton(
                        text="Изменить текст папки", 
                        callback_data="head"
                    )
                ],
                [
                    InlineKeyboardButton(text="Добавить", callback_data="add"),
                    InlineKeyboardButton(text="Удалить", callback_data="delete")
                ]
            ]
        
        # Кнопка "Назад" для всех кроме корневой папки
        if vertex_type != "U":
            kb += [
                [InlineKeyboardButton(
                    text="Назад", 
                    callback_data="back"
                )]
            ]
    else:
        # Кнопка для выхода из режима удаления
        kb += [
            [InlineKeyboardButton(
                text="Завершить удаление", 
                callback_data="delete_back"
            )]
        ]

    return InlineKeyboardMarkup(
        inline_keyboard=kb,
        resize_keyboard=True,
        row_width=1
    )


def reply_choose_private_kb() -> ReplyKeyboardMarkup:
    """
    Создает reply-клавиатуру для выбора типа папки (приватная/публичная).
    
    Returns:
        ReplyKeyboardMarkup: Клавиатура с двумя кнопками
    """
    kb = [
        [KeyboardButton(text="Приватная"), KeyboardButton(text="Публичная")]
    ]

    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        row_width=1,
        input_field_placeholder=messages.CHOOSE_PRIVATE_KB
    )


def reply_media_group_kb() -> ReplyKeyboardMarkup:
    """
    Создает reply-клавиатуру для завершения добавления медиагруппы.
    
    Returns:
        ReplyKeyboardMarkup: Клавиатура с одной кнопкой
    """
    kb = [
        [KeyboardButton(text="Завершить добавление")]
    ]

    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        row_width=1,
        input_field_placeholder=messages.MEDIA_GROUP_KB
    )


def reply_head_text_kb() -> ReplyKeyboardMarkup:
    """
    Создает reply-клавиатуру для работы с текстом папки.
    
    Returns:
        ReplyKeyboardMarkup: Клавиатура с кнопкой очистки текста
    """
    kb = [
        [KeyboardButton(text="Очистить текст")]
    ]

    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        row_width=1,
        input_field_placeholder=messages.HEAD_TEXT_KB
    )