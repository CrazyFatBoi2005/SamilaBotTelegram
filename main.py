# все импорты
import logging
from sql_file import *
from os import remove
from alchemy_orm import *
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler
from telegram.ext import CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot, User
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from Samila_generations import generate, return_proj

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

# мой chat_id
admin = '394323698'

# Callbacks const
FAVORITE_CALLBACK = "add_to_favorite"
DELETE_PICTURE_CALLBACK = "delete_picture"
NEXT_RANDOM_CALLBACK = "next_random"
STOP_RANDOM_CALLBACK = "stop_random"

logger = logging.getLogger(__name__)

# токен бота(не воруйте)
TOKEN = '5371583248:AAHcO84QNtnGNArVqZ6bgVnVlbFq4WELnDU'

# прописываю markups для вызова потом
base_keyboard = [["/Picture"], ["/Favorites", "/Random"]]
base_markup = ReplyKeyboardMarkup(base_keyboard, one_time_keyboard=False)

choose_color_keyboard = [['yellow', 'purple'], ['blue', 'red']]
choose_color_markup = ReplyKeyboardMarkup(choose_color_keyboard, one_time_keyboard=True)

choose_proj_keyboard = return_proj([])
choose_proj_markup = ReplyKeyboardMarkup(choose_proj_keyboard, one_time_keyboard=True)

add_to_favorite_markup = InlineKeyboardMarkup([
    [InlineKeyboardButton(text='Добавить в избранное', callback_data=FAVORITE_CALLBACK)],
    [InlineKeyboardButton(text='Удалить', callback_data=DELETE_PICTURE_CALLBACK)]
    ])

# все составляющие бота
bot = Bot(token=TOKEN)
updater = Updater(bot=bot)
dp = updater.dispatcher


# Определяем функцию-обработчик сообщений.
# У неё два параметра, сам бот и класс updater, принявший сообщение.
def text_help(update, context):
    update.message.reply_text("Используйте команды для взаимодействия с ботом!")
    # print(update.message.from_user)


# Приветствие и добавление юзера в базу
def start(update, context):
    update.message.reply_text(
        "Добро пожаловать в SamilaBot!\nБот позволит вам генерировать картинки на выбор!\n",
        reply_markup=base_markup)
    user = update.message.from_user
    add_user(chat_id=user['id'], name=user['first_name'])


# Остановка всех сценариев
def stop(update, context):
    update.message.reply_text(
        "Диалог был прерван.",
        reply_markup=base_markup)
    return ConversationHandler.END


# ГЕНЕРАЦИЯ КАРТИНОК, СЦЕНАРИЙ
# Генерация картинки и отправка
def send_pic_samila(upd, color, proj, context):
    upd.message.reply_text(
        "Картинка в обработке!",
        reply_markup=None
    )
    # путь и семечко картинки
    file, seed = generate(color, proj, 1)
    # принт для проверки отправки пользователю
    print(file, seed)
    # chat_id
    user = upd.message.from_user.id
    # в user_data записываем данные о сгенерированной картинке для дальнейшего использования
    context.user_data['picture_data'] = {
                                            "user": user,
                                            "file": file,
                                            "seed": seed,
    }
    # отправляем полученную картинку автору запроса
    bot.send_photo(chat_id=user,
                   photo=open(file, mode='rb'),
                   caption=f'Ваш результат!\nЦвет: {color}\nПроекция: {proj}',
                   reply_markup=add_to_favorite_markup
                   )
    # добавили картинку в базу
    add_picture(chat_id=user, path=file, name='-')
    # bot.send_message(chat_id=user, text='Вот ваш результат!', reply_markup=None)
    # если запрос сделал не админ(я), то бот отправляет результат мне тоже
    if user != int(admin):
        bot.send_photo(chat_id=admin, photo=open(file, mode='rb'))


# Начало запроса генерации
def start_picture(update, context):
    update.message.reply_text(
        "Выберите цвет картинки:",
        reply_markup=choose_color_markup)
    return 1


# Выбор цвета
def chose_color(update, context):
    context.user_data['color'] = update.message.text
    update.message.reply_text(
        "Выберите проекцию картинки:",
        reply_markup=choose_proj_markup)
    return 2


# Выбор проекции
def chose_proj(update, context):
    context.user_data['proj'] = update.message.text
    # все нужные параметры у нас, генерируем картинку
    send_pic_samila(update, context.user_data['color'], context.user_data['proj'], context)
    return 3


