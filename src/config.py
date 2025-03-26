from typing import Dict, List

# Регулярное выражение для проверки закодированных строк
REGEX = r"[A-z0-9@$%&]{4,16}:[A-z0-9@$%&]{58,64}"

# Наборы символов для кодирования/декодирования
SYMBOLS = "@$%&0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
ALPHABET = (
    " !?@#$%&№()[/]{\}<|>^_\"'`*+-=~.,:;0123456789ABCDEFGHIJKLMNOPQR"
    "STUVWXYZabcdefghijklmnopqrstuvwxyzАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзий"
    "клмнопрстуфхцчшщъыьэюя"
)

# Словари для быстрого поиска символов
DICT_SYMBOLS: Dict[str, int] = {char: idx for idx, char in enumerate(SYMBOLS)}
DICT_ALPHABET: Dict[str, int] = {char: idx for idx, char in enumerate(ALPHABET)}

# Константы
MAX_LEN_NAME = 50  # Максимальная длина имени папки


def my_pow(value: int, power: int) -> int:
    """
    Эффективное возведение в степень через возведение в квадрат (рекурсивная реализация).
    
    Args:
        value: Основание
        power: Показатель степени
        
    Returns:
        Результат value^power
    """
    if power == 0:
        return 1
    if power % 2 == 0:
        return my_pow(value * value, power // 2)
    else:
        return value * my_pow(value * value, (power - 1) // 2)


def crypt(string: str, is_encode: bool) -> str:
    """
    Кодирует или декодирует строку с использованием пользовательского алгоритма 
    преобразования между системами счисления.
    
    Args:
        string: Входная строка для кодирования/декодирования
        is_encode: True для кодирования, False для декодирования
        
    Returns:
        Закодированная/раскодированная строка
    """
    length = len(string)
    number = 0
    
    # Выбираем соответствующий набор символов в зависимости от операции
    if is_encode:
        char_dict, output_chars, input_base, output_base = (
            DICT_ALPHABET, SYMBOLS, len(ALPHABET), len(SYMBOLS))
    else:
        char_dict, output_chars, input_base, output_base = (
            DICT_SYMBOLS, ALPHABET, len(SYMBOLS), len(ALPHABET))

    # Преобразуем строку в числовое представление
    for i in range(length):
        number += char_dict[string[i]] * my_pow(input_base, length - i - 1)

    # Конвертируем число в новую систему счисления
    result = ""
    while number != 0:
        result += output_chars[number % output_base]
        number //= output_base
    
    return result[::-1]  # Разворачиваем строку


def encoding_folder(id: str, folder_name: str) -> str:
    """
    Кодирует ID папки и её название в специальный формат.
    
    Args:
        id: Идентификатор папки
        folder_name: Название папки
        
    Returns:
        Закодированная строка в формате "код_id:код_названия"
        
    Raises:
        ValueError: Если название папки слишком длинное
    """
    if len(folder_name) > MAX_LEN_NAME:
        raise ValueError("Слишком длинное название папки")
    
    # Дополняем название пробелами до максимальной длины
    padded_name = folder_name.ljust(MAX_LEN_NAME)
    
    return f"{crypt(id, True)}:{crypt(padded_name, True)}"


def decoding_folder(coding_string: str) -> List[str]:
    """
    Декодирует строку с закодированными ID папки и её названием.
    
    Args:
        coding_string: Закодированная строка в формате "код_id:код_названия"
        
    Returns:
        Список из двух элементов: [id, название_папки]
    """
    return [crypt(part, False).strip() for part in coding_string.split(':')]