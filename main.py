import random
import telebot
from telebot import types
import datetime
from dateutil.relativedelta import relativedelta


from create_write_timer import Create
from sqlitefunc import Data_base
from NewTimer import Timers

bot = telebot.TeleBot('')

db = Data_base('user.db',"""CREATE TABLE IF NOT EXISTS chat_id(
                    id INTEGER, 
                    username STRING, 
                    name_soldier STRING, 
                    date TIMESTAMP, 
                    delta_date INTEGER, 
                    timer_status BOOLEAN,
                    reminder_time TIMESTAMP
                )""")

def create_keyboard(*buttons):
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    for button in buttons:
        but = types.KeyboardButton(button)
        markup.add(but)
    return markup

def button_on_off(id, type_button):
    record = db.select.one_record(id)
    match type_button:
        case 'таймер':
            status = record.timer_status
        case 'уведомления':
            status = record.notification_status
        case 'праздники':
            status = record.holidays_status
    if status == True:
        return 'Выключить ' + type_button
    else:
        return 'Включить ' + type_button
def markup_main_menu(id):
    return create_keyboard('Изменить таймер',
                           button_on_off(id, 'таймер'),
                           'Показать таймер',
                           'Что я умею',
                           'О разработчике',
                           'Обратная связь')

@bot.message_handler(commands=['start'])
def start(message):
    db.create_new_user(message.chat.id, message.from_user.username)
    bot.send_message(message.chat.id,
                     f"Привет, {message.from_user.username}! "
                     f"Я бот для ждуль которые ждут своих солдатиков из армии.")
    record = db.select.one_record(message.chat.id)
    if record.timer_status is not None:
        bot.send_message(message.chat.id,
                         "У тебя уже есть активный таймер",
                         reply_markup=markup_main_menu(message.chat.id))
    else:
        markup = create_keyboard('Создать таймер!',
                                 'Что я умею',
                                 'О разработчике',
                                 'Обратная связь')
        bot.send_message(message.chat.id,
                         'Нажми кнопку "Что я умею" и я расскажу о своих функциях.',
                         reply_markup=markup)

@bot.message_handler(commands=['stop'])
def stop(message):
    db.delete_user(message.chat.id)
    timer.update_timer(message.chat.id)
    bot.send_message(message.chat.id, 'Твоя запись удалена',
                     reply_markup=types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda call: True)
def call_back(call):
    match call.data:
        case 'Continue_create_timer':
            continue_create_timer(call.message)
        case 'Update_time':
            create.create_time_timer(call.message, False)
        case 'Status_notification':
            db.write.notification_status(call.message.chat.id, False)
            bot.send_message(call.message.chat.id, 'Уведомления выключены!')
            menu_ending(call.message, False)