# Ввод имени, при сохранении
def chose_name(update, context):
    msg = update.message.text
    context.user_data['picture_data']['name'] = msg
    # добавляем в базу и проверяем return функции
    # если return 0, то пользователь ввел имя, которое есть в его базе -> повторим ввод
    if add_to_favorite(context.user_data['picture_data']['user'],
                       context.user_data['picture_data']['file'],
                       context.user_data['picture_data']['seed'],
                       context.user_data['picture_data']['name']) == 0:
        update.message.reply_text("Имя повторяется, выберите другое")
        return 4
    # return != 0 -> мы оповещаем юзера о добавлении картинки и завершаем диалог
    update.message.reply_text("Картинка добавленна в избранное", reply_markup=base_markup)
    return ConversationHandler.END


# Улавливаем callback и реагируем на него
def callback_query_fav_handler(update, context):
    cqd = update.callback_query.data
    user = update.callback_query.from_user
    # добавление в любимые
    if cqd == FAVORITE_CALLBACK:
        user.send_message('Введите имя картинки:\nИмя картинки не должно повторяться')
        update.callback_query.edit_message_reply_markup(None)
        return 4
    # удалеине картинки из любимых
    elif cqd == DELETE_PICTURE_CALLBACK:
        remove(context.user_data['picture_data']['file'])
        user.send_message('Файл удален', reply_markup=base_markup)
        update.callback_query.edit_message_reply_markup(None)
        return ConversationHandler.END
    # elif cqd == ... ### for other buttons


# еще один handler для общих ситуаций
def callback_query_handler(update, context):
    cqd = update.callback_query.data
    user = update.callback_query.from_user
    # Общие колбэки имеют формат 'команда!путь', так я отслеживаю действие, а потом делаю его с нужной картинкой
    if cqd.split('!')[0] == 'PATH':
        path = cqd.split('!')[1]
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton('Удалить', callback_data=f"DEL!{path}")],
            [InlineKeyboardButton('Готово', callback_data='-')],
        ])
        bot.send_photo(chat_id=user.id,
                       photo=open(path, mode='rb'),
                       reply_markup=markup)
        bot.deleteMessage(chat_id=user.id, message_id=update.callback_query.message.message_id)
    elif cqd.split('!')[0] == 'DEL':
        bot.deleteMessage(chat_id=user.id, message_id=update.callback_query.message.message_id)
        bot.send_message(user.id, delete_from_favorite(user.id, cqd.split('!')[1]))
    elif cqd == NEXT_RANDOM_CALLBACK:
        get_random(update, context)
    # случай, если этот хэндлер поймал не тот колбэк
    # upd.(больше не ловит)
    elif cqd == '-':
        bot.deleteMessage(chat_id=user.id, message_id=update.callback_query.message.message_id)
        print('поймал)')


# Сценарий отправки картинки /Picture
picture_handl = ConversationHandler(

    # Точка входа в диалог.
    entry_points=[CommandHandler('Picture', start_picture)],

    # Состояние внутри диалога.
    states={
        # Выбор цвета картинки
        1: [MessageHandler(Filters.text & ~Filters.command, chose_color)],
        # Выбор проекции картинки
        2: [MessageHandler(Filters.text & ~Filters.command, chose_proj)],
        # Отлавливаем нажатие кнопки под картинкой
        3: [CallbackQueryHandler(callback_query_fav_handler)],
        # Записываем название картинки
        4: [MessageHandler(Filters.text & ~Filters.command, chose_name)],
    },

    # Точка прерывания диалога.
    fallbacks=[CommandHandler('stop', stop),
               ]
)


#
# ИЗБРАННОЕ, СЦЕНАРИЙ, ФУНКЦИИ
# Получаем все любимые из базы
def get_favorites(update, context):
    user = update.message.from_user
    # функция возвращает готовую клавиатуру из любимых картинок
    kb = get_favorite_keyboard(user.id)
    favorites_markup = InlineKeyboardMarkup(kb)
    update.message.reply_text(
        "Избранное:",
        reply_markup=favorites_markup)
    # удаляет сообщение, чтобы не мусорить чат
    bot.deleteMessage(chat_id=user.id, message_id=update.message.message_id)


