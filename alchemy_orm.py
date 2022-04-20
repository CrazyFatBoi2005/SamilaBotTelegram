# Файл для работы с orm
from data import db_session
from sqlalchemy.exc import IntegrityError
from data.users import User
from data.pictures import Picture


# добавляем пользователя в базу orm
def add_user(chat_id, name):
    # Пробуем добавить
    try:
        db_session.global_init("db/orb_base.db")
        user = User()
        user.chat_id = chat_id
        user.name = name
        user.number = 'None'
        db_sess = db_session.create_session()
        db_sess.add(user)
        db_sess.commit()
    # Если этот пользователь уже есть
    except IntegrityError:
        return 0


# добавляем картинку в базу orm
def add_picture(chat_id, name, path):
    try:
        db_session.global_init("db/orb_base.db")
        pic = Picture()
        pic.chat_id = chat_id
        pic.name = name
        pic.path = path
        db_sess = db_session.create_session()
        db_sess.add(pic)
        db_sess.commit()
    except IntegrityError:
        return 0
