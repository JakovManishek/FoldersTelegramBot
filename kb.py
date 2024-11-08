from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
import db_functions
import text
from math import ceil

    

def inline_start_kb(chat_id: int,
                    autor_id: int,
                    chat_type: str,
                    vertex_type: str,
                    private_mode: int,
                    delete_mode: bool,
                    next_vertices: list[str]) -> InlineKeyboardMarkup:


    pages = [int(page) for page in db_functions.get_value_db("Users", "pages", chat_id).split("\\")]
    cnt_page = ceil(len(next_vertices) / 10)
    page = pages[-1]

    kb = []


    if cnt_page == 0:
        if chat_type == "private" and ((private_mode == 1 and autor_id == chat_id) or private_mode == 0):
            kb += [[InlineKeyboardButton(text="Изменить текст папки", callback_data=f"head")]]
            kb += [[InlineKeyboardButton(text="Добавить", callback_data='add')]]

        if vertex_type != "U":
            kb += [[InlineKeyboardButton(text="Назад", callback_data='back')]]

        return InlineKeyboardMarkup(inline_keyboard=kb)
    

    if page < 1:
        pages[-1] = 1
        db_functions.set_value_db("Users", "pages", chat_id, "\\".join([str(page) for page in pages]))
        page = 1
    start = (page - 1) * 10
    stop = min(len(next_vertices), start + 10)
    while start >= stop:
        pages[-1] -= 1
        db_functions.set_value_db("Users", "pages", chat_id, "\\".join([str(page) for page in pages]))

        page -= 1
        start = (page - 1) * 10
        stop = min(len(next_vertices), start + 10)


    for ind in range(start, stop):
        type, id = next_vertices[ind].split(":")
        id = int(id)
        name = db_functions.get_value_db("Folders" if type == "F" else "Files", "name", id)

        kb.append([InlineKeyboardButton(text=name, callback_data=next_vertices[ind])])

    kb += [[InlineKeyboardButton(text="<<", callback_data="pagina_back"),
            InlineKeyboardButton(text=f"{page}/{cnt_page}", callback_data="pagina_view"),
            InlineKeyboardButton(text=">>", callback_data="pagina_next")]]
    
    print("3: ", delete_mode, chat_type, private_mode, vertex_type)
    if not delete_mode:
        if chat_type == "private" and ((private_mode == 1 and autor_id == chat_id) or private_mode == 0):
            kb += [[InlineKeyboardButton(text="Изменить текст папки", callback_data=f"head")],
                        [InlineKeyboardButton(text=f"Добавить", callback_data=f"add"),
                        InlineKeyboardButton(text=f"Удалить", callback_data=f"delete")]]
        if vertex_type != "U":     
            kb += [[InlineKeyboardButton(text="Назад", callback_data="back")]]

    else:
        kb += [[InlineKeyboardButton(text="Завершить удаление", callback_data=f"delete_back")]]

    # print("4:", kb)
    
    return InlineKeyboardMarkup(inline_keyboard=kb, resize_keyboard=True, row_width=1)




def reply_choose_private_kb() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text="Приватная"), KeyboardButton(text="Публичная")]]

    return ReplyKeyboardMarkup(keyboard=kb,
                               resize_keyboard=True,
                               row_width=1,
                               input_field_placeholder=text.choose_private_kb)


def reply_media_group_kb() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text="Завершить добавление")]]

    return ReplyKeyboardMarkup(keyboard=kb,
                               resize_keyboard=True,
                               row_width=1,
                               input_field_placeholder=text.media_group_kb)


def reply_head_text_kb() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text="Очистить текст")]]

    return ReplyKeyboardMarkup(keyboard=kb,
                               resize_keyboard=True,
                               row_width=1,
                               input_field_placeholder=text.head_text_kb)