@bot.message_handler(content_types=['text'])
def processing_message(message):
    match message.text:
        case 'Создать таймер!':
            if db.select.timer_status(message.chat.id) is None:
                create.create_timer(message, True)
            else:
                bot.send_message(message.chat.id,
                                 "У тебя уже есть активный таймер",
                                 reply_markup=markup_main_menu(message.chat.id))

        case 'Что я умею':
            bot.send_message(message.chat.id,
                             'Основная моя функция присылать уведомление с заданным интервалом времени '
                             'о количестве оставшихся дней до окончания службы солдата.'
                             'Для создания таймера нажмите кнопку «Создать таймер!» и введите следующие данные:\n'
                             '-Имя солдата\n'
                             '-Дату призыва\n'
                             '-Время уведомления\n' 
                             '-Интервал уведомлений\n'
                             'После создания таймера у вас будет возможность изменить все эти настройки, '
                             'для этого нажмите кнопку «Изменить таймер». Если вы передумали изменять параметры таймера, '
                             'вы можете отметить это действие нажав на кнопку «Я передумал».\n'
                             'Так же вы можете выключить или включить таймер, для этого нажмите кнопку «Включить/Выключить таймер». '
                             'После выключения таймера я перестану присылать вам уведомления, пока вы не включите таймер снова.\n'
                             'Дополнительной функций является поздравления с праздниками, если вы не хотите получать '
                             'уведомления о праздниках, вы можете выключить их в меню настройки таймера.\n'
                             'Если вы хотите написать: о ошибках, о дополнительных функциях или хотите оставить отзыв, '
                             'нажмите кнопку «Обратная связь» и напишите своё сообщение.')

        case 'О разработчике':
            bot.send_message(message.chat.id,
                             'Разработчик: @fedotkot \n'
                             'E-mail: fedotkotStudio@ya.ru \n'
                             'Версия бота: 1.0')
        case 'Обратная связь':
            bot.send_message(message.chat.id, 'Напишите своё сообщение:',
                             reply_markup=create_keyboard('Я передумал'))
            bot.register_next_step_handler(message, write_report)

        case 'РВ':
            bot.send_message(message.chat.id, 'СН')

        case 'РОССИЯ!!!':
            bot.send_message(message.chat.id, "СЛАВА РОССИЙСКОМУ СОЛДАТУ!")

        case _:
            # Действия для активного таймера
            if db.select.timer_status(message.chat.id) is not None:
                match message.text:
                    case 'Изменить таймер':
                            markup = create_keyboard('Изменить имя солдата',
                                                     'Изменить дату призыва',
                                                     'Измениить интервал',
                                                     'Изменить время',
                                                     button_on_off(message.chat.id, 'уведомления'),
                                                     button_on_off(message.chat.id, 'праздники'),
                                                     'Я передумал')
                            bot.send_message(message.chat.id,
                                             'Что вы хотите измениить?',
                                             reply_markup=markup)
                            bot.register_next_step_handler(message, update_data_timer)

                    case 'Выключить таймер':
                        update_status(message.chat.id, 'таймер', False)

                    case 'Включить таймер':
                        update_status(message.chat.id, 'таймер', True)

                    case 'Показать таймер':
                        view_timer(message.chat.id)
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='Продолжить создание таймера!',
                                                      callback_data='Continue_create_timer'))
                bot.send_message(message.chat.id,
                                 'У вас нет активного таймера. Вы не закончили создание таймера',
                                 reply_markup=markup)

def declination(days):
    match days:
        case 1:
            return 'день'
        case 2:
            return 'дня'
        case day if 3 <= day <= 366:
            return 'дней'

def view_timer(id):
    record = db.select.one_record(id)
    delta = (datetime.datetime.strptime(record.date, '%Y-%m-%d').date() + relativedelta(years = 1) - datetime.date.today()).days
    days_have_passed = (datetime.date.today() - datetime.datetime.strptime(record.date, '%Y-%m-%d').date()).days
    bot.send_message(id,
                     f'Имя солдата: {record.name_soldier}\n'
                     f'Дата начала службы: {record.date}\n'
                     f'{days_have_passed} {declination(days_have_passed)}  прошло с момента призыва\n'
                     f'{delta} {declination(delta)} остлалось до конца службы\n'
                     )

def update_status(id, type_status, status):
    match type_status:
        case 'таймер':
                if db.select.timer_status(id) != status:
                    db.write.timer_status(id, status)
                    timer.update_timer(id)
                    real_status = status
                else:
                    real_status = not status
        case 'уведомления':
                if db.select.notification_status(id) != status:
                    db.write.notification_status(id, status)
                    real_status = status
                else:
                    real_status = not status
        case 'праздники':
                if db.select.holidays_status(id) != status:
                    db.write.holidays_status(id, status)
                    real_status = status
                else:
                    real_status = not status
    if real_status == status:
        if status == True:
            bot.send_message(id, type_status + ' включены', reply_markup=markup_main_menu(id))
        else:
            bot.send_message(id, type_status + ' выключены', reply_markup=markup_main_menu(id))
    else:
        if status == True:
            bot.send_message(id, f'Кого ты пытаешься обмануть?! {type_status} и так включен!',
                             reply_markup=markup_main_menu(id))
        else:
            bot.send_message(id, f'Кого ты пытаешься обмануть?! {type_status} и так выключен!',
                             reply_markup=markup_main_menu(id))

def continue_create_timer(message):
    record = db.select.one_record(message.chat.id)
    if record.name_soldier is None:
        create.create_timer(message, True)
    elif record.date is None:
        create.create_date_call(message, True)
    elif record.reminder_time is None:
        create.create_time_timer(message, True)
    elif record.delta_date is None:
        create.create_interval_date(message, True)

