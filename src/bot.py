"""
Главный модуль Telegram-бота для управления структурой папок и файлов.

Основные компоненты:
- Обработчики команд (/start, /help)
- Машина состояний для добавления новых элементов
- Работа с медиафайлами
- Взаимодействие с базой данных
"""

import asyncio
from math import ceil
from typing import Optional, Union

import keyboards.builders as builders
import config
import database.сore as core
import texts.messages as messages

from dotenv import load_dotenv
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession


# Загрузка BOT_TOKEN из .env файла
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


# Инициализация бота с HTML-разметкой по умолчанию
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()


class OrderAdd(StatesGroup):
    """Класс состояний для добавления новых элементов."""
    folder_mode = State()
    new_vertices = State()
    new_group_vertices = State()
    create_group_vertex = State()
    add_group_folder = State()
    set_head_text = State()


async def clear_chat(chat_id: int, message_id: int) -> None:
    """Очистка чата от предыдущих сообщений.
    
    Args:
        chat_id: ID чата
        message_id: ID сообщения, от которого очищаем
    """
    try:
        for i in range(message_id, 0, -1):
            await bot.delete_message(chat_id, i)
    except TelegramBadRequest:
        pass


async def check_user_in_table(message: Message) -> None:
    """Проверка наличия пользователя в базе данных.
    
    Если пользователя нет - создает новую запись.
    """
    chat_id = message.chat.id
    chat_type = message.chat.type
    name = message.chat.title or message.chat.username

    if not core.is_user_in_table(chat_id):
        core.create_user(chat_id, chat_type, name)

async def send_start_message(
    level_message_type: str,
    message: Message | None = None,
    callback: CallbackQuery | None = None,
    change_page: int | None = 0
) -> None:
    """
    Отправляет стартовое сообщение с клавиатурой для навигации по папкам.
    
    Args:
        level_message_type: Тип сообщения ("message" или "callback")
        message: Объект сообщения (если level_message_type == "message")
        callback: Объект callback (если level_message_type == "callback")
        change_page: Изменение текущей страницы (для пагинации)
        
    Raises:
        ValueError: Если переданы некорректные параметры
    """
    # Проверка входных параметров
    if level_message_type not in ("message", "callback"):
        raise ValueError("Неподдерживаемый тип сообщения")
    if level_message_type == "message" and message is None:
        raise ValueError("Не передано сообщение")
    if level_message_type == "callback" and callback is None:
        raise ValueError("Не передан callback")

    # Получаем данные чата
    if level_message_type == "message":
        chat_type = message.chat.type  # type: ignore
        chat_id = message.chat.id  # type: ignore
    else:
        chat_type = callback.message.chat.type  # type: ignore
        chat_id = callback.message.chat.id  # type: ignore

    # Получаем текущий путь пользователя
    try:
        path = core.get_value_db("Users", "path", chat_id)
        vertex_type, vertex_id = path.split("\\")[-1].split(":")
        vertex_id = int(vertex_id)
    except (ValueError, AttributeError) as ex:
        print(f"Ошибка разбора пути: {ex}")
        # Сбрасываем путь к корневой папке
        path = core.get_value_db("Users", "path", chat_id).split("\\")
        core.set_value_db("Users", "path", chat_id, path[0])
        core.set_value_db("Users", "pages", chat_id, "1")
        await send_start_message(level_message_type="callback", callback=callback)
        return

    # Получаем параметры текущей папки
    try:
        delete_mode = core.get_value_db("Users", "delete_mode", chat_id)
        private_mode = core.get_value_db("Folders", "private_mode", vertex_id)
        autor_id = core.get_value_db("Folders", "autor_id", vertex_id)
        folder_params = core.get_full_parameters(vertex_id)
    except Exception as ex:
        print(f"Ошибка получения параметров: {ex}")
        # Сбрасываем настройки
        path = core.get_value_db("Users", "path", chat_id).split("\\")
        core.set_value_db("Users", "path", chat_id, path[0])
        core.set_value_db("Users", "pages", chat_id, "1")
        await send_start_message(level_message_type="callback", callback=callback)
        return

    # Обрабатываем список дочерних элементов
    next_vertices = (
        [] if folder_params[3].split(";")[0] == "" 
        else folder_params[3].split(";")
    )

    # Проверяем существование дочерних элементов
    i = 0
    while i < len(next_vertices):
        try:
            vert_type, vert_id = next_vertices[i].split(":")
            if vert_type != "D":
                # Проверяем существование папки
                _ = core.get_value_db("Folders", "id", int(vert_id))
        except Exception as ex:
            print(f"Ошибка проверки элемента: {ex}")
            next_vertices.pop(i)
        else:
            i += 1

    # Обновляем список вершин
    core.set_value_db(
        "Folders", 
        "next_vertices", 
        vertex_id, 
        ";".join(next_vertices)
    )

    # Обрабатываем пагинацию
    pages = [
        int(page) for page in 
        core.get_value_db("Users", "pages", chat_id).split("\\")
    ]
    
    if change_page != 0:
        pages[-1] += change_page
        core.set_value_db(
            "Users", 
            "pages", 
            chat_id, 
            "\\".join(str(page) for page in pages)
        )
    
    # Сбрасываем режим удаления если нет элементов
    if not next_vertices:
        core.set_value_db("Users", "delete_mode", chat_id, 0)
        delete_mode = 0

    # Формируем сообщение и клавиатуру
    text_message = messages.start_text(
        chat_type=chat_type,
        folder_link=config.encoding_folder(f"{vertex_type}:{vertex_id}", folder_params[0]),
        folder_name=folder_params[0],
        vertex_type=vertex_type,
        private_mode=folder_params[2],
        delete_mode=delete_mode,
        is_empty=(len(next_vertices) == 0),
        head_text=folder_params[4]
    )
    
    reply_markup = builders.inline_start_kb(
        chat_id=chat_id,
        autor_id=autor_id,
        chat_type=chat_type,
        vertex_type=vertex_type,
        private_mode=private_mode,
        delete_mode=delete_mode,
        next_vertices=next_vertices
    )

    # Отправляем сообщение
    if level_message_type == "message":
        await message.answer(text=text_message, reply_markup=reply_markup)  # type: ignore
    else:
        await callback.message.edit_text(text=text_message, reply_markup=reply_markup)  # type: ignore

    # Очищаем чат
    if level_message_type == "message" and chat_type == "private":
        await clear_chat(chat_id, message.message_id)  # type: ignore


