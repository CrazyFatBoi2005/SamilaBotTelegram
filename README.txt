SamilaLibBot - Бот основанный на открытой библиотеке Samila
Для взаимодействия с ботом достаточно открыть его в Telegram и написать команду /start из подсказок
После команды /start Бот откроет клавиатуру с 3 кнопками:
    /Picture
        Данная команда начинает генерацию катинки(занимает некоторое время 10-15 секунд):
            Бот попросит вас указать:
                цвет(цвета будут на клавиатуре с кнопками)
                проекцию(проекции будут на клавиатуре и влиют на форму сгенерированного рисунка)
            Если вы захотите сохранить картинку себе в избранное(кнопкой под получившейся картинкой),
            бот попросит вас указать имя картинки. Позже вы сможете посмотреть эту картинку в команде /Favorites,
            указав нужное вам имя.
            Иначе, вы можете удалить картинку(кнопкой "Удлить", которая будет под результатом)
    /Favorites
        Данная команда выводит вам кнопки с именами картинок, которые вы сгенериорвали и сохранили,
        после нажатия на нужную вам кнопку с соответсвующем именем, бот отправит вам эту картинку, где вы можете:
            Посмотреть на картинку/Сохранить ее к себе в галерею
            Удалить картинку из избранного
    /Random
        Данная команда позволяет вам посмотреть картинки, которые сгенерировали другие пользователи:
            После нажатия вам отправится случайная картинка из базы, под ней будут кнопки:
                Добавить к себе(указать имя и картинка уже будет у вас в избранном)
                Стоп(прекратить смотреть картинки других пользователей)
                Следующий(следующий случайный файл из базы)
Бот отвечает на ваши сообщения и запутаться в нем будет сложно
Бот работает на heroku