def update_data_timer(message):
    match message.text:
        case 'Изменить имя солдата':
            create.create_timer(message, False)
        case 'Изменить дату призыва':
            create.create_date_call(message, False)
        case 'Измениить интервал':
            create.create_interval_date(message, False)
        case 'Изменить время':
            create.create_time_timer(message, False)
        case 'Выключить уведомления':
            update_status(message.chat.id, 'уведомления', False)
        case 'Включить уведомления':
            update_status(message.chat.id, 'уведомления', True)
        case 'Выключить праздники':
            update_status(message.chat.id, 'праздники', False)
        case 'Включить праздники':
            update_status(message.chat.id, 'праздники', True)
        case 'Я передумал':
            menu_ending(message, False)

def write_report(message):
    match  message.text:
        case 'Я передумал':
            menu_ending(message, False)
        case _:
            db.write_report(message.chat.id,
                            message.from_user.username,
                            datetime.datetime.now(),
                            message.text)
            bot.send_message(message.chat.id, 'Репорт отправлен!')
            menu_ending(message, False)

def menu_ending(message, status):
    if  status == True:
        print(f'Пользователь {message.from_user.username} Внес измения в базу данных!')
        bot.send_message(message.chat.id, 'Готово! Таймер изменен!')
        bot.send_message(message.chat.id,
                         'Теперь в любой момент вы можете изменить мои настройки '
                         'или выключить таймер',
                         reply_markup=markup_main_menu(message.chat.id))
    else:
        bot.send_message(message.chat.id,
                         'Нажми кнопку "Что я умею" и я расскажу о своих функциях.',
                         reply_markup=markup_main_menu(message.chat.id))

def send_timer_message(record):
    #Если сегодня день окончания службы
    if datetime.datetime.today() == datetime.datetime.strptime(record.date, '%Y-%m-%d').date() + relativedelta(years = 1):
        text ='sss'
        db.write.timer_status(record.id,False)
    else:
        #Количество дней от начала призыва
        days = (datetime.date.today() - datetime.datetime.strptime(record.date, '%Y-%m-%d').date()).days
        #Условие, если количество дней делится на промежутки дней без остатка
        if days % record.delta_date == 0:
            second_date = datetime.datetime.strptime(record.date, '%Y-%m-%d').date() + relativedelta(years = 1)
            delta = (second_date - datetime.date.today()).days
            match random.randint(1,5):
                case 1:
                    text = f'{record.name_soldier} вернется через {delta} дней!'
                case 2:
                    text = f'Прошло всего {days} {declination(days)}, а {record.name_soldier} скучает по дому... \n' \
                           f'А впереди ещё {delta} {declination(delta)}.'
                case 3:
                    text = f'Солдат спит служба идет! Осталось всего лишь: {delta} {declination(delta)}.'
                case 4:
                    text = f'Кто-то скоро будет слушать Сектор газа... Осталось {delta}'
                case 5:
                    s = (second_date - datetime.date.today()).seconds
                    text = f'Осталось {s} секунд до дембеля.'
        else:
            text = ''
    if text != '':
        bot.send_message(record.id, text)
        print(f'Отправили сообщение в чат: {record.id} пользователю: {record.user_name}')

def notification_message(records):
    for record in records:
        if db.select.notification_status(record.id):
            if (record.notification_status is None) and ((record.timer_status == True) or (record.timer_status == False)):
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='Установить время',
                                                      callback_data='Update_time'))
                bot.send_message(record.id,
                                 'У вас не установленно время таймера. '
                                 'Вы можете выставвить его настройках таймера или нажать кнопку "Установить время"',
                                 reply_markup=markup)
                off_notification(record.id)
            else:
                if record.timer_status is None:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton(text='Продолжить создание таймера!',
                                                          callback_data='Continue_create_timer'))
                    bot.clear_step_handler(record.id)
                    bot.send_message(record.id,
                                     'Вы не закончили создавать таймер.'
                                     'Нажмите кнопку "Продолжить создание таймера!"',
                                     reply_markup=markup)
                    off_notification(record.id)

def off_notification(id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Выключить уведомления',
                                          callback_data='Status_notification'))
    bot.send_message(id, 'Если не хотите получать уведомления, то нажмите на кнопку "Выключить уведомления"',
                     reply_markup=markup)

if __name__ == '__main__':
    print('Я включился!')
    timer = Timers('user.db', send_timer_message, bot, notification_message)
    create = Create(bot, menu_ending, db, timer, create_keyboard)
    timer.start()
    bot.polling(none_stop=True)