@dp.message(CommandStart())
async def start(message: Message) -> None:
    """Обработчик команды /start."""
    await check_user_in_table(message)
    await send_start_message(level_message_type="message", message=message)


@dp.message(Command('help'))
async def help_command(message: Message) -> None:
    """Обработчик команды /help."""
    await message.answer(text=messages.HELP_INSTRUCTION)


@dp.message(Command('made_by'))
async def made_by_command(message: Message) -> None:
    """Обработчик команды /made_by."""
    await message.answer(text=messages.MADE_BY_TEXT)


@dp.callback_query(F.data)
async def inline_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Обработчик всех inline-кнопок."""
    await state.clear()
    chat_id = callback.message.chat.id
    call = str(callback.data)

    try:
        # Получаем текущий путь
        path = core.get_value_db("Users", "path", chat_id)
        vertex_type, vertex_id = path.split("\\")[-1].split(":")
        vertex_id = int(vertex_id)
        
        next_vertices = core.get_value_db("Folders", "next_vertices", vertex_id).split(";")
    except Exception:
        # Сброс при ошибке
        path = core.get_value_db("Users", "path", chat_id).split("\\")
        core.set_value_db("Users", "path", chat_id, path[0])
        core.set_value_db("Users", "pages", chat_id, 1)
        await send_start_message(level_message_type="callback", callback=callback)
        return

    next_vertices = [] if next_vertices[0] == "" else next_vertices
    page = int(core.get_value_db("Users", "pages", chat_id).split("\\")[-1])
    cnt_page = ceil(len(next_vertices) / 10)

    match call:
        case 'head':
            await callback.answer()
            await callback.message.answer(
                text=messages.ADD_HEAD_TEXT,
                reply_markup=builders.reply_head_text_kb()
            )
            await state.set_state(OrderAdd.set_head_text)
            await state.update_data(autor=callback.from_user.id)

        case 'add':
            await callback.answer()
            await state.set_state(OrderAdd.new_vertices)
            await callback.message.answer(
                text=messages.ADD_VERTEX_TEXT,
                reply_markup=builders.reply_media_group_kb()
            )
            await state.update_data(cnt=1)

        case 'delete':
            await callback.answer()
            core.set_value_db("Users", "delete_mode", chat_id, 1)
            await send_start_message(level_message_type="callback", callback=callback)

        case 'delete_back':
            await callback.answer()
            core.set_value_db("Users", "delete_mode", chat_id, 0)
            await send_start_message(level_message_type="callback", callback=callback)

        case 'pagina_back':
            if page == 1:
                await callback.answer(text=messages.FIRST_PAGE_ANSWER)
            else:
                await callback.answer()
                await send_start_message(
                    level_message_type="callback",
                    callback=callback,
                    change_page=-1
                )

        case 'pagina_view':
            await callback.answer(text=messages.now_page_answer(page, cnt_page))

        case 'pagina_next':
            if page == cnt_page:
                await callback.answer(text=messages.LAST_PAGE_ANSWER)
            else:
                await callback.answer()
                await send_start_message(
                    level_message_type="callback",
                    callback=callback,
                    change_page=1
                )

        case "back":
            await callback.answer()
            path = core.get_value_db("Users", "path", chat_id).split("\\")
            pages = core.get_value_db("Users", "pages", chat_id).split("\\")
            path.pop()
            pages.pop()
            core.set_value_db("Users", "path", chat_id, "\\".join(path))
            core.set_value_db("Users", "pages", chat_id, "\\".join(pages))
            await send_start_message(level_message_type="callback", callback=callback)

        case _:
            await callback.answer()
            vertex_type, vertex_id = call.split(":")
            vertex_id = int(vertex_id)
            delete_mode = core.get_value_db("Users", "delete_mode", chat_id)

            if delete_mode:
                try:
                    core.delete(chat_id, call)
                except Exception:
                    pass
                finally:
                    await send_start_message(level_message_type="callback", callback=callback)
                return

            if vertex_type == "F":
                try:
                    core.get_value_db("Folders", "id", vertex_id)
                except Exception:
                    pass
                else:
                    path = core.get_value_db("Users", "path", chat_id).split("\\")
                    pages = core.get_value_db("Users", "pages", chat_id).split("\\")
                    path.append(call)
                    pages.append("1")
                    core.set_value_db("Users", "path", chat_id, "\\".join(path))
                    core.set_value_db("Users", "pages", chat_id, "\\".join(pages))
                await send_start_message(level_message_type="callback", callback=callback)

            else:
                try:
                    file_type = core.get_value_db("Files", "file_type", vertex_id)
                    file_id = core.get_value_db("Files", "file_id", vertex_id)
                except Exception:
                    await send_start_message(level_message_type="callback", callback=callback)
                else:
                    match file_type:
                        case "photo":
                            await bot.send_photo(chat_id=chat_id, photo=file_id)
                        case "video":
                            await bot.send_video(chat_id=chat_id, video=file_id)
                        case "document":
                            await bot.send_document(chat_id=chat_id, document=file_id)
                        case "audio":
                            await bot.send_audio(chat_id=chat_id, audio=file_id)
                        case "voice":
                            await bot.send_voice(chat_id=chat_id, voice=file_id)
                        case "sticker":
                            await bot.send_sticker(chat_id=chat_id, sticker=file_id)
                        case "video_note":
                            await bot.send_video_note(chat_id=chat_id, video_note=file_id)
                        case _:
                            await callback.message.answer(text="Произошла ошибка в отправке файла.")


@dp.message(F.text.regexp(config.REGEX), OrderAdd.new_vertices)
async def regex_link_add_private(message: Message, state: FSMContext) -> None:
    """Обработка добавления папки по ссылке."""
    chat_id = message.chat.id
    decode = config.decoding_folder(message.text)
    new_vertex_type, new_vertex_id = decode[0].split(":")
    new_vertex_id = int(new_vertex_id)

    try:
        core.add_folder(chat_id, new_vertex_type, new_vertex_id)
    except TypeError:
        await message.answer(text=messages.LINK_IS_NOT_VALID_ERROR)
    except KeyError:
        await message.answer(text=messages.DOUBLICATE_FOLDER_ERROR)
    else:
        await message.answer(f"Добавлена папка: {decode[-1]}")

    await state.clear()
    await send_start_message(level_message_type="message", message=message)


@dp.message(F.text, OrderAdd.new_vertices)
async def folder_name_chosen(message: Message, state: FSMContext) -> None:
    """Обработка названия новой папки."""
    if message.text == "Завершить добавление":
        await state.clear()
        await send_start_message(level_message_type="message", message=message)
        return

    await state.update_data(folder_name=message.text)
    await message.answer(
        messages.CHOOSE_NAME_TEXT,
        reply_markup=builders.reply_choose_private_kb()
    )
    await state.set_state(OrderAdd.folder_mode)


@dp.message(F.text, OrderAdd.folder_mode)
async def private_chosen(message: Message, state: FSMContext) -> None:
    """Выбор типа папки (приватная/публичная)."""
    user_data = await state.get_data()
    chat_id = message.chat.id

    if message.text in ['Приватная', 'Публичная']:
        private_mode = 1 if message.text == 'Приватная' else 0
        try:
            core.create(chat_id, "fold", user_data['folder_name'], private_mode)
        except Exception:
            await message.answer(text=messages.LONG_NAME_ERROR)
        else:
            await message.answer(
                text=messages.folder_is_create_text(
                    message.text.lower(),
                    user_data['folder_name']
                )
            )
    else:
        await message.answer(
            text=messages.INCORRECTLY_PRIVATE_CHOSEN_ERROR,
            reply_markup=builders.reply_choose_private_kb()
        )

    await state.clear()
    await send_start_message(level_message_type="message", message=message)


@dp.message(OrderAdd.new_vertices)
async def send_media(message: Message, state: FSMContext) -> None:
    """Обработка добавления медиафайлов."""
    user_id = message.chat.id
    user_data = await state.get_data()
    cnt = user_data["cnt"]

    if message.text == "Завершить добавление":
        await state.clear()
        await send_start_message(level_message_type="message", message=message)
        return

    media = None
    if message.photo:
        media = [message.photo[2].file_id, f"photo_{cnt}", "photo"]
    elif message.video:
        media = [message.video.file_id, message.video.file_name, "video"]
    elif message.document:
        media = [message.document.file_id, message.document.file_name, "document"]
    elif message.audio:
        media = [message.audio.file_id, message.audio.file_name, "audio"]
    elif message.voice:
        media = [message.voice.file_id, f"voice_{cnt}", "voice"]
    elif message.sticker:
        media = [message.sticker.file_id, f"sticker_{cnt}", "sticker"]
    elif message.video_note:
        media = [message.video_note.file_id, f"video_note_{cnt}", "video_note"]

    if not media:
        await message.answer(text=messages.INCORRECTLY_MEDIA_ERROR)
        return

    core.create(user_id, "file", media[1], file_id=media[0], file_type=media[2])
    await state.update_data(cnt=cnt + 1)
    await message.answer(text=f"{cnt} медиа добавлено")


@dp.message(F.text, OrderAdd.set_head_text)
async def set_head_text(message: Message, state: FSMContext) -> None:
    """Установка заголовочного текста для папки."""
    chat_id = message.chat.id
    vertex_id = int(core.get_value_db("Users", "path", chat_id).split("\\")[-1].split(":")[-1])

    if message.text == "Очистить текст":
        core.set_value_db("Folders", "head_text", vertex_id, "")
    else:
        core.set_value_db("Folders", "head_text", vertex_id, message.text)
        await message.answer(text=messages.COMPLETE_HEAD_TEXT)

    await state.clear()
    await send_start_message(level_message_type="message", message=message)


@dp.message(F.text)
async def other_text(message: Message) -> None:
    """Обработка прочих текстовых сообщений."""
    if message.chat.type == "private":
        await message.answer(text=messages.INCORRECTLY_TEXT_ERROR)


async def main() -> None:
    """Основная функция запуска бота."""
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())