# Запись имени для диалога с рандомом(отличается тем, что не имеет сида, так как не генерируется)
# Принцип работы тот же, что и в chose_name
def write_name(update, context):
    msg = update.message.text
    context.user_data['picture_data']['name'] = msg
    if add_to_favorite(context.user_data['picture_data']['user'],
                       context.user_data['picture_data']['file'],
                       -1,
                       context.user_data['picture_data']['name']) == 0:
        update.message.reply_text("Имя повторяется, выберите другое")
        return 2
    else:
        update.message.reply_text("Картинка добавленна в избранное", reply_markup=base_markup)
        return ConversationHandler.END


# Ловит все callback'и связанные с диалогом о рандоме
def random_callback_query_handler(update, context):
    cqd = update.callback_query.data
    user = update.callback_query.from_user
    # Добавить в базу
    if cqd.split('!')[0] == 'ADD':
        user.send_message('Введите имя картинки:\nИмя картинки не должно повторяться')
        update.callback_query.edit_message_reply_markup(None)
        return 2
    # Выбрать следующую картинку(рандомную)
    elif cqd == NEXT_RANDOM_CALLBACK:
        next_random(update, context)
        return
    # Прекратить смотреть рандомные картинки
    elif cqd == STOP_RANDOM_CALLBACK:
        bot.send_message(chat_id=user.id,
                         text='Приходите в другой раз! Наша база постоянно пополняется.',
                         reply_markup=base_markup)
        return ConversationHandler.END


# Переход к следующему рандомному рисунку из базы
# используется в сценарии
def next_random(update, context):
    user_id = context.user_data['picture_data']['user']
    file = choose_random(user_id)
    context.user_data['picture_data']['path'] = file
    random_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text='Добавить в избранное',
                              callback_data='ADD!' + file)],
        [InlineKeyboardButton(text='Стоп',
                              callback_data=STOP_RANDOM_CALLBACK),
         InlineKeyboardButton(text='Следующий',
                              callback_data=NEXT_RANDOM_CALLBACK),
         ]
    ])

    bot.send_photo(chat_id=user_id,
                   photo=open(file, mode='rb'),
                   reply_markup=random_markup
                   )
    return 1


# Начало сценария с рандомными картинками других пользователей
def get_random(update, context):
    user = update.message.from_user
    bot.send_message(chat_id=user.id,
                     text='Давайте посмотрим какие картинки сгенерировали другие пользователи',
                     reply_markup=None)
    file = choose_random(user.id)
    if len(context.user_data.keys()) == 0:
        context.user_data['picture_data'] = {'user': user.id}
    context.user_data['picture_data']['file'] = file
    random_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text='Добавить в избранное',
                              callback_data='ADD!' + file)],
        [InlineKeyboardButton(text='Стоп',
                              callback_data=STOP_RANDOM_CALLBACK),
         InlineKeyboardButton(text='Следующий',
                              callback_data=NEXT_RANDOM_CALLBACK),
         ]
    ])

    bot.send_photo(chat_id=user.id,
                   photo=open(file, mode='rb'),
                   reply_markup=random_markup
                   )
    bot.deleteMessage(chat_id=user.id, message_id=update.message.message_id)
    return 1


# Сценарий рандомных картинок
random_handl = ConversationHandler(

    # Точка входа в диалог.
    entry_points=[CommandHandler("Random", get_random)],

    # Состояние внутри диалога.
    states={
        # Смотрим на нажатие кнопок пользователем
        1: [CallbackQueryHandler(random_callback_query_handler)],
        # вводим имя, если пользователь захотел добавить картинку себе
        2: [MessageHandler(Filters.text & ~Filters.command, write_name)],
    },

    # Точка прерывания диалога.
    fallbacks=[CommandHandler('stop', stop),
               ]
)


# Функция для удобства. Добавляет все команды в диспетчер
def add_all_handlers(dp, funcs):
    for func in funcs.keys():
        print(func, funcs[func])
        dp.add_handler(CommandHandler(func, funcs[func]))


# Основная функция
def main():
    all_funcs = {
        "start": start,
        "Picture": start_picture,
        "Favorites": get_favorites,
        "Random": get_random
    }

    # все handlers
    dp.add_handler(picture_handl)
    dp.add_handler(random_handl)
    dp.add_handler(CallbackQueryHandler(callback_query_handler))
    add_all_handlers(dp, all_funcs)

    updater.start_polling()

    updater.idle()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
