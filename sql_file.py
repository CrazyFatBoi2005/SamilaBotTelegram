# SQLITE файлик с запросами
import sqlite3
from os import remove
from random import randint
from telegram import InlineKeyboardButton


# получаем массив со словарями {путь, имя} для каждой картинки из избранного данного пользователя
def get_all_favorites(chat_id):
    con = sqlite3.connect('bot.db')
    cur = con.cursor()
    all_favorites = cur.execute(f"""SELECT chat_id, name, path FROM favorites 
                WHERE chat_id = {chat_id};""").fetchall()
    con.close()
    res = []
    for i in range(len(all_favorites)):
        res.append({
            'picture_name': all_favorites[i][1],
            'picture_path': all_favorites[i][2]
        })
    return res


# Добавляем картинку в базу
def add_to_favorite(chat_id, path, seed, name):
    check_name = get_all_favorites(chat_id)
    double = False
    for i in range(len(check_name)):
        if check_name[i]['picture_name'] == name:
            double = True
            break
    # если имя не повторяется
    if not double:
        # добавляем в базу
        con = sqlite3.connect('bot.db')
        cur = con.cursor()
        cur.execute(f"""INSERT INTO favorites(chat_id, path, seed, name)
            VALUES({chat_id}, "{path}", {seed}, "{name}");""")
        con.commit()
        con.close()
        return 1
    else:
        # иначе повторяем ввод в main.py
        return 0


# Удаляем из любимого
def delete_from_favorite(chat_id, path):
    try:
        con = sqlite3.connect('bot.db')
        cur = con.cursor()
        cur.execute(f"""DELETE FROM favorites
                    WHERE chat_id = {chat_id} AND path = '{path}';""")
        con.commit()
        con.close()
        return 'Удалено'
    except:
        return 'Файл не найден'


# Получем клавиатру с именами всех картинок, добавленных в любимое данным пользователем
def get_favorite_keyboard(chat_id):
    favorites = get_all_favorites(chat_id)
    keyboard = []
    flag = False
    # до тысячи строк кнопок)
    for i in range(1000):
        row = []
        # 4 столбика
        for j in range(4):
            if j + i * 4 < len(favorites):
                # добавляем кнопку в строку с уникальным колбэком, имя кнопки = текст кнопки
                row.append(InlineKeyboardButton(
                    text=str(favorites[i * 4 + j]['picture_name']).capitalize(),
                    callback_data='PATH!' + favorites[i * 4 + j]['picture_path']
                ))
            else:
                # если картинки кончились - выходим из цикла флагом
                flag = True
                break
        # добавляем последнюю получившуюся строку
        keyboard.append(row)
        # выходим по окончанию картинок
        if flag:
            break
    # возвращаем клавиатуру
    return keyboard


# выбор рандомной картинки из любимого других пользователей(без ваших картинок)
def choose_random(chat_id):
    con = sqlite3.connect('bot.db')
    cur = con.cursor()
    all_favorites = cur.execute(f"""SELECT chat_id, name, path FROM favorites 
        WHERE chat_id != {chat_id};""").fetchall()
    con.close()
    # любая картинка
    r = randint(0,  len(all_favorites) - 1)
    # возвращаяю путь к картинке
    return all_favorites[r][2]
